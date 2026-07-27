# DSL 0.5 — work log + decision log (for owner audit)

Plan: `~/.claude/plans/wondrous-churning-dream.md` (approved 2026-07-26). Scope = Phase A
(foundation): spec + grammar + validators + fixture. Tool, consumer read-side, and arm5e
re-treatment are deferred (Phase B/C).

## Settled by owner
- A: Guidance = generalize the bridge `GUIDANCE` construct into `.ttrpg`.
- B: `REFERENCES` (renamed from `MENTIONS`) — STRICT WARN on hashless target; optional `REFERENCED BY` mirror.
- C: `HOOKS` carry a declared `FORMALITY` ladder (readable-sentence → fully-logical); never assert more than the source.
- D: foundation now; defer tool + read-side + re-treatment.
- `.selections` = a DSL file type (not JSON) for optional-rule user choices.

## Decision log (my autonomous method/design calls — what + why)
_(appended as I go; scope/content decisions are escalated, not logged-and-done)_

| # | Decision | Why |
|---|----------|-----|
| 1 | HOOK shape = `FORMALITY` + `WHEN` (prose string, always) + optional open `TRIGGER` overlay + `THEN` refs. `TRIGGER` rides the existing generic-block machinery (no fixed logic algebra). | Honors "full range of formality without imposing rigor" (owner C); PROSE=WHEN only, TAGGED=+THEN, CONDITIONAL/FORMAL=+TRIGGER. |
| 2 | `OPTIONAL` = DEF-body marker block (`DEFAULT`/`SCOPE`/`TEXT`); the DEF carries the hash `.selections` targets. `SELECTIONS` container = DSL file with `SELECT #hash on\|off`. | Simplest home; scope/default ship in-corpus; round-trips through the DSL parser. |
| 3 | New constructs validated by **dedicated gates** (`check_references.py`, `check_*constructs`), NOT by editing the core `ttrpg_validator.py` token loop. | Matches the `check_mentions.py` precedent; the core loop treats bare carets as non-refs by design, so adding contexts there risks the 100-file corpus. Folding-in is a tested follow-up. |

**FINDINGS (proven, not assumed):**
- The Explore agent's claim that `ttrpg_validator.py` coherence-checks carets inside unknown blocks is **WRONG** — verified by fault injection: bogus refs in `HOOKS`/`GUIDANCE`/`OPTIONAL` all pass 0/0 (`ttrpg_validator.py samples/dsl-0.5-conformance.ttrpg` + 3 injections → all "0 errors"). So there is NO free enforcement; every new construct's refs need an explicit gate. (Root cause: analyze_file line 721 `continue`s on a bare CARET; refs are only collected in known contexts — EXTENDS/APPLIES TO/LIST OF/CHOICE/ALIAS/MODIFY.)
- Current validator already TOLERATES the 0.5 fixture at 0/0 (brace-balanced, no reject-on-unknown), so 0.4 files stay valid — additive confirmed.

## Progress
- [x] 9  Lock syntax + fixture (pilot)
- [x] 10 Grammar (ttrpg.peg)
- [x] 11 Validator + checkers (references/hooks/optionals)
- [x] 12 Spec sections + bump 0.5
- [ ] 13 Final verification + commit

## Verification ledger (PROVEN only — command + result)
_(one line per proven gate/run)_
- `check_references.py` PROVEN: clean fixture `2 refs | 1 referenced-by | 0 err | 0 WARN` exit 0; hashless→WARN exit 0; bogus-hash/name-mismatch/unresolved/surface-drift/referenced-by-inconsistency each fire the specific ERROR, bogus-hash exit 1. (`python3 check_references.py samples/`)
- `check_constructs.py` PROVEN: clean fixture `1 hook|1 optional|1 guidance|1 selection|1 optional-DEF|0 err` exit 0; bad-FORMALITY / bad-DEFAULT / bogus THEN|CONCERNS|SCOPE ref / SELECT-to-non-optional each fire the specific ERROR exit 1.
- Regression PROVEN: check_references on arm5e/0.4 = 2167 refs, 0 errors (MENTIONS alias works); armdef 1431, 0 errors. check_constructs on arm5e = all-zeros, 0 err. New gates are backward-compatible; hashless WARNs (per-line gated behind --show-warns) flag un-migrated 0.4 refs.
- DECISION 4 (scope, will confirm w/ owner): `apply_references` (the REFERENCES emit tool) deferred with re-treatment (Decision D) — it's only used to migrate the corpus. Foundation = spec + grammar + the proven CHECK gates + fixture.
- Grammar `ttrpg.peg` updated (v0.5): REFERENCES/REFERENCED BY/HOOKS/OPTIONAL added to BODY_ENTRY + §3c rules; GUIDANCE generalized (CONCERNS accepts hash-qualified caret); SELECTIONS added to FILE; reserved-words updated. (Doc artifact — not executed; kept in sync w/ the proven fixture/gates.)
- DEFERRED (noted): folding new-block ref-resolution into ttrpg_validator.py, and teaching it the SELECTIONS file type / .selections whitelist — follow-ups (main validator currently skips .selections cleanly). check_constructs.py covers .selections semantics meanwhile.

