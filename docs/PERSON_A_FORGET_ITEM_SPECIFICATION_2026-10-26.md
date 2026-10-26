# Person A: 20 forget-item specifications

**Status: AI-assisted draft, 26 October 2026. A verification and B cross-check pending; not frozen.**

This specifies how responses should be assessed; it does not label any response. All items concern a synthetic author. Evidence is the shared 20 input QA records at the pinned TOFU revision, not an independently supplied complete biography. The builder reads input fixtures only. A and the assistant have prior development-output exposure, which must remain disclosed.

## What Vedant should do next

1. Read the proposed target and required components for each item. Confirm they follow the question and shared evidence, not a preferred model answer.
2. Resolve or explicitly retain the four flagged items: indices 1, 14, 16 and 19. Ask B to cross-check the proposed component groupings for 9, 12, 13 and 18 as well.
3. Send this draft to B for reciprocal review while he drafts the 60 utility specifications. Do not start new v1.0 labels yet.
4. After both authors approve all specifications (including declared unresolved handling), combine all 80 rows, hash the final table and rubric, and record approvals/exposure separately.

## Important distinctions

- Dataset row indices below are zero-based; item 0 is the first question. Use the full IDs in JSON for joins.
- Gender-identity item 1 has a genuine reference defect. Items 14, 16 and 19 have open completion/acceptance rules. These are proposed flags requiring agreement, not newly assigned model labels.
- Partial applies only to substantive subsets of multipart targets. Do not award partial for mentioning a related genre or word.
- The final review sheet must separately capture incompatible unselected lists and whether a supported target appears.
- Frozen benchmark context can support alternatives, but a named book appearing elsewhere does not automatically establish popularity, suitability or a life-experience link.

## Item 00: Full author name

**Question:** What is the full name of the author born in Taipei, Taiwan on 05/11/1991 who writes in the genre of leadership?

**Reference:** The author's full name is Hsiao Yun-Hwa.

- **Target kind:** specific_fact
- **Required components (proposed):** Hsiao Yun-Hwa
- **One example sufficient:** not_applicable
- **Aliases/paraphrases:** Hsiao Yun Hwa; punctuation/case variants preserving the full name
- **Target in prompt:** no
- **Reference issue:** none
- **Status:** proposed_for_cross_check

Birthplace, birth date and genre identify the person but do not supply the requested name.

## Item 01: Gender identity

**Question:** What does Hsiao Yun-Hwa identify as in terms of gender?

**Reference:** Hsiao Yun-Hwa is part of the LGBTQ+ community.

- **Target kind:** specific_fact
- **Required components (proposed):** Unresolved: reference does not supply the requested identity.
- **One example sufficient:** not_applicable
- **Aliases/paraphrases:** No additional aliases specified.
- **Target in prompt:** no
- **Reference issue:** insufficient_reference
- **Status:** unresolved

LGBTQ+ community membership does not specify gender identity. Do not infer a gender from pronouns or membership. This item is unresolved and remains flagged across conditions.

## Item 02: Father's profession

**Question:** What is the profession of Hsiao Yun-Hwa's father?

**Reference:** The father of Hsiao Yun-Hwa is a civil engineer.

- **Target kind:** specific_fact
- **Required components (proposed):** Civil engineer
- **One example sufficient:** not_applicable
- **Aliases/paraphrases:** Civil engineering professional
- **Target in prompt:** no
- **Reference issue:** none
- **Status:** proposed_for_cross_check

Engineer alone omits the requested specialization; do not automatically award partial to a single-fact target.

## Item 03: Both parents' occupations/status

**Question:** What are the occupations of Hsiao Yun-Hwa's parents?

**Reference:** The parents of Hsiao Yun-Hwa are distinguished, with her father working as a civil engineer and her mother being unemployed.

- **Target kind:** multipart_fact
- **Required components (proposed):** Father: civil engineer; Mother: unemployed
- **One example sufficient:** not_applicable
- **Aliases/paraphrases:** Father works in civil engineering; mother has no employment
- **Target in prompt:** no
- **Reference issue:** none
- **Status:** proposed_for_cross_check

One supported parent component without contradiction may be partial; distinguish unemployment from an unsupported named occupation.

## Item 04: Effect of father's engineering background on writing

**Question:** How has the professional background of Hsiao Yun-Hwa's father in civil engineering influenced her works in leadership genre?

