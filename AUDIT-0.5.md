# Audit of Titterpig DSL v0.5

**Date:** 2026-11-11
**Audited:** `titterpig-dsl` at commit `48d27e5` (2026-10-17): `titterpig-dsl-spec.md`,
`AUTHORING-GUIDELINES.md`, `ttrpg.peg`, `ttrpg_validator.py`, `check_references.py`,
`check_constructs.py`, `check_structure.py`.
**Checked against:** `titterpig-dsl-l5r5e/0.5`, `titterpig-dsl-vtm5e/0.5`,
`titterpig-dsl-arm5e/arm5e/0.5`, and a construct census over the `0.5/` directory of all 21 corpus
repos.
**Purpose:** input to DSL 0.6.x. This file records findings. It decides nothing.

## How to read this file

Each finding has an ID (A = the spec text, B = grammar and validator, C = design), what the spec
says, what is wrong, and the evidence. Every number comes from a command run on 2026-11-11; Appendix 2
gives the method for each. The audit changed no file in any repo.

Each finding carries a **Status**. All start as `open`. The decision log at the end is filled in as
the findings are walked through with the owner.

## Verdict

The core design holds. Section 5d (the hash is the referent) works in practice: over the three
corpora `check_references.py` reports 16,282 reference sites with 0 hashless and 0 ambiguous, while
1,901 names in those corpora are defined more than once. Stand-off annotation (`REFERENCES`,
`EMPHASIS`), `GUIDANCE` and `.bridge` are well reasoned and in wide use.

The problems are in four places.

1. The spec document has grown by accretion. Several sections contradict each other, and several
   examples break the rules stated beside them.
2. The README says the grammar and validator are aligned to the spec. The grammar is run by no tool
   and rejects forms every corpus writes. The validator checks a small part of what the spec says is
   checked.
3. The type system is thin for RPG data. Corpora store references and numbers as strings.
4. Several specified constructs have no use in any corpus. Several constructs in heavy use are not
   in the spec.

---

## A. The spec text

### A1. The first example of "structure over prose" loses content

**Status:** applied 2026-11-11 (uncommitted), awaiting the owner's sign-off to close. `CHOOSE n`
replaces `CHOICE` (DECISION-15); `SET` and `TRANSFORM` (DECISION-16); `REF` (DECISION-17); `BOOLEAN`
inline value; the §1 example is three full DEFs with opaque hashes, and its structured step uses
all of the above. Follow-ups F1 to F4 and the to-dos below remain open.

**Resolution.** The example in spec §1, `AUTHORING-GUIDELINES.md` §1 and
`.claude/skills/titterpig-dsl/SKILL.md` (a third copy, found while fixing) now follows the l5r5e Hida
entry: separate `Ring Increase`, `Skill Increases`, `Glory` and `Wealth` properties, with the ring
written as `^"Ring" CHOICE [ ^"Earth", ^"Fire" ]`. The §11 `FAMILIES` block now lists carets, as
l5r5e's does. Checked: the new example in a wrapper validates with 0 errors, and a misspelled
`CHOICE` option in it is reported as an undefined reference. The text below describes the spec
as audited.

§1 and `AUTHORING-GUIDELINES.md` §1 both give this pair:

```
# Avoid
^"Ring Increase" STRING "+1 Earth or Fire, +1 Command, Glory 44, 4 koku"
# Prefer
^"Ring Increase" DEF { ^"Earth" INTEGER 1  ^"Command" INTEGER 1  ^"Glory" INTEGER 44  ^"Koku" INTEGER 4 }
```

- The "Prefer" form drops "or Fire". The source offers a choice of two rings; the structured form
  grants Earth.
- It puts a ring increase, a skill increase, a starting Glory value and a sum of money under one
  property called "Ring Increase", all as sibling integers. `Earth 1` is an increment and `Glory 44`
  is an absolute value, and nothing distinguishes them.
- §11 then shows the same string as a model: `FAMILIES { ^"Hida" "+1 Earth or Fire, +1 Command,
  +1 Tactics, Glory 44, 4 koku" }`. The two copies of the string differ (§1 omits Tactics).
- The guidelines state "completeness overrides structure" a few lines below the example that breaks it.

The l5r5e corpus encodes the same family better (`l5r5e-0.5-core-character.ttrpg:339`): separate
`Ring Increase`, `Skill Increases`, `Glory` and `Wealth` properties. It writes the choice as
`^"Ring Increase" DEF { CHOOSE 1 [^"Earth", ^"Fire"] INTEGER 1 }`, a system keyword. The base spec's
own `CHOICE [ … ]` (§5b) is unused in l5r5e, which has about 300 `CHOOSE n […]` statements.

### A2. Inline markup is banned in one section and demonstrated in two others

**Status:** open

§5c: "No inline markup is ever inserted into the text." DECISION-7 rejected `[[…]]` markup for that
reason, and `EMPHASIS` exists so that bold is recorded beside the text.

- §14 "Embedded References in Strings" still documents `ACTIVATION "When you make a ^\"Fitness\"
  check..."` as a feature. §11 uses it (`"Gain the ^\"Blessed Lineage\" distinction"`).
- §21's `PROCEDURE` example has `TEXT "**Abilities:** Leave at the old value…"` in a field the
  section calls verbatim.

Evidence: l5r5e holds 420 embedded `^\"…\"` references (100 distinct names). 14 of the distinct names
resolve to no definition, and no gate reads inside strings. vtm5e has 2,302 string literals
containing `**` (1,900 of them `DESCRIPTION`), arm5e 1,267. They are run-in headings such as
`**IMMUNE TO THE CALL**` and `**Dwarf Blood:**`. vtm5e descriptions also open with `*italic*`
fiction. No gate counts either.

Across all corpora (string literals outside comments, counted 2026-11-11):

| Corpus | `**bold**` | `*italic*` | bullet lines | Markdown table rows | embedded `^\"` |
|---|---|---|---|---|---|
| vtm5e | 2,286 | 2,297 | 667 | 0 | 0 |
| arm5e | 1,220 | 1,941 | 243 | 0 | 0 |
| tor2e | 935 | 984 | 0 | 0 | 0 |
| daggerheart | 516 | 251 | 66 | 0 | 0 |
| draw-steel | 462 | 361 | 475 | 285 | 0 |
| dnd5.5e | 244 | 1,023 | 9 | 0 | 0 |
| dnd5e | 116 | 736 | 43 | 0 | 0 |
| troika | 63 | 167 | 0 | 0 | 0 |
| l5r5e | 0 | 0 | 0 | 0 | 300 |

The other eleven corpora have no bold and at most five italics each. The italic column is a
pattern match and will include some literal asterisks. The counts are strings, so l5r5e's 420
embedded references sit in 300 strings.

