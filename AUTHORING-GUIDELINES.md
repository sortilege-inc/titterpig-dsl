# Titterpig DSL — Authoring Guidelines (v0.4)

> Advisory best-practices for writing **system-specific** `.ttrpg` and `.lore` files. The
> *normative* rules live in [`titterpig-dsl-spec.md`](./titterpig-dsl-spec.md) (v0.4); this document
> is how to apply them well. When the two conflict, the spec wins.

## 1. Prime directive — structure over prose

Represent anything a tool will read as **structured DSL**, never packed into a free-text string or
a comment. The grammar is permissive; do not use that permissiveness to bury data.

```
# Avoid — data trapped in a string:
^"Ring Increase" STRING "+1 Earth or Fire, +1 Command, Glory 44, 4 koku"

# Prefer — structured, machine-readable:
^"Ring Increase" DEF {
    ^"Earth" INTEGER 1
    ^"Command" INTEGER 1
    ^"Glory" INTEGER 44
    ^"Koku" INTEGER 4
}
```

The **shape** of a structure is yours to design (system-owned — there is no universal cross-system
type layer). The **discipline** of structuring over prose is universal. Genuine narrative flavor
stays prose and goes in `.lore`.

## 2. Choosing a file type

| If the content is… | Use |
|---|---|
| Game mechanics / rules | `.ttrpg` |
| A single character (PC/NPC) as its own file | `.actor` |
| *Structured* world-building a tool queries (locations, factions, NPCs, scenes, hooks) | `.setting` / `.frame` / `.arc` / `.campaign` |
| *Free prose* meant only to be read (history, color, fiction) | `.lore` (Markdown, no DSL) |

**Query test:** if a tool must look something up in it → structured container; if it's just meant
to be read → `.lore`. The same subject can appear in both (mechanics in `.ttrpg`/`.setting`, story
in `.lore`) — mirror, don't duplicate.

## 3. Naming & organization

- One repo per system (`titterpig-dsl-<system>`).
- Organize files under a **content-version directory** (`0.3/`, `1.0/`) — version lives in the
  directory, not re-encoded redundantly everywhere.
- Consistent filenames within a system: `<system>-<version>-<book>-<facet>.ttrpg`.
- Every file declares `NAME`, `VERSION` (content), `SPEC_VERSION` (DSL-spec targeted, e.g. `"0.4"`),
  and `RELEASE_DATE`.

## 4. Identity & references

- **Hash IDs** are opaque, `≥16` alphanumeric chars, globally unique, and carry **no semantics** a
  tool parses out. Add one to anything that will be cross-referenced or corrected by errata.
- Use caret refs `^"Name"` for readability. **Define before you reference**, and keep every
  reference resolvable — coherence/consilience validation will flag danglers.

## 5. System vocabulary — be consistent with yourself

Systems invent their own keywords; the base spec won't stop you. The failure mode is *internal*
inconsistency:

- **One keyword per concept**, one **structural pattern per entity type**. (Don't author schools
  four different ways.)
- Prefer named structured sub-blocks over packed strings.
- Reuse the base-spec constructs (`DEF`, `EXTENDS`, `PROPERTIES`, `RULES`, `APPLIES TO`) rather than
  reinventing them.

## 6. Errata & corrections

- **Never in comments.** A stripped comment is a lost correction.
- Put corrections in a dedicated `*-errata-*` EXTENSION file as machine-readable
  `MODIFY` / `OVERRIDE` / `ADD`. Keep source files pristine; tooling composes the overlay.

## 7. Narrative — `.lore`

- Plain Markdown, no DSL syntax, written for humans.
- Keep mechanics out of `.lore` and prose out of `.ttrpg`: the ability's *rules* go in `.ttrpg`,
  its *story* in `.lore`.

## 8. Intentional exceptions — `FIAT`

Sometimes a value or an entity is *deliberately* out of bounds or incomplete — a boss with a
supernatural Ring 7, a one-off published NPC that omits standard stats. Mark it with `FIAT` so the
validator accepts it **and** the intent is on the record:

- **Reason required.** `^"Air" INTEGER 7 FIAT "Oni Lord: supernatural Air"` — never a bare `FIAT`.
  The reason is what turns a silenced error into an auditable decision.
- **Narrowest scope.** Property-level for a single odd value; element-level only when the whole
  definition is exceptional (it cascades over the entire subtree and will also hide real mistakes
  beneath it).
- **Not for routine partial NPCs.** Define standard NPCs against their own actor type (complete on
  their own terms). Reach for `FIAT` only for true one-offs — if you're writing it a lot, the
  underlying type probably needs adjusting instead.

## 9. Pre-commit checklist

- [ ] All mechanical data is structured (no data in strings or comments)
- [ ] Correct file type for the content
- [ ] `NAME` / `VERSION` / `SPEC_VERSION` / `RELEASE_DATE` present
- [ ] Hash IDs are opaque, `≥16` chars, unique — on everything referenced
- [ ] Every `^"Name"` / `#hash` / `EXTENDS` / `APPLIES TO` / `DEPENDS_ON` resolves
- [ ] One keyword-and-structure pattern per entity type
- [ ] Errata in overlay files, not comments
- [ ] Flavor prose in `.lore`, not `.ttrpg`
- [ ] Deliberate constraint/completeness deviations marked `FIAT "reason"` — and nothing else silenced
