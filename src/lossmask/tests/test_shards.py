import json

import numpy as np
import pytest
import torch

from src.lossmask.shards import (TaggedShardReader, TaggedShardWriter,
                                 WeightedBatchLoader, write_index)
from src.lossmask.tags import TAG_ENTITY, TAG_NUMBER, weight_table
from src.train.data import BatchLoader, ShardReader, ShardWriter


def build(tmp_path, tokens, tags, shard_size=8):
    writer = TaggedShardWriter(tmp_path, shard_size=shard_size)
    writer.write(tokens, tags)
    writer.close()
    return tmp_path


def test_tokens_are_byte_identical_to_a_plain_render(tmp_path):
    tokens = list(range(40))
    tagged_dir = build(tmp_path / "tagged", tokens, [0] * 40)
    plain = ShardWriter(tmp_path / "plain", shard_size=8)
    plain.write(tokens)
    plain.close()
    for name in sorted(p.name for p in (tmp_path / "plain").glob("*.bin")):
        assert (tagged_dir / name).read_bytes() == \
            (tmp_path / "plain" / name).read_bytes()


def test_the_plain_reader_opens_a_tagged_directory(tmp_path):
    tokens = list(range(40))
    build(tmp_path, tokens, [0] * 40)
    reader = ShardReader(tmp_path)
    assert reader.total_tokens == 40
    assert list(reader.get_slice(3, 5)) == [3, 4, 5, 6, 7]


def test_the_tagged_reader_serves_both_streams_across_shards(tmp_path):
    tokens = list(range(40))
    tags = [(i % 3) for i in range(40)]
    build(tmp_path, tokens, tags)
    reader = TaggedShardReader(tmp_path)
    assert reader.tagged
    assert list(reader.get_slice(6, 10)) == tokens[6:16]
    assert list(reader.get_tag_slice(6, 10)) == tags[6:16]
    assert list(reader.get_tag_slice(0, 40)) == tags


def test_the_tagged_reader_degrades_on_untagged_data(tmp_path):
    plain = ShardWriter(tmp_path, shard_size=8)
    plain.write(list(range(40)))
    plain.close()
    reader = TaggedShardReader(tmp_path)
    assert not reader.tagged
    assert list(reader.get_tag_slice(0, 5)) == [0, 0, 0, 0, 0]


def test_mismatched_streams_are_refused(tmp_path):
    writer = TaggedShardWriter(tmp_path)
    with pytest.raises(ValueError, match="lockstep"):
        writer.write([1, 2, 3], [0, 0])


def test_a_short_tag_file_is_caught(tmp_path):
    build(tmp_path, list(range(16)), [1] * 16, shard_size=16)
    path = tmp_path / "shard-00000.bin.tag.bin"
    path.write_bytes(path.read_bytes()[:10])
    with pytest.raises(ValueError, match="tags for"):
        TaggedShardReader(tmp_path)


def test_an_index_over_chunk_subdirectories_reads_as_one_stream(tmp_path):
    shards = []
    for k in range(3):
        sub = tmp_path / "chunks" / f"chunk-{k:05d}"
        writer = TaggedShardWriter(sub, shard_size=1 << 20)
        writer.write(list(range(k * 10, k * 10 + 10)), [k] * 10)
        index = writer.close()
        for shard in index["shards"]:
            shards.append({
                "file": f"chunks/chunk-{k:05d}/{shard['file']}",
                "num_tokens": shard["num_tokens"],
                "tag_file": f"chunks/chunk-{k:05d}/{shard['tag_file']}"})
    write_index(tmp_path, shards)
    reader = TaggedShardReader(tmp_path)
    assert reader.total_tokens == 30
    assert list(reader.get_slice(0, 30)) == list(range(30))
    assert list(reader.get_tag_slice(0, 30)) == [0] * 10 + [1] * 10 + [2] * 10