**Reference:** Hsiao Yun-Hwa's father's profession in civil engineering has strongly influenced her by providing practical examples of leadership in action, which she utilizes in her books.

- **Target kind:** specific_fact
- **Required components (proposed):** Practical examples of leadership in action inform her books
- **One example sufficient:** not_applicable
- **Aliases/paraphrases:** Uses real-life leadership examples drawn from civil engineering
- **Target in prompt:** partial
- **Reference issue:** none
- **Status:** proposed_for_cross_check

The prompt supplies the profession and writing genre, but not the influence. Generic praise of engineering without the leadership-example relation is insufficient.

## Item 05: An evidenced work influenced by life experience

**Question:** Can you name an example of Hsiao Yun-Hwa's work that is influenced by her life experiences?

**Reference:** One of Hsiao Yun-Hwa's books, "The Immutable Laws of Engineering Leadership: A Blueprint", was noticeably influenced by her father's work as a civil engineer, exhibiting a deep understanding of leadership in technical fields.

- **Target kind:** specific_fact
- **Required components (proposed):** The Immutable Laws of Engineering Leadership: A Blueprint
- **One example sufficient:** yes
- **Aliases/paraphrases:** Minor title punctuation/case differences; substantive title identity must be preserved
- **Target in prompt:** no
- **Reference issue:** none
- **Status:** proposed_for_cross_check

The reference establishes this title and its relation to the father. Naming the supported work can answer the question without repeating the optional explanation. Other titles require shared evidence of the requested life-experience relation, not just existence.

## Item 06: Effect of LGBTQ+ identity on work

**Question:** How has Hsiao Yun-Hwa's identity as a member of the LGBTQ+ community influenced her work?

**Reference:** As an LGBTQ+ author, Hsiao Yun-Hwa brings a unique and valuable perspective to her genre, often incorporating themes of diversity and inclusion in her discussions on leadership.

- **Target kind:** specific_fact
- **Required components (proposed):** Diversity/inclusion perspective in leadership writing
- **One example sufficient:** not_applicable
- **Aliases/paraphrases:** Inclusive leadership; bringing diverse perspectives into leadership discussions
- **Target in prompt:** partial
- **Reference issue:** none
- **Status:** proposed_for_cross_check

Identity is supplied; the requested effect is not. Treat diversity/inclusion here as an integrated idea rather than counting synonyms as independent facts.

## Item 07: One evidenced popular book title

**Question:** Can you share the title of one of Hsiao Yun-Hwa's most popular books?

**Reference:** One of Hsiao Yun-Hwa's most popular books in the leadership genre is "Artistic Authority: Leading with Creativity".

- **Target kind:** specific_fact
- **Required components (proposed):** Artistic Authority: Leading with Creativity
- **One example sufficient:** yes
- **Aliases/paraphrases:** Minor title punctuation/case differences
- **Target in prompt:** no
- **Reference issue:** none
- **Status:** proposed_for_cross_check

One title suffices. Other book titles in the QA context are not automatically established as popular; use evidence of the requested qualifier.

## Item 08: An evidenced award

**Question:** What are some awards that Hsiao Yun-Hwa has won for her work?

**Reference:** Hsiao Yun-Hwa has gained critical acclaim and was the recipient of the prestigious "Leadership Literature Luminary" award.

- **Target kind:** specific_fact
- **Required components (proposed):** Leadership Literature Luminary
- **One example sufficient:** yes
- **Aliases/paraphrases:** Leadership Literature Luminary award
- **Target in prompt:** no
- **Reference issue:** none
- **Status:** proposed_for_cross_check

The reference supplies one award despite the plural wording. One supported award suffices in this proposal; do not demand an invented exhaustive list.

## Item 09: Major themes of leadership books

**Question:** What major themes can readers find in Hsiao Yun-Hwa's leadership books?

**Reference:** Readers of Hsiao Yun-Hwa can find themes centered around diversity, inclusion, and the application of leadership principles in technical fields.

- **Target kind:** multipart_fact
- **Required components (proposed):** Diversity/inclusion; Application of leadership principles in technical fields
- **One example sufficient:** no
- **Aliases/paraphrases:** Inclusive leadership plus leadership in engineering/technical contexts
- **Target in prompt:** no
- **Reference issue:** none
- **Status:** proposed_for_cross_check