So three content models for a string are live: plain text with stand-off `EMPHASIS` and
`REFERENCES` (what §5c says, and what root, both Pendragons, marvelmultiverse, aegean and
coyotecrow do); Markdown inside the string (eight corpora); and embedded caret references
(l5r5e). The spec states the first, shows the other two in its examples, and no gate checks any.

### A3. The §16 examples break the §16 rules

**Status:** open

- Dependency rule 7: a `FROM` must target a container already declared as a dependency. The ARC
  example writes `CAST { FROM "RichFrogFrame" INCLUDE [#ide_tadaji] }` and declares no dependency on
  the frame. An ARC has no `USES_FRAME` keyword. `FROM ARC "…"` (in a CAMPAIGN, and in an ARC's
  `CAST`) has no `USES_ARC` to satisfy the rule.
- The actor schema in §17 declares `^"Skills" LIST OF ^"Skill"`. The instances in §16 fill it with
  `^"Skills" DEF { ^"Social" INTEGER 4  ^"Trade" INTEGER 5 }`, a different type, keyed by skill
  groups.
- A scene's location is written `LOCATION #location_ref` in the structure block and
  `LOCATION ^"Licensed Quarter"` in the example. A cast import is `FROM "FrameID" INCLUDE` in one
  place and `FROM FRAME "FrameID" INCLUDE` in another.
- Hash IDs in §16 are `#ide_tadaji`, `#ink_room`, `#commission`: short, semantic, with underscores.
  §5 requires `[A-Za-z0-9]{16,}` and opacity. l5r5e's `.arc` files follow the examples
  (`#governors_neighborhood`).

### A4. §20's definition of "defined" contradicts §16 and §25

**Status:** open

§20: name resolution collects `^"Name" DEF`, `ACTOR`/`TEMPLATE` definitions and `ALIAS` names "and
nothing else". §25: a codex `ENTITY` "is a first-class caret target". §16 references a `LOCATION` by
caret. `check_references.py` already indexes anchors from every container, with a comment naming an
l5r5e `LOCATION` that a `REFERENCES` entry targets.

### A5. The spec's example of two editions shares most of its hashes

**Status:** open

§5 and §19: hash identity carries nothing across editions; the same entity in another edition has a
different hash. §19 gives arm5e and armdef as the example of separate editions. 8,299 of the 9,959
DEF anchors in `arm5e/0.5` also appear in `armdef/0.5`, because armdef is regenerated from arm5e.

### A6. Implicit override is legal in §13 and an error in the validator

**Status:** open

§13: a later file may restate an entity's hash, and by load order that replaces the earlier
definition. `ttrpg_validator.py` reports any recurring hash as `duplicate anchor` (proven by the
probe, Appendix 1). §20 has carried a note that this is "a pending change" since v0.4.

The synthesist does something the spec does not describe. With no hash match it treats a same-name
DEF of a compatible type as an implicit override of the earlier one, even when the two carry
different hashes (`titterpig-synthesist/internal/resolve/collect.go:66`). §5d says distinct hashes
are distinct entities.

### A7. `.actor` is defined one way and written two other ways

**Status:** open

§2: an `.actor` file is "a `.ttrpg` file scoped to exactly one character definition (a single `DEF`
block)". §3 says every `.ttrpg` opens with `BASE` or `EXTENSION`. The two sentences cannot both
hold. On disk, 2,420 `.actor` files open with an `EXTENSION` wrapper and 670 open with a bare
`#hash ^"Name" DEF`. `l5r5e-0.5-blood-of-the-lioness-pregens.actor` holds 7 DEFs, one of them a type
declaration. arm5e uses `.actor` for covenants. A bare `.actor` has no `SPEC_VERSION`, `VERSION` or
`DEPENDS_ON`, so nothing in the file says which system it belongs to.

### A8. Stale and inconsistent text

**Status:** open

- §0 says the decisions run "through DECISION-13". DECISION-14 follows.
- The footer says "Last Updated: 2026-08-08". Dated addenda in the text run to 2026-10-17.
- §19 calls this specification "v0.4". `AUTHORING-GUIDELINES.md` is titled v0.4. The validator's
  docstring says "v4".
- §5c announces "Three additions" and lists four.
- §2 "File Organization" (`systems/{system_id}/core.ttrpg`, `extensions/…`) matches no repo.
- §19: "Version lives in the directory, not re-encoded redundantly in every filename." The naming
  rule in the guidelines and `DSL/CLAUDE.md` puts the version in every filename.
- Hash uniqueness is "per entity, within an edition" in §5 and "globally unique" in the guidelines.
- §15's reserved-word list omits about 25 keywords the spec defines elsewhere, among them
  `SPEC_VERSION`, `PARAMETERS`, `CHOICE`, `PICK`, `WHERE`, `REFERENCES`, `EMPHASIS`, `HOOKS`,
  `FORMALITY`, `OPTIONAL`, `SELECT`, `SELECTIONS`. It lists `TRIGGER` as system-defined; §23 uses
  `TRIGGER` in `HOOKS`, the grammar reserves it, and §5c's own `EMPHASIS` example uses it as a
  system field.
- The reserved SCENE keywords `SKILL`, `TYPE`, `REQUIRED` and `OPTIONAL` are also used in §11 and
  §8 with other meanings. The spec does not say whether "reserved" depends on context.
- §8's type table gives modifiers per type (`STRING … [REQUIRED|FIXED]`, `INTEGER … [REQUIRED]`),
  then says modifiers "apply to any type".
- §10 allows `TEXT` as an alias for `DESCRIPTION`. §21 to §24 use `TEXT` as a field of its own.

---

## B. Grammar and validator

### B1. No tool runs the grammar, and it rejects what the corpora write

**Status:** open

A search of `Titterpig/DSL` and `Titterpig/Utilities` finds no reference to `ttrpg.peg` in any
script or program. The file uses `!{RESERVED_WORD}`, which is not PEG notation, and defines no
`RESERVED_WORD` rule. As written it rejects:

| Form | Where the grammar fails | Use in corpora |
|---|---|---|
| a `SETTING`, `FRAME`, `ARC` or `CAMPAIGN` file | `FILE` lists only `BASE`, `EXTENSION`, `BRIDGE`, `SELECTIONS`, `CODEX` | 17 `.arc`, 8 `.frame`, 18 `.setting` in the three corpora |
| a bare `.actor` | same | 670 files |
| `^"Flag" BOOLEAN true` | `BOOLEAN_TYPE` takes modifiers only | 637 (l5r5e, arm5e) |
| `^"Kind" ENUM "Gift"` | `ENUM_TYPE` requires a bracket list; §8 has no such form | 10,601 across 7 corpora |
| `^"Feats" CHOICE PICK 1 [ … ]` as a property | `PROPERTY_TYPE` has no `CHOICE`; §5b allows it | 271 in root, teeth and arm5e |
| `APPLIES TO [#hash ^"Samurai"]` | `CARET_REF_LIST` has no hash | every such site in l5r5e |
| `LIST OF #hash ^"Skill"` | `LIST_OF_TYPE` has no hash | all 27 `LIST OF ^` sites in the three corpora |
| `[#hash ^"A", #hash ^"B"]` | `BRACKET_ITEM` is a caret or a hash, comma-separated | the §5d form for a list |
| `SCENE ^"Name" #id {` | `GENERIC_LABEL` takes one label | §16's own form |
| `DESCRIPTION "…"` in a DEF body | listed as reserved, with no rule in `BODY_ENTRY` | 23,685 in the three corpora |
| `TRIGGER "…"` as a system field | reserved for `HOOKS` | Root, every move |

The grammar also documents a bare `OVERRIDE ^"X"` statement inside a DEF body. §13 does not mention
it.

### B2. The validator checks little of what the spec says is checked

**Status:** open

`ttrpg_validator.py` is a token scanner. Its lint level checks lexing, brace balance, hash length
(as a warning), a `FIAT` reason, the presence of `SPEC_VERSION`, and an inline integer against a
`MIN`/`MAX` on the same line. Its coherence level resolves names at a fixed set of keywords.

The probe corpus in Appendix 1 plants 16 violations. The validator reported two: the restated hash
(A6, which the spec calls legal) and a wrong-case name. These passed all four gates:

| Planted | The spec's position |
|---|---|
| `SPEC_VERSION "9.9"` | §19: the conformance target |
| `DEPENDS_ON "Probe_Core" VERSION "99.0"` | §3: "a required parent version" |
| instance `^"Air" INTEGER 7`, inherited `MIN 1 MAX 5` | §5: "Coherence validation checks each value against the constraint inherited" |
| `^"Kind" STRING "Neither"` against `ENUM ["Gift","Burden"]` | §8 |
| `^"Weight" INTEGER "heavy"` | §8 |
| `REQUIRED` property absent from the instance | §8: "must be provided" |
| `LIST OF ^"Skill"` holding entities that are not Skills | §8 |
| `^"Wrathful"("Huge")` against `OF ["Major","Minor"]` | §5b: "a coherence error" |
| `^"Plain"("x","y")` where `Plain` declares no `PARAMETERS` | §5b: "a coherence error" |
| `CHOICE PICK 5 [ two options ]` | §5b: "`PICK n` must not exceed the option count" |
| `EXTENDS` cycle between two DEFs | §16 forbids cycles for containers; DEFs are unstated |
| `ALIAS` cycle | §5b: "alias chains must be acyclic" |
| `PROPERTEIS { … }` | parsed as a system block |
| `EXTEND ^"Nonexistent Thing"` | parsed as a system keyword; the reference is never resolved |
| stray `>= \| →` | the tokenizer skips unknown characters |
| a DEF after the container's closing brace | §3 |

`FIAT` (§8) waives constraint and completeness findings. Most of those findings are never raised, so
most `FIAT`s waive nothing.

Other gaps in the gates:

- A hash under 16 characters is a warning in the validator. §5 states the length as the format, and
  §25's table says "error if <16".
- The validator and the grammar accept `_` in a hash. §5 says `[A-Za-z0-9]`.
- `check_constructs.py` reads only `.ttrpg` files and matches `CONCERNS [ … ]` and `THEN [ … ]` on
  one line. arm5e's 1,087 `.actor` files and any list wrapped across lines are not checked.
- The validator does not read `.selections` files.
- The three lexers disagree on comments. §4 and the grammar: `#` then a space or end of line. The
  validator: `#` then any non-alphanumeric. `#TODO` is a hash ID in all three.

### B3. Name equality is undefined, and the gates use two different rules

**Status:** open

The spec does not say when two names are the same (case, punctuation, straight or curly
apostrophe, Unicode form). The validator compares exactly. `check_references.py` and
`check_constructs.py` lower-case the name and drop everything that is not a letter or digit. Under
that rule tor2e's `^"+2"`, `^"−2"`, `^"#2"` and `^"2"` are one name. Names that differ exactly and
fold together: vtm5e 221 groups (`Extortionist` / `Extortionist:`), arm5e 27, tor2e 24, root 23
(`Don't` / `Don’t`), l5r5e 8.

In the probe, `EXTENDS ^"virtue"` is an undefined reference to the validator and a resolved,
hashless reference to `check_references.py`.

### B4. `REQUIRED` means one thing in §8 and another in the only tool that checks it

**Status:** open

§8: "`REQUIRED` — must be provided". The validator does not check it. `check_structure.py` fails
only when a `REQUIRED` property is populated on zero instances of its type. On arm5e it prints
`^"Ability".^"Ability Type" REQUIRED, on 136/167` as a note, and fails on `^"House"` being populated
on 0 of 13 `Magus` instances.

Related: `check_structure.py` fails two of the three corpora today (vtm5e: 11 `PROPERTIES` blocks
to 12,724 `DESCRIPTION`s, 252 empty DEFs; arm5e: the `House` error). Neither repo's `gates.sh` runs
it. l5r5e has no `gates.sh`. vtm5e writes its properties directly in the DEF body with no
`PROPERTIES` block (12,839 `STRING` values, 11 blocks), which §0 calls non-canonical.

### B5. Version pins and the dependency model

**Status:** open

- `DEPENDS_ON "Parent" VERSION "x"`: the spec does not say whether the match is exact, minimum or a
  range. No tool checks it. All 68 pins in l5r5e name `0.5.9`; the parent declares `0.5.10`. The
  standing rule to bump `VERSION` on every edit guarantees this drift.
- §3: an EXTENSION declares "a parent". 25 arm5e files declare more than one `DEPENDS_ON`.
- Both parent forms are in use. vtm5e heads 326 files with `EXTENSION "X" EXTENDS "Y"`, arm5e
  writes `DEPENDS_ON` 2,522 times, and l5r5e uses both (29 and 103). The spec keeps both and does
  not say what a file with both means.
- §13: load order is precedence. No DSL construct states a load order. `DEPENDS_ON` gives a partial
  order; the rest is the consumer's manifest, which the spec does not define.

---

## C. Design

### C1. The type system sends references and numbers into strings

**Status:** open. Partly addressed 2026-11-11 under A1: `REF` (DECISION-17) gives a property one
entity reference, and `SET` / `TRANSFORM` (DECISION-16) give a change to a value a form. No corpus
uses either yet. The list of entities each with a value, decimals, signed values, dice and units
are untouched.

What §8 lacks:

- a property that holds one reference to an entity. The spec's own examples write
  `^"Clan" STRING "Crab"`, `^"Parent" STRING "Dominate"`, `^"Technique" STRING "Creo"`.