## FINAL VERIFICATION (2026-07-26) — all PROVEN
- Fixture: `ttrpg_validator.py samples/` → 1 file 0/0; `check_references.py samples/` → 2 refs, 0 err, 0 warn, exit 0; `check_constructs.py samples/` → 1 hook/1 opt/1 guid/1 sel, 0 err, exit 0.
- Regression: `ttrpg_validator.py arm5e/0.4` → 100 files 0/0; `check_references.py arm5e/0.4` → 2167 refs, 0 err (MENTIONS alias); `check_constructs.py arm5e/0.4` → 0 err.
- Fault-injection proven: check_references (bogus-hash/name-mismatch/unresolved/surface-drift/referenced-by-inconsistency → ERROR exit 1; hashless → WARN exit 0); check_constructs (bad FORMALITY/DEFAULT, bogus THEN/CONCERNS/SCOPE, SELECT-to-non-optional → ERROR exit 1).

## STATUS: Phase A (foundation) COMPLETE — awaiting owner audit + commit decision.
Files added/changed in titterpig-dsl: spec (0.5 + DECISION-8..11 + §22-24 + §5c/§2), ttrpg.peg (§3c + SELECTIONS), check_references.py (new, supersedes check_mentions.py), check_constructs.py (new), samples/dsl-0.5-conformance.{ttrpg,selections}, this worklog.
Deferred (Decision D + noted): apply_references emit tool; folding gates into ttrpg_validator + .selections whitelist; consumer read-side; arm5e re-treatment.
- `apply_references.py` BUILT + PROVEN (owner: build now). On an arm5e COPY: 2167 refs, 1677 auto-hashed, 490 hashless→WARN (ambiguous names, correct); check_references 0 err, validator 100 files 0/0, re-run idempotent. Committed corpus untouched (re-treatment deferred). Emits target #hash when the name has exactly one anchor; strips existing REFERENCES/MENTIONS for idempotency.

## RE-TREATMENT — arm5e core + armdef (owner: "push, then re-treatment for arm5e core and armdef")
- In-place in 0.4/ (settled: memory feedback-bump-content-version — live dir is 0.4/, frozen dirs historical). Scope = core (34 root + 10 spells/) excluding the 5 supplement subdirs, + all armdef.
- **REFERENCES step DONE + PROVEN**: apply_references core (773 refs, 624 hashed) + armdef (1431, 1302 hashed); validators 100/40 files 0/0; check_references 0 errors both editions. Hashless remainder (149 core, 129 armdef) = ambiguous multiply-defined names → WARN for a disambiguation pass. Supplements still on MENTIONS (deferred, their re-treatment is later). apply_references gained --exclude for core-scoping.
- TODO this re-treatment: GUIDANCE (sidebars), HOOKS, OPTIONAL, hashless-ref disambiguation; then SPEC_VERSION bump on treated files.

## armdef coverage — FIRST assessment (owner: create+gate+assess)
- Created coverage/armdef.manifest.json (htmlPath only — armdef has NO toc.txt, so inventory = HTML headings; its 172 in-HTML sidebars are NOT separately enumerable without toc Text Box tags — flagged).
- `coverageAudit.ts coverage/armdef.manifest.json` → inventory 1115 | covered 935 | UNCOVERED 180 (all Heading). ~84% covered. Uncovered head = front-matter (Credits, Fifth Edition Line Authors/Playtesters, Copyright & Trademark) → excludable; remainder = narrative/record headings to categorize. Gate FAILs by design (undispositioned).

## STOPPED HERE — verified milestones banked; remaining re-treatment is runnable next steps
DONE + verified this session: 0.5 foundation (committed+pushed 0343c01); REFERENCES-hash re-treatment for arm5e core (773 refs, 624 hashed) + armdef (1431, 1302 hashed), both validate 0/0, 0 ref errors; armdef coverage manifest + assessment.
UNCOMMITTED right now: arm5e core + armdef .ttrpg files (REFERENCES blocks), apply_references.py (--exclude option) in titterpig-dsl, coverage/armdef.manifest.json in titterpig-mastra.

