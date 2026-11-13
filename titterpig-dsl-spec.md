# Titterpig DSL Specification v0.5

> **Status: v0.5 (current, canonical).** Supersedes v0.4 (which superseded v0.3); superseded
> versions live in this repo's git history. `AUTHORING-GUIDELINES.md` holds authoring
> best-practices for system-specific content. The
> `ttrpg.peg` grammar states the syntax and `check_grammar.py` runs it: every good fixture in this
> repo is accepted and every planted syntax fault refused (§20). Validation is split:
> `ttrpg_validator.py` lints spec adherence, while `check_references.py` and `check_constructs.py` coherence-check the v0.5
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
6. **`EMPHASIS` takes a kind, and `LABEL`** *(§5c, DECISION-19)* — `EMPHASIS BOLD { … }`,
   `EMPHASIS ITALIC { … }` and `EMPHASIS BOLD ITALIC { … }` say how a marked span is set; a bare
   `EMPHASIS { … }` stays legal. `LABEL { … }` names a run-in label, and `LABEL 2 { … }` one at
   depth 2. Markdown emphasis inside a string (`**…**`, `*…*`) is flagged: a warning in a file
   below 0.6, an error from 0.6 *(not additive)*.
7. **Embedded references are checked, and may keep a different literal** *(§5c, §14, DECISION-20)*
   — `^\"Enraged\"` inside a string points at a DEF where the text names it, and
   `^\"Enraged\"/\"state of rage\"` points at the DEF and leaves "state of rage" as the text.
   Every one resolves, as any reference does.
8. **`TABLE`** *(new, §5e, DECISION-21)* — a primitive block for a table: `AXIS` lines declare what
   it is looked up by, and `AT [ … ] { … }` gives the result at a coordinate. A table of records
   names its type and `COLUMNS` and holds no cells.
9. **A `FROM` names its container's kind and is itself the declaration** *(§16, DECISION-22; not
   additive)* — `FROM EXTENSION "id" INCLUDE [ #hash ^"Name" ]`. Rule 7's demand that the
   container be declared a second time in the header is withdrawn. A `FROM "id"` with no kind is a
   warning in a file below 0.6 and an error from 0.6.
10. **A scene's type and a conflict's type are entities the system defines** *(§16, DECISION-23;
    not additive)* — `TYPE #hash ^"Investigation"`. The base spec no longer fixes a list of scene
    types. A string in that slot is a warning in a file below 0.6 and an error from 0.6.
11. **What a reference may point at: two tiers** *(§20, DECISION-24)* — a definition (a DEF, an
    `ACTOR`, a `TEMPLATE`, an `ALIAS`, a codex `ENTITY`) is a name every file may use. A named
    block (`SCENE`, `LOCATION`, `ENTRY`) is a target through its hash, and its name is a label
    inside its own file. References between scenes and locations are now checked.
12. **A caret name may hold an escaped quote** *(§14, DECISION-25)* — `^"Mrinmoy \"Vidyapati\"
    Mishra"`. The grammar allowed no escape there and both tools cut such a name short.
13. **A port keeps its source's hashes and names its source** *(§3, §5, §19, DECISION-26)* — a
    file made from another edition's file keeps the hash of everything it carries over, and says
    in its header which file it came from: `ORIGIN "arm5e" EXTENSION "ArM5_Grogs_Abilities"`.
    Anywhere else, a hash that two editions share means nothing.
14. **A definition is replaced only by a statement that names it** *(§5, §13, §20, DECISION-27; not
    additive)* — the implicit override is withdrawn. A DEF's hash stands once in a corpus, and a
    second DEF under it is an error. A later file changes an entity with `OVERRIDE`, `MODIFY` or
    `REPRINT`. No corpus used the implicit form and the validator never accepted it. A DEF of the
    same name under another hash is a second entity and replaces nothing, and a consumer must not
    merge the two.
15. **An `.actor` file is an `EXTENSION` file of instances** *(§2, §3, DECISION-28; not additive)* —
    it opens with the `EXTENSION` wrapper as a `.ttrpg` does, holds one or more instance DEFs, and
    holds nothing else. §2 had called it a standalone single DEF. A file that opens with a bare
    DEF is the older form and the validator warns on it.
16. **A block's keywords are reserved inside that block** *(§15, §18, DECISION-29)* — `SKILL` is a
    SCENE keyword, and outside a scene a system may use the word for a field of its own. The
    file-level, definition, type, modifier, scope, choice and modification keywords are reserved
    everywhere.
17. **A definition's prose is `DESCRIPTION`** *(§10, DECISION-30; not additive)* — `TEXT` is no
    longer an alias for it. `TEXT` is the prose field of an `ENTRY` and of other blocks that are
    not definitions.
18. **The grammar runs** *(§20, DECISION-31)* — `check_grammar.py` reads `ttrpg.peg` and parses
    files with it. The grammar is gated on this repo's fixtures. It now has rules for a keyword
    statement, the narrative containers and hash-qualified lists, and a rule for the words
    reserved everywhere.
19. **The validator checks a value against what its definition extends** *(§5, §5b, §6, §8, §20,
    DECISION-32)* — a range, an `ENUM`, a type, a list's members, a bound reference's
    arguments, a property written twice, and a cycle of `EXTENDS` or of `ALIAS`. `EXTENDS` is
    acyclic. A hash shorter than 16 characters, or with an underscore, is refused from 0.6.
20. **When two names are the same** *(§14, DECISION-33; not additive)* — the same characters,
    once Unicode form, runs of white space and straight or curly quotes are set aside. Case,
    punctuation and accents count. Every tool in this repo compares names this one way.
21. **`REQUIRED` has one meaning** *(§8, DECISION-34)* — every entry of the type has the
    property. The validator checks it for every instance. A rule of character creation is not
    written as `REQUIRED`, and a required `^"Name"` is answered by the DEF's own name.
22. **A version pin means "at least"** *(§3, §19, DECISION-35)* — `DEPENDS_ON "Parent" VERSION
    "x"` says the parent is at version x or later. The validator checks it.
23. **What a file depends on** *(§3, DECISION-36)* — every `DEPENDS_ON` it writes and the id its
    header `EXTENDS`, any number of them. Each names a loaded file, no two files depend on each
    other, and a file id is declared once. An `EXTENSION` names at least one parent.
24. **A dependency loads first** *(§13, DECISION-37)* — the one rule of load order the spec
    states. Any order beyond it is the consumer's, and the spec defines no manifest.

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
  artifact**, not an automatic overlay. *(Amended by DECISION-26: that artifact is a port, and it
  keeps its source's hashes. Amended by DECISION-27: the implicit form is withdrawn.)*

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

- **DECISION-19 — `EMPHASIS` says how a span is set, and a run-in label is a `LABEL`** *(resolved,
  v0.6, 2026-11-12)* (§5c): `EMPHASIS { "…" }` recorded that the source marks a span and had no
  place for which marking. Eight corpora kept the distinction by writing Markdown inside their
  strings instead (about 5,500 strings with `**bold**` and 7,600 with `*italic*`), which §5c
  forbids; Troika sets bold, italic and bold italic in one paragraph, each for a different kind of
  thing. The decision is a kind between the keyword and the brace: `BOLD`, `ITALIC`, or both. A
  block with no kind stays legal, so the 2,721 existing blocks are unchanged. 2,273 of the bold
  spans in those corpora are run-in labels (`Prot:`, `Ease Factor:`), which are structure and not
  stress. They get a block of their own, **`LABEL`**, with an optional depth after the keyword
  (`LABEL 2`), 1 when none is written. Both blocks stay beside the text, as DECISION-7 settled. A
  whole paragraph set in one face (fiction, an epigraph) is **not yet recordable (to-do)**. With a
  place for every marked span, Markdown emphasis inside a string becomes a validator finding: a
  **warning** in a file that declares a `SPEC_VERSION` below 0.6, or none, and an **error** in one
  that declares 0.6 or later. A `FIAT` with its reason excuses asterisks the source itself prints.

- **DECISION-20 — Embedded references stay, are checked, and may keep a different literal**
  *(resolved, v0.6, 2026-11-12; amends DECISION-7)* (§5c, §14): §14 documented `^\"Name\"` inside a
  string while §5c said no markup is ever inserted into the text, and no tool read inside a string.
  l5r5e holds 420 embedded references; 14 pointed at nothing and nothing reported them. The decision
  is that the embedded form stays and becomes a full reference site. `^\"Name\"` cites the DEF where
  the text prints its name. **`^\"Name\"/\"literal\"`** cites the DEF and keeps `literal` as the
  text, for the plural, the inflection or the paraphrase the source prints. A `#hash` may stand
  before the caret. In a triple-quoted string the quotes are written without the backslash. The
  purpose is an index: a tool finds every place a rule's DEF is cited, and the text a reader sees
  is unchanged. A string's **text** is the string with each embedded reference read as its literal,
  or as its name where it has none; verbatim checks and the surface forms of `REFERENCES`,
  `EMPHASIS` and `LABEL` are matched against the text. DECISION-7's stand-off `REFERENCES` block
  stays legal, and emphasis and labels stay beside the text.

- **DECISION-21 — A table is a `TABLE` block with axes and cells** *(resolved, v0.6, 2026-11-12)*
  (§5e): the spec defined no table, and the corpora wrote five kinds: a grid of strings (973
  tables, 12,384 rows, in 13 corpora), pairs of strings, a DEF per row holding a list of cell
  strings, a DEF per cell holding its coordinates as properties, and roll-keyed system blocks. 397
  of the string grids are roll lookups whose range sits in a string (`"3–7"`). The decision is a
  primitive **`TABLE`** block in a DEF's body. `AXIS ^"Name"` declares what the table is looked up
  by: the entities of a type, a range of numbers, any whole number, a roll, or a list. **`AT [ … ]
  { … }`** gives the result at a coordinate, one coordinate per axis; a coordinate may be a range,
  an open range (`MIN n`, `MAX n`) or `ANY`. The result is a block, so it holds whatever the table
  yields: values, a `REF`, a `TRANSFORM`, a further roll, a named DEF. A table of records (a weapon
  list) holds no cells: it names the type as its one axis and lists the type's properties as
  `COLUMNS`, so each value stays on its entity. `TABLE` is a primitive and not a shipped base DEF:
  a table type would carry no data of its own, and the keywords already say what the block is. A
  specified grid of printed strings was considered and not adopted.

- **DECISION-22 — An import is one `FROM` line that names its container's kind** *(resolved, v0.6,
  2026-11-12)* (§16): dependency rule 7 required every `FROM` to target a container already
  declared as a dependency, and gave an ARC no way to declare a frame and nothing a way to declare
  an arc. §16's own ARC example broke the rule, as did 20 of the 22 `FROM` lines in the corpora,
  and no tool checked it. The decision is that the `FROM` line is itself the declaration. It always
  names the kind of container (`FROM EXTENSION`, `FROM FRAME`, `FROM ARC`, `FROM SETTING`), the
  container must be in the loaded set and be of that kind, and each `INCLUDE` item is a reference
  site (§5d). The spelling with no kind, `FROM "id"`, is a warning in a file that declares a
  `SPEC_VERSION` below 0.6, or none, and an error in one that declares 0.6 or later. Three smaller
  rulings came with it. §16's examples carry opaque hashes and its ARC example is the real Lost
  Writer arc from l5r5e. A block's name comes before its hash by convention (`SCENE ^"Name" #hash
  {`), and hash before name is also legal. A skill group is a property of a character, so a
  character's skills are a keyed block of values and not a list of references.

- **DECISION-23 — A scene's type and a conflict's type are entities the system defines**
  *(resolved, v0.6, 2026-11-12)* (§16): §16 fixed scene types to five strings (`"Roleplay"`,
  `"Combat"`, `"Intrigue"`, `"Travel"`, `"Montage"`) and wrote a conflict's as `"combat" |
  "intrigue"`, notation that is not DSL. Two of the five are L5R terms, 60 scenes in the corpora use
  two values that are not on the list (`"Investigation"` 32, `"Exploration"` 28), and nothing
  reported them. The decision is that the base spec fixes no list. A system defines its scene
  types and conflict types as entities, and a scene or a conflict points at one: `TYPE #hash
  ^"Investigation"`. It is a reference site (§5d). Where the source leaves the type open, a
  `CHOOSE` stands in the slot (§5b). A string there is a warning in a file that declares a
  `SPEC_VERSION` below 0.6, or none, and an error in one that declares 0.6 or later.

- **DECISION-24 — Two tiers of target: a definition by name, a named block by its hash**
  *(resolved, v0.6, 2026-11-12)* (§20): §20 said only a DEF, an `ACTOR`, a `TEMPLATE` or an `ALIAS`
  is defined, "and nothing else". §25 called a codex entity a first-class caret target, and §16 had
  scenes point at locations and flows at scenes. The validator followed §25 and the reference gate
  followed §20, and neither resolved a reference between two blocks. The corpora hold 2,007
  `LOCATION` and 497 `SCENE` blocks that 464 references point at, beside 8,187 `ENTRY` blocks whose
  names are labels (245 named `Sidebar 1` in one corpus). 160 places were declared twice, as a
  block and as a DEF, so that a reference could reach them. The decision is two tiers. A
  definition, now including a codex `ENTITY`, is a name every file may use. A named block is a
  target through its hash: referenced as `#hash ^"Name"` from anywhere, with the hash unique in
  the corpus, while its name alone resolves only inside the file that declares it. `SCENE_REF`,
  `LEADS_TO`, `COMPLETED_SCENES`, `OPPONENTS`, a scene's `LOCATION` and an `INCLUDE` item are
  reference sites under §5d and are resolved.

- **DECISION-25 — A caret name may hold an escaped quote** *(resolved, v0.6, 2026-11-12)* (§14):
  the grammar's caret name ran to the first quote and allowed no escape, and both tools read it
  that way. 33 lines in five corpora write a name with a quote in it
  (`^"Mrinmoy \"Vidyapati\" Mishra"`), 31 of them a DEF's own name, so 31 definitions were
  invisible to the validator and to the reference gate. The decision is that `\"` inside a caret
  name is a quote, as it is inside a string.

- **DECISION-26 — A port keeps its source's hashes and declares its source** *(resolved, v0.6,
  2026-11-12)* (§3, §5, §19, §20; amends DECISION-4): §5 said the same entity in another edition
  is "a separate definition with a different hash", and §19 gave arm5e and armdef as its two
  editions. The two cores bear that out: they share no hash, and 1,201 names are defined in both
  under different ones. The 46 sourcebooks are generated. armdef's copies are made from arm5e's,
  and 10,275 of their 10,276 hashed definitions carry the hash and the name they have in arm5e.
  No generated file said so, and a tool could not tell a port from an accident: invisiblesun and
  root share 1,508 hashes, none of them under the same name. The decision is that a port keeps
  the hash of every definition and named block it carries over, and declares the file it was made
  from in its header: `ORIGIN "arm5e" EXTENSION "ArM5_Grogs_Abilities"`. A hash that stands in a
  port and in its origin is one entity carried over, and has the same name in both. A hash that
  two editions share in any other case means nothing.