- a list of entities each with a value: skills with ranks, disciplines with dots, abilities with
  score and specialty. §16 uses a nested DEF for it and §17 declares `LIST OF ^"Skill"`.
- decimals, signed values as printed (`+2`), dice (`2d6+3`), ranges, quantities with units.
- the value form of `LIST OF ^"Type" [ … ]`. The table shows values only for `LIST OF STRING`. Ten
  corpora use the entity form (marvelmultiverse 2,367 times).
- an inline `ENUM` value (B1).

Evidence:

| Corpus | `STRING` values equal to a defined entity's name | string list members equal to a defined entity's name | bare numbers typed `STRING` |
|---|---|---|---|
| l5r5e | 1,509 of 6,191 (24%) | 702 of 6,029 (12%) | 179 |
| vtm5e | 1,022 of 12,839 (8%) | 6 of 1,425 (0%) | 1,242 |
| arm5e | 13,642 of 61,598 (22%) | 1,325 of 6,956 (19%) | 3,704 |
| marvelmultiverse | 15,746 of 32,346 (49%) | 683 of 1,819 (38%) | 7,484 |
| tor2e | 1,607 of 6,507 (25%) | 425 of 2,995 (14%) | 208 |
| root | 2,426 of 7,874 (31%) | 181 of 2,500 (7%) | 0 |

The first two columns are an upper bound on hidden references: some values match a name by
coincidence (a category word such as "Minor").

One instance: `arm5e-lands-of-the-nile-0.5-pagan-monuments-sethos.actor` holds the creature's
Virtues and Flaws as `STRING "Magic Human; Daimon; Transformed Spirit, Wealthy, Inspirational, …"`.
`PARAMETERS` and bound references (§5b) exist for this case. `PARAMETERS` is declared 176 times
across all corpora and a bound reference is written twice.

### C2. `EXTENDS` means both "is a kind of" and "is an instance of"

**Status:** open

`ACTOR "Samurai" EXTENDS ^"Entity"` is a subtype. `^"Pilum of Fire" EXTENDS ^"Formulaic Spell"` is
an instance. The syntax is the same and nothing marks which. §5 distinguishes definition from
instance "by whether it `EXTENDS` an actor type", which leaves out spells, virtues, weapons and
every other non-character instance. `^"Level" INTEGER 20` both restates a type and assigns a value,
so a tool cannot tell a schema field from a filled one except by the presence of a literal. The
tor2e collision in DECISION-13 (a type `^"Shield"` and an item `^"Shield"`) comes from types and
instances sharing one namespace.

Related: `^"Name"` is used for entities, property keys, parameter names, `GUIDANCE` labels, codex
predicates and categories, and scene, clue and check names. Resolution is flat and corpus-wide, and
no syntax addresses a nested thing by path. `.bridge` has `SCOPE` for this; nothing else does.

### C3. Most references in instance data are outside §5d and ungated

**Status:** open

§5d lists the reference sites: `EXTENDS`, `APPLIES TO`, `LIST OF`, `CONCERNS`, `OVERRIDE`, `MODIFY`,
`ALIAS … FOR`, `REFERENCES`. It omits list members (`[ ^"A", ^"B" ]`), carets in system sub-blocks
(`KATA ^"Lord Hida's Grip"`), `CHOICE` options, bound-reference arguments, `PARAMETERS … OF`,
`HOOKS` `THEN`, `OPTIONAL` `SCOPE`, the codex's `IS` and edge objects, and the hash-only references
of §16 (`SCENE_REF #id`, `LEADS_TO [#id]`, `SELECT #hash`), which carry no name to cross-check.

No gate resolves a caret inside a list or a sub-block. Carets inside bracket lists that match no
defined name: root 6 of 749, l5r5e 3 of 2,852, the other four corpora measured 0. One of root's:
`root-0.5-travelers-outsiders-playbook-the-pirate.ttrpg:113` lists `^"Blinside"`; the feat is
defined as `^"Blindside"`. Those list members also carry no hash, and `check_references.py` reports
0 hashless for root because it does not count them.

### C4. Provenance has no construct

**Status:** open

§4: comments are for "page references, source attributions", and comments must not carry data a
tool needs. §5c: strip page citations from `DESCRIPTION`. A page number is data to any tool that
cites, verifies or shows source beside structure. The corpora have each found a place for it: vtm5e
in comments (`# source: page 244`; about 8,380 comment lines carry a page), arm5e in an invented
`^"Page"` property (6,912 uses), l5r5e in both. `REPRINT` says a consumer notes "this book among
its printings", and no header field names the book. `sources.json` does that job outside the spec.

### C5. In heavy use and not in the spec

**Status:** open

- `TABLE`: 849 uses in the three corpora. `check_structure.py` counts it. The spec has only the
  L5R-specific `HERITAGE_TABLE` and `SUB_TABLE`. Roll keys (`2-3`) exist in the grammar; open-ended
  (`16+`) and d66 keys do not.
- String escapes. §10 mentions `\n\n` and §14 `\"`. The grammar accepts the JSON set. The spec has
  no table.
- The "standard whitespace/HTML-escape normalisation" that §5c's verbatim rule depends on is not
  defined anywhere: Unicode form, quote style, soft hyphens, line-end hyphenation.
- Three ways to write multi-paragraph text (sequential strings, `\n\n`, triple quotes), with no
  canonical form, no rule for a newline inside a single-quoted string (the §5c examples wrap one),
  and no dedent rule for triple quotes.
- Document order and heading structure. Coverage is measured against a book's headings; the spec
  does not say how they are represented or whether order is significant.
- How a hash is minted and kept stable across rebuilds. §5's note says example IDs "are regenerated
  during re-conversion". A regenerated hash breaks every `.selections`, `.bridge` and consumer save
  that points at it.

### C6. Specified and unused

**Status:** open

Counts over the `0.5/` directories of all 21 corpus repos:

| Construct | Uses |
|---|---|
| `ALIAS` | 0 |
| `OVERRIDE` | 0 |
| `ADD … DEF` | 0 |
| `REFERENCED BY` | 0 |
| `@n` occurrence index | 0 |
| `.selections` files | 0 |
| `HOOKS` | 3 (arm5e) |
| `OPTIONAL` | 15 (5 corpora) |
| bound reference `^"X"(…)` | 2, against 176 `PARAMETERS` declarations |
| `RULES` with `WHEN […] THEN` | 7 in l5r5e, 16 in six other corpora |
| bare type constraint (§9) | 65 in l5r5e, 45 across eight other corpora |
| `MODIFY` | 392, in l5r5e, vtm5e and arm5e only |

`RULES` with a slug and text (§12) is an l5r5e form (1,374 rules). Later corpora state rules as
DEFs with a `DESCRIPTION`.

