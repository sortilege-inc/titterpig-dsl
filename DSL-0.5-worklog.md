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