- **DECISION-27 — No implicit override, by hash or by name** *(resolved, v0.6, 2026-11-12)* (§5, §5d, §13, §20; amends
  DECISION-4): DECISION-4 let a later file replace a definition by restating its hash on a new
  DEF, with no keyword. The validator has reported every such DEF as a duplicate anchor since
  v0.4, and §20 carried a note calling the difference "a pending change". None of the 22 corpus
  directories restates a DEF's hash: 96,571 hashed DEFs, each hash once in its corpus. They write
  their changes out, in 603 `MODIFY` and 355 `REPRINT` statements. The validator knows no load
  order, so it could not have said which of two DEFs under one hash wins, and it could not have
  told a replacement from a DEF pasted twice. The decision is that a DEF's hash stands once in a
  corpus and a second DEF under it is an error. A later file changes an entity only by naming it:
  `OVERRIDE`, `MODIFY`, or `REPRINT`. A named block stated again under its own hash and name, and
  a codex `ENTITY` restated to add sources (§25), stay legal.

  The same decision settles the name. §5d already said two hashes are two entities. The
  synthesist replaced an earlier DEF with a later one of the same name and a compatible type all
  the same: 301 entities and 356 definitions across six compositions, every pair under two
  different hashes. tor2e's core `^"Combat"`, which holds the combat chapter, was replaced by
  Strider Mode's empty `^"Combat" DEF { }`, and the built JSON lost the chapter. A DEF of the same
  name under another hash is a second entity. It replaces nothing, and a consumer must not merge
  the two. A book that means an entity another file defines says so with `REPRINT`, `ALIAS`,
  `MODIFY` or `OVERRIDE`.

- **DECISION-28 — An `.actor` file is an `EXTENSION` file of instances** *(resolved, v0.6,
  2026-11-12)* (§2, §3, §5): §2 called an `.actor` "a `.ttrpg` file scoped to exactly one
  character definition (a single `DEF` block)" and "a standalone file", while §3 has every
  `.ttrpg` open with `BASE` or `EXTENSION`. Of the 3,077 `.actor` files in 13 corpora, 2,407
  open with an `EXTENSION` wrapper and 670 with a bare DEF, and 78 hold more than one DEF: a
  magus at four ages, an adventure's pregenerated characters, a chapter's NPCs. A bare file has
  no header, so it cannot declare a `SPEC_VERSION` or name the system it belongs to. Three
  rulings. An `.actor` always opens with the `EXTENSION` wrapper. It holds one or more DEFs. It
  holds instances only: each DEF extends a type, and a type declaration belongs in a `.ttrpg`.
  The type need not be an `ACTOR` type, since arm5e's creatures and covenants extend plain DEFs.

- **DECISION-29 — A block's keywords are reserved inside that block** *(resolved, v0.6,
  2026-11-12)* (§15, §18): §15 said "only these keywords are reserved" and §18 reserved its list
  "for use within narrative containers", and neither said what the same word is elsewhere. The
  corpora use six of those words as a system's own field outside the block that reserves them:
  `SKILL` on 1,698 lines (l5r5e's curricula), `TRIGGER` on 438, `TYPE` on 317, `TAGS` on 78,
  `THEMES` on 49 and `SOURCE` on 15. The grammar already read them so: 51 of §18's 58 words are
  not grammar keywords. The decision is that a keyword listed under a block (Tables, Hooks,
  Codex, Bridge, the narrative containers) is reserved inside that block, and a system may use
  the word elsewhere. The file-level, definition, type, modifier, scope, choice and modification
  keywords are reserved everywhere.

- **DECISION-30 — A definition's prose is `DESCRIPTION`; `TEXT` is not its alias** *(resolved,
  v0.6, 2026-11-12)* (§10, §22): §10 let a system write `TEXT` for `DESCRIPTION` "when the
  content is mechanical rather than narrative", while §21 to §24 use `TEXT` as the prose field of
  an `ENTRY`. One corpus took up the alias: all 3,513 `TEXT` statements that sit directly in a DEF
  are in draw-steel. The other 21 corpus directories write a DEF's prose as `DESCRIPTION`, on 42,126
  lines, and `MODIFY … SET DESCRIPTION` (§13) names that field. The decision is one name for the
  field. A DEF's prose is `DESCRIPTION`. `TEXT` is the prose field of an `ENTRY` and of other
  blocks that are not definitions. `TEXT` directly in a DEF is a warning in a file that declares a
  `SPEC_VERSION` below 0.6, or none, and an error from 0.6.

- **DECISION-31 — The grammar is run, and gated on the fixtures** *(resolved, v0.6, 2026-11-12)*
  (§20): no tool read `ttrpg.peg`. Its `UPPER_IDENT` rule ended in `!{RESERVED_WORD}`, which is
  not PEG notation and named a rule that did not exist. Run for the first time, it accepted 13
  of this repo's 35 good fixture files and 1,350 of the 7,055 DSL files in the corpora, and it
  refused `DESCRIPTION "x"` in a DEF: the optional label of a keyword statement took the string
  and left the statement no value. The decision is that the grammar is run.
  `check_grammar.py` is a packrat interpreter for the grammar's notation, with no dependency.
  It refuses a grammar that names an undefined rule or holds an unreachable one. The grammar
  must accept every good fixture in this repo and refuse every planted syntax fault in
  `tests/grammar-bad`. The corpora are measured and not gated: after the repairs the grammar
  accepts 5,157 of 7,055 files. Three points of syntax are now stated by the grammar. The
  arguments of a keyword statement begin on the keyword's line. The words reserved everywhere
  are one rule, `RESERVED_WORD`, and include the openers of the annotation blocks. A list may
  be empty.

- **DECISION-32 — The validator checks what §5 and §8 say is checked** *(resolved, v0.6,
  2026-11-12)* (§5, §5b, §6, §8, §20): §5 said "coherence validation checks each value against
  the constraint inherited from the actor type", and §5b called three faults of a bound
  reference coherence errors. The validator checked none of them: of 24 violations planted one
  to a file, it reported one. The decision adds six groups of checks. A cycle of `EXTENDS` or of
  `ALIAS`, and a bound reference that does not fit its base's `PARAMETERS`, are errors at every
  version; no corpus has one. An `INTEGER` outside the `MIN` / `MAX` it inherits, a value
  outside the `ENUM` it inherits, a value of another kind than its type, a named member of a
  `LIST OF ^"Type"` that does not extend the type, and one property written twice in a
  definition are a warning in a file that declares a `SPEC_VERSION` below 0.6, or none, and an
  error from 0.6; `FIAT` waives each. A hash shorter than 16 characters, or with an underscore,
  takes the same gating and no waiver. The corpora gain 815 warnings and no error. A
  `REQUIRED` property left out and a `DEPENDS_ON` version pin are left to their own findings.

- **DECISION-33 — When two names are the same** *(resolved, v0.6, 2026-11-12)* (§14, §5d): the
  spec did not say, and the tools disagreed. The validator and the synthesist compared names
  exactly. The reference gate and `check_constructs.py` lower-cased a name and dropped every
  character outside `a-z0-9`, so `Orcs` and `Orcs!` were one name, `+2` and `−2` were one name,
  and `Mahō` lost a letter. That fold merges 1,023 groups of the corpora's 98,095 defined
  names, and 5 of about 98,000 references need it. The decision is one rule for every tool: two
  names are the same when their characters are the same after Unicode normal form, a run of
  white space read as one space, and a curly quote read as a straight one. Case, punctuation
  and accents count. `Jupiter's Touch` and `Jupiter’s Touch` are one name; `Status` and
  `status` are two.

- **DECISION-34 — `REQUIRED` means every entry of the type has the property** *(resolved, v0.6,
  2026-11-13)* (§8, §5, §20): §8 said only "must be provided". One tool looked, and it failed a
  property only when no instance of its type had it at all. Types declare 4,790 properties and
  mark 835 `REQUIRED`, under three meanings: every entry of this kind has the field (782, on
  types that are not `ACTOR` types); a finished player character must have it (most of the 53
  on `ACTOR` types); and `^"Name"` (239). No consumer acts on the word. The decision keeps the
  first meaning and no other. `REQUIRED` is a statement about the source's entries, so a miss
  is a field the conversion dropped or a type that is the wrong shape. Every instance must
  have the property: it writes it, a type above it gives the value, or it is a `PARAMETERS`
  slot. A required `^"Name"` is answered by the DEF's own name. A rule of character creation
  ("a player character chooses a school") is written where the choice is made, as a `CHOOSE`,
  since a `REQUIRED` on the actor type would bind every NPC, template and subclass that
  extends it. A miss is a warning in a file that declares a `SPEC_VERSION` below 0.6, or none,
  and an error from 0.6; an element-level `FIAT` waives it. The corpora gain 302 warnings in
  four corpora.

- **DECISION-35 — A version pin means "at least"** *(resolved, v0.6, 2026-11-13)* (§3, §19,
  §20): `DEPENDS_ON "Parent" VERSION "x"` was in the spec with no meaning given, and no tool
  read it. The corpora hold 459 pins. 274 name the parent's own version, 117 name its first two
  parts (`"0.5"` against `"0.5.0"`), and 68 name a version the parent has since left (`"0.5.9"`
  against `"0.5.10"`). A file's `VERSION` is bumped on every edit, so a pin read as exact goes
  stale the first time its parent is touched. The decision is that a pin says the file needs
  something the parent gained at that version: the loaded parent must be at that version or a
  later one. Versions are compared part by part, numbers as numbers, and a pin with fewer parts
  is met by any version that begins with it. A parent that is older is an error. All 459 pins
  are met today.

