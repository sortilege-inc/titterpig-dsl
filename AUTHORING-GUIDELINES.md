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

### The boundary (ratified 2026-07-14)

Where exactly "structure over prose" starts and stops — the operational test used by authors and
by validation tooling (the titterpig-mastra quality judge cites this section):

Structure is **required** for:

1. **Labeled stat-lines and roll formulas** — anything of the shape `LABEL: formula`
   (`"CASTING TOTAL: Communication + Corpse Magic + Aura modifier + stress die"`) or a stat run
   (`"Init +2, Attack +11, Damage +15"`). These go in typed fields or system sub-blocks
   (`FORMULAS`, `COMBAT`, `LEVEL_CALCULATION`), never inside a `DESCRIPTION` string.
2. **Enumerable lists** — specialties, virtues/flaws, attacks, spell parameters: one typed item
   per element whenever a field or sub-block exists for them.
3. **Whole stat blocks** — never serialize an entity's statistics into one string.

Structure is **not** required for flowing rules prose that mentions numeric values inline
("An Ease Factor of 9 will calm the upset, 12 will win someone's love…", "+5 damage every round
while the spell lasts") — that is the book's own voice and stays in `DESCRIPTION`.

**Completeness overrides structure.** RPG rules are pervasively "X always, except Y" — the
exceptions are rife and *desired*. When a datum resists a clean typed shape, keep the **full
as-authored text** (verbatim inside the structured field, or in prose) rather than trimming it to
fit: a formula's exception rider travels with it
(`"COMMANDING ROLL: Communication + Leadership + stress die; Leadership may be limited by Language
Ability"`), and a value like "3 (5 against fire)" stays whole. Whatever difficulty that poses for
functional implementations is not the `.ttrpg` file's concern — **completeness and correctness are
the only objectives**. Structure must never cause content loss.

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

### Templates vs. instances (DECISION-5)

- A **specific character who exists in the world** (a named NPC, a published persona) is an
  **instance**: `^"Name" DEF { EXTENDS ^"<actor type>" ... }`.
- A **reusable starting point players or GMs instantiate from** — pregens, archetype packages,
  modifier bundles — is a **`TEMPLATE`**: same DEF shape with the `TEMPLATE` marker, plus a
  `CHOICES` block holding its customization points (keep the source's customization notes there,
  verbatim, not in the description). Templates may `EXTENDS` other templates; sourcebooks refine
  base templates that way instead of restating them.

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

### Parameterized refs, aliases & choices (DECISION-6)

When a printed thing is a *family with a slot* rather than one fixed entity, or a *choice*, reach
for these instead of burying the meaning in a verbatim string (spec §5b):

- **Parameterize, don't enumerate.** A virtue like `Puissant Single Weapon` is `^"Puissant"` (a DEF
  that declares `PARAMETERS { ^"subject" OF ^"Ability" }`) bound at use: `^"Puissant"(^"Single
  Weapon")`. Don't mint 40 separate `Puissant X` DEFs, and don't leave it a dead string. The slot's
  domain is a caret type (must resolve) or `STRING` (free text like a place — `^"Area Lore"("Normandy")`).
  Don't parameterize what isn't actually variable.
- **Alias for setting renames, not for variants.** `ALIAS ^"Ride" FOR ^"Drive"` when a setting
  re-labels the *same* mechanic. It changes only the name — no value, no slot. If the value differs,
  it's a `MODIFY`/`OVERRIDE` (errata) or a new DEF, not an alias. Ship aliases in a `*-aliases-*`
  extension so base files stay pristine.
- **`CHOICE` for "A or B" and open allotments** — `CHOICE [ ^"Demonic Might", ^"Demonic Powers" ]`,
  or quantified slots `CHOICE [ 1 OF ^"Virtue" WHERE { ^"Size" "Major" }, … ]`. A verbatim-string
  option is the escape hatch when nothing structured fits — completeness still beats shape.
- **Rendering is the consumer's job.** Store the structured `(base, bindings)`; the display string
  (`Puissant Single Weapon`) is produced downstream, not written into the file.

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
- [ ] No content trimmed to fit a structure — exceptions and riders kept verbatim (completeness beats shape)
- [ ] Correct file type for the content
- [ ] `NAME` / `VERSION` / `SPEC_VERSION` / `RELEASE_DATE` present
- [ ] Hash IDs are opaque, `≥16` chars, unique — on everything referenced
- [ ] Every `^"Name"` / `#hash` / `EXTENDS` / `APPLIES TO` / `DEPENDS_ON` resolves
- [ ] One keyword-and-structure pattern per entity type
- [ ] Errata in overlay files, not comments
- [ ] Flavor prose in `.lore`, not `.ttrpg`
- [ ] Deliberate constraint/completeness deviations marked `FIAT "reason"` — and nothing else silenced
