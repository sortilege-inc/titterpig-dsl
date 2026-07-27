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

## REMAINING BULK (runnable; resume fresh for quality):
- Core: the GUIDANCE sweep above; the 2 concentration-roll hooks in hermetic-magic (THEN target needs disambiguating between the two ^"Concentration" DEFs #tzkuW2sQSwdFvHyA6vbd5MFW / #tocBOFaacYAtllK16su3pLde); hashless-ref disambiguation (149).
- armdef: disposition the 180 uncovered headings (front-matter→exclude, etc.) to green the gate; then GUIDANCE; hashless-ref disambiguation (129).
- Finalize: SPEC_VERSION 0.5 + content VERSION patch on treated files; full gate re-run; commit.
