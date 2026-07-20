---
name: titterpig-dsl
description: >-
  Author, validate, and migrate Titterpig DSL — the system-agnostic language for encoding TTRPG
  sourcebooks as machine-readable `.ttrpg`/`.actor`/`.arc`/`.setting`/`.lore` files. Use when working
  in `titterpig-dsl` or any `titterpig-dsl-<system>` repo: writing or editing DSL, running the
  validator, resolving lint/coherence findings, applying FIAT/errata, or migrating a system to a new
  SPEC_VERSION. This is the canonical hub; system repos have thin skills that defer here.
---

# Titterpig DSL (canonical)

Titterpig encodes tabletop-RPG sourcebooks as **structured, machine-readable** data. `titterpig-dsl`
is the canonical repo; each game lives in its own `titterpig-dsl-<system>` repo and validates against
the tooling here. Current spec: **v0.4**.

## Authoritative files (read these; don't reinvent them)

All paths are inside the `titterpig-dsl` repo (from a system repo, `../titterpig-dsl/`):

| File | What it is |
|---|---|
| `titterpig-dsl-spec.md` | **Single source of truth** — the normative v0.4 grammar & semantics. |
| `AUTHORING-GUIDELINES.md` | Advisory best-practices for writing system content. Spec wins on conflict. |
| `ttrpg.peg` | v0.4 PEG grammar, aligned to the spec. |
| `ttrpg_validator.py` | v0.4 validator (two levels: lint + coherence). |
| `tests/good.ttrpg`, `tests/bad.ttrpg` | Conformant / intentionally-broken fixtures — worked examples. |
| `archive/` | Superseded material. **Not** part of the current spec — ignore for authoring. |

**When a fact isn't here, read the spec** — do not guess grammar or keyword semantics from memory.

## Prime directive: structure over prose

Anything a tool will read is **structured DSL**, never packed into a free-text string or a comment.
The grammar is permissive; that is not license to bury data.

```
# Avoid — data trapped in a string:
^"Ring Increase" STRING "+1 Earth or Fire, +1 Command, Glory 44, 4 koku"

# Prefer — structured, queryable:
^"Ring Increase" DEF {
    ^"Earth" INTEGER 1
    ^"Command" INTEGER 1
    ^"Glory" INTEGER 44
    ^"Koku" INTEGER 4
}
```

The *shape* of a structure is system-owned; the *discipline* of structuring is universal. Genuine
narrative flavor stays prose and goes in `.lore`.

## File types — the query test

If a tool must look something up in it → a **structured** container; if it's only meant to be read →
`.lore`.

| Content | File |
|---|---|
| Game mechanics / rules | `.ttrpg` |
| A single character (PC/NPC) as its own file | `.actor` |
| Structured world-building a tool queries (locations, factions, scenes, hooks) | `.setting` / `.frame` / `.arc` / `.campaign` |
| Free prose meant only to be read (history, color, fiction) | `.lore` (Markdown, no DSL) |

The same subject can appear in both — mechanics in `.ttrpg`, story in `.lore`. **Mirror, don't
duplicate.**

## Core constructs (defined normatively in the spec)

`BASE` / `EXTENSION` files · `DEF` · `PROPERTIES` · `EXTENDS` · `RULES` · `APPLIES TO` · `LIST OF` ·
`DEPENDS_ON … VERSION` · typed values (`STRING`/`INTEGER`/`ENUM`/`LIST`) with `REQUIRED`/`FIXED`/
`DEFAULT`/`MIN`/`MAX`. Reuse these rather than reinventing them; systems add their own *vocabulary* on
top, not their own *core*.

## Identity & references

- **Hash IDs** (`#…`): opaque, **≥16 alphanumeric chars**, globally unique, carry no parseable
  semantics. Add one to anything cross-referenced or corrected by errata.
- **Caret refs** `^"Name"` for readability. **Define before you reference.** Every `^"Name"` /
  `#hash` / `EXTENDS` / `APPLIES TO` / `DEPENDS_ON` must resolve — coherence validation flags danglers.
- Use `EXTENDS` when something *is a* Type with its own stat block; reserve `APPLIES TO` for
  trait/scope uses.

## Metadata (every file with a header)