- **DECISION-36 — What a file depends on** *(resolved, v0.6, 2026-11-13)* (§3, §20): §3 said an
  extension declares "a parent", in one of two forms. Of 6,259 files that could name one, 5,012
  write `DEPENDS_ON`, 923 write `EXTENSION "X" EXTENDS "Y"`, 276 write both (Pendragon's header
  names the base and its `DEPENDS_ON` a types file), and 49 write several `DEPENDS_ON` (arm5e's
  errata file names 20 books). The validator checked one thing, that a `DEPENDS_ON` names a
  file. The decision keeps both forms and says what they mean. A file depends on every id it
  names with `DEPENDS_ON` and on the id its header `EXTENDS`; any number is legal. Each names a
  file in the loaded set. No two files depend on each other. A file id is declared once in a
  corpus. An `EXTENSION` names at least one parent, and a `BASE` names none but the dice
  module. A cycle is an error at every version, and so is a `DEPENDS_ON` that names nothing, as
  before; the rest is a warning in a file that declares a `SPEC_VERSION` below 0.6, or none,
  and an error from 0.6. The corpora gain 44 warnings.

- **DECISION-37 — A dependency loads first** *(resolved, v0.6, 2026-11-13)* (§13): §13 makes
  load order precedence, and no construct states an order. The order lives in each consumer's
  manifest, which the spec does not define. Eleven manifests were compared with what their
  files declare: of 5,338 dependencies, the target loads before the file that names it in
  5,319. The decision states the one rule the spec can own: a file loads after everything it
  depends on. Among files that rule leaves unordered, the order is the consumer's. The spec
  defines no manifest format.

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
| `.actor` | EXTENSION | One or more instances (characters, PC or NPC, and other records with a sheet) as a file of their own (DSL) *(v0.6: wrapped, §2)* |
| `.bridge` | BRIDGE | **Cross-edition conversion** — a directed correspondence between two editions (DSL) *(v0.4, §21)* |
| `.lore` | (none — Markdown) | **Free narrative prose / flavor** — no DSL syntax *(v0.4)* |
| `.codex` | CODEX | **Stand-off lore knowledge graph** — typed entities + declared relationships over `.lore` prose (DSL) *(v0.5, §25)* |
| `.selections` | SELECTIONS | **User's optional-rule choices** for a corpus — `SELECT #hash on\|off` (DSL) *(v0.5, §24)* |

**An `.actor` file is an `EXTENSION` file that holds instances and nothing else** *(v0.6,
DECISION-28)*. The extension says what the file holds, which makes characters easy to share, version
and find apart from the rules.

```
EXTENSION "tor2e-core-ash" EXTENDS "tor2e" {
    NAME "Ash"
    VERSION "0.5"
    SPEC_VERSION "0.6"
    RELEASE_DATE "2026-11-12"

    #tzjEoZpJbPbQBT05csRIVx5 ^"Ash" DEF {
        EXTENDS #TOR0020000000000 ^"Adversary"
        PROPERTIES {
            ^"Name" STRING "Ash"
        }
    }
}
```

- **It opens with the `EXTENSION` wrapper**, as a `.ttrpg` does (§3). So it declares its
  `SPEC_VERSION`, its own `VERSION`, and the file it depends on.
- **It holds one or more instance DEFs** (§5). One file may hold one character, one character in
  several states (a magus at Gauntlet and again fifteen years on), or a group that belongs together
  (an adventure's pregenerated characters, a chapter's NPCs).
- **It holds instances only.** Each DEF `EXTENDS` a type, usually one of the system's `ACTOR` types,
  or another instance in the same file. A type declaration, an `ACTOR` or `TEMPLATE` definition, and
  a `MODIFY`, `OVERRIDE`, `ADD`, `REPRINT` or `ALIAS` belong in a `.ttrpg`.

Before v0.6 this section called an `.actor` a standalone single DEF with no wrapper. A file that
opens with a bare DEF is that older form. It carries no `SPEC_VERSION`, so it reads as older than
0.6, and the validator **warns**. A type or a modification in an `.actor` is a warning in a file that
declares a `SPEC_VERSION` below 0.6 and an error from 0.6.

### Structured Narrative vs. Free Prose (`.setting`/`.frame` vs `.lore`) *(v0.4)*

Narrative content splits by whether tools need to *query* it:

- **Structured narrative → `.setting`, `.frame`, `.arc`, `.campaign`** (DSL syntax). Use these when the content has addressable, cross-referenced parts a tool consumes — locations, factions, NPC stat blocks, scenes, hooks, timelines. These carry hash IDs and caret references.
- **Free prose → `.lore`** (Markdown, no DSL). Use this for readable flavor and world description meant for humans — history essays, cultural color, fiction. A `.lore` file is **not** parsed as DSL.

Rule of thumb: if a tool must look something up in it, it's `.setting`/`.frame`; if it's just meant to be read, it's `.lore`. The same subject may appear in both (a mechanical `.setting`/`.ttrpg` entry plus a `.lore` essay).

When a tool must query the *facts inside* a `.lore` essay — who a person is, where a place sits, how factions relate — the answer is **not** to structure the prose but to build a **stand-off `.codex` knowledge graph** beside it (§25). The `.lore` body stays byte-verbatim and opaque; the codex holds the typed entities and relationships and points *into* the prose. This keeps the query test intact: the prose is still "just meant to be read," and the structured, queryable layer is a separate file.

### File Organization

The corpora are organised as one repository per system, with one directory per content version
(§19):

```
titterpig-dsl-<system>/
  <contentver>/
    <system>-<contentver>-<book>-<facet>.<ext>
```

`titterpig-dsl-l5r5e/0.5/l5r5e-0.5-core-base.ttrpg` and
`titterpig-dsl-l5r5e/0.5/l5r5e-0.5-emerald-empire-adventure-seeds.frame` sit side by side. The
extension says what a file holds (the table above); the directory does not sort files by type. Two
editions kept in one repository take a directory each (`arm5e/0.5/`, `armdef/0.5/`). A `.bridge`
lives outside both corpora it joins (§21).

This is how the corpora are laid out. No tool checks it.

---

## 3. File-Level Structure

Every `.ttrpg` file opens with either a `BASE` or `EXTENSION` declaration. These are the only two file-level wrappers. An `.actor` file opens with `EXTENSION` (§2).

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

**What a file depends on** *(v0.6, DECISION-36)*. A file depends on every id it names with
`DEPENDS_ON` and on the id its header `EXTENDS`. The two forms mean the same thing, and a file may
use either, both, or several `DEPENDS_ON` lines:

```
EXTENSION "pendragon5e-bokl-appendices" EXTENDS "pendragon5e" {    # the base, in the header
    DEPENDS_ON "pendragon5e-bokl-types" VERSION "0.5"              # and a file of types
}

EXTENSION "ArM5_Core_Errata" {
    DEPENDS_ON "ArM5_Abilities"                                    # one line for each file
    DEPENDS_ON "ArM5_Core_Base"                                    # the errata corrects:
    DEPENDS_ON "ArM5_Core_Systems"                                 # twenty in all
}
```

- **Each names a file in the loaded set.** An id that no loaded file declares is an error.
- **No two files depend on each other**, directly or through others.
- **A file id is declared once in a corpus**, whatever kind of file declares it. An arc and a frame
  do not share an id.
- **An `EXTENSION` names at least one parent.** A `BASE` names none, the dice module aside.
- A dependency loads before the file that names it (§13).

A cycle, and a `DEPENDS_ON` that names nothing, are errors at every version. A header `EXTENDS`
that names nothing, an id declared twice, an `EXTENSION` with no parent and a `BASE` with one are
warnings in a file that declares a `SPEC_VERSION` below 0.6, or none, and errors from 0.6.

**A version pin means "at least"** *(v0.6, DECISION-35)*. `DEPENDS_ON "Parent" VERSION "0.5.9"` says
this file needs something the parent gained at 0.5.9: the parent that is loaded must be at that
version or a later one.

- Versions are compared part by part, split at each dot or hyphen, numbers as numbers: 0.5.10 is
  later than 0.5.9, and 0.10 is later than 0.9.
- A pin with fewer parts is met by any version that begins with it: `"0.5"` is met by `"0.5.0"`
  and by `"0.5.9"`.
- A loaded parent that is older than the pin is an **error**. A parent that declares no `VERSION`
  cannot be compared, and the validator **warns**.
- A pin is never exact. A file's `VERSION` rises with every edit to it, so an exact pin would
  break each time a parent was corrected.

**Fields:**
- `FileID`: Unique identifier (e.g., `"L5R5e_Core_Core"`, `"VTM5e_Companion_Errata"`)
- `NAME`: Full display name
- `VERSION`: Content version of this file (semantic or date-based)
- `SPEC_VERSION` *(v0.4)*: The DSL-spec version this file targets (e.g., `"0.4"`). Distinct from `VERSION`; lets tooling detect spec conformance.
- `RELEASE_DATE`: ISO date format
- `ORIGIN` *(v0.6)*: only in a **port**, a file made from another edition's file. It names that
  edition and that file: `ORIGIN "arm5e" EXTENSION "ArM5_Grogs_Abilities"` (§19).

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
alias, still accepted so 0.4 corpora keep validating). Four additions:
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

**v0.6 changes (DECISION-19).**

1. **`EMPHASIS` may say how the span is set.** `BOLD`, `ITALIC` or both stand between the keyword
   and its brace, and a DEF holds one block per kind:

   ```
   SCENE #txWKzqF0ygAjNWBHNG3TOPs ^"2nd Floor Passenger: The Gas Form" {
       DESCRIPTION "Outside the door is a cloud of green gas with little balloon bladders floating
                    in it supporting decorative jewelry much like your ear would. The mandrill takes
                    a little gas mask (mandrill-sized only) out from a compartment in the wall by
                    his panel and put it on. …"
       EMPHASIS BOLD        { "cloud of green gas" }
       EMPHASIS ITALIC {
           "decorative jewelry"
           "little gas mask"
       }
       EMPHASIS BOLD ITALIC { "The mandrill" }
   }
   ```

   `EMPHASIS { … }` with no kind stays legal: the span is marked and the kind was not recorded.
   Other kinds (underline, strike-through, small capitals) are **not yet defined (to-do)**.

2. **`LABEL` — a run-in label.** `LABEL { "surface form" }`. A label the source sets at the head of
   the text it labels stays in the string as printed and is named here:

   ```
   DESCRIPTION "Prot: The bonus the armor grants to the character’s Soak score.\nLoad: The amount
                the armor adds to the character’s Burden.\nCost: A general indication of the expense
                of the armor. More expensive armor is better."
   LABEL {
       "Prot:"
       "Load:"
       "Cost:"
   }
   ```

   A whole number after the keyword is the label's **depth**; with none written the depth is 1. A
   label of depth 2 sits under the depth-1 label before it:

   ```
   DESCRIPTION "Sample Vestals Initiation: Nature Lore\n\nEase Factor: 15 (Minor Virtue known to the
                Mystagogue)\n\nScript Bonus: +10 Script Details: The Initiate must prepare a cake
                using ritual ingredients. …"
   LABEL   { "Sample Vestals Initiation: Nature Lore" }
   LABEL 2 {
       "Ease Factor:"
       "Script Bonus:"
       "Script Details:"
   }
   ```

   The rule is the one `EMPHASIS` has: **the surface form must appear in the DEF's own prose**, and
   an `@n` occurrence index is accepted on the same terms.

3. **A whole paragraph set in one face is not yet recordable (to-do).** Opening fiction, an epigraph
   or a line of flavour set wholly in italic is the paragraph's style and not a span marked inside
   it. Listing it under `EMPHASIS` would repeat the paragraph as its own surface form.

4. **Markdown emphasis inside a string is flagged.** A paired `**…**` or `*…*` in a string raises
   a **warning** in a file that declares a `SPEC_VERSION` below 0.6, or none, and an **error** in
   one that declares 0.6 or later. The span belongs in an `EMPHASIS` or `LABEL` block.

   An asterisk the source prints is text and stays. One followed by a space (a footnote mark, a
   bullet) or preceded by a letter, a digit or a closing bracket (`Chirurgery 20*`, `Courtesy 20 (+1)*`) does not read as the start of a
   span and is not flagged. Where two printed asterisks do read as a span, a `FIAT` (§8) records
   that the source prints them:

   ```
   ^"Marks" STRING "Weapons marked *thus* need two hands." FIAT "printed asterisks"
   ```

**v0.6 changes (DECISION-20): embedded references.** A reference may also be written inside the
string, at the words that cite the DEF:

```
EFFECT "… When the character becomes Compromised, they also become ^\"Enraged\" (see page 272)."
EFFECT "… they fly into a ^\"Enraged\"/\"state of rage\" …"
EFFECT "… they also become #hash ^\"Enraged\" …"
```

| Written in the string | Cites | Text |
|---|---|---|
| `^\"Enraged\"` | `^"Enraged"` | `Enraged` |
| `^\"Enraged\"/\"state of rage\"` | `^"Enraged"` | `state of rage` |
| `#hash ^\"Enraged\"/\"state of rage\"` | `^"Enraged"`, by its hash | `state of rage` |

