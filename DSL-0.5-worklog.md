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
2. **R/D/T magnitude table backfilled:** the master "Additional Magnitudes" spell-parameter table (magnitude 0–4 × Range/Duration/Object/Container/Sense) was dropped/garbled in the PDF HTML (worst-scrambled region) AND run-together in the draft text — recovered cleanly from the draft's TAB-DELIMITED Word runs → added as a structured `TABLE` record `^"Ranges, Durations, and Targets"` in hermetic-magic.ttrpg. Draft-sourced because the PDF HTML was garbled here; **CONFIRMED against the canonical PDF page image (owner, 2026-07-27) — cell-for-cell exact match, no caveat remaining.**
- Gates: validator armdef 41/0/0; check_references 1431/0-err/0-hashless; check_constructs 0 err; coverage PASS (1115/1115).
- **Net rescan conclusion:** armdef is substantially COMPLETE + CORRECT. The scramble dropped only a handful of sidebars (all now fixed: Static/Dynamic Targets, Possible Abuses of Storms, R/D/T table) + mis-grouped the 3 elemental story-seeds (fixed). Bulk of content converted correctly despite the mangled HTML.

## OWNER DECISIONS ON 0.5.0 CLOSEOUT (2026-07-27)
1. **arm5e supplements (5 subdirs) → NEXT effort** (owner: "we'll do that next"). Still 0.4/MENTIONS; the 1356 whole-dir hashless WARNs are all here (core scope = 0). Not part of 0.5.0 core.
2. **Core TABLE-caption DESCRIPTIONs → STRIPPED** (owner: "strip"). Removed all **49** editorial captions ("The source presents this as a sidebar table…" / "Presented in the source as…" / the 2 "Material and Size Tables" split-notes) across 11 core files. Table DATA (Table Columns + TABLE rows) is verbatim + self-documenting. Kept VERSION 0.5.0 (finalization, not post-release revision). Committed 30bf8ac. Gates green (validator 100/0/0, refs 0-err, constructs unchanged, coverage PASS). **0 editorial-prefix DESCRIPTIONs remain in core.**
3. **arm5e-core draft rescan → NOT POSSIBLE** (owner: "no manuscript"). The 2004 core edition has no draft; arm5e-core stands on its own coverage gate + the verbatim verification done during the GUIDANCE re-treatment. (Only armdef had a draft manuscript to cross-check.)

## FINAL STATE — ALL GATES GREEN, BOTH EDITIONS (2026-07-27)
- CORE: validator 100/0/0 · refs 706/0-err/0-hashless · constructs 3 hook/1 opt/37 guid/0 err · coverage PASS. SPEC_VERSION 0.5 / VERSION 0.5.0. Editorial table-captions stripped.
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

## SUPPLEMENTS → 0.5.0 IN PROGRESS (2026-07-27) — see SUPPLEMENTS-0.5-handoff.md for the resume prompt
- DONE + committed/pushed: version+REFERENCES-hash all 5 (`2b3bb94`); Power-types + House-ref disambiguation, owner-reviewed (`73bb309`). apply_references gained `--only=<subdir>`.
- Hashless 274→153. REMAINING: (A) finish supplement disambiguation ONE-AT-A-TIME w/ owner — The Gift/Church/Parma→core-systems; Second Sight/Animal Ken/etc→Ability (watch Ability-vs-Virtue nuance); Faerie Blood/Elementalist/Failed Apprentice→owner call; 4 rop-faerie faerie-powers→leave hashless; Damage/Advancement Table edge. (B) grogs GUIDANCE+caption strip (105, verbatim from Grogs HTML). (C) 5 coverage gates. (D) core Houses restructure (owner: DEF mechanical + prose→new houses.lore pointing to DEF; drop order-of-hermes dup House DEFs; verbatim-merge vs source; VERSION 0.5.1 on touched core). (E) finalize+commit.
- Power-types RULE: Thing-of-Virtue/Virtue-Flaw context = the Virtue; creature power stat-line = the Magic Quality.

