# titterpig-dsl
A Domain Specific Language for encoding Tabletop Roleplaying Game Sourcebooks

> **This repo is kept pristine.** It holds the **spec and its supporting files** only — grammar,
> validator, gates, authoring guidelines, conformance fixtures. **Nothing system-specific and no
> working files.** Session working logs, handoffs and conversion notes live in
> `titterpig-mastra/worklogs/`; system content lives in its own `titterpig-dsl-<system>` repo.

## Status (v0.5)

| Artifact | Status |
|---|---|
| `titterpig-dsl-spec.md` | **Canonical v0.5 spec** — current, authoritative, single source of truth |
| `AUTHORING-GUIDELINES.md` | Authoring best-practices for system-specific `.ttrpg`/`.lore` (advisory; the spec wins on conflict) |
| `ttrpg.peg` | **The grammar** — the formal statement of the syntax (v0.5, with the v0.6 working draft) |
| `check_grammar.py` | **Grammar check** — runs `ttrpg.peg` against files, with no dependency. `python3 check_grammar.py tests/*good* tests/decision6.ttrpg tests/ports-origin modules/0.6` must accept every file; `python3 check_grammar.py tests/grammar-bad --expect-refused` must refuse every file. A corpus may be measured the same way and is not gated |
| `ttrpg_validator.py` | **Validator** — two levels: lint (spec adherence) + coherence (referential integrity), with FIAT waivers. `python3 ttrpg_validator.py <file-or-dir>` |
| `check_references.py` | **v0.5 gate** — two parts. **A:** `REFERENCES` / `REFERENCED BY` coherence (DECISION-11; also parses the deprecated 0.4-era `MENTIONS`). **B:** every other reference site (§5d, DECISION-13) — `EXTENDS`, `APPLIES TO`, `LIST OF`, `CONCERNS`, `OVERRIDE`, `MODIFY`, `ALIAS … FOR` across all DSL file types. A hashless reference WARNs; a hashless reference whose name resolves to more than one distinct entity is an **ERROR**. `--show-warns` lists every site. |
| `check_constructs.py` | **v0.5 gate** — `GUIDANCE` / `HOOKS` / `OPTIONAL` / `.selections` semantics |
| `check_structure.py` | **Shape gate** — fails a corpus whose `DESCRIPTION`s outnumber its `PROPERTIES` blocks. It checked `REQUIRED` until v0.6; the validator does now (DECISION-34) |
| `apply_references.py` | Migration tool — emits `REFERENCES` blocks, hashing a target when its name has exactly one anchor |
| `samples/` | v0.5 conformance fixture (`.ttrpg` + `.selections`) |
| `tests/` | Validator fixtures — `good.*` (conformant) / `bad.*` (intentional findings), `mods-*` for the §13 modification system, `good.bridge` / `bad.bridge` for §21, `dice-good.ttrpg` for §8's dice (run it with `modules/0.6/`), `emphasis-good/` and `emphasis-bad/` for §5c's `EMPHASIS` kinds and `LABEL`, `embedded-good/` and `embedded-bad/` for §5c's embedded references (run both pairs with `check_references.py` as well), `tables-good.ttrpg` and `tables-bad.ttrpg` for §5e's `TABLE` (run the good one with `modules/0.6/`), `markdown-good.ttrpg` and `markdown-bad.ttrpg` for the Markdown-emphasis finding, `narrative-good/` and `narrative-bad/` for §16's `FROM` imports and scene types, `anchors-good/` and `anchors-bad/` for §20's two tiers of target (run both with `check_references.py` as well), `ports-good/` and `ports-bad/` for §19's ports (run both with `--corpus port-old=tests/ports-origin`, the edition they were ported from), `restate-good/` and `restate-bad/` for what may be stated twice under one hash (§13, DECISION-27), `actors-good/` and `actors-bad/` for §2's `.actor` files (DECISION-28), `text-good/` and `text-bad/` for §10's prose fields and §15's keywords in context (DECISION-29, DECISION-30), `grammar-bad/` for twelve planted syntax faults that `check_grammar.py --expect-refused` must refuse (DECISION-31), `values-good/` and `values-bad/` for a value against what its definition extends (DECISION-32; run `check_constructs.py` on both as well), `names-good/` and `names-bad/` for when two names are the same (DECISION-33; run `check_references.py` and `check_constructs.py` on both as well), `required-good/` and `required-bad/` for `REQUIRED` (DECISION-34), `pins-good/` and `pins-bad/` for `DEPENDS_ON … VERSION` pins (DECISION-35), `deps-good/` and `deps-bad/` for what a file depends on (DECISION-36) |
| `modules/` | **The dice module (§8, DECISION-18)** — `^"Die"` and d2 to d100, shipped with the spec and included by every edition. Validate a corpus that rolls dice with `modules/0.6/` passed alongside it |
| `bridges/` | **Cross-edition conversion documents (§21)** — cross-system, not system-specific; see the note below |

`titterpig-dsl-spec.md` is the single source of truth. `ttrpg.peg` states its syntax and is proven
on this repo's fixtures; the validator is a separate reader of the same syntax. **Coherence is corpus-wide** — validate a whole system version directory (not a lone file) so
cross-file references resolve.

### Why `bridges/` sits here despite the pristine rule
A `.bridge` (§21) is the one construct with **two** dependency lineages: it asserts correspondence
*across* two edition namespaces and belongs to neither. The spec places it "outside both, in the
canonical DSL repo's `bridges/<specver>/`" precisely so it cannot be mistaken for either edition's
content — so it is cross-system rather than system-specific. Validate in two-corpus mode:

```bash
python3 ttrpg_validator.py bridges/0.5/ \
    --corpus dnd5e="../titterpig-dsl-dnd5e/0.5" \
    --corpus dnd5.5e="../titterpig-dsl-dnd5.5e/0.5" \
    --corpus arm5e="../titterpig-dsl-arm5e/arm5e/0.5"
```