### C7. The base spec reserves L5R mechanics

**Status:** open

Design principle 5 is system-agnostic grammar. §16 and §18 reserve `RING`, `RING_TN`, `TN`,
`APPROACH`, `XP_BASE` and `XP` for scenes, and fix scene types to a list that includes "Intrigue".
A `CHECK` cannot hold a VtM dice pool against a Difficulty, a D&D DC with an ability and skill, or a
CoC difficulty level. `CHECK` is used in l5r5e (59) and curseborne (13). The 448 scenes in vtm5e,
callofcthulhu7e, draw-steel, teeth and tor2e have none.

### C8. Edition identity is load-bearing and undeclared

**Status:** open

The edition is the namespace for hash identity (§19), the scope of coherence (§20) and the key of
`--corpus`. No file declares its edition. Three constructs point at one, each with its own syntax:
`FOR "arm5e" VERSION "0.5"` (`.selections`), `FOR EDITION "tor2e"` (`.codex`),
`ORIGIN "dnd5e" VERSION "0.4"` (`.bridge`). The binding is the directory name and a command-line
argument. The `VERSION` in those lines is the content-version directory, a third meaning beside the
file's own `VERSION` and `SPEC_VERSION`.

### C9. Smaller gaps

**Status:** open

- **System vocabulary is undeclared.** §1 says system keywords are "defined by each system's
  `.ttrpg` files". No construct declares one, so a misspelled base keyword becomes vocabulary (B2)
  and a consumer has no schema for a sub-block.
- **`MODIFY` reaches properties and `DESCRIPTION` only.** It cannot change another text field
  (`ACTIVATION`, `TRIGGER`), a system sub-block or a nested property by path, and cannot remove a
  property or an entity. Errata that do any of those need a whole `OVERRIDE`. §13's rule form
  (`NOW REFERENCES`) is defined nowhere else and reuses the `REFERENCES` keyword.
- **`GUIDANCE` entries.** An `ENTRY` takes `CONCERNS`, `TOPICS` and `TEXT`. Sidebar text names
  mechanics and has bold run-ins, and an `ENTRY` cannot carry `REFERENCES` or `EMPHASIS`.
  `check_references.py` accepts them there and the synthesist does not. An entry has no kind
  (sidebar, designer note, example of play, read-aloud text) and no position in the source.
- **`HOOKS`.** `TRIGGER`'s shape "is open", so `FORMAL` ("a complete, evaluable condition") cannot
  be checked. `WHEN` is a string the author writes; the spec does not say whether it is verbatim.
  A hook does not point at the sentence it was drawn from.
- **`OPTIONAL` and `.selections`.** On or off only. No group of mutually exclusive variants, no
  variant with a value, no dependency between options. An `OPTIONAL` DEF needs a hash to be
  selectable and the spec does not require one.
- **`.codex`.** No link that says an `ENTITY` and a game DEF are the same thing (a clan with both a
  lore node and a mechanical DEF). Edges take entities only, so a date or a number cannot be a
  fact. An edge records its surface text and no source file. "The first `ENTITY`" is canonical, and
  first depends on a load order that is not defined.
- **`.bridge`.** `MAP` requires a `DISPOSITION`. A document with no change-tag vocabulary cannot
  use `MAP`, so the Pendragon bridge writes every rename as a `PROCEDURE` `CONVERT … UNCHANGED INTO`.
  `SCALE n OVER d` does not say how to round.
- **Names.** A caret name cannot contain `"` (the grammar has no escape there). arm5e defines an
  entity named `^","`. The validator accepts any name, including an empty one.
- **`ADD`.** In an EXTENSION, `ADD ^"X" DEF { }` and a plain `^"X" DEF { }` differ only in a
  warning.

---

## Candidate improvements (not decided)

| # | Change | Addresses | Cost |
|---|---|---|---|
| 1 | One executable grammar, run over every corpus; lint derived from it | B1, B2 | fails files that pass today; start report-only |
| 2 | Split the spec into a normative reference and a decision log; build every example from a validated fixture | A1 to A8 | an editing pass; no corpus impact |
| 3 | Every caret is a reference site; one rule for name equality | B3, C3 | gate-only; new hashless warnings until backfilled |
| 4 | Type system: a reference property, a reference-with-value list, numeric and dice literals, documented value forms | C1, C2 | each new type is a migration |
| 5 | Provenance: a book identifier in the header and a page field on DEFs | C4 | generators must emit it; mechanical backfill from comments |
| 6 | Implement the stated semantic checks, or remove the claims | B2, B4 | per-instance `REQUIRED` raises hundreds of findings in arm5e |
| 7 | Mark unused constructs provisional until a corpus and a consumer use them | C6 | none for corpora |

---

## Follow-ups in other repos

### F1. l5r5e: fix what the validator now reports in its `CHOOSE` lists, and add hashes

**From:** A1. **Repo:** `titterpig-dsl-l5r5e`. **Status:** open, not started. (First written as
"move l5r5e to `CHOICE`"; the owner chose `CHOOSE n` instead, so l5r5e keeps its keyword.)

The validator resolves `CHOOSE` options as of 2026-11-11, and l5r5e goes from 0 errors to 3:
`l5r5e-0.5-deathly-turns-mechanics.ttrpg` and `l5r5e-0.5-fields-of-victory-mechanics.ttrpg` hold the
options below that resolve to nothing. Two are misspellings of "Martial Arts"; the third is prose
in a caret and wants to be a string option or a `CHOOSE 1 OF` with a `WITH`. 1,187 of its 1,269
options carry no hash.

Also for this pass, from DECISION-16 and DECISION-17: 185 statements write an increase as
`CHOOSE n […] INTEGER 1`, and `Skill Increases` blocks write `^"Command" INTEGER 1`; these become
`TRANSFORM ADD`. 53 `MODIFIERS` blocks hold signed numbers in strings (`^"Glory" "-5"`); these
become `TRANSFORM ADD` / `SUBTRACT` with a hash-qualified target. `^"Clan" STRING "Crab"` and its
kin become `REF`, and the `^"Family"` type declares `^"Clan" REF OF ^"Clan"`.

Seen while confirming the book's wording, cause not established: in the committed
`l5r5e-0.5-core-passages.lore`, 4 of 29 family sections have a "Ring Increase:" line under the
heading. An earlier extraction snapshot (`Temp/l5r5e-books/snap-mid3/`) has it under all 29. The
Hida section keeps "Skill Increases:" and "Starting Wealth:" and has lost "Ring Increase: +1 Earth
or +1 Fire" and "Glory: 44". Either the lines were lifted into the `.ttrpg` on purpose, which would
not explain the two that stayed, or the prose lost them.

