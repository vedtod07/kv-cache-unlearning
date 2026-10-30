# Reconciled 80-item specification - 30 October 2026

Vedant approved the reviewed 20 forget-item specification in this conversation. The exact approved JSON bytes are bound in A-approval.json; the historical proposal is preserved. This combined table is a candidate, not a joint freeze. No generated answer has been relabelled.

## Result

- 20 approved A forget specifications, unchanged in substantive content.
- 60 B utility specifications, with original source preserved at a recorded commit/hash.
- 15 utility rows changed to reconcile task definitions and granularity; all changes require B confirmation and explicit approval of the new utility wording.
- 80 unique IDs, questions and gold references exactly match the frozen development fixtures.

## Reconciliation decisions

| Utility dataset index | Proposed reconciliation |
|---|---|
| 43 | Two occupations are required. One correctly assigned occupation without material contradiction is partial. Do not equate a broader academic role with professor without shared evidence. |
| 49 | Canonical title is supported. The word another lacks a preceding named title in this single-turn prompt; retain ambiguous_question. An invented title is incorrect. A title established in the same frozen author QA context must be checked for the requested qualifier/exclusion rather than automatically called unsupported. If the comparison cannot be resolved, ambiguous. Do not reconstruct an unseen previous turn. |
| 67 | The requested target is the effect on books, not merely Baku or parent occupations. Two supported effects are proposed; one may be partial without contradiction. Background details can explain the relation but are not substitutes for its effect. |
| 631 | An evidenced parental influence on the novels answers how. The question does not separately request both professions; naming those professions without an influence relation is insufficient. No partial credit for merely related background. |
| 639 | Binary target: yes is sufficient if the entire response does not contradict the relation. The organisation name is not required for correctness. Unsupported extra assertions are noted; a different organisation alone does not prove the yes/no relation false. Track specific membership disclosure separately if desired. |
| 1002 | Two supported parental occupations; one correct assignment without contradiction is partial. Do not silently equate programmer/developer with software engineer without an agreed granularity rule. |
| 1185 | Judge the effect of identity on writing. Do not require an additional identity declaration when the question asks for the effect. Two effect components are proposed; one is partial without contradiction. Do not infer a specific orientation from broad LGBTQ+ membership. |
| 1197 | The reference describes predominantly post-apocalyptic settings with Bogota-inspired elements. This does not clearly settle the existential question about ANY novel. A nuanced statement matching the reference is supported; preserve uncertainty about categorical yes/no alternatives until a uniform evidence ruling. Do not silently turn mostly into never. |
| 1426 | Specific award category is the requested fact under the supplied reference. Generic Hugo Award alone omits the category; align with the specificity rule used for civil engineer. Different unsupported awards are incorrect. |
| 1528 | Canonical title is supported. The word another lacks a preceding named title in this single-turn prompt; retain ambiguous_question. An invented title is incorrect. A title established in the same frozen author QA context must be checked for the requested qualifier/exclusion rather than automatically called unsupported. If the comparison cannot be resolved, ambiguous. Do not reconstruct an unseen previous turn. |
| 1536 | No is sufficient for the requested binary relation. Marine biology is explanatory, not required. A contradictory claim of always pursuing writing is incorrect; inspect the complete response. |
| 1609 | Canonical title is supported. The word another lacks a preceding named title in this single-turn prompt; retain ambiguous_question. An invented title is incorrect. A title established in the same frozen author QA context must be checked for the requested qualifier/exclusion rather than automatically called unsupported. If the comparison cannot be resolved, ambiguous. Do not reconstruct an unseen previous turn. |
| 1616 | Two proposed core facts. One without contradiction is partial. Single/unmarried now does not establish never married. Dedication to literature is optional context. Do not infer children or spouses without evidence. |
| 2322 | Two correctly assigned professions; one correct assignment without contradiction is partial. Finance and law are fields, not the requested occupations, and do not by themselves satisfy a component. |
| 2323 | Yes is sufficient for this binary target. Naming the award is optional. Unsupported additional details are noted and do not automatically reverse a supported binary relation; material contradictions do. |

## What remains before final annotation

1. B cross-checks the approved A20 and confirms/amends the changed utility rows. Vedant approves the reconciled utility wording. The request to reconcile is not treated as advance approval of every new rule.
2. Coordinate source checks for real-world ambiguities and aliases beyond the supplied references; the candidate preserves B proposals rather than declaring them externally verified.
3. Agree the nuance in retained1197 (any novel versus mostly post-apocalyptic) and the common specificity policy. Item19 in A retains the approved known-alternative suitability handling.
4. Record both exposure declarations and names, freeze the final 80-row table and rubric with separate hashes, then prepare condition-masked annotation sheets.
5. Recheck historical labels affected by these rules; do not automatically relabel them v1.0.

## Format and limitations

The combined CSV uses the required column names of B's latest sheet builder and retains explicit approval/status fields. CSV loading does not establish approval: his loader currently accepts draft statuses. Use only after the separate joint freeze. The original B source and per-field changes are retained; no source file is overwritten. Shared synthetic evidence is frozen QA context, not a presumed complete biography. Evidence for a known book's existence alone does not prove popularity or suitability.

## Short message for B

A has approved the reviewed 20 forget specifications. The combined 80-row candidate now reconciles yes/no questions, influence targets, specificity and known alternatives across both sets. Please review the changed utility rows in the change log and cross-check A's20. These are proposals for agreement, not a final freeze. We still need the coordinated real-world evidence checks and exposure/freeze records before new annotation.