## SUPPLEMENTS 0.5.0 — TASK B (grogs GUIDANCE) DONE + PROVEN (2026-07-27, this session; UNCOMMITTED)
- **Completeness correction:** the editorial-prefix set is **131 records, not 105** — the handoff missed the 26 `"Source presents this as…"` variant (73 "The source presents this as" + 26 "Source presents this as" + 32 "Presented in the source as"). All 131 in `arm5e-grogs-0.4-systems.ttrpg`.
- **Owner decision (AskUserQuestion 2026-07-27): GUIDANCE (core-faithful).** Model: prose records → module-level `GUIDANCE { ENTRY ^"name" #hash { CONCERNS[…] TEXT } }`; tables → stay DEF w/ verbatim source prose (or stripped); grouping headers → thin DEFs.
- **Result:** 113 prose → GUIDANCE ENTRY (name-matched → coverage preserved), 11 table records (verbatim source prose via drop_tables extract, or DESCRIPTION stripped when sidebar is table-only), 7 thin grouping DEFs (incl. "Time-Lost Witnesses…(cont'd)" + 6 "Story Seeds: X"). 56 prefix-artifact refs dropped. All 131 names survive as ENTRY/DEF (0 lost).
- **TEXT is source-verbatim** — extracted from source HTML by heading (`scratchpad/grogsB/extract.py`), **complete-by-construction**: body stops at next heading OR enclosing sidebar `</div>` (the sidebar-boundary was the crux — 32 records over-grabbed into main text before that fix; "The Vibria Company" pulled in Almogavars content). Emphasis preserved (`<em>`→`*`, `<strong>`→`**`), PDF span-split hyphenations rejoined. Verbatim asserted per-record (token-subsequence vs source, with the same merges) → **0 fails**, incl. per-chunk check on table prose. Found + fixed corpus paraphrases the source-extract corrects (Aging Chart "nearby table"→"the table"; Weight-of-Common-Materials flattened Size/Weight sub-table; "Sources of Inspiration" corpus was a 10-tok stub, source has full 91-tok body).
- **Refs re-derived:** `apply_references.py … --only=grogs` (folds converted-record REFERENCES away; GUIDANCE uses CONCERNS/TEXT, untouched by apply_references).
- **Gates PROVEN:** validator 100 files 0/0; check_constructs 70 guidance / 0 err; check_references 1814 refs / 0 err / 155 hashless; **0 editorial prefixes remain**; grogs coverage gate **PASS** (645 inv / 576 covered / 69 excluded / 0 uncovered, non-empty).
- Tools: `scratchpad/grogsB/{extract.py,gen.py}`; backup `systems.orig.ttrpg`.

## SUPPLEMENTS 0.5.0 — TASK C coverage snapshot (2026-07-27)
- **grogs PASS** (0 uncovered). The other 4 FAIL, all in the **Text Box** category (sidebars):
  hedge-magic 65 uncovered (67/132), covenants 39 (67/106), rop-magic 76 (38/114), rop-faerie 37 (40/77) = **217 uncovered Text Boxes**.
- Memory `arm5e-supplements-recordgap` claims a prior pass built ~260 sidebar records → these may be over-enumeration / name-mismatch rather than pure gaps. NEEDS per-supplement source characterization before dispositioning (never rubber-stamp). NOT yet investigated.

## SUPPLEMENTS 0.5.0 — hashless after B = 155 (was 153); disambiguation (task A) still owner one-at-a-time. Not started.