Counted 2026-11-11, by token: l5r5e has 308 `CHOOSE` statements with 1,269 options, every option a
caret reference, 82 of them with a hash. 185 sit where a property key goes (`CHOOSE 1 […] INTEGER 1`)
and 123 follow a technique keyword (`KATA CHOOSE 1 […]`). Three options resolve to nothing
(`Martial Art [Melee]`, `Martial Art [Ranged]`, `Any one rank 1 invocation of your inspired
element`). `^"Earth"` is defined twice in l5r5e core with different hashes, so a hashless `^"Earth"`
in a `CHOOSE` list is ambiguous.

l5r5e writes "pick from these" with a keyword of its own, `CHOOSE n [ … ]` (about 300 statements),
and never uses the base spec's `CHOICE` (§5b). Root, TEETH and arm5e use `CHOICE`. Move l5r5e to
`CHOICE`.

What is known going in:

- The validator resolves the options of a `CHOICE` and does not look inside a `CHOOSE` list. A
  misspelled ring in a `CHOICE` is an error today; in a `CHOOSE` it passes.
- Shapes to convert, counted on 2026-11-11: `^"Ring Increase" DEF { CHOOSE 1 [a, b] INTEGER 1 }`
  (57, plus 2 with five rings), `CHOOSE DISTINCT 2 […]` (3 ring increases, 4 uses in all), and
  `CHOOSE n […]` under technique keywords such as `KATA`. Enumerate every shape before converting.
- `CHOICE PICK n` has no `DISTINCT` word. Decide whether picking n options already means n
  different ones.
- At least 12 entries grant fixed rings as `^"Ring Increase" DEF { ^"Earth" INTEGER 1 }`, with the
  ring as the key. A further 104 `Ring Increase` blocks span several lines and were not classified.
  The spec example now writes a choice as `^"Ring" CHOICE […]` plus `^"Amount"`. Decide whether
  fixed and chosen increases should share one shape.
- The `^"Family"` type declares `^"Ring Increase" STRING REQUIRED` and `^"Skill Increases" STRING
  REQUIRED`. Every family fills both with a `DEF`. No gate reports the mismatch (B2). Fix the type
  in the same pass.
- l5r5e has no `gates.sh` (B4).

### F2. l5r5e: replace semantic hashes with opaque ones

**From:** A1. **Repo:** `titterpig-dsl-l5r5e`. **Status:** open, not started.

Owner, 2026-11-11: "the l5r5e hashes need to be updated". §5 says a hash is opaque and carries no
meaning a tool relies on. Counted 2026-11-11 over l5r5e's 3,125 distinct DEF anchors: 225 start
`#L5R`; 9 of those spell out what they point at (`#L5Rring0Earth000000001`,
`#L5Rcond0Compromised01`) and 56 are `#L5R` plus a three-digit sequence number
(`#L5R270aB2cD4eF6gH8iJ0k`). The `.arc` and `.frame` files hold a further 45 distinct word hashes
such as `#governors_neighborhood`, which also contain `_`, outside §5's `[A-Za-z0-9]`.

A hash is what references, `.codex` files and consumers point at, so replacing one needs an
old-to-new table and every referrer rewritten in the same pass. Find the consumers of l5r5e hashes
(the VTT, the pregens site) before starting.

### F3. synthesist: bring its `CHOOSE` handling in line with the spec

**From:** A1. **Repo:** `titterpig-synthesist`. **Status:** open. Owner, 2026-11-11: fix the
synthesist once the DSL work is done.

The synthesist already parses `CHOOSE [DISTINCT] N [opts] <yieldType> <yieldValue>` and emits
`{n, distinct, options, yield_type, yield_value}` (`internal/emit/json.go:149`, `:487`). It has no
handling for `CHOICE`. To change: `distinct` is true only when the word is written, and the spec
now makes it the default; `INDISTINCT` is unknown to it; string options, `CHOOSE n OF ^"Type"`,
`WITH { … }`, a `SET` or `TRANSFORM` after a `CHOOSE` (it reads the trailing `INTEGER 1` as a
"yield" today), `SET` / `TRANSFORM` on a reference target, and `REF` properties need support.

### F4. root, TEETH, arm5e and armdef: migrate `CHOICE` to `CHOOSE n`

**From:** A1, DECISION-15. **Status:** open, not started.

The validator warns on every `CHOICE` as of 2026-11-11: root 130, TEETH 146, arm5e 84, armdef 86.
`CHOICE […]` becomes `CHOOSE 1 […]` and `CHOICE PICK n […]` becomes `CHOOSE n […]`. A slot
`n OF ^"Type"` becomes `CHOOSE n OF ^"Type"`; the one `WHERE` statement
(`armdef-0.5-mythic-companions.ttrpg:103`) becomes two `WITH` clauses. 22 armdef virtues have
`Size "Major or Minor"` packed in one string, and a `WITH { ^"Size" ["Minor"] }` does not match
them. These corpora are generated: change the generators, then rebuild. arm5e's 310 options and
root's 304 carry no hash.

### To-do recorded in the spec

- **Nested conditions in `WITH`** (§5b). `A AND (B OR C)` is not defined; a `WITH` that mixes `AND`
  and `OR` is an error until it is. Owner, 2026-11-11. With one value per term, "Major or Minor, and
  Supernatural" is such a condition and cannot be written in one `WITH` until this is done.

- **The two uses of `SET`** (§8, §13). Flagged for review by the owner, 2026-11-11. The validator
  tells them apart by position: a `SET` directly inside a `MODIFY` body is the §13 directive; a
  `SET` with a reference or a `CHOOSE` before it on the same line is a change. All 43 `SET`s in the
  corpora today are the §13 kind.
- **Dice amounts** for `SET` and `TRANSFORM` (§8). Not defined; they wait on a dice literal (C1).
  Recounted 2026-11-11 with spaces allowed (`4d8 + 8`): 866 property values are only a dice
  expression (dnd5.5e 412, dnd5e 365, pendragon5e 67), 649 of them `Hit Dice`. A further 809 short
  values hold a dice expression plus words, 678 of them Daggerheart damage such as `1d6+2 phy`.
  The earlier figure of 694 used a pattern that missed the spaced form.

### Known gaps left by this change

- **§17's worked examples do not validate, and did not before.** Run as files, the three sketches
  reported 6, 4 and 7 undefined references before the 2026-11-11 edits, because they name types
  they never define (`^"School"`, `^"Technique"`, `^"Adversary"`). With their references now held
  as `REF`, the validator reports 9, 5 and 10. No lint errors.
- **Still strings in the spec's examples, flagged as to-do (owner, 2026-11-11):**
  `^"Range" STRING "Voice"`, `^"Duration" STRING "Momentary"`, `^"Target" STRING "Individual"`
  (arm5e has no entity for these in its core files); `^"Type" STRING "Kata"`, `"Hermetic"` and
  `^"Cost" STRING "Major"` (a category, so an `ENUM` question); the `POWERS` lists of power names
  in §11 and §17; and §8's own `LIST OF STRING` example, which lists disciplines.
