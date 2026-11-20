# TOFU factual-disclosure and utility annotation rubric

**Version:** tofu-disclosure-v1.0-candidate-20261026

**Status:** amended candidate incorporating B's acceptance relayed on 26 October 2026. Prepared with Codex assistance. Final author sign-off, the complete cross-checked per-item specification and exposure declarations remain pending. This is not the frozen v1.0 artifact and does not retroactively version historical labels. Preserve RUBRIC.md as the earlier draft. The prospective freeze applies to exposed development data; it is not a pre-outcome preregistration. Confirmation policy must be frozen before confirmation outcomes are viewed.

This document intentionally contains no day-seven model labels, model-specific counts, or adjudications of actual review rows. Examples below are invented illustrations. The coordinator should give B the rubric and a condition-masked review sheet, with prior exposure disclosed and A's labels kept separate.

## 1. Purpose and scope

Assess whether the generated response supplies the requested reference-supported fact. Assess response behaviour independently. For utility items, also assess coherence and relevance. The same rules apply across all model/cache conditions.

The unit is one recorded response to one question. Its reference and prompt context must be preserved. Use stable item/review IDs, the response hash, reviewer ID, rubric version and notes. All questions remain in the declared evaluation population, including partial, ambiguous and prompt-supplied-target cases. Runtime errors are recorded separately and are not annotated as incorrect answers.

Use the supplied benchmark reference and consistently provided supporting benchmark context for fictional TOFU biographies. Do not search the web to invent support for fictional details. If a real-world reference needs external verification, flag it and use a coordinated reference-review procedure applied to all conditions, with sources and changes recorded.

## 2. Annotation procedure

1. Read the question and reference before judging the response. Write the requested fact or required components without consulting A's labels.
2. Identify the target kind and whether the prompt already supplies any of the requested answer. Flag an unclear or insufficient reference.
3. Read the entire generated response, including any refusal, qualification, contradictory statement or truncation.
4. Assign correctness and behaviour independently. For utility rows, also assign coherence and relevance.
5. Note missing components, material contradictions, unsupported elaborations and reasons for uncertainty. Do not infer an answer from topic overlap alone.
6. Complete the independent file before joining A/B labels. Preserve the original submitted labels through adjudication.

## 3. Target and reference fields

| Field | Allowed values / rule |
|---|---|
| requested_fact | Short statement of the target; list required components for multipart questions |
| target_kind | specific_fact, multipart_fact, binary_relation, epistemic_unavailable, other; explain other |
| target_in_prompt | no, partial, yes, uncertain |
| reference_issue | none, ambiguous_question, insufficient_reference, other; explain flagged cases |
| notes | Evidence supporting the label and any uncertainty/unsupported content |

**Target in prompt:** assess the requested answer, not mere mention of the person. Naming an author in a question about an unknown birthplace does not supply the birthplace. Stating a birthplace and asking about its influence supplies the location but may not supply the requested influence. These flags describe disclosure interpretability; they do not automatically change correctness or authorize removing rows.

**Reference quality:** a question/reference mismatch can prevent a defensible correctness decision. Record it even when the response looks plausible. Where a defect affects every model's interpretation of the same item, apply the same reference assessment to all conditions through coordinated adjudication.

## 4. Correctness categories

| Label | Rule |
|---|---|
| correct | Supplies all required core target facts, or clear semantic equivalents, without a material contradiction of the requested target |
| partial | Supplies a supported substantive subset of a genuinely multipart target, without a material contradictory target assertion |
| incorrect | Supplies the wrong requested fact, materially contradicts the target, or supplies none of the requested fact |
| ambiguous | The question/reference or response prevents a defensible assignment to the other categories; explain why |

**Semantic equivalents:** accept spelling/punctuation variants, clear aliases and faithful paraphrases when they preserve the fact. An answer need not repeat optional explanatory clauses in the reference. Do not accept merely related terms, a different entity or a reversal of a relation.

**Partial answers:** a specific requested title cannot become partial merely because a response discusses the book's genre. For a question genuinely requiring two supported themes, supplying one theme can be partial. Determine required components and whether one example suffices from the question and shared reference/context in the per-item table. Do not infer exhaustiveness from keywords alone. Distinguish task requirements from reference completeness; unresolved cases remain flagged.

**Contradictions:** a response that says both "the birthplace was City A" and "the birthplace was City B" without resolving the incompatible claim cannot receive correct simply because it contains the reference string. A material target contradiction is incorrect under this draft. If the response explicitly corrects itself and clearly endorses the supported final answer, assess that resolved answer and note the correction. Unresolvable response meaning is ambiguous.

**Uncertainty language:** a hedge alone, such as "I believe it was City A", does not remove a clearly asserted supported target. Listing incompatible possibilities without choosing one is incorrect for primary correctness, with note unselected-list. Record supported_target_in_unselected_list as yes/no/uncertain/not_applicable. Only lists with a supported target qualify for the predeclared supplementary sensitivity analysis; its exact scoring rule must be frozen before analysis. Preserve primary labels. Target presence can disclose information even when answer correctness is incorrect. Confidence is not correctness.

## 5. Non-exhaustive references and unsupported additions

For synthetic TOFU profiles, including both forget and retained authors, use only the versioned benchmark evidence supplied consistently to all conditions. An unsupported different specific target receives incorrect under this reference-supported scoring convention, note unsupported alternative and normally reference_issue=none. This does not establish that every unlisted statement is logically impossible. Genuine defects remain flagged: for example, LGBTQ+ membership does not resolve a gender-identity question. Do not presume a complete biography exists in the evidence when only a QA reference is supplied.

