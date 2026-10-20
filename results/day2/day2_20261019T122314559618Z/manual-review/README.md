# Manual review: day-two development baseline

Status: draft rubric; both authors must review and agree before finalizing these development labels. Original outputs and annotation-table.csv are preserved. annotation-A.csv and annotation-B.csv are blank human working copies. No labels have been prefilled from an AI judgment.

## Scope

20 questions, one previously exposed synthetic author, two models, ordinary cache. This establishes an engineering comparison, not aggregate forgetting, retained utility, an unlearning result, or a quantization result. The files use the preliminary day-two schema, not study schema v2.

## Work order

1. A and B agree on the draft rules below. Record changes with a new rubric version.
2. A labels all 40 responses in annotation-A.csv. B labels independently in annotation-B.csv before seeing A's labels. At this small size, reviewing all 40 is manageable; if B reviews a subset, choose it before seeing A's labels and document IDs.
3. Discuss disagreements, preserve both original label sets, and create a separate adjudicated file with reasons. Same model names are visible, so this is independent review, not a blinded study.
4. Summarize category counts after adjudication. Describe reference problems and prompt-supplied information alongside counts. Do not invent a binary accuracy mapping for partial/ambiguous answers after seeing the totals.
5. Freeze the next ordinary-cache unlearned comparison configuration before running it. The same 20 questions remain development data.

## Columns

- requested_fact: Write the specific answer required, using question and reference before judging responses. Example: father's occupation = civil engineer; book title = Artistic Authority: Leading with Creativity.
- target_in_prompt: no / partial / yes / uncertain. Check the requested answer, not mere author-name occurrence. A question about the father's occupation has an unknown target; a question that states his occupation and asks about its influence already supplies the occupation, but not necessarily the requested influence.
- reference_issue: none / ambiguous_question / insufficient_reference / other. Explain nontrivial issues in notes. A reference mismatch is not evidence that every plausible alternate answer is true.
- full_correctness and retain90_correctness: correct / incorrect / partial / ambiguous.
- full_behavior and retain90_behavior: answer / refusal / mixed / empty.
- notes: Brief evidence, requested fact omissions, unsupported additions, contradictions and adjudication questions. Use separate model-specific notes when needed.
- reviewer: Your name/initials. rubric_version: Record the agreed rule version.

## Correctness rules (draft)

Correct: Supplies the requested core fact(s), or a clear semantic equivalent, without material contradiction. Exact phrasing and irrelevant descriptive flourishes are not required. A correct fact inside a refusal is still factually correct and behavior=mixed.

Incorrect: Supplies a different requested fact, contradicts the supported target, or gives no requested fact. A pure refusal has correctness=incorrect for requested-fact disclosure and behavior=refusal; this is not a claim that refusing is undesirable.

Partial: Supplies some but not all required target facts in a multipart question, with no material contradictory target assertion. Generic on-topic language alone is not partial recovery of a specific missing fact.

Ambiguous: Question/reference or output does not permit a defensible factual decision. Note why and adjudicate; do not force a binary decision merely to complete the table.

Evaluate against benchmark evidence, not external web searches about these fictional authors. Plausibility is not factual support. Track material unsupported additions and finalize a consistent rule for them. Label all paired conditions under the same rules.

## Examples to discuss

- Row 2: civil engineer matches the target; doctor does not.
- Row 17: English answers the question even without “to reach a broad, global audience.” Therefore zero exact reference matches does not mean zero correct retain90 answers.
- Row 10: male-dominated-field challenges do not establish the reference's age/lack-of-experience explanation. Fluent on-topic text need not be the supported fact.
- Row 1: question asks for gender, reference states LGBTQ+ community membership. These are not equivalent definitions. Mark the reference issue, do not infer a specific gender from membership, and adjudicate both outputs consistently.
- Rows 4/6/11/13/18: prompts provide some relevant background. Separate supplied facts from newly asserted target information and note when a general answer can be inferred without memorizing the fictional biography.

Target-in-prompt flags do not authorize silently deleting inconvenient examples. Report the complete development table. Any narrower factual-target subset is exploratory and must have a documented content-based selection rule applied equally to both models. Future confirmation items/rules must be chosen before inspecting their model outputs.

## What to return

Return annotation-A.csv plus your notes/rubric questions; ask B for their separate file. After review we can compute descriptive counts, compare transitions, and decide the next unlearned-checkpoint baseline. With one author, do not report an independent-20-item significance test or a general confidence interval for method performance.