- **The literal.** A slash and a second quoted string directly after the name give the words the
  text keeps. It is not empty. Without it the text is the name.
- **In a triple-quoted string** (§10) the quotes carry no backslash: `^"Enraged"/"state of rage"`.
- **Each one is a reference site (§5d).** It resolves by its hash when it carries one; a hashless
  one WARNs, and a hashless one whose name is more than one entity is an ERROR. It counts as a
  reference from the entity around the string, so a `REFERENCED BY` may mirror it.
- **A string's text** is the string with each embedded reference read as its literal, or as its
  name where it has none. The verbatim rule below is a rule about the text, and the surface forms
  of `REFERENCES`, `EMPHASIS` and `LABEL` are matched against it.
- A `REFERENCES` block and embedded references are two ways to record the same fact, and both are
  legal.

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
  added, removed, or reworded. No inline markup is ever inserted into the text. From v0.6 an
  embedded reference (above) is the one thing a string may hold besides its text, and the rule
  applies to the text: the string with each embedded reference read as its literal or its name.
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
- **Unique per entity, within an edition/version namespace.** A hash names one entity, and its
  definition appears once: a second DEF under a hash the corpus already declares is an **error**
  *(v0.6, DECISION-27)*. A later-loaded file (a sourcebook, an errata overlay) changes an entity by
  naming it in an `OVERRIDE`, a `MODIFY` or a `REPRINT` (§13, §5b). Before v0.6 a restated hash was
  read as a silent replacement.
  **Across editions the namespace resets.** Nothing resolves from one edition into another, and
  the "same" entity in a different edition is a **separate definition** (edition changes may be
  breaking — §19). An entity converted afresh for the other edition has a hash of its own. An
  entity carried over by a **port** keeps the hash it had *(v0.6, §19, DECISION-26)*. A hash that
  two editions share outside a declared port means nothing. Within an edition, two *different*
  entities must never share a hash.
- **Format:** `#` followed by `≥16` alphanumeric characters (`[A-Za-z0-9]{16,}`). A shorter hash,
  or one with an underscore, is a warning in a file that declares a `SPEC_VERSION` below 0.6, or
  none, and an **error** from 0.6 *(DECISION-32)*.
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
- `TABLE { }` — a table (see §5e)
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

Instances use the **same** grammar as definitions — no `=` assignments, no dotted paths, no `STATS` block, and the canonical `#hash ^"Name" DEF` ordering. An `.actor` file holds one or more such instances (§2). Coherence validation checks each value against the constraint inherited from the actor type (here, Air ∈ 1–5).

---


### §5d — Reference resolution: one rule for every construct *(v0.5, DECISION-13)*

A **reference site** is any place one definition names *an entity that already exists*: `EXTENDS`,
`APPLIES TO`, `LIST OF`, `CONCERNS`, `OVERRIDE`, `MODIFY`, the target of `ALIAS … FOR`, an entity
option or `OF` type of a `CHOOSE` (§5b), the type and the value of a `REF`, the target of a `SET`
or `TRANSFORM` and the die of a `ROLL` (§8), the type of an `AXIS … OF`, an entity listed as an
axis point and an entity given as a coordinate of an `AT` (§5e), the `REFERENCES` /
`REFERENCED BY` targets and embedded references of §5c, and the references between narrative
blocks of §16: `SCENE_REF`, `LEADS_TO`, `COMPLETED_SCENES`, `OPPONENTS`, a scene's `LOCATION`, and
each `INCLUDE` item of a `FROM`. All of them obey the same rule. What a reference may point at is
set out in §20.

**Declaration sites are not reference sites.** `ADD #hash ^"Name" DEF { … }` (§13) *asserts new
content*, so its hash is an anchor being minted, not a pointer to one; `ALIAS ^"New" FOR ^"Existing"`
likewise declares `^"New"` and references only `^"Existing"`. `SET`, `ADD_TO` and `REMOVE_FROM` name a
**property** of the entity being modified, not an entity, and are outside this rule.

**The `#hash` is the referent. The `^"Name"` is a readability aid.**

```
EXTENDS #tor5Shield000000001 ^"Shield"     # resolves to that anchor, whatever else is named "Shield"
EXTENDS ^"Shield"                          # resolves by name — and only if the name is unambiguous
```

1. **Resolution is by hash when a hash is present.** The caret name must be the anchor's own name (§14 says when two names are the same);
   a mismatch is an **ERROR** (it means one of the two was edited and the other was not). A hash that
   is not a declared anchor is an **ERROR**.
2. **A hashless reference SHOULD carry the hash.** Where the name resolves to exactly one entity the
   reference is well-defined but untraceable, so it **WARNs**.
3. **A hashless reference whose name resolves to more than one distinct entity is an ERROR.** Nothing
   in the file says which is meant, so every consumer must invent a tie-break, and two consumers that
   invent different ones disagree about what the corpus says. An entity is its hash: two DEFs with
   distinct hashes, or a hashless DEF beside a hashed one, are distinct entities. Two DEFs cannot
   carry the same hash (§5, DECISION-27).

**Scope of the name form.** `^"Name"` remains legal and remains the readable surface — this is not a
deprecation. It is sufficient only where the name is unique corpus-wide, which is a property of the
corpus, not of the reference, and can stop being true when a later file adds a same-named entity. That
is precisely what the hash immunises against.

**Migration.** The hash for an unambiguous hashless reference is mechanically derivable — the name
already resolves — so backfilling is a scripted, reviewable edit, not re-authoring. Ambiguous sites
cannot be backfilled mechanically: they need the intended target chosen, which is the point.

---

### §5e — Tables: `TABLE`, `AXIS` and `AT` *(v0.6, DECISION-21)*

A table is a `TABLE` block in the body of a DEF. The DEF gives it its name and hash. `TABLE` is a
primitive of the language, as `PROPERTIES` is: there is no table type to extend.

**A lookup table** declares its axes, then gives a result at each coordinate.

```
#hash ^"Fate Chart" DEF {
    TABLE {
        AXIS ^"Odds" OF #hash ^"Odds"
        AXIS ^"Chaos Factor" 1-9

        AT [ #hash ^"Certain", 1 ]        { ^"Exceptional Yes" INTEGER 10  ^"Yes" INTEGER 50  ^"Exceptional No" INTEGER 91 }
        AT [ #hash ^"Certain", 2 ]        { ^"Exceptional Yes" INTEGER 13  ^"Yes" INTEGER 65  ^"Exceptional No" INTEGER 94 }
        AT [ #hash ^"Nearly Certain", 1 ] { ^"Exceptional Yes" INTEGER 7   ^"Yes" INTEGER 35  ^"Exceptional No" INTEGER 88 }
        …
    }
}
```

`AXIS ^"Name"` is followed by the axis's points:

| Written | The points of the axis |
|---|---|
| `OF #hash ^"Type"` | the entities of that type |
| `1-9` | the whole numbers in the range |
| `INTEGER` | any whole number |
| `ROLL n OF #hash ^"die"` | the totals of that roll (§8) |
| `[ "Light", "Medium", "Heavy" ]` | the strings or entities listed |

`AT [ … ] { … }` gives one coordinate for each axis, in the order the axes are declared, and then
the result in a block.

| Coordinate | Covers |
|---|---|
| `4` | that number |
| `3-7` | the numbers in the range |
| `MIN 16` | 16 and every number above it |
| `MAX 1` | 1 and every number below it |
| `#hash ^"Certain"` | that entity |
| `"Light"` | that string |
| `ANY` | every point of the axis |

The result block holds what a DEF body holds: values, a `REF`, a `SET` or `TRANSFORM`, a `ROLL`,
a named DEF, or another `TABLE`.

**A roll table** is a table whose one axis is a roll.

```
#hash ^"Cursed Punishment" DEF {
    TABLE {
        AXIS ^"Roll" ROLL 2 OF #hash ^"d10"

        AT [ 2 ]   { ^"Punishment" STRING "Forgiven"
                     ^"Effect" STRING "The character is forgiven or forgotten by the gods. Reduce their Hubris by 1."
                     #hash ^"Hubris" TRANSFORM SUBTRACT 1 }
        AT [ 3-7 ] { ^"Punishment" STRING "No effect"
                     ^"Effect" STRING "The character remains unpunished." }
        AT [ 8 ]   { ^"Punishment" STRING "Incompetent"
                     ^"Effect" STRING "One randomly determined skill is always rolled at a -2D penalty." }
        …
    }
}
```

**A table of records** holds no cells. Where each row of a printed table is an entity and each
column one of its properties, the table names the type as its one axis and lists the properties as
`COLUMNS`, in the order printed. The values stay on the entities.

```
#hash ^"Armor Table" DEF {
    TABLE {
        AXIS ^"Material" OF #hash ^"Armor"
        COLUMNS [ ^"Partial Prot", ^"Partial Load", ^"Full Prot", ^"Full Load", ^"Cost" ]
    }
}
```

**References.** The type after `OF`, an entity listed as an axis point and an entity given as a
coordinate are reference sites (§5d). A name in `COLUMNS` is a property of the axis type and is
not one.

**Coherence.**

- A `TABLE` declares at least one `AXIS`, and holds `AT` cells or `COLUMNS`, not both.
- Each `AT` gives as many coordinates as the table has axes.
- A coordinate is of a kind its axis takes: a number on a range, `INTEGER` or roll axis; an entity
  of the type on an `OF` axis; one of the listed points on a list axis. A number lies inside a
  range axis, and a range runs from low to high.
- No two cells cover the same coordinates.
- `COLUMNS` needs exactly one axis, declared `OF` a type, and each column is a property that type
  declares, its own or inherited.

**Not yet defined (to-do).** Column headings in more than one tier; footnote marks on a cell;
whether every point of an axis has a cell, which is not checked.

**A `TABLE` block in an older file.** Corpora wrote `TABLE { COLUMNS [ … ] ROW [ … ] }` grids of
strings as a system-defined block before v0.6. A `TABLE` with no `AXIS` is left alone in a file
that declares a `SPEC_VERSION` below 0.6, or none, and is an **error** in one that declares 0.6 or
later.

## 6. Inheritance (EXTENDS)

A DEF that `EXTENDS` another inherits all of its PROPERTIES and RULES. The child can add new properties, override defaults, and add rules.

**`EXTENDS` is acyclic** *(v0.6, DECISION-32)*. A definition that extends itself, directly or through
others, is an **error**.

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
    ^"Techniques" LIST OF ^"Technique"
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
| STRING | `STRING [value]` | Text value |
| INTEGER | `INTEGER [value]` | Numeric value |
| BOOLEAN | `BOOLEAN [true\|false]` | True/false |
| ENUM | `ENUM ["val1", "val2", ...]` | Constrained choice |
| LIST | `LIST ["val1", "val2"]` | Literal list of values |
| LIST OF | `LIST OF ^"TypeName"` | Typed collection referencing another DEF |
| LIST OF STRING | `LIST OF STRING [values]` | Typed collection of strings with optional defaults |
| REF | `REF OF ^"TypeName"` · `^"Name" REF ^"Entity"` | Reference to one entity *(v0.6, see below)* |
| ROLL | `ROLL n OF ^"Die"` | A roll of `n` dice *(v0.6, see below)* |
| DEF (nested) | `^"Name" DEF { ... }` | Nested structured object |

### Modifiers (apply to any type)

A modifier follows the type and its value, on any type in the table above. `MIN` and `MAX` are the
exception: they constrain an `INTEGER` only.

- `REQUIRED` — every entry of the type has this property *(v0.6, DECISION-34; see below)*
- `FIXED` — cannot be changed after creation
- `DEFAULT value` — default value if not provided
- `MIN n` / `MAX n` — range constraints (INTEGER)
- `FIAT "reason"` *(v0.4)* — waive validation for this value (intentional exception; see *FIAT* below)

### `REQUIRED` — what every entry of a type has *(v0.6, DECISION-34)*

`REQUIRED` on a property says that **every entry of this type in the source has it**. It is a
statement about the book: every row of a roll table has a roll and a text.

```
#hash ^"Roll Table Entry" DEF {
    PROPERTIES {
        ^"Roll" STRING REQUIRED
        ^"Text" STRING REQUIRED
        ^"Note" STRING
    }
}

#hash ^"Row 1" DEF {
    EXTENDS #hash ^"Roll Table Entry"
    PROPERTIES {
        ^"Roll" STRING "1-3"
        ^"Text" STRING "A stranger arrives."
    }
}
```