`NAME`, `VERSION` (the game's own content version), `SPEC_VERSION "0.4"` (the DSL spec targeted),
`RELEASE_DATE`. Organize files under a **content-version directory** (`0.4/`); the version lives in
the directory, not re-encoded redundantly everywhere. Filenames: `<system>-<version>-<book>-<facet>.ttrpg`.

## Errata — never in comments

A stripped comment is a lost correction. Put corrections in a dedicated `*-errata-*` EXTENSION file as
machine-readable `MODIFY` / `OVERRIDE` / `ADD`. Source files stay pristine; tooling composes the overlay.

## FIAT — deliberate, reasoned exceptions

For values/entities *intentionally* out of bounds or incomplete (a boss with supernatural Ring 7; a
one-off published NPC missing standard stats):

- **Reason required.** `^"Air" INTEGER 7 FIAT "Oni Lord: supernatural Air"` — never a bare `FIAT`
  (the validator errors on a reasonless FIAT). The reason turns a silenced error into an auditable
  decision.
- **Narrowest scope.** Property-level for a single odd value; element-level only when the whole
  definition is exceptional (it cascades and will also hide real mistakes beneath it).
- **Not for routine partial NPCs.** Give standard NPCs their own actor type. If you're reaching for
  FIAT a lot, the underlying type probably needs adjusting.

## Validation

Two levels: **lint** (spec adherence, per-file) + **coherence** (referential integrity, corpus-wide).
Because coherence is corpus-wide, **validate a whole content-version directory**, not a lone file, so
cross-file references resolve.

```bash
# from a system repo (e.g. titterpig-dsl-tor2e):
python3 ../titterpig-dsl/ttrpg_validator.py 0.4/
```

Output lines: `<level> <SEVERITY> L<line> <message>`, ending with a
`N file(s) checked — E error(s), W warning(s).` summary. **Exit codes:** `0` = no errors (warnings
allowed), `1` = one or more errors, `2` = bad invocation. Note: a `... | tail` pipe reports the pipe's
exit status, not the validator's — check the summary line, or run unpiped, to read pass/fail.

**Goal: iterate to 0 errors / 0 warnings.** A genuine content omission the game's owner must resolve
should be **flagged**, not silenced — don't paper over it with FIAT.

## Completeness — validation status is NOT completeness

**A file that validates 0/0 can still be missing half the source.** Validation checks that what you
wrote is well-formed and internally coherent; it says nothing about whether you captured everything
the source contains. Converting a *subset* of a source and reporting it "done" — even with a
"follow-up / known limitations" note — is a **failure**, not a caveat. Coverage is measured against
the **source's own enumerable sets**, never against validation status or your memory of what you did.

This is enforced, not advisory:

- **The coverage gate is hard-blocking.** A conversion is complete only when
  `titterpig-mastra/scripts/coverageAudit.ts <manifest>` **exits 0** — i.e. every enumerable content
  unit the source lists (its outline's `Table:` / `Adversary:` / `Loremaster Character:` /
  `Text Box:` / `Map` tags, plus headings) is either **covered** by a corpus entity or explicitly
  **deferred / excluded with a reason** in the coverage manifest. Run it before reporting any
  conversion done; if it fails, the conversion is not done.
- **Deferral is the owner's call, not yours.** Marking a unit `deferred`/`excluded` records a
  decision *and its reason* in the manifest (bulk-dispositionable by pattern). You do not get to
  silently drop content or unilaterally decide a bucket is "the clean subset" — surface it and get
  sign-off. "Harder to structure" (heterogeneous rules prose) is a reason to *ask how to model it*,
  never a reason to skip it.
- **`sources.json` must be in sync** with the files on disk — an unregistered file is uncaptured
  content as far as a consumer that reads the manifest is concerned.
- Reuse the schema you already built. If a bucket's schema fits more of the source (e.g. more
  roll-tables, more items), the remaining instances are *in scope by default* — narrowing to a
  subset is a decision to surface, not a default to take.

## Migrating a system to a new SPEC_VERSION

The recipe that worked for l5r5e, tor2e, vtm5e, and draw-steel (see `titterpig-mastra/RESUME.md` for
the full write-up and live loose threads):

1. **Version dirs.** Freeze current content in a `<contentver>/` dir; create the new `0.4/` from it,
   renaming the version segment. Content `VERSION` stays the game's own; `SPEC_VERSION` is separate.
2. **Metadata.** Add `SPEC_VERSION "0.4"` and bump `VERSION` on every header. Watch for versions that
   live only in `DEPENDS_ON … VERSION` pins — those files still need a standalone `VERSION`, and pins
   updated. Beware false-positive `VERSION` matches inside keywords (`REVERSION`, `COTERIE_VERSION`).
3. **Hash IDs.** Lengthen any `#id` under 16 chars to ≥16, consistently corpus-wide.
4. **Undefined referenced types.** Define types referenced via `EXTENDS`/`APPLIES TO`/`LIST OF` but
   never defined — usually in core. If it's a genuine content omission the owner must resolve, flag it.
5. **`APPLIES TO` → `EXTENDS`.** Where a named *instance* uses `APPLIES TO [^"Type"]` to mean "is a
   Type" (has a stat block), convert to `EXTENDS`. Leave trait/scope uses. Per-case; validate after.
6. **Stale-hash `EXTENDS`.** `EXTENDS #deadhash ^"Name"` with a resolvable name → drop the dead hash
   (by-name is canonical). Hash-only `EXTENDS #dead` needs the intended target found.
7. **Validate** to 0/0.
8. **Commit** (see below).

## Git / commit conventions

- **Per-repo identity** — these clones carry no default git identity. Set:
  `Jordan Peacock <jordan@sortilege.online>`.
- **Push flow:** `git pull --rebase --autostash origin main && git push`. The remote frequently
  advances (Jordan pushes from elsewhere) and clones carry pre-existing whitespace/line-ending noise,
  so `--autostash` matters.
- Clone via SSH: `git@github.com:sortilege-inc/<repo>.git` (no `gh`/HTTPS).
- Commit/push only when the user asks.

## Pre-commit checklist

- [ ] All mechanical data structured (nothing in strings or comments)
- [ ] Correct file type for the content (query test)
- [ ] `NAME` / `VERSION` / `SPEC_VERSION` / `RELEASE_DATE` present
- [ ] Hash IDs opaque, ≥16 chars, unique — on everything referenced
- [ ] Every `^"Name"` / `#hash` / `EXTENDS` / `APPLIES TO` / `DEPENDS_ON` resolves
- [ ] One keyword-and-structure pattern per entity type (no internal inconsistency)
- [ ] Errata in overlay files, not comments
- [ ] Flavor prose in `.lore`, mechanics in `.ttrpg`
- [ ] Deliberate deviations marked `FIAT "reason"` — and nothing else silenced
- [ ] Validator reports 0 errors / 0 warnings (or every remaining finding is a flagged owner-decision)
- [ ] **Source-coverage gate passes** (`coverageAudit.ts` exits 0) — every enumerable source unit is
      covered or deferred/excluded-with-reason; `sources.json` in sync. Validation ≠ completeness.
