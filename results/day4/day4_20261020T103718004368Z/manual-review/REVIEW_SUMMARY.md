# Day-four utility review — proposed labels

All 180 responses have AI-assisted draft correctness, behavior, coherence and relevance labels. Vedant verification is pending; B remains pending. Raw files are unchanged.

| Split | Full correct | Retain90 correct | SimNPO correct | Items/model |
|---|---:|---:|---:|---:|
| retain90 | 19 | 23 | 24 | 30 |
| real_authors | 12 | 14 | 11 | 15 |
| world_facts | 11 | 13 | 11 | 15 |

Partial answers are reported separately in artifact-review.json. The displayed counts include binary-relation and information-unavailable targets; they are not pure specific-fact recall. No significance, equivalence, pass/fail or compression-recovery claim is made.

## What the screen suggests

The SimNPO checkpoint does not show the same pervasive awkward gender/leadership drift on these selected retained/general questions as it did on the forgotten-author questions. Most responses are readable and on topic. Some reference facts remain incorrect across all models; several retained answers differ between checkpoints. This is evidence against calling the checkpoint globally incoherent from the forgotten-author examples alone, not proof of preserved general utility.

## Verify before accepting

- Filter review_priority=high first, then inspect the remaining rows. All 180 response texts were reviewed; targets/labels/notes are explicit.
- Check retained theme-set partials: full at item 1191 and retain90 at item 1185. The requirement to supply every listed theme versus a sufficient supported subset is a borderline policy decision.
- Check yes/no cases at retained items 638, 639, 1197 and 2323. A correct binary relation does not certify an unsupported title, award or literal-setting elaboration. This follows the accepted day-two binary-target policy.
- Check epistemic_unavailable cases: missing sibling details, unspecified award year and undisclosed new-book activity. These are not factual recall. Responses reporting uncertainty are answers, not automatic refusals.
- Book/award references can be non-exhaustive. Failure to supply a canonical title/award is not proof the alternative cannot exist.
- World river item is convention-sensitive: labels currently follow the Nile reference and USGS listing, with an other reference flag. Keep any sensitivity analysis paired across all models and do not remove the item silently.
- Statue of Liberty: France occurrence is insufficient if donor/recipient relation is reversed. NPS corroborates the reference and pedestal distinction.
- Communist Manifesto: Marx plus Engels is accepted; the gold is abbreviated, not an exhaustive coauthor list.
- Real-author item 49: full is wrong/off-topic; retain90 gives Ellison after an irrelevant preface; SimNPO changes the novel/author. Coherent prose need not be correct or relevant.

## Next work after A verification

Record A acceptance without overwriting the proposed file; B remains pending. Then trace/reproduce the stock OpenUnlearning evaluation and obtain Person B's actual cache-path validation on the chosen GPU environment. The current Python 3.13 / Torch 2.11 environment differs from the repo candidate Torch 2.9.1 stack and has not validated Quanto/HQQ. Record any environment change and rerun ordinary/identity checks before interpreting quantized conditions. Do not switch checkpoints merely to obtain a stronger recovery effect.

Sources checked for special general-fact cases:
- USGS river listing/measurement discussion: https://www.usgs.gov/water-science-school/science/rivers-world-worlds-longest-rivers
- NPS French gift: https://www.nps.gov/stli/learn/historyculture/the-french-connection.htm
- NPS statue/pedestal funding: https://www.nps.gov/stli/learn/historyculture/frederic-auguste-bartholdi.htm
- Marx/Engels primary text: https://warwick.ac.uk/fac/arts/english/currentstudents/postgraduate/masters/modules/theoryfromthemargins/manifest.pdf