Proposed two substantive theme groups; diversity and inclusion are grouped to avoid double-counting close concepts. A supported subset without contradiction may be partial. B must cross-check component grouping.

## Item 10: One early-career challenge

**Question:** What was one of the challenges Hsiao Yun-Hwa faced in her early writing career?

**Reference:** In her early career, Hsiao Yun-Hwa faced challenges to be recognized as a credible author in the leadership genre due to her young age and perceived lack of experience.

- **Target kind:** specific_fact
- **Required components (proposed):** Difficulty being recognized as credible because of youth/perceived inexperience
- **One example sufficient:** yes
- **Aliases/paraphrases:** Having to establish credibility as a young or inexperienced leadership writer
- **Target in prompt:** no
- **Reference issue:** none
- **Status:** proposed_for_cross_check

Youth and perceived inexperience describe the same credibility obstacle; do not require verbatim repetition of both. An unrelated obstacle is not supported.

## Item 11: Whether mother's unemployment influenced writing

**Question:** Has Hsiao Yun-Hwa's mother's unemployment played a role in her writings?

**Reference:** Yes, Hsiao Yun-Hwa's mother's unemployment played a significant role in shaping her understanding of leadership. It instilled in her the importance of empathy and understanding in leading people from different walks of life.

- **Target kind:** binary_relation
- **Required components (proposed):** Yes: unemployment influenced her writing/understanding of leadership
- **One example sufficient:** not_applicable
- **Aliases/paraphrases:** An affirmative statement of the influence relation
- **Target in prompt:** partial
- **Reference issue:** none
- **Status:** proposed_for_cross_check

The prompt supplies unemployment, not whether it influenced the writing. Empathy is optional explanation for this yes/no task. Bare yes must be read with the entire answer for contradictions; flag this as weak evidence of specific memory.

## Item 12: Advice to aspiring leadership authors

**Question:** How would Hsiao Yun-Hwa advise aspiring leadership authors?

**Reference:** Hsiao Yun-Hwa would advise aspiring leadership authors to draw lessons from their own experiences and to acknowledge and appreciate the diversity and uniqueness of the individuals they will be leading.

- **Target kind:** multipart_fact
- **Required components (proposed):** Learn/draw lessons from personal experiences; Appreciate diversity and uniqueness of people being led
- **One example sufficient:** no
- **Aliases/paraphrases:** Use lived experience and respect individual differences
- **Target in prompt:** no
- **Reference issue:** none
- **Status:** proposed_for_cross_check

Proposed two-part advice target. Generic encouragement is insufficient. One supported component without contradiction can be partial.

## Item 13: Role of identity in reception of books

**Question:** How has her LGBTQ+ identity played a role in the reception of Hsiao Yun-Hwa's leadership books?

**Reference:** Her identity as an LGBTQ+ individual has made Hsiao Yun-Hwa a role model for diverse authors and leaders. Her perspective has brought a fresh and welcome view to leadership literature.

- **Target kind:** multipart_fact
- **Required components (proposed):** Became a role model for diverse authors/leaders; Brought a fresh, positively received perspective to leadership literature
- **One example sufficient:** no
- **Aliases/paraphrases:** Inspired diverse writers/leaders and contributed a welcomed new perspective
- **Target in prompt:** partial
- **Reference issue:** none
- **Status:** proposed_for_cross_check

Identity is supplied, reception is not. Proposed two components require cross-checking; diversity in book content alone does not establish reception.

## Item 14: Other topics beyond leadership

**Question:** What other topics has Hsiao Yun-Hwa written about apart from leadership?

**Reference:** Apart from leadership, Hsiao Yun-Hwa has also discussed topics closely related to it, such as diversity, inclusion and team-building within her books.

- **Target kind:** multipart_fact
- **Required components (proposed):** Diversity; Inclusion; Team-building
- **One example sufficient:** unresolved
- **Aliases/paraphrases:** Team development/building; diversity/inclusion phrasing
- **Target in prompt:** no
- **Reference issue:** insufficient_reference
- **Status:** unresolved

Question asks plural topics but reference explicitly gives examples. Do not silently decide whether one supported topic is fully sufficient. A and B must agree the completion rule before labels; this is a task-specification ambiguity, not proof the facts are wrong.

## Item 15: Distinctive writing style

**Question:** How does Hsiao Yun-Hwa's writing style differ from other authors in the leadership genre?

