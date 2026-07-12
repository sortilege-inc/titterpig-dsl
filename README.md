# titterpig-dsl
A Domain Specific Language for encoding Tabletop Roleplaying Game Sourcebooks

## Status (v4 — 2026-07-12)

| Artifact | Status |
|---|---|
| `titterpig-dsl-spec.md` | **Canonical v4 spec** — current, authoritative |
| `AUTHORING-GUIDELINES.md` | v4 authoring best-practices for system-specific `.ttrpg`/`.lore` |
| `ttrpg.peg` | **v4 grammar** — aligned to the spec (adds `SPEC_VERSION`, `FIAT`) |
| `ttrpg_validator.py` | **v4 validator** — two levels: lint (spec adherence) + coherence (referential integrity), with FIAT waivers. Run: `python3 ttrpg_validator.py <file-or-dir>` |
| `tests/` | Validator fixtures — `good.ttrpg` (conformant) and `bad.ttrpg` (intentional findings) |
| `archive/` | **Historical / superseded** — not part of the current spec |

`titterpig-dsl-spec.md` is the single source of truth; `ttrpg.peg` and `ttrpg_validator.py` are
aligned to it. **Coherence is corpus-wide** — validate a whole system directory (not a lone file)
so cross-file references resolve.
