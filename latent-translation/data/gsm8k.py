"""GSM8K dataset loading and formatting for the latent-space translation pipeline.

Loads from HuggingFace datasets, formats using the Qwen instruct chat template,
and produces paired tokenizations for both the small and large models.
"""

import re
import torch
from torch.utils.data import Dataset
from datasets import load_dataset
from typing import Optional


# DESIGN DECISION: GSM8K answers have the format "...reasoning...\n#### <number>".
# We extract the final number after #### as the answer.  The "steps" are the
# reasoning lines before ####.  We format the question using the Qwen chat
# template and produce labels that only supervise the answer portion.

ANSWER_PATTERN = re.compile(r"####\s*(.+)")
NUMBER_PATTERN = re.compile(r"[\d,]+\.?\d*")


def extract_answer(answer_text: str) -> str:
    """Extract the final numerical answer from GSM8K answer format."""
    match = ANSWER_PATTERN.search(answer_text)
    if match:
        return match.group(1).strip().replace(",", "")
    # Fallback: find the last number in the text
    numbers = NUMBER_PATTERN.findall(answer_text)
    return numbers[-1].replace(",", "") if numbers else answer_text.strip()


def extract_steps(answer_text: str) -> list[str]:
    """Extract reasoning steps (everything before ####)."""
    parts = answer_text.split("####")
    if len(parts) > 1:
        reasoning = parts[0].strip()
    else:
        reasoning = answer_text.strip()
    return [s.strip() for s in reasoning.split("\n") if s.strip()]


class GSM8KDataset(Dataset):
    """GSM8K dataset with dual tokenization for both small and large models."""

    def __init__(
        self,
        split: str,
        tokenizer_small,
        tokenizer_large,
        max_seq_len: int = 512,
        max_samples: Optional[int] = None,
    ):
        # DESIGN DECISION: GSM8K has "train" and "test" splits on HuggingFace.
        # We use the test split for evaluation. For validation during training,
        # we hold out the last 200 examples from the train split.
        if split == "val":
            raw = load_dataset("gsm8k", "main", split="train")
            raw = raw.select(range(max(0, len(raw) - 200), len(raw)))
        elif split == "train":
            raw = load_dataset("gsm8k", "main", split="train")
            raw = raw.select(range(len(raw) - 200))
        else:  # test
            raw = load_dataset("gsm8k", "main", split="test")

        if max_samples is not None:
            raw = raw.select(range(min(max_samples, len(raw))))

        self.tokenizer_small = tokenizer_small
        self.tokenizer_large = tokenizer_large
        self.max_seq_len = max_seq_len

        self.questions = []
        self.answers = []       # final numerical answer string
        self.steps = []         # reasoning steps
        self.entries = []       # pre-tokenized entries

        for item in raw:
            question = item["question"]
            answer_text = item["answer"]
            final_answer = extract_answer(answer_text)
            steps = extract_steps(answer_text)

            self.questions.append(question)
            self.answers.append(final_answer)
            self.steps.append(steps)

            entry = self._prepare_entry(question, final_answer, steps)
            self.entries.append(entry)

    def _prepare_entry(
        self, question: str, answer: str, steps: list[str]
    ) -> dict:
        """Tokenize a single example for both models."""
        # Format as Qwen instruct chat
        messages = [{"role": "user", "content": question}]

        # The model should produce the final answer.
        # We format the assistant response as "The answer is {answer}"
        # to give a clear answer token span.
        assistant_response = f"The answer is {answer}"

        # ── Small model tokenization ─────────────────────────────────
        prompt_small = self.tokenizer_small.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=False,
        )
        full_text_small = prompt_small + assistant_response
        prompt_ids_small = self.tokenizer_small.encode(
            prompt_small, add_special_tokens=False
        )
        full_ids_small = self.tokenizer_small.encode(
            full_text_small, add_special_tokens=False
        )

        # Labels: -100 for prompt tokens, actual IDs for answer tokens
        labels_small = [-100] * len(prompt_ids_small) + full_ids_small[len(prompt_ids_small):]
        # Add EOS
        full_ids_small.append(self.tokenizer_small.eos_token_id)
        labels_small.append(self.tokenizer_small.eos_token_id)

        # Truncate
        full_ids_small = full_ids_small[:self.max_seq_len]
        labels_small = labels_small[:self.max_seq_len]

        # ── Large model tokenization ─────────────────────────────────
        prompt_large = self.tokenizer_large.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=False,
        )
        prompt_ids_large = self.tokenizer_large.encode(
            prompt_large, add_special_tokens=False
        )[:self.max_seq_len]

        # Keep the large-model sequence length aligned with the small-model
        # training sequence by extending the prompt with placeholder tokens.
        # This gives the cross-model path latent "slots" for the answer region
        # without requiring teacher-forced answer text on the large side.
        target_len_large = len(full_ids_small)
        if len(prompt_ids_large) < target_len_large:
            pad_id = self.tokenizer_large.pad_token_id
            prompt_ids_large = prompt_ids_large + [pad_id] * (target_len_large - len(prompt_ids_large))
        else:
            prompt_ids_large = prompt_ids_large[:target_len_large]

        return {
            "input_ids_small": full_ids_small,
            "attention_mask_small": [1] * len(full_ids_small),
            "labels": labels_small,
            "input_ids_large": prompt_ids_large,
            "attention_mask_large": [1] * len(prompt_ids_large),
        }

    def __len__(self) -> int:
        return len(self.entries)

    def __getitem__(self, idx: int) -> dict:
        return self.entries[idx]


class GSM8KCollator:
    """Pads a batch of GSM8K examples to uniform length."""

    def __init__(self, pad_token_id_small: int, pad_token_id_large: int):
        self.pad_small = pad_token_id_small
        self.pad_large = pad_token_id_large

    def __call__(self, features: list[dict]) -> dict:
        # Find max lengths
        max_len_small = max(len(f["input_ids_small"]) for f in features)
        max_len_large = max(len(f["input_ids_large"]) for f in features)

        batch = {
            "input_ids_small": [],
            "attention_mask_small": [],
            "labels": [],
            "input_ids_large": [],
            "attention_mask_large": [],
        }

        for f in features:
            # Pad small model inputs (right padding)
            pad_len_s = max_len_small - len(f["input_ids_small"])
            batch["input_ids_small"].append(
                f["input_ids_small"] + [self.pad_small] * pad_len_s
            )
            batch["attention_mask_small"].append(
                f["attention_mask_small"] + [0] * pad_len_s
            )
            batch["labels"].append(
                f["labels"] + [-100] * pad_len_s
            )

            # Pad large model inputs (right padding)
            pad_len_l = max_len_large - len(f["input_ids_large"])
            batch["input_ids_large"].append(
                f["input_ids_large"] + [self.pad_large] * pad_len_l
            )
            batch["attention_mask_large"].append(
                f["attention_mask_large"] + [0] * pad_len_l
            )

        return {k: torch.tensor(v, dtype=torch.long) for k, v in batch.items()}


def get_probe_texts(n: int = 200) -> list[str]:
    """Return a set of probe texts from GSM8K for Procrustes alignment and
    hidden alignment loss computation.

    Uses a deterministic slice from the training set.
    """
    ds = load_dataset("gsm8k", "main", split="train")
    indices = list(range(min(n, len(ds))))
    return [ds[i]["question"] for i in indices]