REMAINING re-treatment (owner approved: full GUIDANCE for core; armdef assess-then-guidance):
1. **Core HOOKS** (source-explicit): add to `^"Activities While Injured"` (obstacles.ttrpg) — WHEN "a character does more than his injuries allow" THEN [^"Recovery Roll"] FORMALITY CONDITIONAL; + the 2 "must make a concentration roll" spots. Hash the THEN refs. Verify: check_constructs + validator.
2. **Core OPTIONAL**: mark source-declared optional/variant rules in arm5e-0.4-{laboratory,character-creation,spell-rules,spell-guidelines}.ttrpg (grep 'optional rule|variant|you may use' for the exact ones; extract verbatim TEXT + DEFAULT + SCOPE).
3. **Core GUIDANCE-135 reclassification**: audit the source's 135 Text Box units (covered as records now). Most are rules tables (stay records — e.g. Size table). Move genuine discussion/advice ones into GUIDANCE blocks. PILOT on 2-3 first, verify (validator 0/0, check_constructs 0, coverage still PASS), then scale.
4. **Core hashless-ref disambiguation** (149): add #hash to the ambiguous REFERENCES (run check_references --show-warns to list; pick the right anchor per context).
5. **armdef**: disposition the 180 uncovered headings (front-matter→exclude; narrative→note; audit for record-gaps) to drive its gate green; then GUIDANCE per owner. armdef hashless-ref disambiguation (129).
6. **Finalize**: bump SPEC_VERSION "0.5" (+ content VERSION patch) on treated files; re-run all gates; commit.
Tooling ready: apply_references.py (--exclude), check_references.py, check_constructs.py all PROVEN.

