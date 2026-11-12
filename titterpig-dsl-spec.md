# Titterpig DSL Specification v0.5

> **Status: v0.5 (current, canonical).** Supersedes v0.4 (which superseded v0.3); superseded
> versions live in this repo's git history. `AUTHORING-GUIDELINES.md` holds authoring
> best-practices for system-specific content. The
> `ttrpg.peg` grammar is **aligned to v0.5**. Validation is split: `ttrpg_validator.py` lints spec
> adherence, while `check_references.py` and `check_constructs.py` coherence-check the v0.5
> `REFERENCES`/`REFERENCED BY`, `HOOKS`, `OPTIONAL`/`.selections`, and `GUIDANCE` constructs.

## 0. What changed

The DSL is **at v0.5**, and a v0.6 working draft is in progress. This section lists the v0.6 changes
first, then the v0.5 additions, then the v0.4 changelog for history; the *Resolved decisions*
subsections below carry the full detail.

### v0.6 — working draft *(in progress, 2026-11)*

Changes made since v0.5, listed as they are decided. **Not all are additive.**

1. **`CHOOSE n` replaces `CHOICE`** *(§5b, DECISION-15; not additive)* — one construct for a choice,
   with the count always written: `CHOOSE 1 [ … ]`, `CHOOSE 3 OF ^"Type" WITH { … }`. `CHOICE`,
   `PICK` and `WHERE` are removed. `DISTINCT` (the default) and `INDISTINCT` say whether one option
   may be picked more than once.
2. **`BOOLEAN` takes an inline value** *(§8)* — `^"Starting" BOOLEAN true`, as `STRING` and `INTEGER`
   already did.
3. **`SET` and `TRANSFORM`** *(new, §8, DECISION-16)* — a change to a value says which kind it is:
   `#hash ^"Glory" SET 44` (becomes 44), `#hash ^"Command" TRANSFORM ADD 1` (goes up by 1). The
   methods are `ADD`, `SUBTRACT`, `MULTIPLY` and `DIVIDE`, with `ROUND`, `MIN` and `MAX`, and
   `TRANSFORM MANUAL "…"` for what they cannot express.
4. **`REF`** *(new, §8, DECISION-17)* — a property type that holds a reference to one entity:
   `^"Clan" REF #hash ^"Crab"`, declared on the type as `REF OF #hash ^"Clan"`.
5. **Dice are DEFs; `ROLL` and `NEXT`** *(new, §8, DECISION-18)* — a die is a DEF that `EXTENDS
   ^"Die"` and lists its `FACES`. The spec ships a dice module (`modules/0.6/`) that every edition
   includes. `ROLL n OF ^"die"` rolls dice, and `NEXT` before a statement makes it a step that
   follows the one above.

### v0.5 — five new constructs, and one rule tightened *(current)*

1. **`GUIDANCE`** *(new, §22, DECISION-8)* — first-class guidance prose (most **sidebars**): prose
   *about* the mechanics that is neither a deterministic `DESCRIPTION` rule nor opaque `.lore` flavor.
   A module-level `GUIDANCE { ENTRY ^"Name" #hash { CONCERNS [ … ] TEXT … } }` block lives beside what
   it `CONCERNS`; consumers get a "guidance available" signal. Generalized from the `.bridge` construct.
2. **`HOOKS` + `FORMALITY`** *(new, §23, DECISION-9)* — a stand-off `HOOKS` block surfacing that a
   narrative situation has a possible mechanical consequence, without being a rules engine. Each hook
   declares a `FORMALITY` on the ladder `PROSE → TAGGED → CONDITIONAL → FORMAL` (author uses the
   highest level the source supports and no higher; consumers dispatch on it).
3. **`OPTIONAL` + `.selections`** *(new, §24, DECISION-10)* — an `OPTIONAL` marker on a DEF/rule ships
   its default posture (`on`/`off`) and `SCOPE` in-corpus; user choices are recorded in a new
   **`.selections`** DSL file (`SELECT #hash on|off`) that round-trips through the same parser.
4. **`REFERENCES` / `REFERENCED BY`** *(renamed + extended, §5c, DECISION-11)* — v0.4's `MENTIONS` is
   renamed **`REFERENCES`** (`MENTIONS` kept as a deprecated alias). A target may be a mechanic's
   **parent** DEF and **SHOULD** carry the target's `#hash` (a hashless target **WARNs**), with an
   optional inverse **`REFERENCED BY`** mirror.
5. **`.codex`** *(new container, §25, DECISION-12)* — a **stand-off lore knowledge graph**: typed
   `ENTITY` nodes, a declared `RELATIONS` predicate vocabulary (with `INVERSE`/`DOMAIN`/`RANGE`/
   `SYMMETRIC`/`TRANSITIVE`), and a `CATEGORIES` taxonomy, all derived from `.lore` prose and stored
   beside it. The `.lore` body stays byte-verbatim and opaque; the codex points *into* it
   (`SOURCE … AT <heading-slug>`, `FROM "<surface>"`) and never edits it — the same "mirror, don't
   duplicate" split as `.ttrpg`↔`.lore`, applied to world facts.

**One rule tightened, not additive** *(§5d, DECISION-13)* — **a reference resolves by `#hash`; the
caret name is a readability aid.** v0.4 called `EXTENDS ^"Name"` "canonical and sufficient"; v0.5
withdraws that and applies DECISION-11's strict-hash rule to *every* reference site. A hashless
reference WARNs; a hashless reference whose name resolves to more than one distinct entity is an
**ERROR**. Existing files stay syntactically valid — nothing is removed from the grammar — but a
corpus with ambiguous by-name references will now fail its references gate, which is the point.

### v0.5 addendum — one entity, many printings *(2026-10-17, DECISION-14)*

Additive: every file valid before stays valid.

1. **`REPRINT ^"Name"`** *(new, §5b)* — a book that prints an entity whose text the target holds
   (unchanged, or in an older wording the target supersedes) says so with a pointer, not a second
   `DEF`. No new entity is created; the target must resolve, its text stands, and the book is recorded
   as one of the target's printings.
2. **`SET DESCRIPTION "…"`** *(new, §13)* — `MODIFY` may replace the target's whole `DESCRIPTION` with
   a variant printing's verbatim text, for a variant whose own wording should take effect.

`ALIAS` (§5b) remains the construct for the same entity printed under a **different name**.

### v0.4 — consistency/clarity pass over v0.3

v0.4 is a consistency/clarity pass over v0.3's grammar — not a redesign. Key changes:

1. **Structure over prose (new core principle).** Mechanically-critical data must be structured,
   never buried in opaque strings or comments (§1 → *Structural Representation*;
   `AUTHORING-GUIDELINES.md`).
2. **Canonical instance form** is `^"Name" DEF { PROPERTIES { ... } }`. Flat `key: value` /
   `METADATA`-style property forms seen in some sourcebook files are **non-canonical** and are
   migration targets.
3. **Hash IDs are opaque, `≥16` chars, carry no semantics** a tool relies on, and are **unique per
   entity within an edition** (§5, §14, §19). Short/prefixed IDs in the examples below are
   illustrative and predate this rule.
4. **Versioning:** each file declares its content `VERSION` and a `SPEC_VERSION` pinning the
   DSL-spec version it targets; systems organize by version directory (§3, §19).
5. **Errata is machine-readable** via `MODIFY`/`OVERRIDE`/`ADD` in dedicated `*-errata-*` EXTENSION
   files; **comments never carry data** (§4, §13).
6. **`.lore` is canonical** for free narrative prose (Markdown, no DSL); `.setting`/`.frame`/`.arc`/
   `.campaign` are *structured* narrative containers (DSL). §2 defines the boundary.
7. **Validation** is two levels — lint (spec adherence) + coherence/consilience (referential
   integrity); sophisticated rules evaluation is downstream, not part of the DSL (§20).
8. **`FIAT` — intentional exceptions** *(new)*: a required-reason marker that waives validation
   (constraint *and* completeness) for a value or, cascading, for an element and its whole subtree
   — the machine-readable way to assert a deliberate deviation (§8).
9. **`.bridge` — cross-edition conversion** *(new)*: a first-class container for an edition-conversion
   document. It is the only container with **two** dependency lineages (`ORIGIN` and `DESTINATION`)
   and the only one whose coherence is checked against **two** corpora (§21, §20).

### Resolved decisions (2026-07-12)

- **DECISION-1 — `APPLIES TO` disentanglement** *(resolved)* (§7): `APPLIES TO` is **scope only**;
  `EXTENDS` expresses type / `is-a` inheritance; categorization uses a distinct tag.
- **DECISION-2 — Definitions vs. instances** *(resolved)* (§5, §16): characters/NPCs are
  **instances** — a `DEF` that `EXTENDS` its actor type and fills in values via canonical
  `PROPERTIES` with inline typed values (`^"Air" INTEGER 4`). The old
  `DEF ^"Name" #id { TYPE "npc" … STATS { rings.air = 4 } }` form (reversed order, `=` assignment,
  dotted paths, `TYPE`-as-tag) is **deprecated**; no new grammar is added.
- **DECISION-3 — Intentional exceptions** *(resolved)* (§8): `FIAT "reason"` waives validation —
  constraints and completeness — at a single value or, cascading, an element and its subtree. The
  reason is **required**. Reserved for true exceptions; standard NPCs are defined against their own
  actor type and need no `FIAT`.
- **DECISION-4 — Composition, editions & precedence** *(resolved)* (§5, §13, §19): consumers load an
  **ordered composition set** from **one edition namespace**; later files override earlier ones by
  load-order precedence, **explicitly** (`OVERRIDE`/`MODIFY`/`ADD`) or **implicitly** (re-stating a
  hash). Hash identity is **edition-scoped** — stable within an edition, independent across editions
  (edition changes are breaking). Forward-porting a stranded sourcebook is an explicit **derived
  artifact**, not an automatic overlay.

### Resolved decisions (2026-07-14)

- **DECISION-5 — Templates are first-class** *(resolved)* (§5): a `TEMPLATE` is an **instantiable
  archetype** — not an entity in play — that downstream applications instantiate instances from,
  resolving its declared `CHOICES`. Templates `EXTENDS` an actor type (pre-generated characters) or
  **another template** (sourcebooks that refine base templates, e.g. Grogs); instances created from
  a template are instances of its underlying actor type. This models both full-statblock pregens
  (ArM5 Definitive grog/companion/magus templates) and modifier-bundle archetypes (L5R5e NPC
  templates) with one vocabulary, and enables quick, decisive instantiation by GMs at the table.
- **DECISION-6 — Parameterized references, aliases & choices** *(resolved)* (§5b): three ways a
  reference can carry more than a bare name. **Parameterized DEFs** declare typed slots
  (`PARAMETERS { ^"subject" OF ^"Ability" }`) that **bound references** fill
  (`^"Puissant"(^"Single Weapon")`, `^"Area Lore"("Normandy")`) — one base entity, a family of
  instances. **`ALIAS ^"Ride" FOR ^"Drive"`** makes one name a display synonym of an existing entity
  (a setting-level rename; same entity/hash, no value change). **A choice** is a structured
  "pick from these" value — specific entities, verbatim strings, or a number of entities of a type
  (written `CHOOSE n` since v0.6; DECISION-15 replaced the keyword this decision introduced). Motivated by ArM5's pervasive parameterized virtues
  (Puissant/Great/Affinity), "A or B" required virtues, and setting vocabulary re-skins. The bare
  `^"Name"` form is unchanged; these are additive.

### Resolved decisions (2026-07-26)

- **DECISION-7 — In-prose references via stand-off `MENTIONS`** *(resolved)* (§5c): an entry's rules
  text (a spell effect, a virtue's mechanics) is captured **verbatim** in its `DESCRIPTION`, and the
  mechanical terms inside that prose (`Light Wound`, `Improvement Ease Factor`, `recovery roll`) are
  linked to their DEFs by a **separate `MENTIONS` block** — stand-off annotation, never inline
  markup. Each entry pairs the **exact printed surface form** with its target caret ref
  (`"Improvement Ease Factor" -> ^"Improvement Ease Factor"`). Chosen over inline `[[…]]` markup
  because it keeps `DESCRIPTION` byte-for-byte verbatim (the project's hard rule and what the
  `doublecheck` verifier depends on), reuses existing caret-ref-list validation instead of adding
  string-embedded micro-syntax, and still buys back point-of-use precision — the surface form
  disambiguates two different targets in one paragraph (Improvement vs Stable Ease Factor) and lets a
  renderer locate each occurrence without mutating the text. Cross-rulebook page citations
  (`(ArM5, page 179)`) are **stripped** from the `DESCRIPTION` — the DEF reference supersedes them.

### Resolved decisions (2026-07-26, v0.5)

Five constructs recurring across systems that 0.4 could not cleanly hold. All additive — 0.4 files
stay valid.

- **DECISION-8 — Guidance is first-class, distinct from lore and from rules** *(resolved)* (§22): prose
  that is *about* the mechanics but is neither deterministic/structural (a `DESCRIPTION` rule) nor
  opaque flavor (`.lore`) — most **sidebars** — gets a `GUIDANCE` block (generalized from the BRIDGE
  construct, §21). It lives beside what it `CONCERNS`; consumers get a "guidance available" signal and
  present it contextually. `.lore` remains opaque-by-design (no consumer assumes structure in it), so
  guidance that tools must locate belongs in `.ttrpg`, not `.lore`.
- **DECISION-9 — Conditional emit hooks with a declared FORMALITY** *(resolved)* (§23): a stand-off
  `HOOKS` block makes *visible* that a narrative/roleplay situation has a possible mechanical
  consequence otherwise untracked (*"if the amulet is removed or damaged … a recovery roll"*). It is
  **not a rules engine**. Each `HOOK` declares a `FORMALITY` — `PROSE` → `TAGGED` → `CONDITIONAL` →
  `FORMAL` — the DSL's vocabulary for *how formal the encoding is*; an author uses the **highest level
  the source supports and no higher**, and consumers dispatch on the level.
- **DECISION-10 — Optional/variant rules carry a default posture; choices live in `.selections`**
  *(resolved)* (§24): an `OPTIONAL` marker on a DEF/rule ships its **default posture** (`on`/`off`) and
  **scope** (types/entities, or `GLOBAL`) in-corpus. User choices are recorded in a **`.selections`**
  DSL file (`SELECT #hash on|off`) that round-trips through the same parser/validator; consumers read
  corpus + selections to know the active rule set.
- **DECISION-11 — `MENTIONS` → `REFERENCES` (+ `REFERENCED BY`), parent targets, strict hash**
  *(resolved)* (§5c): the DECISION-7 construct is renamed **`REFERENCES`** (`MENTIONS` kept as a
  deprecated alias). A target may be a mechanic's **parent** DEF when the mechanic is not its own DEF
  (`"Light Wound" -> ^"Wounds"`) — the surface form carries the sub-component specificity, so no
  sub-component DEFs need be minted. A target **SHOULD carry the target's `#hash`**; a hashless target
  **WARNs** (many names are multiply-defined, and a later same-name entity must not silently re-point a
  link). An optional inverse **`REFERENCED BY`** block mirrors it (tool-derivable; when present each
  entry must correspond to a real `REFERENCES`).
- **DECISION-12 — Lore is queryable via a stand-off `.codex` graph, never by structuring the prose**
  *(resolved)* (§25): the queryable companion to `.lore` is a new **`.codex`** container — a knowledge
  graph of typed `ENTITY` nodes over a declared `RELATIONS` predicate vocabulary and a `CATEGORIES`
  taxonomy, derived from the narrative and stored beside it. Inline wiki-markup in the prose was
  rejected for the same reason as DECISION-7: it mutates verbatim narrative and forces every consumer
  to parse the body. The codex instead points *into* the prose (`SOURCE … AT <heading-slug>`,
  `FROM "<surface>"`), so `.lore` keeps its opaque-body contract (§2) and existing `.lore` files are
  untouched. Predicates are declared (an undeclared predicate is a coherence error) so the graph is
  robust rather than a synonym swamp; a category may be a taxonomy node **or** an existing game DEF, so
  lore types and mechanical types unify. This is `.setting`'s hand-authored canon's extraction-oriented
  sibling — the two coexist and cross-reference.

- **DECISION-13 — A reference resolves by `#hash`; the caret name is for humans**
  *(resolved, v0.5)* (§5d): DECISION-11 gave `REFERENCES` a strict-hash rule — *"a hashless target
  WARNs (many names are multiply-defined, and a later same-name entity must not silently re-point a
  link)"* — and stopped there. Every **other** by-name construct (`EXTENDS`, `APPLIES TO`, `LIST OF`,
  `CONCERNS`, `OVERRIDE`, `MODIFY`, `ALIAS … FOR`) kept resolving by name alone, and §6 went
  further and called the by-name form *canonical and sufficient*, recording a validator that demanded
  a hash as "a validator bug to fix". That was backwards: **the `#hash` is the functional referent and
  the `^"Name"` is a readability aid**, which is the whole reason hash IDs exist (§5, §12). The hazard
  DECISION-11 named is not specific to prose references — it is a property of resolving by name. It
  bites hardest in inheritance, where a collision is not confined to the colliding entity: in
  `titterpig-dsl-tor2e` the type `^"Shield"` and one of the three printed shields share a name, so
  **`^"Buckler"` and `^"Great Shield"` — unambiguous by name and by hash — are reported as circular**
  because the name they point at is not. v0.5 therefore applies one rule to every reference site (§5d):
  resolution is **by hash when present**; a hashless reference **WARNs**; and a hashless reference whose
  name resolves to **more than one distinct entity is an ERROR**, because no rule can choose for it.
  §6's "canonical and sufficient" language and its "validator bug" note are **withdrawn**.