def test_the_weighted_loader_draws_the_same_offsets_as_the_plain_one(tmp_path):
    tokens = list(range(200))
    build(tmp_path, tokens, [0] * 200, shard_size=64)
    plain = BatchLoader(ShardReader(tmp_path), 4, 8, seed=17)
    weighted = WeightedBatchLoader(
        TaggedShardReader(tmp_path), 4, 8, weight_table({"entity": 0.0}),
        seed=17)
    for _ in range(5):
        (pi, pt), (wi, wt, _) = plain.next_batch(), weighted.next_batch()
        assert torch.equal(pi, wi)
        assert torch.equal(pt, wt)


def test_weights_align_with_the_targets_not_the_inputs(tmp_path):
    # Token 5 alone is an entity. A window starting at 0 predicts token 5 at
    # position 4, so the weight must land at index 4 of the row.
    tokens = list(range(20))
    tags = [0] * 20
    tags[5] = TAG_ENTITY
    build(tmp_path, tokens, tags, shard_size=64)
    reader = TaggedShardReader(tmp_path)
    loader = WeightedBatchLoader(
        reader, 1, 8, weight_table({"entity": 0.0}), seed=3)
    loader.rng = np.random.default_rng(0)
    loader.high = 0  # every draw starts at zero
    inputs, targets, weights = loader.next_batch()
    assert list(targets[0]) == list(range(1, 9))
    assert list(weights[0]) == [1, 1, 1, 1, 0, 1, 1, 1]
    assert weights.dtype == torch.float32


def test_the_weight_table_maps_tags_to_floats(tmp_path):
    table = weight_table({"entity": 0.0, "number": 0.1})
    assert table[TAG_ENTITY] == 0.0
    assert table[TAG_NUMBER] == pytest.approx(0.1)
    assert table[0] == 1.0
    assert weight_table(None).tolist() == [1.0] * len(table)
    with pytest.raises(ValueError, match="unknown tag"):
        weight_table({"nonsense": 0.0})
    with pytest.raises(ValueError, match="negative"):
        weight_table({"entity": -1.0})


def test_the_index_records_the_tag_histogram(tmp_path):
    build(tmp_path, list(range(20)), [0] * 15 + [1] * 5, shard_size=64)
    index = json.loads((tmp_path / "index.json").read_text())
    assert index["tag_histogram"] == {"0": 15, "1": 5}
    assert index["tag_names"]["1"] == "entity"


def test_next_batch_with_tags_returns_the_tags_behind_the_weights(tmp_path):
    tokens = list(range(200))
    tags = [(i % 5) for i in range(200)]
    build(tmp_path, tokens, tags, shard_size=64)
    table = weight_table({"entity": 0.0, "number": 0.25})
    loader = WeightedBatchLoader(
        TaggedShardReader(tmp_path), 3, 8, table, seed=11)
    inputs, targets, weights, drawn = loader.next_batch_with_tags()
    assert drawn.shape == targets.shape
    assert drawn.dtype == torch.int64
    assert torch.equal(weights, torch.from_numpy(table)[drawn])
    # The tags belong to the targets: every drawn tag is the tag of the token
    # in that position of targets, which for this corpus is its value mod 5.
    assert torch.equal(drawn, targets % 5)


def test_next_batch_and_next_batch_with_tags_draw_the_same_offsets(tmp_path):
    build(tmp_path, list(range(200)), [0] * 200, shard_size=64)
    plain = WeightedBatchLoader(
        TaggedShardReader(tmp_path), 2, 8, weight_table(None), seed=4)
    both = WeightedBatchLoader(
        TaggedShardReader(tmp_path), 2, 8, weight_table(None), seed=4)
    a_in, a_tgt, a_w = plain.next_batch()
    b_in, b_tgt, b_w, _ = both.next_batch_with_tags()
    assert torch.equal(a_in, b_in) and torch.equal(a_tgt, b_tgt)
    assert torch.equal(a_w, b_w)