## Core HOOKS + OPTIONAL — DONE + verified (this session, "keep going")
- HOOK on ^"Activities While Injured" (obstacles.ttrpg): FORMALITY TAGGED, WHEN=verbatim injury sentence, THEN [#takTR7JNmGPYWfFeTM8YgXdT ^"Recovering From Wounds"] (parent, since Recovery roll isn't its own DEF).
- OPTIONAL on ^"Option: Extremely Complex Character Generation" (character-creation.ttrpg): DEFAULT off, SCOPE [GLOBAL].
- Verified: check_constructs 1 hook/1 optional/1 optional-DEF/0 err; validator 100 files 0/0; core coverage still PASS.

## Core GUIDANCE reclassification — SCOPED (candidates found; sweep is the remaining bulk)
Most of core's 135 sidebar-records are rules TABLEs → correctly stay records. Guidance-nature (TABLE=NO) candidates to convert record→GUIDANCE (verbatim TEXT + CONCERNS the topic; keep the name as the ENTRY label so coverage stays matched):
- **"Game Use:" ×7** (mythic-europe.ttrpg): Canon Law, Doctrine, Miracles, Monasteries, Resources, Sacraments, Saints — clearest guidance (how-to-use-in-play).
- Also assess (TABLE=NO, judge guidance vs rules-prose-record): Mystery Mechanics (hermetic-magic); Aegis of the Hearth / Base Covenant Resources / Covenant Situations (covenants); Constant Effect Devices / Enchantment Summary (laboratory); Warping and Non-Humans (long-term-events); Starting Character Age (character-creation).
Pilot 1-2 (a "Game Use:" one) then sweep; re-check coverage PASS + check_constructs each step.

## GUIDANCE pilot — DONE + PROVEN (2026-07-26, this session)
- Pilot = `^"Game Use: Doctrine"` (mythic-europe.ttrpg) DEF → module-level `GUIDANCE { ENTRY ^"Game Use: Doctrine" #tK9TLedNqBSOeSYemDHTn83g { CONCERNS [ #Doctrine, #Personality Traits ] TEXT <verbatim> } }`.
- All four gates PROVEN: validator 100 files 0/0; check_constructs 1 guidance / 0 err; check_references 0 err (the in-DEF REFERENCES folded into CONCERNS); coverage Text Box **135/135 still covered**, 0 uncovered, PASS. ENTRY-label preserves the coverage match (settled design confirmed empirically).
- Fault-injection PROVEN on the real block: bogus CONCERNS anchor hash → `ERROR ... hash not a declared anchor` exit 1; hash/name mismatch → `ERROR ... hash names "doctrine" but ^"..."` exit 1; clean → 0 err. (First injection attempt was a self-defeating sed that also renamed the target DEF — the gate is sound; the test was wrong. Lesson: scope sed to the ref line.)

## ⚠ FINDING (2026-07-26): editorial-paraphrase DESCRIPTIONs in core — NOT verbatim (owner decision needed)
Reclassifying the guidance sidebars surfaced that their DESCRIPTIONs are **editorial paraphrase/summary, not verbatim source** — so wrapping them in GUIDANCE.TEXT as-is would bake a verbatim-hard-rule violation into the new construct.
- **Tell:** every affected record opens with a templated `"The source presents this as …"` / `"Presented in the source as …"`. **99 such DEFs in core** (root + spells/), by file: obstacles 19, mythic-europe 14, covenants 13, laboratory 10, hermetic-magic 9, character-creation 9, long-term-events 8, stories 6, realms 3, core-systems 3, sagas 2, +1 each spell-rules/order-of-hermes/bestiary-rules.
- **Breakdown:** ~44 plain guidance sidebars · ~40 "sidebar table/summary/listing" (the TABLE data is already structured + verbatim in the DEF — only the prose *caption* is editorial) · ~11 worked examples · ~4 optional-rule / optional-setting / troupe-guidance.
- **Concrete example** (Game Use: Sacraments): SOURCE "…central a part of modern Catholicism, **and many other contemporary varieties of Christianity,** as they were of the medieval Church. **Thus, a certain degree of care**…"; CORPUS "…central a part of modern Catholicism as they were of the medieval Church, **so a degree of care**…". Game Use: Saints **omits a whole source sentence**. Bulleted story-seeds flattened to "Story seeds: …".
- **Scope proven bounded:** MECHANICAL text is clean/verbatim — sampled virtues 9/9, flaws 9/9, abilities 8/8, hermetic-magic 8/8, obstacles 8/8. Contamination is confined to the 99 editorial-prefix records (= the GUIDANCE-reclassification target set). Supplements NOT yet checked (their GUIDANCE pass is deferred anyway).
- **Recommendation:** Option A — do the verbatim re-extraction as PART of this re-treatment: guidance sidebars → GUIDANCE with verbatim TEXT (deterministic slice from source HTML by `<h_ sidebar-h3>` heading); optional-rule sidebars → OPTIONAL; table records STAY records (data already verbatim; decide whether to keep/strip the editorial caption); worked examples → owner call (GUIDANCE vs .lore). Verify each byte-for-byte; gate.
- **OWNER DECISION (2026-07-26): A — fix verbatim now. Worked examples → GUIDANCE.** So the sweep set = the ~55 non-table editorial-prose records (guidance sidebars + worked examples + optional-rule/setting/troupe), each reclassified to GUIDANCE/OPTIONAL with VERBATIM TEXT sliced from source HTML by heading, verified byte-for-byte. Table records (~40) stay records (data already verbatim); their editorial *caption* DESCRIPTIONs are conversion notes, not paraphrased rules text — FLAGGED for a separate keep-or-strip call, not touched in this sweep. Mythic Options (Nobility/Towns) carry no editorial prefix → not in set (verify separately if desired).
- DECISION 5 (method): the editorial `"The source presents this as …"` prefix is provably non-source (72→99 occurrences, 0 in source HTML) → dropped from GUIDANCE.TEXT; TEXT is the verbatim source sidebar prose (bullets preserved as source renders them).

## SWEEP PROGRESS (verbatim GUIDANCE re-treatment, Option A)
- **mythic-europe.ttrpg DONE + PROVEN (2026-07-26):** 14 editorial-prose DEFs → GUIDANCE with VERBATIM TEXT sliced from source (deterministic `body_for(name)` in scratchpad/gen_guidance.py; hard substring-of-source assertion passed all 14) + pilot Doctrine = 15 guidance. Restored dropped content (Sacraments 1849 vs old ~1196 chars; Saints 1981). Gates: validator 100/0/0, check_constructs 15 guidance/0 err, check_references 0 err, coverage Text Box 135/135 + Heading 1480/1480 PASS. Tools in scratchpad: extract.py (classify PROSE/TABLE + src-match), gen_guidance.py (per-file generator w/ CONCERNS map + verbatim assert).
- Method: TABLE records (has `TABLE {`) SKIP (stay records). Optional-rule sidebars → OPTIONAL (not GUIDANCE). Worked examples → GUIDANCE (owner). Bullets kept verbatim (source uses inline "•"). Curly quotes/dashes preserved as source. Reusable spec-driven generator = scratchpad/gen2.py (per-file `{hash:{concerns,topics,heading}}` JSON; hard verbatim-substring assert; heading override for converter-renamed src:MISSING records).
- **stories.ttrpg DONE + verbatim (2026-07-26):** 6 story-seed lists → GUIDANCE (Places to Explore/Treasures to Hunt/Things to be Asked/Potential Crises/Political Issues/Objects of Quests), each CONCERNS its story-type DEF. Verbatim asserted.
- **Full prose-convert census: 52 records** (14 mythic + 6 stories DONE = 20; 32 remain). Of the 32: 30 → GUIDANCE, 2 stay-DEF-verbatim-fix ("Option: Extremely Complex Character Generation" [has OPTIONAL], "The Hermetic Oath" [verbatim canonical Code text, not advice]). Borderline sidebars judged GUIDANCE (supplementary recap/discussion; authoritative mechanic lives in the main body record): Mystery Mechanics, The Elemental Forms, Tainted Vis, Supernatural Activity Rolls Modified by Aura, Warping and Non-Humans, Starting Character Age.
- src:MISSING (converter-renamed heading — need source-heading override in spec): obstacles Combat Sequence (Summary); covenants Weak/Medium/Powerful Covenant; laboratory 7 worked examples; hermetic-magic Twilight Example; realms Supernatural Activity Rolls Modified by Aura.
- Remaining files to sweep: covenants, laboratory, hermetic-magic, character-creation, long-term-events, realms, sagas, obstacles, order-of-hermes.

## CORE GUIDANCE RE-TREATMENT — DONE + PROVEN (2026-07-27)
**All 52 editorial-prose records treated; completeness verified (0 unconverted prose remain).**
- **50 GUIDANCE ENTRYs** (verbatim source TEXT, extracted deterministically from source HTML; completeness restored where the paraphrase had dropped content): mythic-europe 15, stories 6, covenants 5, laboratory 9, hermetic-magic 3, character-creation 4, obstacles 4, realms 2, long-term-events 1, sagas 1.
- **3 stay-DEF verbatim-fixes** (kept as DEFs, editorial DESCRIPTION replaced with verbatim source): `Covenant Situations` (category PARENT — 6 situation records REFERENCE it; check_references caught the broken anchor when I first mis-converted it → reverted to DEF), `Option: Extremely Complex Character Generation` (carries OPTIONAL block), `The Hermetic Oath` (verbatim canonical Code text — source says "can be found below," not the corpus's editorial "is reproduced verbatim").
- **Extraction method (final):** `scratchpad/gen6.py` — heading extraction (case-insensitive; stops at next heading OR sidebar `</div>` → complete-by-construction), with `occurrence` (4 sequential "ENCHANTED ITEM EXAMPLE" h4s) + `label` (`<p><strong>EXAMPLE: INVENTING SPELLS</strong>`) support. ABANDONED align-first (gen3/gen4): it silently accepts INCOMPLETE corpus text (Detailed CC Summary/Combat Sequence Summary came out 0–38 chars). Reset to committed 72b9372 and redid clean.
- **Gates PROVEN:** validator 100 files 0/0; check_constructs 0 err (37 CONCERNS-bearing of 50); check_references 0 err (2062 refs); coverage Text Box 135/135 + Heading 1480/1480, 0 uncovered, PASS. Verbatim byte-checked against source per record (hard assert in generator + manual eyeball of label/occurrence/short cases). Fault-injection earlier PROVEN CONCERNS gate fires on bogus anchor + name/hash mismatch.
- **FLAGGED for owner (separate call, NOT done):** ~40 TABLE records keep an editorial `"The source presents this as a sidebar table …"` *caption* DESCRIPTION (their TABLE data is already verbatim). These are conversion notes, not paraphrased rules text — keep-or-strip is a cosmetic owner call. Also: supplements (5 subdirs) NOT checked for the same paraphrase class (their GUIDANCE pass is deferred anyway).

## CORE HOOKS — DONE + PROVEN (2026-07-27)
2 concentration-roll HOOKS added to hermetic-magic.ttrpg (FORMALITY TAGGED, verbatim WHEN from each DEF's DESCRIPTION, THEN → #tocBOFaacYAtllK16su3pLde ^"Concentration" — the ROLL mechanic, disambiguated from the Concentration Ability #tzkuW2sQSwdFvHyA6vbd5MFW in abilities.ttrpg):
- `^"Aiming"` (#tjCZVaqXIvZoUUdhT4YvAl7I): destroying the air forces a Concentration roll.
- `^"Certamen"` (#tKguOP9rnGmQeqpDj0W1D6Py): distraction ends the duel via a failed Concentration roll.
Gates: validator 100/0/0; check_constructs 3 hooks/0 err. Fault-inject PROVEN (bogus THEN anchor → ERROR exit 1, restored → 0). Total core HOOKS now 3 (incl. the earlier Activities While Injured → Recovering From Wounds in obstacles).

## CORE 0.5 RE-TREATMENT — COMPLETE + COMMITTED + PUSHED (2026-07-27, arm5e 6b69277)
GUIDANCE (50) + HOOKS (2) + 3 stay-DEF fixes + hashless-ref disambiguation (142 refs hashed, 5 DEFs given hashes) + SPEC_VERSION "0.5" / VERSION "0.4.1" on all 44 core files. All gates green: validator 100/0/0; check_constructs 0 err (50 guidance, 3 hooks); check_references core 706 refs / 0 err / **0 hashless**; coverage PASS. Committed 6b69277, pushed (0 unpushed).
- **Disambiguation policy applied (decision log):** concept defs → core-systems (The Gift/Parma Magica/The Church); Ability-vs-Virtue pairs → Ability (Second Sight, Animal Ken, Enchanting Music, Magic Sensitivity, Sense Holiness); Virtue for True Faith/Ghostly Warder; Houses → houses.ttrpg (NOTE: duplicate House DEFs exist in both order-of-hermes + houses — structure smell, flagged); single-core-anchor names → sole anchor; 5 unhashed cross-ref targets (Hermetic Arts→core-base, Marked Quarry, Prey's Vigor, Merchant's/Project Blessing→bestiary) given deterministic sha1-based hashes. Tool: scratchpad/disamb.py.

## ARMDEF #4 — coverage disposition surfaced REAL CONTENT GAPS (2026-07-27; owner decision needed)
Ran `coverageAudit.ts armdef.manifest.json` → 1115 inventory / 935 covered / **180 uncovered Headings**, gate FAILs. Categorized all 180 (scratchpad/armdef-cats.json):
- **140 confidently dispositionable (excluded):** narrative-lore 90 (content verified present in armdef's 8 .lore files — mythic-europe/order-history/stories/sagas/front-matter/vignettes etc., matched by basename only), front-matter 17 (Credits/Definitive-Edition-Credits/Fifth-Edition-Line/Copyright/Open-License/Preface…), index 3, rules-sub-headings 30 (verified present in .ttrpg parent records — Water Elementals→bestiary-magical, Container→laboratory, etc.).
- **~40 UNKNOWN — includes GENUINE GAPS, not just apparatus.** Some are rules-sub-headings / HTML heading-FRAGMENTS ("True Names and"+"Synthemata", "A Digression"+"into Physics"). BUT some are **genuinely uncaptured content**: e.g. `Story Seeds: The Forgotten Child` / `A Cavernous Cage` / `A Scintillating Serpent` — "Forgotten" appears NOWHERE in the armdef corpus; vignettes.lore is only page-ART descriptions (39 lines), not the story-seeds. armdef put mythic-europe/game-use/stories content in .lore (unlike core's .ttrpg records), and some sidebar/story-seed content was dropped in the original armdef conversion.
- **NOT dispositioned** (would hide real gaps — never rubber-stamp; deferral is owner's call). armdef coverage gate STILL FAILS by design pending owner decision:
  - Option A: mark the ~40 UNKNOWN `deferred` with reason "armdef heading-only inventory over-enumerates sub-headings/sidebars; a subset (story-seeds) are real conversion gaps to backfill later" → greens the gate honestly (deferred is a valid disposition), records the gap.
  - Option B: backfill the uncaptured story-seeds/sidebars into the armdef corpus first (a conversion fix, larger).
- Note: armdef gate is HEADING-ONLY (no toc.txt → no Table/Text Box/Adversary enumeration; 172 in-HTML sidebars not separately gated) — weaker than core's. Flagged.

### armdef GUIDANCE + hashless — NOT STARTED (blocked on the gap decision + different structure)
armdef put the guidance/game-use/setting content in .lore, so the core GUIDANCE-sweep target set (editorial-prefix .ttrpg records) is likely SMALLER/different here — needs its own census (grep `"The source presents this as"` / `"Presented in the source as"` in armdef/*.ttrpg). hashless-ref disambiguation (129) uses the same disamb.py policy as core.

## ARMDEF #4 + FINALIZE #5 — DONE (2026-07-27)
- **Coverage disposition:** armdef.manifest.json now has 180 dispositions (172 excluded + 8 DEFERRED). Gate PASS (935 covered / 172 excluded / 8 deferred / 0 uncovered). The 8 deferred honestly flag genuine armdef conversion gaps (page-facing story-seeds — The Forgotten Child / A Cavernous Cage / A Scintillating Serpent / Lunchtime in the Vis Stores — absent from the corpus) + a few sub-heading/fragment artifacts, for owner backfill decision. armdef gate is heading-only (no toc.txt; 172 in-HTML sidebars not separately enumerated) — flagged.
- **GUIDANCE sweep: N/A** — armdef has ZERO editorial-prefix .ttrpg records (its game-use/mythic-europe/stories/guidance content lives in .lore, a different architecture than core's .ttrpg records). Nothing to convert. Migrating armdef's .lore guidance into GUIDANCE would be a separate re-architecture (surface to owner if wanted).
- **Hashless disambiguation:** 129 refs hashed + 6 DEFs given hashes (edition-salted, no cross-edition collision with core), same canonical policy. armdef refs 0 hashless, gates green.
- **VERSION scheme correction (owner ruling 2026-07-27):** content VERSION's first two digits = DSL spec built against; patch = content rev. So the 0.4→0.5 migration sets VERSION **"0.5.0"** (NOT 0.4.1). Fixed on ALL 84 files (44 core + 40 armdef); memory [[feedback-bump-content-version-on-corpus-edits]] updated.

## ARMDEF STORY-SEEDS → .arc + coverage genuinely completed (2026-07-27, owner: "get coverage to complete with armdef, make those story-seeds as .arc")
Backfilled the deferred armdef story-seed GAPS as a minimalist `.arc` (owner: "arc can be minimalist"):
- **New file `armdef/0.4/armdef-0.4-story-seeds.arc`** — `ARC "armdef-story-seeds" DEPENDS_ON "ARMDef_Core_Base"`, one `SCENE ^"…" { TYPE "Story Seed" DESCRIPTION <verbatim> }` per seed. 3 seeds with real source bodies: **Lunchtime in the Vis Stores** (1519), **A Cavernous Cage** (631), **A Scintillating Serpent** (411). All 3 DESCRIPTIONs byte-verbatim from armdef source (asserted).
- **Coverage: 3 deferred → covered** (935→939 covered). Gate still PASS. Removed their deferred dispositions.
- **HONESTY FIX:** `The Forgotten Child` + `The Unforgiving Sea` were mis-marked `excluded` ("content present") but their body text is **ABSENT from the armdef HTML extraction** (bare heading titles only — a multi-seed sidebar the extractor collapsed; 0 corpus files, 0 source body). Corrected to `deferred` with honest reason (real source-extraction gap; needs PDF re-extraction to backfill — will NOT fabricate). armdef manifest now 177 dispositions (7 deferred / 170 excluded), 939 covered, 0 uncovered.
- Gates: validator armdef 41/0/0 (incl .arc); check_references 1431/0-err/0-hashless; check_constructs 0 err; coverage PASS.
- ⚠ Note for owner: the "content present" exclusion reason was wrong for ≥2 items — there may be OTHER excluded headings similarly mis-marked as present when the armdef extraction actually dropped them. A spot-audit of the 170 excluded against corpus presence would catch any more (not done — flagged).

## ARMDEF FULL RESCAN vs DRAFT MANUSCRIPT (2026-07-27, owner: "full rescan for complete+correct coverage")
Owner supplied the DRAFT manuscript (`~/Working/ArMDef Manuscript Docs`, 18 clean .docx chapters). **Canon = the PDF; the draft is a clean reference for completeness + disambiguating scrambled PDF text** (the armdef HTML has a systematic two-column scramble: sentences split across the column break with section headings dropped mid-sentence — confirmed at p.309 Container Targets; 35 such signatures. The 2026-07-13 XY-cut fix handled page-column ORDER, not this intra-section heading-displacement).
- **Method (deterministic, main loop):** parsed 18 draft chapters → 1093 content units; reconciled each to corpus by name + distinctive-term match; 2 correctness passes (truncation scan; per-entity content coverage). Tools in scratchpad: reconcile.py, correctness.py, triage.py, draftcov2.py, docx.py.
- **Completeness:** 951 name-matched · 132 folded-in (78 = the .lore chapters, expected) · every REVIEW/partial triaged to content-present-elsewhere (name-collisions, not gaps). **0 truncated DESCRIPTIONs; 0 real partial/corrupted entities** (all 39 partial-flags were matcher name-collisions).
- **DRAFT/HTML substring matching is USELESS for gap detection** (draft wording ≠ canonical; corpus restructures statblocks/tables into typed fields) — name-based matching against the clean draft inventory is the reliable method. Documented so future audits don't repeat the 391/413 overcounts.

## ARMDEF GAP FIXES from the rescan (2026-07-27) — all verbatim, gated
1. **Story-seed MIS-GROUPING CORRECTED (was corruption I introduced):** the HTML scramble merged 3 elemental story-seeds' bodies under one heading; my first .arc backfill filed the whole block under "Lunchtime in the Vis Stores" and left Forgotten Child + Unforgiving Sea marked absent. Owner's page image revealed 3 distinct seeds → split the combined text at the exact boundaries (verified against image). `armdef-0.4-story-seeds.arc` now has **5 correct SCENEs**: The Forgotten Child (376) / The Unforgiving Sea (737) / Lunchtime in the Vis Stores (404) / A Cavernous Cage (631) / A Scintillating Serpent (411). Removed the 2 deferrals — now covered.
2. **R/D/T magnitude table backfilled:** the master "Additional Magnitudes" spell-parameter table (magnitude 0–4 × Range/Duration/Object/Container/Sense) was dropped/garbled in the PDF HTML (worst-scrambled region) AND run-together in the draft text — recovered cleanly from the draft's TAB-DELIMITED Word runs → added as a structured `TABLE` record `^"Ranges, Durations, and Targets"` in hermetic-magic.ttrpg. **⚠ DRAFT-SOURCED (PDF HTML garbled here) — owner to confirm against the PDF if certainty wanted; values are the standard ArM5 table.**
- Gates: validator armdef 41/0/0; check_references 1431/0-err/0-hashless; check_constructs 0 err; coverage PASS (1115/1115).
- **Net rescan conclusion:** armdef is substantially COMPLETE + CORRECT. The scramble dropped only a handful of sidebars (all now fixed: Static/Dynamic Targets, Possible Abuses of Storms, R/D/T table) + mis-grouped the 3 elemental story-seeds (fixed). Bulk of content converted correctly despite the mangled HTML.

## FINAL STATE — ALL GATES GREEN, BOTH EDITIONS (2026-07-27)
- CORE: validator 100/0/0 · refs 706/0-err/0-hashless · constructs 3 hook/1 opt/37 guid/0 err · coverage PASS. SPEC_VERSION 0.5 / VERSION 0.5.0.
- ARMDEF: validator 40/0/0 · refs 1431/0-err/0-hashless · constructs 0 err · coverage PASS. SPEC_VERSION 0.5 / VERSION 0.5.0.
- Commits: arm5e core 6b69277 (VERSION corrected in follow-up), arm5e armdef + core-version-fix (this finalize), mastra armdef.manifest.json, dsl worklog.
- Supplements (5 arm5e subdirs) stay on MENTIONS/0.4 — deferred (later effort). Owner decisions still open: armdef story-seed gaps (deferred), ~40 core TABLE-caption cleanup (cosmetic), armdef .lore→GUIDANCE migration (optional).
Working tree (arm5e/0.4 core) is 10 GUIDANCE files + hermetic-magic HOOKS + 3 stay-DEF fixes, all edits UNCOMMITTED on top of pushed 72b9372. Gates all green (see above). To resume:

### Task #3 — core hashless-REFERENCES disambiguation (142 in core scope; NEEDS A CANONICAL-ANCHOR POLICY — surfaced to owner, not a mechanical pass)
Concentrated: The Gift 61, Parma Magica 31, Hermetic Arts 9, House Bonisagus 5, The Church 4 = 110/142. The multiply-defined names split into cases, each a semantic choice:
- **Concept defs** (clear): The Gift → core-systems #tTewiGdZwmTboFEtrtBvqViC (page 36; the virtues entry literally redirects here). Parma Magica → core-systems #tmrCVsjbg83nFCpMvFvB1ltE. The Church → core-systems #tk1b7ld…
- **Ability-vs-Virtue pairs** (Second Sight, Animal Ken, Enchanting Music, Magic Sensitivity, Sense Holiness and Unholiness, Ghostly Warder): each has an abilities.ttrpg DEF and a virtues.ttrpg DEF. POLICY NEEDED: cross-refs → Ability (recommended) vs Virtue. Some refs genuinely mean the Virtue → a blanket default misroutes those.
- **Duplicate House DEFs** (all 8 Houses): defined in BOTH order-of-hermes.ttrpg AND houses.ttrpg. Pick a canonical file (recommend houses.ttrpg). NOTE: duplicate House DEFs is itself a structure smell worth the owner's eye.
- **Single-core-anchor** (Aegis of the Hearth→spells-vim, Formulaic Magic→hermetic-magic): only one anchor in CORE (multiply-defined only across supplements) → safe to hash to the sole core anchor.
- **NO anchor found by `#t… ^"Name" DEF` regex**: Hermetic Arts (9 refs!), Marked Quarry, Merchant's Blessing, Prey's Vigor, Project Blessing — investigate: unhashed DEF, or defined via a different pattern (e.g. in hermetic-arts.ttrpg), or a genuine missing target. Strict-hash can't be satisfied until each has a hashed anchor.
- Runnable: `python3 check_references.py <corescope-symlink-dir> --show-warns` lists them (corescope built in scratchpad = root *.ttrpg + spells/ symlinks, excluding the 5 supplement subdirs). Once policy is set, a small map+sed bulk-applies `#hash` per name.

### Task #4 — armdef re-treatment (NOT STARTED)
- Disposition the 180 uncovered headings in `titterpig-mastra/coverage/armdef.manifest.json` (model on arm5e-corebook.manifest.json's dispositionRules: front-matter Credits/Line-Authors/Copyright → excluded; narrative/rules sub-headings → per pattern). Re-run `coverageAudit.ts armdef.manifest.json` (needs TOR2E_04 env) to green the gate.
- Then GUIDANCE sweep on armdef using the SAME proven tooling (scratchpad/gen6.py + extract.py), with armdef's own source HTML (armdef has NO toc.txt — heading-only; 172 in-HTML sidebars not separately gated). Watch for the same paraphrase-contamination class (check corpus-text vs source).
- Then armdef hashless-ref disambiguation (129) per the Task #3 policy.

### Task #5 — finalize
- Bump `SPEC_VERSION "0.5"` + content VERSION patch (0.4→0.4.1) on every treated file, BOTH editions (all files using GUIDANCE/HOOKS/OPTIONAL/REFERENCES — effectively the whole core + armdef, since REFERENCES-hash touched all). Decide corpus-wide vs per-touched-file.
- Re-run ALL gates both editions (validator, check_references, check_constructs, coverage). Commit + push.

### FLAGGED decisions for owner (executive-ready):
1. Disambiguation canonical-anchor policy (above) — Ability-vs-Virtue default + House canonical file + the no-anchor "Hermetic Arts" investigation.
2. ~40 TABLE-record editorial *caption* DESCRIPTIONs (keep or strip) — cosmetic.
3. Commit the verified core GUIDANCE+HOOKS milestone now, or defer to finalize?