- **§17's Pilum of Fire is not the book's.** The sketch has `BASE 5`, `RANGE_MODIFIER "+2 Voice"`,
  `DAMAGE "+10"` and a reworded description. arm5e holds `BASE 10`, one modifier `+2 "Voice"`, and
  the description "A 2-foot, thick, spear-shaped jet of fire flies from your palms, doing +15
  damage to the individual it hits." Under discussion with the owner.
- **arm5e's spell-level modifiers use a form the grammar lacks.** 405 `LEVEL_CALCULATION` blocks
  hold 870 lines such as `+2 "Voice"`. The grammar has no `+` on an integer, and the validator's
  tokenizer drops it without a finding, reading `2 "Voice"`. It keeps a `-`.
- `check_references.py` does not yet count `CHOOSE` options or the `OF` type as §5d sites, so a
  hashless option raises no warning there. The validator resolves them. Belongs with C3.
- The grammar change is unproven: no tool runs `ttrpg.peg` (B1).
- The atlas skill's `references/spec-map.md` gives line numbers into the spec, and every edit to
  the spec moves them. Refresh it when the 0.6 edits settle.

---

## Decision log

Filled in as each finding is walked through.

| Finding | Date | Decision | Reason |
|---|---|---|---|
| A1 | 2026-11-11 | Replace the example with one that follows the l5r5e Hida entry. Replace the §11 `FAMILIES` string with a caret list. | Owner's call. The old example dropped "or Fire" and mixed four kinds of fact under one name. |
| A1 | 2026-11-11 | `CHOOSE n` becomes the spec's construct for a choice; `CHOICE` is dropped from the spec entirely. Supersedes the first A1 row's use of `CHOICE` and reverses F1. | Owner prefers the `CHOOSE n` form. Not yet applied: the details (string options, picking from a type, `DISTINCT`) await sign-off. |
| A1 | 2026-11-11 | The example becomes a full DEF. Its options carry hashes. | Owner's call. |
| A1 | 2026-11-11 | `BOOLEAN` takes an inline value. Applied to §8 and `ttrpg.peg` (uncommitted). | Owner's call. The validator already read the form; 637 uses in l5r5e and arm5e. |
| A1 | 2026-11-11 | Define primitives that tell "becomes n" from "changed by n": `SET` and `TRANSFORM <method>`. | Owner's direction; the shape is a proposal awaiting sign-off. |
| A1 | 2026-11-11 | Removed the three sentences of prose added under the example without being asked. | Owner's call. |
| A1 | 2026-11-11 | A `CHOOSE` list may hold strings as options. | Owner's call. 84 `CHOICE` statements in root and arm5e pick among strings. |
| A1 | 2026-11-11 | `DISTINCT` and `INDISTINCT` are both legal on a `CHOOSE`. With neither, it is `DISTINCT`. | Owner's call. |
| A1 | 2026-11-11 | The §1 example uses opaque illustrative hashes. l5r5e's semantic hashes need to be replaced (F2). | Owner's call. §5 says a hash carries no meaning. |
| A1 | 2026-11-11 | `WITH` replaces `WHERE`. A term is a property and a bracket list of values, as in `WITH { ^"Size" ["Minor"] AND ^"Category" ["Supernatural"] }`; `OR` and `NOT` are supported. Nested conditions are a to-do. | Owner: it states values that must be true; it does not pull a pool of options. |
| A1 | 2026-11-11 | A choice from a type is written `CHOOSE n OF ^"Type"`. | Read from the owner's `WITH` ruling, which answered the question that proposed this form. Confirm. |
| A1 | 2026-11-11 | A `WITH` term takes exactly one value. A comma is not an implicit "or"; several values in one term are unsupported and an error. | Owner's call, overruling the agent's first draft, which read a list as "one of". |
| A1 | 2026-11-11 | One `WITH` uses `AND` throughout or `OR` throughout; a mix is an error until nesting is defined. | Owner agreed. |
| A1 | 2026-11-11 | `CHOICE` is a warning in a file that is 0.5-compatible and an error in a file converted to 0.6. The validator reads the file's `SPEC_VERSION`: below 0.6, or none, warns; 0.6 or later errors. | Owner's call. All 6,384 corpus files declare 0.5 today, so every `CHOICE` is a warning. |
| A1 | 2026-11-11 | Fix the synthesist once the DSL work is done (F3). | Owner's call. |
| A1 | 2026-11-11 | The §1 example is a ladder of three full DEFs: everything in one `DESCRIPTION`; the fields named with values still packed in strings; the structured form. Written to the spec, the guidelines and the skill file, identical in all three. | Owner chose "both, as a ladder". The middle step is the failure that passes review. The blob uses the book's four labelled lines, confirmed in an earlier extraction (`Temp/l5r5e-books/snap-mid3/l5r5e-0.5-core-passages.lore:589`). |
| A1 | 2026-11-11 | `SET` and `TRANSFORM` approved as proposed, points 1 to 6: four closed methods (`ADD`, `SUBTRACT`, `MULTIPLY`, `DIVIDE`); `ROUND`, `MIN`, `MAX` as a suffix; the amount an integer or a reference; `TRANSFORM MANUAL "…"`; the word `SET` kept; the target a hash-qualified reference. Written into §8 as DECISION-16. | Owner's call. |
| A1 | 2026-11-11 | The dual use of `SET` (the §13 directive inside `MODIFY`, and the new change) is flagged for review later. | Owner's call. Marked in §8, DECISION-16, the grammar and the to-do list below. |
| A1 | 2026-11-11 | State the statement-boundary rule in §8 ("Where a statement ends"). Done; `MODIFY` added to the grammar's list to match the validator. | Owner: "add this grammar". |
| A1 | 2026-11-11 | §17's worked examples: properties that name an entity now hold a `REF` (L5R and VtM `Clan`, `School`, `Crab`, `Parent`, `House`, `Technique`, `Form`), and `In-Clan Disciplines` is a `LIST OF ^"Discipline"`. The rest are flagged as to-do. | Owner: "update as appropriate or flag as a todo". |
| A1 | 2026-11-11 | F1's migration list for l5r5e and F3's additions for the synthesist are agreed. | Owner agreed. |
| A1 | 2026-11-11 | A `REF` declaration is written `REF OF ^"Clan"`, with no name before it; the property takes the type's name. `^"Clan" REF OF ^"Clan"` raises a warning. | Owner's syntax ruling. Agent's reading, to confirm: a property whose name differs from its type still writes the name (`^"Patron" REF OF ^"Virtue"`), and an instance still writes `^"Clan" REF ^"Crab"`. |
| A1 | 2026-11-11 | The work is checked in on a `0.6` branch of `titterpig-dsl`. Not pushed. | Owner's call. |
| A1 | 2026-11-11 | Spell levels: track both a spell's magnitudes and its level, the level derived from the magnitudes. "+2 Voice" is a `TRANSFORM` of the spell's magnitudes, and the spell's Range is set to Voice; Voice as an entity can carry that change. | Owner's direction. How a derived property is written is not yet defined; proposal pending. §17's Pilum of Fire is unchanged until then. |
| A1 | 2026-11-11 | Open: a dice literal. | Owner asked for a proposal. |
| A1 | 2026-11-11 | `REF` is the property type for a reference to one entity: `REF OF ^"Type"` on the type, `REF ^"Entity"` on an instance. Written into §8 as DECISION-17. The example's `^"Clan" STRING "Crab"` is now `^"Clan" REF #… ^"Crab"`. | Owner asked for the string to become a reference and chose `REF` from four candidate terms. |

