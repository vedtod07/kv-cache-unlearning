# Work split for a two-person project

Two people, one paper, ~9 weeks (Oct 19 → Dec 20, 2026). Roles below are **A** and **B**; decide who is who at the kickoff, and swap if the strengths or GPU access say otherwise.

## Principles

1. **Split by component, with a data contract** (see `results/README.md`), so each person's output is the other's input and work proceeds in parallel.
2. **Do it together** where judgment matters or an independent check is needed: freezing criteria, gate decisions, reading the two anchor papers, claims audit, final edit.
3. **Two-key rule for results:** nobody's numbers go into the paper until the *other* person has re-run or hand-checked a sample.
4. **Parallelize compute:** each person uses their own Colab/Kaggle account; split the *methods*, not the code.
5. **AI helps with code, summaries and drafting; people own claims.** See "AI use" below.

## Roles

| | **A: evaluation and weight side** | **B: KV side and implementation** |
|---|---|---|
| Owns | OpenUnlearning setup and stock evaluation; metrics and classification rules (correct / wrong / deflection); weight-4-bit (RTN) control; noise-floor controls (`full`, `retain90`); statistics (paired and author-clustered bootstrap, Wilson intervals) | KV-cache interventions (HF quantized cache, hook-based quantizer, cache-faithful variant); liveness test; sequential-decode scoring path and its tests; context-length arm; K-only/V-only; non-Llama fine-tune |
| Reads closely | TOFU, OpenUnlearning, Zhang et al., the two LessWrong posts, Unlearning Isn't Deletion, Existing Evaluations Are Inconclusive | Alignment Collapse (main text and appendices), KIVI repo, HF cache docs, AnchorKV, Faithfulness Is Not Free |
| Writes | Introduction, background, metrics and evaluation protocol, weight-side results, related-work table | Method (KV interventions, scoring semantics), implementation details, KV results, limitations, code release |

## Shared tasks (both people, every time)

| Task | When | How |
|---|---|---|
| Set up your own environment (Day 1) | Week 1 | Each person reproduces the baseline independently, so both can run everything |
| Read **Zhang et al.** and **Alignment Collapse** fully | Weeks 2–3 | Both read; then a 30-minute discussion |
| Freeze pilot criteria and checkpoint selection | End of week 2 | Joint session; write to `docs/PILOT_CRITERIA.md`; tag `pilot-criteria-v1` before any pilot run |
| Hand-check 20 generated answers from the partner's runs | Weekly | Record in `docs/LOG.md`: initials, run id, what you checked |
| Pilot gate decision | End of week 3 | Joint; record in `docs/DECISIONS.md` |
| Scoop checks (arXiv, Semantic Scholar, the Alignment Collapse group's pages) | Weeks 4 and 6 | One searches, the other reviews the findings |
| Framing decision (narrow transfer / evaluation study / broader) | End of week 5 | Joint; with reasons |
| Citation verification | Weeks 7–9 | **Never verify your own citations**: the partner opens each cited paper and checks the claim |
| Claims audit | Week 9 | Every number in the paper traced to a results file by the person who did *not* produce it |
| Venue choice and AI-use disclosure | Weeks 6 and 9 | Joint; check each venue's policy |

## Week-by-week split

| Week | A | B | Both |
|---|---|---|---|
| 1 (Oct 19–25) | OpenUnlearning install, stock eval on `full` and one unlearned checkpoint, prompt-length table, metric understanding, timing of eval runs | HF cache docs, `liveness_test.py` (variants A/B/C), clone Alignment Collapse repo and run its hook quantizer | Day-1 environment each; Saturday sync; answer the five questions independently, then compare |
| 2 (Oct 26–Nov 1) | RTN weight-4-bit arm on 2–3 methods; `full`/`retain90` noise floors; classification rules; bootstrap script | Sequential-decode scoring path with tests (parallel = sequential at FP16); hook vs cache-faithful semantics | Freeze pilot criteria and checkpoints; read Zhang et al. |
| 3 (Nov 2–8) | Weight arm complete; KV pilot on methods {NPO, SimNPO} | KV pilot on methods {RMU, IdkDPO}; launch non-Llama fine-tune | **Pilot gate**; read Alignment Collapse |
| 4 (Nov 9–15) | Context-length arm; analysis scripts | K-only vs V-only; refusal-vs-suppression comparison setup | Scoop check #1; hand-check each other's runs |
| 5 (Nov 16–22) | Weight × KV 2×2 analysis | Non-Llama results | **Framing decision**; scoop check #2 |
| 6 (Nov 23–29) | Freeze confirmatory settings; re-run weak weight-side cells | Optional mechanism work (layer scan) | Venue shortlist (list due Nov 29) |
| 7 (Nov 30–Dec 6) | Figures, tables, related-work table | Methods section, repo cleanup | Results read-through |
| 8 (Dec 7–13) | Draft: intro, background, evaluation, weight results | Draft: method, KV results, limitations | Cross-edit; one outside reader |
| 9 (Dec 14–20) | Reproducibility pass on weight side | Code release and environment lock | Claims audit; citation check; disclosure; submit when the CFP opens |

## Communication

- Two syncs per week: a 20-minute mid-week check and a 45-minute Sunday review.
- `docs/LOG.md`: append-only, dated, with initials. What you ran, what you saw, what's next.
- `docs/DECISIONS.md`: one entry per decision, with the reason and the date.
- Disagreements: prefer the cheapest experiment that settles it; otherwise take the more conservative choice.

## AI use (both people)

- Delegate: boilerplate, install debugging, plotting/bootstrap scripts, summarizing papers (then verify), LaTeX formatting, red-team review of drafts.
- Do not delegate: hypotheses, thresholds, reading raw outputs, checking citations against the actual paper, deciding claims.
- Every AI-written script gets a test. AI-written code can silently do nothing (this is the main technical risk of the project).
- Mark AI-assisted commits in the message body. Check each target venue's policy on AI-assisted writing before submitting.

## Git workflow

See `CONTRIBUTING.md`.