## SUPPLEMENTS 0.5.0 — TASK C: SIDEBAR BACKFILL (owner decision 2026-07-27: BACKFILL ALL 217, parity)
- Coverage gates: grogs PASS. hedge-magic/covenants/rop-magic/rop-faerie FAIL with **217 uncovered Text Box sidebars** total (hedge 65, rop-magic 76, covenants 39, rop-faerie 37). VERIFIED genuinely ABSENT from corpus (sampled 7 in rop-magic → 0 found), present in source. Types: story-seeds, worked examples, rules-discussion boxes, options, templates. The original supplement conversions captured mechanical records but skipped sidebars; the prior record-gap pass (memory `arm5e-supplements-recordgap`) was uncommitted/lost or the sidebars were deferred (manifests show deferred:0).
- **Owner: backfill all 217** as verbatim GUIDANCE ENTRYs from source HTML, same proven method as grogs (extract by heading, sidebar-bounded, verbatim-asserted). Source HTMLs: `~/Working/arm5e-sourcebook-conversions/{hedge-magic-revised,covenants,rop-magic,rop-faerie}/*.html`. PLAN: pilot rop-faerie (37) → coverage green + gates green, then scale to the other 3. Templates (e.g. "Cat Character Template") captured as GUIDANCE-verbatim for now (structural template→.actor is a possible follow-up). CONCERNS optional (TEXT-only OK, matches core's 13/50 CONCERNS-less).
- **DONE + PROVEN (2026-07-27, this session; UNCOMMITTED):** backfilled all 217 sidebars as new `arm5e-<supp>-0.4-sidebars.ttrpg` files (EXTENSION DEPENDS_ON each supplement's Core_Ext). Split: **GUIDANCE ENTRY** for prose sidebars (verbatim TEXT), **TABLE DEF** for table-bearing sidebars (structured columns/rows + verbatim prose DESCRIPTION — NOT flattened into a string, per the prime directive). Per supplement: rop-faerie 33 GUIDANCE + 4 TABLE, hedge-magic 63 G + 2 T, covenants 39 G, rop-magic 75 G. Deterministic hashes (sha1 of edition|supp|name). Tools: `scratchpad/grogsB/{srcextract.py,backfill.py}`.
  - Extraction = same proven method as grogs (sidebar-`</div>`-bounded, emphasis preserved, span-splits rejoined) PLUS heading-fragment coalescing (truncated toc names like "Does My Character" → real body under the continuation fragment) and `<table>` parsing. Every unit verbatim-asserted (token-subsequence vs source) → 0 non-verbatim.
  - `sidebar on page 145` (rop-magic) = back-cover publication box → **excluded** in the manifest, mirroring rop-faerie's owner-approved 2026-07-26 disposition (settled policy, not a new call).
  - **ALL 5 supplement coverage gates PASS** (0 uncovered each): grogs 645/0, hedge-magic 921/0, covenants 726/0, rop-magic 824/0, rop-faerie 731/0. sources.json synced (+4 files, 150 total). validator 104/0/0, check_constructs 0 err, check_references 0 err.
  - **Backfilled files carry NO REFERENCES** (GUIDANCE=TEXT is not ref-scanned; TABLE DESCRIPTIONs left ref-less). Do NOT run `apply_references --only=<supp>` on them — it would STRIP that supplement's committed per-ref disambiguation (see regression note).

## ⚠ REGRESSION found + fixed (2026-07-27): apply_references --only strips a supplement's manual disambiguation
- `apply_references --only=grogs` (run during task B to re-derive grogs refs) **stripped the 10 committed grogs House-ref hashes** (73bb309) → 5 became hashless (other 5 folded into GUIDANCE). Because "House X" is multiply-defined (houses.ttrpg + order-of-hermes.ttrpg), apply_references can't auto-resolve it and drops the manual hash.
- **FIXED:** re-hashed the 5 grogs House refs to the canonical houses.ttrpg anchors (settled policy). Verified: grogs House refs 0 hashless; covenants (18) + rop-faerie (4) House hashes intact (NOT regressed — I never re-ran apply_references on them). **RULE: never re-run apply_references on a supplement after its disambiguation.**

## SUPPLEMENTS 0.5.0 — TASK A disambiguation IN PROGRESS (2026-07-27; UNCOMMITTED). Hashless 150 → 58.
- **Settled clusters applied (66 refs), per owner-approved core policy** (not re-asked): The Gift 50 + The Church 5 + Parma Magica 4 → core-systems concept; True Faith 4 + Ghostly Warder 2 → Virtue (context confirmed: refs in faith Virtues/Flaws, Ghostly Warder in "Magical Warder" Virtue); Animal Trainer 1 → sole grog Training-Package anchor.
- **Cluster 1 Ability-vs-Virtue (26 refs) — owner reviewed per-ref against source, CONFIRMED + applied:** Second Sight 18 → **Ability** (source repeatedly: "the Ability", "Supernatural Ability", "a score of"); Animal Ken 3 → **Virtue** (source explicit: "Supernatural Virtue Animal Ken" / "Animal Ken Virtue" — context FLIPS the naive Ability default, vindicating case-by-case); Wilderness Sense 2 → Ability (Atlantean Magic "Ability Roll", Magical Blood "Supernatural Ability") + 1 → Virtue (Sailors, listed under "Virtues and Flaws"); Magic Sensitivity 2 → Ability. Anchors: SecondSight-Ability #t2Lm60x9JehOADnxby9Oub7N, WildSense-Ability #tSvkpsdrvckD5kgaS9ArVu5L, WildSense-Virtue #tz6bsyR4yX8MWr8GlA8RLh6F, MagSens-Ability #t32ity40YBIfef8Dn3urAmdV, AnimalKen-Virtue #tVAOPf1PKHbNri1MEmtic7AU.
- **REMAINING 58 hashless — owner case-by-case (in progress):** Elementalist ×4 =19 (Hedge Art vs Virtue; all refs inside Elemental Affinity/Philosophiae/Theurgy/Medicine/Vulnerable-to-Form Virtues → recommend Hedge Art), Faerie Blood 16 (owner wants to check sources; 3 anchors), Failed Apprentice 15 (Virtue vs grog Training Package), Magical Meditation 2 (Ability vs Magic Quality, in "Grant (Major Virtue)" creature power), 4 rop-faerie faerie-powers (recommend leave hashless — no standalone hashed DEF), Damage Table 1 + Advancement Table 1 (pick from source).
- Method: `grep '"<Name>" -> ^"<Name>"'` for the hashless refs; pull enclosing DEF + DESCRIPTION sentence + Source; apply `"<Name>" -> #hash ^"<Name>"` per-file/DEF; verify validator 0/0 + check_references 0-err. Per-ref context tool inline in this session.
- D + E still pending. Owner decisions come one cluster at a time with source evidence.

## SUPPLEMENTS 0.5.0 — TASK A DISAMBIGUATION COMPLETE (2026-07-27; UNCOMMITTED). **0 hashless across all of arm5e/0.4.**
All 150 remaining hashless resolved, owner reviewed per-cluster with source evidence:
- Settled (66): The Gift 50 / The Church 5 / Parma Magica 4 → core-systems concept; True Faith 4 / Ghostly Warder 2 → Virtue; Animal Trainer 1 → sole grog anchor.
- Cluster 1 Ability-vs-Virtue (26): Second Sight 18 → Ability; **Animal Ken 3 → Virtue** (source "Supernatural Virtue"); Wilderness Sense 2 Ability + 1 Virtue (Sailors); Magic Sensitivity 2 → Ability.
- Cluster 2 Elementalist (19) → **Hedge Art** (source "the four Elementalist Forms").
- Cluster 3 Faerie Blood (16) → **core Virtue** #t42wfOx20p6v1MMqVFQRKMz3 (every mention names the Virtue/trait).
- Cluster 4 Failed Apprentice (15) → **core Virtue** #tUGeMVmLG8tnV6RcT8JrbBsy (Minor Social Status Virtue; owner confirmed even the template's virtue-assignment/CHOICE ultimately reference it; description is non-mechanical prose).
- Magical Meditation (2): **SPLIT** — "This Quality" occurrence → Magic Quality #tUVmSPidFhAHJZElG4cK9pa8, "the Supernatural Ability" occurrence → Ability #tBapzC9frzWETwU4EkhEh2X7.
- Damage Table (hedge) → obstacles Recovery copy #tPmMFIniA2THCTPSXmiTuGW0; Advancement Table (covenants) → long-term-events copy #tV0Ccacyab7mMNWKyr8BxusN (owner's pick; both are byte-identical duplicate core DEFs).
- 4 rop-faerie statblock faerie-powers (Endless Wine/Extend Glamour/Focus (Domestic Work)/Transform into Object (Plant)): owner said **hash them** → added sha1-based #hash to each bestiary.ttrpg DEF + pointed the refs. 0 hashless.
- **⚠ DUPLICATE-DEF SMELLS FLAGGED for task D consolidation** (same class as Houses): obstacles.ttrpg has TWO byte-identical `^"Damage Table"` DEFs (Combat Sequence :43 + Recovery :667); `^"Advancement Table"` is byte-identical-duplicated across long-term-events :68 + character-creation :292.
- **GATES ALL GREEN:** validator 104 files 0/0; check_constructs 0 err; check_references 1814 refs / 0 err / **0 hashless**; all 5 supplement coverage gates PASS. Both cores + all 5 supplements now fully at 0.5.0 for validation/references/constructs/coverage.
- Supplement A/B/C committed + pushed: arm5e `9ddba59`, mastra `234bb21` (rop-magic page-145 exclusion), dsl `baab029` (worklog).

## CORE 0.5.1 — DUPLICATE TABLES + HOUSES RESTRUCTURE (2026-07-27; UNCOMMITTED)
### Duplicate-table consolidation (owner: "take care of the duplicate tables")
- `^"Damage Table"` was defined TWICE byte-identically in obstacles.ttrpg (Combat Sequence :43 + Recovery :667); `^"Advancement Table"` twice (long-term-events :68 + character-creation :292, differing only in column-header casing). Both to-drop copies were UNREFERENCED. Removed the Combat Damage-Table copy (kept Recovery #tPmMFI — owner's disambiguation pick) and the character-creation Advancement-Table copy (kept long-term-events #tV0Cc). Coverage safe (name-match): core Table 108/108 still covered. VERSION → 0.5.1 on obstacles + character-creation.
### Houses restructure (owner-directed)
- **Reconciliation:** houses.ttrpg DESCRIPTIONs are the verbatim-complete narratives — proven against the core source HTML (`arm5e-corebook-conversion`): 11/12 byte-exact to each `<h4>HOUSE X</h4>` section; Verditius complete across an interrupting "Hermetic Oath" sidebar. The order-of-hermes writeups are SHORTER paraphrases with **0 unique content** (Mercere "assuming"/Tytalus "fell" = tense/verb synonyms of the source text). So: use houses.ttrpg narratives; drop OoH.
- **New `arm5e-0.4-houses.lore`** — 12 `### House X` sections, verbatim narrative, with a `>` pointer to the `^"House X"` DEFs (mechanics = House Type/Benefit/Source structured fields). Registered in sources.json.
- **houses.ttrpg**: 12 House DEFs keep `EXTENDS "Hermetic House"` + PROPERTIES; long DESCRIPTIONs removed (0 remain). **order-of-hermes.ttrpg**: 12 duplicate House DEFs dropped (19 non-House DEFs kept). OoH's by-name House refs already pointed at the canonical houses.ttrpg hashes, and no records referenced the OoH House hashes → clean drop. VERSION → 0.5.1 on both.
- **FINAL GATES — ALL GREEN, BOTH EDITIONS:** arm5e validator 104/0/0 · refs 1801 / 0-err / **0 hashless** · constructs 0 err · coverage core + 5 supplements ALL PASS. armdef validator 41/0/0 · refs 1431 / 0-err / 0-hashless · constructs 0 err · coverage PASS.
- REMAINING: commit + push core 0.5.1 (tables + Houses); update this worklog.

## NEXT EFFORT — 0.5 version-dir migration + Houses of Hermes: True Lineages (2026-07-27)
Plan + kickoff prompt: **`HOH-TRUE-LINEAGES-0.5-handoff.md`** (authoritative; read it first).
- **Phase 0 — version-dir migration (owner-confirmed):** both editions are complete at DSL 0.5 but
  still sit in `0.4/` dirs with `-0.4-` filenames. `git mv arm5e/0.4 → arm5e/0.5` and
  `armdef/0.4 → armdef/0.5` (**keep the edition-first layout — no top-level `0.5/`**, the owner
  confirmed that structure is deliberate); rename the 201 `-0.4-` filenames to `-0.5-`; update
  `sources.json` (153 entries), the 8 mastra coverage manifests, the mastra scripts/gates, and this
  worklog. Leave `TOR2E_04` alone (different repo, still spec 0.4). Rename not copy+freeze: the files
  in `0.4/` are already SPEC 0.5, so freezing them as "0.4" would mislabel them; git history holds the
  true 0.4 state.
- **Phase 1 — True Lineages → DSL 0.5.** Extraction DONE + verified (144pp → 528 toc units: 428
  Heading / 93 Text Box / 7 Table). Corpus foundation (`core-ext`) + coverage manifest committed;
  **baseline 586 inventory units / 576 uncovered** = the scope. Deterministic hand-conversion in the
  main loop (narrative-heavy book, modest mechanical set — not the mastra pipeline). Pilot Chapter One
  (Bonisagus) end-to-end, then Guernicus / Mercere / Tremere.
- Reusable verbatim-slicing tooling moved out of the session scratchpad into a durable home:
  `arm5e-sourcebook-conversions/scripts/{srcextract.py,backfill_sidebars.py}` (verified on True
  Lineages: 514 headings indexed).

## PHASE 0 — 0.5 VERSION-DIR MIGRATION: DONE + PROVEN (2026-07-27)
Pure rename; **zero content change**. Every gate reproduces its pre-migration number exactly.

- `git mv arm5e/0.4 → arm5e/0.5`, `git mv armdef/0.4 → armdef/0.5` (edition-first layout kept; no
  top-level `0.5/`). `arm5e/0.1|0.2|0.3` untouched. 201 files `git mv`'d `-0.4-` → `-0.5-`
  (git status: 147 R + 55 RM + 1 M — history preserved).
- In-corpus filename references rewritten: 230 occurrences across 55 files. Verified first that
  **every** `-0.4-` occurrence in the corpus was a filename (199 distinct, all quoted/backticked
  paths); the only bare `0.4` was `sources.json`'s stale `content_version` → `"0.5.0"`.
  `DEPENDS_ON` uses file-IDs, not filenames — confirmed unaffected (refs gate unchanged).
- `sources.json`: 151 entries repathed + `houses-true-lineages/…-0.5-core-ext.ttrpg` registered
  (was on disk but unlisted since `79c7d31`) → **152 entries, 0 missing / 0 unlisted vs disk.**
- External refs updated: 8 mastra coverage manifests (`corpusDirs` + filenames inside disposition
  reasons), 60 mastra `scripts/`+`src/` files, mastra `README/RESUME/TASKS.md`,
  `titterpig-dsl/bridges/README.md`. `TOR2E_04` and every `dnd5e`/`dnd5.5e`/`tor2e` `0.4` path left
  alone; the `arm4-to-arm5e-0.4-appendix-i.bridge` **filename** deliberately preserved (bridge spec
  dir is 0.4) while its `--corpus arm5e=` path moved to 0.5.
- **GATES — every number matches the pre-migration baseline:** validator arm5e/0.5 105 files 0/0 ·
  armdef/0.5 41/0/0 · check_references arm5e 1801 refs 0 err **0 hashless** / armdef 1431 0 err 0
  hashless · check_constructs arm5e 0 err (3 hook / 1 optional / 70 guidance) / armdef 0 err ·
  coverage 7/8 **PASS** with identical unit counts (corebook 1736, covenants 726, grogs 645,
  hedge-magic 921, rop-faerie 731, rop-magic 824, armdef 1115; all 0 uncovered).
  8th = `arm5e-houses-true-lineages` **FAILs by design** — 586 units / 576 uncovered = the Phase 1
  scope. (The handoff's "all 8 PASS" was off by this one; corrected here.)

### ⚠ PRE-EXISTING BREAKAGE surfaced by running the bridge gate (NOT caused by the migration)
`ttrpg_validator.py bridges/0.4/arm4-to-arm5e-0.4-appendix-i.bridge --corpus arm5e=…` →
**1 error: `destination reference ^"Starting Character Age" is not defined in edition "arm5e"`.**
- Cause: the core 0.5 re-treatment (`6b69277`) converted the `^"Starting Character Age"` DEF into a
  `GUIDANCE ENTRY` (`arm5e-0.5-character-creation.ttrpg:351`). Exactly the documented trap — *a
  GUIDANCE ENTRY is not a ref-able anchor*; the bridge's inbound ref was not checked first.
- **PROVEN pre-existing:** the identical error reproduces against the pre-migration corpus
  (`git archive 79c7d31 arm5e/0.4` → same single error). Migration is not implicated.
- Not fixed — reverting a GUIDANCE→DEF is a content decision. **Owner call pending** (options: give
  the bridge an `ALIASES` entry; revert that one record to a DEF carrying the verbatim text; or make
  GUIDANCE ENTRYs anchor-able in the gates). Also: the bridge gate is not part of
  `arm5e/armdef` gate runs, which is why it went unnoticed — worth wiring in.

## PHASE 1 PILOT — True Lineages Chapter One (House Bonisagus) DONE + PROVEN (2026-07-27)
Deterministic hand-conversion in the main loop. **pp.4–34 fully converted; that slice is 0 uncovered.**

**Output** (6 files in `arm5e/0.5/houses-true-lineages/`, all registered in `sources.json` → 158 entries,
0 missing / 0 unlisted): `…-bonisagus.lore` (29 verbatim narrative sections) · `…-bonisagus.ttrpg`
(House Utilities: House Acclaim / Folios / Intrigue; Original Research + 3 Breakthrough types + 6
procedure steps; 4 Example Discoveries + **6 Parma Magica folds**) · `…-virtues-flaws.ttrpg` (7) ·
`…-spells.ttrpg` (Reveal the Lingering Spirit, InMe 20) · `…-statblocks.ttrpg` (Glaucon, 19 typed stat
lines) · `…-sidebars.ttrpg` (all 20 Text Boxes: 13 GUIDANCE + 6 TABLE DEFs + 1 OPTIONAL).
`core-ext` gained 6 types: House Utility, Breakthrough, Original Research Step, Example Discovery,
Parma Magica Fold, Example Character.

**GATES — all PROVEN:** verbatim gate PASS (every emitted TEXT/DESCRIPTION is a token subsequence of
the source) · completeness **363/363 source units on pp.4–34, 0 tokens lost** · validator arm5e/0.5
**110 files 0/0** · check_references **1801 refs / 0 err / 0 hashless** · check_constructs 0 err ·
coverage: Chapter One slice **0 uncovered** (book-wide 89 covered / 40 excluded / 457 remaining =
Chapters 2–4, not yet converted).

### METHOD — three defects the gates caught, each fixed at the root (this is what scales)
1. **Heading-bounded slicing silently drops narrative.** The proven `srcextract` method bounds a body
   at the next heading, so text resuming AFTER an interrupting sidebar is lost — **34 of 129 paragraphs
   on pp.4–20**. Replaced with a slicer over the per-page JSON's explicit `box_open`/`box_close`
   stream (`scratchpad/tl/pageslice.py`), which partitions EVERY unit on a page into exactly one
   destination — complete by construction. **The old method would have under-converted all four chapters.**
2. **Column-order artifacts.** Four places emit a section heading BEFORE the tail paragraphs of the
   preceding column (House Utilities/p21, Original Research/p26, Bibliography+Figurine/p34). Each was
   **verified against the rendered PDF page image** before being encoded as an explicit reassignment.
3. **Ligatures.** The True Lineages extraction profile does NOT de-ligature (`reﬁne`), unlike every
   other arm5e source HTML — the committed corpus contains **zero** ligature characters. Normalized in
   the conversion layer, on both the emitted text and the verification reference.
   ⚠ **`books.py` profile gap — fix at extraction time for Societates and Mystery Cults.**

### Tables — structured, never flattened, each verified against the page image
5 of the 7 HTML tables are in Chapter One. The PDF splits header cells and value cells across
different x-bands, so the raw grid is unusable as-is: added `fit_columns` (merge adjacent columns that
are never both non-empty — lossless) plus wrap-row joining, with the real column set read off the
rendered page. `Research and Acclaim Points` (p.21) has NO `<table>` markup at all — a dot-leader list;
its 11 rows are sliced from the source between each leader and the next label (labels asserted present,
values never hand-entered). Verified page images: 5, 7, 14, 21, 22, 24, 26, 33, 34.

### Decision log (autonomous method/design calls)
| # | Decision | Why |
|---|---|---|
| 6 | Page-JSON box stream replaces heading-bounded slicing as the primary slicer. | Complete by construction; the heading method provably dropped 26% of the narrative. |
| 7 | 6 new core-ext types rather than overloading core types. | Matches the supplement precedent (RoP:Magic/Hedge each declare their own); the book distinguishes these kinds itself. |
| 8 | Glaucon = a DEF in `…-statblocks.ttrpg` (RoP:Magic precedent), not an `.actor`. | In-edition consistency; arm5e has no `.actor` files. **Flagged for the owner** — the skill's query test would also allow `.actor`. |
| 9 | Every stat line is its own typed field (19 for Glaucon), not one prose blob. | Prime directive; RoP:Magic precedent. |
| 10 | `Key Facts` = a structured DEF (Population / Domus Magna / Prima / Favored Tribunals). | It is a data box, not prose. One per House chapter. |
| 11 | The asterisk the source puts after a House-exclusive V/F name → `^"House Exclusive"` field; the bold run-in label is dropped from DESCRIPTION (it only repeats the DEF name). | The asterisk is data the source explains in its own intro; a run-in duplicate is noise. |
| 12 | Narrative sub-headings / V/F category labels / the "NEW … SPELL" label → `excluded`, reusing the owner's 2026-07-26 Grogs wording. | Settled precedent, not a fresh call. Completeness is separately proven by the 363/363 token gate, so exclusion hides nothing. |

## TRUE LINEAGES COMPLETE — Chapters 2, 3 and 4 converted (2026-07-27)
**The whole book is done: `coverageAudit.ts arm5e-houses-true-lineages.manifest.json` → 586 units,
468 covered / 118 excluded / **0 UNCOVERED**, exit 0.** All 8 arm5e/armdef coverage gates PASS.

| Ch | House | pp | Output |
|---|---|---|---|
| 2 | Guernicus | 35–77 | `.lore` (29 sections) · `guernicus.ttrpg` 60 records (15 Code clauses each with its Oath sentence as a typed field, Peripheral Code, Tribunal procedure, penalties + 6 punishments, 10 Quaesitorial duties, Shroud Magic) · `guernicus-spells.ttrpg` (20 spells + 5 guideline sets + Fenicil's 8 Rituals) · `guernicus-sidebars.ttrpg` (27 Text Boxes) |
| 3 | Mercere | 78–109 | `.lore` (11) · `mercere.ttrpg` (9 Mastered Spell abilities, Portals, Mutantum Magic, the untitled vis-exchange TABLE) · `mercere-virtues-flaws.ttrpg` (19 V + 9 F) · `mercere-spells.ttrpg` (11) · `mercere-sidebars.ttrpg` (21) |
| 4 | Tremere | 110–144 | `.lore` (29, incl. the Appendix Timeline) · `tremere.ttrpg` 41 records (promotion, 9 specialist roles, **15 Certamen styles**) · `tremere-spells.ttrpg` (15) · `tremere-virtues.ttrpg` (7) · `tremere-bestiary.ttrpg` (4 creature stat blocks) · `tremere-sidebars.ttrpg` (34 GUIDANCE) |

**GATES — all PROVEN:** verbatim gate PASS on every chapter · completeness **363/363, 667/667,
339/339, 450/450 source units, 0 tokens lost** in all four · order gate 0 out-of-order sections ·
validator arm5e/0.5 **122 files 0/0**, armdef 41/0/0 · check_references 1802 / 0 err / **0 hashless**
(armdef 1431/0/0) · check_constructs 0 err · bridge 1 file 0/0 · `sources.json` **173 entries, 0
missing / 0 unlisted**.

### THE DEFECT CLASS THAT MATTERED — reading order, invisible to every existing gate
The page-JSON stream is authoritative for BOX membership but **not for reading order**. It can emit a
display heading before the preceding column's tail (mis-filing paragraphs between sections) or the
right column before the left (scrambling order within a section). **Validation, references and
coverage all pass while this is wrong, and the completeness gate only asks whether each unit exists
somewhere.** New tooling in `arm5e-sourcebook-conversions/scripts/`:
- `layoutorder.py` — reconstructs each page's true reading order from `pdftotext -layout` by splitting
  lines at the column boundary; `order_report` (the **order gate**) and `sort_units`.
- `layoutanchor.py` — proves how many leading units of a section were displaced, by finding what is
  printed after that heading **in its own column cell** (substring matching anchors "Penalties" inside
  "Determining Penalties" in the other column — it must be a whole-cell match).
- `hoh_chapter.prepare(lo, hi)` — slice → repair displacement → restore order → report what it could
  not prove. 6 repairs in Ch2, 5 in Ch3, 1 in Ch4.
- **It found a real defect in the already-committed Chapter One**: p30's right column continues
  `HERMETIC INTEGRATION`, but 3 paragraphs had been filed under `Example Discoveries`. Fixed (`7899f14`).
- ⚠ Twice the gate itself was wrong before the corpus was (comparing positions across different pages).
  Both alarms were investigated and disproved **before** any content was changed.

### Other source shapes handled at the root
- `list` units (9, all in Ch3) were invisible to both the slicer and the completeness gate — both read
  them now.
- A section is only treated as a **spell** if it actually prints a stat line: `Blood of Heroes` (a
  Virtue) and `Heroic` (a rules note) sit inside Mercere's spell run and were being mined for bogus
  Range/Target values and truncated.
- V/F Size and Category come from **each entry's own opening line**, never the summary sidebar — that
  box's first group heading did not survive extraction.
- Two-line box titles are merged ("The House View of" + "Tremere in 1220"), so both outline units match.
- Stat lines are stripped from DESCRIPTIONs once parsed into typed fields — cut at the parsed value, so
  it can never slice through a word.
- Creature stat blocks in Tremere's sidebars → `tremere-bestiary.ttrpg` with per-label typed fields,
  keeping the narrative intro as the DESCRIPTION, rather than flattened into GUIDANCE prose.

### Decision log (additional autonomous calls)
| # | Decision | Why |
|---|---|---|
| 13 | `pdftotext -layout` is the reading-order oracle; the page JSON stays authoritative for box membership. | The JSON's order is wrong on ~12 pages; the printed layout is not. Cheaper and more reliable than reading page images. |
| 14 | Chapters 2–4 use House-scoped filenames (`guernicus-spells.ttrpg`), where Chapter One kept book-wide facet names (`spells.ttrpg`). | Avoids rewriting Chapter One's committed files. **Flagged for the owner** — harmonizing is a rename, not a re-conversion. |
| 15 | Fenicil's Rituals get their own type, not `Formulaic Spell`. | The source states their Technique and Form "are not involved in the casting or learning" and they are cast against an Ease Factor, not a level. |
| 16 | New types declared per chapter in `core-ext`: Code Clause, Tribunal Procedure Step, Hermetic Penalty, Quaesitorial Duty, Fenicil Ritual, Spell Guideline Set, Mastered Spell Special Ability, Certamen Style, House Specialist Role, Magic Creature. | Each is a kind the book itself enumerates; core has no place for them. |