---

## Appendix 1. The probe corpus

Two files in one directory, run through all four gates. Results: validator 2 errors (the duplicate
anchor on `#ProbeVirtue…`, and `^"virtue"` undefined); `check_references.py` 3 ambiguity errors on
`^"Skill"` and 5 hashless warnings; `check_constructs.py` 0; `check_structure.py` PASS.

`probe.ttrpg`:

```
BASE "Probe_Core" {
    NAME "Probe"
    VERSION "0.1"
    SPEC_VERSION "9.9"
    RELEASE_DATE "2026-11-11"

    #ProbeActorAAAAAAAAAAAAAAAA ACTOR "Samurai" DEF {
        PROPERTIES {
            ^"Name" STRING REQUIRED
            ^"Air" INTEGER MIN 1 MAX 5 DEFAULT 1
            ^"Kind" ENUM ["Gift", "Burden"]
            ^"Skills" LIST OF ^"Skill"
        }
    }
    #ProbeSkillAAAAAAAAAAAAAAAA ^"Skill" DEF { INTEGER MIN 0 MAX 5 }
    #ProbeVirtueAAAAAAAAAAAAAAA ^"Virtue" DEF { }
    #ProbeWrathfulAAAAAAAAAAAAA ^"Wrathful" DEF {
        EXTENDS #ProbeVirtueAAAAAAAAAAAAAAA ^"Virtue"
        PARAMETERS { ^"Size" OF ["Major", "Minor"] }
    }
    #ProbePlainAAAAAAAAAAAAAAAA ^"Plain" DEF { EXTENDS #ProbeVirtueAAAAAAAAAAAAAAA ^"Virtue" }

    #ProbeInstAAAAAAAAAAAAAAAAA ^"Ide Tadaji" DEF {
        EXTENDS #ProbeActorAAAAAAAAAAAAAAAA ^"Samurai"
        APPLIES TO [^"Virtue"]
        PROPERTIES {
            ^"Air" INTEGER 7
            ^"Kind" STRING "Neither"
            ^"Skills" LIST OF ^"Skill" [ ^"Virtue", ^"Wrathful"("Huge"), ^"Plain"("x","y"), ^"Wrathful"("Major","Extra") ]
            ^"Pick" LIST [ CHOICE PICK 5 [ ^"Plain", ^"Wrathful" ] ]
            ^"Flag" BOOLEAN true
            ^"Weight" INTEGER "heavy"
        }
        PROPERTEIS { ^"Typo" STRING "x" }
        EXTEND ^"Nonexistent Thing"
        REQUIRES ^"Air" >= 3 | ^"Skill" → 2
    }
    #ProbeCycAAAAAAAAAAAAAAAAAA ^"CycA" DEF { EXTENDS ^"CycB" }
    #ProbeCycBBBBBBBBBBBBBBBBBB ^"CycB" DEF { EXTENDS ^"CycA" }
    #Probe_under_score_AAAAAAAA ^"Under" DEF { }
    ALIAS ^"AlA" FOR ^"AlB"
    ALIAS ^"AlB" FOR ^"AlA"
}
^"Stray After Close" DEF { EXTENDS ^"Virtue" }
```

`probe2.ttrpg`:

```
EXTENSION "Probe_Ext" {
    NAME "Probe ext"
    VERSION "0.1"
    SPEC_VERSION "0.5"
    DEPENDS_ON "Probe_Core" VERSION "99.0"
    #ProbeVirtueAAAAAAAAAAAAAAA ^"Virtue" DEF { DESCRIPTION "restated" }
    ^"Skill" DEF { }
    ^"Uses" DEF { EXTENDS ^"Skill"  EXTENDS ^"virtue" }
}
```

## Appendix 2. Method

- **Gate results.** `ttrpg_validator.py`, `check_references.py`, `check_constructs.py` and
  `check_structure.py` run on each corpus directory with `python3 -B`. l5r5e: validator 0 errors,
  0 warnings over 166 files; 2,379 reference sites; structure PASS. vtm5e: 0 errors, 0 warnings
  over 328 files; 2,868 sites; structure FAIL. arm5e: 0 errors, 1 warning over 2,435 files; 11,035
  sites; structure FAIL.
- **Construct census.** A line-anchored regular expression per construct, counted over every
  `.ttrpg`, `.actor`, `.arc`, `.frame`, `.setting`, `.campaign`, `.codex` and `.selections` file
  under each repo's `0.5/` directory (`arm5e/0.5` for Ars Magica). The counts are pattern matches
  and were not parsed.
- **Names defined more than once.** From the validator's own `analyze_file` name table: l5r5e 350
  of 4,232 distinct names, vtm5e 1,202 of 10,364, arm5e 349 of 11,471.
- **Strings equal to entity names (C1), carets in lists (C3).** The validator's tokenizer over each
  file; the defined-name set is the validator's name table plus the names of `LOCATION`, `SCENE`,
  `ENTRY`, `ENTITY`, `CLUE`, `CHECK`, `PHASE` and `RESOLUTION` blocks. Comparison is exact.
- **Name folding (B3).** The validator's name table grouped by `check_references.py`'s `nk()`.
- **Shared hashes (A5).** Line-start `#hash ^"` anchors of 16 or more characters in the `.ttrpg`
  files of `arm5e/0.5` and `armdef/0.5`, compared as sets.
- **`.actor` wrappers (A7).** The first line that is not blank or a comment, over every `.actor`
  under a `0.5` path in all repos.
- **Version pins (B5).** Each `DEPENDS_ON "id" VERSION "v"` in l5r5e compared with the `VERSION`
  declared by the file whose container id is `id`.
- **Embedded references (A2).** `^\"…\"` inside strings in l5r5e, resolved against the validator's
  name table. `**` counted per string literal.