- **DECISION-14 — One entity, many printings: `REPRINT`, `ALIAS`, and `MODIFY … SET DESCRIPTION`**
  *(resolved, v0.5 addendum, 2026-10-17)* (§5b, §13): sourcebooks routinely reprint an entity another
  book already defines — a Virtue from a supplement folded into a later core, or one book's Flaw
  reprinted in another. Converted as a second `DEF`, the reprint becomes a second entity: consumers
  list it twice, and a conversion that must keep names unique invents labels like
  `"Finding Hidden Loot (Between Sand & Sea)"` that no book prints. The decision is that a printing
  which adds nothing is a **pointer**, chosen by what should show: the **target's** text — because the
  printing is unchanged, or because the target supersedes it (a definitive edition over an older
  supplement's wording) → `REPRINT ^"Name"`; **only the name** differs → `ALIAS ^"New" FOR
  ^"Existing"`; the **printing's own** wording should take effect → `MODIFY ^"Existing" { SET
  DESCRIPTION "…" }`, which carries the variant text verbatim. A `MODIFY` always applies on top of the
  entity it modifies, so it is the wrong pointer when the target's text is the authoritative one. An
  empty `MODIFY` was rejected as the reprint marker: it reads as an unfinished patch, and says nothing
  about the book printing the entity.

### Resolved decisions (2026-11-11, v0.6 working draft)

- **DECISION-15 — `CHOOSE n` replaces `CHOICE`** *(resolved, v0.6)* (§5b): DECISION-6 gave a choice
  the form `CHOICE [ … ]`, with `PICK n` for a count other than one and `n OF ^"Type" WHERE { … }` for
  an open allotment. Three corpora adopted it (root, TEETH, arm5e: 360 statements). l5r5e had already
  written 308 choices as `CHOOSE n [ … ]`, and the synthesist reads that form and has no handling for
  the other. The decision is to keep one: **`CHOOSE n`**, with the count always written. `CHOICE` and
  `PICK` are removed, with no deprecated alias: `CHOICE` is a warning in a file that declares a
  `SPEC_VERSION` below 0.6 and an error in one that declares 0.6 or later. A choice from a type is `CHOOSE n OF ^"Type"`. What
  must be true of each entity chosen is stated by **`WITH { … }`**, which replaces `WHERE`: each term
  is a property and one value in brackets (a comma is not an implicit "or"), terms are joined by
  `AND` or `OR`, and `NOT` negates one. A condition nested inside another is **not yet defined (to-do)**. `DISTINCT` and `INDISTINCT`
  say whether one option may be picked more than once; with neither word a choice is `DISTINCT`. An
  option that names an entity is a reference site and carries the entity's `#hash` (§5d). This is the
  first change since v0.4 that is not additive: a v0.5 file that uses `CHOICE` is not a valid v0.6
  file.

- **DECISION-16 — A change to a value says what kind of change it is: `SET` and `TRANSFORM`**
  *(resolved, v0.6)* (§8): corpora wrote "the value becomes 44" and "add 1 to the value" the same
  way, as a bare `INTEGER`, and told them apart by the name of the property they sat under
  (`^"Glory" INTEGER 44` beside `^"Skill Increases" DEF { ^"Command" INTEGER 1 }`). Elsewhere a change
  was a signed number in a string (`MODIFIERS { ^"Glory" "+3" }`). The decision is two primitives.
  `<target> SET <amount>` makes the value the amount. `<target> TRANSFORM <METHOD> <amount>` changes
  it, by one of a closed set of methods: `ADD`, `SUBTRACT`, `MULTIPLY`, `DIVIDE`. A `TRANSFORM` may
  be followed by `ROUND UP|DOWN|NEAREST`, `MIN n` and `MAX n`. The amount is an integer or a
  reference to another value. `TRANSFORM MANUAL "…"` carries, in the source's words, a change the
  methods cannot express; it is the escape §21 already uses. The target is a reference to the thing
  changed, so it is a reference site (§5d), or it is a `CHOOSE`. **Flagged for review:** `SET` is
  also a directive inside `MODIFY` (§13), written before its target, where it patches a definition
  when files are composed. The two uses are told apart by position.

- **DECISION-17 — A property that names one entity holds a reference: `REF`** *(resolved, v0.6)*
  (§8): the type table had `LIST OF ^"Type"` for many entities and nothing for one, so corpora and
  this spec's own examples wrote the entity's name in a string (`^"Clan" STRING "Crab"`), which no
  gate checks. `REF` is the property type for one entity: `REF OF ^"Type"` declares it, taking the
  type's name as the property's name unless one is written, and `^"Name" REF ^"Entity"` gives its
  value. Both are reference sites, and the entity must be of the declared type.

- **DECISION-18 — Dice are DEFs, a roll is `ROLL n OF`, and `NEXT` orders steps** *(resolved, v0.6)*
  (§8): 3,251 property values across 13 corpora held a dice expression in a string (`"4d8 + 8"`,
  `"2D6+4"`, `"1d6+2 phy"`, `"50 (3D6 ×5)"`). A dice literal was considered and rejected: it covered
  the simple shapes and left out multipliers, sums of dice, bonuses and damage types. The decision
  is that **a die is an entity**: a DEF that `EXTENDS ^"Die"` and lists its faces in a `FACES` block,
  each face with a weight of 1 unless it says otherwise. l5r5e already wrote its Ring Die and Skill
  Die this way. Variant dice and uneven odds are then new DEFs and need no new grammar. The spec
  ships a **dice module** defining `^"Die"` and d2, d3, d4, d6, d8, d10, d20 and d100; every edition
  includes it, it is edition-neutral, and a system's BASE may `DEPENDS_ON` it. `ROLL n OF ^"die"`
  rolls dice, and the existing `SET`, `TRANSFORM` and `REF` do the rest: the modifier, where the sum
  is stored, the damage type. That needs order, which the DSL did not have, so **`NEXT`** before a
  statement makes it a step that follows the statement above. `NEXT` was chosen over `THEN`, which
  already means the consequence of a `WHEN` in rules and hooks. A chain runs forward only: this is
  not a rules engine, and there is no branch and no loop.

## 1. Overview & Design Principles

Titterpig is a domain-specific language (DSL) for defining tabletop role-playing game (TTRPG) systems, content, and narrative structures. The base specification defines a **system-agnostic syntax toolkit** — it owns the grammar, while each game system owns its vocabulary.

### Design Principles

1. **Readable**: Files should read like game rules documentation
2. **Declarative**: Describe what exists, not how to compute it
3. **Composable**: Definitions can be layered, extended, and combined across files
4. **Type-safe**: Properties carry type information and constraints
5. **System-agnostic**: The same grammar supports L5R, VTM, Ars Magica, and any other TTRPG — without changes to the base spec
6. **Structured, not prose** *(v0.4)*: Mechanically-critical data is represented as structured DEFs/properties, never buried in opaque strings or comments (see *Structural Representation* below)

### What the Base Spec Owns

- File-level wrappers (`BASE`, `EXTENSION`)
- Definition blocks (`DEF`, `ACTOR`)
- Typed properties and constraints
- Inheritance (`EXTENDS`) and scope (`APPLIES TO`)
- Cross-referencing (caret references `^"Name"`, hash IDs `#id`)
- Rule containers (`RULES`)
- Modification primitives (`OVERRIDE`, `ADD`, `MODIFY`)
- Narrative containers (`SETTING`, `FRAME`, `ARC`, `CAMPAIGN`)

### What Systems Own

Everything else. Keywords like `CURRICULUM`, `SCHOOL_ABILITY`, `POWERS`, `AMALGAMS`, `CHARACTERISTICS`, `DISCIPLINE`, `PREDATOR_TEMPLATES` — these are vocabulary defined by each system's `.ttrpg` files, not reserved by the base spec.

### Structural Representation *(v0.4)*

The base spec is permissive: the grammar accepts almost any well-formed block. That flexibility must **not** be used to bury data in prose. **Mechanically-critical data — anything a tool will read (bonuses, costs, dice, ranks, stats, prerequisites) — must be represented structurally, not packed into free-text strings or comments.**

```
# Avoid — everything in one string:
#h9k7mQ2vX7wZ9tB4cD1a ^"Hida" DEF {
    EXTENDS #p4Tz8LwQ1nRv6YbK3xGs ^"Family"
    DESCRIPTION """
        Ring Increase: +1 Earth or +1 Fire
        Skill Increases: +1 Command, +1 Tactics
        Glory: 44
        Starting Wealth: 4 koku
    """
}

# Avoid — the fields named, the values still packed in strings:
#h9k7mQ2vX7wZ9tB4cD1a ^"Hida" DEF {
    EXTENDS #p4Tz8LwQ1nRv6YbK3xGs ^"Family"
    PROPERTIES {
        ^"Ring Increase"   STRING "+1 Earth or +1 Fire"
        ^"Skill Increases" STRING "+1 Command, +1 Tactics"
        ^"Glory"           INTEGER 44
        ^"Wealth"          STRING "4 koku"
    }
}

# Prefer — structured, machine-readable:
#h9k7mQ2vX7wZ9tB4cD1a ^"Hida" DEF {
    EXTENDS #p4Tz8LwQ1nRv6YbK3xGs ^"Family"
    APPLIES TO [#c2Hn7VdM9sXq5JrW8eLf ^"Samurai"]

    PROPERTIES {
        ^"Family Name" STRING "Hida" FIXED
        ^"Clan"        REF #w6Jc1ZpR4mXe9LtV3bKn ^"Crab"
        ^"Ring Increase" DEF {
            CHOOSE 1 [#k3nP8mQ2vX7wZ9tB4cD1 ^"Earth", #r7Yt2LmW9qKc4VbN6xHs ^"Fire"] TRANSFORM ADD 1
        }
        ^"Skill Increases" DEF {
            #d8Sg5QhT2yNk7McA4vPr ^"Command" TRANSFORM ADD 1
            #f1Bn6WxE3zHj9RdL5sUo ^"Tactics" TRANSFORM ADD 1
        }
        #m2Vq7KcY4tGf8NwJ6pXa ^"Glory" SET 44
        ^"Wealth" DEF { ^"Count" INTEGER 4  ^"Type" STRING "koku"  ^"Starting" BOOLEAN true }
    }
}
```

The *shapes* of these structures are system-owned (there is no universal cross-system type layer); the *discipline* of structuring over prose is universal. Genuine narrative flavor stays prose and belongs in `.lore`. See `AUTHORING-GUIDELINES.md`.

---

## 2. File Types

The DSL uses multiple file extensions, each corresponding to a specific container type:

| Extension | Container(s) | Purpose |
|-----------|-------------|---------|
| `.ttrpg` | BASE, EXTENSION | Game system mechanics and rules (DSL) |
| `.setting` | SETTING | *Structured* system-agnostic world-building (DSL) |
| `.frame` | FRAME | Campaign scaffolding — setting + light mechanics (DSL) |
| `.arc` | ARC | Complete playable narrative adventures (DSL) |
| `.campaign` | CAMPAIGN | Long-form multi-arc story collections (DSL) |
| `.actor` | (single DEF) | A single character — PC or NPC — as a discrete file (DSL) |
| `.bridge` | BRIDGE | **Cross-edition conversion** — a directed correspondence between two editions (DSL) *(v0.4, §21)* |
| `.lore` | (none — Markdown) | **Free narrative prose / flavor** — no DSL syntax *(v0.4)* |
| `.codex` | CODEX | **Stand-off lore knowledge graph** — typed entities + declared relationships over `.lore` prose (DSL) *(v0.5, §25)* |
| `.selections` | SELECTIONS | **User's optional-rule choices** for a corpus — `SELECT #hash on\|off` (DSL) *(v0.5, §24)* |

The `.actor` extension is a convenience alias: an `.actor` file is a `.ttrpg` file scoped to exactly one character definition (a single `DEF` block). It uses identical syntax to a DEF within an EXTENSION but exists as a standalone file, making it easy to share, version, or reference individual characters independently of the containers they appear in.

### Structured Narrative vs. Free Prose (`.setting`/`.frame` vs `.lore`) *(v0.4)*

Narrative content splits by whether tools need to *query* it:

- **Structured narrative → `.setting`, `.frame`, `.arc`, `.campaign`** (DSL syntax). Use these when the content has addressable, cross-referenced parts a tool consumes — locations, factions, NPC stat blocks, scenes, hooks, timelines. These carry hash IDs and caret references.
- **Free prose → `.lore`** (Markdown, no DSL). Use this for readable flavor and world description meant for humans — history essays, cultural color, fiction. A `.lore` file is **not** parsed as DSL.

Rule of thumb: if a tool must look something up in it, it's `.setting`/`.frame`; if it's just meant to be read, it's `.lore`. The same subject may appear in both (a mechanical `.setting`/`.ttrpg` entry plus a `.lore` essay).

When a tool must query the *facts inside* a `.lore` essay — who a person is, where a place sits, how factions relate — the answer is **not** to structure the prose but to build a **stand-off `.codex` knowledge graph** beside it (§25). The `.lore` body stays byte-verbatim and opaque; the codex holds the typed entities and relationships and points *into* the prose. This keeps the query test intact: the prose is still "just meant to be read," and the structured, queryable layer is a separate file.

### File Organization

Files are organized as:
- `systems/{system_id}/core.ttrpg` — Base system definitions
- `extensions/{system_id}/{extension_id}.ttrpg` — Extensions, errata, sourcebooks, house rules
- `settings/{setting_id}.setting` — World-building and lore
- `frames/{system_id}/{frame_id}.frame` — Campaign scaffolds
- `arcs/{system_id}/{arc_id}.arc` — Playable adventures
- `campaigns/{system_id}/{campaign_id}.campaign` — Multi-arc campaigns
- `actors/{character_id}.actor` — Individual character definitions (PC or NPC)
- `bridges/{origin}-to-{destination}-{doc}.bridge` — Cross-edition conversions (§21), in the canonical repo or beside a system's corpus; never inside either edition's corpus

---

## 3. File-Level Structure

Every `.ttrpg` file opens with either a `BASE` or `EXTENSION` declaration. These are the only two file-level wrappers.

### BASE — Standalone Module

A BASE defines a self-contained ruleset module. It has no parent, with one exception: it may declare `DEPENDS_ON "Titterpig_Dice"`, the dice module the spec ships (§8).

```
BASE "FileID" {
    NAME "Human-readable Name"
    VERSION "0.1"
    SPEC_VERSION "0.4"
    RELEASE_DATE "YYYY-MM-DD"

    # ... definitions ...
}
```

### EXTENSION — Dependent Module

An EXTENSION modifies or adds to a parent module. Two forms exist:

**With EXTENDS (names the parent inline):**
```
EXTENSION "FileID" EXTENDS "ParentFileID" {
    NAME "Extension Name"
    VERSION "0.1"
    RELEASE_DATE "YYYY-MM-DD"

    # ... modifications and additions ...
}
```

**With DEPENDS_ON (versioned dependency in the body):**
```
EXTENSION "FileID" {
    NAME "Extension Name"
    VERSION "0.1"
    RELEASE_DATE "YYYY-MM-DD"
    DEPENDS_ON "ParentFileID" VERSION "0.1"

    # ... modifications and additions ...
}
```

Both forms declare a parent. `EXTENDS` is concise; `DEPENDS_ON` allows specifying a required parent version.

**Fields:**
- `FileID`: Unique identifier (e.g., `"L5R5e_Core_Core"`, `"VTM5e_Companion_Errata"`)
- `NAME`: Full display name
- `VERSION`: Content version of this file (semantic or date-based)
- `SPEC_VERSION` *(v0.4)*: The DSL-spec version this file targets (e.g., `"0.4"`). Distinct from `VERSION`; lets tooling detect spec conformance.
- `RELEASE_DATE`: ISO date format

**Errata files:** corrections live in dedicated `*-errata-*` EXTENSION files as machine-readable `MODIFY`/`OVERRIDE`/`ADD` (see §13), never as comments in source files.

---

## 4. Comments

```
# This is a comment (hash + space)
// This is also a comment (double slash)
# ============= Section separator =============
```

**Rule:** `#` followed by a space or end-of-line is a comment. `#` followed by an alphanumeric character is a hash ID (not a comment). This distinction is unambiguous:

```
# This is a comment
#L5R001abc   ← this is a hash ID
```

Comments are for human annotation only — mechanical notes, page references, source attributions, and TODO markers.

**Rule (v0.4): comments MUST NOT carry data a tool needs.** Anything a parser or downstream tool must read — corrections, values, stats, cross-references — belongs in structured DSL, not a comment. Corrections in particular go in machine-readable errata files (§13), never as `# … should read …` notes. A comment must be safe to strip without losing meaning.

---

## 5. Definitions (DEF)

The `DEF` block is the core building block. Every named game concept — a school, a technique, a clan, a ring, a discipline power — is a DEF.

### Named Definition (most common)

```
^"Name" DEF {
    # body
}
```

### Anchored Definition (with hash ID)

```
#hashID ^"Name" DEF {
    # body
}
```

### ACTOR Definition (character type)

```
#hashID ACTOR "Name" DEF {
    # body
}
```

`ACTOR` is an optional semantic marker indicating this DEF declares a character **type** (the schema a PC or NPC conforms to). It has no syntactic effect — it's documentation for humans and tooling. ACTOR DEFs typically have PROPERTIES and RULES blocks defining the character schema.

### TEMPLATE Definition (instantiable archetype) *(v0.4, DECISION-5)*

```
#hashID TEMPLATE "Name" DEF {
    EXTENDS ^"Grog"                # an actor type, or another TEMPLATE
    PROPERTIES { ... }             # the concrete values the template fixes
    CHOICES {                      # declared open slots / customization options
        "Swap Large for an Affinity or Puissant Ability with Great Weapons."
    }
    DESCRIPTION "..."
}
```

`TEMPLATE` is a semantic marker (like `ACTOR`, no syntactic effect) declaring an **instantiable
archetype**: a pre-generated character, an NPC bundle, or any reusable starting point a downstream
application **instantiates** instances from. Semantics:

- A template is **not an entity in play**. Consumers create instances from it: copy its concrete
  values, resolve its `CHOICES`, and the result is an instance of the template's underlying actor
  type.
- A template `EXTENDS` either an **actor type** (a full pregen) or **another template** — child
  values override inherited ones per normal inheritance (§6), which is how sourcebooks refine base
  templates without restating them.
- **`CHOICES`** declares the customization points the template leaves open. Entries may be faithful
  prose (a source's "Customization Notes") or structured per-system shapes; either way they live
  here, not buried in the description, so tooling can present them at instantiation time.
- Relation to §13: `MODIFY`/`OVERRIDE`/`ADD` remain **load-order composition** against defined
  entities (errata may patch a template like anything else). Template instantiation is
  **consumer-time** and orthogonal.

### §5b — Parameterized references, aliases & choices *(v0.4, DECISION-6)*

Three additive constructs let a reference carry more than a bare name. The plain `^"Name"` form is
unchanged and remains the common case.

#### Parameterized definitions and bound references

A DEF may declare **parameters** — named, typed slots that a reference binds at the point of use.
This models the pervasive "one base virtue, many specializations" pattern (`Puissant Single
Weapon`, `Great Stamina`, `Affinity with Ignem`, `Area Lore` → `Normandy Lore`):

```
#hash ^"Puissant" DEF {
    EXTENDS ^"Virtue"
    PARAMETERS { ^"subject" OF ^"Ability" }     # one slot, ranges over Ability entities
    PROPERTIES { ^"Size" STRING "Minor" FIXED }
    DESCRIPTION "Add 2 to rolls using the chosen Ability."
}

#hash ^"Area Lore" DEF {
    EXTENDS ^"Ability"
    PARAMETERS { ^"area" OF STRING }             # free-text slot (no Land entities exist)
}
```

- A parameter's **domain** is a caret type (`OF ^"Ability"` — the bound value must resolve to an
  entity of that type), `OF STRING` (any free text), or `OF ["A", "B", …]` (an **enum** of literal
  allowed values). The enum form selects among fixed alternatives — e.g. a virtue the book lets you
  take at either severity declares `PARAMETERS { ^"Size" OF ["Major", "Minor"] }`, and a reference
  binds the choice: `^"Wrathful"("Major")`. Naming the parameter after the property it fills
  (`^"Size"`) tells consumers to apply the bound value there; the `OF [...]` bounds the legal values
  so an invalid binding (`^"Wrathful"("Huge")`) is a coherence error. A DEF may declare several
  parameters (a Story flaw might take `^"Size" OF ["Major","Minor"]` and `^"goal" OF STRING`).
- A **bound reference** appends a parenthesized argument list to a caret ref, wherever a caret ref
  is legal (list items, values, `EXTENDS` targets):

  ```
  ^"Puissant"(^"Single Weapon")     ^"Great"(^"Stamina")     ^"Area Lore"("Normandy")
  ```

  Arguments bind **positionally**, or by name for clarity (`^"Puissant"(^"subject" = ^"Single
  Weapon")`). A caret argument must resolve to an entity of the declared type; a string argument
  fills a `STRING` slot.
- **Rendering is the consumer's job.** The DSL stores the structured (base, bindings) form; the
  derived display name (`Puissant Single Weapon`) is produced by downstream applications, not
  encoded in the file. A bound reference whose base declares no `PARAMETERS`, or whose argument
  count or types don't match, is a coherence error.

#### Aliases — setting/edition renames

`ALIAS` declares one name a **display synonym** of an existing entity — the same entity (same hash,
same rules), a different label, and **no** change of value:

```
ALIAS ^"Ride" FOR ^"Drive"
```

References to `^"Ride"` resolve to the `Drive` entity but display as `Ride`. An alias is distinct
from `MODIFY`/`OVERRIDE` (which patch an entity) and from a new DEF (a different entity); it adds
nothing and changes nothing. Aliases are edition-scoped, so a setting ships an `*-aliases-*`
extension file to re-skin vocabulary without touching base definitions (a VtM 1200s campaign
renaming `Drive` to `Ride`). The `FOR` target must resolve; alias chains must be acyclic; an alias
name must not already name a *different* entity. An alias may target a bound reference.

#### Reprints — the same entity printed again *(v0.5 addendum, DECISION-14)*

`REPRINT` records that this file's book prints an existing entity whose text the **target** holds —
unchanged, or in an older wording the target supersedes (a definitive edition over a supplement):

```
REPRINT #tZhJv5oWt4DoTU8mwaNHNmPz ^"Folk Magic"
```

It declares **no** new entity and mints no anchor: references to the name resolve to the original,
and consumers list the entity once, noting this book among its printings; the target's text stands.
The target must resolve and **SHOULD** carry its `#hash` (§5d). A file must not both `REPRINT` and
`DEF` the same entity, and an entity the file itself defines cannot be its own reprint. When the
reprint's **name** differs, use `ALIAS` instead; when the reprint's **own wording** should take effect,
use `MODIFY … SET DESCRIPTION` (§13).

#### Choices — `CHOOSE n` *(v0.6, DECISION-15)*

`CHOOSE` says that a number of things are picked, and from what. The count is always written.

```
CHOOSE 1 [ #hash ^"Demonic Might", #hash ^"Demonic Powers" ]    # one of these two entities
CHOOSE 5 [ #hash ^"Fitness", #hash ^"Command", … ]               # five of those listed
CHOOSE 1 [ "Charm", "Cunning", "Finesse", "Luck", "Might" ]     # options may be strings
CHOOSE 2 OF #hash ^"Roguish Feat"                                 # any two entities of a type
CHOOSE 3 OF #hash ^"Virtue" WITH { ^"Size" ["Minor"] AND ^"Category" ["Supernatural"] }
```

**From a list.** `CHOOSE n [ … ]` picks `n` of the options listed. An option is one of:

- an entity reference, which may be a bound reference;
- a verbatim string, for an option the corpus has no entity for (completeness wins over shape);
- another `CHOOSE`.

**From a type.** `CHOOSE n OF ^"Type"` picks `n` entities of that type: every DEF that `EXTENDS` it,
directly or through a chain.

**`WITH` — what must be true of each entity chosen.** A `WITH { … }` may follow `CHOOSE n OF
^"Type"`. Each term is a property of the type and one value in brackets. A term holds when the
entity's property has that value. Terms are joined by `AND` or by `OR`, and `NOT` before a term
negates it:

```
WITH { ^"Size" ["Minor"] }
WITH { ^"Size" ["Minor"] AND ^"Category" ["Supernatural"] }
WITH { ^"Size" ["Major"] OR ^"Size" ["Minor"] }
WITH { ^"Category" ["Supernatural"] AND NOT ^"Size" ["Free"] }
```

A value is a string, an integer, `true` / `false`, or an entity reference. A term takes exactly one
value: a comma is not an implicit "or", and `^"Size" ["Major", "Minor"]` is an error. One `WITH`
joins its terms with `AND` throughout or with `OR` throughout.

> **To-do — nested conditions.** A condition inside another (`A AND (B OR C)`) is not yet defined, so
> a `WITH` that mixes `AND` and `OR` is an error until it is.

**`DISTINCT` and `INDISTINCT`.** `CHOOSE DISTINCT n …` picks `n` different options. `CHOOSE
INDISTINCT n …` lets one option be picked more than once. With neither word the choice is `DISTINCT`.

**One or the other.** A list option may itself be a `CHOOSE`, for "one Major Virtue, or three Minor
ones":

```
CHOOSE 1 [
    CHOOSE 1 OF #hash ^"Virtue" WITH { ^"Size" ["Major"] AND ^"Category" ["Supernatural"] },
    CHOOSE 3 OF #hash ^"Virtue" WITH { ^"Size" ["Minor"] AND ^"Category" ["Supernatural"] }
]
```

**Where a `CHOOSE` may stand.**

- As a property's value: `^"Background" CHOOSE 1 [ … ]`.
- As an item in a list, beside fixed items: `[ #hash ^"Second Sight", CHOOSE 1 [ … ] ]`.
- After a system keyword, in a template's `CHOICES` block, or alone in a block:
  `KATA CHOOSE 1 [ … ]`.
- In place of a name or a target. Where a block gives each named thing a value or a change (§8), a
  `CHOOSE` may stand where the name would, and what follows applies to each option chosen:
  `^"Ring Increase" DEF { CHOOSE 1 [ #hash ^"Earth", #hash ^"Fire" ] TRANSFORM ADD 1 }`.

**References.** An entity option and the type after `OF` are reference sites (§5d): each resolves,
and each SHOULD carry the entity's `#hash`.

**Coherence.**

- The count is a positive integer. In a `DISTINCT` choice from a list it must not exceed the number
  of options.
- Every entity option and every `OF` type resolves. String options are unchecked.
- Every property named in a `WITH` is a property of the type, its own or inherited.
- A `WITH` term has exactly one value, and a `WITH` does not mix `AND` and `OR`.

**`CHOICE` in an older file.** A file that declares a `SPEC_VERSION` below 0.6, or none, and still
writes `CHOICE` raises a **warning**; its options are still resolved. A file that declares
`SPEC_VERSION "0.6"` or later and writes `CHOICE` raises an **error**.

### §5c — In-prose references: the `REFERENCES` block *(v0.4 as `MENTIONS`; v0.5, DECISION-11)*

**v0.5 changes (DECISION-11).** The block is renamed **`REFERENCES`** (`MENTIONS` remains a deprecated
alias, still accepted so 0.4 corpora keep validating). Three additions:
1. **Hash-qualified targets, strict.** A target may be written `#hash ^"Name"` and — per the strict
   rule — SHOULD be; a **hashless target WARNs** (a name may resolve to several DEFs, and a later
   same-name entity must not silently re-point the link). Resolution is by hash when present (the hash
   must be a declared anchor whose name matches the caret).
2. **Mechanical-parent targets.** When a referenced mechanic is not its own DEF, target its owning
   **parent** DEF (`"Light Wound" -> ^"Wounds"`); the surface form carries the sub-component
   specificity, so sub-component DEFs need not be minted.
3. **Optional inverse mirror `REFERENCED BY`.** `REFERENCED BY { "surface" <- #hash ^"Referrer" }` on
   the target records what references it — tool-derivable, and gated for consistency against the
   forward `REFERENCES`; its absence is never an error.
4. **`EMPHASIS` — a marked span with no referent.** `EMPHASIS { "surface form" }`. DECISION-7 settled
   that a span the source sets apart is recorded *beside* the verbatim text and never as markup
   inside it; `REFERENCES` covers the case where the span names another DEF, and this covers the case
   where it names nothing. No target, so no hash, no resolution and no inverse mirror — the only
   coherence rule is the one `REFERENCES` already has: **the surface form must appear in the DEF's
   own prose.** An `@n` occurrence index is accepted on the same terms.

   Root sets a move this way, every move, in all three books:

   ```
   #tOf8uzMsrgh5Gd67BS7ge8AJ ^"Travel Through the Forest" DEF {
       TRIGGER "When you travel from clearing to clearing through the forest, the band
                collectively decides how it travels and one member of the band rolls for the group:"
       EMPHASIS { "travel from clearing to clearing through the forest" }
   }
   ```

   The book prints the triggering fiction in the body serif's bold and the instruction that follows
   it in the roman. That is not decoration: it is where the fiction ends and the mechanics begin,
   drawn by the typesetter, and a text channel cannot see it. Written as `**bold**` inside the
   `TRIGGER` it would change the string the verbatim check compares against the page; written here it
   changes nothing and a renderer can still set the move the way the book sets it.

   **Use it for what the source marks, not for what an author wants stressed.** An `EMPHASIS` is a
   claim about the page, and like every other such claim it should be derived from the source rather
   than decided — Root's 234 are read out of the PDF's font runs, not typed.

The rest of this section (byte-verbatim `DESCRIPTION`, exact-surface-form rules, page-cite stripping)
is unchanged — read `MENTIONS` below as `REFERENCES`.

An entry's rules text **is** the entry — a spell's effect, a virtue's mechanics — so it is captured
**verbatim** in `DESCRIPTION`, not dropped to prose or a `.lore` file. But that prose names other
DEFs: *"the target heals a Light Wound … if the roll exceeds the Improvement Ease Factor."* Those
names are made machine-resolvable by a **stand-off `MENTIONS` block**, not by editing the text.

```
#hashID ^"Close the Flesh" DEF {
    EXTENDS ^"Rune Spell"
    PROPERTIES { ^"Rune" STRING "Berkanan" FIXED  ^"Level" INTEGER 20 … }
    DESCRIPTION "This spell is usually carved onto an amulet … The target heals a Light
      Wound, and as long as the runes last … the character must make an immediate recovery roll
      for that injury. If this equals or exceeds the Improvement Ease Factor, then the wound
      remains healed. If the roll equals or exceeds the Stable Ease Factor, then the Light Wound
      re-opens …"
    MENTIONS {
        "Light Wound"             -> ^"Light Wound"
        "recovery roll"           -> ^"Recovery Roll"
        "Improvement Ease Factor" -> ^"Improvement Ease Factor"
        "Stable Ease Factor"      -> ^"Stable Ease Factor"
    }
}
```

Rules:

- **`DESCRIPTION` stays byte-for-byte verbatim.** The only transforms allowed are the standard
  whitespace/HTML-escape normalisation **and** stripping a cross-rulebook page citation
  (`(ArM5, page 179)`, `(see ArM5 p. 42)`) — the `MENTIONS`/`EXTENDS` reference supersedes the
  citation, which would otherwise be a dead pointer once the entity has a DEF. Nothing else is
  added, removed, or reworded. No inline markup is ever inserted into the text.
- **Each `MENTIONS` entry is `"<surface form>" -> <caret ref>`.** The surface form is the term
  **exactly as printed in this `DESCRIPTION`** (including case and inflection — `"recovery roll"`,
  not `"Recovery Roll"`). This is what lets a renderer locate and link the occurrence, and lets two
  different targets in one paragraph (Improvement vs Stable Ease Factor) each resolve correctly.
- **Coherence checks:** every caret ref target must resolve in the corpus (same as any reference);
  and every surface form **must appear as a substring of the `DESCRIPTION`** — a `MENTIONS` entry
  whose surface string is absent is drift and fails validation. A term may be mentioned once even if
  it recurs; add a `@<n>` occurrence index (`"Light Wound"@2 -> …`) only when different occurrences
  of the *same* surface string must point to *different* targets, which is rare.
- **Optional and additive.** A DEF with no external references simply omits `MENTIONS`. Existing
  files are unaffected until re-treated.

Rationale and the rejected alternative are in DECISION-7. In short: inline `[[…]]` markup was
rejected because it mutates the verbatim rules text (breaking the hard verbatim rule and the
`doublecheck` verifier) and adds string-embedded micro-syntax to the grammar; stand-off annotation
keeps the text pure and reuses existing caret-ref validation while preserving point-of-use precision.

### Hash IDs *(v0.4 rules)*

Hash IDs are optional cross-reference anchors on any DEF or rule. When present:

- **Opaque:** the ID carries no semantics a tool relies on. Do **not** encode system, category, or sequence meaning that code parses out of the ID — that information lives in fields.
- **Unique per entity, within an edition/version namespace.** A hash names one entity; its
  *canonical* definition appears once. **Recurrence of the same hash across files within an edition is
  legal** — a later-loaded file (a sourcebook, an errata overlay) re-stating a hash **replaces or
  amends** that entity by load-order precedence (the override mechanism, §13), not a collision.
  **Across editions the namespace resets:** the "same" entity in a different edition is a **separate
  definition with a different hash** (edition changes may be breaking — §19). Two *different* entities
  must never share a hash.
- **Format:** `#` followed by `≥16` alphanumeric characters (`[A-Za-z0-9]{16,}`).
- A short, non-semantic readability prefix is *tolerated* (e.g. `#L5R…`) but must not be depended on.

```
#L5Rk3nP8mQ2vX7wZ9tB4cD1    ← opaque, ≥16 chars, unique per entity within its edition
```

> Note: many inline examples in §§6–17 use short illustrative IDs that predate this rule; they show *structure*, not conformant IDs, and are regenerated during re-conversion.

### DEF Body Contents

A DEF body can contain any combination of:
- `PROPERTIES { }` — typed fields
- `RULES { }` — behavioral rules
- `EXTENDS` — inheritance declaration
- `APPLIES TO` — scope constraint
- Bare type constraints (see §8)
- Nested DEFs
- System-defined sub-blocks (see §10)
- Inline text strings

### Definitions vs. Instances *(v0.4)*

A `DEF` serves two roles, distinguished by whether it `EXTENDS` an **actor type**:

- **Definition (schema):** declares a type and its fields *with* type/constraint information — e.g. `ACTOR "Samurai" DEF { PROPERTIES { ^"Air" INTEGER MIN 1 MAX 5 DEFAULT 1 } }`.
- **Instance (a specific character — PC or NPC):** a `DEF` that `EXTENDS` an actor type and fills in concrete values via canonical `PROPERTIES`, using the inline-value form (§8). Types and constraints are **inherited** from the extended actor, not restated.

```
#<hash> ^"Ide Tadaji" DEF {
    EXTENDS ^"Samurai"
    PROPERTIES {
        ^"Rings" DEF {
            ^"Air"   INTEGER 4
            ^"Water" INTEGER 3
        }
        ^"Honor" INTEGER 35
        ^"Role"  STRING "Unicorn Trade Governor"
    }
}
```

Instances use the **same** grammar as definitions — no `=` assignments, no dotted paths, no `STATS` block, and the canonical `#hash ^"Name" DEF` ordering. An `.actor` file is exactly one such instance. Coherence validation checks each value against the constraint inherited from the actor type (here, Air ∈ 1–5).

---


### §5d — Reference resolution: one rule for every construct *(v0.5, DECISION-13)*

A **reference site** is any place one definition names *an entity that already exists*: `EXTENDS`,
`APPLIES TO`, `LIST OF`, `CONCERNS`, `OVERRIDE`, `MODIFY`, the target of `ALIAS … FOR`, an entity
option or `OF` type of a `CHOOSE` (§5b), the type and the value of a `REF`, the target of a `SET`
or `TRANSFORM` and the die of a `ROLL` (§8), and the `REFERENCES` / `REFERENCED BY` targets of §5c. All of them obey the same
rule.

**Declaration sites are not reference sites.** `ADD #hash ^"Name" DEF { … }` (§13) *asserts new
content*, so its hash is an anchor being minted, not a pointer to one; `ALIAS ^"New" FOR ^"Existing"`
likewise declares `^"New"` and references only `^"Existing"`. `SET`, `ADD_TO` and `REMOVE_FROM` name a
**property** of the entity being modified, not an entity, and are outside this rule.

**The `#hash` is the referent. The `^"Name"` is a readability aid.**

```
EXTENDS #tor5Shield000000001 ^"Shield"     # resolves to that anchor, whatever else is named "Shield"
EXTENDS ^"Shield"                          # resolves by name — and only if the name is unambiguous
```

1. **Resolution is by hash when a hash is present.** The caret name must match the anchor's own name;
   a mismatch is an **ERROR** (it means one of the two was edited and the other was not). A hash that
   is not a declared anchor is an **ERROR**.
2. **A hashless reference SHOULD carry the hash.** Where the name resolves to exactly one entity the
   reference is well-defined but untraceable, so it **WARNs**.
3. **A hashless reference whose name resolves to more than one distinct entity is an ERROR.** Nothing
   in the file says which is meant, so every consumer must invent a tie-break, and two consumers that
   invent different ones disagree about what the corpus says. Two DEFs are the *same* entity when they
   carry the same hash (a legal restatement — §13, DECISION-4); distinct hashes, or a hashless DEF
   beside a hashed one, are distinct entities.

**Scope of the name form.** `^"Name"` remains legal and remains the readable surface — this is not a
deprecation. It is sufficient only where the name is unique corpus-wide, which is a property of the
corpus, not of the reference, and can stop being true when a later file adds a same-named entity. That
is precisely what the hash immunises against.

**Migration.** The hash for an unambiguous hashless reference is mechanically derivable — the name
already resolves — so backfilling is a scripted, reviewable edit, not re-authoring. Ambiguous sites
cannot be backfilled mechanically: they need the intended target chosen, which is the point.

---

## 6. Inheritance (EXTENDS)

A DEF that `EXTENDS` another inherits all of its PROPERTIES and RULES. The child can add new properties, override defaults, and add rules.

**By name:**
```
^"Samurai" DEF {
    EXTENDS ^"Entity"
}
```

**By hash + name:**
```
^"Samurai" DEF {
    EXTENDS #L5R001aB2cD4eF6gH8iJ0kL ^"Entity"
}
```

Both forms are legal, and **§5d governs which one resolves**: the hash is the referent, the caret
name is the readable surface, and they must agree. A hashless `EXTENDS` WARNs; a hashless `EXTENDS`
whose name resolves to more than one distinct entity is an **ERROR**.

> *(v0.4 said the by-name form was "canonical and sufficient" and called a validator that required a
> hash "a validator bug to fix". **Both statements are withdrawn in v0.5 — see DECISION-13.** They
> made inheritance the one graph in the corpus that could not be resolved unambiguously, and the
> damage is not confined to the colliding entity: a sibling that references the collided name is
> reported broken too.)*

---

## 7. Scope (APPLIES TO)

`APPLIES TO` declares which actor types a definition can be attached to. This is a scope constraint, not inheritance. Its targets are reference sites and resolve under **§5d** (hash is the referent; hashless WARNs; hashless-and-ambiguous is an ERROR).

> **DECISION-1 (resolved, v0.4):** `APPLIES TO` has historically been overloaded for three jobs — scope (attachment), type inheritance, and category tagging. **v0.4 restricts it to scope only.** Use `EXTENDS` for type / `is-a` relationships, and a dedicated tag (e.g. `^"Category" ENUM [...]` or `TAGS [...]`) for categorization. Files that used `APPLIES TO` for inheritance or tagging are migration targets.

```
^"Hida Defender" DEF {
    APPLIES TO [^"Samurai"]
}

^"Blood Potency" DEF {
    APPLIES TO [^"Kindred"]
}

^"Void Points" DEF {
    APPLIES TO [^"Samurai", ^"Adversary"]
}
```

The bracket list contains caret references to ACTOR DEFs. A definition with `APPLIES TO` can only be used by the listed actor types.

---

## 8. Properties Block

The `PROPERTIES` block defines the typed fields of a DEF.

```
PROPERTIES {
    ^"Name" STRING REQUIRED
    ^"Description" STRING
    ^"Honor" INTEGER MIN 0 MAX 100 DEFAULT 50
    ^"Active" BOOLEAN DEFAULT true
    ^"Category" ENUM ["Kata", "Shuji", "Ritual"]
    ^"Skills" LIST OF ^"Skill"
    ^"Roles" LIST ["Bushi", "Courtier"]
    ^"Rings" DEF {
        ^"Air" INTEGER MIN 1 MAX 5 DEFAULT 1
        ^"Earth" INTEGER MIN 1 MAX 5 DEFAULT 1
    }
}
```

### Property Types

| Type | Syntax | Description |
|------|--------|-------------|
| STRING | `STRING [value] [REQUIRED\|FIXED]` | Text value |
| INTEGER | `INTEGER [MIN n] [MAX n] [DEFAULT n] [REQUIRED]` | Numeric value with optional constraints |
| BOOLEAN | `BOOLEAN [true\|false] [DEFAULT true\|false]` | True/false |
| ENUM | `ENUM ["val1", "val2", ...]` | Constrained choice |
| LIST | `LIST ["val1", "val2"]` | Literal list of values |
| LIST OF | `LIST OF ^"TypeName"` | Typed collection referencing another DEF |
| LIST OF STRING | `LIST OF STRING [values]` | Typed collection of strings with optional defaults |
| REF | `REF OF ^"TypeName"` · `^"Name" REF ^"Entity"` | Reference to one entity *(v0.6, see below)* |
| ROLL | `ROLL n OF ^"Die"` | A roll of `n` dice *(v0.6, see below)* |
| DEF (nested) | `^"Name" DEF { ... }` | Nested structured object |

### Modifiers (apply to any type)

- `REQUIRED` — must be provided
- `FIXED` — cannot be changed after creation
- `DEFAULT value` — default value if not provided
- `MIN n` / `MAX n` — range constraints (INTEGER)
- `FIAT "reason"` *(v0.4)* — waive validation for this value (intentional exception; see *FIAT* below)

### Inline Value Assignment

A property can include its value inline at declaration time:

```
^"School Name" STRING "Hida Defender" FIXED
^"Clan" REF #hash ^"Crab"
^"Combat Conflict Rank" INTEGER 2
^"Starting" BOOLEAN true
^"In-Clan Disciplines" LIST OF STRING ["Celerity", "Potence", "Presence"]
```

### One entity — `REF` *(v0.6, DECISION-17)*

A property that names one entity holds a reference to it. A name in a `STRING` is not checked; a
`REF` is.

```
# on the type: what kind of entity the property points at
REF OF #hash ^"Clan" REQUIRED

# on an instance: the entity it points at
^"Clan" REF #hash ^"Crab"
```

- `REF OF ^"Type"` declares the property. With no name written, the property takes the type's
  name: `REF OF ^"Clan"` declares a property `^"Clan"`.
- A name may always be written before `REF`. It must be when the property's name differs from its
  type (`^"Patron" REF OF #hash ^"Virtue"`), and it may repeat the type's name
  (`^"Clan" REF OF #hash ^"Clan"`).
- `REF ^"Entity"`, after the property's name, gives its value. An instance inherits the declaration
  and writes only the value; both may be written on one line
  (`REF OF #hash ^"Clan" #hash ^"Crab"`).
- The type and the entity are reference sites (§5d).
- Coherence: both resolve. Where the type is declared, the entity must be of that type: it
  `EXTENDS` it, directly or through a chain.
- For several entities, use `LIST OF ^"Type" [ … ]`.

### Changes to a value — `SET` and `TRANSFORM` *(v0.6, DECISION-16)*

An entity often changes a value that belongs to something else: a family adds 1 to a skill, a
heritage sets starting Glory, a condition halves movement. A change names its target and says what
happens to it.

```
#hash ^"Glory"   SET 44                                  # the value becomes 44
#hash ^"Command" TRANSFORM ADD 1                         # the value goes up by 1
#hash ^"Honor"   TRANSFORM SUBTRACT 5
#hash ^"Damage"  TRANSFORM MULTIPLY 2
#hash ^"Speed"   TRANSFORM DIVIDE 2 ROUND DOWN MIN 1
#hash ^"TN"      TRANSFORM ADD #hash ^"School Rank"      # the amount is another value
#hash ^"Damage Die" TRANSFORM MANUAL "increase the die by one step"
CHOOSE 1 [ #hash ^"Earth", #hash ^"Fire" ] TRANSFORM ADD 1
```

- **Target.** A reference to the thing whose value changes, or a `CHOOSE` (§5b), in which case the
  change applies to each option chosen. A target that is a reference is a reference site (§5d).
- **`SET <amount>`.** The value becomes the amount.
- **`TRANSFORM <METHOD> <amount>`.** The value is changed by the method. The methods are a closed
  set: `ADD`, `SUBTRACT`, `MULTIPLY`, `DIVIDE`. Write the method the source prints: "−5" is
  `SUBTRACT 5`.
- **Amount.** An integer, or a reference to another value. Dice amounts are not yet defined.
- **`ROUND UP`, `ROUND DOWN`, `ROUND NEAREST`.** How a result that is not whole is rounded.
- **`MIN n`, `MAX n`.** The result is not below `n`, or not above it.
- **`TRANSFORM MANUAL "…"`.** A change the methods cannot express, in the source's own words,
  verbatim. It is the same escape §21 uses for a conversion that needs judgement.

A change may stand wherever a property may: in a `PROPERTIES` block, in a nested property `DEF`, or
in a system block. When a change applies, and to whom, is not part of the change. That stays with the
entity that carries it, with `APPLIES TO`, and with the text.

### Where a statement ends *(v0.6)*

The DSL has no statement terminator. Two statements end at a place where a reference may or may not
follow: `REF OF ^"Type"`, which an entity may follow, and `SET` or `TRANSFORM <METHOD>`, which an
amount may follow. One rule settles both:

**A reference that is followed by a property type (`STRING`, `INTEGER`, `BOOLEAN`, `ENUM`, `LIST`,
`REF`, `ROLL`), `DEF`, `CHOOSE`, `SET`, `TRANSFORM` or `MODIFY` opens the next statement.** It is not the
entity or the amount of the statement before it.

```
REF OF #hash ^"Clan"                      # declares the property; gives no entity
^"Glory" INTEGER MIN 0 MAX 100            # ^"Glory" is followed by INTEGER: a new statement

#hash ^"Command" TRANSFORM ADD            # an error: no amount
#hash ^"Tactics" TRANSFORM ADD 1          # ^"Tactics" is followed by TRANSFORM: a new statement
```

> **For review — two uses of `SET`.** `SET` is also a directive inside a `MODIFY` block (§13), written
> before its target (`SET ^"Starting Honor" DEFAULT 45`), where it patches a definition when files
> are composed. Here it follows its target and describes a change in play. Position tells them
> apart: directly inside a `MODIFY` body it is the §13 directive. Whether one word should serve both
> is to be reviewed.

Coherence: the target resolves; the method is one of the four, or `MANUAL` followed by a string; the
amount is an integer or a reference that resolves; `ROUND` is followed by `UP`, `DOWN` or `NEAREST`.

### Dice and rolls — `FACES`, `ROLL` and `NEXT` *(v0.6, DECISION-18)*

**A die is a DEF.** It `EXTENDS ^"Die"` and lists its faces in a `FACES` block.

```
#hash ^"d8" DEF {
    EXTENDS #hash ^"Die"
    FACES { 1-8 }
}
```

- A face is a number. A range of numbers stands for one face each: `1-8` is eight faces.
- A face may be followed by what it shows, a string or a reference, for a die whose faces are not
  numbers: `1 "Blank"`, `2 #hash ^"Opportunity"`.
- Each face has a weight of 1. `WEIGHT n` after a face gives it another: `3 WEIGHT 2`.

**The dice module.** This repo ships `modules/0.6/titterpig-0.6-dice.ttrpg`. It defines `^"Die"` and
`^"d2"`, `^"d3"`, `^"d4"`, `^"d6"`, `^"d8"`, `^"d10"`, `^"d20"` and `^"d100"`. Every edition includes
it. It is edition-neutral: its hashes are the same wherever it is included (§19). A system's BASE
declares `DEPENDS_ON "Titterpig_Dice"` (§3), and a corpus is validated with the module passed
alongside it. A system defines any other die it needs as a DEF of its own.

**A roll.** `ROLL n OF #hash ^"die"` rolls `n` of a die. Where the faces are numbers, its value is
their sum. The die is a reference site (§5d). A `TRANSFORM` may follow a roll in the same statement
and changes its value:

```
^"Roll" ROLL 4 OF #hash ^"d8" TRANSFORM ADD 12
```

**Steps — `NEXT`.** Statements in a block have no order. `NEXT` before a statement makes it a step
that follows the statement above it. A step's result is named by the property it sits under, and a
later step refers to it by that name.

```
^"Roll" ROLL 4 OF #hash ^"d8" TRANSFORM ADD 12      # roll 4 d8 and add 12
NEXT #hash ^"Hit Points" SET ^"Roll"                 # store the sum
^"Damage Type" REF #hash ^"Physical"                 # no NEXT: order does not matter here
```

A chain of steps runs forward only. There is no way to write a branch or a loop.

Coherence: the count is 1 or more; the die resolves and is a `^"Die"`; a `WEIGHT` is a positive
integer; a range runs from low to high; `NEXT` has a statement before it and a statement after it.

### FIAT — Intentional Exceptions *(v0.4)*

`FIAT` is an author's assertion that a value or element is **intentionally correct and complete**, even where it would otherwise fail validation. It suppresses validation findings — both **constraint** violations (`MIN`/`MAX`/`ENUM`/type) and **completeness** requirements (`REQUIRED` / missing fields) — within its scope. A **reason string is required**: `FIAT` is a documented, auditable exception, never a silent mute. (It is the machine-readable way to record intent — a `# this is fine` comment is not valid, since comments carry no data in v0.4.)

**Property level** — a trailing modifier; waives findings for that one value:

```
^"Air" INTEGER 7 FIAT "Oni Lord: supernatural Air, beyond the mortal 1–5 range"
```

**Element level** — a statement in a DEF body; **cascades**, waiving findings for that DEF and its *entire subtree* (every descendant property and sub-DEF):

```
#h9k7mQ2vX7wZ9tB4 ^"The Nameless One" DEF {
    EXTENDS ^"Adversary"
    FIAT "One-off published horror: intentionally omits standard adversary stats and exceeds normal limits"
    PROPERTIES {
        ^"Fear" INTEGER 12
        # fields normally required of an Adversary are intentionally absent here
    }
}
```

**Scope guidance:** use the **narrowest** `FIAT` that covers the deviation. Property-level for a single odd value; element-level only when the whole definition is exceptional — the cascade will also suppress genuine mistakes beneath it. Standard NPCs/adversaries should be *defined against their own actor type* (so they are complete on their own terms and need no `FIAT`); reserve `FIAT` for true one-offs.

**Tooling:** both the DSL validator and downstream consumers honor `FIAT`. Because every `FIAT` carries a reason, tooling can emit a **FIAT report** — the full list of intentional deviations in a corpus — for review.

---

## 9. Bare Type Constraints

A DEF may declare a bare type constraint directly in its body (outside PROPERTIES) when the definition itself represents a typed value:

```
^"Strength" DEF {
    APPLIES TO [^"Kindred", ^"Mortal"]
    INTEGER MIN 1 MAX 5
}

^"Approach" DEF {
    ENUM ["Air", "Earth", "Fire", "Water", "Void"]
}

^"Chronicle" DEF {
    STRING REQUIRED
}

^"GM Role" DEF {
    BOOLEAN DEFAULT false
}
```

This means "Strength IS an integer 1–5" rather than "Strength HAS an integer property." The parser treats it as an implicit `^"Value"` property of the declared type.

---

## 10. Text Content

### Inline Strings

Single-line text uses quoted strings, either as values of keywords or bare within a block:

```
^"Way of the Crab" DEF {
    DESCRIPTION "Ignore the Cumbersome quality of armor you wear."
}
```

### Multi-line String Content

For multi-line descriptive content, use sequential quoted strings within a block:

```
SCHOOL_ABILITY "Way of the Crab" {
    "Ignore the Cumbersome quality of armor you wear."
    "Once per round, before making a check to resist a critical strike,"
    "you may reduce the severity of that critical strike by your school rank."
}
```

### Long String Content

For paragraph-length mechanical text, use a single string with `\n\n` for paragraph breaks:

```
SYSTEM "The user takes one turn and pays the cost, summoning shadow extensions.\n\nThey can also use the shadows to perform simple actions but nothing as advanced as typing."
```

### Triple-Quoted Text Blocks

For multi-line descriptive content where preserving line breaks matters, use triple-quoted text blocks:

```
^"Way of the Crab" DEF {
    DESCRIPTION """
        Ignore the Cumbersome quality of armor you wear.
        Once per round, before making a check to resist a
        critical strike, you may spend 1 Void point to add
        your school rank to the TN of that check.
    """
}
```

Systems may use `TEXT` as an alias for `DESCRIPTION` when the content is mechanical rather than narrative.

---

## 11. System-Defined Sub-Blocks

Systems define their own keyword vocabulary for structured sub-blocks. The base spec does **not** reserve these keywords — they are conventions established by each system's files.

### L5R5e Examples

```
CURRICULUM {
    RANK 1 {
        SKILL_GROUP "Martial Skills"
        SKILL "Command"
        TECHNIQUE_GROUP "Rank 1 Kata"
        ^"Lord Hida's Grip" [kata]
    }
}

STARTING_TECHNIQUES {
    KATA ^"Lord Hida's Grip"
    KATA CHOOSE 1 [^"Striking as Earth", ^"Striking as Water"]
}

SCHOOL_ABILITY "Way of the Crab" {
    "Ignore the Cumbersome quality of armor you wear."
}

MASTERY_ABILITY ^"The Mountain Does Not Fall" {
    "At the beginning of your turn, you may spend 1 Void point..."
}

STARTING_OUTFIT ["Lacquered armor", "traveling clothes", "daishō"]

ACTIVATION "As an Attack action, make a TN 4 Martial Arts check..."

OPPORTUNITIES {
    "Earth (op): Your target cannot guard this round."
    "Void +(op): This effect persists for one additional round."
}

FAMILIES {
    ^"Hida"
    ^"Hiruma"
    ^"Kaiu"
}

HERITAGE_TABLE {
    1 ^"Famous Deed" DEF {
        MODIFIERS { #hash ^"Glory" TRANSFORM ADD 3 }
        SUB_TABLE "1d10" {
            "1-2" "A famous weapon: Receive one weapon of rarity 7 or lower"
        }
    }

    # An entry keyed to a span of die results uses a roll range. Supplement
    # heritage tables assign one result to several rolls; the range is part
    # of the structure, never a note in prose.
    2-3 ^"Triumph over the Lion" DEF {
        MODIFIERS { #hash ^"Honor" TRANSFORM ADD 5 }
        SUB_TABLE "1d10" {
            "1-3" "A weapon"
            "9" "A horse or another animal"
        }
    }

    # Where an entry grants something outright instead of a second roll.
    10 ^"Imperial Heritage" DEF {
        MODIFIERS { #hash ^"Status" TRANSFORM ADD 10 }
        EFFECT { "Gain the ^\"Blessed Lineage\" distinction" }
    }
}

GENERAL_OPPORTUNITIES {
    ANY {
        "(op): If you failed, determine the easiest way to accomplish the task."
    }
    AIR {
        "(op): Learn another character in the scene's demeanor."
    }
}
```

### VTM5e Examples

```
CHARACTERISTICS {
    TYPE "Mental"
    MASQUERADE_THREAT "Low"
    BLOOD_RESONANCE "Phlegmatic"
}

POWERS {
    LEVEL_1 ["Awe", "Daunt"]
    LEVEL_2 ["Lingering Kiss"]
    LEVEL_3 ["Entrancement", "Dread Gaze"]
}

AMALGAMS {
    "Unliving Hive" REQUIRES ^"Animalism" >= 3 AND ^"Obfuscate" >= 2
}

TRIGGER ^"Bestial Failure"

PREDATOR_TEMPLATES {
    "Alleycat" {
        SPECIALTY "Intimidation_Mugging"
        DISCIPLINE_BONUS "Potence_1"
    }
}

DICE_POOL "Wits + Oblivion"
DURATION "One scene or until ended"
COST "One Rouse Check"
```

The base spec recognizes the **pattern** (keyword followed by `{ }`, `[ ]`, or a value) without prescribing which keywords exist. Each system's files define their own vocabulary.

---

## 12. Rules Block

```
RULES {
    #L5R002mN3oP: WHEN [^"Entity" CREATED] THEN REQUIRE ^"Name"
    #L5R005uV1wX: WHEN [^"Strife" > ^"Composure"] THEN ^"Samurai" IS compromised
    #L5R300aB2cD: technique_categories_granted_by_school
}
```

Rules are hash-labeled entries inside a `RULES { }` block. The base spec defines the container syntax:

- `#hashID: WHEN [condition] THEN action` — structured rule with trigger
- `#hashID: label_name "text"` — a named rule carrying the source's own statement of it,
  verbatim (paragraphs as `\n\n`, §10). Where the source prints a name for the item — a table
  row, a bulleted term, a step heading — the text leads with it: `"Label: text"`.

A rule states itself. `#hashID: label_name` with no text — a name, with the rule described in a
comment beside it — carries nothing a tool can read, and a comment is not data: the validator
**warns** on one *(2026-09-23)*. The L5R 5e corpus held 980 of them, written that way in its first
pass under this section's earlier wording ("named rule placeholder — description lives in
comments or documentation"); they were given the book's text, or removed where the book has no
such rule.

The condition/action grammar is system-defined. `WHEN` and `THEN` are recognized by the base spec as rule structure markers. Other keywords used in rule expressions (`REQUIRE`, `IS`, `CREATED`, `INTERACTS`, `ENTERS`, `USE`, etc.) are conventions, not base-spec reserved words.

---

## 13. Modification System (Extensions)

Extensions can modify parent content using three strategies:

### OVERRIDE — Full Replacement

Completely replaces a parent DEF:

```
EXTENSION "Errata2020" EXTENDS "L5R5e_Core" {
    OVERRIDE ^"Hida Defender" {
        # completely replaces the parent definition
    }
}
```

### ADD — New Content

Introduces content not in the parent:

```
EXTENSION "Sourcebook" EXTENDS "L5R5e_Core" {
    ADD ^"New School" DEF {
        # brand new definition
    }
}
```

`ADD` asserts the content is *new*. If the name is already defined in the loaded corpus the
assertion is false, and the validator raises a **warning** — pointing at `OVERRIDE` / `MODIFY`,
which is what a deliberate replacement should say. It is a warning rather than an error because the
loaded set is not necessarily the consumer's composition set: the collision may be with an optional
sourcebook that would never be co-loaded with this one, and precedence would resolve it either way
(*Composition & Precedence*, below).

### MODIFY — Partial Changes

Surgical modifications to existing definitions:

```
EXTENSION "Errata2020" EXTENDS "L5R5e_Core" {
    MODIFY ^"Hida Defender" {
        SET ^"Starting Honor" DEFAULT 45
        ADD_TO ^"Techniques Available" "Mantras"
        REMOVE_FROM ^"Roles" "Shinobi"
    }
}
```

Both spellings of the statement are legal and mean the same thing: `MODIFY ^"X" { … }` and
`^"X" MODIFY { … }`.

Within a `MODIFY` block:
- `SET` — change a property value or constraint
- `ADD_TO` — append to a list property
- `REMOVE_FROM` — remove from a list property
- `SET DESCRIPTION "…"` — replace the target's whole `DESCRIPTION` *(v0.5 addendum)*
- `PROPERTIES { … }` — **introduce** properties the target does not have
- `RULES { … }` — modify individual rules (below)

### Variant printings — `SET DESCRIPTION` *(v0.5 addendum, DECISION-14)*

A book that reprints an entity in **different words** that should take effect — a corrected sentence,
a later supplement's rewording — expresses it as a `MODIFY` of the original whose `SET DESCRIPTION`
carries the variant's text, verbatim and whole:

```
MODIFY #DemoRisingBladeX2yZ4aB6cD ^"Rising Blade" {
    SET DESCRIPTION "Strike upward from a low guard. (The reprint's wording, whole and verbatim.)"
}
```

The replacement is the **entire** description, never a diff, so the variant stays byte-verbatim and
needs no patch language. `SET DESCRIPTION` must be followed by a string. A `MODIFY` applies on top of
its target, so the variant's wording is what a composition carrying it shows; when the target's text
should stand instead (it supersedes the variant), the printing is a `REPRINT` (§5b). Only the name
differing is an `ALIAS`.

### Changing vs. introducing a property *(v0.4, decided 2026-07-25)*

`SET` **changes**; a `PROPERTIES` block **introduces**. The two are not interchangeable:

```
MODIFY ^"Covenant Boon" {
    SET ^"Magnitude" ENUM ["Minor", "Major", "Free"]   # widens a field the target has
    PROPERTIES {
        ^"Category" ENUM ["Site", "Buildings", "Resources"]   # a field it never had
        ^"Requires" STRING
    }
}
```

`SET` naming a property the target does not declare — neither its own nor one inherited through
`EXTENDS` — is an **error**. That is the whole point of the split: a mistyped `SET ^"Magnitud"`
would otherwise be indistinguishable from a deliberate new field, and would silently create a
property nothing reads instead of widening the one that was meant. Widening a type with a genuinely
new field is normal and expected — it just has to say so, in a `PROPERTIES` block.

`ADD_TO` / `REMOVE_FROM` require the named property to exist **and be a `LIST`** (error otherwise).
`REMOVE_FROM` naming a value the list does not carry is a **warning**, not an error: an earlier
layer's `ADD_TO` may legitimately have put it there.

**Narrowing an enum.** `SET ^"P" ENUM [...]` that *drops* a permitted value is legal — but a
loaded definition that still assigns a dropped value is orphaned by it, and each such instance
raises a **warning** against the instance, naming the `SET` responsible.

### MODIFY in Rules

Extensions can also modify individual rules within a DEF:

```
^"Blood Potency" MODIFY {
    RULES {
        #5Gpn6DrSZp MODIFY: blood_surge_mechanics NOW REFERENCES #YD4PosF ^"Blood Surge Table"
    }
}
```

### Errata & Corrections *(v0.4)*

Errata and corrections are **data, not commentary.** They MUST be expressed as machine-readable `MODIFY` / `OVERRIDE` / `ADD` inside a dedicated **errata EXTENSION file** named `*-errata-*` that depends on the corrected module. Source files stay pristine; tooling composes the overlay deterministically.

```
EXTENSION "L5R5e_Core_Errata" EXTENDS "L5R5e_Core" {
    NAME "L5R5e Core — Errata"
    VERSION "2020.1"
    SPEC_VERSION "0.4"

    MODIFY ^"Hida Defender" {
        SET ^"Starting Honor" DEFAULT 45   # p.65 correction (annotation only)
    }
}
```

Writing a correction *as* a comment (`# p.65 … should read …`) is **non-conformant** — comment-only corrections are lost the moment a tool strips comments.

### Composition & Precedence *(v0.4)*

A downstream consumer loads a **selected, ordered set** of `.ttrpg` files — a *composition set* (a
BASE + chosen EXTENSIONs + errata + homebrew), all drawn from **one edition namespace** (§19). **Load
order is precedence:** when more than one loaded file defines the same entity, the **later one wins**.
There are two ways for a later file to override an earlier one, both valid:

- **Explicit** — it issues `OVERRIDE` / `MODIFY` / `ADD` (above) naming the target. Surgical and
  auditable; the base definition stays put and the overlay is applied deterministically.
- **Implicit** — it simply **re-states the target entity's hash** with new content; by load-order
  precedence that replaces the earlier definition wholesale. No directive needed.

Consumers normally load only **one** definition of a given entity; overlapping printings (a spell
reprinted in two sourcebooks, a beta and a final ruleset, a draft and a definitive edition) are
generally not co-loaded, and when they are, precedence silently resolves them. Precedence resolution
itself is a **consumer / `.ttrpg → .json`** concern — the file-level validator checks *coherence*
within an edition (§20), not which layer ultimately wins.

---

## 14. Cross-References

### Caret References `^"Name"`

Refer to named definitions by their display name:

```
EXTENDS ^"School"
APPLIES TO [^"Samurai"]
LIST OF ^"Technique"
KATA ^"Lord Hida's Grip"
```

### Hash IDs `#identifier`

Unique anchors for cross-file traceability:

```
#L5R001aB2cD4eF6gH8iJ0kL ACTOR "Entity" DEF { }
#L5R002: WHEN [^"Entity" CREATED] THEN REQUIRE ^"Name"
```

### Embedded References in Strings

Caret references can appear inside quoted strings with escaped quotes:

```
ACTIVATION "When you make a ^\"Fitness\" check..."
EFFECT "If you fail, you suffer ^\"Disoriented\"."
```

### Combined Hash + Caret

When both appear together, the hash provides the unique ID and the caret provides the human-readable name:

```
EXTENDS #L5R001aB2cD4eF6gH8iJ0kL ^"Entity"
#L5R250aB2cD4eF6gH8iJ0k ^"Clan" DEF { }
```

---

## 15. Reserved Keywords (Base Spec)

Only these keywords are reserved by the base spec:

**File-level:** `BASE`, `EXTENSION`, `EXTENDS`, `NAME`, `VERSION`, `RELEASE_DATE`, `DEPENDS_ON`

**Definition:** `DEF`, `ACTOR`, `TEMPLATE`, `CHOICES`, `PROPERTIES`, `RULES`

**Types:** `STRING`, `INTEGER`, `BOOLEAN`, `ENUM`, `LIST`, `OF`, `REF`, `ROLL`

**Dice (§8):** `FACES`, `WEIGHT`, `ROLL`, `NEXT`

**Changes (§8):** `SET`, `TRANSFORM`, `ADD`, `SUBTRACT`, `MULTIPLY`, `DIVIDE`, `ROUND`, `UP`, `DOWN`, `NEAREST`, `MANUAL` (`SET` and `ADD` are shared with **Modification**, `MANUAL` with **Bridge**, `MIN` / `MAX` with **Modifiers**)

**Modifiers:** `REQUIRED`, `FIXED`, `DEFAULT`, `MIN`, `MAX`, `FIAT`

**Scope:** `APPLIES`, `TO`, `ALIAS`

**Choice (§5b):** `CHOOSE`, `DISTINCT`, `INDISTINCT`, `WITH`, `AND`, `OR`, `NOT` (`OF` is shared with **Types**)

**Rule structure:** `WHEN`, `THEN`

**Modification:** `OVERRIDE`, `ADD`, `MODIFY`, `SET`, `ADD_TO`, `REMOVE_FROM`, `REPRINT`

**Text:** `DESCRIPTION`, `TEXT`

**Narrative containers:** `SETTING`, `FRAME`, `ARC`, `CAMPAIGN`, `SCENE`, `LOCATION` (and their sub-keywords as defined in §16)

**Codex (§25):** `CODEX`, `SOURCES`, `CATEGORIES`, `RELATIONS`, `ENTITY`, `IS`, `RELATIONSHIPS`, `INVERSE`, `DOMAIN`, `RANGE`, `SYMMETRIC`, `TRANSITIVE`, `SOURCE`, `AT`, `FROM` (`FOR`/`EDITION`/`DEPENDS_ON`/`VERSION` are shared with §3/§19; `EXTENDS` with §6)

**Bridge (§21):** `BRIDGE`, `ORIGIN`, `DESTINATION`, `EXTERNAL`, `DISPOSITIONS`, `DISPOSITION`, `ALIASES`, `CONVERSION`, `GUIDANCE`, `MAP`, `REMAINDER`, `PROCEDURE`, `SUBJECT`, `SCOPE`, `ASPECT`, `CONCERNS`, `TOPICS`, `EXHAUSTIVE`, `CONVERT`, `INTO`, `UNCHANGED`, `SCALE`, `OVER`, `RESTATE`, `MANUAL` (`ALIAS`/`FOR` are shared with §5b; `ENTRY` and `TEXT` with §16/§10)

All other keywords — `CURRICULUM`, `SCHOOL_ABILITY`, `POWERS`, `AMALGAMS`, `TRIGGER`, `CHARACTERISTICS`, `HERITAGE_TABLE`, `ACTIVATION`, `OPPORTUNITIES`, `PREDATOR_TEMPLATES`, `DICE_POOL`, `COST`, `DURATION`, etc. — are **system-defined**. They belong to L5R5e, VTM5e, or whatever system uses them.

---

## 16. Narrative Containers

The DSL supports structured narrative content through four container types. These complement the BASE (game mechanics) and EXTENSION (content additions) containers.

### SETTING — System-Agnostic World-Building

A SETTING defines lore, geography, factions, history, and culture with no mechanical dependencies. Settings are reusable across game systems.

```
SETTING "SettingID" {
    NAME "Human-readable Setting Name"
    VERSION "1.0.0"

    THEMES {
        "Theme description"
        "Another theme"
    }

    HISTORY {
        ENTRY ^"Event Name" {
            PERIOD "Time period or date"
            DESCRIPTION "What happened"
        }
    }

    LOCATION ^"Location Name" {
        DESCRIPTION "Physical and atmospheric description"
        TAGS ["tag1", "tag2"]

        LOCATION ^"Sub-Location" {
            DESCRIPTION "Nested location within parent"
        }
    }

    ENTRY ^"Faction Name" {
        TYPE "faction"
        DESCRIPTION "Faction overview"
        TRAITS ["trait1", "trait2"]
    }
}
```

**Fields:**
- `SettingID`: Unique identifier (e.g., `"RichFrog"`, `"Rokugan"`)
- `NAME`: Full display name
- `VERSION`: Semantic version
- `THEMES`: Narrative themes as a string list
- `HISTORY`: Timeline of significant events
- `LOCATION`: Named places with optional nesting
- `ENTRY`: Factions, cultures, or other setting elements

**Example:**

```
SETTING "RichFrog" {
    NAME "City of the Rich Frog"
    VERSION "0.1.0"

    THEMES {
        "Commerce and corruption at the crossroads"
        "Three-clan tension beneath a veneer of civility"
        "The cost of ambition in a stratified society"
    }

    HISTORY {
        ENTRY ^"Founding" {
            PERIOD "Early Empire"
            DESCRIPTION "Founded as a minor trading post at the convergence of three clan territories"
        }
        ENTRY ^"Rise of the Markets" {
            PERIOD "Mid Empire"
            DESCRIPTION "Explosive growth as merchant caravans discovered the strategic location"
        }
    }

    LOCATION ^"City of the Rich Frog" {
        DESCRIPTION "A bustling trade city straddling the borders of Lion, Unicorn, and Dragonfly territories"
        TAGS ["urban", "trade-hub", "contested"]

        LOCATION ^"Licensed Quarter" {
            DESCRIPTION "The regulated commercial district where sanctioned merchants conduct business"
        }
        LOCATION ^"Leatherworkers' Road" {
            DESCRIPTION "An unofficial market street where eta craftspeople sell goods of surprising quality"
        }
    }

    ENTRY ^"Ide Trading Coalition" {
        TYPE "faction"
        DESCRIPTION "Unicorn-backed merchant consortium controlling the northern trade routes"
        TRAITS ["wealthy", "pragmatic", "well-connected"]
    }

    ENTRY ^"Kitsu Spiritualists" {
        TYPE "faction"
        DESCRIPTION "Lion-aligned spirit guardians who watch for ancestral disturbances"
        TRAITS ["devout", "watchful", "politically influential"]
    }
}
```

### FRAME — Campaign Scaffold

A FRAME provides a starting point for GMs: a setting combined with enough mechanical scaffolding to begin play, without defining complete scenes or arcs. It requires a BASE system and optionally references a SETTING.

> **DECISION-2 (resolved, v0.4):** NPCs are **instances** — write them with the canonical instance form (§5, *Definitions vs. Instances*): a `#hash ^"Name" DEF` that `EXTENDS` its actor type with a `PROPERTIES` block of inline typed values. The looser `DEF ^"Name" #id { TYPE "npc" … STATS { rings.air = 4 } }` form in the illustrative FRAME/ARC blocks below — reversed order, `=` assignment, dotted paths, `TYPE`-as-tag — is **deprecated** and left as-is only pending re-conversion. No new grammar is added.

```
FRAME "FrameID" {
    NAME "Human-readable Frame Name"
    VERSION "1.0.0"
    DEPENDS_ON "BaseSystemID"
    USES_SETTING "SettingID"    # optional

    THEMES {
        "Theme description"
    }

    STARTING_CONDITIONS {
        DESCRIPTION "How PCs enter the frame"
        MODIFICATIONS {
            # Character creation adjustments for this frame
            attribute_name RANGE(new_min, new_max)
            attribute_name DEFAULT new_value
        }
    }

    # NPC roster — canonical instances (see §5, Definitions vs. Instances)
    #npc_id ^"NPC Name" DEF {
        EXTENDS ^"Adversary"
        PROPERTIES {
            ^"Role" STRING "Role in the frame"
            ^"Description" STRING "Brief description"
            # stats as typed fields, e.g. ^"Rings" DEF { ^"Air" INTEGER 3 }
        }
    }

    # Adventure hooks for the GM
    ENTRY ^"Hook Name" {
        TYPE "hook"
        DESCRIPTION "Situation that draws PCs into action"
        TAGS ["combat", "intrigue", "exploration"]
    }

    # Optional lightweight rules specific to this frame
    RULES {
        RULE rule_name ADDS_TO PARENT {
            # Frame-specific rule
        }
    }
}
```

**Fields:**
- `FrameID`: Unique identifier
- `DEPENDS_ON`: Required BASE system
- `USES_SETTING`: Optional SETTING reference for world-building context
- `STARTING_CONDITIONS`: Character creation modifications
- `DEF`: NPC definitions with mechanical stats
- `ENTRY`: Adventure hooks and GM guidance
- `RULES`: Lightweight frame-specific rules

**Example:**

```
FRAME "RichFrogFrame" {
    NAME "Rich Frog Chronicles"
    VERSION "0.1.0"
    DEPENDS_ON "L5R5e"
    USES_SETTING "RichFrog"

    THEMES {
        "Trade and espionage at the crossroads"
        "Duty to clan versus personal ambition"
    }

    STARTING_CONDITIONS {
        DESCRIPTION "PCs are newly assigned samurai sent to represent their clan's interests in the City of the Rich Frog"
        MODIFICATIONS {
            status RANGE(20, 35)
            glory RANGE(10, 25)
        }
    }

    #ide_tadaji ^"Ide Tadaji" DEF {
        EXTENDS ^"Adversary"
        PROPERTIES {
            ^"Role" STRING "Unicorn Trade Governor"
            ^"Description" STRING "Affable merchant-diplomat who controls the city's official commerce"
            ^"Rings" DEF {
                ^"Air"   INTEGER 4
                ^"Water" INTEGER 3
            }
            ^"Skills" DEF {
                ^"Social" INTEGER 4
                ^"Trade"  INTEGER 5
            }
            ^"Honor" INTEGER 35
        }
    }

    ENTRY ^"Missing Shipment" {
        TYPE "hook"
        DESCRIPTION "A valuable Unicorn trade caravan has vanished between Rich Frog and Dragonfly lands"
        TAGS ["investigation", "travel"]
    }

    ENTRY ^"The Forger's Mark" {
        TYPE "hook"
        DESCRIPTION "Documents bearing an impossibly perfect copy of the governor's seal are circulating in the Licensed Quarter"
        TAGS ["intrigue", "investigation"]
    }
}
```

### ARC — Playable Adventure

An ARC is a self-contained, playable narrative experience. It may span part of a session or multiple sessions and represents most standalone published adventure modules. An ARC requires a BASE system and contains SCENE blocks organized by a FLOW.

```
ARC "ArcID" {
    NAME "Human-readable Arc Name"
    VERSION "1.0.0"
    DEPENDS_ON "BaseSystemID"
    USES_SETTING "SettingID"        # optional
    USES_EXTENSION "ExtensionID"    # optional, repeatable

    THEMES {
        "Theme description"
    }

    CAST {
        FROM "FrameID" INCLUDE [#npc_id1, #npc_id2]
        FROM ARC "OtherArcID" INCLUDE [#npc_id3]

        #new_npc ^"New NPC" DEF {
            EXTENDS ^"Adversary"
            PROPERTIES {
                ^"Role" STRING "Role in this arc"
                ^"Description" STRING "Brief description"
                # stats as typed fields
            }
        }
    }

    LOCATION ^"Location Name" {
        DESCRIPTION "Description"
        FROM SETTING "SettingID"    # references a SETTING location
    }

    FLOW {
        PHASE ^"Phase Name" {
            DESCRIPTION "What this phase represents"
            PACING "Suggested pacing guidance"

            SCENE_REF #scene_id
            SCENE_REF #another_scene_id
        }
    }

    SCENE ^"Scene Name" #scene_id {
        TYPE "Roleplay"
        LOCATION #location_ref
        DESCRIPTION "Scene overview for the GM"

        PREREQUISITES {
            # Gating conditions
        }

        OBJECTIVES {
            REQUIRED "Primary goal"
            OPTIONAL "Secondary goal"
        }

        CHECKS {
            CHECK ^"Check Name" {
                SKILL "skill_name"
                RING "ring_name"
                TN 2
                ON_SUCCESS "What happens"
                ON_FAILURE "What happens"
            }
        }

        CLUES {
            CLUE ^"Clue Name" {
                DESCRIPTION "What the PCs learn"
                DISCOVERED_BY "How they find it"
            }
        }

        RESOLUTIONS {
            RESOLUTION ^"Outcome Name" {
                CONDITION "What triggers this outcome"
                OUTCOME "What happens"
                LEADS_TO [#next_scene_id]
            }
        }
    }

    REWARDS {
        XP_BASE 3
        CONDITIONAL_REWARDS {
            REWARD "Condition description" {
                XP 1
            }
        }
    }
}
```

**Fields:**
- `ArcID`: Unique identifier
- `DEPENDS_ON`: Required BASE system
- `USES_SETTING`: Optional SETTING reference
- `USES_EXTENSION`: Optional EXTENSION dependencies (repeatable)
- `CAST`: NPC roster — imported via FROM or defined inline
- `LOCATION`: Place definitions, optionally referencing a SETTING
- `FLOW`: Scene sequencing grouped into PHASEs
- `SCENE`: Individual narrative/gameplay units (see Scene Block Specification)
- `REWARDS`: XP and outcome-based rewards

**Example:**

```
ARC "LostWriter" {
    NAME "The Lost Writer of Rich Frog"
    VERSION "0.1.0"
    DEPENDS_ON "L5R5e"
    USES_SETTING "RichFrog"

    THEMES {
        "Art as resistance versus art as duty"
        "The hidden cost of perfection"
    }

    CAST {
        FROM "RichFrogFrame" INCLUDE [#ide_tadaji]

        #doji_fumiko ^"Doji Fumiko" DEF {
            EXTENDS ^"Adversary"
            PROPERTIES {
                ^"Role" STRING "Missing calligrapher and secret author"
                ^"Description" STRING "A Crane artisan who disappeared while visiting the city. She has been writing a seditious play in hiding."
                ^"Rings" DEF {
                    ^"Air"  INTEGER 3
                    ^"Fire" INTEGER 4
                }
                ^"Skills" DEF {
                    ^"Artisan" INTEGER 5
                    ^"Social"  INTEGER 3
                }
                ^"Honor" INTEGER 55
            }
        }

        #bayushi_koto ^"Bayushi Koto" DEF {
            EXTENDS ^"Adversary"
            PROPERTIES {
                ^"Role" STRING "Scorpion fixer pursuing the manuscript"
                ^"Description" STRING "A charming Scorpion agent tasked with acquiring Fumiko's manuscript before it embarrasses the Crane"
                ^"Rings" DEF {
                    ^"Air"  INTEGER 4
                    ^"Fire" INTEGER 3
                }
                ^"Skills" DEF {
                    ^"Social"  INTEGER 4
                    ^"Martial" INTEGER 3
                }
                ^"Honor" INTEGER 25
            }
        }
    }

    LOCATION ^"The Ink-Stained Room" #ink_room {
        DESCRIPTION "A hidden workshop above a Leatherworkers' Road shop, cluttered with drafts, brushes, and stolen ink"
    }

    FLOW {
        PHASE ^"The Commission" {
            DESCRIPTION "PCs receive their assignment and begin investigating"
            PACING "1-2 scenes, establishing tone"

            SCENE_REF #commission
            SCENE_REF #market_inquiry
        }

        PHASE ^"The Trail" {
            DESCRIPTION "Investigation deepens, rival agents emerge"
            PACING "2-3 scenes, rising tension"

            SCENE_REF #ink_trail
            SCENE_REF #scorpion_encounter
        }

        PHASE ^"The Choice" {
            DESCRIPTION "PCs find Fumiko and must decide her fate"
            PACING "1-2 scenes, climax"

            SCENE_REF #hidden_workshop
            SCENE_REF #final_confrontation
        }
    }

    SCENE ^"The Commission" #commission {
        TYPE "Roleplay"
        LOCATION ^"Licensed Quarter"
        DESCRIPTION "A Crane dignitary hires the PCs to locate a missing calligrapher last seen in the city"

        OBJECTIVES {
            REQUIRED "Accept the commission and learn basic details about Doji Fumiko"
            OPTIONAL "Negotiate terms for additional compensation"
            OPTIONAL "Detect the Crane patron's hidden anxiety about what Fumiko may be writing"
        }

        CHECKS {
            CHECK ^"Read the Patron" {
                SKILL "social"
                RING "air"
                TN 3
                ON_SUCCESS "The patron is hiding something — they fear the content of Fumiko's work, not just her safety"
                ON_FAILURE "The patron seems genuinely worried about a missing artist"
            }
        }

        CLUES {
            CLUE ^"Last Known Location" {
                DESCRIPTION "Fumiko was last seen purchasing unusual ink near Leatherworkers' Road"
                DISCOVERED_BY "Provided freely by the patron"
            }
            CLUE ^"The Patron's Fear" {
                DESCRIPTION "The Crane clan is worried about a manuscript, not just a missing person"
                DISCOVERED_BY "Successful TN 3 Air/Social check"
            }
        }

        RESOLUTIONS {
            RESOLUTION ^"Eager Acceptance" {
                CONDITION "PCs accept without pressing for details"
                OUTCOME "Begin investigation with limited information"
                LEADS_TO [#market_inquiry]
            }
            RESOLUTION ^"Suspicious Acceptance" {
                CONDITION "PCs detect the patron's hidden agenda"
                OUTCOME "Begin investigation knowing the manuscript is the true target"
                LEADS_TO [#market_inquiry, #ink_trail]
            }
        }
    }

    SCENE ^"The Hidden Workshop" #hidden_workshop {
        TYPE "Intrigue"
        LOCATION #ink_room
        DESCRIPTION "PCs discover Fumiko's hiding place and must confront her about her work"

        PREREQUISITES {
            MINIMUM_CLUES 3
            COMPLETED_SCENES [#ink_trail]
        }

        OBJECTIVES {
            REQUIRED "Locate Fumiko and learn the truth about her manuscript"
            OPTIONAL "Read the manuscript and understand its significance"
        }

        CONFLICT {
            TYPE "intrigue"
            STAKES "Whether Fumiko's art survives or is destroyed"
            OPPONENTS [#bayushi_koto]
        }

        RESOLUTIONS {
            RESOLUTION ^"Protect the Artist" {
                CONDITION "PCs side with Fumiko and help her escape or publish"
                OUTCOME "Fumiko's work survives; Crane and Scorpion are displeased"
                LEADS_TO [#final_confrontation]
            }
            RESOLUTION ^"Duty First" {
                CONDITION "PCs return Fumiko to the Crane"
                OUTCOME "Fumiko is silenced; PCs earn Crane favor but lose something intangible"
                LEADS_TO [#final_confrontation]
            }
            RESOLUTION ^"Scorpion Bargain" {
                CONDITION "PCs negotiate with Bayushi Koto"
                OUTCOME "The manuscript changes hands; consequences ripple outward"
                LEADS_TO [#final_confrontation]
            }
        }
    }

    REWARDS {
        XP_BASE 3
        CONDITIONAL_REWARDS {
            REWARD "Protected Fumiko's artistic freedom" {
                XP 1
            }
            REWARD "Resolved the situation without violence" {
                XP 1
            }
            REWARD "Discovered all clues" {
                XP 1
            }
        }
    }
}
```

### CAMPAIGN — Multi-Arc Story

A CAMPAIGN collects multiple ARCs into a long-form narrative. It defines progression between arcs, recurring characters, and overarching themes.

```
CAMPAIGN "CampaignID" {
    NAME "Human-readable Campaign Name"
    VERSION "1.0.0"
    DEPENDS_ON "BaseSystemID"
    USES_SETTING "SettingID"    # optional
    USES_FRAME "FrameID"       # optional

    THEMES {
        "Overarching theme"
    }

    RECURRING_CAST {
        FROM FRAME "FrameID" INCLUDE [#npc_id]
        FROM ARC "ArcID" INCLUDE [#npc_id]
    }

    # Arc sequence with FROM references
    FROM ARC "ArcID1"
    FROM ARC "ArcID2"
    FROM ARC "ArcID3"

    PROGRESSION {
        BETWEEN "ArcID1" AND "ArcID2" {
            DOWNTIME "Duration and activities available"
            ADVANCEMENT "What characters gain between arcs"
        }
    }
}
```

**Fields:**
- `CampaignID`: Unique identifier
- `DEPENDS_ON`: Required BASE system
- `USES_SETTING`: Optional SETTING reference
- `USES_FRAME`: Optional FRAME reference for campaign scaffolding
- `RECURRING_CAST`: NPCs that persist across arcs
- `FROM ARC`: References to constituent arcs in sequence
- `PROGRESSION`: Downtime and advancement between arcs

**Example:**

```
CAMPAIGN "RichFrogChronicles" {
    NAME "Rich Frog Chronicles"
    VERSION "0.1.0"
    DEPENDS_ON "L5R5e"
    USES_SETTING "RichFrog"
    USES_FRAME "RichFrogFrame"

    THEMES {
        "Power and influence at the crossroads of empires"
        "The personal cost of duty across a career"
    }

    RECURRING_CAST {
        FROM FRAME "RichFrogFrame" INCLUDE [#ide_tadaji]
        FROM ARC "LostWriter" INCLUDE [#bayushi_koto]
    }

    FROM ARC "LostWriter"
    FROM ARC "SilkAndSteel"
    FROM ARC "FrogsFall"

    PROGRESSION {
        BETWEEN "LostWriter" AND "SilkAndSteel" {
            DOWNTIME "Three months pass. PCs may pursue personal projects or train."
            ADVANCEMENT "PCs gain 5 XP and one new distinction reflecting events of the first arc"
        }
        BETWEEN "SilkAndSteel" AND "FrogsFall" {
            DOWNTIME "A full year passes. Political tensions escalate across Rokugan."
            ADVANCEMENT "PCs gain 8 XP, increase status by 5, and receive a new assignment"
        }
    }
}
```

### Scene Block Specification

A SCENE represents a single narrative or gameplay unit within an ARC. Scenes can also be defined standalone within an EXTENSION for reuse across arcs.

#### Scene Types

```
ENUM ["Roleplay", "Combat", "Intrigue", "Travel", "Montage"]
```

- **Roleplay** — Exposition, social interaction, NPC dialogue
- **Combat** — Skirmish, duel, mass battle
- **Intrigue** — Social conflict with structured momentum and objectives
- **Travel** — Journey between locations with hazards and encounters
- **Montage** — Multiple brief sub-moments summarized (training, time passage)

#### Scene Structure

```
SCENE ^"Scene Name" #scene_id {
    TYPE "SceneType"
    LOCATION #location_ref
    DESCRIPTION "GM-facing overview"

    PREREQUISITES {
        MINIMUM_CLUES count
        COMPLETED_SCENES [#scene_id, #scene_id]
        CONDITION "Custom gating expression"
    }

    OBJECTIVES {
        REQUIRED "Primary goal description"
        OPTIONAL "Secondary goal description"
    }

    CHECKS {
        CHECK ^"Check Name" {
            SKILL "skill_name"
            RING "ring_name"
            TN target_number
            RING_TN "ring_name" target_number   # optional, repeatable (v0.5, 2026-09-23)
            APPROACH "approach_name"       # optional
            ALTERNATIVE {                  # optional, repeatable (v0.5, 2026-09-23)
                SKILL "skill_name"
                TN target_number
                RING_TN "ring_name" target_number
            }
            ON_SUCCESS "Result description"
            ON_FAILURE "Result description"
        }
    }

    CLUES {
        CLUE ^"Clue Name" {
            DESCRIPTION "What the PCs learn"
            DISCOVERED_BY "How they find it"
        }
    }

    CONFLICT {
        TYPE "combat" | "intrigue"
        STAKES "What is at risk"
        OPPONENTS [#npc_ref, #npc_ref]
    }

    RESOLUTIONS {
        RESOLUTION ^"Outcome Name" {
            CONDITION "What triggers this outcome"
            OUTCOME "What happens"
            LEADS_TO [#next_scene_id]
        }
    }

    # Only for TYPE "Montage"
    MONTAGE {
        MOMENT ^"Moment Name" {
            DESCRIPTION "Brief sub-moment"
        }
    }
}
```

#### Section Details

**PREREQUISITES** — Gating conditions that must be met before the scene becomes available.
- `MINIMUM_CLUES`: Integer count of clues the PCs must have discovered
- `COMPLETED_SCENES`: List of scene IDs that must have been played
- `CONDITION`: Freeform gating expression for custom logic

**OBJECTIVES** — Goals for the PCs within the scene.
- `REQUIRED`: Must be addressed for the scene to reach a resolution
- `OPTIONAL`: Bonus goals that enrich the experience

**CHECKS** — Specific mechanical rolls the scene may call for.
- `SKILL`: The skill used for the check. Repeat it when the text allows either of several skills
  at the same TN (*"a TN 1 Medicine or Skulduggery check"*).
- `RING`: The ring or attribute used — **only when the text requires that one**. A check that
  allows any ring states no `RING`; never record one the text does not name. Repeat it when the
  text allows either of several (*"a TN 2 Games [Water or Air] check"*).
- `TN`: Target number for success — when `RING_TN` lines follow, the TN for any ring they do not name
- `RING_TN` *(v0.5, 2026-09-23)*: the TN for one named ring, where the text gives rings their own
  TNs. One line per ring, as printed: *"a TN 3 Fitness check (Earth 1, Fire 4)"* is `TN 3`,
  `RING_TN "Earth" 1`, `RING_TN "Fire" 4` (L5R5e core p. 297: *"a TN of 4 if the character uses
  their Fire Ring … a TN of only 1 if the character uses their Earth Ring … and a TN of 3 for any
  other ring"*).
- `APPROACH`: Optional specific approach (system-dependent)
- `ALTERNATIVE { … }` *(v0.5, 2026-09-23)*: a second way to make the same check that the text
  offers in the same breath with its own skill, TN or ring TNs — *"a TN 3 Aesthetics (Air 2) or
  TN 2 Skulduggery (Earth 1) check"* is `SKILL "Aesthetics"`, `TN 3`, `RING_TN "Air" 2` and
  `ALTERNATIVE { SKILL "Skulduggery" TN 2 RING_TN "Earth" 1 }`. It takes `SKILL`, `RING`, `TN`
  and `RING_TN`; the outcomes are the check's.
- `ON_SUCCESS` / `ON_FAILURE`: Narrative consequences — **only those the text states**; a check
  whose failure the text leaves open has no `ON_FAILURE`.

**CLUES** — Discoverable information.
- `DESCRIPTION`: What the PCs learn
- `DISCOVERED_BY`: Method of discovery (free, check result, NPC interaction)

**CONFLICT** — Combat or intrigue encounter parameters.
- `TYPE`: Either `"combat"` or `"intrigue"`
- `STAKES`: What the conflict determines
- `OPPONENTS`: NPC references from the CAST

**RESOLUTIONS** — Multiple possible outcomes for the scene.
- `CONDITION`: What triggers this resolution
- `OUTCOME`: Narrative result
- `LEADS_TO`: List of scene IDs that become available

**MONTAGE** — Only valid in scenes with `TYPE "Montage"`. Contains brief sub-moments.

#### Standalone Scenes

Scenes can be defined outside an ARC for reuse as encounter templates:

```
EXTENSION "EncounterPack" EXTENDS "L5R5e" {
    NAME "Rich Frog Encounters"
    VERSION "0.1.0"

    SCENE ^"Roadside Duel" #roadside_duel {
        TYPE "Combat"
        DESCRIPTION "A traveling ronin challenges a PC to a formal duel at a crossroads shrine"

        OBJECTIVES {
            REQUIRED "Survive the duel"
            OPTIONAL "Win the duel honorably without lethal force"
        }

        CONFLICT {
            TYPE "combat"
            STAKES "Honor and reputation"
        }

        RESOLUTIONS {
            RESOLUTION ^"Honorable Victory" {
                CONDITION "PC wins without killing the ronin"
                OUTCOME "Gain 5 glory and the ronin's respect"
            }
            RESOLUTION ^"Lethal Victory" {
                CONDITION "PC kills the ronin"
                OUTCOME "Gain 3 glory but lose 5 honor"
            }
            RESOLUTION ^"Defeat" {
                CONDITION "PC loses the duel"
                OUTCOME "Lose 5 glory but the ronin spares the PC"
            }
        }
    }
}
```

### Location Block Specification

A LOCATION defines a named place that can be used across SETTING, FRAME, and ARC containers. Locations support nesting for hierarchical geography.

```
LOCATION ^"Location Name" #location_id {
    DESCRIPTION "Physical and atmospheric description"
    TAGS ["tag1", "tag2"]
    FROM SETTING "SettingID"    # optional: inherits from a SETTING location

    LOCATION ^"Sub-Location" #sub_id {
        DESCRIPTION "Nested location"
    }
}
```

**Fields:**
- `^"Location Name"`: Caret-quoted display name
- `#location_id`: Optional hash ID for cross-referencing
- `DESCRIPTION`: GM-facing description
- `TAGS`: Categorical tags (e.g., `"urban"`, `"dangerous"`, `"sacred"`)
- `FROM SETTING`: Links this location to a SETTING-defined location, inheriting its properties
- Nested `LOCATION` blocks: Sub-locations within this location

#### Cross-Referencing Locations

Locations defined in a SETTING can be referenced from FRAME or ARC containers:

```
# In a SETTING
SETTING "RichFrog" {
    LOCATION ^"Licensed Quarter" #licensed_quarter {
        DESCRIPTION "The regulated commercial district"
    }
}

# In an ARC
ARC "LostWriter" {
    USES_SETTING "RichFrog"

    SCENE ^"Market Inquiry" #market_inquiry {
        LOCATION #licensed_quarter    # references the SETTING location
    }
}
```

### Cross-Container References

Containers reference each other using three mechanisms: `DEPENDS_ON`, `USES_*`, and `FROM`.

**DEPENDS_ON** — Declares a required BASE system dependency:
```
DEPENDS_ON "BaseSystemID"
```
Used by: FRAME, ARC, CAMPAIGN, EXTENSION (with optional VERSION)

**USES_SETTING** — References a SETTING for world-building context:
```
USES_SETTING "SettingID"
```
Used by: FRAME, ARC, CAMPAIGN

**USES_FRAME** — References a FRAME for campaign scaffolding:
```
USES_FRAME "FrameID"
```
Used by: CAMPAIGN

**USES_EXTENSION** — References an EXTENSION for additional mechanical content:
```
USES_EXTENSION "ExtensionID"
```
Used by: ARC

**FROM** — Cross-container import:
```
FROM "FrameID" INCLUDE [#npc_id1, #npc_id2]
FROM ARC "ArcID" INCLUDE [#npc_id]
FROM FRAME "FrameID" INCLUDE [#npc_id]
FROM SETTING "SettingID"
FROM ARC "ArcID"
```

**LEADS_TO** — Scene transitions within RESOLUTION blocks:
```
LEADS_TO [#scene_id1, #scene_id2]
```

### Dependency Hierarchy

Containers form an acyclic dependency graph:

```
SETTING (system-agnostic, .setting files)
    ^
    | USES_SETTING
    |
FRAME (.frame) ---------> BASE (.ttrpg)
    ^                        ^
    | USES_FRAME             | DEPENDS_ON
    |                        |
CAMPAIGN (.campaign) --> ARC (.arc) --> EXTENSION (.ttrpg)
                          |
                          | contains
                          v
                        SCENE blocks
```

#### Dependency Rules

1. **SETTING** has no dependencies — it is system-agnostic and self-contained
2. **FRAME** requires exactly one BASE via `DEPENDS_ON` and optionally one SETTING via `USES_SETTING`
3. **ARC** requires exactly one BASE via `DEPENDS_ON`, optionally one SETTING via `USES_SETTING`, and optionally one or more EXTENSIONs via `USES_EXTENSION`
4. **CAMPAIGN** requires exactly one BASE via `DEPENDS_ON`, optionally one SETTING, and optionally one FRAME via `USES_FRAME`
5. **Cycles are forbidden** — no container may directly or transitively depend on itself
6. **SCENE** blocks exist within ARCs or within EXTENSIONs (as standalone reusable encounters)
7. Cross-references via `FROM` must target containers that are already declared as dependencies (via `DEPENDS_ON`, `USES_SETTING`, `USES_FRAME`, or `USES_EXTENSION`)

---

## 17. Worked Examples

Three brief examples showing the same grammar accommodating very different systems.

### L5R5e — Schools, Techniques, Curriculum

```
BASE "L5R5e_Core" {
    NAME "Legend of the Five Rings 5th Edition"
    VERSION "0.3"
    RELEASE_DATE "2026-03-01"

    # ============= Character Template =============

    #L5R001aB2cD ACTOR "Entity" DEF {
        PROPERTIES {
            ^"Name" STRING REQUIRED
        }
    }

    #L5R003xY4zA ACTOR "Samurai" DEF {
        EXTENDS #L5R001aB2cD ^"Entity"
        PROPERTIES {
            REF OF ^"Clan" REQUIRED
            REF OF ^"School"
            ^"School Rank" INTEGER MIN 1 MAX 6 DEFAULT 1
            ^"Honor" INTEGER MIN 0 MAX 100
            ^"Glory" INTEGER MIN 0 MAX 100
            ^"Status" INTEGER MIN 0 MAX 100
            ^"Rings" DEF {
                ^"Air" INTEGER MIN 1 MAX 5 DEFAULT 1
                ^"Earth" INTEGER MIN 1 MAX 5 DEFAULT 1
                ^"Fire" INTEGER MIN 1 MAX 5 DEFAULT 1
                ^"Water" INTEGER MIN 1 MAX 5 DEFAULT 1
                ^"Void" INTEGER MIN 1 MAX 5 DEFAULT 1
            }
            ^"Skills" LIST OF ^"Skill"
            ^"Techniques" LIST OF ^"Technique"
        }
        RULES {
            #L5R004jK5lM: WHEN [^"Samurai" CREATED] THEN REQUIRE ^"Clan", ^"School"
            #L5R005uV6wX: WHEN [^"Strife" > ^"Composure"] THEN ^"Samurai" IS compromised
        }
    }

    # ============= Rings & Skills =============

    ^"Skill" DEF {
        APPLIES TO [^"Samurai", ^"Adversary"]
        INTEGER MIN 0 MAX 5
    }

    ^"Air" DEF {
        APPLIES TO [^"Samurai", ^"Adversary"]
        INTEGER MIN 1 MAX 5
    }

    # ============= Schools =============

    ^"Hida Defender" DEF {
        EXTENDS ^"School"
        APPLIES TO [^"Samurai"]
        PROPERTIES {
            ^"Clan" REF ^"Crab" FIXED
            ^"Roles" LIST ["Bushi", "Guardian"]
            ^"Starting Honor" INTEGER DEFAULT 40
            ^"Starting Skills" LIST OF ^"Skill"
        }

        SCHOOL_ABILITY "Way of the Crab" {
            "Ignore the Cumbersome quality of armor you wear."
        }

        STARTING_TECHNIQUES {
            KATA ^"Lord Hida's Grip"
            KATA CHOOSE 1 [^"Striking as Earth", ^"Striking as Water"]
        }

        CURRICULUM {
            RANK 1 {
                SKILL_GROUP "Martial Skills"
                SKILL "Command"
                SKILL "Medicine"
                TECHNIQUE_GROUP "Rank 1 Kata"
                ^"Rushing Avalanche Style" [kata]
            }
            RANK 6 {
                ^"The Mountain Does Not Fall"
            }
        }

        MASTERY_ABILITY ^"The Mountain Does Not Fall" {
            "At the beginning of your turn, you may spend 1 Void point..."
        }

        STARTING_OUTFIT [
            "Lacquered armor", "traveling clothes",
            "daishō (katana and wakizashi)",
            "tetsubō or ōtsuchi", "knife", "traveling pack"
        ]
    }

    # ============= Techniques =============

    ^"Crimson Leaves Strike" DEF {
        EXTENDS ^"Technique"
        PROPERTIES {
            ^"Type" STRING "Kata"
            ^"Rank" INTEGER 3
        }
        ACTIVATION "As an Attack action, make a TN 4 Martial Arts (Earth) check..."
        EFFECTS {
            "If you succeed, target suffers physical damage equal to your Earth Ring plus bonus successes."
        }
        OPPORTUNITIES {
            "Earth (op): Your target cannot guard until the end of their next turn."
        }
    }
}
```

### VTM5e — Disciplines, Powers, Amalgams

```
BASE "VTM5e_Core" {
    NAME "Vampire: The Masquerade 5th Edition"
    VERSION "0.3"
    RELEASE_DATE "2026-03-01"

    # ============= Character Template =============

    #VnK8MrPxWb ACTOR "Entity" DEF {
        PROPERTIES {
            ^"Name" STRING REQUIRED
        }
    }

    #X3yZ5aB7cD ACTOR "Kindred" DEF {
        EXTENDS #VnK8MrPxWb ^"Entity"
        PROPERTIES {
            REF OF ^"Clan" REQUIRED
            ^"Generation" INTEGER MIN 4 MAX 16
            ^"Hunger" INTEGER MIN 0 MAX 5 DEFAULT 1
            ^"Humanity" INTEGER MIN 0 MAX 10 DEFAULT 7
            ^"Attributes" DEF {
                ^"Strength" INTEGER MIN 1 MAX 5 DEFAULT 1
                ^"Dexterity" INTEGER MIN 1 MAX 5 DEFAULT 1
                ^"Stamina" INTEGER MIN 1 MAX 5 DEFAULT 1
                ^"Charisma" INTEGER MIN 1 MAX 5 DEFAULT 1
                ^"Manipulation" INTEGER MIN 1 MAX 5 DEFAULT 1
                ^"Composure" INTEGER MIN 1 MAX 5 DEFAULT 1
                ^"Intelligence" INTEGER MIN 1 MAX 5 DEFAULT 1
                ^"Wits" INTEGER MIN 1 MAX 5 DEFAULT 1
                ^"Resolve" INTEGER MIN 1 MAX 5 DEFAULT 1
            }
            ^"Disciplines" LIST OF ^"Discipline"
        }
        RULES {
            #vtm001abc: WHEN [^"Hunger" >= 5] THEN ^"Kindred" IS starving
            #vtm002def: WHEN [^"Humanity" == 0] THEN ^"Kindred" IS lost_to_the_beast
        }
    }

    # ============= Blood Potency =============

    ^"Blood Potency" DEF {
        APPLIES TO [^"Kindred"]
        INTEGER MIN 0 MAX 10
        RULES {
            #vtm010xyz: blood_potency_determines_surge_bonus
            #vtm011abc: blood_potency_restricts_feeding
        }
    }

    # ============= Disciplines =============

    ^"Dominate" DEF {
        EXTENDS ^"Discipline"
        CHARACTERISTICS {
            TYPE "Mental"
            MASQUERADE_THREAT "Low"
            BLOOD_RESONANCE "Phlegmatic"
        }

        POWERS {
            LEVEL_1 ["Cloud Memory", "Compel"]
            LEVEL_2 ["Mesmerize", "Dementation"]
            LEVEL_3 ["The Forgetful Mind", "Submerged Directive"]
            LEVEL_4 ["Rationalize"]
            LEVEL_5 ["Mass Manipulation", "Terminal Decree"]
        }

        AMALGAMS {
            "Dementation" REQUIRES ^"Dominate" >= 2 AND ^"Obfuscate" >= 2
        }
    }

    ^"Cloud Memory" DEF {
        EXTENDS ^"Discipline Power"
        PROPERTIES {
            ^"Level" INTEGER 1
            ^"Parent" REF ^"Dominate"
        }
        COST "Free"
        DICE_POOL "Charisma + Domination vs. Wits + Resolve"
        DURATION "Indefinitely"
        SYSTEM "By speaking the phrase 'Forget!' the user can make a mortal forget the past few moments. No new memories are formed and the missing time is left a haze..."
    }

    # ============= Clans =============

    ^"Brujah" DEF {
        EXTENDS ^"Clan"
        PROPERTIES {
            ^"Clan Name" STRING "Brujah" FIXED
            ^"In-Clan Disciplines" LIST OF ^"Discipline" [^"Celerity", ^"Potence", ^"Presence"]
        }
        TRIGGER ^"Bestial Failure"
        RULES {
            #bruj001: brujah_frenzy_bonus
        }
    }
}
```

### Ars Magica 5e — Arts, Spells, Virtues

This sketch demonstrates the spec handling a third, very different system — one with a fundamentally different magic framework — without any base spec changes.

```
BASE "ArM5e_Core" {
    NAME "Ars Magica 5th Edition"
    VERSION "0.1"
    RELEASE_DATE "2026-03-01"

    # ============= Character Template =============

    #ARM001 ACTOR "Magus" DEF {
        EXTENDS ^"Character"
        PROPERTIES {
            ^"Name" STRING REQUIRED
            REF OF ^"House" REQUIRED
            ^"Age" INTEGER MIN 25
            ^"Techniques" DEF {
                ^"Creo" INTEGER MIN 0 DEFAULT 0
                ^"Intellego" INTEGER MIN 0 DEFAULT 0
                ^"Muto" INTEGER MIN 0 DEFAULT 0
                ^"Perdo" INTEGER MIN 0 DEFAULT 0
                ^"Rego" INTEGER MIN 0 DEFAULT 0
            }
            ^"Forms" DEF {
                ^"Animal" INTEGER MIN 0 DEFAULT 0
                ^"Aquam" INTEGER MIN 0 DEFAULT 0
                ^"Auram" INTEGER MIN 0 DEFAULT 0
                ^"Corpus" INTEGER MIN 0 DEFAULT 0
                ^"Herbam" INTEGER MIN 0 DEFAULT 0
                ^"Ignem" INTEGER MIN 0 DEFAULT 0
                ^"Imaginem" INTEGER MIN 0 DEFAULT 0
                ^"Mentem" INTEGER MIN 0 DEFAULT 0
                ^"Terram" INTEGER MIN 0 DEFAULT 0
                ^"Vim" INTEGER MIN 0 DEFAULT 0
            }
            ^"Virtues" LIST OF ^"Virtue"
            ^"Flaws" LIST OF ^"Flaw"
            ^"Known Spells" LIST OF ^"Spell"
        }
    }

    # ============= Virtues & Flaws =============

    ^"Gentle Gift" DEF {
        EXTENDS ^"Virtue"
        PROPERTIES {
            ^"Type" STRING "Hermetic" FIXED
            ^"Cost" STRING "Major" FIXED
        }
        DESCRIPTION "Your Gift does not cause the usual penalties to social interactions."
    }

    ^"Blatant Gift" DEF {
        EXTENDS ^"Flaw"
        PROPERTIES {
            ^"Type" STRING "Hermetic" FIXED
            ^"Cost" STRING "Major" FIXED
        }
        DESCRIPTION "Your Gift is especially disturbing to mundanes."
    }

    # ============= Spells =============

    ^"Voice" DEF {
        EXTENDS ^"Range"
        PARAMETERS { ^"spell" OF ^"Spell" }       # the spell cast at this Range comes in
        PROPERTIES {
            ^"Magnitudes" TRANSFORM ADD 2          # and gains 2 magnitudes
        }
    }

    ^"Pilum of Fire" DEF {
        EXTENDS ^"Formulaic Spell"
        PROPERTIES {
            ^"Technique" REF ^"Creo" FIXED
            ^"Form" REF ^"Ignem" FIXED
            ^"Level" INTEGER 20
            ^"Range" REF ^"Voice"
            ^"Duration" REF ^"Momentary"
            ^"Target" REF ^"Individual"
        }
        LEVEL_CALCULATION {
            BASE 10
        }
        DESCRIPTION "A 2-foot, thick, spear-shaped jet of fire flies from your palms, doing +15 damage to the individual it hits."
    }

    # ============= Lab Activities =============

    ^"Lab Total" DEF {
        APPLIES TO [^"Magus"]
        FORMULA "Technique + Form + Intelligence + Magic Theory + Aura"
        RULES {
            #arm050: lab_total_determines_seasonal_progress
        }
    }
}
```

All three systems use only base-spec grammar (`DEF`, `EXTENDS`, `PROPERTIES`, `APPLIES TO`, `RULES`, etc.) plus their own system-defined vocabulary (`CURRICULUM`, `AMALGAMS`, `LEVEL_CALCULATION`, etc.). No base spec changes are needed per system.

---

## 18. Narrative Container Keywords (Reference)

These keywords are reserved by the base spec for use within narrative containers:

**SETTING:** `THEMES`, `HISTORY`, `ENTRY`, `PERIOD`

**FRAME:** `STARTING_CONDITIONS`, `MODIFICATIONS`, `RANGE`

**ARC:** `CAST`, `FLOW`, `PHASE`, `SCENE_REF`, `REWARDS`, `XP_BASE`, `CONDITIONAL_REWARDS`, `REWARD`, `XP`

**SCENE:** `TYPE`, `PREREQUISITES`, `MINIMUM_CLUES`, `COMPLETED_SCENES`, `CONDITION`, `OBJECTIVES`, `REQUIRED`, `OPTIONAL`, `CHECKS`, `CHECK`, `SKILL`, `RING`, `TN`, `RING_TN`, `ALTERNATIVE`, `APPROACH`, `ON_SUCCESS`, `ON_FAILURE`, `CLUES`, `CLUE`, `DISCOVERED_BY`, `CONFLICT`, `STAKES`, `OPPONENTS`, `RESOLUTIONS`, `RESOLUTION`, `OUTCOME`, `MONTAGE`, `MOMENT`

**LOCATION:** `TAGS`

**CAMPAIGN:** `RECURRING_CAST`, `PROGRESSION`, `BETWEEN`, `AND`, `DOWNTIME`, `ADVANCEMENT`

**Cross-container:** `DEPENDS_ON`, `USES_SETTING`, `USES_FRAME`, `USES_EXTENSION`, `FROM`, `INCLUDE`, `LEADS_TO`

---

## 19. Versioning *(v0.4)*

Three distinct version axes, kept separate:

- **DSL-spec version** — the version of *this specification* (v0.4). Files pin the spec they target via `SPEC_VERSION`.
- **File content `VERSION`** — the version of a file's game content (semantic or date-based), independent of the spec version.
- **Directory organization** — systems organize files under a content-version directory (e.g. `0.3/`, `1.0/`). Version lives in the directory, not re-encoded redundantly in every filename.

`DEPENDS_ON "Parent" VERSION "x"` pins a required parent *content* version. Tooling treats `SPEC_VERSION` as the conformance target.

### Editions & version namespaces *(v0.4)*

An **edition** (or a major/beta version line) is an **identity namespace**. Hash identity is **stable
within** it and carries **no identity across** it: an edition change is a **breaking change**, so "the
same" entity in a newer edition is a *new* definition with a *new* hash (§5), not an overlay on the
old one. Editions are therefore kept as **separate systems** — e.g. `arm5e` (Ars Magica 5th) vs.
`armdef` (the Definitive edition), or a system's beta lines vs. its final rules. Within one edition,
core + sourcebooks + errata share the namespace and compose by precedence (§13).

The spec's **dice module** (§8) is the one thing shared across editions. It is edition-neutral: every
edition includes it, and its hashes are the same in each.

**Forward-porting.** A sourcebook published for an older edition does **not** automatically apply to a
newer one — it references the old edition's hashes. To use it under a newer edition, generate a **new
`.ttrpg` of that sourcebook converted to the newer edition**, targeting the newer edition's
definitions and diffs — a derived artifact, not an automatic overlay.

The machine-readable edition diff this presupposes is a **`.bridge` file (§21)** — the one container
with two dependency lineages, holding a *directed* correspondence between two namespaces. A bridge
does not weaken the rule above: it asserts correspondence, explicitly and third-party, precisely
because identity does not carry. (The generator that consumes a bridge to emit the derived artifact
remains future work.)

## 20. Validation *(v0.4)*

Validation of `.ttrpg`/`.lore` files has two levels, both operating on the files themselves:

1. **Lint — spec adherence.** Does the file conform to this grammar/spec (structure, types, reserved-word usage, canonical forms)? One source of truth: the linter is derived from / checked against the grammar.
2. **Coherence / consilience — referential integrity.** Across **an edition's** corpus: is everything referenced actually defined? Do `^"Name"`, `#hash`, `EXTENDS`, `APPLIES TO`, `DEPENDS_ON` resolve to real, correctly-typed targets — **and unambiguously** (§5d)? No **dangling** anchors, and **no hash shared by two *different* entities**. (A hash *recurring* across files is a legal override (§13, DECISION-4), not a duplicate — so coherence is scoped to one edition and treats consistent recurrence as override, not error. *Note: the current `ttrpg_validator.py` still flags all recurrence as a duplicate-anchor error; scoping it to inconsistent-recurrence is a pending change — see `titterpig-mastra/TASKS.md`.*)

**The modification system is part of coherence** *(v0.4, 2026-07-25)*. A `MODIFY` / `OVERRIDE`
naming a target that does not exist modifies nothing, silently and permanently — rename the parent
definition, or mistype the target, and the overlay simply stops applying with no diagnostic. So
every `MODIFY ^"X"` / `OVERRIDE ^"X"` target must resolve in the loaded corpus (**error** if not),
alongside the per-directive rules in §13: `SET` against an undeclared property and `ADD_TO` /
`REMOVE_FROM` against a non-`LIST` are errors; a colliding `ADD`, a `REMOVE_FROM` of an absent
value, and an enum narrowed out from under a live instance are warnings.

**What counts as "defined."** Name resolution collects `^"Name" DEF` (including nested and `ADD`-ed
ones), `ACTOR` / `TEMPLATE` definitions, and `ALIAS` names — and nothing else. A bare
`^"Name" { … }` block declares no name: §5 is the only spelling of a definition, and a caret that
opens a statement without `DEF` resolves nothing. Frozen pre-0.4 content directories (§19) that
still use the old spelling are historical artifacts and are not expected to validate against this
spec version.

**Intentional exceptions:** both levels honor `FIAT` (§8) — a value or element marked `FIAT "reason"` is exempt from the findings it would otherwise raise (constraint violations and, cascading, completeness). Because each `FIAT` carries a reason, the full set is reportable for audit.

**Out of scope for the DSL:** *sophisticated rules validation* (evaluating whether game rules are internally consistent or produce legal characters) runs **downstream**, in the tools that consume `.ttrpg`/`.lore`, and is built later. The DSL guarantees a well-formed, coherent knowledge base — not a rules engine.

### Bridges — two-corpus coherence *(v0.4)*

A `.bridge` file (§21) is the one container whose references span **two** edition namespaces, so
coherence for it is checked against **two** corpora, not one:

- An `ORIGIN`-side caret reference must resolve in the **origin** edition's corpus.
- A `DESTINATION`-side caret reference must resolve in the **destination** edition's corpus.
- Neither side is checked against the other, and a bridge's own definitions (its declared
  dispositions, its guidance entry labels) belong to **neither** edition — they are file-local.

The validator is therefore given a corpus per edition id:

```bash
python3 ttrpg_validator.py bridges/0.5/ \
    --corpus dnd5e="…/titterpig-dsl-dnd5e/0.5" \
    --corpus dnd5.5e="…/titterpig-dsl-dnd5.5e/0.5"
```

A side declared `EXTERNAL "reason"` (§21) has no titterpig corpus, so its references cannot be
resolved; they are counted and reported, never silently passed. A side that is **not** `EXTERNAL` and
has **no** `--corpus` mapping is an **error**: an unchecked cross-edition reference is exactly the rot
a bridge exists to prevent, and "not checked" must never read as "checked and fine."

**Untyped referents.** A bridge slot may name its referent with a plain string instead of a caret
reference, for things the target corpus has no `DEF` for (§21). Those are not gated — but if an
untyped referent's text *would* have resolved to a real entity on its declared side, the validator
raises a **warning**, so quoting cannot be used to dodge the reference gate.

---

## 21. BRIDGE — Cross-Edition Conversion *(v0.4)*

§19 makes an edition an **identity namespace**: hash identity is stable within it and carries none
across it. §13 scopes a composition set to one edition namespace, and §20 scopes coherence to one
edition. Every container defined above has exactly **one** dependency lineage.

A published *edition-conversion document* — "Converting to SRD 5.2.1", Ars Magica 5th's "Appendix I:
Fourth Edition Conversion" — asserts precisely the thing §19 forbids inside a namespace: **this
older-edition thing became that newer-edition thing.** It inherently has **two** lineages. That is
the structural gap `.bridge` fills. It is *not* an `EXTENSION` (one lineage), *not* the §13
`MODIFY`/`OVERRIDE`/`ADD` errata system (same edition, and errata *corrects* where a bridge
*corresponds*), and *not* `FIAT` (which waives a check rather than recording a fact).

A bridge does **not** re-establish identity across editions. It records a **directed, third-party
assertion of correspondence** between two independent namespaces — an edition diff, machine-readable.
§19's forward-porting note ("a derived artifact, not an automatic overlay") describes the *output* of
consuming a bridge; the bridge is the input that makes that generation possible.

### Directed, not symmetric

`ORIGIN` and `DESTINATION` are **mandatory** and the direction is **load-bearing**. A bridge is
**not reversible by inspection**: `Duergar → use Spy` does not invert (Spy did not become Duergar),
several origin entities may collapse onto one destination entity, and a `DESTINATION`-only unit
("this rule is new") has no origin to run back to. A tool that wants the reverse direction needs a
separately authored bridge, not an inversion of this one.

### File-level structure

```
BRIDGE "FileID" {
    NAME "Converting to System Reference Document 5.2.1"
    VERSION "2025.1"
    SPEC_VERSION "0.4"
    RELEASE_DATE "2025-04-22"

    ORIGIN      "dnd5e"    VERSION "0.4"
    DESTINATION "dnd5.5e"  VERSION "0.4"

    DISPOSITIONS { … }     # the vocabulary this document uses
    ALIASES      { … }     # names this document uses that its editions do not
    CONVERSION   { … }     # the mechanizable correspondences and dispositions
    GUIDANCE     { … }     # prose, taggable with what it concerns
}
```

`ORIGIN` / `DESTINATION` name an **edition id** (the system id under which that edition's corpus
lives, §19), optionally pinning a content `VERSION`. A side with no titterpig corpus is declared
`EXTERNAL` with a **required reason**, exactly as `FIAT` requires one:

```
ORIGIN "arm4" VERSION "4" EXTERNAL "No titterpig corpus exists for Ars Magica Fourth Edition."
```

**Placement.** A `.bridge` file MUST NOT live inside either edition's corpus directory — its origin
names would not resolve there and its presence would pollute that edition's namespace. Bridges live
outside both corpora, named `<origin>-to-<destination>-<specver>-<document>.bridge`: in the canonical
DSL repo's `bridges/<specver>/`, or in a system repo's `bridges/<specver>/`, **beside** that edition's
corpus directory and never inside it *(2026-09-29)* — the Pendragon 5e→6e bridge sits in
`titterpig-dsl-pendragon6e/bridges/0.5/`, next to `0.5/`. Wherever it lives, a bridge is listed in the
canonical `bridges/sources.json` and validated in two-corpus mode.

### Sided references

Every reference in a bridge is **side-qualified**; the side is never inferred. It comes either from
the enclosing slot keyword (`ORIGIN`, `DESTINATION`) or from an explicit inline qualifier
(`SCOPE DESTINATION ^"Barbarian"`, `CONCERNS [ ORIGIN ^"Virtue", DESTINATION ^"Virtue" ]`).

A referent is one of two things:

- **Typed** — `^"Name"`, a caret reference. **Gated** (§20): it must resolve in that side's corpus.
- **Untyped** — `"Name"`, a plain string, for a thing the target corpus has no `DEF` for (a
  subsystem, a section, a procedure: "Tiers of Play", "Character Generation"). **Not gated**, but the
  validator warns if it *would* have resolved, so this is not an escape hatch from the gate.

Prefer typed. An untyped referent is a statement that the corpus has nothing to point at. Where the
corpus *does* have the entity but under a different name than the document uses, declare an `ALIAS`
(below) rather than leaving the reference untyped.

### DISPOSITIONS — the document's own vocabulary

A conversion document declares what its change-tags mean; the bridge declares them too rather than
inventing a spec-wide vocabulary, because the vocabularies differ per document. Each is a `DEF`, so
`DISPOSITION` references resolve through ordinary coherence (§20) — a tag that was never declared is
an error, not a typo that survives.

```
DISPOSITIONS {
    ^"New Name" DEF {
        ^"Description" STRING "New Name. This tag is applied to a rule that has a new name. Unless stated otherwise, the rule hasn't changed apart from its name."
    }
    ^"Revised Rule" DEF { … }
}
```

**A disposition is a SET, not a single value.** Documents compose tags
(`Magic Action [New Name, Revised Rule]`), so `DISPOSITION` always takes a list.

### ALIASES — when the document and the edition disagree

A conversion document is written *about* two editions, not generated from them, and real ones name
things the edition they describe does not. SRD 5.2.1's own conversion guide calls a Warlock feature
`Contract Patron`; the SRD it describes calls it `Contact Patron`. Neither silently retyping the
reference nor leaving it untyped is right: the first loses the document's wording, the second loses a
correspondence that genuinely exists.

`ALIASES` reconciles the two, reusing §5b's `ALIAS` with a side qualifier:

```
ALIASES {
    # Publisher typo: the SRD 5.2.1 feature is "Contact Patron".
    ALIAS ^"Contract Patron" FOR DESTINATION ^"Level 9: Contact Patron"
}
```

The alias name is then **resolvable on that side** — `DESTINATION ^"Contract Patron"` gates clean —
so units keep the document's own vocabulary while the alias records, machine-readably, which entity
that vocabulary denotes. As in §5b it is a naming statement only: same entity, no value change. The
`FOR` target is gated like any other sided reference; an alias to nothing is an error.

Reserve it for genuine document/edition disagreement. It is **not** a way to make a wrong
correspondence resolve, and it is not the tool for a name the edition simply has no `DEF` for — that
is an untyped referent.

### CONVERSION — the mechanizable part

Three unit kinds. Each carries `TEXT` — the source's own statement of the change, **verbatim**.

#### MAP — one correspondence

```
MAP {
    ORIGIN      ^"Flying Sword"
    DESTINATION ^"Animated Flying Sword"
    DISPOSITION [ ^"New Name", ^"Revised Rule" ]
    TEXT "Animated Flying Sword (formerly Flying Sword)"
}
```

Fields, all optional except `DISPOSITION` and at least one of `ORIGIN` / `DESTINATION`:

| Field | Meaning |
|---|---|
| `ORIGIN` | Referent(s) in the origin edition. A bare list is side-qualified by the slot. |
| `DESTINATION` | Referent(s) in the destination edition. |
| `SCOPE` | A sided reference situating the correspondence — the entity these referents belong to. Required where a name is only unique within a parent (`Epic Boon` exists under twelve classes). |
| `ASPECT` | A free string naming the *part* of the entity the disposition is about ("Starting Equipment", "Weapon Proficiencies"). Untyped by nature: a sub-part often has no `DEF`. |
| `DISPOSITION` | The tag set, as caret references into `DISPOSITIONS`. |
| `TEXT` | The source's verbatim statement. |

**One MAP asserts exactly one correspondence.** When both sides carry more than one referent the
correspondence is **joint** — `[^"Stillness of Mind", ^"Purity of Body"] → [^"Self-Restoration"]` is
one merge, not two renames. Lists on only one side are unambiguous either way (six new features with
no origin are six independent facts however you read them), so no distributive marker is needed.

A `MAP` covers, with no extra vocabulary:

| Source shape | Shape in the bridge |
|---|---|
| Rename — *Warrior Veteran (formerly Veteran)* | 1 origin → 1 destination |
| Revision in place — *Rage [Revised Rule]* | same name on both sides |
| Substitution — *Duergar (use Spy)* | 1 → 1, lossy; `DISPOSITION [^"Omitted Rule"]` |
| Merge — *Silk Rope and Hemp Rope … into … Rope* | N origins → 1 destination |
| Split — *the Search action and the new Study action* | 1 origin → N destinations |
| Introduction — *Sorcerous Burst* | destination only |
| Omission — *Vehicle proficiency has been removed* | origin only |
| Restructure — *Incubus (no longer a Succubus variant)* | 1 → 1 with `SCOPE` / `TEXT` recording it |

Substitution is **not** a rename and must not be modelled as one: it is lossy and many-to-one (five
5.1 monsters collapse onto three 5.2.1 replacements). The `Omitted Rule` disposition is what
distinguishes them; a consumer that treats them alike will silently mangle content.

#### REMAINDER — a bulk disposition over what is not listed

```
REMAINDER {
    SCOPE ORIGIN ^"Monster"
    DISPOSITION [ ^"Revised Rule" ]
    TEXT "All monsters not listed above have revisions to their presentations and statistics."
}
```

This is essential, not a convenience: without it you cannot tell **"unmentioned means unchanged"**
from **"unmentioned means not covered"** — the same job `dispositionRules` do in a coverage manifest.
A `REMAINDER` applies its disposition to every member of `SCOPE` on that side that no `MAP` in this
bridge names.

`EXHAUSTIVE BOOLEAN` (default `true`) records whether the source claims the disposition for *all*
unlisted members or hedges. `"All monsters not listed above …"` is exhaustive; `"Most magic items not
listed above …"` is not, and a consumer must treat the latter as a presumption requiring a per-entity
check rather than a fact.

#### PROCEDURE — carrying a character's values across

`MAP` corresponds *entities*. A `PROCEDURE` converts the *values on a sheet* — the table-facing half
of the problem, and all that some conversion documents contain.

```
PROCEDURE {
    SUBJECT ORIGIN ^"Ability"
    TEXT "**Abilities:** Leave at the old value, and multiply remaining XP by five. Spread the XP from removed Abilities among the replacements, as desired."
    CONVERT ORIGIN ^"Ability" UNCHANGED INTO DESTINATION ^"Ability"
    CONVERT ORIGIN ^"Experience Points" SCALE 5 INTO DESTINATION ^"Using Experience Points"
    CONVERT ORIGIN ^"Experience Points" MANUAL "Spread the XP from removed Abilities among the replacements, as desired."
}
```

A `CONVERT` is `CONVERT <sided-ref> <operation> [INTO <sided-ref>]`. The operation vocabulary is
closed — the DSL guarantees a knowledge base, not a rules engine (§20), so this is deliberately not
an expression language:

| Operation | Meaning |
|---|---|
| `UNCHANGED` | The value carries across as-is. |
| `SCALE n [OVER d]` | Multiply by `n`, optionally divided by `d`. `SCALE 5` (×5); `SCALE 1 OVER 3` (÷3); `SCALE 6 OVER 5` (+20%). |
| `RESTATE` | Take the destination edition's printed value; the old one is discarded. |
| `MANUAL "instruction"` | Requires human judgement. The instruction is the source's own words, verbatim. |

`INTO` retargets: `CONVERT ORIGIN ^"Twilight Points" SCALE 1 OVER 3 INTO DESTINATION ^"Warping Score"`.

`MANUAL` is how a procedure records that the source **delegates to the reader** without pretending it
mechanized something it did not. It is the honest encoding of "Convert each Virtue or Flaw to its new
status" — and it stays in `CONVERSION`, not `GUIDANCE`, because it is keyed to a named field.

### GUIDANCE — prose, taggable

Free prose in the manner of a `.lore` file, but carrying machine-readable tags for what it concerns.

```
GUIDANCE {
    ENTRY ^"Character Generation" {
        TOPICS   [ "Character Generation" ]
        CONCERNS [ ORIGIN ^"Virtue", ORIGIN ^"Flaw", DESTINATION ^"Virtue", DESTINATION ^"Flaw" ]
        TEXT """
        First, Virtues and Flaws no longer have point values; they are split into Major and Minor. …
        """
    }
}
```

- An `ENTRY`'s caret is a **local label**, not a reference — it names the passage so a consumer can
  link to it. Conventionally it is the source heading.
- `CONCERNS` holds sided references and **goes through the same gate as conversion rules** (§20). A
  guidance tag naming an entity that does not exist is silent rot; it is checked, not trusted.
- **Guidance may name both sides.** "Virtues and Flaws no longer have point values" concerns the
  origin's virtues *and* the destination's. There is no default side and none is inferred — that
  would let an origin-side typo resolve against the destination corpus and disappear. Name every
  side you mean.
- `TOPICS` holds free strings for subsystem-scale subjects with no `DEF` to point at ("Character
  Generation", "Combat", "Using This Guide"). Ungated by design; `CONCERNS` carries whatever *is*
  typed. Using `TOPICS` where a `DEF` exists is the same warning as an untyped referent.

### Rules or guidance? — the boundary

> If it asserts a **correspondence or disposition about a named referent**, it is a conversion rule.
> If it **explains why, or tells a human how to decide**, it is guidance.

Real documents blur this constantly, and one source unit legitimately produces both. `Barbarian Class
Features [New Rule]` is a disposition, a paragraph, and a list of six features: the six features
become six `MAP`s carrying the paragraph verbatim as `TEXT`; the chapter's framing prose becomes a
`GUIDANCE` entry. The test is not the prose's length — it is whether a tool could *act* on it. A
sentence a tool can act on belongs in `CONVERSION` even when it is wrapped in explanation; a sentence
that only a person can act on belongs in `GUIDANCE` even when it names entities (tag them with
`CONCERNS`).

Content that is a **style rule for the destination edition** rather than a correspondence — SRD
5.2.1's ~60-category capitalization list — is guidance. It maps nothing; it tells an author how the
destination edition presents its terms. Keeping it out of the mapping grammar is deliberate.

### Consuming a bridge

A bridge is a knowledge base, not a program. What it makes possible:

1. **Auditing** an origin-edition artifact — which of its entities are renamed, revised, substituted,
   or omitted downstream, and which are covered only by a `REMAINDER`.
2. **Generating** the derived forward-port §19 describes, with every generated correspondence
   traceable to a source unit's verbatim `TEXT`.
3. **Refusing** to do either silently: a non-`EXHAUSTIVE` `REMAINDER`, a `MANUAL` `CONVERT`, and an
   `Omitted Rule` substitution are each a machine-readable "a human must look at this."

---

## 22. Guidance *(v0.5, DECISION-8)* — the `GUIDANCE` block

Guidance is prose *about* the mechanics that is neither a `DESCRIPTION` rule (deterministic/structural)
nor `.lore` flavor (opaque, no assumed structure). Most **sidebars** are guidance. It reuses the BRIDGE
`GUIDANCE` construct (§21), now also legal in a DEF body and at module level in a `.ttrpg`.

```
GUIDANCE {
    ENTRY ^"local-label" #hash? {
        CONCERNS [ ^"Entity", … ]      # what it guides; optional inside a DEF (⇒ the enclosing DEF)
        TOPICS   [ "topic", … ]         # optional free-text tags
        TEXT     "verbatim guidance prose"
    }
}
```

- The `ENTRY` caret is a **local label** for the passage, not a reference.
- `CONCERNS` refs resolve like any caret ref (hash-qualified allowed). A consumer detects "guidance
  available for X" by X appearing in some `CONCERNS`. `TEXT` is verbatim.
- Distinct from `.lore` (no tool assumes structure in it) and from `DESCRIPTION` (the entry's own rules).

## 23. Conditional emit hooks *(v0.5, DECISION-9)* — the `HOOKS` block + `FORMALITY`

A hook makes *visible* that a narrative situation has an otherwise-untracked mechanical consequence. It
is **stand-off** (it annotates, never mutates, the verbatim `DESCRIPTION`) and is **not a rules engine**.

```
HOOKS {
    HOOK #hash? {
        FORMALITY CONDITIONAL
        WHEN "the amulet is removed or damaged before the wound would have healed naturally"
        TRIGGER { ANY [ "amulet removed", "amulet damaged" ] }   # optional structured overlay
        THEN [ #hash ^"Recovery Roll" ]                          # the mechanic(s) implicated
    }
}
```

- **`FORMALITY`** declares *how formal this hook is* — an ordered ladder, least→most machine-actionable:
  `PROSE` (readable sentence only) · `TAGGED` (prose + resolvable `THEN` refs, condition unparsed) ·
  `CONDITIONAL` (a light structured `TRIGGER` — subjects/states, `||`/`&&` — plus refs) · `FORMAL` (a
  complete, evaluable condition→effect). An author uses the **highest level the source supports and no
  higher** — the DSL never demands more rigor than the source offers; consumers dispatch on the level.
- **`WHEN`** is the human-readable condition (a string), present at every level. **`TRIGGER`** is an
  optional structured overlay for `CONDITIONAL`/`FORMAL`; its internal shape is open (as formal as
  authored). **`THEN`** lists the mechanic caret refs implicated (may be empty at `PROSE`).
- Coherence: `FORMALITY` is one of the four levels; every `THEN`/`TRIGGER` ref resolves.

## 24. Optional & variant rules *(v0.5, DECISION-10)* — the `OPTIONAL` marker and `.selections`

An optional/variant rule (a variant combat rule, a creature-scoped option) ships a **default posture**
in-corpus; a saga's actual choices live in a separate `.selections` file.

```
#hash ^"Constriction Attack" DEF {
    EXTENDS ^"Combat Option"
    OPTIONAL {
        DEFAULT off                     # on | off — the shipped posture
        SCOPE [ ^"Dragon" ]            # narrow: types/entities; wide: GLOBAL
        TEXT "Optional rule: a dragon may constrict a grappled opponent…"
    }
    DESCRIPTION "…"
}
```

- `OPTIONAL` marks the enclosing DEF an optional/variant rule. `DEFAULT` is `on`/`off`; `SCOPE` names
  the types/entities it applies to, or the literal `GLOBAL` for a wide rule. The DEF's `#hash` is how a
  `.selections` file names it.

### `.selections` files

A `.selections` file records a corpus's / campaign's user choices, as a DSL container so it round-trips
through the same parser and validator:

```
SELECTIONS "my_saga" {
    NAME "…"   VERSION "…"   SPEC_VERSION "0.5"   RELEASE_DATE "…"
    FOR "arm5e" VERSION "0.5"
    SELECT #hash on  "optional provenance note"
    SELECT #otherHash off
}
```

- Each `SELECT` names an `OPTIONAL` DEF's `#hash` and a posture (`on`/`off`); the validator checks the
  hash resolves to a DEF that carries an `OPTIONAL` block. A consumer reads corpus + `.selections` to
  know the active rule set. Generating/editing `.selections` interactively is a downstream tool, not
  part of the DSL.

---

## 25. CODEX — Lore Knowledge Graph *(v0.5, DECISION-12)*

A `.codex` file is a **stand-off knowledge graph over `.lore` prose**: typed entities, a declared
relationship vocabulary, and a category taxonomy, all *derived from* the narrative but stored *beside*
it. The `.lore` body stays byte-verbatim and opaque (§2); the codex points **into** it and never edits
it. It is the structured, queryable companion to free prose — the same "mirror, don't duplicate" split
as `.ttrpg`↔`.lore`, applied to world facts (who a person is, where a place sits, how factions relate).

**Why a container, not `.lore` structure.** The query test (§2) routes anything a tool looks something
up in into a structured container; a fact graph is exactly that. A separate file preserves the `.lore`
"opaque body" contract and leaves every existing `.lore` file untouched. Inline wiki-markup in the
prose is rejected for the same reason as DECISION-7: it mutates verbatim narrative and forces every
consumer to parse the body.

### File-level structure

```
CODEX "FileID" {
    NAME "…"  VERSION "…"  SPEC_VERSION "0.5"  RELEASE_DATE "…"
    [DEPENDS_ON "SchemaCodexID" VERSION "…"]   # import a shared ontology
    [FOR EDITION "tor2e"]                        # edition whose DEFs categories/objects may resolve against

    [SOURCES { … }]       # derived-provenance manifest (which prose, which versions)
    CATEGORIES { … }      # the type taxonomy (schema)
    RELATIONS  { … }      # the predicate vocabulary (schema)
    ENTITY … { … }        # nodes + edges (data)
}
```

A codex may be **schema-only** (just `CATEGORIES`/`RELATIONS`, imported by others via `DEPENDS_ON`),
**data-only** (just `ENTITY` blocks, depending on a schema codex), or **combined**. This mirrors the
BASE/EXTENSION split: the schema is the reusable base, per-book graphs depend on it.

A single logical graph may also be **physically split** across many codex files that share one schema
and one entity namespace: a lightweight **parent** carries the `SOURCES` manifest and edition-spanning
anchor entities, and **section files** (per book, per chapter) hold the rest. Because an entity is a
first-class caret target, any section resolves `^"Name"` to any other, and a section may **amend** a
node introduced elsewhere (see the amend rule under ENTITY). This keeps each file small while the
consumer reads them as one graph.

### SOURCES — the derived-provenance manifest

A codex is *derived from* prose, so it records its inputs. The optional header block lists which files
(or books), at which versions, the graph was built from:

```
SOURCES {
    "l5r5e-0.5-courts-of-stone-crane-clan.lore" VERSION "0.4.1"
    "Emerald Empire" VERSION "0.4" AT "l5r5e-0.5-emerald-empire-history.lore"
}
```

Each entry is a source label — a `.lore` path or a book name — with an optional `VERSION` and an
optional `AT "<path>"` that pins the specific prose file when the label is a book. The block is
provenance/manifest metadata; it does not itself assert graph facts (those are `ENTITY` blocks whose
`SOURCE … AT` bind individual nodes into the prose). On a split graph it lives in the parent and grows
as each book is folded in.

`FOR EDITION` (optional) names the edition namespace (§19) whose DEFs a category or relationship object
may resolve to (`IS ^"Hobbit"` → that edition's culture DEF). Absent it, carets resolve within the
codex and any co-validated corpus.

### CATEGORIES — the type taxonomy

```
CATEGORIES {
    ^"Place"       DEF {}
    ^"Settlement"  DEF { EXTENDS ^"Place" }
    ^"Ruined City" DEF { EXTENDS ^"Settlement" }
}
```

Each category is a `DEF` (§5): it may carry a `#hash`, may `EXTENDS` a parent (the taxonomy is a DAG),
and lives in the corpus symbol table. A category name may instead be an **existing game DEF**
(`^"Hobbit"`, `^"Scorpion Clan"`); `IS` resolves against categories and DEFs alike, so lore taxonomy
and mechanical types **unify** without a separate layer.

### RELATIONS — the declared predicate vocabulary

Every relationship predicate MUST be declared before use. **An undeclared predicate is a coherence
error** — this is what makes the graph robust rather than a synonym swamp (`located-in` vs `in` vs
`inside`).

```
RELATIONS {
    ^"located-in" { INVERSE ^"contains"  DOMAIN ^"Place"  RANGE ^"Place"  TRANSITIVE }
    ^"lives-in"   { INVERSE ^"residents" DOMAIN ^"Person" RANGE ^"Place"  }
    ^"bordered-by"{ SYMMETRIC             DOMAIN ^"Place"  RANGE ^"Place"  }
}
```

Predicate qualifiers, all optional:

- **`INVERSE ^"name"`** — the reverse edge, tool-derivable; declaring it lets a consumer answer both
  directions from one asserted fact (assert `A located-in B`, read back `B contains A`). `INVERSE` and
  `SYMMETRIC` are mutually exclusive (declaring both is an **error**).
- **`DOMAIN ^"Category"` / `RANGE ^"Category"`** — the expected subject / object category. A fact
  whose endpoints violate domain/range **WARNs** (the source is often looser than the taxonomy; not an
  error).
- **`SYMMETRIC`** — the edge is its own inverse (`bordered-by`).
- **`TRANSITIVE`** — a consumer may chain the edge (`A located-in B`, `B located-in C` ⟹
  `A located-in C`). Declarative only: the DSL asserts facts, it does not compute closures.

### ENTITY — nodes and edges

```
ENTITY #hash ^"Name" {
    IS ^"Category" [ ^"Category2" … ]                  # one or more; ≥1 required
    [SOURCE "<lore-file>" [AT "<heading-slug>"]]       # provenance into the prose
    RELATIONSHIPS {
        ^"predicate" -> ^"Object" [FROM "<surface text>"]
        …
    }
}
```

- **`#hash`** — opaque, ≥16 chars (§5). An entity is a first-class caret target: any file in
  the corpus resolves `^"Name"` to it, so **entity→entity links are ordinary caret refs** and are
  coherence-checked like any other reference. **Amend across files (§13).** A node is *canonically*
  defined once — the first `ENTITY #hash ^"Name"` that introduces it. A later section file may
  **re-state `ENTITY #hash ^"Name"`** (same hash, same name) to add `SOURCE` bindings and
  `RELATIONSHIPS` as further books describe the same subject; the consumer merges the re-statements by
  hash into one node. This recurrence is **legal and expected** (multiple sources enriching one entry).
  What stays an **error** is a hash mapped to *two different* entity names, or a hash shared between a
  codex entity and any other anchor — those are genuine collisions, not amends.
- **`IS`** — one or more categories (multi-typing is common: a place that `IS ^"City" ^"Capital"`).
  Each must resolve to a declared `CATEGORY` or an in-corpus DEF; an unresolved `IS` is an **error**
  (it is the type system).
- **`SOURCE … AT`** — binds the entity to the `.lore` file and heading that describes it, by path and
  GitHub-style heading slug. The one structural assumption made about the prose body is heading text:
  a slug matching no heading **WARNs**. `SOURCE` is optional (some entities are named only in passing).
- **`RELATIONSHIPS`** — the entity's outgoing edges. Each line is `^"predicate" -> ^"Object"
  [FROM "surface"]`, reusing the §5c arrow and surface-form. The predicate MUST be declared in a
  `RELATIONS` block in scope (**error** otherwise). The object caret **should** resolve to an entity,
  DEF, or category; an unresolved object **WARNs** — facts derived from prose routinely name things
  not yet modeled, the same tolerance as bridge untyped referents (§21). `FROM` records the verbatim
  source phrase the fact was derived from, making the edge auditable against the `.lore`; it is
  advisory provenance (substring-checked against the prose only by a verifier that loads the `.lore`).

### Validation summary

| Check | Level |
|---|---|
| `IS` resolves to a `CATEGORY` or in-corpus DEF | **error** |
| relationship predicate declared in a `RELATIONS` block | **error** |
| `#hash` opaque, ≥16 chars | **error** if <16 |
| `#hash` reused for a *different* entity name, or shared with a non-entity anchor | **error** |
| `#hash` re-stated for the *same* entity name across files (amend, §13) | allowed |
| category `EXTENDS` parent resolves | **error** |
| `INVERSE` + `SYMMETRIC` on one predicate | **error** |
| relationship object caret resolves | warn |
| `DOMAIN` / `RANGE` respected by an edge | warn |
| `SOURCE` / `AT` slug matches a `.lore` heading | warn |

### Relationship to other containers

- **`.lore`** — the prose the codex is derived from; untouched, opaque body.
- **`.setting`** (§16) — hand-authored structured world-building (LOCATION / FACTION / HISTORY). A
  codex may reference `.setting` DEFs as categories or objects. The difference is intent: `.setting`
  is authored canon, a `.codex` is a fact graph *extracted* from prose. They coexist and cross-reference.
- **`REFERENCES` (§5c)** — the same stand-off arrow/surface-form pattern, applied to world entities
  rather than in-`DESCRIPTION` mechanics.

---

**Spec Version:** 0.5
**Last Updated:** 2026-08-08
**Status:** Canonical (supersedes v0.4)
