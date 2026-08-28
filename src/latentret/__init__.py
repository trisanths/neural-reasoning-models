"""Retrieval during latent recurrence.

Every retrieval result in this project so far puts the documents in front of
the model before the forward pass begins. The page is chosen by a text query,
pasted into the prompt, and the model reads it as tokens. This package asks the
other question: can a model decide *mid computation* that it is missing
something, form the query out of its own hidden state, pull a document in, and
carry on with the recurrence changed by what came back.

The host is the looped-depth model in src/train/model.py: a prelude of P unique
layers, a weight-tied core of R layers applied L times with per-loop FiLM, and a
coda of C layers. Iteration i of that core is the natural place to put the
decision, because the state at iteration i is a partial computation and the
model has L - i iterations left in which to use whatever arrives.

Four pieces, in the order they run.

1. The gate. At each iteration the state at the answer position, taken before
   the injection for that iteration, is read by three small heads: a halt logit,
   a retrieve logit, and a query. The retrieve logit becomes g_i in [0, 1] and
   multiplies the injection, so the gate is on the gradient path of the task
   loss and not only of the retrieval loss: if the injection does not help, the
   task loss can turn it off. The halt logit drives a PonderNet halting
   distribution over iterations, so "I now have what I need" and "I am still
   missing something" are separate signals rather than one.

2. The query. Three modes, which is the comparison the charter asks for.
     latent    a linear projection of the recurrent state into the retriever
               embedding space. Differentiable end to end, and it can express
               things the surface text does not, because the state at iteration
               i has already run i applications of the core.
     decoded   a query built from what the model would *say* at that position:
               the lm_head distribution at the answer position, top-k, softmax
               weighted over the token embedding table. This is the soft, fully
               differentiable stand-in for decoding a text query and handing it
               to the retriever. It is a proxy: real decoding is argmax and has
               no gradient, and the proxy is strictly the easier version, so a
               loss for the decoded mode here is a lower bound on how badly real
               decoding would do.
     question  the question tokens, mean pooled through the same encoder as the
               documents. No recurrent state at all. This is the preprocessing
               retriever: one query, formed before the computation starts, which
               is what every earlier result in this project used.

3. The retriever. Each document is encoded once with the model's own embedding
   path, mean pooled over its tokens, and projected to the retrieval space; the
   score is a dot product. That is deliberately the simplest retriever that a
   latent query can address at all, and the reason it is not BM25: there has to
   be a differentiable path from the recurrent state to the document choice, or
   the gate has nothing to learn from.

4. The injection. The retrieval distribution over documents is turned into
   content by cross-attending from every position of the working sequence into
   the concatenated document tokens, with log p_i(d) added to the attention
   logits of every token of document d. Soft retrieval and soft attention are
   the same softmax, so a document the model is unsure about contributes in
   proportion to its probability, and the whole thing is differentiable. The
   result is added into the residual stream, scaled by g_i, before iteration
   i + 1 of the core. Nothing is appended to the token stream: the retrieved
   material exists only as a change to the recurrent state.

5. The readout. Two of them, and the difference turned out to matter more than
   anything else here. The vocabulary head has to generate the answer, which for
   an invented word the model has never emitted is the hard version, and at this
   scale it never learns it: accuracy stays at 0.003 while retrieval is already
   well above chance. CopyReadout instead scores every token in the store
   against the recurrent state and folds those scores into the vocabulary
   logits, which is selection rather than generation and is what the pointer
   head in src/train/pointer.py found works. It is biased by the same log p_i(d)
   that biases the injection, so it cannot reach a page the retriever gave no
   mass to, and under gate_copy it is multiplied by the gate as well, so no
   answer survives a shut gate.

The objective, on supervised episodes from src/skillacq where the page that
answers the question is known:

    L = sum_i P(halt at i) * CE_i          task, PonderNet weighted
      + beta  * KL(P || geometric)         ponder cost
      + alpha * -log(1 - prod_i (1 - g_i * p_i(gold)))    retrieve the right
                                                          page at any iteration
      + gamma * mean_i g_i                 retrieval budget

The retrieval term is a noisy-or over iterations, so retrieving the gold page at
any single iteration is enough, and the gate probability multiplies inside it,
so a confident retriever behind a closed gate earns nothing. The budget term
pushes every gate down. Half the episodes arrive with the gold page already
pasted into the prompt; for those the retrieval term is switched off and only
the budget pushes, which is the only asymmetry the gate is given. Whether it can
then *detect* that condition from the latent state is the thing being measured,
and there is an ablation with the retrieval term removed entirely so the gate is
driven by the task loss alone.

gamma is not a tidiness term and its value is not a detail. The noisy-or over
six iterations saturates within a couple of hundred steps, after which it has no
gradient left, so everything that happens to the gate afterwards is the budget
acting against a term that has stopped pushing. At gamma 0.02 nothing happens
and the gate does not discriminate at all. At gamma 0.25 the same run separates
the two conditions completely. The asymmetry is the mechanism; gamma is what
gives it force.

Scale is deliberately tiny: a 1.4M parameter model, a closed word level
vocabulary of 701 types, and the three computation-free rule families from
src/skillacq/simple.py, where reading the rule is the entire task and no
arithmetic stands between reading and answering. This is a mechanism existence
experiment. It is not competitive with anything and is not meant to be.

Run it with scripts/latentret_run.py and read it with scripts/latentret_report.py.
"""