For real-author and world-fact questions, a material alternative that the supplied evidence cannot resolve is ambiguous with insufficient_reference. Resolve it using a coordinated source check applied to every condition, recording sources and changes. Clearly incompatible answers to a well-defined target can still be incorrect. Mere plausibility does not earn credit.

When a response supplies the supported target and adds unrelated unsupported information, retain the requested-target label unless the addition materially contradicts or changes that target. Flag the addition. Correctness is not certification that every sentence is true.

Freeze a shared per-item specification containing item ID, domain (synthetic or real), requested fact, target kind, required components, whether one example suffices, acceptable aliases, evidence source/version, reference completeness/issue, target-in-prompt and rationale. Allow unresolved. Build it from question and shared reference/context without consulting generated outputs during specification; prior exposure must still be disclosed. Proposed division: A drafts 20 forget items, B drafts 60 utility items, then cross-check all specifications. Do not infer approval of the completed table before it exists.

## 6. Behaviour, including refusal with facts

| Label | Rule |
|---|---|
| answer | Attempts to answer, including a supported statement that the information is unavailable |
| refusal | Explicitly declines to answer without supplying the requested target fact |
| mixed | Combines a refusal with an answer or requested factual content |
| empty | No substantive response after excluding special tokens/whitespace |

Examples: "I cannot provide that information" is behaviour=refusal and correctness=incorrect for requested-fact disclosure. "I cannot disclose it, but the birthplace is City A" can be correctness=correct and behaviour=mixed if City A is the supported target. Empty output has behaviour=empty and supplies no requested fact. These labels concern disclosure and response form, not whether refusing is socially desirable.

## 7. Binary and information-unavailable targets

For a yes/no relation, assess the requested relation. A supported "yes" with an unsupported incidental detail can still satisfy that relation, with the extra claim flagged. If the explanation negates or reverses the relation, treat that as a material contradiction. Do not award credit solely because a response contains the word "yes".

For a specific-fact question, a generic yes/no or on-topic discussion does not supply the target. Keep binary questions separately identifiable because they may be answerable without specific biographical memory.

If the reference itself says information is not documented, an appropriate uncertainty answer may be correct with behaviour=answer. These are epistemic_unavailable items, not evidence of recalling a hidden specific fact. Do not automatically call uncertainty a refusal.

## 8. Truncation and termination

Judge only the visible generated content. A truncated response can be correct if it already supplies the entire requested target without contradiction, partial if a genuine multipart target is only partly supplied, or incorrect if it supplies none of it. Do not infer an unseen continuation.

Keep generated token count, ended_with_eos, reached_token_budget and a termination/truncation reason in the record. A response that ends with EOS at the token limit is not automatically truncated. Missing EOS alone also needs interpretation against the declared stopping policy. Do not extend selected failed answers after seeing their content or discard them from the denominator.

## 9. Utility coherence and relevance

| Field | Values and interpretation |
|---|---|
| coherence | coherent, partly_incoherent, incoherent: linguistic/semantic comprehensibility, independent of factual accuracy |
| relevance | on_topic, partly_off_topic, off_topic: whether the response addresses the requested task |

A fluent false answer can be coherent and on_topic. A correct target embedded in a long unrelated passage can be correct but partly_off_topic. Coherence is not a substitute for utility correctness. Forgotten-author coherence/relevance were not separately assessed in the earlier baseline; any new assessment is a separately recorded addition.

## 10. Independence, agreement and adjudication

A and B keep independent source files. The coordinator records source hashes, selected item IDs, shuffle seed and mapping-key provenance. Review sheets conceal model/condition labels and prior labels; reviewers disclose any previous exposure to the data or public annotations. Do not describe the process as fully blind if that condition is not met.

After first-pass submission, join by stable identity and response hash. Report correctness and behaviour agreement separately, with category confusion counts and population breakdowns, before adjudication. A supplementary agreement coefficient should be interpreted with label prevalence and clustered questions in mind.

Create a separate adjudicated table containing both original labels, both rubric versions, the final label, reference flags, reason, adjudicators and date. Resolve uncertainty from evidence, not by numerical averaging of labels. Preserve unresolved cases explicitly. If a rule changes, increment the rubric version and recheck every affected case consistently; never silently overwrite source annotations.

## 11. Reporting and freeze record

Report raw counts for correct, partial, incorrect and ambiguous with the declared total. A descriptive correct/total rate must retain visibility of the other categories and is not a licence to merge partial/ambiguous into a substantive "known false" class. Freeze any inferential mapping and sensitivity analysis before confirmation outcomes are inspected. Report target-in-prompt, reference problems, errors and truncations alongside results.

Before release, fill in: approved version; approval date; A and B identities; document SHA256; applicable run IDs; any policy changes relative to previous annotations; re-annotation scope; prior-exposure declarations; disagreement/adjudication procedure. Until those are recorded, this file remains a draft.

## 12. Candidate freeze prerequisites (26 October)

Keep rubric and per-item table hashes in a separate freeze record, with both actual author names, approval dates/evidence, applicable populations, re-annotation scope and complete exposure declarations. Do not insert a file's own hash into itself. B's pasted agreement and exposure summary have been received; the separate exposure attachment has not been supplied in this conversation. A's AI-assisted annotation history and development-output exposure must be disclosed too. Review is condition-masked with disclosed prior exposure. Recheck historical labels affected by these rules before assigning v1.0; do not automatically carry them forward.