- **Who must have it.** Every **instance** of the type: a DEF that extends the type, directly or
  through others, and is not itself a type. A type is an `ACTOR` or `TEMPLATE` definition, a DEF
  that another DEF extends, or a DEF that declares fields and gives no value.
- **What counts as having it.** The instance writes the property. Or a type between the two gives
  it a value, which then holds for everything below. Or the property is a `PARAMETERS` slot, which
  the reference supplies (§5b).
- **`^"Name"`.** A required `^"Name"` is answered by the DEF's own name. An instance need not
  write its name twice.
- **Not for a rule of play.** "A player character chooses a school" is a step of character
  creation. It is written where the choice is made, as a `CHOOSE` (§5b). Written as `REQUIRED` on
  the actor type, it would bind every NPC, template and subclass that extends the type.
- **An exception the source prints.** An entry the book gives without the field takes an
  element-level `FIAT "reason"` (below): *Path of Waves* traditions are schools with no clan.
- **Severity.** An instance without a required property is a warning in a file that declares a
  `SPEC_VERSION` below 0.6, or none, and an error from 0.6.

A miss means one of two things: the conversion dropped a field the book gives, or the type
requires what not every entry has. Before v0.6 the spec said only "must be provided".

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

**Printed asterisks *(v0.6)*.** A `FIAT` also excuses the Markdown-emphasis finding of §5c, for a string whose asterisks the source prints.

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

**A definition's prose is `DESCRIPTION`** *(v0.6, DECISION-30)*, as in the examples above. `TEXT` is
the prose field of a block that is not a definition: a guidance `ENTRY` (§22), the units of a bridge
(§21), an `OPTIONAL` block (§24), and a system block that carries prose of its own (curseborne's
scenes hold `READ_ALOUD { TEXT "…" }`).

```
MODIFY #tbebb8a5383255856b3d30 ^"Universal Tiebreaker" {
    GUIDANCE {
        ENTRY ^"errata-universal-tiebreaker-0" #L5RERG0TplpshcZa3oDYQ3 {
            CONCERNS [ #tbebb8a5383255856b3d30 ^"Universal Tiebreaker" ]
            TOPICS [ "errata" ]
            TEXT "p. 26, Margin Note \"Universal Tiebreaker\": The second bullet should read \"Adversary NPCs supersede minion NPCs\""
        }
    }
}
```

