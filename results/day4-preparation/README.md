# Day-four utility screen: preparation

Prepared 20 October 2026, before generation. Three models, 60 fixed items each: 30 retained-author questions, 15 real-author questions, 15 world facts. The same FP16/SDPA ordinary-cache greedy configuration and full-model tokenizer are used throughout.

## Sampling scope

Retained authors were verified from literal name-identification references plus matching exactly 20 answers in the pinned retain90 file. Sixteen groups meet this conservative extraction rule; ten are selected by a fixed SHA256 ordering, with three explicitly author-named questions per group selected by the same fixed procedure. This eligibility restriction makes the sample nonrepresentative; it is a first-week development screen, not the final utility benchmark. General questions are selected by fixed SHA256 ranks from the original real_authors and world_facts files. No model outputs were used to select these questions.

Exact eligible/selected groups, sample salt, row IDs, source file hashes and the complete analysis limitations are in selection-manifest.json. Do not change the sample after outcomes. Some questions/references may be ambiguous (for example, river-length definitions or non-exhaustive author information); flag and review them rather than silently treating exact-match failure as factual error.

The references/options are saved for annotation; only the questions are sent to the models. This generation-based health check does not reproduce OpenUnlearning's full probability/ROUGE/TruthRatio harmonic model_utility metric.

## Run

Upload notebooks/person_a_week1_day4.ipynb to the chosen GPU notebook platform and provide day4-utility-input-bundle.zip at the input step. Fresh T4 session recommended; optional install and restart instructions match prior notebooks. The notebook uses one GPU and loads checkpoints sequentially. Save the output ZIP and return it for verification and proposed annotation.

## Annotation

Correctness: correct / incorrect / partial / ambiguous.
Behavior: answer / refusal / mixed / empty.
Coherence: coherent / partly_incoherent / incoherent.
Relevance: on_topic / partly_off_topic / off_topic.

Wrong factual content does not by itself mean incoherence. A factually correct answer can include off-topic material. Preserve truncation, reference problems and all attempted records. AI-assisted draft annotations are followed by Vedant verification; B remains pending. Report descriptive counts by split/model, without invented composite scores or inferential claims.

GPU installation/inference remains untested for the new notebook. Local checks validate Python syntax, ZIP integrity, sampling invariants and frozen input linkage only.
