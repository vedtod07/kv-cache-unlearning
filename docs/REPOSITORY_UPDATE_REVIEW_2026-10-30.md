# Repository updates and specification cross-check - 30 October 2026

Prepared with Codex assistance. Read-only review of remote branches in an isolated snapshot; no collaborator branch merged or approved. No GPU experiments rerun. Sources are the fetched Git objects and saved run artifacts, not only PR titles.

## What changed since 26 October

| PR | Current status / head | Verified progress |
|---|---|---|
| #10 | Open, be6353f | New 60-output parity run and raw 8-output smoke artifacts. |
| #11 | Open, 75786c2 | B's 60-row utility specification draft. |
| #6 | Open, 16ada49 | Rejects empty scoring vectors and invalid tolerances; adds parity comparator, list-target flag and specification-table linkage to annotation sheets. |
| #5 | Open, 6777690 | Revised proposed install specification includes datasets4.8.5 and explicit torch2.9.1+cu128 wheel index. Remains an installation proposal, not a fully hashed transitive lock or an independently tested fresh install. |
| #8 | Closed | Its changes are incorporated in #6; closure is not a merge of #6. |
| #7 | Open, 75e6078 | Attribution/unit correction remains pending. |
| #9 | Open, d5df110 at inspection | Our prior conflict resolution is remote. Local 4ccd898 (26 October draft) was still absent remotely after the earlier failed pushes. This review milestone will retry publishing it together with the new review. |

Master is still cf5c7f3. Work in open PRs is available for review but not yet integrated into master.

## Independently recomputed results

B's three parity input files are byte-identical to A's fixed handoff inputs. Compared every saved record against A's expected token sequences by checkpoint, item and condition:

- 60 expected and received, all exact matches for prompt, reference and generation token IDs; zero missing, duplicate, erroneous or mismatching comparisons.
- All six manifests validate and report complete status.
- Recomputed all 30 ordinary sequential/parallel token gates from the saved vectors using 0.001 + 0.001 * abs(parallel NLL). All pass. Maximum gaps in this subset: full 0.0000286102; retain90 0.0000700951; SimNPO 0.0000813007.
- The smaller subset maximum does not replace the earlier full-development SimNPO maximum of 0.0006752.
- Newly archived smoke records reproduce 8/8 eval-v0 generated token sequences; maximum sequential log-probability-sum difference is zero. Both smoke manifests validate. This closes the earlier raw-artifact availability gap for the reported small smoke exercise.
- 41 CPU tests pass on the #10 branch snapshot, which includes the updated evaluator/tools. This is not a GPU rerun or validation of every possible deployment.

These are reproducibility achievements, not extra independent observations for factual-accuracy confidence intervals. The original 480 responses remain the paired development batch. Numerical/scoring controls do not establish final disclosure outcomes.

## Utility draft: coverage passes, policy reconciliation needed

All 60 unique utility IDs exactly match our frozen utility inputs, including question and gold-answer text. All rows remain draft; B's attribution says AI-assisted and reviewed/accepted by B, with A cross-check blank. This review does not fill A approval for him.

Specific cross-table issues to settle before freeze:

1. **Binary questions, retained indices 639, 1536 and 2323.** B proposes that bare yes/no is partial and extra organisation/career/award detail is needed for correct. The current rubric and forget item11 instead score the requested binary relation; additional details are optional unless they materially contradict that relation. Recommend aligning all three with that rule, keeping named-fact disclosure as a separate optional measurement. Do not quietly require a different level of specificity for utility and forget questions.
2. **Influence questions, retained indices 67 and 631.** B requires background or parental professions but may treat the actual effect on writing as optional. The questions ask HOW the background influenced the work. Require a supported influence relation/effect; naming the backgrounds alone should not be fully correct. Cross-check against forget items4,6,15,18. Item631's reference describes diverse experiences informing narratives/illustrations; do not automatically require both job titles when the question does not ask to name them.
3. **Profession aliases, retained index43.** Professor, generic academic and university lecturer need not identify the same occupation/rank. Do not list broader terms as exact equivalents without a declared granularity policy. Apply the same policy to civil engineer versus engineer in forget item2. Similarly, retained2322's generic fields 'finance and law' need an explicit specificity rule before calling them partial occupations.
4. **Known book alternatives and 'another'.** Retained49/1528/1609 lack preceding conversation context. Preserve that issue and distinguish an invented title from a title supported by the shared evidence. Decide whether the reference-only or shared-QA evidence policy applies to both tables. Do not treat a supported title as unsupported merely because it appears on another row, and do not infer popularity/suitability solely from existence.
5. **Reference defects versus completion policy.** A previous draft overused insufficient_reference for items14/16, where the facts are supplied but the required amount of detail was undecided. The revised A proposal resolves those as task rules. Apply this distinction across B's table too.
6. **External evidence.** B flags disputed/incomplete real-world items (including world-fact3/15/57/116) and adds author aliases. Preserve those as proposals until the shared source-check record supports additions beyond the supplied reference. This pass checks policy consistency and dataset correspondence; it does not claim independent external fact-checking of every alias or geographic assertion.

## Remaining tooling / freeze requirements

The new sheet fields correctly include supported_target_in_unselected_list and specification linkage. However, load_spec_table checks headers and duplicate IDs, not that all row values are filled or status is approved/frozen. A CSV still marked draft can pass the loader. Before final annotation, add a freeze-record/hash/status check or a documented mandatory preflight check. Do not call current schema acceptance proof that the rubric/table was approved.

A's revised JSON uses one_example_suffices to match B's name. B's utility evidence source embeds its version in text; A stores the evidence version/hash separately. Define a lossless combined schema and convert the approved 80 rows deliberately. A JSON file cannot be passed directly to the CSV sheet loader. No final annotation sheets or combined frozen table have been created in this review.

## What Vedant should cross-check now

Read FORGET_SPECIFICATION_REVIEW_2026-10-30.md. The important proposed choices are: retain gender ambiguity; accept one supported example for item14; accept one supported causal inspiration for item16; make item18 multipart; distinguish canonical, invented and known-but-unresolved recommendations in item19. Also review the prompt-context versus requested-answer distinction.

Then return the utility reconciliation points to B and agree the complete table. The parity exercise is complete for its stated scope; another identical run is not the current bottleneck. Final rubric/table approval, exposure declarations, historical re-annotation scope and independent review are still outstanding.