Before v0.6 a system could write `TEXT` for a DEF's `DESCRIPTION` "when the content is mechanical
rather than narrative". `TEXT` directly in a DEF is a warning in a file that declares a `SPEC_VERSION`
below 0.6, or none, and an error from 0.6.

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
    TABLE {
        AXIS ^"Roll" ROLL 1 OF #hash ^"d10"

        AT [ 1 ] {
            ^"Famous Deed" DEF {
                MODIFIERS { #hash ^"Glory" TRANSFORM ADD 3 }
                TABLE {
                    AXIS ^"Roll" ROLL 1 OF #hash ^"d10"
                    AT [ 1-2 ] { EFFECT { "A famous weapon: Receive one weapon of rarity 7 or lower" } }
                }
            }
        }

        # A result that covers a span of die results gives the span as its coordinate.
        # Supplement heritage tables assign one result to several rolls; the range is
        # part of the structure, never a note in prose.
        AT [ 2-3 ] {
            ^"Triumph over the Lion" DEF {
                MODIFIERS { #hash ^"Honor" TRANSFORM ADD 5 }
                TABLE {
                    AXIS ^"Roll" ROLL 1 OF #hash ^"d10"
                    AT [ 1-3 ] { EFFECT { "A weapon" } }
                    AT [ 9 ]   { EFFECT { "A horse or another animal" } }
                }
            }
        }

        # Where an entry grants something outright instead of a second roll.
        AT [ 10 ] {
            ^"Imperial Heritage" DEF {
                MODIFIERS { #hash ^"Status" TRANSFORM ADD 10 }
                EFFECT { "Gain the ^\"Blessed Lineage\" distinction" }
            }
        }
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
sourcebook that would never be co-loaded with this one. Where both are loaded they are two entities
of one name, and neither replaces the other (*Composition & Precedence*, below).

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
order is precedence:** each file's `OVERRIDE` / `MODIFY` / `ADD` (above) and `REPRINT` (§5b) is applied
over what the files before it define, and where two files change the same thing the **later one wins**.

**A later file changes an earlier definition only by naming it** *(v0.6, DECISION-27)*. The statement
is surgical and auditable: the base definition stays put and the overlay is applied deterministically.
A new DEF under the target's hash replaces nothing. A DEF's hash stands once in the loaded set, and a
second DEF under it is an **error** (§20). Before v0.6 that second DEF was an "implicit" override. No
corpus used it, the validator rejected it, and it could not be told from a DEF pasted twice.

**A DEF of the same name under another hash is a second entity** *(v0.6, DECISION-27)*. It replaces
nothing, whatever its type and wherever it loads, because an entity is its hash (§5d). Both definitions
reach the consumer, and a consumer must not merge two DEFs because their names match. A hashless
reference to that name is an error until it carries a hash (§5d). A book that means the entity
another file defines names it: `REPRINT` where the text is the same, `ALIAS` where only the name
differs, `MODIFY` where its wording should take effect, `OVERRIDE` to replace it (§5b, above).

**A dependency loads first** *(v0.6, DECISION-37)*. A file loads after every file it depends on
(§3). That is the one rule of order this spec states. Among files it leaves unordered, the order is
the consumer's to choose and to record; the spec defines no manifest. Order decides something only
where two files change the same thing.

A set holds **one** definition of a given entity. Overlapping printings (a spell reprinted in two
sourcebooks, a beta and a final ruleset) are generally not co-loaded, and a book that prints an entity
another loaded file defines says so with `REPRINT`, `ALIAS` or `MODIFY` (§5b). A port and its origin
(§19) belong to two editions and are never loaded in one set: that is an error *(v0.6)*. Precedence resolution
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

A quote inside a name is written `\"`, as it is inside a string *(v0.6, DECISION-25)*:
`^"Mrinmoy \"Vidyapati\" Mishra"`.

### When two names are the same *(v0.6, DECISION-33)*

Two names are the same when their characters are the same, once three differences are set aside
that a reader cannot see or should not care about:

- **Unicode form.** A letter with an accent written as one character, or as the letter and a
  combining accent, is the same letter (the names are compared in normal form NFC).
- **White space.** A run of spaces, a tab or a no-break space reads as one space, and space at
  either end is dropped.
- **Quote style.** `’` and `‘` read as `'`, and `“` and `”` as `"`.

Everything else counts: **case, punctuation and accents**.

| These are one name | These are two |
|---|---|
| `^"Jupiter's Touch"` and `^"Jupiter’s Touch"` | `^"Status"` and `^"status"` |
| `^"Long Bow"` and `^"Long  Bow"` | `^"Long Bow"` and `^"Longbow"` |
| | `^"Orcs"` and `^"Orcs!"` |
| | `^"Maho"` and `^"Mahō"` |

Every comparison of names uses this rule: a reference against a definition, a caret name against
the name of the hash before it (§5d), an alias, a list member. Two definitions whose names are the
same are two entities of one name where their hashes differ (§13).

### Hash IDs `#identifier`

Unique anchors for cross-file traceability:

```
#L5R001aB2cD4eF6gH8iJ0kL ACTOR "Entity" DEF { }
#L5R002: WHEN [^"Entity" CREATED] THEN REQUIRE ^"Name"
```

### Embedded References in Strings

A caret reference can appear inside a quoted string, with its quotes escaped. A slash and a second
quoted string after it give the words the text keeps where they differ from the name, and a hash
may stand before the caret (§5c, DECISION-20):

```
ACTIVATION "When you make a ^\"Fitness\" check..."
EFFECT "If you fail, you suffer ^\"Disoriented\"."
EFFECT "You fly into a #hash ^\"Enraged\"/\"state of rage\"."
```

Each is a reference site and resolves under §5d.

### Combined Hash + Caret

When both appear together, the hash provides the unique ID and the caret provides the human-readable name:

```
EXTENDS #L5R001aB2cD4eF6gH8iJ0kL ^"Entity"
#L5R250aB2cD4eF6gH8iJ0k ^"Clan" DEF { }
```

---

## 15. Reserved Keywords (Base Spec)

Only these keywords are reserved by the base spec.

**Where a keyword is reserved** *(v0.6, DECISION-29)*. A keyword listed under a block (Tables, Hooks,
Codex, Bridge, the narrative containers of §18) is reserved inside that block. Outside it, a system
may use the word for a field of its own: l5r5e's curricula write `SKILL "Aesthetics"`, and `SKILL`
is a SCENE keyword. The file-level, definition, type, modifier, scope, choice and modification
keywords are reserved everywhere.

**File-level:** `BASE`, `EXTENSION`, `EXTENDS`, `NAME`, `VERSION`, `SPEC_VERSION`, `RELEASE_DATE`, `DEPENDS_ON`, `ORIGIN` (a port's source, §19; shared with **Bridge**)

**Definition:** `DEF`, `ACTOR`, `TEMPLATE`, `CHOICES`, `PROPERTIES`, `RULES`

**Types:** `STRING`, `INTEGER`, `BOOLEAN`, `ENUM`, `LIST`, `OF`, `REF`, `ROLL`, and the `BOOLEAN` values `true` and `false`

**Dice (§8):** `FACES`, `WEIGHT`, `ROLL`, `NEXT`

**Changes (§8):** `SET`, `TRANSFORM`, `ADD`, `SUBTRACT`, `MULTIPLY`, `DIVIDE`, `ROUND`, `UP`, `DOWN`, `NEAREST`, `MANUAL` (`SET` and `ADD` are shared with **Modification**, `MANUAL` with **Bridge**, `MIN` / `MAX` with **Modifiers**)

**Modifiers:** `REQUIRED`, `FIXED`, `DEFAULT`, `MIN`, `MAX`, `FIAT`

**Scope:** `APPLIES`, `TO`, `ALIAS`

**Parameters (§5b):** `PARAMETERS` (`OF` is shared with **Types**, `ALIAS` and `FOR` with **Scope** and **Codex**)

**Choice (§5b):** `CHOOSE`, `DISTINCT`, `INDISTINCT`, `WITH`, `AND`, `OR`, `NOT` (`OF` is shared with **Types**)

**Rule structure:** `WHEN`, `THEN`

**Hooks (§23):** `HOOKS`, `HOOK`, `FORMALITY`, `PROSE`, `TAGGED`, `CONDITIONAL`, `FORMAL`, and `TRIGGER` inside a `HOOK` (`WHEN` and `THEN` are shared with **Rule structure**)

**Optional rules and selections (§24):** `OPTIONAL`, `GLOBAL`, `SELECTIONS`, `SELECT`, `on`, `off` (`DEFAULT` is shared with **Modifiers**, `SCOPE` with **Bridge**, `FOR` and `VERSION` with §3/§19; `OPTIONAL` is also a SCENE keyword, §18)

**Modification:** `OVERRIDE`, `ADD`, `MODIFY`, `SET`, `ADD_TO`, `REMOVE_FROM`, `REPRINT`

**Text:** `DESCRIPTION`, `TEXT`

**Tables (§5e):** `TABLE`, `AXIS`, `AT`, `COLUMNS`, `ANY` (`OF`, `INTEGER` and `ROLL` are shared with **Types**, `MIN` / `MAX` with **Modifiers**, `AT` with **Codex**)

**Annotation beside text (§5c):** `REFERENCES`, `MENTIONS`, `REFERENCED`, `BY`, `EMPHASIS`, `BOLD`, `ITALIC`, `LABEL`

**Narrative containers:** `SETTING`, `FRAME`, `ARC`, `CAMPAIGN`, `SCENE`, `LOCATION` (and their sub-keywords as defined in §16)

**Codex (§25):** `CODEX`, `SOURCES`, `CATEGORIES`, `RELATIONS`, `ENTITY`, `IS`, `RELATIONSHIPS`, `INVERSE`, `DOMAIN`, `RANGE`, `SYMMETRIC`, `TRANSITIVE`, `SOURCE`, `AT`, `FROM` (`FOR`/`EDITION`/`DEPENDS_ON`/`VERSION` are shared with §3/§19; `EXTENDS` with §6)

**Bridge (§21):** `BRIDGE`, `ORIGIN`, `DESTINATION`, `EXTERNAL`, `DISPOSITIONS`, `DISPOSITION`, `ALIASES`, `CONVERSION`, `GUIDANCE`, `MAP`, `REMAINDER`, `PROCEDURE`, `SUBJECT`, `SCOPE`, `ASPECT`, `CONCERNS`, `TOPICS`, `EXHAUSTIVE`, `CONVERT`, `INTO`, `UNCHANGED`, `SCALE`, `OVER`, `RESTATE`, `MANUAL` (`ALIAS`/`FOR` are shared with §5b; `ENTRY` and `TEXT` with §16/§10)

All other keywords — `CURRICULUM`, `SCHOOL_ABILITY`, `POWERS`, `AMALGAMS`, `TRIGGER` (outside a `HOOK`), `CHARACTERISTICS`, `HERITAGE_TABLE`, `ACTIVATION`, `OPPORTUNITIES`, `PREDATOR_TEMPLATES`, `DICE_POOL`, `COST`, `DURATION`, etc. — are **system-defined**. They belong to L5R5e, VTM5e, or whatever system uses them.

---

## 16. Narrative Containers

The DSL supports structured narrative content through four container types. These complement the BASE (game mechanics) and EXTENSION (content additions) containers.

### SETTING — System-Agnostic World-Building

A SETTING defines lore, geography, factions, history, and culture with no mechanical dependencies. Settings are reusable across game systems.

```
SETTING "SettingID" {
    NAME "Human-readable Setting Name"
    VERSION "1.0.0"
    SPEC_VERSION "0.6"

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
    SPEC_VERSION "0.6"

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

> **DECISION-2 (resolved, v0.4):** NPCs are **instances** — write them with the canonical instance form (§5, *Definitions vs. Instances*): a `#hash ^"Name" DEF` that `EXTENDS` its actor type with a `PROPERTIES` block of inline typed values. The looser `DEF ^"Name" #id { TYPE "npc" … STATS { rings.air = 4 } }` form — reversed order, `=` assignment, dotted paths, `TYPE`-as-tag — is **deprecated**. No new grammar is added.

```
FRAME "FrameID" {
    NAME "Human-readable Frame Name"
    VERSION "1.0.0"
    SPEC_VERSION "0.6"
    DEPENDS_ON "BaseSystemID"
    USES_SETTING "SettingID"    # optional

    THEMES {
        "Theme description"
    }

    STARTING_CONDITIONS {
        DESCRIPTION "How PCs enter the frame"
        MODIFICATIONS {
            # Character creation adjustments for this frame
            #hash ^"Property" SET value                     # a starting value (§8)
            ^"Property" INTEGER MIN new_min MAX new_max      # a range (§8)
        }
    }

    # NPC roster — canonical instances (see §5, Definitions vs. Instances)
    #hash ^"NPC Name" DEF {
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
        #hash: rule_label "The frame-specific rule, in the source's words"    # §12
    }
}
```

**Fields:**
- `FrameID`: Unique identifier
- `DEPENDS_ON`: Required BASE system
- `USES_SETTING`: Optional SETTING reference for world-building context
- `STARTING_CONDITIONS`: Character creation modifications. `MODIFICATIONS` holds them in the forms
  §8 already defines: `#hash ^"Property" SET value` for a starting value, and a property
  declaration with `MIN` / `MAX` for a range
- `DEF`: NPC definitions with mechanical stats
- `ENTRY`: Adventure hooks and GM guidance
- `RULES`: Lightweight frame-specific rules, written as §12 defines a rule

**Example:**

```
FRAME "RichFrogFrame" {
    NAME "Rich Frog Chronicles"
    VERSION "0.1.0"
    SPEC_VERSION "0.6"
    DEPENDS_ON "L5R5e"
    USES_SETTING "RichFrog"

    THEMES {
        "Trade and espionage at the crossroads"
        "Duty to clan versus personal ambition"
    }

    STARTING_CONDITIONS {
        DESCRIPTION "PCs are newly assigned samurai sent to represent their clan's interests in the City of the Rich Frog"
        MODIFICATIONS {
            ^"Status" INTEGER MIN 20 MAX 35
            ^"Glory"  INTEGER MIN 10 MAX 25
        }
    }

    #k8Rw3NqT6yLm1XcV9bJp4ZsD ^"Ide Tadaji" DEF {
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
    SPEC_VERSION "0.6"
    DEPENDS_ON "BaseSystemID"
    USES_SETTING "SettingID"        # optional
    USES_EXTENSION "ExtensionID"    # optional, repeatable

    THEMES {
        "Theme description"
    }

    CAST {
        FROM EXTENSION "ExtensionID" INCLUDE [#hash ^"NPC Name", #hash ^"Another NPC"]
        FROM FRAME "FrameID" INCLUDE [#hash ^"NPC Name"]
        FROM ARC "OtherArcID" INCLUDE [#hash ^"NPC Name"]

        #hash ^"New NPC" DEF {
            EXTENDS ^"Adversary"
            PROPERTIES {
                ^"Role" STRING "Role in this arc"
                ^"Description" STRING "Brief description"
                # stats as typed fields
            }
        }
    }

    FROM SETTING "SettingID" INCLUDE [#hash ^"Location Name"]    # a SETTING's location, imported

    LOCATION ^"Location Name" #hash {
        DESCRIPTION "Description"
    }

    FLOW {
        PHASE ^"Phase Name" {
            DESCRIPTION "What this phase represents"
            PACING "Suggested pacing guidance"

            SCENE_REF #hash ^"Scene Name"
            SCENE_REF #hash ^"Another Scene"
        }
    }

    SCENE ^"Scene Name" #hash {
        TYPE #hash ^"Scene Type Name"
        LOCATION #hash ^"Location Name"
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
                LEADS_TO [#hash ^"Next Scene"]
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
- `CAST`: NPC roster — imported via `FROM <KIND> "id" INCLUDE [ … ]` or defined inline. The
  `FROM` line is the declaration of that dependency; no `USES_` line is written for it
- `LOCATION`: Place definitions. A SETTING's location is imported with `FROM SETTING "id" INCLUDE [ … ]`
- `FLOW`: Scene sequencing grouped into PHASEs
- `SCENE`: Individual narrative/gameplay units (see Scene Block Specification)
- `REWARDS`: XP and outcome-based rewards

**Example:**

```
ARC "L5R5e_LostWriter" {
    NAME "The Lost Writer in the City of the Rich Frog"
    VERSION "0.5.5"
    SPEC_VERSION "0.6"
    DEPENDS_ON "L5R5e_Core_Core"
    USES_EXTENSION "L5R5e_Children_of_Five_Winds"

    THEMES {
        "Duty versus ethics — must you obey orders that conflict with your conscience?"
        "The tension between freedom and captivity, both literal and spiritual"
        "Art as a vessel for truth, and the dangers of uncovering it"
    }

    CAST {
        # defined once, in the book's GM file, and imported
        FROM EXTENSION "L5R5e_Children_of_Five_Winds_GM" INCLUDE [
            #AEzCQP2Drp0S9YJeerwTbW ^"Miya Tetsua",
            #3XqIrJ05JKkc7Iz9bHiDuy ^"Adventure Ifrit"
        ]

        # defined here
        #q7Lm2XvR9tKc4WbN8sHdPz3F ^"Shinjo Higuchi" DEF {
            EXTENDS #t4540de6f35155c46f41f0 ^"NPC"
            PROPERTIES {
                ^"Role"        STRING "The missing author, possessed by an ifrit"
                ^"Description" STRING "A popular—if a bit controversial—author of stories and poems, Hana-no-Ame (real name: Shinjo Higuchi) has reportedly gone missing while visiting the City of the Rich Frog."
                ^"Combat Conflict Rank"   INTEGER 4
                ^"Intrigue Conflict Rank" INTEGER 1
                ^"Rings" DEF {
                    ^"Air"   INTEGER 3
                    ^"Earth" INTEGER 2
                    ^"Fire"  INTEGER 5
                    ^"Water" INTEGER 1
                    ^"Void"  INTEGER 3
                }
                ^"Skills" DEF {
                    ^"Artisan" INTEGER 1
                    ^"Martial" INTEGER 2
                    ^"Scholar" INTEGER 1
                    ^"Social"  INTEGER 1
                    ^"Trade"   INTEGER 0
                }
                ^"Honor"  INTEGER 60
                ^"Glory"  INTEGER 50
                ^"Status" INTEGER 39
            }
        }
    }

    LOCATION ^"City of the Rich Frog" #b4Wn8KsY2pQx6TcV9mRj3LhD {
        DESCRIPTION "Located at the junction of the Three Sides River and Drowned Merchant River, the City of the Rich Frog is one of Rokugan's most vital river ports, facilitating trade among its people. …"
        TAGS ["urban", "trade-hub", "contested", "imperial-holding"]

        LOCATION ^"Teahouse with No Name" #h2Vq7KcY4tGf8NwJ6pXa5ZrM {
            DESCRIPTION "In the Lion Clan's district within the City of the Rich Frog, an old and renowned teahouse overlooks the banks of the Drowned Merchant River. …"
            TAGS ["lion-district", "social", "formal"]
        }

        LOCATION ^"Manor Gardens" #n9Tc3JwE6yHk2RdL7sUo4BfG {
            DESCRIPTION "Nao recommends moving Higuchi to the manor's interior garden for the confrontation, while Tetsua ensures that any potential prying eyes or innocent bystanders are sent away from the island."
            TAGS ["island", "outdoor", "dangerous", "supernatural"]
        }
    }

    FLOW {
        PHASE ^"Investigation" {
            DESCRIPTION "In Part Two, the PCs follow a trail of clues to various locations in the City of the Rich Frog to track down Hana-no-Ame. …"
            PACING "3-6 scenes depending on PC choices, player-driven exploration"

            SCENE_REF #w5Zp1RmX8eLt4VbK9cJn2QsA ^"Tea Ceremony at the Teahouse with No Name"
            SCENE_REF #d3Sg8QhT5yNk1McA7vPr6WxE ^"Audience with the Governor"
        }

        PHASE ^"Confrontation" {
            DESCRIPTION "In Part Three, the PCs meet with the governor of the City of the Rich Frog and ready their allies. …"
            PACING "1 scene, climactic combat and moral decision"

            SCENE_REF #f6Bn2WxE9zHj4RdL1sUo8KcY ^"The Possessed Author"
        }
    }

    SCENE ^"Tea Ceremony at the Teahouse with No Name" #w5Zp1RmX8eLt4VbK9cJn2QsA {
        TYPE #m8Kd4TqW1zNb6XcR3vLs9JhP ^"Intrigue"
        LOCATION #h2Vq7KcY4tGf8NwJ6pXa5ZrM ^"Teahouse with No Name"
        DESCRIPTION "Whether separately or together, the PCs have arrived at the Teahouse with No Name to gather more information about Hana-no-Ame's disappearance … "

        OBJECTIVES {
            REQUIRED "Appeal to Tea Master Ikoma Kotone."
            OPTIONAL "Avoid breaching tea ceremony protocol"
        }

        CHECKS {
            CHECK ^"Stir the Leaves" #0VDeckbNgpBJyQnoibqr0E {
                SKILL "Courtesy"
                SKILL "Performance"
                RING "Air"
                TN 3
                ON_FAILURE "Each character who fails increases the TN of their next check targeting Kotone by 1."
            }
        }

        RESOLUTIONS {
            RESOLUTION ^"Productive Visit" {
                CONDITION "PCs obtain at least one clue"
                OUTCOME "As the PCs exit the teahouse, they are approached by a man who introduces himself as Daidoji Shin (see profile on page 174). …"
                LEADS_TO [#d3Sg8QhT5yNk1McA7vPr6WxE ^"Audience with the Governor"]
            }
        }
    }

    SCENE ^"Audience with the Governor" #d3Sg8QhT5yNk1McA7vPr6WxE {
        TYPE #x1Gv7RnC5pLw3HbZ8sKt2MdQ ^"Roleplay"
        DESCRIPTION "…"

        RESOLUTIONS {
            RESOLUTION ^"Governor Cooperates" {
                CONDITION "When the PCs are ready"
                OUTCOME "In this part of the adventure, the PCs—having gathered as many clues as they can—attempt to confront Higuchi. …"
                LEADS_TO [#f6Bn2WxE9zHj4RdL1sUo8KcY ^"The Possessed Author"]
            }
        }
    }

    SCENE ^"The Possessed Author" #f6Bn2WxE9zHj4RdL1sUo8KcY {
        TYPE #e5Wj2NxB9cTm4QfV7hDr6LpS ^"Combat"
        LOCATION #n9Tc3JwE6yHk2RdL7sUo4BfG ^"Manor Gardens"
        DESCRIPTION "Nao recommends moving Higuchi to the manor's interior garden for the confrontation, while Tetsua ensures that any potential prying eyes or innocent bystanders are sent away from the island. …"

        PREREQUISITES {
            COMPLETED_SCENES [#d3Sg8QhT5yNk1McA7vPr6WxE ^"Audience with the Governor"]
        }

        OBJECTIVES {
            REQUIRED "Resolve the ifrit's possession of Higuchi"
            OPTIONAL "Save Higuchi's life"
            OPTIONAL "Resolve the situation without destroying the ifrit"
        }

        CONFLICT {
            TYPE #e5Wj2NxB9cTm4QfV7hDr6LpS ^"Combat"
            STAKES "Higuchi's life, the ifrit's fate, and the safety of the City of the Rich Frog"
            OPPONENTS [#q7Lm2XvR9tKc4WbN8sHdPz3F ^"Shinjo Higuchi", #3XqIrJ05JKkc7Iz9bHiDuy ^"Adventure Ifrit"]
        }

        CHECKS {
            CHECK ^"Recognize the Ifrit" {
                SKILL "Theology"
                RING "Fire"
                TN 2
                ON_SUCCESS "Anyone who passes a TN 2 Theology (Fire) check will recognize the spirit as an ifrit."
            }
        }
    }

    REWARDS {
        XP_BASE 3
        CONDITIONAL_REWARDS {
            REWARD "Each hour of play" {
                XP 1
            }
            REWARD "any players felt that their character achieved their personal goal for this adventure" {
                XP 2
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
    SPEC_VERSION "0.6"
    DEPENDS_ON "BaseSystemID"
    USES_SETTING "SettingID"    # optional
    USES_FRAME "FrameID"       # optional

    THEMES {
        "Overarching theme"
    }

    RECURRING_CAST {
        FROM FRAME "FrameID" INCLUDE [#hash ^"NPC Name"]
        FROM ARC "ArcID" INCLUDE [#hash ^"NPC Name"]
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
CAMPAIGN "ChildrenOfFear" {
    NAME "The Children of Fear"
    VERSION "0.5"
    SPEC_VERSION "0.6"
    DEPENDS_ON "CallOfCthulhu7e_Core_Base"

    THEMES {
        "An epic, player-led 1920s journey along Hiuen-Tsiang's Silk Road pilgrim route across China, Central Asia, northern India, and hidden Tibet."
        "A race to decide the fate of a prophesied reincarnation — the 'King of Fear' — bound within Agartha as the balance with Shambhala fails."
    }

    FROM ARC "ChildrenOfFear_Ch1_City_of_Decaying_Splendor"
    FROM ARC "ChildrenOfFear_Ch2_To_the_Gates_of_the_Sun"
    FROM ARC "ChildrenOfFear_Ch3_Song_of_the_Lost_and_Forgotten"
    FROM ARC "ChildrenOfFear_Ch4_Old_Bones"
    FROM ARC "ChildrenOfFear_Ch5_Feast_and_Famine"
    FROM ARC "ChildrenOfFear_Ch6_Liberation"
    FROM ARC "ChildrenOfFear_Ch7_Spirits_of_the_Earth"
    FROM ARC "ChildrenOfFear_Ch8_The_Heart_of_the_World"

    PROGRESSION {
        BETWEEN "ChildrenOfFear_Ch1_City_of_Decaying_Splendor" AND "ChildrenOfFear_Ch2_To_the_Gates_of_the_Sun" {
            DOWNTIME "Overland travel westward out of Peking toward Chang'an (Sian) — weeks of preparation, research, and investigator development."
            ADVANCEMENT "Standard 7e experience: skill-improvement checks from the chapter's rolls; the party builds its expedition and contacts."
        }
    }
}
```

### Scene Block Specification

A SCENE represents a single narrative or gameplay unit within an ARC. Scenes can also be defined standalone within an EXTENSION for reuse across arcs.

#### Scene Types

A scene's `TYPE` is a reference to a **scene type**, an entity the system defines *(v0.6,
DECISION-23)*. The base spec fixes no list. A system's BASE defines one parent, `^"Scene Type"`,
and each of its scene types as a DEF that extends it:

```
#hash ^"Scene Type" DEF { }
#hash ^"Roleplay"      DEF { EXTENDS #hash ^"Scene Type" }
#hash ^"Combat"        DEF { EXTENDS #hash ^"Scene Type" }
#hash ^"Investigation" DEF { EXTENDS #hash ^"Scene Type" }
```

A conflict's `TYPE` is a reference to a **conflict type**, defined the same way under
`^"Conflict Type"`. Both are reference sites (§5d). Where the source leaves the type open, a
`CHOOSE` stands in the slot: `TYPE CHOOSE 1 [#hash ^"Skirmish", #hash ^"Intrigue"]`.

A string in either slot (`TYPE "Roleplay"`) is the older form. It raises a **warning** in a file
that declares a `SPEC_VERSION` below 0.6, or none, and an **error** in one that declares 0.6 or
later.

#### Scene Structure

```
SCENE ^"Scene Name" #hash {
    TYPE #hash ^"Scene Type Name"
    LOCATION #hash ^"Location Name"
    DESCRIPTION "GM-facing overview"

    PREREQUISITES {
        MINIMUM_CLUES count
        COMPLETED_SCENES [#hash ^"Scene Name", #hash ^"Scene Name"]
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
        TYPE #hash ^"Conflict Type Name"
        STAKES "What is at risk"
        OPPONENTS [#hash ^"NPC Name", #hash ^"NPC Name"]
    }

    RESOLUTIONS {
        RESOLUTION ^"Outcome Name" {
            CONDITION "What triggers this outcome"
            OUTCOME "What happens"
            LEADS_TO [#hash ^"Next Scene"]
        }
    }

    # Only for a scene type that summarises several brief moments
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
- `TYPE`: A reference to a conflict type the system defines
- `STAKES`: What the conflict determines
- `OPPONENTS`: NPC references from the CAST

**RESOLUTIONS** — Multiple possible outcomes for the scene.
- `CONDITION`: What triggers this resolution
- `OUTCOME`: Narrative result
- `LEADS_TO`: List of scene IDs that become available

**MONTAGE** — Brief sub-moments, for a scene whose type summarises several (a montage).

#### Standalone Scenes

Scenes can be defined outside an ARC for reuse as encounter templates:

```
EXTENSION "EncounterPack" EXTENDS "L5R5e" {
    NAME "Rich Frog Encounters"
    VERSION "0.1.0"
    SPEC_VERSION "0.6"

    SCENE ^"Roadside Duel" #y4Hc9PvM2xQe7JrW5tLf8NdB {
        TYPE #e5Wj2NxB9cTm4QfV7hDr6LpS ^"Combat"
        DESCRIPTION "A traveling ronin challenges a PC to a formal duel at a crossroads shrine"

        OBJECTIVES {
            REQUIRED "Survive the duel"
            OPTIONAL "Win the duel honorably without lethal force"
        }

        CONFLICT {
            TYPE #e5Wj2NxB9cTm4QfV7hDr6LpS ^"Combat"
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
LOCATION ^"Location Name" #hash {
    DESCRIPTION "Physical and atmospheric description"
    TAGS ["tag1", "tag2"]

    LOCATION ^"Sub-Location" #hash {
        DESCRIPTION "Nested location"
    }
}
```

**Fields:**
- `^"Location Name"`: Caret-quoted display name
- `#hash`: Optional hash ID for cross-referencing
- `DESCRIPTION`: GM-facing description
- `TAGS`: Categorical tags (e.g., `"urban"`, `"dangerous"`, `"sacred"`)
- Nested `LOCATION` blocks: Sub-locations within this location

#### Cross-Referencing Locations

A location defined in a SETTING is imported into a FRAME or an ARC with `FROM SETTING`, and is then
referenced as any other location is:

```
# In a SETTING
SETTING "RichFrog" {
    LOCATION ^"Licensed Quarter" #c2Hn7VdM9sXq5JrW8eLf3TbK {
        DESCRIPTION "The regulated commercial district"
    }
}

# In an ARC
ARC "MarketInquiry" {
    FROM SETTING "RichFrog" INCLUDE [#c2Hn7VdM9sXq5JrW8eLf3TbK ^"Licensed Quarter"]

    SCENE ^"Market Inquiry" #p6Tz1LwQ8nRv3YbK5xGs9FdC {
        LOCATION #c2Hn7VdM9sXq5JrW8eLf3TbK ^"Licensed Quarter"    # the SETTING's location
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

**FROM** — Cross-container import *(v0.6, DECISION-22)*:
```
FROM EXTENSION "ExtensionID" INCLUDE [#hash ^"NPC Name", #hash ^"Another NPC"]
FROM FRAME "FrameID" INCLUDE [#hash ^"NPC Name"]
FROM ARC "ArcID" INCLUDE [#hash ^"NPC Name"]
FROM ARC "ArcID"
FROM SETTING "SettingID" INCLUDE [#hash ^"Location Name"]
```
A `FROM` names the kind of container it imports from, then the container's id. It is itself the
declaration of that dependency: no `USES_` line is written for it. Each `INCLUDE` item is a
reference to something that container defines (§5d).

A `FROM "id"` with no kind is the older spelling. It raises a **warning** in a file that declares
a `SPEC_VERSION` below 0.6, or none, and an **error** in one that declares 0.6 or later.

**Declaring a block.** A named block (`SCENE`, `LOCATION`, `ENTRY`, `CHECK`) gives its name and then
its hash, by convention: `SCENE ^"Scene Name" #hash {`. Hash before name is also legal. A reference
to a scene, a location or a cast member is written as any other reference (§5d): `#hash ^"Name"`.
The hash makes the block a target for any file; the name alone is a label inside the file that
declares it (§20).

**LEADS_TO** — Scene transitions within RESOLUTION blocks:
```
LEADS_TO [#hash ^"Scene Name", #hash ^"Another Scene"]
```

### Dependency Hierarchy

Containers form an acyclic dependency graph. Each line lists what a container may depend on:

```
CAMPAIGN  (.campaign)  ->  ARC, FRAME, SETTING, BASE
ARC       (.arc)       ->  ARC, FRAME, EXTENSION, SETTING, BASE
FRAME     (.frame)     ->  SETTING, BASE
EXTENSION (.ttrpg)     ->  BASE
SETTING   (.setting)   ->  nothing
SCENE blocks sit inside an ARC, or inside an EXTENSION as reusable encounters
```

| From | To | By |
|---|---|---|
| CAMPAIGN | BASE | `DEPENDS_ON` |
| CAMPAIGN | SETTING | `USES_SETTING` |
| CAMPAIGN | FRAME | `USES_FRAME`, `FROM FRAME` |
| CAMPAIGN | ARC | `FROM ARC` |
| ARC | BASE | `DEPENDS_ON` |
| ARC | SETTING | `USES_SETTING`, `FROM SETTING` |
| ARC | EXTENSION | `USES_EXTENSION`, `FROM EXTENSION` |
| ARC | FRAME | `FROM FRAME` |
| ARC | ARC | `FROM ARC` |
| FRAME | BASE | `DEPENDS_ON` |
| FRAME | SETTING | `USES_SETTING`, `FROM SETTING` |
| EXTENSION | BASE | `EXTENDS` |

#### Dependency Rules

1. **SETTING** has no dependencies — it is system-agnostic and self-contained
2. **FRAME** requires exactly one BASE via `DEPENDS_ON` and optionally one SETTING via `USES_SETTING`
3. **ARC** requires exactly one BASE via `DEPENDS_ON`, optionally one SETTING via `USES_SETTING`, and optionally one or more EXTENSIONs via `USES_EXTENSION`
4. **CAMPAIGN** requires exactly one BASE via `DEPENDS_ON`, optionally one SETTING, and optionally one FRAME via `USES_FRAME`
5. **Cycles are forbidden** — no container may directly or transitively depend on itself
6. **SCENE** blocks exist within ARCs or within EXTENSIONs (as standalone reusable encounters)
7. A `FROM` names the kind of the container it imports from, and that container must be in the loaded set and be of that kind. The `FROM` line is itself a dependency of the file and counts under rule 5 *(v0.6, DECISION-22; before v0.6 this rule required the container to be declared a second time in the header)*

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
            ^"Skills" DEF {
                ^"Command" INTEGER MIN 0 DEFAULT 0
                ^"Tactics" INTEGER MIN 0 DEFAULT 0
                # … one property for each skill
            }
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

These keywords are reserved by the base spec inside the narrative container named, and only there
(§15, DECISION-29). Outside it a system may use the word for a field of its own.

**SETTING:** `THEMES`, `HISTORY`, `ENTRY`, `PERIOD`

**FRAME:** `STARTING_CONDITIONS`, `MODIFICATIONS`

**ARC:** `CAST`, `FLOW`, `PHASE`, `SCENE_REF`, `REWARDS`, `XP_BASE`, `CONDITIONAL_REWARDS`, `REWARD`, `XP`

**SCENE:** `TYPE`, `PREREQUISITES`, `MINIMUM_CLUES`, `COMPLETED_SCENES`, `CONDITION`, `OBJECTIVES`, `REQUIRED`, `OPTIONAL`, `CHECKS`, `CHECK`, `SKILL`, `RING`, `TN`, `RING_TN`, `ALTERNATIVE`, `APPROACH`, `ON_SUCCESS`, `ON_FAILURE`, `CLUES`, `CLUE`, `DISCOVERED_BY`, `CONFLICT`, `STAKES`, `OPPONENTS`, `RESOLUTIONS`, `RESOLUTION`, `OUTCOME`, `MONTAGE`, `MOMENT`

**LOCATION:** `TAGS`

**CAMPAIGN:** `RECURRING_CAST`, `PROGRESSION`, `BETWEEN`, `AND`, `DOWNTIME`, `ADVANCEMENT`

**Cross-container:** `DEPENDS_ON`, `USES_SETTING`, `USES_FRAME`, `USES_EXTENSION`, `FROM`, `INCLUDE`, `LEADS_TO`

---

## 19. Versioning *(v0.4)*

Three distinct version axes, kept separate:

- **DSL-spec version** — the version of *this specification*. Files pin the spec they target via `SPEC_VERSION`.
- **File content `VERSION`** — the version of a file's game content (semantic or date-based), independent of the spec version.
- **Directory organization** — a system keeps its files under a content-version directory (`0.5/`), and each filename carries that version too (`l5r5e-0.5-core-base.ttrpg`), so a file names its version wherever it is copied. That number is the corpus's content version. It is neither the file's own `VERSION` nor its `SPEC_VERSION`.

`DEPENDS_ON "Parent" VERSION "x"` says the parent's *content* version is x or later (§3, DECISION-35). Tooling treats `SPEC_VERSION` as the conformance target.

### Editions & version namespaces *(v0.4)*

An **edition** (or a major/beta version line) is an **identity namespace**. Hash identity is **stable
within** it, and nothing resolves across it: an edition change is a **breaking change**, so "the
same" entity in a newer edition is a *new* definition (§5), not an overlay on the old one. Editions
are therefore kept as **separate systems** — e.g. `arm5e` (Ars Magica 5th) vs. `armdef` (the
Definitive edition), or a system's beta lines vs. its final rules. Within one edition, core +
sourcebooks + errata share the namespace and compose by precedence (§13).

A hash stands in two editions on purpose in two cases only:

- The spec's **dice module** (§8) is edition-neutral. It is one file, every edition includes it,
  and its hashes are the same in each.
- A **port** keeps the hashes of the file it was made from (*Ports*, below).

An entity converted afresh for another edition has a hash of its own: the cores of `arm5e` and
`armdef` share none, and `^"Faerie Blood"` has one hash in each.

**Forward-porting.** A sourcebook published for an older edition does **not** automatically apply to a
newer one — it references the old edition's hashes. To use it under a newer edition, generate a **new
`.ttrpg` of that sourcebook converted to the newer edition**, targeting the newer edition's
definitions and diffs — a derived artifact, not an automatic overlay.

### Ports *(v0.6, DECISION-26)*

That derived artifact is a **port**: a file made from a file of another edition. It says so in its
header.

```
EXTENSION "ARMDef_Grogs_Abilities" {
    NAME "Ars Magica Fifth Edition, Grogs - New Abilities"
    VERSION "0.5.2"
    SPEC_VERSION "0.6"
    RELEASE_DATE "2026-07-25"
    ORIGIN "arm5e" EXTENSION "ArM5_Grogs_Abilities"
    DEPENDS_ON "ARMDef_Grogs_Core_Ext"

    #tu5h4xn3dqOCTXEYMVzZrEWh ^"Craft Poppets" DEF {
        EXTENDS #tLzvYKtdVMBerES3oaOuTyEy ^"Ability"
        # ...
    }
}
```

- **`ORIGIN "edition" <KIND> "id"`** stands in the header, once. It names the edition the file was
  ported from (an edition id, as a bridge names one, §21) and the container it was made from:
  `EXTENSION`, `BASE`, `SETTING`, `FRAME`, `ARC` or `CAMPAIGN`.
- **A port keeps its anchors.** Every definition and named block the port carries over keeps the
  hash it has in the origin. `^"Craft Poppets"` is `#tu5h4xn3dqOCTXEYMVzZrEWh` in both files.
- **A shared hash is one entity, carried over.** A hash that stands in a port and in its origin has
  the same name in both. The two bodies may differ, since each is written for its own edition.
- **A port's references are its own edition's.** Every reference in a port resolves in the port's
  edition (§20). A reference to the other edition's core is re-pointed: `^"Ability"` is
  `#tWPnyoi9rSMWyMo7Njlo9XM2` in arm5e and `#tLzvYKtdVMBerES3oaOuTyEy` in armdef, and the port
  writes the second.
- A port may leave out an entity its own edition already holds, with a `REPRINT`, an `ALIAS` or a
  `MODIFY` in its place (§5b, §13). It may add definitions of its own, each under a new hash.
- A port and its origin are files of two editions. They are never loaded in one composition set
  (§13).
- **Outside a port, a shared hash means nothing.** Two editions may hold the same hash by accident,
  and no tool may read that as identity. Where no port carries an entity across, the
  correspondence between two editions is a bridge's to state (§21).

The machine-readable edition diff this presupposes is a **`.bridge` file (§21)** — the one container
with two dependency lineages, holding a *directed* correspondence between two namespaces. A bridge
does not weaken the rule above: it asserts correspondence, explicitly and third-party, precisely
because identity does not carry. (The generator that consumes a bridge to emit the derived artifact
remains future work.)

## 20. Validation *(v0.4)*

Validation of `.ttrpg`/`.lore` files has two levels, both operating on the files themselves:

1. **Lint — spec adherence.** Does the file conform to this grammar/spec (structure, types, reserved-word usage, canonical forms)? `ttrpg.peg` states the syntax and `check_grammar.py` runs it *(v0.6, DECISION-31)*: every good fixture in this repo must be accepted and every planted syntax fault in `tests/grammar-bad` refused. `ttrpg_validator.py` is a second reader. It scans tokens and does not use the grammar, so the two can disagree about what is well-formed, and a disagreement is a defect in one of them.
2. **Coherence / consilience — referential integrity.** Across **an edition's** corpus: is everything referenced actually defined? Do `^"Name"`, `#hash`, `EXTENDS`, `APPLIES TO`, `DEPENDS_ON` resolve to real, correctly-typed targets — **and unambiguously** (§5d)? No **dangling** anchors, and **no hash declared twice**: a second DEF under a hash the corpus already declares is a **duplicate anchor**, an error *(v0.6, DECISION-27; before v0.6 the spec read it as an implicit override, which the validator never accepted)*. Two restatements are not duplicates: a named block stated again under its own hash and name, and a codex `ENTITY` restated to add sources (§25). The same hash on two different names is an error in every case.

**A value is checked against what its definition extends** *(v0.6, DECISION-32)*. The validator
follows each `EXTENDS` chain to the nearest declaration of a property and reports:

| What | Severity |
|---|---|
| a cycle of `EXTENDS` (§6) or of `ALIAS` (§5b) | error |
| a bound reference with more arguments than its base's `PARAMETERS`, with arguments where the base declares none, or with a string outside a parameter's list (§5b) | error |
| an `INTEGER` outside the `MIN` / `MAX` it inherits (§5, §8) | gated |
| a value outside the `ENUM` it inherits (§8) | gated |
| a value of another kind than its type keyword, or than the type it inherits (§8) | gated |
| a named member of a `LIST OF ^"Type"` that does not extend the type (§8) | gated |
| one property written twice in a definition (§8) | gated |
| an instance without a property a type up its chain declares `REQUIRED` (§8, DECISION-34) | gated |

"Gated" is a warning in a file that declares a `SPEC_VERSION` below 0.6, or none, and an error from
0.6. `FIAT "reason"` waives a gated finding: a value the source prints outside its type's range is
what `FIAT` is for (§8).

A version pin is checked too: the loaded parent is at the pinned version or a later one (§3,
DECISION-35), and an older parent is an error.

So are a file's dependencies (§3, DECISION-36): each names a loaded file, no two files depend on
each other, a file id is declared once, an `EXTENSION` names a parent and a `BASE` does not. The
order files are loaded in is not checked. The validator is given no order.

Not checked, and why: a value for a property no type declares, which no rule forbids; the fields
of a nested or unnamed DEF; and a misspelt keyword, which reads as a system's own (§15). A name that
two definitions share is not followed up a chain: the reference needs its hash (§5d).

**The modification system is part of coherence** *(v0.4, 2026-07-25)*. A `MODIFY` / `OVERRIDE`
naming a target that does not exist modifies nothing, silently and permanently — rename the parent
definition, or mistype the target, and the overlay simply stops applying with no diagnostic. So
every `MODIFY ^"X"` / `OVERRIDE ^"X"` target must resolve in the loaded corpus (**error** if not),
alongside the per-directive rules in §13: `SET` against an undeclared property and `ADD_TO` /
`REMOVE_FROM` against a non-`LIST` are errors; a colliding `ADD`, a `REMOVE_FROM` of an absent
value, and an enum narrowed out from under a live instance are warnings.

**What counts as "defined."** *(v0.6, DECISION-24)* There are two tiers.

1. **A definition is a name every file may use.** Name resolution collects `^"Name" DEF`
   (including nested and `ADD`-ed ones), `ACTOR` / `TEMPLATE` definitions, `ALIAS` names, and the
   `ENTITY` nodes of a codex (§25).
2. **A named block is a target through its hash.** A block that gives a name after its keyword
   (`SCENE ^"Name" #hash {`, `LOCATION ^"Name" #hash {`, `ENTRY ^"Name" #hash {`) declares an
   **anchor** when it carries a hash: any file may reference it as `#hash ^"Name"`, the hash is
   unique in the corpus as a DEF's is, and the name must be the block's own. The block's **name**
   is a label local to the file that declares it. A reference by name alone resolves to it only
   inside that file, and WARNs as any hashless reference does (§5d). A block with no hash can be
   named only there.

Before v0.6 this section counted definitions and "nothing else", while §16 had scenes point at
locations and §25 called a codex entity a first-class caret target.

A bare `^"Name" { … }` block, with no keyword before the caret, declares no name: a caret that
opens a statement without `DEF` resolves nothing. Frozen pre-0.4 content directories (§19) that
still use the old spelling are historical artifacts and are not expected to validate against this
spec version.

**Intentional exceptions:** both levels honor `FIAT` (§8) — a value or element marked `FIAT "reason"` is exempt from the findings it would otherwise raise (constraint violations and, cascading, completeness). Because each `FIAT` carries a reason, the full set is reportable for audit.

**Out of scope for the DSL:** *sophisticated rules validation* (evaluating whether game rules are internally consistent or produce legal characters) runs **downstream**, in the tools that consume `.ttrpg`/`.lore`, and is built later. The DSL guarantees a well-formed, coherent knowledge base — not a rules engine.

### Ports — checked against their origin *(v0.6, DECISION-26)*

A port (§19) declares `ORIGIN "edition" <KIND> "id"`. The validator checks:

- **Form (lint).** The line names an edition id, a container kind and a container id, and a file
  has at most one.
- **Not loaded together.** If the origin container is in the loaded set, that is an **error**: a
  port and its origin are two editions' files (§13).
- **Against the origin's corpus.** Given a corpus for the origin's edition
  (`--corpus arm5e="…/arm5e/0.5"`, the flag a bridge uses), the origin container must exist there
  and be of the kind named, and every hash the port shares with it must carry the same name in
  both. Each failure is an **error**.
- **No corpus given.** The port's references are still resolved in its own edition. The claim
  about its origin is not checked, and the validator says so in one **warning** per edition id.

A hash that two editions share outside a declared port is not a finding. No rule gives it a
meaning (§5).

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
across it, a declared port aside. §13 scopes a composition set to one edition namespace, and §20 scopes coherence to one
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
| `#hash` re-stated for the *same* entity name across files (amend) | allowed |
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
**Last Updated:** 2026-11-12
**Status:** Canonical (supersedes v0.4)
