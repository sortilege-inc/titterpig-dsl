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
| `ttrpg.peg` | **v0.5 grammar** — aligned to the spec |
| `ttrpg_validator.py` | **Validator** — two levels: lint (spec adherence) + coherence (referential integrity), with FIAT waivers. `python3 ttrpg_validator.py <file-or-dir>` |
| `check_references.py` | **v0.5 gate** — `REFERENCES` / `REFERENCED BY` coherence; `--show-warns` lists hashless refs. Supersedes `check_mentions.py`. |
| `check_constructs.py` | **v0.5 gate** — `GUIDANCE` / `HOOKS` / `OPTIONAL` / `.selections` semantics |
| `apply_references.py` | Migration tool — emits `REFERENCES` blocks, hashing a target when its name has exactly one anchor |
| `samples/` | v0.5 conformance fixture (`.ttrpg` + `.selections`) |
| `tests/` | Validator fixtures — `good.*` (conformant) / `bad.*` (intentional findings), `mods-*` for the §13 modification system, `good.bridge` / `bad.bridge` for §21 |
| `bridges/` | **Cross-edition conversion documents (§21)** — cross-system, not system-specific; see the note below |
| `check_mentions.py`, `apply_mentions.py` | **Superseded** by the `*_references` pair (0.4-era `MENTIONS`); retained only while a corpus still carries `MENTIONS` |
| `archive/` | **Historical / superseded** — v0.2–v0.3 material, not part of the current spec |

`titterpig-dsl-spec.md` is the single source of truth; `ttrpg.peg` and the validator are aligned to
it. **Coherence is corpus-wide** — validate a whole system version directory (not a lone file) so
cross-file references resolve.

### Why `bridges/` sits here despite the pristine rule
A `.bridge` (§21) is the one construct with **two** dependency lineages: it asserts correspondence
*across* two edition namespaces and belongs to neither. The spec places it "outside both, in the
canonical DSL repo's `bridges/<specver>/`" precisely so it cannot be mistaken for either edition's
content — so it is cross-system rather than system-specific. Validate in two-corpus mode:

```bash
python3 ttrpg_validator.py bridges/0.4/ \
    --corpus dnd5e="../titterpig-dsl-dnd5e/0.4" \
    --corpus dnd5.5e="../titterpig-dsl-dnd5.5e/0.4" \
    --corpus arm5e="../titterpig-dsl-arm5e/arm5e/0.5"
```