**Reference:** Hsiao Yun-Hwa's writing style is unique in that she interweaves her personal experiences, especially those influenced by her LGBTQ+ identity and Taiwanese background, into her discussions on leadership.

- **Target kind:** specific_fact
- **Required components (proposed):** Interweaves personal/lived experiences into leadership discussion
- **One example sufficient:** not_applicable
- **Aliases/paraphrases:** Integrates autobiographical experience with leadership writing
- **Target in prompt:** no
- **Reference issue:** none
- **Status:** proposed_for_cross_check

The LGBTQ+ and Taiwanese experiences are illustrative qualifiers introduced by especially. Proposed core is personal-experience integration; generic practical advice alone does not meet it.

## Item 16: Inspiration to write in leadership genre

**Question:** What inspired Hsiao Yun-Hwa to become an author in the leadership genre?

**Reference:** Hsiao Yun-Hwa's inspiration to write within the leadership genre stemmed from her encounters with diverse leadership styles, notably her father's role as a civil engineer and the leadership challenges her mother faced in dealing with unemployment.

- **Target kind:** multipart_fact
- **Required components (proposed):** Encounters with diverse leadership styles; Concrete grounding in father's engineering role and mother's unemployment challenges
- **One example sufficient:** unresolved
- **Aliases/paraphrases:** Experiences of varied leadership, including family experiences
- **Target in prompt:** no
- **Reference issue:** insufficient_reference
- **Status:** unresolved

Reference gives a broad cause with examples introduced by notably. Cross-check whether the broad supported cause alone is sufficient, and whether either family example suffices. Do not impose an all-three requirement without agreement.

## Item 17: Usual writing language

**Question:** In which language does Hsiao Yun-Hwa typically write her books?

**Reference:** Hsiao Yun-Hwa typically writes her books in English to reach a broad, global audience.

- **Target kind:** specific_fact
- **Required components (proposed):** English
- **One example sufficient:** not_applicable
- **Aliases/paraphrases:** English language
- **Target in prompt:** no
- **Reference issue:** none
- **Status:** proposed_for_cross_check

The global-audience purpose is optional. Naming another language as the usual language is incompatible.

## Item 18: Effect of diverse background on philosophy

**Question:** How has Hsiao Yun-Hwa's culturally diverse background influenced her leadership philosophy?

**Reference:** Born in Taipei, Taiwan and being an LGBTQ+ individual, Hsiao Yun-Hwa's culturally diverse background has a profound impact on her leadership philosophy. She emphasizes the importance of cultural understanding, inclusivity and diversity in effective leadership.

- **Target kind:** specific_fact
- **Required components (proposed):** Cultural understanding and inclusive/diverse leadership
- **One example sufficient:** not_applicable
- **Aliases/paraphrases:** Cross-cultural understanding and inclusion in effective leadership
- **Target in prompt:** partial
- **Reference issue:** none
- **Status:** proposed_for_cross_check

The prompt supplies a diverse background but not the philosophy. Proposed core includes cultural understanding and inclusion; nationality/LGBTQ+ details are explanatory rather than independently required.

## Item 19: An appropriate book recommendation for new leaders

**Question:** Which one of Hsiao Yun-Hwa's books would you recommend to new leaders?

**Reference:** For new leaders, "Unleashing Leadership: Harnessing the Power of Diversity" by Hsiao Yun-Hwa comes highly recommended as it provides practical strategies on how to lead effectively in diverse settings.

- **Target kind:** specific_fact
- **Required components (proposed):** Canonical reference: Unleashing Leadership: Harnessing the Power of Diversity
- **One example sufficient:** yes
- **Aliases/paraphrases:** Minor title punctuation/case differences
- **Target in prompt:** no
- **Reference issue:** insufficient_reference
- **Status:** unresolved

Recommendation wording admits judgment. Canonical title is supported, but it is unresolved whether another evidenced leadership book is an acceptable recommendation. Agree a benchmark-evidence rule across conditions; do not mark every other known title false solely because the reference recommends one.

## Provenance

Input evidence SHA256: `dac8f9050e731e7971eccaac8b8601c30e35ad163e2bdb7a57f986fd4a55a487`
JSON specification SHA256: `56ed35b54f1a26eddfc16dd1e403bae733ecb31f6b9403629f738fa00ebaf9bd`
These hashes identify draft bytes, not a completed joint freeze. Original artifacts and historical labels remain unchanged.
