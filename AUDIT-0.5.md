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

**Status:** closed 2026-11-11 by the owner. Committed and pushed on branch `0.6`. `CHOOSE n`
replaces `CHOICE` (DECISION-15); `SET` and `TRANSFORM` (DECISION-16); `REF` (DECISION-17); dice as
DEFs, `ROLL` and `NEXT` (DECISION-18); `BOOLEAN` inline value; the §1 example is three full DEFs with
opaque hashes. Follow-ups F1 to F6 and the to-dos listed after them stay open and are tracked there.

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

**Status:** closed 2026-11-12 by the owner. Committed and pushed on branch `0.6`. `EMPHASIS`
kinds, `LABEL` and the Markdown-emphasis finding (DECISION-19); embedded references with an
optional literal, checked by both tools (DECISION-20); the `TABLE` primitive (DECISION-21). The
follow-ups are F7 to F10, and the to-dos and gaps are listed below.

§5c: "No inline markup is ever inserted into the text." DECISION-7 rejected `[[…]]` markup for that
reason, and `EMPHASIS` exists so that bold is recorded beside the text.

- §14 "Embedded References in Strings" still documents `ACTIVATION "When you make a ^\"Fitness\"
  check..."` as a feature. §11 uses it (`"Gain the ^\"Blessed Lineage\" distinction"`).
- §21's `PROCEDURE` example has `TEXT "**Abilities:** Leave at the old value…"` in a field the
  section calls verbatim.

Evidence, recounted 2026-11-12 with a string-literal reader over the 22 corpus directories
(1,430,006 string literals outside comments; armdef mirrors arm5e and is left out of the tables).
An earlier version of this section gave slightly different counts from line patterns, and said 14
distinct embedded names were dangling. The figure is 10 distinct names in 14 places.

Strings that carry each kind:

| Corpus | `**bold**` | `*italic*` | Markdown `- ` list lines | Markdown tables | embedded `^\"` | `EMPHASIS` blocks | `REFERENCES` blocks |
|---|---|---|---|---|---|---|---|
| vtm5e | 2,286 | 2,279 | 0 | 0 | 0 | 0 | 0 |
| arm5e | 1,094 | 1,791 | 20 | 0 | 0 | 0 | 937 |
| tor2e | 737 | 965 | 0 | 0 | 0 | 0 | 0 |
| daggerheart | 516 | 251 | 0 | 0 | 0 | 0 | 0 |
| draw-steel | 462 | 361 | 871 | 285 | 0 | 142 | 6 |
| dnd5.5e | 244 | 1,023 | 0 | 0 | 0 | 0 | 0 |
| dnd5e | 116 | 735 | 0 | 0 | 0 | 0 | 0 |
| troika | 63 | 167 | 0 | 0 | 0 | 0 | 0 |
| l5r5e | 0 | 0 | 0 | 0 | 300 | 0 | 44 |

The other corpora hold ten such strings between them (invisiblesun 5, root 4, callofcthulhu7e 1,
pendragon6e 1). The stand-off users are pendragon6e (1,423 `EMPHASIS` blocks), pendragon5e (425),
marvelmultiverse (326), aegean (148), draw-steel (142), root (137), coyotecrow (74) and
mythic-gme2 (46).

The bold and italic columns are pattern matches and include asterisks the books print: arm5e's
footnote marks (`arm5e-0.5-hermetic-magic.ttrpg:578`, `"* Baptismal names … \n** Caster must …"`),
pendragon6e's `Chirurgery 20*`, troika's `* indicates a Weapon`. The printed bullet `•` is the book's
own character and is not counted as markup (vtm5e has 2,368 such lines, draw-steel 1,523, arm5e
609).

What the marked spans are, by where they sit (15,072 bold spans, 13,292 italic spans; the sorting is
by position and is rough):

| Bold span | Count | Example |
|---|---|---|
| inside a sentence | 9,849 | daggerheart: `take **1d8+3** physical damage` |
| run-in label opening a paragraph | 2,273 | arm5e: `**Prot:** The bonus the armor grants…` |
| other bold opening a paragraph | 2,031 | daggerheart: `**Spend a Fear** to summon…` |
| heading on its own line | 577 | vtm5e: `**IMMUNE TO THE CALL**` |
| the whole string | 342 | troika table rows |

| Italic span | Count | Example |
|---|---|---|
| inside a paragraph | 11,987 | dnd5.5e: `created by the *Bestow Curse* spell` |
| a whole paragraph | 842 | draw-steel: `*You become an actual shadow.*` |
| the whole string | 463 | vtm5e fiction and attributions |

Troika marks three ways in one paragraph (`troika-0.5-core-blancmange-and-thistle.arc:41`):
`A ***sweet old lady*** … gives a *red bonbon* to ***the mandrill***`, and elsewhere
`a **cloud of green gas**`. `EMPHASIS { "…" }` records that a span is marked and has no place for
which marking.

Embedded references: l5r5e holds 420 in 300 strings (100 distinct names), under `EFFECTS` (66
strings), `OPPORTUNITIES` (61), `SUB_TABLE` (57), `ACTIVATION` (35) and others. 10 of the names, in
14 places, resolve to no definition (`Shadowlands Taint` 4, `Otherworldly` 2, eight more once
each). No gate reads inside strings.

Draw Steel's source is itself Markdown (Steel Compendium, per that repo's README), so its strings
hold whole Markdown passages: 285 strings with tables (1,447 rows), 338 with `####` headings, 68
with links. One caret name there runs 1,317 characters over several lines and holds an entire
ability (`draw-steel-0.5-core-ancestries.ttrpg:388`).

Who reads which:

- The vtm5e VTT turns `**…**` in a string into bold (`sortilege-vtt-vtm5e/system/vtm5e/entity.js:31`,
  `engine/gm-text.js:41`). Taking the markers out of that corpus changes what its screen shows until
  the VTT reads `EMPHASIS`.
- The pendragon6e VTT reads `EMPHASIS` blocks (`sortilege-vtt-pendragon6e/system/pendragon6e/data.js:96`).
- The synthesist has no code that names `EMPHASIS` (grep, 0 hits in `*.go`). The pendragon6e VTT
  finds the blocks under an entity's generic `blocks`.
- I found no code in the l5r5e VTT that reads a caret inside a string (one grep; not proven absent).

So three content models for a string are live: plain text with stand-off `EMPHASIS` and
`REFERENCES` (what §5c says, and what root, both Pendragons, marvelmultiverse, aegean, coyotecrow
and mythic-gme2 do); Markdown inside the string (eight corpora); and embedded caret references
(l5r5e). The spec states the first, shows the other two in its examples, and no gate checks any.

### A3. The §16 examples break the §16 rules

**Status:** closed 2026-11-12 by the owner. Committed and pushed on branch `0.6`. Every point
raised was ruled and applied. DECISION-22: a `FROM` names its container's kind and is itself the declaration;
the examples carry opaque hashes; the ARC example is the real Lost Writer arc; a block's name
comes before its hash by convention and the other order is legal; a skill group is a property of a
character. DECISION-23: a scene's type and a conflict's type are entities the system defines. Five
smaller fixes: the stale DECISION-2 clause; `MODIFICATIONS` without `RANGE(…)`; a frame's `RULES`
in §12's form; a location imported with `FROM SETTING … INCLUDE`; the dependency diagram. The
CAMPAIGN example is the real Children of Fear campaign. The SETTING and FRAME examples are still
invented, by the owner's leave, until l5r5e has a Rokugan setting. Run as files beside stubs for
what they depend on, the five §16 examples now give 0 errors and 0 warnings, down from 23
warnings.

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

Further points of the same kind, found 2026-11-12:

- No §16 structure block or example declares `SPEC_VERSION`, which §0 requires of every file.
- The DECISION-2 note above the FRAME block says the deprecated NPC form is "left as-is" in the
  blocks below. Those blocks now use the instance form; the sentence is stale.
- FRAME's `MODIFICATIONS { status RANGE(20, 35) }` and `RULES { RULE rule_name ADDS_TO PARENT { } }`
  are forms found nowhere else in the spec, and the grammar has no rule for either.
- The ARC example's `FLOW` points at four scenes the example never defines (`#market_inquiry`,
  `#ink_trail`, `#scorpion_encounter`, `#final_confrontation`), and the CAMPAIGN example lists two
  arcs that do not exist.
- `LOCATION ^"X" { FROM SETTING "SettingID" }` names the setting and not the location in it.
- The CONFLICT block writes `TYPE "combat" | "intrigue"` inside a code block, and scene types are
  capitalised (`"Intrigue"`) where conflict types are lowercase (`"intrigue"`).
- A block is declared `SCENE ^"Name" #hash {`, name before hash; a DEF is `#hash ^"Name" DEF`.
- The dependency diagram shows no arrow from ARC to SETTING, which rule 3 allows.

**The spec's examples in the spec's validator.** The four §16 examples, written to files beside a
stub base, give 0 errors and 23 warnings: 19 for hashes shorter than 16 characters and 4 for a
missing `SPEC_VERSION`. With five faults planted in the arc (an undefined base, setting, frame,
scene reference and `LEADS_TO` target), the validator reports one, the base. `check_references.py`
reports none.

**The corpora** (121 narrative files, counted 2026-11-12, armdef left out: 70 `.arc`, 32 `.frame`,
18 `.setting`, 1 `.campaign`):

| What §16 specifies | In the corpora |
|---|---|
| `SPEC_VERSION` absent | declared in all 121 |
| `USES_SETTING`, `USES_FRAME` | 0 uses |
| `FROM FRAME "id" INCLUDE`, `FROM SETTING "id"` | 0 uses |
| `FROM "id" INCLUDE` | 14 uses. 11 target an `EXTENSION` (the file holding the NPCs), 3 target an id that is not a container in the corpus (curseborne 2, tor2e 1) |
| `FROM ARC "id"` | 8 uses, in the one campaign |
| rule 7 | 20 of the 22 `FROM` lines name a container their file does not declare. The 2 that comply are teeth's, through `USES_EXTENSION` |
| `DEPENDS_ON` on every arc and frame | 14 l5r5e files write `ARC "id" EXTENDS "l5r5e" {` and have none |
| semantic hashes | l5r5e only: 48, such as `#arrival_7933e585a909`. The other ten corpora use opaque hashes |
| `SCENE ^"Name" #hash {` | 478. `SCENE #hash ^"Name" {`: 19 (coyotecrow 6, troika 13) |
| `LOCATION ^"Name" #hash {` | 1,549 (arm5e 1,525). 458 more carry no hash |
| name before hash on a block, all kinds | 9,913 headers (`ENTRY` 7,886, `LOCATION` 1,549, `SCENE` 478) against 20 the other way |
| `SCENE_REF #hash` | 328, every one hash-only: `SCENE_REF #tQ2C3ShKhZRaG6de79YFMy9` |
| a scene's `LOCATION` reference | `LOCATION #hash` 17 (l5r5e); `LOCATION ^"Name"` 69 (draw-steel 60, curseborne 9) |
| `^"Skills" DEF { ^"Social" INTEGER 4 }` | 0. l5r5e's NPCs write `^"Skills" LIST OF STRING ["Artisan 1", "Martial 2", …]` |
| `RANGE(…)` | 0. `MODIFICATIONS`: one block (curseborne), holding `DEFAULT` lines only |

l5r5e holds the real adventure the ARC example imitates
(`l5r5e-0.5-children-of-five-winds-lost-writer.arc`). Its people and places differ from the
example's: the governor is Miya Tetsua, and the example's Ide Tadaji, Doji Fumiko and Bayushi Koto
are not in it.

**What the real arc shows** (read 2026-11-12):

- It declares `DEPENDS_ON "L5R5e_Core_Core"` and `USES_EXTENSION "L5R5e_Children_of_Five_Winds"`,
  and defines its nine cast members inline. It has no `FROM`.
- Two of the nine are defined a second time in the book's GM file
  (`l5r5e-0.5-children-of-five-winds-gm-tools.ttrpg`, `EXTENSION "L5R5e_Children_of_Five_Winds_GM"`),
  under different hashes: `#L5RCW51lM3nO5pQ7rS9tU1v ^"Miya Tetsua"` in the arc and
  `#AEzCQP2Drp0S9YJeerwTbW ^"Miya Tetsua"` there, with the same stat block restated. The same for
  `^"Adventure Ifrit"`. Each name is now two entities.
- All three `OPPONENTS` references point at hashes declared nowhere:
  `OPPONENTS [#kaeru_haya_60be37c72620]`, where the cast declares
  `#L5RCW54sT6uV8wX0yZ2aB4c ^"Kaeru Haya"`. They are hash-only, so nothing ties them to a name, and
  neither tool reports them. The arc's other 36 hash-only references (`SCENE_REF` 9, `LOCATION` 9,
  `LEADS_TO` 17, `COMPLETED_SCENES` 1) resolve.
- Skill groups are not entities in l5r5e. A skill carries `SKILL_GROUP "Artisan Skills"` as a
  string, and the `^"NPC"` type declares no properties at all, so an NPC's
  `^"Skills" LIST OF STRING ["Artisan 3", "Martial 2", …]` is checked against nothing.

Related findings, not repeated here: B1 (the grammar has no rule for a narrative container), B2
(what the validator does not check), C3 (hash-only references carry no name to cross-check), C7
(L5R mechanics reserved in scenes).

### A4. §20's definition of "defined" contradicts §16 and §25

**Status:** closed 2026-11-12 by the owner. Committed and pushed on branch `0.6`.
DECISION-24: two tiers. A definition, now including a codex `ENTITY`, is a name every file may
use. A named block is a target through its hash, and its name is a label inside its own file.
Both tools follow it, and references between scenes, locations and cast are resolved.
DECISION-25, which came out of the work: a caret name may hold an escaped quote.

§20: name resolution collects `^"Name" DEF`, `ACTOR`/`TEMPLATE` definitions and `ALIAS` names "and
nothing else". §25: a codex `ENTITY` "is a first-class caret target". §16 has scenes point at a
`LOCATION` and flows point at a `SCENE`. §21 and §22 call an `ENTRY`'s caret "a local label, not a
reference".

**Corrected 2026-11-12.** This finding said `check_references.py` indexes anchors from every
container and names an l5r5e `LOCATION` that a `REFERENCES` entry targets. It indexes DEFs in every
kind of file, and nothing else. The l5r5e example, `^"Mountain Song Temple"`, is a DEF nested
inside an arc (`l5r5e-0.5-imperfect-land.arc:54`), written that way so a reference can reach it.

**What each source counts as a thing a reference may point at:**

| | DEF | codex `ENTITY` | `LOCATION`, `SCENE` | `ENTRY` |
|---|---|---|---|---|
| §20 | yes | no | no | no |
| §25 | | yes | | |
| §16 | | | yes | |
| §21, §22 | | | | no: "a local label" |
| `ttrpg_validator.py` | yes | yes | no | no |
| `check_references.py` | yes | no | no | no |

Probed 2026-11-12 with one referrer pointing at each kind. The validator reports the references to
the location and the scene as undefined and accepts the codex entity. The gate reports all four
that are not DEFs: 7 errors. A `SCENE_REF` and a scene's `LOCATION` that point at hashes declared
nowhere are reported by neither tool.

**Named blocks in the corpora** (armdef left out):

| Block | Declared | With a hash | Names repeated within a corpus | Also the name of a DEF |
|---|---|---|---|---|
| `LOCATION` | 2,007 | 1,549 | 107 | 165 |
| `SCENE` | 497 | 497 | 60 | 63 |
| `ENTRY` | 8,187 | 7,894 | 2,095 | 362 |
| `RESOLUTION` | 436 | 0 | 237 | 0 |
| `CLUE` | 257 | 0 | 0 | 1 |
| `PHASE` | 124 | 0 | 6 | 4 |
| `CHECK` | 73 | 1 | 0 | 1 |
| codex `ENTITY` | 1,496 | 1,496 | 249 (amends across files, which §25 allows) | 104 |

- **Locations and scenes are referenced.** `SCENE_REF` 328, `LEADS_TO` 49, a scene's `LOCATION` 86
  (17 by hash, 69 by name), `COMPLETED_SCENES` 1. Every one resolves to a declared block.
- **An `ENTRY`'s name is a label.** invisiblesun has 245 entries named `Sidebar 1`, pendragon6e 209
  named `margin-note-1`, marvelmultiverse 76 named `example-1`. draw-steel has 57 `RESOLUTION`
  blocks named `Tactics`.
- **Nothing checks a block's hash.** arm5e has four hashes that each sit on two different entries
  (`#t1ed6d9b1394ac006d6d3be` on "New Virtues (Mythic Judaism)" and "New Virtues (Mythic Islam)").
  l5r5e has 10 `OPPONENTS` references to hashes declared nowhere, across its arcs; the Lost Writer's
  three (A3) are part of that count.
- **Places are declared twice to make them referenceable.** 160 names are both a `LOCATION` or
  `SCENE` block and a DEF: arm5e 84, root 62, tor2e 14. "The Tomb of Queen Cleopatra" is a
  `LOCATION` in a setting and a DEF in an `.actor`. 523 references to those names carry a hash and
  10 do not (arm5e 8, tor2e 2).
- One block shares its hash with a DEF: l5r5e's `CHECK #0VDeckbNgpBJyQnoibqr0E ^"Stir the Leaves"`
  and a DEF of the same name.

### A5. The spec's example of two editions shares most of its hashes

**Status:** closed 2026-11-12 by the owner. Committed and pushed on branch `0.6`. A port keeps
its source's hashes and declares its source (DECISION-26).

§5 and §19: hash identity carries nothing across editions; the same entity in another edition has a
different hash. §19 gives arm5e and armdef as the example of separate editions. Most DEF anchors in
`arm5e/0.5` also appear in `armdef/0.5`, because the armdef sourcebooks are regenerated from arm5e.

**Evidence, recounted 2026-11-12.** Every hashed DEF in `.ttrpg` and `.actor` files, read with the
validator's tokenizer. This replaces the first count (8,299 of 9,959), which I could not reproduce.

| Hashed DEFs | arm5e | armdef | Same hash in both |
|---|---|---|---|
| Core (top level and `spells/`) | 1,410 | 2,232 | 0 |
| The 46 sourcebooks | 10,555 | 10,276 | 10,275 |
| Total | 11,965 | 12,508 | 10,275 |

- The two cores were converted from two different books and share no hash. 1,201 names are defined
  in both editions under different hashes (`^"Faerie Blood"` is `#t42wf…` in arm5e and `#t1nZX…` in
  armdef).
- The sourcebooks are ports. `retarget_armdef.py` copies each arm5e file, gives it an armdef id and
  `DEPENDS_ON`, and re-points its references at armdef's core. Its own header says a DEF's `#hash`
  anchor is never rewritten. All 10,275 shared hashes carry the same name on both sides.
- Of the 10,275 pairs, 5,549 have identical bodies, 3,788 differ only in the hashes of what they
  reference, and 938 differ in more (the one opened renames a property, `^"Personality Traits"` to
  `^"Personality Trait"`). No ported file is byte-identical to its source (0 of 2,382): each
  declares its own id.
- 280 sourcebook DEFs exist only in arm5e and 1 only in armdef. The 280 are entries the Definitive
  core also prints, which the port turns into `REPRINT`, `ALIAS` or `MODIFY` (DECISION-14).
  UNVERIFIED: I did not check each of the 280 against that table.
- A tool depends on the shared hashes: `retarget_armdef.py` (`check_armdef_only`) matches a renamed
  DEF to its arm5e source by hash.
- Nothing in a ported file says it is a port or names the file it came from.
- A second pair shares hashes by accident. `invisiblesun/0.5` and `root/0.5` have 1,508 DEF hashes
  in common and none of them carries the same name (`#t0414qus2S0amh67MiPhYGCp` is
  `^"Elderbrin Camp in the Realm of the Gold Sun"` in one and `^"New Faction Roll Mechanics (Ruins
  and Expeditions p18)"` in the other). No other pair among the 22 corpus directories shares one;
  dnd5e and dnd5.5e share none, and neither do pendragon5e and pendragon6e.
- No tool compares hashes across editions. Passing both copies of one book (Grogs) to the validator
  in one run gives 273 `duplicate anchor` errors.
- Seven files in the dossiers project cite shared hashes. The one opened names its edition in its
  header (`EXTENDS "ARMDef_Core_Base"`).

**Ruling (owner, 2026-11-12):** "ports keep them but there should be a port declaration".
Written as DECISION-26.

- **Spec.** §5 and §19 no longer say the other edition's entity has a different hash. A port
  keeps the hash of everything it carries over and declares its source in its header:
  `ORIGIN "arm5e" EXTENSION "ArM5_Grogs_Abilities"`. A hash two editions share outside a declared
  port means nothing. §19 has a new *Ports* section, §20 lists what is checked, and §3, §13, §15,
  §21 and `bridges/README.md` are brought into line. The owner confirmed the line's wording
  ("Yes, as written").
- **Grammar.** `ORIGIN_DECL` in the header. Unproven, as every grammar change is (B1).
- **Validator.** The line's form; a port and its origin in one loaded set; and, given the origin
  edition's corpus with `--corpus`, that the origin container exists, is of the kind named, and
  gives every hash it shares with the port the same name. With no corpus the run says so in one
  warning per edition id.
- **Proof.**
  - Fixtures: `tests/ports-good` with `--corpus port-old=tests/ports-origin` gives 0 errors and
    0 warnings, and 1 warning without the corpus. `tests/ports-bad` holds nine planted faults and
    gives 10 errors with the corpus (fault 9 raises two) and 5 without it.
  - The real corpus: a scratch copy of `armdef/0.5` with an `ORIGIN` line written into each of
    its 2,390 ported files, validated with arm5e as the corpus, gives the findings the unchanged
    armdef gives (5 errors, 2,723 warnings, the same list) and none about a port. Renaming one
    carried-over DEF in that copy and misspelling one origin id gives one error each.
  - No change elsewhere: the old validator and the new give byte-identical output on all 22
    corpus directories, and on the dnd5e to dnd5.5e bridge with both corpora.
- **Not done.** No corpus file declares an `ORIGIN` yet (F14). invisiblesun and root still share
  their 1,508 hashes (F15).

### A6. Implicit override is legal in §13 and an error in the validator

**Status:** closed 2026-11-12 by the owner. Committed and pushed on branch `0.6`. No implicit
override, by hash or by name (DECISION-27).

§13: a later file may restate an entity's hash, and by load order that replaces the earlier
definition. `ttrpg_validator.py` reports any recurring hash as `duplicate anchor` (proven by the
probe, Appendix 1). §20 has carried a note that this is "a pending change" since v0.4.

The synthesist does something the spec does not describe. With no hash match it treats a same-name
DEF of a compatible type as an implicit override of the earlier one, even when the two carry
different hashes (`titterpig-synthesist/internal/resolve/collect.go:66`). §5d says distinct hashes
are distinct entities.

**Evidence, counted 2026-11-12.**

*A restated hash.*

- No corpus restates a DEF's hash. The 22 corpus directories hold 96,571 hashed DEFs and each
  hash stands once in its corpus; the validator reports no `duplicate anchor` in any of them.
- Changes are written out: 603 `MODIFY` and 355 `REPRINT` statements. No line in the 22
  directories begins with `OVERRIDE` or `ADD`.
- The one hash restated on purpose is a block's. l5r5e's 2020 errata file supersedes its 2019
  file and repeats 13 of its guidance `ENTRY` blocks, each under the same hash and name, inside
  the same explicit `MODIFY`. A4 made that legal. §25 lets a codex `ENTITY` be restated the same
  way to add sources.
- The validator knows no load order. The order of a composition is written only in the
  synthesist's manifest.

*The same name under another hash.* Counted by building the synthesist at `207d945` and running
`--collect -v` on each manifest.

| Composition | Entities replaced by a name match | Definitions dropped |
|---|---|---|
| arm5e-0.5-full | 114 | 138 |
| armdef-0.5-full | 125 | 140 |
| callofcthulhu7e-0.5 | 18 | 23 |
| dnd5.5e-0.5 | 13 | 13 |
| l5r5e-0.5 | 6 | 6 |
| tor2e-0.5 | 25 | 36 |
| Total | 301 | 356 |

- In all 301 the replaced DEF carries a different hash from the one that replaces it, and a
  different body. None is a match by hash. In 165 the DEF that wins is the shorter of the two.
- tor2e: the core rulebook's `#ty7p38adq9mo4x4elEf5xGA ^"Combat"` holds the combat chapter, with
  an epigraph, a description and nested DEFs. Strider Mode's `#t3CjgX8PA3uTc56tNZkmsHp ^"Combat"
  DEF { }` is an empty heading, loads later, and replaces it. The built
  `tor2e-0.5.resolved.json` (2026-10-13) has the Strider hash and has neither the core hash, nor
  the epigraph's text, nor the nested `^"The Onset of Battle"`.
- arm5e: the actor type `#t0pngx6WgYt7QZLQE1H73Gy3 ACTOR "Magus"`, which extends `^"Character"`,
  is replaced by `#tzWhfmKnMGhj7DODAwBeTkii ^"Magus"`, a rules entry in the character-creation
  file that extends nothing.
- l5r5e: `^"Daidoji Shin"` in the GM tools file is replaced by the fuller `^"Daidoji Shin"` in
  the NPC file. The two are one person under two hashes.
- The rule is deliberate in the synthesist. Its README states it ("matched by hash then name"),
  five arm5e and armdef manifests carry a `type_equivalence` list so that reprints under another
  type still match, and `CORPUS.md` calls one case "a consumer gotcha, not a corpus error". It
  predates `REPRINT` (DECISION-14).
- A further 107 same-name DEFs in arm5e-0.5-full, and 119 in armdef-0.5-full, are kept apart
  because their types are unrelated.
- Other manifests: arm5e-0.5-core 38, armdef-0.5-core 9, armdef-0.5-sub-rosa-13 114,
  dnd5.5e-0.5-historica-arcanum 14, dnd5.5e-0.5-wyldwolf-axis-mikko 13,
  dnd5e-0.5-historica-arcanum 2, and none in daggerheart, mythic-gme2 and troika. These were
  counted and not opened.

**Ruling on Part 1 (owner, 2026-11-12):** "Yes, drop it". Written as DECISION-27.

- **Spec.** The implicit override is withdrawn from §5, §5d, §13 and §20. A DEF's hash stands
  once in a corpus and a second DEF under it is an error. A later file changes an entity by
  naming it in `OVERRIDE`, `MODIFY` or `REPRINT`. §20 drops its "pending change" note and states
  the two restatements that stay legal: a named block under its own hash and name, and a codex
  `ENTITY`.
- **Validator.** It already reported the error. Its message now says what to write, and its
  header states the rule.
- **Proof.** `tests/restate-good` (a block repeated across two errata files, as l5r5e does) gives
  0 errors and 0 warnings. `tests/restate-bad` plants three faults (a hash restated in a later
  file under the same name, under another name, and twice in one file) and gives 3 errors. The
  old validator and the new give byte-identical output on all 22 corpus directories.

**Ruling on Part 2 (owner, 2026-11-12):** "Yes, two entities". Written into DECISION-27.

- **Spec.** §13 states that a DEF of the same name under another hash is a second entity, that
  it replaces nothing whatever its type and load position, and that a consumer must not merge
  two DEFs because their names match. It lists what a book writes when it means the other file's
  entity: `REPRINT`, `ALIAS`, `MODIFY` or `OVERRIDE`. §13's `ADD` paragraph no longer says
  precedence resolves a same-name collision.
- **Tools in this repo.** No change. A same-name DEF under another hash was already legal to the
  validator and the gate.
- **Proof.** `tests/restate-good` now holds two DEFs named `^"Combat"` under two hashes and a
  reference to each by hash: 0 errors and 0 warnings in the validator, 0 errors in the gate.
- **Not done.** The synthesist still merges by name, and the 301 pairs are not triaged (F16).

### A7. `.actor` is defined one way and written two other ways

**Status:** closed 2026-11-12 by the owner. Committed and pushed on branch `0.6`. An `.actor` is
an `EXTENSION` file of one or more instances (DECISION-28).

§2: an `.actor` file is "a `.ttrpg` file scoped to exactly one character definition (a single `DEF`
block)". §3 says every `.ttrpg` opens with `BASE` or `EXTENSION`. The two sentences cannot both
hold. On disk, 2,420 `.actor` files open with an `EXTENSION` wrapper and 670 open with a bare
`#hash ^"Name" DEF`. `l5r5e-0.5-blood-of-the-lioness-pregens.actor` holds 7 DEFs, one of them a type
declaration. arm5e uses `.actor` for covenants. A bare `.actor` has no `SPEC_VERSION`, `VERSION` or
`DEPENDS_ON`, so nothing in the file says which system it belongs to.

**Evidence, recounted 2026-11-12.** Every `.actor` file in the 22 corpus directories, read with
the validator's tokenizer: 3,077 files in 13 corpora. The first count had 2,420 wrapped.

| How the file opens | Files | Corpora |
|---|---|---|
| `EXTENSION "id" …` wrapper | 2,407 | arm5e 1,087, armdef 1,087, pendragon6e 151, pendragon5e 66, callofcthulhu7e 11, l5r5e 5 |
| A bare `#hash ^"Name" DEF` | 670 | tor2e 311, marvelmultiverse 211, aegean 50, troika 36, coyotecrow 31, root 24, curseborne 7 |

- Every wrapped file declares `SPEC_VERSION` and names a parent (`EXTENDS "id"` or `DEPENDS_ON`).
  No bare file can: it has no header.
- **How many DEFs.** 2,999 files hold one. 78 hold several, 418 DEFs between them: arm5e 30
  files (134 DEFs) and the same in armdef, callofcthulhu7e all 11 (107), l5r5e all 5 (33),
  curseborne 2 (10). The ones opened hold:
  - one character at several ages (arm5e's Gwidion of Verditius: at Gauntlet, +15, +30, +45
    years, 8 DEFs);
  - a section's characters (arm5e's The Church, "the women characters", 7 DEFs);
  - an adventure's pregenerated characters (l5r5e, 6 or 7 a file);
  - a chapter's NPCs (callofcthulhu7e, 3 to 23 a file).
- **What they hold.** Every top-level statement in every file is a DEF. All but one of the 3,417
  DEFs extend a type. The one is a type declared inside an actor file:
  `#t84d75db874b40237553ca ^"Historical Persona"` in
  `l5r5e-0.5-blood-of-the-lioness-pregens.actor`, which six DEFs in that file then extend. No
  file holds a `MODIFY`, a `REPRINT` or any other statement.
- **What the DEFs extend.** In 11 corpora the type is an `ACTOR` type, or a `TEMPLATE` that
  extends one (root's playbooks). arm5e's extend `^"Example Character"` (693), `^"Creature"`
  (303), `^"Covenant"` (157) and `^"Saint"` (25); `^"Creature"` and `^"Covenant"` are declared as
  plain DEFs. Four arm5e DEFs extend another character.
- **Tools.** The validator skips its "no SPEC_VERSION" warning for any `.actor`
  (`ttrpg_validator.py`, "bare single-DEF fragments"). The grammar's `FILE` rule has no bare-DEF
  form, so it rejects the 670. The synthesist parses a bare file as "standalone". A bare file
  validated alone (`tor2e-0.5-core-ash.actor`) gives 2 errors for an undefined `^"Adversary"`,
  and nothing in the file says which corpus would define it.
- The dossiers project writes its character files with the wrapper
  (`EXTENSION "dossiers-khalida-bint-tariq" EXTENDS "ARMDef_Core_Base"`).

**Rulings (owner, 2026-11-12):** "part 1: always wrapped", "part 2: one or more", "part 3:
instances only. mark historical persona as a todo". Written as DECISION-28.

- **Spec.** §2 defines an `.actor` as an `EXTENSION` file that holds one or more instance DEFs
  and nothing else, with an example. The "standalone single DEF" text is gone. §3 and §5 are
  brought into line, and so is the guidelines' file-type row.
- **Validator.** A file that opens with a bare DEF gets one warning, which replaces the
  missing-`SPEC_VERSION` warning it was exempt from. A type, an `ACTOR` or `TEMPLATE` definition,
  or a `MODIFY`, `OVERRIDE`, `ADD`, `REPRINT` or `ALIAS` in an `.actor` is a warning below 0.6
  and an error from 0.6. A wrapped `.actor` must declare `SPEC_VERSION` as any file does.
- **Grammar.** No rule changes: `FILE` never had a bare-DEF form. A header note says so.
- **Proof.**
  - `tests/actors-good` (one instance; one character at two ages; an instance of a plain type)
    gives 0 errors and 0 warnings. `tests/actors-bad` holds seven faults and gives 5 errors and
    3 warnings.
  - Old validator against new on the 22 corpus directories: 14 give byte-identical output. The
    other eight gain warnings and nothing else. Seven gain one per bare file, 670 in all
    (tor2e 311, marvelmultiverse 211, aegean 50, troika 36, coyotecrow 31, root 24,
    curseborne 7). l5r5e gains one, for `^"Historical Persona"`. No error count changes.
- **Not done.** The 670 files are not wrapped (F17). `^"Historical Persona"` is not moved (F1).

### A8. Stale and inconsistent text

**Status:** closed 2026-11-12 by the owner. Committed and pushed on branch `0.6`. All eleven
items are settled, two of them as DECISION-29 and DECISION-30.

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

**Checked against the spec as it stands, 2026-11-12.** The items above are numbered 1 to 11 in
order.

- **1 is already fixed.** "through DECISION-13" left §0 in commit `1193d69` (A1).
- **2 stands.** The footer reads "Spec Version: 0.5", "Last Updated: 2026-08-08".
- **3 stands in two of three places.** §19 still says "*this specification* (v0.4)" and the
  guidelines are titled "(v0.4)". The validator's header no longer says "v4"; it says "v0.5, with
  the v0.6 working-draft CHOOSE construct", which names one of the 0.6 constructs it now checks.
- **4 stands.** §5c, DECISION-11: "Three additions:" followed by items 1 to 4.
- **5 and 6 stand.** Every corpus repo is laid out
  `titterpig-dsl-<system>/<contentver>/<system>-<contentver>-<book>-<facet>.<ext>`
  (`DSL/CLAUDE.md`, "File naming"), with the content version in the directory and in the
  filename.
- **7 stands,** and A5 has since settled it: a hash is unique within an edition (DECISION-26).
  The guidelines still say "globally unique".
- **8, recounted.** §15 has gained the 0.6 keywords. 17 keywords that the grammar matches by
  name are in neither §15 nor §18: `SPEC_VERSION`, `PARAMETERS`, `HOOKS`, `HOOK`, `FORMALITY`,
  `TRIGGER`, `PROSE`, `TAGGED`, `CONDITIONAL`, `FORMAL`, `SELECT`, `SELECTIONS`, `GLOBAL`, `on`,
  `off`, `true`, `false`. `OPTIONAL` is listed only as a SCENE keyword in §18. §15 still calls
  `TRIGGER` system-defined.
- **9, counted.** As the first word of a line in the 22 corpus directories: `SKILL` stands 95
  times inside a `SCENE` and 1,698 times outside one (l5r5e's curricula write
  `SKILL "Aesthetics"`); `TYPE` 488 inside and 317 outside; `OPTIONAL` 122 inside and 16 outside;
  `REQUIRED` 205 inside and none outside as a line's first word.
- **10, counted.** The corpora follow "apply to any type" and not the table: `INTEGER … FIXED`
  1,019 times, `STRING … DEFAULT` 322, `ENUM … REQUIRED` 115, `BOOLEAN … REQUIRED` 11,
  `LIST OF STRING … REQUIRED` 15. `MIN` and `MAX` stand only on `INTEGER`.
- **11, counted.** 14,926 `TEXT "…"` lines: 10,895 in an `ENTRY`, 3,512 directly in a DEF, the
  rest in system blocks (`READ_ALOUD` 69). No block holds both a `TEXT` and a `DESCRIPTION`.
- **Not in the first list.** The spec's title and status line say v0.5 is current while §0
  carries a v0.6 working draft. That is true until 0.6 is released, and is left alone.

**More detail on the four open items, 2026-11-12.**

- **6.** All 8,066 DSL and `.lore` files in the 22 corpus directories carry their directory's
  version in the filename.
- **9.** Counting a reserved word as the first word of a line outside the block that reserves
  it: `SKILL` 1,698 (all l5r5e), `TRIGGER` 438 (root 234, draw-steel 203), `TYPE` 317 (root 194,
  l5r5e 106), `TAGS` 78, `THEMES` 49, `SOURCE` 15, and seven more words on one or two lines
  each. 51 of §18's 58 words are not grammar keywords at all, so the grammar reads them as
  system keywords wherever they stand.
- **11.** All 3,512 `TEXT` lines that sit directly in a DEF are in draw-steel, whose DEFs hold 32
  `DESCRIPTION` lines. The other 21 directories write a DEF's prose as `DESCRIPTION` (42,126
  lines in all). The reference gate reads every string in a DEF as its prose, so the two names
  are the same to it. `MODIFY … SET DESCRIPTION` (§13) names one of them: on a DEF whose prose is
  a `TEXT` it would add a second prose field beside the first. draw-steel has no synthesist
  manifest, so no built JSON shows how a consumer reads its `TEXT`.

**Rulings on 5, 6, 9 and 11 (owner, 2026-11-12):** "accept all recommendations".

- **5.** §2's File Organization now shows the real layout,
  `titterpig-dsl-<system>/<contentver>/<system>-<contentver>-<book>-<facet>.<ext>`. It describes
  how the corpora are laid out. No tool checks it.
- **6.** §19 says the content version stands in the directory and in each filename, and that it
  is neither the file's `VERSION` nor its `SPEC_VERSION`.
- **9.** DECISION-29: a keyword listed under a block is reserved inside that block, and a system
  may use the word elsewhere. The file-level, definition, type, modifier, scope, choice and
  modification keywords are reserved everywhere. Stated in §15 and §18. No tool changes: the
  grammar and the validator already read the words that way.
- **11.** DECISION-30: a definition's prose is `DESCRIPTION`, and `TEXT` is not its alias. `TEXT`
  is the prose field of an `ENTRY` and of other blocks that are not definitions. The validator
  reports `TEXT "…"` directly in a DEF: a warning below 0.6, an error from 0.6.
- **Proof.**
  - `tests/text-good` (a DEF with `DESCRIPTION`; `SKILL`, `TYPE` and `TRIGGER` as a system's own
    fields; `TEXT` in a system block and in an `ENTRY`) gives 0 errors and 0 warnings.
    `tests/text-bad` gives 2 errors in a file that declares 0.6 and 1 warning in one that
    declares 0.5.
  - Old validator against new on the 22 corpus directories: 21 give byte-identical output.
    draw-steel gains 3,513 warnings, all for `TEXT` directly in a DEF, and no error. The line
    count above found 3,512; the validator reads tokens and is the number to trust.
- **Not done.** draw-steel's lines are not renamed (F18).

**Applied (owner, 2026-11-12: "Yes, apply them").**

- **2.** The footer's date is 2026-11-12.
- **3.** §19 says "the version of *this specification*", with no number. The validator's header
  says "v0.5, with the v0.6 working draft". The guidelines' title still says "(v0.4)": they have
  not been revised for the 0.5 or 0.6 constructs, so a newer label would claim too much.
- **4.** §5c says "Four additions".
- **7.** The guidelines say a hash is "unique within an edition".
- **8.** §15 gains `SPEC_VERSION`, `true` and `false`, a Parameters line (`PARAMETERS`), a Hooks
  line (`HOOKS`, `HOOK`, `FORMALITY`, `PROSE`, `TAGGED`, `CONDITIONAL`, `FORMAL`, `TRIGGER`) and
  an Optional-rules line (`OPTIONAL`, `GLOBAL`, `SELECTIONS`, `SELECT`, `on`, `off`). A recount
  finds no grammar keyword outside §15 and §18. `TRIGGER` is listed as reserved inside a `HOOK`
  and stays in the system-defined list "outside a `HOOK`": 438 corpus lines write
  `TRIGGER "…"` as a system field, and two files hold a `HOOKS` block. It is one more case of
  item 9.
- **10.** §8's type table shows the type and its value only, and the Modifiers heading says a
  modifier follows any type, with `MIN` and `MAX` for `INTEGER`. The grammar's `ENUM`, `LIST` and
  `LIST OF` rules now take modifiers too; they took none, which would have refused 136 corpus
  lines. Unproven, as every grammar change is.

---

## B. Grammar and validator

### B1. No tool runs the grammar, and it rejects what the corpora write

**Status:** closed 2026-11-12 by the owner. Committed and pushed on branch `0.6`. The grammar
is run by `check_grammar.py` and gated on the repo's fixtures (DECISION-31).

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

**Evidence, measured 2026-11-12.** The table above was made by reading the grammar. For this
count the grammar was run: a small packrat interpreter for Ford's PEG notation, written in the
scratchpad, reads `ttrpg.peg` as it stands on branch `0.6` and parses whole files from `FILE`.

- **The grammar is PEG and reads cleanly, with one exception.** 195 rules. `UPPER_IDENT` ends in
  `!{RESERVED_WORD}`, which is not PEG notation, and no `RESERVED_WORD` rule exists. The run
  reads it the generous way: no word is refused.
- **Six rules are reachable from nothing:** `EMBEDDED_REF`, `EMBEDDED_NAME`, `EMBEDDED_LITERAL`,
  `STRING_CONTENT` and `Q` (added under A2) and `FROM_IMPORT` (added under A3).
- **It accepts 13 of the repo's 37 good fixtures.** The 24 it refuses include every narrative
  container file, both `restate-good` errata files, and `text-good`.
- **It accepts 1,350 of the 7,055 DSL files in the 22 corpus directories (19%).** No corpus is
  accepted whole. aegean, curseborne and troika: no file. vtm5e 1 of 328, tor2e 2 of 374,
  arm5e 548 of 2,435. The best are invisiblesun (36 of 39), daggerheart (25 of 29), dnd5e (10 of
  12) and dnd5.5e (11 of 14).
- **What it refuses**, each tried alone as the one statement in a DEF body:

  | Statement | Result |
  |---|---|
  | `DESCRIPTION "x"` | refused |
  | `EFFECT "x"`, `SOURCE "x"`, `TRIGGER "x"` (a system keyword and a string) | refused |
  | `APPLIES TO [#hash ^"B"]` | refused |
  | `^"L" LIST [#hash ^"B"]` | refused |
  | `^"L" LIST OF #hash ^"B"` | refused |
  | `^"K" ENUM "Gift"` | refused |
  | `^"A" STRING "x"`, `^"F" BOOLEAN true`, `PROPERTIES { … }`, `TAGS ["a", "b"]` | accepted |
  | `EXTENDS #hash ^"B"`, `REFERENCES { … }`, `EMPHASIS { "x" }`, a `GUIDANCE` entry | accepted |

  A file that opens with `SETTING`, `FRAME`, `ARC` or `CAMPAIGN` is refused at its first word
  (131 corpus files), and so is a bare `.actor`.
- **Rows of the first table that no longer hold:** `BOOLEAN true` is accepted since A1,
  `CHOICE` is gone from the spec, and `SCENE ^"Name" #id {` is accepted as a label since A3,
  though the file around it still is not.
- **Three readers of the syntax exist and none is checked against another:** this grammar, which
  nothing runs; the validator's token scanner; and the synthesist's hand-written parser in Go.
- §20 says of lint: "One source of truth: the linter is derived from / checked against the
  grammar." Neither is so.

**Ruling (owner, 2026-11-12):** "Yes, make it run". Written as DECISION-31.

- **The tool.** `check_grammar.py`, a packrat interpreter for the grammar's own notation with
  no dependency. It refuses a grammar that names an undefined rule or holds an unreachable one,
  then parses each file whole and reports the farthest point it reached and what it wanted
  there. `--expect-refused` turns the test round for planted faults.
- **The grammar, repaired.**
  - `RESERVED_WORD` is a rule, and `UPPER_IDENT` refuses those words.
  - A keyword statement (`GENERIC_BLOCK`) is a keyword and what stands on its line. The old rule
    let an optional label take the statement's only value, which is why `DESCRIPTION "x"` was
    refused.
  - One body grammar serves a file, a DEF, a keyword block and a `MODIFY`.
  - `SETTING`, `FRAME`, `ARC` and `CAMPAIGN` files are accepted (`CONTAINER_BLOCK`), and
    `FROM_IMPORT` is reached through them.
  - A reference in a list, after `APPLIES TO`, after `LIST OF` and in `COLUMNS` may carry its
    hash.
  - A DEF may give its hash after its name. A bridge unit may hold a `FIAT`. A list may be
    empty.
  - The embedded-reference rules are declared an entry of their own (`# @entry
    STRING_CONTENT`): they describe the text inside a string.
- **Proof.**
  - As it was, the grammar does not load: `'{RESERVED_WORD}' is not PEG notation`, exit 2.
  - Good fixtures: 35 of 35 files accepted (13 before the repairs).
  - Planted faults: `tests/grammar-bad` holds twelve, and all twelve are refused. The twelfth
    (a `REFERENCES` line with no arrow) was accepted on the first run. Two causes: `REFERENCES`
    was not reserved, and `'REF'` stood before `'REFERENCES'` in an ordered choice and matched
    its first letters. Both are fixed, and the fixture is what showed them.
  - A broken grammar (one rule naming an undefined one) is refused with exit 2.
  - The validator is untouched; its fixtures give the results they gave at the A8 commit.
- **The corpora, measured and not gated.** 5,157 of 7,055 files accepted (73%), from 1,350
  (19%). vtm5e 326 of 328, draw-steel 116 of 118, arm5e 2,112 of 2,435, l5r5e 136 of 166. The
  1,898 refusals are counted in F19.
- **Not done.** The corpora are not at 100% and no corpus gate runs the tool (F19).

### B2. The validator checks little of what the spec says is checked

**Status:** closed 2026-11-12 by the owner. Committed and pushed on branch `0.6`. The validator
checks a value against what its definition extends (DECISION-32).

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

**Evidence, re-run 2026-11-12 against the tools as they now stand.**

*The probe, rebuilt.* One planted violation per file, each beside the same clean base, all
declaring `SPEC_VERSION "0.6"`, and run through the validator, the reference gate,
`check_constructs.py` and the grammar. A clean control instance passes all four.

| # | Planted | Validator | Grammar | Other |
|---|---|---|---|---|
| 1 | `SPEC_VERSION "9.9"` | silent | accepts | |
| 2 | `DEPENDS_ON … VERSION "99.0"`; the parent is 0.1 | silent | accepts | |
| 3 | `INTEGER 7` against an inherited `MIN 1 MAX 5` | silent | accepts | |
| 4 | a value outside the declared `ENUM` | silent | accepts | |
| 5 | `INTEGER "heavy"` | silent | **refuses** | |
| 6 | a `REQUIRED` property left out | silent | accepts | |
| 7 | `LIST OF ^"Skill"` holding a Virtue | silent | accepts | |
| 8 | a bound value outside the parameter's list | silent | accepts | |
| 9 | arguments to a DEF with no `PARAMETERS` | silent | accepts | |
| 10 | more arguments than `PARAMETERS` | silent | accepts | |
| 11 | `CHOOSE DISTINCT 5` from two options | **error** | accepts | |
| 12 | an `EXTENDS` cycle | silent | accepts | |
| 13 | an `ALIAS` cycle | silent | accepts | |
| 14 | `PROPERTEIS { … }` | silent | accepts | |
| 15 | `EXTEND ^"Nonexistent Thing"` | silent | accepts | |
| 16 | stray `>= \| →` | silent | **refuses** | |
| 17 | a DEF after the container's closing brace | silent | **refuses** | |
| 18 | a hash shorter than 16 characters | warning | accepts | |
| 19 | an underscore in a hash | silent | accepts | |
| 20 | `#TODO revisit this` | warning (as a short hash) | **refuses** | |
| 21 | a `HOOK` whose `THEN` list wraps a line and names nothing defined | silent | accepts | `check_constructs.py` silent |
| 22 | one property written twice in an instance | silent | accepts | |
| 23 | a property the type does not declare | silent | accepts | |
| 24 | a `.selections` file selecting an undeclared hash | not read | accepts | `check_constructs.py` **error** |

Of 24, the validator reports one as an error and two as warnings, the grammar refuses four, and
`check_constructs.py` reports one. Sixteen pass every tool. The reference gate reports none.

*What each rule would cost.* A scratch reader built on the validator's tokenizer walked every
DEF in the 22 corpus directories, followed each `EXTENDS` chain by name, and counted what each
rule would report. These are a prototype's counts. It found 39,792 instances and compared
201,527 instance values with a declaration up the chain.

| Rule | Would report | Where |
|---|---|---|
| an `EXTENDS` cycle | 0 | |
| an `ALIAS` cycle | 0 | |
| a bound reference against its `PARAMETERS` (arity, value) | 0 of 107 bound references | |
| a named member of a `LIST OF ^"Type"` that is not of the type | 0 of 1,243 | most list bodies hold unnamed records (F19) and are not counted |
| a hash shorter than 16 | 0 of 221,433 hash tokens | |
| an underscore in a hash | 118 | l5r5e (F2) |
| an `INTEGER` outside the inherited `MIN`/`MAX` | 3 | draw-steel 2 (Ajax the Invincible is `Level 11`, the type says 1 to 10), daggerheart 1 |
| a value not in the inherited `ENUM` | 229 | armdef 92, arm5e 87, draw-steel 50 (`^"Action Type"` "Triggered"; the list has "Triggered action") |
| a value of another type than declared | 222 | arm5e 100, armdef 100, draw-steel 22 (`^"Soak" STRING "+21 (hardened bronze statue)"`, declared `INTEGER`) |
| one property twice in a DEF | 66 | arm5e 33, armdef 33 |
| an instance missing a `REQUIRED` property | 1,386 instances | daggerheart 348, root 331, armdef 236, l5r5e 182, draw-steel 148; most miss `^"Name"`, required on `^"Entity"`. B4 is about what `REQUIRED` means |
| a value for a property no type up the chain declares | 52,123 | arm5e 22,933, armdef 23,075, l5r5e 4,504. No rule of the spec forbids it |
| a `DEPENDS_ON … VERSION` that is not the parent's `VERSION` | 117 of 391 pins | draw-steel: every file pins `"0.5"` and `DS_Core` declares `"0.5.0"`. B5 is about pins |
| a `SPEC_VERSION` that is not a version of the spec | 0 | all 6,316 declaring files say `"0.5"` |

A first count of list members was wrong and is not in the table: it read the fields of unnamed
records as members and reported 5,448. Counting named members only gives the row above.

**Ruling (owner, 2026-11-12):** "Yes, add them". Written as DECISION-32.

- **Validator.** A collector records each definition's properties, parameters and list members,
  and a pass checks them against what the definition extends.
  - Errors at every version: a cycle of `EXTENDS` or of `ALIAS`; a bound reference with too
    many arguments, with arguments where its base declares no `PARAMETERS`, or with a string
    outside a parameter's list.
  - Gated (a warning below 0.6, an error from 0.6) and waived by `FIAT`: an `INTEGER` outside
    the range it inherits, a value outside the `ENUM` it inherits, a value of another kind than
    its type, a named list member that is not of the list's type, one property written twice.
  - A hash under 16 characters, or with an underscore: the same gating, no waiver.
- **`check_constructs.py`** reads every DSL file type (it read `.ttrpg` only), joins a `THEN`,
  `CONCERNS` or `SCOPE` list that wraps a line, reads a list that a comment follows, and counts
  a named block's hash as an anchor.
- **Spec.** §6 says `EXTENDS` is acyclic. §5 states the hash format's severity. §20 lists what
  is checked, at what severity, and what is not.
- **Proof.**
  - The probe: the validator now reports 14 of the 24 planted violations (3 before). With the
    grammar and `check_constructs.py`, 18 are caught. The six that pass every tool are the two
    left to B4 and B5, the two misspelt keywords, `SPEC_VERSION "9.9"`, and a value for an
    undeclared property.
  - Fixtures: `tests/values-good` gives 0 errors and 0 warnings in the validator and 0 errors
    in `check_constructs.py`. `tests/values-bad` holds one fault per file and gives 15 errors
    and 4 warnings in the validator, and 1 error in `check_constructs.py`.
  - Every earlier fixture gives what it gave at the B1 commit.
  - Old tools against new on the 22 corpus directories. Validator: 15 directories are
    byte-identical and 7 gain warnings, 815 in all, with no new error (F20).
    `check_constructs.py`: 0 errors in all 22, as before, and it now counts guidance in `.arc`
    and `.actor` files (vtm5e 727 to 733, curseborne 6 to 11).
- **Two corrections made on the way.**
  - The list-member rule was to be an error at every version, on a count of zero. The count was
    wrong: the prototype skipped definitions that extend nothing. The validator found 15
    (curseborne 14, teeth 1), so the rule is gated like the other value rules.
  - Reading `.arc` files, `check_constructs.py` first reported two `CONCERNS` hashes as
    undeclared. Both name a `SCENE`, which is a legal target since DECISION-24. The tool now
    indexes named blocks.

### B3. Name equality is undefined, and the gates use two different rules

**Status:** closed 2026-11-12 by the owner. Committed and pushed on branch `0.6`. §14 says when
two names are the same, and every tool here compares that way (DECISION-33).

The spec does not say when two names are the same (case, punctuation, straight or curly
apostrophe, Unicode form). The validator compares exactly. `check_references.py` and
`check_constructs.py` lower-case the name and drop everything that is not a letter or digit. Under
that rule tor2e's `^"+2"`, `^"−2"`, `^"#2"` and `^"2"` are one name. Names that differ exactly and
fold together: vtm5e 221 groups (`Extortionist` / `Extortionist:`), arm5e 27, tor2e 24, root 23
(`Don't` / `Don’t`), l5r5e 8.

In the probe, `EXTENDS ^"virtue"` is an undefined reference to the validator and a resolved,
hashless reference to `check_references.py`.

**Evidence, measured 2026-11-12.**

*Who compares how.* The validator and the synthesist compare names exactly.
`check_references.py`, `check_constructs.py` and `apply_references.py` fold a name first: lower
case, a curly apostrophe made straight, then every character outside `a-z0-9` dropped. That
fold drops an accented letter whole: `Mahō` becomes `mah`.

*Definitions.* The 22 corpus directories define 98,095 names. Distinct names that become one:

| Rule | Groups that merge | Examples |
|---|---|---|
| quote style, Unicode form and spacing only | 43 | `Jupiter's Touch` / `Jupiter’s Touch` (armdef); `I'll Take That` / `I’ll Take That` (root) |
| case as well | 462 more | `Status` / `status` (l5r5e); `Exhaustion` / `exhaustion` (root); `PEOPLE PERSON` / `People Person` (vtm5e) |
| the gates' fold as well | 518 more | `Orcs` / `Orcs!` (tor2e); `Feeding` / `Feeding:` (vtm5e); `16-18` / `16–18` (pendragon5e); `Long Bow` / `Longbow` (root); `Earth (op)` / `Earth (op)+` (l5r5e) |

*References.* Two scans: the validator's sites (84,723 references) and the gate's own
(`REFERENCES` arrows and `CONCERNS`, `THEN` and `SCOPE` lists: 13,293).

- 86,291 references carry a hash. In all but 4 the name is the anchor's name, character for
  character. The 4 are in callofcthulhu7e: `^"PILOT"` for `^"Pilot"`, `^"Key"` for `^"Key:"`,
  and one sidebar title written twice in other capitals.
- 11,703 hashless references match a definition exactly. One resolves only under the gates'
  fold: l5r5e's embedded `^"Tent [Small]"`, for `^"Tent (Small)"`. 17 resolve under no rule
  (F10).
- So 5 references in about 98,000 depend on folding.

*The gate, run three ways over the 22 directories.* Its own fold: 31 errors and 397 hashless
WARNs. Exact comparison: 36 and 396. Quote style, Unicode form and spacing folded: 36 and 396.
The two stricter rules give the same result as each other, and differ from today's in two
corpora only: callofcthulhu7e gains 4 errors and l5r5e gains 1.

**Ruling (owner, 2026-11-12):** "Yes, that rule". Written as DECISION-33.

- **The rule.** Two names are the same when their characters are the same after Unicode normal
  form, a run of white space read as one space, and a curly quote read as a straight one. Case,
  punctuation and accents count.
- **Spec.** §14 has a section, *When two names are the same*, with a table of pairs. §5d points
  at it.
- **Tools.** One function, written the same in three files: `name_key` in the validator, applied
  to every caret name as it is read and to a definition named by a string; `nk` in
  `check_references.py` and in `check_constructs.py`, in place of their fold.
- **Proof.**
  - `tests/names-good` writes each definition one way and references it another (a curly
    apostrophe for a straight one, a combining accent, two spaces, a no-break space): 0 errors
    and 0 warnings in the validator, 0 errors and 0 hashless WARNs in the gate, 0 errors in
    `check_constructs.py`.
  - `tests/names-bad` references by another case, without a `!`, without an accent, and with
    brackets for parentheses: 4 errors in the validator, 4 in the gate, 1 in
    `check_constructs.py`.
  - Old tools against new on the 22 corpus directories. Validator: byte-identical output in all
    22. Reference gate: identical in 20; callofcthulhu7e goes from 0 errors to 4 and l5r5e from
    30 to 31. `check_constructs.py`: identical in 21; callofcthulhu7e goes from 0 errors to 4,
    the same four `CONCERNS` lines.
- **Not done.** The five references are not corrected, and the synthesist is not changed (F21).

### B4. `REQUIRED` means one thing in §8 and another in the only tool that checks it

**Status:** closed 2026-11-13 by the owner. Committed and pushed on branch `0.6`. `REQUIRED`
means every entry of the type has the property, and the validator checks it (DECISION-34).

§8: "`REQUIRED` — must be provided". The validator does not check it. `check_structure.py` fails
only when a `REQUIRED` property is populated on zero instances of its type. On arm5e it prints
`^"Ability".^"Ability Type" REQUIRED, on 136/167` as a note, and fails on `^"House"` being populated
on 0 of 13 `Magus` instances.

Related: `check_structure.py` fails two of the three corpora today (vtm5e: 11 `PROPERTIES` blocks
to 12,724 `DESCRIPTION`s, 252 empty DEFs; arm5e: the `House` error). Neither repo's `gates.sh` runs
it. l5r5e has no `gates.sh`. vtm5e writes its properties directly in the DEF body with no
`PROPERTIES` block (12,839 `STRING` values, 11 blocks), which §0 calls non-canonical.

**Evidence, measured 2026-11-13.** Counted with `check_structure.py`'s own reading of what a
type is, what an instance is, and what fills a property, over the 22 corpus directories.

- **What the spec says.** §8: "`REQUIRED` — must be provided". §8 on `FIAT`: it waives
  "completeness requirements (`REQUIRED` / missing fields)". §5: an instance is a DEF that
  extends an actor type and fills in values. Nothing says who must provide, or what counts.
- **What the tool does.** It fails a `REQUIRED` property that no instance of its type fills,
  and prints a note for one that some instances leave out. Today: 6 errors (arm5e 1, armdef 2,
  draw-steel 3) and 23 notes.
- **The declarations.** 842 properties are declared `REQUIRED`, 239 of them `^"Name"`. 170 sit
  on a type with no instance. None is also given a `DEFAULT`.
- **The instances.** The other 672 declarations face 81,447 instance slots, and 81,086 are
  filled (99.6%). 638 declarations are met by every instance, 28 by some, 6 by none.
- **Read as "every instance must provide", 361 slots are empty,** in four corpora: armdef 210,
  arm5e 71, l5r5e 50, draw-steel 30. The largest: `^"Laboratory Virtue".^"Category"` missing on
  70 of 96 (armdef) and `^"Laboratory Flaw".^"Category"` on 64 of 93;
  `^"Ability".^"Ability Type"` on 31 of 167 (arm5e); `^"School".^"Clan"` on 27 of 110 (l5r5e);
  `^"Magus".^"House"` on all 13 (arm5e); `^"Hero"`'s `^"Kit"`, `^"Class"` and `^"Ancestry"` on
  all 10 (draw-steel).
- **`^"Name"` and the DEF's own name.** The tool counts a required `^"Name"` as filled by the
  DEF header. 5,969 instances extend a type that requires `^"Name"`. 4,955 write
  `^"Name" STRING "…"` as well as their header. 1,014 are named by the header alone:
  daggerheart 348 of 348, root 331 of 331, draw-steel 157 of 157, arm5e 81 of 81, armdef 80 of
  80, teeth 14, l5r5e 3. The spec's own instance in §5, `^"Ide Tadaji"`, is one of this kind:
  §17's `Samurai` requires `^"Name"` and the instance does not write it.
- **What else the tool counts as filled:** the property written on the instance, with or
  without a value; a value given by a type up the chain; a `PARAMETERS` slot of that name. An
  element-level `FIAT` takes the instance out of the count.

**How `REQUIRED` is used today, measured 2026-11-13 at the owner's request.**

- **How often.** Types declare 4,790 properties and mark 835 of them `REQUIRED` (17%). The
  share runs from 65% (mythic-gme2) and about 42% (curseborne, pendragon5e, troika) down to 1%
  (callofcthulhu7e, daggerheart, dnd5e, dnd5.5e).
- **On what.** 782 of the 835 sit on a type that is not an `ACTOR` type: a kind of entry or a
  row of a table (`^"Roll Table Entry"`: `^"Roll"`, `^"Text"`; `^"Hymn Power"`: `^"Range"`,
  `^"Duration"`, `^"Target"`; `^"Fate Chart Cell"`; `^"Glossary Entry"`: `^"Term"`). 53 sit on an
  `ACTOR` type (`^"Samurai"`: `^"Clan"`, `^"Family"`, `^"School"`; `^"Hero"`: `^"Ancestry"`,
  `^"Class"`, `^"Kit"`; `^"Magus"`: `^"House"`). 239 of the 835 are `^"Name"`.
- **Who reads it.** `check_structure.py` is the only tool that acts on it. The synthesist
  carries it into the resolved JSON as a modifier. The dashboard's parser records it and the
  engine strips it; neither acts on it. UNVERIFIED for the VTT instances, which were not
  searched.
- **Three meanings are in use under the one word.**
  - *Every entry has this field.* The 782. A statement about the source's entries, and nearly
    always true: this is where the 99.6% comes from.
  - *A finished player character must have this.* The `ACTOR` declarations other than
    `^"Name"`. A rule of character creation, written on a type that NPCs, templates and
    subtypes also extend.
  - *`^"Name"`.* The 239, which the DEF's own name already answers.
- **The unmet ones, opened.**

  | Declaration | Unmet on | What the instances are |
  |---|---|---|
  | armdef `^"Laboratory Virtue".^"Category"` | 70 of 96 | *Covenants*' laboratory virtues. They carry `^"Group"` and no `^"Category"`; the type was written from the Definitive core's entries |
  | arm5e `^"Ability".^"Ability Type"` | 31 of 167 | abilities from *Rival Magic* and *Realms of Power: The Divine* with a `^"Source"` and a `^"Page"` and nothing else |
  | l5r5e `^"School".^"Clan"` | 27 of 110 | *Path of Waves* traditions (`^"Ganzu Guardian Tradition"`), which belong to no clan |
  | l5r5e `^"Samurai".^"School"` | 8 of 27 | seven pregenerated characters with a clan, a family and rings, and no school property |
  | arm5e `^"Magus".^"House"` | 13 of 13 | the template magi, one per House, named `^"Bjornaer"`, `^"Bonisagus"`: the House is the DEF's name |
  | draw-steel `^"Hero"`'s `^"Kit"`, `^"Class"`, `^"Ancestry"` | 10 of 10 | the ten classes (`^"Censor"`, `^"Conduit"`). Each is a kind of hero; none is a character |

**Ruling (owner, 2026-11-13):** "Yes, that meaning only". Written as DECISION-34.

- **The meaning.** `REQUIRED` says that every entry of the type has the property. It is a
  statement about the source's entries. It is not used for a rule of character creation, and a
  required `^"Name"` is answered by the DEF's own name.
- **Spec.** §8 has a section on `REQUIRED`: who must have the property, what counts as having
  it, `^"Name"`, why a rule of play is written as a `CHOOSE`, the `FIAT` for an entry the book
  prints without the field, and the severity. §20's table lists the check.
- **Validator.** An instance that lacks a property a type up its chain declares `REQUIRED` is
  reported once, with the properties and the type named: a warning below 0.6, an error from
  0.6, waived by an element-level `FIAT`. Entries written inside another DEF are checked too.
- **`check_structure.py`** no longer checks `REQUIRED`. It keeps its shape check. The 280 lines
  that read types and instances for the old check are removed.
- **Proof.**
  - `tests/required-good` gives 0 errors and 0 warnings: a property written on the instance;
    one given by a type above; `^"Name"` by the DEF's name; a `PARAMETERS` slot; a `FIAT`; a
    subtype that declares and owes nothing. `tests/required-bad` gives 3 errors in a file that
    declares 0.6 and 1 warning in one that declares 0.5.
  - The spec's own example, run as a file: 0 errors and 0 warnings, and the grammar accepts it.
  - Old validator against new on the 22 corpus directories: 18 byte-identical. Four gain
    warnings and nothing else, 302 in all: armdef 196, arm5e 55, l5r5e 41, draw-steel 10.
  - `check_structure.py`, before and after: arm5e, armdef and draw-steel go from FAIL to PASS,
    since each failed on `REQUIRED` alone. Seven directories still fail on shape.
- **Against the census.** The validator's 302 findings cover 334 empty slots, where
  `check_structure.py`'s reading gave 361. The validator counts a `TEMPLATE` as a type, so
  arm5e's and armdef's template magi no longer owe a `^"House"` (13 and 12 slots).
- **Not done.** The 302 are not triaged, and the `ACTOR` declarations that state a rule of
  character creation are not rewritten (F22).

### B5. Version pins and the dependency model

**Status:** closed 2026-11-13 by the owner. Committed and pushed on branch `0.6`. A pin means
"at least" (DECISION-35), a file's dependencies are defined and checked (DECISION-36), and a
dependency loads first (DECISION-37).

- `DEPENDS_ON "Parent" VERSION "x"`: the spec does not say whether the match is exact, minimum or a
  range. No tool checks it. All 68 pins in l5r5e name `0.5.9`; the parent declares `0.5.10`. The
  standing rule to bump `VERSION` on every edit guarantees this drift.
- §3: an EXTENSION declares "a parent". 25 arm5e files declare more than one `DEPENDS_ON`.
- Both parent forms are in use. vtm5e heads 326 files with `EXTENSION "X" EXTENDS "Y"`, arm5e
  writes `DEPENDS_ON` 2,522 times, and l5r5e uses both (29 and 103). The spec keeps both and does
  not say what a file with both means.
- §13: load order is precedence. No DSL construct states a load order. `DEPENDS_ON` gives a partial
  order; the rest is the consumer's manifest, which the spec does not define.

**Evidence, recounted 2026-11-13** over the 7,055 DSL files in the 22 corpus directories, with
the validator's tokenizer.

*Version pins.* 459 `DEPENDS_ON … VERSION` lines, in four corpora.

| Corpus | Pins | The pin | The parent's `VERSION` |
|---|---|---|---|
| pendragon6e | 243 | `"0.5"` | `"0.5"`: equal |
| draw-steel | 117 | `"0.5"` | `"0.5.0"`: the pin is its first two parts |
| l5r5e (68 `.codex` files) | 68 | `"0.5.9"` | `"0.5.10"`: the parent has moved on |
| pendragon5e | 31 | `"0.5"` | `"0.5"`: equal |

No tool reads a pin. The other 5,114 `DEPENDS_ON` lines carry none.

*How a file names what it needs.* Of the 6,259 `EXTENSION`, `ARC`, `FRAME`, `SETTING` and
`CAMPAIGN` files:

| Form | Files | Where |
|---|---|---|
| `DEPENDS_ON` only | 5,012 | arm5e, armdef, draw-steel and others |
| `EXTENSION "X" EXTENDS "Y"` only | 923 | vtm5e 326, teeth 90, pendragon5e 87, root 76, and 14 more |
| both | 276 | pendragon6e 243 and pendragon5e 31 (the header names the base, `DEPENDS_ON` names a types file), l5r5e 2 |
| neither | 48 | 36 `SETTING` files, and 12 `EXTENSION` files (arm5e 5, armdef 5, l5r5e 2) |

- 49 files carry more than one `DEPENDS_ON`, all in arm5e and armdef. `arm5e-0.5-errata.ttrpg`
  has 20, one for each book it corrects.
- Three armdef files are declared `BASE` and carry a `DEPENDS_ON` on another `BASE`
  (`armdef-0.5-core-character-creation.ttrpg`). §3: a `BASE` has no parent.
- 25 header `EXTENDS` name an id no file declares: l5r5e 14 (`EXTENDS "l5r5e"`), teeth 11. Every
  `DEPENDS_ON` target is a file id.
- Four ids in root are each declared by two files, an `.arc` and a `.frame`
  (`"PellenickyGlade"`).
- No two files depend on each other, through any chain.
- 670 bare `.actor` files have no id and name nothing (F17).

*What the validator checks,* tried on seven small sets. It reports a `DEPENDS_ON` whose target is
no file id. It is silent on a header `EXTENDS` whose target is no file id, on a pin of `"9.9"`
against a parent at `"1.2.0"`, on two files that depend on each other, on an `EXTENSION` that
names no parent, and on two files with one id.

*Load order.* Eleven synthesist manifests list their files in load order. Of the 5,338
dependencies their files declare, the target loads before the file that needs it in 5,319. It
loads after in 19: 18 in `armdef-0.5-full` and 1 in `arm5e-0.5-full`
(`arm5e-covenants-0.5-example-laboratories.ttrpg` is listed before
`arm5e-covenants-0.5-laboratory.ttrpg`, which it depends on).

**Ruling on Part 1 (owner, 2026-11-13):** "Yes, at least". Written as DECISION-35.

- **Spec.** §3 says what a pin means and how two versions are compared; §19 and §20 agree.
- **Validator.** It reads each file's own `VERSION` and each pin, in ordinary and codex files,
  and reports a loaded parent that is older than the pin as an error. A parent with no
  `VERSION` is a warning.
- **Proof.** `tests/pins-good` (an equal pin, a pin the parent has moved past, a pin of two
  parts) gives 0 errors and 0 warnings. `tests/pins-bad` gives 2 errors and 1 warning: a pin
  newer than the parent, `"0.10"` against `"0.5.9"`, and a parent with no `VERSION`. Old
  validator against new on the 22 corpus directories: byte-identical output in all 22. The new
  check reads all 459 pins there, knows the parent's version for each, and reports none.

**Ruling on Parts 2 and 3 (owner, 2026-11-13):** "Yes, both". Written as DECISION-36 and
DECISION-37.

- **Part 2, the spec.** §3 says a file depends on every `DEPENDS_ON` it writes and on the id
  its header `EXTENDS`, any number of them, with two real examples. Each names a loaded file;
  no two files depend on each other; a file id is declared once; an `EXTENSION` names a parent
  and a `BASE` does not.
- **Part 2, the validator.** A cycle is an error at every version. A header `EXTENDS` that
  names nothing, an id declared twice, an `EXTENSION` with no parent and a `BASE` with one are
  warnings below 0.6 and errors from 0.6.
- **Part 3.** §13 states the one rule: a file loads after everything it depends on. Any order
  beyond that is the consumer's, and the spec defines no manifest. No tool here is given an
  order, so nothing here checks it.
- **Proof.**
  - `tests/deps-good` (the header form, `DEPENDS_ON`, both, and three `DEPENDS_ON` in one file)
    gives 0 errors and 0 warnings. `tests/deps-bad` holds seven faults and gives 7 errors and 1
    warning.
  - Every earlier fixture gives what it states, after one correction: 14 helper files in
    `tests/ports-bad` and `tests/actors-bad` were extensions that named no parent, and each now
    has a `DEPENDS_ON`.
  - Old validator against new on the 22 corpus directories: 17 byte-identical. Five gain
    warnings and nothing else, 44 in all (F23).
- **Not done.** The 44 are not corrected, and the 19 manifest lines that load a file before
  its dependency are not reordered (F23).

---

## C. Design

### C1. The type system sends references and numbers into strings

**Status:** closed 2026-11-13 by the owner. Committed and pushed on branch `0.6`. No value
types are added. A change that holds in a situation is a `SITUATIONAL` block (DECISION-38).
The type keywords are dropped: a value is written alone (DECISION-39). A signed number is a
`SET` or a `TRANSFORM`, decided in conversion (DECISION-40). The entries of a list need not be
named (DECISION-41). `REF` (DECISION-17) and `SET` / `TRANSFORM` (DECISION-16) came under A1.
No corpus uses any of these yet: F24, F25 and F26. Units, ranges, decimals and dice stay in
strings. The rulings and their proof are at the end of this section.

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

**Evidence, recounted 2026-11-13** over the 22 corpus directories, with the validator's
tokenizer. Each `^"Property" STRING "value"` line and each string in a list was sorted by what
the string holds.

| What the string holds | `STRING` values (328,228) | Items of string lists (93,012) | Most in |
|---|---|---|---|
| a short label | 147,400 | 55,277 | |
| exactly the name of a defined entity | 88,215 | 21,433 | invisiblesun, marvelmultiverse, armdef, arm5e |
| prose | 52,071 | 7,312 | |
| a whole number | 21,449 | 4,290 | marvelmultiverse 5,967, pendragon6e 3,845 |
| a number and a unit (`"30 feet"`, `"1 week"`, `"10%"`) | 7,850 | 930 | draw-steel 1,682, armdef 1,225, dnd5e 954 |
| a signed number (`"+3"`, `"–10"`) | 5,865 | 251 | armdef 2,025, arm5e 1,941, marvelmultiverse 1,512 |
| a range (`"30–70"`) | 1,728 | 1,503 | pendragon6e, pendragon5e |
| dice (F6) | 1,489 | 322 | dnd5.5e, pendragon6e, dnd5e |
| an entity's name and a number (`"Artisan 3"`) | 1,116 | 723 | pendragon6e 383, marvelmultiverse 351; l5r5e 637 list items |
| a pair of numbers (`"5/2"`) | 744 | 119 | vtm5e 521 |
| a decimal | 75 | 26 | troika 51 |

The entity-name row is an upper bound. It counts a DEF that writes its own name as
`^"Name" STRING "…"`, and a category word that happens to be a DEF.

Shapes in use that §8 gives no form:

| Shape | Count | Where |
|---|---|---|
| `^"Level" ENUM "subsection"`: an `ENUM` with one value and no list | 10,601 lines | invisiblesun 7,497, root 1,654, mythic-gme2 548, daggerheart 471, callofcthulhu7e 396 |
| an unnamed `DEF { … }` as an item of a list | 24,133 records in 5,417 lists | marvelmultiverse 10,713, pendragon6e 6,054, pendragon5e 3,782, aegean 1,490, tor2e 996 |
| a string and a number on a line: `"Hungry" +6` | 2,581 lines | armdef 1,340, arm5e 1,241, inside `PERSONALITY_TRAITS { … }` and like blocks |
| a signed number and a string: `+2 "Voice"` | 1,754 lines | armdef 884, arm5e 870 (F5) |

No file writes `INTEGER +3`: a signed number is always a string today. The grammar's integer
takes a `-` and no `+`, and the validator's tokenizer drops a `+`.

**The owner's reason for not adding types (2026-11-13):** "in many, many, many games, even
some something starts as a straightforward integer there are inevitably exceptions that are not
integers, etc."

Measured against that, over 21 corpus directories (armdef left out as arm5e's mirror): 329
properties hold a number at least four times in five, 97,365 values between them.

- 254 are a number every time.
- 75, nearly one in four, hold something else at least once: 1,026 values, about 1 in 100.
- What the exceptions look like: arm5e `^"Soak"` `"+4 (armor and Stamina)"` (186 of 1,039);
  arm5e `^"Initiative"` `"constant"`; l5r5e `^"Composure"` `"Infinity"`; aegean `^"Rank"`
  `"Minion"`, `"Champion"`, `"Legend"` beside 402 numbers; aegean `^"Cost"` `"1 per Populace"`;
  arm5e `^"Divine Might"` `"No less than 25"`; tor2e `^"Injury"` `"16 (1h)/18 (2h)"`;
  pendragon6e `^"Value"` `"—"`.
- 35 of the 329 are written both ways in one corpus: `INTEGER 3` in one place and `STRING "3"`
  in another.

This bears on DECISION-32. One of its checks reports a value written `STRING` where the type
declares `INTEGER`: a warning below 0.6 and an error from 0.6 unless the value carries a
`FIAT`. Those findings are the exceptions the owner describes. (This paragraph first gave their
number as 222. The corpus run for DECISION-39 counted 432 on the 22 directories: arm5e 205,
armdef 205, draw-steel 22.)

**Two directions from the owner (2026-11-13).** Both are ruled, at the end of this section.

- "we should introduce something like SITUATIONAL as a primitive for things like this, where
  the value is one thing but modified to another under specific situations. The modification of
  a value would be a TRANSFORM as normal generally, but with a condition (which is usually going
  to be narratively-defined)."
- "we should get rid of references to "STRING" and "INTEGER", etc. you may present a case to the
  contrary if you wish."

*How the type keywords are used,* counted on the 22 corpus directories:

| Line | Count |
|---|---|
| `STRING` followed by a value | 275,749 |
| `INTEGER` followed by a value | 92,493 |
| `BOOLEAN` followed by a value | 2,869 |
| `LIST OF ^"Type"` with items | 24,915 |
| `ENUM` with one value | 10,601 |
| `LIST` with items | 9,393 |
| `STRING`, `INTEGER` or `BOOLEAN` alone: a declaration with nothing else to say | 2,204 (2,161 inside `PROPERTIES`, 43 directly in a DEF) |
| `STRING`, `INTEGER` or `BOOLEAN` with modifiers and no value | 1,923 |
| `LIST OF ^"Type"` alone | 840 |
| `ENUM` with a list: a declaration | 346 |
| a name and a value with no keyword (a list 1,106, a reference 649, a string 262) | 2,017, of which l5r5e 1,225 |

In 371,111 lines the keyword stands before a literal that already shows what it is.

*What reads the keywords.* The validator, the grammar (73 lines) and the spec (153 lines). The
synthesist (23 files), and its resolved JSON gives every property a `"type"` (`"STRING"`,
`"INTEGER"`, `"LIST OF STRING"`). The dashboard (5 files), the engine (14) and mastra (118). 504
conversion scripts under `Titterpig/Temp` write them. UNVERIFIED: which consumers act on the
JSON's `"type"`.

*Strings that give a number and then qualify it:* 9,709 (arm5e and armdef 7,280, vtm5e 838,
callofcthulhu7e 504). They are of several kinds: a value that differs by situation (tor2e
`^"Injury"` `"16 (1h)/18 (2h)"`), a change with a limit (l5r5e `^"Status Award"`
`"+5 (to a minimum of 20)"`), an alternative (draw-steel `^"Size"` `"2 or 3"`), a number and a
unit, and a list of thresholds (arm5e `^"Wound Penalties"`).

**`SITUATIONAL`: ruled and applied, 2026-11-13 (DECISION-38).**

The owner was shown this form and answered "Yes, as written":

```
^"Injury" INTEGER 16
SITUATIONAL "2h" {
    ^"Injury" SET 18
}
```

- `SITUATIONAL <condition> { <changes> }`, wherever a `SET` or `TRANSFORM` may stand.
- The condition is a string in the source's words, or a reference to an entity where the system
  defines the situation as one.
- The changes are ordinary §8 statements, one or more.
- The value outside the block holds otherwise. A consumer shows the changed value beside it and
  applies nothing itself.
- A `HOOK` names the mechanic a situation involves; `SITUATIONAL` gives the value.

*Applied.* The spec: §0 item 25, DECISION-38, a new §8 section after "Changes to a value", the
§5d list of reference sites, the §15 keyword list. `ttrpg.peg`: `SITUATIONAL_BLOCK`, in a body, a
`PROPERTIES` block and a property `DEF`, and the word in `RESERVED_WORD`. `ttrpg_validator.py`:
the checks below. `AUTHORING-GUIDELINES.md` and `README.md`: one line each.

*What the validator checks,* each an error at every version:

| Fault | Message |
|---|---|
| no condition | `SITUATIONAL needs a condition` |
| an empty string as the condition | `SITUATIONAL has an empty condition` |
| no block after the condition | `SITUATIONAL needs a block of changes` |
| a block with no change | `holds at least one change` |
| a value or any other statement in the block | `holds changes only` |
| a `SITUATIONAL` inside another | `does not hold another SITUATIONAL` |
| a condition that is a reference and does not resolve | the reference check's finding |
| a target that is no property of the definition and no entity | the reference check's finding |

A fault in a change inside the block (a `TRANSFORM` with no method) is reported as it is outside
one.

*Proof,* all run on 2026-11-13:

| Check | Result |
|---|---|
| `ttrpg_validator.py tests/situational-good` | 0 errors, 0 warnings |
| the validator as it was before the change, on the same file | 5 errors: it reads each hashless target as a reference to an entity |
| `ttrpg_validator.py tests/situational-bad` | 10 errors, 0 warnings: nine planted faults, and the unresolved condition reports its name and its hash |
| the §8 example, wrapped in a `BASE` and run as a file | validator 0 errors, 0 warnings; grammar accepted |
| the 17 older good sets | 0 errors, 0 warnings each |
| the 15 older bad sets | the same counts as at the B5 commit |
| `check_grammar.py tests/*good* tests/decision6.ttrpg tests/ports-origin modules/0.6` | 49 of 49 accepted |
| `check_grammar.py tests/grammar-bad --expect-refused` | 14 of 14 refused (two new: no condition; a value in the block) |
| old validator against new, on the 22 corpus directories with `modules/0.6` | output identical for all 22; 7,077 files, 39 errors, 20,496 warnings both times |
| `grep -w SITUATIONAL` over the 22 corpus directories | no file holds the word |

*Not done.*

- The grammar was not re-run over the corpora. No corpus file holds the word, and the grammar's
  only changes are a rule that begins with it and its place among the reserved words.
- No corpus is changed. Which of the 9,709 qualified strings are situational values is F24.
- The synthesist and every other consumer do not read the block (F3).
- `check_references.py` does not count a change's target or a `SITUATIONAL` condition among its
  reference sites, as it does not for `SET` and `TRANSFORM` today. The validator checks both.
- The printed cell (`"16 (1h)/18 (2h)"`) is not kept by the form. A corpus that wants it keeps
  it in a property of its own.

**The type keywords: ruled and applied, 2026-11-13 (DECISION-39).**

The owner was asked "Drop STRING, INTEGER, BOOLEAN and instance-side LIST and ENUM, keeping the
declaration constraints?" and answered "Yes, that scope". Asked "Keep the old keywords silent in
files below 0.6, with an error only from 0.6?", he answered "Yes, silent below".

| Before 0.6 | From 0.6 |
|---|---|
| `^"Honor" INTEGER 35` · `^"Name" STRING "Hida"` · `^"Starting" BOOLEAN true` | `^"Honor" 35` · `^"Name" "Hida"` · `^"Starting" true` |
| `^"Roles" LIST ["Bushi"]` · `^"Tags" LIST OF STRING ["a"]` | `^"Roles" ["Bushi"]` · `^"Tags" ["a"]` |
| `^"Level" ENUM "Chapter"` (never in the spec; 10,601 corpus lines) | `^"Level" "Chapter"` |
| `^"Honor" INTEGER MIN 0 MAX 100 DEFAULT 50` | `^"Honor" MIN 0 MAX 100 DEFAULT 50` |
| `^"Notes" STRING` | `^"Notes"`, alone on its line, in a `PROPERTIES` block or a property `DEF` |
| `^"Tags" LIST OF STRING` | `^"Tags" LIST` |
| `INTEGER MIN 1 MAX 5` in a DEF's body (§9) | `MIN 1 MAX 5` |
| `PARAMETERS { ^"area" OF STRING }` | `PARAMETERS { ^"area" }` |
| `AXIS ^"Successes" INTEGER` | `AXIS ^"Successes"` |

Unchanged: `ENUM [ … ]`, `LIST OF ^"Type"` with or without items, `REF OF ^"Type"`, `REF`,
`ROLL`, `DEF`, and every modifier.

*Applied.*

- **Spec:** §0 item 26; DECISION-39; §8 rewritten ("Values and declarations", "Modifiers",
  "A value with its constraints", "Where a statement ends"); §9 renamed "Bare Constraints";
  §5b parameters; §5e axis points; §15 keyword lists; §20's table of value checks; a note on
  DECISION-32. 138 lines of code examples were rewritten by script and read. The records of
  earlier decisions keep the keywords they describe.
- **`ttrpg.peg`:** a value with no keyword, with constraints after it; a declaration that is a
  name and its constraints, or a name alone on its line; `LIST` alone; the constraints alone
  in a DEF's body; a parameter with no domain; an axis with no points; a keyed `CHOOSE` with a
  bare value. The grammar still reads the keywords, for files below 0.6.
- **`ttrpg_validator.py`:** reads the forms above as properties and declarations; reports
  `STRING`, `INTEGER`, `BOOLEAN`, `LIST` before a list and `ENUM` before a single value as
  errors in a file that declares 0.6 or later; no longer compares a value's kind with the
  type it inherits; applies `MIN` / `MAX` to a value only when it is a number.
- **`check_structure.py`:** counts `^"Description" "…"` as it counted `^"Description" STRING`.
- **Fixtures:** every fixture that declares 0.6 and the dice module were rewritten by the same
  script (176 lines). New: `tests/keywords-good` (a 0.6 file with every form, and a 0.5 file
  that keeps the keywords), `tests/keywords-bad` (12 planted faults),
  `tests/grammar-bad/15-min-without-a-number.ttrpg`.
- **`AUTHORING-GUIDELINES.md`, `README.md`.**

*Proof,* all run on 2026-11-13:

| Check | Result |
|---|---|
| `tests/values-good` before it was rewritten, new validator | 12 errors: the gate fails on the keywords |
| the same set after the rewrite | 0 errors, 0 warnings |
| `ttrpg_validator.py tests/keywords-good` | 0 errors, 0 warnings, the 0.5 file's keywords included |
| the old validator on `tests/keywords-good` | 1 warning of the withdrawn kind (`"5 (7 against arrows)"` where the type declares `INTEGER`) |
| `ttrpg_validator.py tests/keywords-bad` | 12 errors, one for each planted fault |
| the 19 other good sets | 0 errors, 0 warnings each |
| the 16 other bad sets | as before, except `values-bad`: 13 errors and 5 warnings (was 15 and 4; see the calls below) |
| the §8 and §9 examples assembled into one file | validator 0 errors, 0 warnings; grammar accepted |
| the 23 whole-file examples in the spec | 17 accepted and 6 refused, before and after; no type keyword left in them |
| `check_grammar.py tests/*good* tests/decision6.ttrpg tests/ports-origin modules/0.6` | 51 of 51 accepted |
| `check_grammar.py tests/grammar-bad --expect-refused` | 15 of 15 refused |
| old validator against new, 22 corpus directories with `modules/0.6` | 19 identical. arm5e and armdef lose 205 warnings each and draw-steel 22: the 432 "written `STRING`; declares it `INTEGER`" findings, now withdrawn. Errors 39 before and after; warnings 20,496 to 20,064 |
| old grammar against new, 22 corpus directories | no file that was accepted is refused. 3 more are accepted (the Lion and the Lily `core-ext` file in arm5e and in armdef, and draw-steel's `monsters-base`): 5,160 of 7,055, from 5,157 |

*What the corpus run caught.* A first version let several declared names share a line
(`PROPERTIES { ^"Size" ^"Category" }`). Eight corpora write two names on a line for a
property and the type it holds (`^"Class" ^"Class"`, daggerheart), and the run reported 53
false "written twice" warnings. The form was withdrawn: a declared name stands alone on its
line.

*Not done.*

- No corpus is migrated, and none declares 0.6. Follow-up F25.
- The synthesist, the engine, the dashboard, mastra and the 504 conversion scripts still read
  and write the keywords (F25).
- `.bridge` and `.codex` files are not checked for the keywords: the validator reads them by
  other code. The two real bridges declare 0.5.
- `check_structure.py` still counts `LIST OF` as its sign of a list.
- `LIST OF INTEGER` (56 corpus lines) is in no version of the grammar.

**The last three forms: ruled and applied, 2026-11-13 (DECISION-40, DECISION-41).**

The owner was shown three forms with a recommendation for each and answered:

1. Signed numbers (recommended: a number may carry the `+` the source prints). "Signed numbers
   should either be set or be transforms. This will likely be an adjudication process as part
   of the conversion. They will be left as strings mechanically, since we're not doing
   integers, etc."
2. A name with a value in a block, `"Convivial" +3` (recommended: read it as that name with
   that value). "Again, these are SET or TRANSFORMS".
3. Unnamed records in a list (recommended: legal). "List entries need not be named, just the
   list itself."

*Applied.*

- **DECISION-40** (rulings 1 and 2): the DSL gains no form. §8 has a new section, "A number
  printed with a sign": such a number, and a name paired with a number, is a `SET` or a
  `TRANSFORM`; which one is decided in conversion; until then it stays in a string as printed.
  No tool changes. The grammar still has no `+` on a number.
- **DECISION-41** (ruling 3): §8 says an item of a list may be a `DEF { … }` with no name and
  no hash. `ttrpg.peg` has `LIST_RECORD`, an item of a bracket list with a DEF's body. The
  validator already read the form and is not changed.
- `AUTHORING-GUIDELINES.md` and `README.md`: a line each.

*Proof,* run on 2026-11-13:

| Check | Result |
|---|---|
| `ttrpg_validator.py tests/records-good` | 0 errors, 0 warnings |
| `check_grammar.py tests/records-good` | accepted; the grammar as it was before refuses it |
| `tests/grammar-bad/16-unnamed-def-outside-a-list.ttrpg` | refused, with `03-def-without-name` |
| `check_grammar.py tests/*good* tests/decision6.ttrpg tests/ports-origin modules/0.6` | 52 of 52 accepted |
| `check_grammar.py tests/grammar-bad --expect-refused` | 16 of 16 refused |
| the two new §8 examples, with `^"Initiative" "+5"`, run as a file | validator 0 errors, 0 warnings; grammar accepted |
| the grammar before DECISION-41 against the grammar after, 22 corpus directories | no file that was accepted is refused. 351 more are accepted (pendragon6e 182, pendragon5e 99, teeth 36, aegean 19, marvelmultiverse 9, tor2e 4, coyotecrow 1, troika 1): 5,511 of 7,055, from 5,160 |

*Not done.*

- No corpus is changed. Deciding each signed number and each name with a number is F26.
- The fields of an unnamed entry are not checked against the type its list names. §20 already
  lists "the fields of a nested or unnamed DEF" as not checked.
- A named DEF written inside a list (`[ ^"Bite" DEF { … } ]`) is not in the grammar and was not
  ruled on.

**What C1 leaves in strings, by decision:** units, ranges, decimals, dice (the to-do under
A1 stands) and pairs of numbers. The owner adds no value types.

### C2. `EXTENDS` means both "is a kind of" and "is an instance of"

**Status:** closed 2026-11-13 by the owner. Committed and pushed on branch `0.6`. An entry may
extend an entry (DECISION-42). A type is told from an entry by what it holds, with no marker
(DECISION-43). No change to the namespace or to paths. One validator defect found on the way
is fixed. The corpora gain 12 warnings (F22).

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

**Since this was written:** DECISION-39 settles the `^"Level" INTEGER 20` point. A line with a
literal is a value (`^"Level" 20`) and a line with none is a declaration. DECISION-13 and
DECISION-27 settle the shared namespace: a reference resolves by hash, and a same-named DEF
under another hash is a second entity. DECISION-34 gave the validator a rule for telling a type
from an entry, which §5 does not state: a type is an `ACTOR` or `TEMPLATE` definition, a DEF
that another DEF extends, or a DEF that declares fields and gives no value.

**Evidence, counted 2026-11-13** over the 22 corpus directories with the validator's reader:
111,333 DEFs and 72,974 `EXTENDS` lines. No DEF extends two things. Of the top-level DEFs that
extend, 37,940 are one step from the top of their chain, 4,951 two and 378 three.

| What an `EXTENDS` line joins | Lines |
|---|---|
| an entry to a type that declares fields | 62,126 |
| an entry to a DEF that declares nothing and gives no value (draw-steel `^"Monster Ability"`, pendragon5e `^"Section"`, l5r5e `^"NPC"`) | 6,472, on 84 parents |
| an entry to a type that carries `ACTOR` or `TEMPLATE` | 3,098 |
| an entry to a DEF that gives values (dnd5.5e `^"Spell"` and `^"Monster"`, arm5e `^"Clumsy Magic"`) | 1,178 |
| a type to a type (l5r5e `^"Distinction"` to `^"Advantage"`) | 100 |

| Role, by the validator's rule | DEFs |
|---|---|
| an entry: it extends something and nothing extends it | 71,652 (29,705 of them nested) |
| a type by its `ACTOR` or `TEMPLATE` marker | 1,098 |
| a type because something extends it | 826 |
| a type because it declares fields | 207 |
| it extends something, is extended, and only declares: a subtype | 60 |
| it extends something, is extended, and gives values | 200 (arm5e 86, armdef 86, l5r5e 22, dnd5.5e 5, invisiblesun 1) |
| it is extended, extends nothing, and gives values | 11 |
| no `EXTENDS` either way | 37,279 (29,515 nested) |

1,304 DEFs act as a type and carry no marker (armdef 265, arm5e 246, pendragon6e 109, teeth 77,
aegean 76, l5r5e 71).

*What the rule cannot tell.*

- **An entry that another entry extends.** arm5e's `^"Clumsy Magic"` is a Flaw with values, and
  Rival Magic's Amazon flaw extends it. The rule counts it a type because something extends
  it, so the `REQUIRED` properties of `^"Flaw"` are not checked on it.
- **A type that gives a value.** dnd5.5e's `^"Spell"` and `^"Monster"` declare fields and give
  some. They are types only because entries extend them.
- **A type that declares nothing.** draw-steel's `^"Monster Ability"` is a type only because
  2,282 entries extend it. With none it would be a thing of no type.
- 50 names are carried by a type and by an entry of some other type, under different hashes.
  §5d keeps them apart.

*A defect found and fixed.* The validator read a type keyword on the line AFTER a
name as that name's type. `EXTENDS ^"Complication"` followed by a line `TEXT "…"` became a
property named Complication with no value, and the DEF was counted a type.

| Check | Result |
|---|---|
| probe: two entries lack a `REQUIRED` property; one has `TEXT` after its `EXTENDS` line | before: 1 reported. After: 2 |
| the validator as committed at B5, on the probe | 1 reported: the defect dates from B4 |
| every fixture set and both grammar gates | unchanged |
| old validator against new, 22 corpus directories | identical for all 22; 39 errors and 20,064 warnings both times |

490 draw-steel entries were read as types. None of them lacks a `REQUIRED` property, so no
corpus result changes and B4's counts stand.

*Proposed 2026-11-13,* and the owner's answers:

1. Mark a type with a word before its name, as `ACTOR` and `TEMPLATE` already do for
   characters. Owner: "why do we need a "TYPE" or "KIND" at all?" Measured below, and the
   proposal was withdrawn. Asked "Drop the marker, and write into §5 that a type is a
   definition that declares a field?", he answered "Yes, no marker".
2. An entry may extend an entry: a variant that starts from the parent's values. Owner: "yes."
3. No second namespace and no path syntax. Owner: "no change".

**Ruling 2, applied as DECISION-42.** §6 says an entry may extend an entry and
that being extended does not make a definition a type. §8's account of who owes a `REQUIRED`
property drops "a DEF that another DEF extends" from its list of types. The validator drops
the same test.

| Check | Result |
|---|---|
| `tests/required-good`, with a variant that takes its clan from the entry it extends | 0 errors, 0 warnings |
| `tests/required-bad`, with an entry that lacks a clan and has a variant | 4 errors, 1 warning; the validator before the ruling reports 3 and misses that entry |
| every other fixture set and both grammar gates | unchanged |
| validator before the ruling against after, 22 corpus directories | 17 identical. 12 new warnings, none gone, 39 errors both times |

The 12, all DEFs that extend a type, lack what it requires, and have something extending them:

| Corpus | DEF | What it is |
|---|---|---|
| vtm5e | `^"Ritual"`, `^"Ceremony"`, `^"Formula"` under `^"Discipline Power"` | subtypes that declare nothing |
| teeth | `^"Mutation"`, `^"Magic Device"`, `^"Hardship"`, `^"Complication"` under `^"Roll Table Entry"` | subtypes that declare nothing |
| arm5e, armdef | `^"Child Virtue"` under `^"Virtue"`, `^"Child Flaw"` under `^"Flaw"` (2 each) | subtypes that declare nothing |
| l5r5e | `^"Treasure Hunter"` under `^"School"`, no `^"Clan"` | an entry; a 2020 errata entry extends it |

**Why a marker might be needed: measured.** With ruling 2 applied, the validator calls a DEF a
type when it carries `ACTOR` or `TEMPLATE` or declares a field and gives no value. Since
DECISION-39 a declaration and a value are written differently, so the file shows which a DEF
is. Over 111,333 DEFs that rule misplaces 11: the subtypes above, which add no field of
their own and so look like entries. Each takes an element-level `FIAT` or one declared field.
A marker would settle those 11 and would be written on 1,304 DEFs to do it. UNVERIFIED:
whether any consumer needs to list a system's types.

**Ruling 1, applied as DECISION-43.** §5's "Definitions vs. Instances" is
rewritten: a DEF is a type or an entry, and what it holds shows which; no word marks a type;
`EXTENDS` is written the same for a subtype, an entry and a variant. §8 points to it. The
validator's rule is the one §5 now states, and its code is not changed by this ruling.

*The exact rule.* The question put to the owner said "a definition that declares a field".
The rule that was measured, and that §5 states, is narrower: a type declares fields and gives
no value of its own, or marks a field `REQUIRED`, or carries `ACTOR` or `TEMPLATE`. The
difference is 282 corpus DEFs that extend something and hold one declaration-shaped line
among their values (l5r5e 126, teeth 88, root 68): teeth's families write a value as
`^"Group" ENUM ["Wealthy Estates"]`. They are entries. Read by the looser wording they would
count as types and go unchecked.

| Check | Result |
|---|---|
| `tests/required-good`: a subtype that marks a field `REQUIRED` and gives a value owes nothing | 0 errors, 0 warnings |
| `tests/required-bad`: a DEF that gives a value and declares a field with no `REQUIRED` is an entry, and its missing clan is reported | 5 errors, 1 warning |
| every other fixture set and both grammar gates | unchanged |
| the validator's code | the copy that ran on the 22 corpora for DECISION-42; this ruling changes text only |

*Not done.*

- The 11 subtypes and l5r5e's `^"Treasure Hunter"` are warnings in their corpora (F22).
- Nothing checks that a DEF with an element-level `FIAT` "says what it is"; a `FIAT` waives
  the finding whatever its reason reads.
- A DEF that only gives a `REF` or a `ROLL` has no literal value, and the validator reads it as
  declaring. No corpus uses either form yet.

### C3. Most references in instance data are outside §5d and ungated

**Status:** closed 2026-11-13 by the owner. Committed and pushed on branch `0.6`. A hash and
name pair is a reference wherever it stands, and so is a name that is an item of a list; the
validator checks both. A name with no hash elsewhere in a system block is the system's own
(DECISION-44). The corpora gain 452 warnings (F27).

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

**Since this was written,** §5d's list has grown (A1 to A4, C1): `CHOOSE` options, `REF`, `SET`
and `TRANSFORM`, `SITUATIONAL`, `ROLL`, table axes and coordinates, embedded references, and
the references between narrative blocks, which are now the hash and name pair.

**What each tool checks today,** from a probe with one undefined name at each place
(2026-11-13):

| Place | Checked by |
|---|---|
| `APPLIES TO [ … ]`, a `CHOOSE` option, a bound reference and its arguments, `PARAMETERS … OF` | the validator |
| a `HOOK`'s `THEN`, an `OPTIONAL`'s `SCOPE`, a guidance `CONCERNS` | `check_constructs.py` |
| a name and a hashed reference on a line (`^"Nature" #hash ^"Extrovert"`) | `check_references.py` |
| a codex's `IS`, its predicates and its relationship objects | the validator |
| a member of a property's list: `^"Skills" [ ^"A" ]`, `LIST OF ^"Type" [ ^"A" ]` | nothing |
| a caret after a system keyword (`KATA ^"Name"`), alone on a line in a system block, or in a keyed block (`RANK 1 { ^"Name" }`) | nothing |
| a hash that is no anchor, or a hash whose anchor has another name, in any of the places in the two rows above | nothing |

§5d's list does not name the first, second and fourth rows, though the tools check them.

**Evidence, counted 2026-11-13:** 730,196 carets in the 22 corpus directories. 560,841 are the
name of a DEF or of a property. 10,290 stand where no tool checks them:

| Place | Carets | With a hash that resolves | With a hash that does not | No hash: one such name | No hash: several | No hash: no such name |
|---|---|---|---|---|---|---|
| a member of a property's list | 6,191 (armdef 3,139, arm5e 2,865, root 161) | 5,845 | 0 | 310 | 30 | 6 |
| a member of a `LIST OF ^"Type"` list | 1,850 (teeth 1,346, invisiblesun 303, curseborne 201) | 1,634 | 15 | 201 | 0 | 0 |
| the value after a name, no hash (`^"Nature" ^"Extrovert"`) | 965 (teeth 395, daggerheart 326, curseborne 164) | | | 588 | 72 | 305 |
| alone on its line in a system block | 778 (arm5e 388, armdef 238, l5r5e 151) | 0 | 0 | 550 | 50 | 178 |
| after a system keyword | 506 (draw-steel 289, l5r5e 191) | 12 | 0 | 126 | 80 | 288 |

- **The 15 broken hashes are all in teeth.** `teeth-0.5-worldbook-gatlock.ttrpg:433` lists
  `#txZPXb7KhtPS1Zm0QeROZYw ^"Dogmaker and Vulpids"` in a `LIST OF ^"Creature"`. No DEF has that
  hash or that name. 12 name no anchor, and 3 name an anchor that has another name.
- **A hashless caret in a list is a reference:** 541 of 547 name something. The 6 that do not
  are root's (`^"Blinside"`, `^"Pick pocket"`).
- **A hashless caret in a system block is not always one.** draw-steel's
  `SPEND ^"Special" "The target must be grabbed…"` is a label and its text. curseborne's
  `RULE ^"Starting Entanglement" ADDS_TO PARENT {` names a rule. teeth's
  `^"Attribute" ^"Attribute"` declares a property and its type. arm5e's
  `VIRTUES { ^"Second Sight" }` and l5r5e's `KATA ^"…"` are references. Of the 2,249 carets in
  these three places, 1,264 name one thing, 214 several and 771 nothing.

*Proposed 2026-11-13.* The owner was asked "Take all four C3 parts as recommended?" and
answered "Yes, all four".

1. A `#hash ^"Name"` pair is a reference wherever it stands, unless it declares, and §5d's
   rule 1 is checked on it.
2. A caret that is a member of a list is a reference, with or without a hash.
3. Elsewhere in a system block a caret with no hash is the system's own name and is not
   checked. Its hash makes it a reference.
4. §5d's list names the places the tools already check.

**Applied as DECISION-44.**

- **Spec:** §0 item 31; DECISION-44; §5d's list gains the bound reference, `PARAMETERS … OF`,
  a hook's `THEN`, `SCOPE`, `SELECT` and the codex; §5d has a new part, "References that no
  keyword marks", with the three rules.
- **`ttrpg_validator.py`:** reads each member of a property's list and each stray hash and
  name pair, and applies §5d to it. `check_references.py` is not changed.
- **Fixtures:** `tests/sites-good`, `tests/sites-bad`.

| Check | Result |
|---|---|
| `ttrpg_validator.py tests/sites-good` | 0 errors, 0 warnings |
| `ttrpg_validator.py tests/sites-bad` | 7 errors, 2 warnings: eight planted faults and one in a 0.5 file. The validator before reports nothing |
| the probe above, run again | the two list rows and the broken hashes are now reported |
| every other fixture set and both grammar gates | unchanged. `tests/decision6.ttrpg` listed an `ALIAS` with no hash and drew a warning until the rule left aliases out |
| validator before against after, 22 corpus directories | 17 identical. 452 new warnings, none gone; 39 errors both times; 20,528 warnings |

The 452:

| Finding | Count | Where |
|---|---|---|
| a list member with no hash that names one entity | 401 | curseborne 194, armdef 141, root 40, daggerheart 26 |
| a list member with no hash whose name several entities carry | 28 | armdef (`^"Covenfolk"`, `^"Heartbeast"`, `^"Faerie Magic"`) |
| a list member whose hash is no anchor | 12 | teeth |
| a list member whose hash is another name's anchor | 3 | teeth |
| a list member with no hash that names nothing | 6 | root (`^"Blinside"`, `^"Pick pocket"`, `^"Sleight of hand"`, `^"Honor"`, `^"Workshop"`, `^"Plots & Schemes"`) |
| a hash and name pair whose hash is no anchor | 2 | root: `^"Clement "Clem" Glenn"` and `^"Bee "Baby" Glenn"` in `sundew-bend.frame` |

The last two are not broken references. Each is a DEF whose name holds an unescaped quote, so
the reader stops at `^"Clement "` and never sees a DEF. Neither definition was being read at
all. DECISION-25 gives the form: `^"Clement \"Clem\" Glenn"`.

The census had estimated 511 hashless members. The validator finds 401: it leaves out a
member that is an `ALIAS` and one under a `FIAT`.

*Not done.*

- No corpus is changed (F27).
- `check_references.py` does not count these places among its reference sites, so its site
  and hashless totals are unchanged. The validator applies the three §5d rules to them.
- A hashless name in a system block that is a reference stays unresolved until it carries
  its hash: 1,264 of them name one entity today (arm5e's `VIRTUES { ^"Second Sight" }`,
  l5r5e's `KATA ^"Open-Hand Style"`).
- A member of a list that sits inside a `REFERENCES` block, or of a keyword list the grammar
  does not know, is not read.

### C4. Provenance has no construct

**Status:** closed 2026-11-13 by the owner. Committed and pushed on branch `0.6`. No construct
is added: the page is the property `^"Page"`, the book gets no field, and a page in a comment
is a note that no tool reads (DECISION-45). The corpus work is F28.

§4: comments are for "page references, source attributions", and comments must not carry data a
tool needs. §5c: strip page citations from `DESCRIPTION`. A page number is data to any tool that
cites, verifies or shows source beside structure. The corpora have each found a place for it: vtm5e
in comments (`# source: page 244`; about 8,380 comment lines carry a page), arm5e in an invented
`^"Page"` property (6,912 uses), l5r5e in both. `REPRINT` says a consumer notes "this book among
its printings", and no header field names the book. `sources.json` does that job outside the spec.

**Evidence, counted 2026-11-13** over the 22 corpus directories (6,986 files, 135,466 DEFs).

*The page.*

| Where it is written | Count | Corpora |
|---|---|---|
| a comment (`# source: chapter opening (page 243)`) | 40,672 of 59,579 comment lines | vtm5e 12,202, invisiblesun 4,704, pendragon6e 4,410, tor2e 3,146, callofcthulhu7e 2,605, and 13 more |
| `^"Page"` | 23,932, a number in 23,779 | invisiblesun 7,734, arm5e 6,912, armdef 6,810, root 1,655, pendragon5e 420 |
| `^"Pages"` | 1,916, a number or a range in a string | pendragon6e 827, pendragon5e 764, coyotecrow 176, marvelmultiverse 149 |
| `^"Source Page"` | 42 | l5r5e |

*The book.*

| Where it is written | Count | Corpora |
|---|---|---|
| `^"Source"` on each entity (`"Core Rules"`, `"Rival Magic"`) | 22,230 | armdef 11,372, arm5e 10,858 |
| `^"Book"` on each entity | 9,389 | invisiblesun 7,734, root 1,655 |
| the file's `NAME` (`"The One Ring 2e - Chapter 3: Adventurers"`) | every file | free text: book and part together |
| `SOURCE "…"` as a line of an `.arc` | 15 | l5r5e 14, armdef 1 |
| `sources.json` beside the corpus | each repo | the book's title, its PDF and its files; outside the spec |

`^"Source"` and `^"Book"` also name things in play in a few places (draw-steel's 222
`^"Source"`, arm5e's 28 `^"Book"` for books a covenant owns); those are not counted above.

*Who reads it.* Five consumer repos were searched. `titterpig-doublecheck/scripts/errata_gen.py`
and the dashboard's l5r5e errata overlay read `^"Source Page"`. mastra's arm5e renderers write
`^"Page"`. The doublecheck's invention check adds a DEF's comments to the text it compares.
No tool was found that takes a page number out of a comment. UNVERIFIED beyond that search.

*Proposed 2026-11-13.* The owner was asked "Take the three C4 parts as recommended?" and
answered "Yes, all three".

1. The page is the property `^"Page"`: a number, or what the source prints as text
   (`"139-160"`), with no new construct.
2. No field for the book. One source per file is the corpora's rule; the file's `NAME` and
   the repo's `sources.json` say which.
3. §4 keeps its rule. A page in a comment is a note that no tool reads.

**Applied as DECISION-45.**

- **Spec:** §0 item 32; DECISION-45; §4 no longer lists page references and source
  attributions as what comments are for, and points to the property; §8 has a new part, "The
  page".
- **`AUTHORING-GUIDELINES.md`, `README.md`:** a line each.
- **No tool changes.** The grammar and the validator already read the form.

| Check | Result |
|---|---|
| `ttrpg_validator.py tests/page-good`: `^"Page"` as a number and as text, on a DEF, in `PROPERTIES`, on a nested entry and on a `SCENE` | 0 errors, 0 warnings |
| `check_grammar.py tests/page-good` | 2 of 2 accepted |
| `check_references.py` and `check_constructs.py` on the same set | 0 errors |
| every other fixture set and both grammar gates | unchanged |

*Not done.*

- No corpus is changed (F28).
- Nothing checks that a page is written as `^"Page"` and not under another name, or that
  its value is a page.
- The spec does not state that a file holds one source. That rule is the corpora's.

### C5. In heavy use and not in the spec

**Status:** closed 2026-11-13 by the owner. Committed and pushed on branch `0.6`. Its seven
parts were ruled one at a time: tables need nothing more; the escapes of a string
(DECISION-46); what verbatim allows (DECISION-47); longer text as one string (DECISION-48);
where order matters (DECISION-49); hashes stable within a major version (DECISION-50);
`EMPHASIS` in a guidance `ENTRY`, and `BASE` still reserved (DECISION-51). A validator crash
on bridge files, in the tree since B2, was found and fixed. The corpus work is F29 and F30.

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

**Since this was written:** `TABLE` has a form (DECISION-21, §5e), with `MIN n` for an
open-ended key. F19 sent four forms here; three are ruled (DECISION-39, 40, 41), and two
remain: an `EMPHASIS` block inside a guidance `ENTRY`, and `BASE n` as a system's field.

**Evidence, counted 2026-11-13** over the 22 corpus directories.

| What | Count | Where |
|---|---|---|
| single-quoted strings | 1,417,638 | |
| escapes used in them | `\n` 231,956; `\"` 8,332; `\\` 7; `\uXXXX` 3; no other | the grammar also takes `\t`, `\r` and `\/` |
| a paragraph break written `\n\n` in one string | 33,488 strings | armdef 6,722, vtm5e 6,614, arm5e 6,436 |
| a single `\n` in a string | 956 strings | callofcthulhu7e 534, pendragon6e 158 |
| a raw line break inside a single-quoted string | 94 strings | arm5e 46, armdef 46, draw-steel 2 |
| triple-quoted strings | 1,897 | draw-steel 1,889 |
| of those, every line indented | 580 | the indent is part of the text unless a rule strips it |
| of those, a line at column 0 | 1,283 | draw-steel writes the text at the margin to keep indent out |
| runs of two or more lines that are each one bare string | 1,833 | pendragon6e 780, l5r5e 413, pendragon5e 157 |
| strings with a curly apostrophe; a curly double quote | 47,650; 11,531 | |
| strings with a soft hyphen; a no-break space; an fi ligature; an HTML entity | 15; 33; 2; 0 | arm5e, armdef, pendragon6e |
| `TABLE {` blocks | 2,307, with 12,394 `ROW` lines and 958 `COLUMNS` or `HEADERS` lines | no corpus writes `AXIS`; F9 has the migration |
| lines keyed by one number; by `lo-hi` | 147; 17 | l5r5e |
| `BASE n` as a system's field | 749 lines | arm5e 372, armdef 377 |

- **The verbatim rule's "standard normalisation" is used by no tool.** `check_references.py`
  tests a surface form against its prose as an exact substring. What a converter may change
  between the page and the string is written down nowhere.
- **A hash can change on a rebuild.** tor2e's generator mints each hash as the SHA-1 of the
  entity's path (`scripts/dsl/common.py`), so the hash is stable while the path is, and a
  renamed or moved entity gets a new one.

*Proposed 2026-11-13,* and ruled one part at a time, below. Parts 4, 6 and 7 were ruled otherwise than first proposed.

1. Tables: nothing more to rule.
2. §10 lists the escapes: `\"`, `\\`, `\n`, `\t`, `\r`, `\/`, `\uXXXX`.
3. §5c says what verbatim allows: the name rule of DECISION-33 (Unicode NFC, white space,
   quote style), and the repair of layout (a word hyphenated at a line end, a soft hyphen, a
   ligature glyph, an HTML entity). Nothing else.
4. Text of several paragraphs is one string with `\n\n` between them. A single-quoted string
   does not run over a line break. A triple-quoted string loses the indent its lines share.
   Bare strings one after another are separate entries of their block.
5. Order: the language depends on the order of statements only for `NEXT`, for the items of a
   list and for a run of bare strings. A file keeps the source's order for display.
6. A hash stays with its entity once a corpus is published. The note that example IDs are
   regenerated goes.
7. `EMPHASIS` stays out of a guidance `ENTRY`, and `BASE` stays reserved. Both are corpus fixes.

The owner asked to take them one at a time.

**Part 1, tables: ruled 2026-11-13. Nothing more to rule.** Owner: "Agreed". An open-ended key
is `AT [ MIN 16 ]` (§5e). A d66 is a die a system defines, with 36 faces; it is not added to
the shared dice module. The corpora hold 14 rows keyed `"N+"` and 773 keyed by a range in a
string, all in the older `ROW` grids, and only troika uses d66 (F9). No file changes.

**Part 2, string escapes: ruled 2026-11-13 and applied as DECISION-46.** The
owner was asked "Part 2: list the grammar's seven escapes and make any other an error?" and
answered "Yes, seven".

- **Spec:** §0 item 33; DECISION-46; §10 has a new part, "Escapes", with the seven and what
  each stands for.
- **`ttrpg.peg`:** a backslash in a single-quoted string or a caret name must open one of the
  seven. It had been read as a plain character when it did not.
- **`ttrpg_validator.py`:** the same test, a warning below 0.6 and an error from 0.6.

| Check | Result |
|---|---|
| probe before the change: `"an unknown escape \q here"` | accepted by the grammar and by the validator |
| `ttrpg_validator.py tests/escapes-good`: each of the seven, a name with `\"`, a triple-quoted string with a backslash and a quote | 0 errors, 0 warnings; grammar accepted |
| `ttrpg_validator.py tests/escapes-bad` | 3 errors, 1 warning; the validator before reports nothing |
| `check_grammar.py tests/grammar-bad --expect-refused` | 17 of 17 refused, with the new `17-unknown-escape` |
| every other fixture set; the good sets in the grammar | unchanged; 56 of 56 accepted |
| validator before against after, 22 corpus directories | identical for all 22; 39 errors, 20,528 warnings |
| grammar before against after, 22 corpus directories | the same files accepted and refused: 5,511 of 7,055 |

No corpus has a backslash that opens no escape.

*Agent's calls, to confirm:* the finding takes no `FIAT`; a caret name follows the same rule
as a string; `\u` must be followed by four hexadecimal digits.

**Part 3, what verbatim allows: ruled 2026-11-13 and applied as DECISION-47.**
The owner was asked "Part 3: define "verbatim" in §5c with these five allowances and nothing
else?" and answered "Yes, those five".

1. Unicode form: composed (NFC).
2. White space: a run is one space; the page's line breaks are not kept; a paragraph break
   is; a no-break space is a space.
3. Quote style: curly and straight are the same.
4. Page layout: a word hyphenated at a line end is rejoined; a soft hyphen is dropped; a
   ligature glyph is written as its letters.
5. HTML entities from an HTML source are decoded.

Wording, punctuation, the kind of a dash, capitals and emphasis are content. The allowance to
strip a cross-rulebook page citation is unchanged.

- **Spec:** §0 item 34; DECISION-47; §5c's `DESCRIPTION` rule points to a new paragraph, "What
  verbatim allows", in place of "the standard whitespace/HTML-escape normalisation".
- **No tool changes, and no tool here checks the rule.** It needs the source. It is the
  standard for a converter and for the verification tools outside this repo.
- The agent told the owner it was unsure of dash kinds: his matching tools fold hyphens and
  dashes, which is a looser test than this rule. He took the list as written.

**Part 4, text of several paragraphs: ruled 2026-11-13 and applied as DECISION-48.** Four rules were proposed. The owner: "let's just use the Paragraphs method; we
should ultimately convert the other approaches over."

- **The one method:** text of several paragraphs is one string with `\n\n` between them.
- **The other approaches are older forms,** to be converted: a triple-quoted block, and a
  single-quoted string that runs over a line break. Each is a warning in a file below 0.6
  and an error from 0.6. The grammar still reads both.
- **Strings in a row** are separate entries of their block. That is how every corpus uses
  them, so nothing is reported.

*Applied.* The spec: §0 item 35; DECISION-48; §10 has one part, "Text of several paragraphs",
where it had three; the triple-quoted examples in §5, §21 and the guidelines are rewritten.
The validator reports the two older forms. Fixtures: `tests/paragraphs-good`,
`tests/paragraphs-bad`; three 0.6 fixtures and `tests/good.bridge` no longer use a
triple-quoted block.

| Check | Result |
|---|---|
| `ttrpg_validator.py tests/paragraphs-good` | 0 errors, 0 warnings; grammar accepted |
| `ttrpg_validator.py tests/paragraphs-bad` | 2 errors, 2 warnings; the validator before reports nothing |
| `embedded-good`, `embedded-bad`, `escapes-good`, rewritten without triple quotes | the same counts as before: 0 and 0, 5 errors, 0 and 0 |
| every other fixture set; both grammar gates | unchanged; 57 of 57 accepted, 17 of 17 refused |
| validator before against after, 22 corpus directories | 14 identical. 1,990 new warnings, none gone; 39 errors both times; 22,518 warnings |

The 1,990: 1,897 triple-quoted blocks (draw-steel 1,889, callofcthulhu7e 3, daggerheart 2,
dnd5.5e 1, dnd5e 1, root 1) and 93 strings over a raw line break (arm5e 46, armdef 46,
draw-steel 1). The two bridges in `bridges/0.5` gain 11 and 85 warnings for their
triple-quoted blocks.

*A crash found and fixed.* `ttrpg_validator.py` raised `ValueError` on any `.bridge` with an
`ALIASES` block: `tests/good.bridge`, and `bridges/0.5/dnd5e-to-dnd5.5e-0.5-srd-conversion.bridge`.
B2's alias-cycle check read a bridge's aliases, which have another shape. The crash was in
every commit from B2 (`4af9e46`) to C4 (`91a48d8`). It went unseen because the agent's
fixture run listed its sets by hand and left out the four single-file bridge and codex
fixtures. Every "fixtures unchanged" in B2 to C4 is true of the sets that were run and says
nothing of those four.

| Check | Result |
|---|---|
| B1's validator (`ecff698`) on `tests/good.bridge` as it was then | 0 errors, 0 warnings |
| B2's validator (`4af9e46`) on the same file, and every later commit's | `ValueError` |
| after the fix: `good.bridge`, `bad.bridge`, `good.codex`, `bad.codex` | 0 and 0; 22 errors; 0 and 0; 5 errors and 5 warnings. `bad.bridge` and both codex files match B1's validator |
| after the fix: the two bridges in `bridges/0.5`, with no corpus given | 1 and 2 errors, as under B1's validator, and the 11 and 85 new warnings |

The fixture run now includes those four files and both real bridges.

*Agent's calls, to confirm:* a triple-quoted block is an error from 0.6, as the agent read
"the other approaches"; neither finding takes a `FIAT`; the grammar keeps reading both forms.

*Not done.* No corpus is converted (F29). The dedent rule proposed for triple-quoted blocks
was not adopted and is not needed: the form goes.

**Part 5, order: ruled 2026-11-13 and applied as DECISION-49.** The owner was
asked "Part 5: state that order matters only in those three places?" and answered "Yes, as
stated".

- The order of statements in a block carries meaning in a `NEXT` chain, in the items of a
  list and in bare strings in a row, and nowhere else.
- A file keeps its source's order and a consumer shows definitions in that order. No rule or
  reference depends on it. Order between files is load order (§13).
- A heading has no form of its own: it is the name of the definition made for its section.

*Applied.* The spec: §0 item 36; DECISION-49; §5 has a new part, "Order"; §8's sentence on
`NEXT` points to it. Text only. No tool changes, and none checks it: there is nothing to check.

UNVERIFIED: whether any consumer relies on the order of definitions for more than display.

**Part 6, hash stability: ruled 2026-11-13 and applied as DECISION-50.** The
agent proposed that a hash stay with its entity once a corpus is published. The owner:
"Hashes are considered stable within same major versions (ie, all 0.5 instances should be
hash-stable)."

*Evidence.* tor2e's generator mints a hash as the SHA-1 of the entity's path, so a renamed or
moved entity gets a new one. For ten corpora, each DEF's hash at an earlier commit of the same
directory was set against today's, for names that stand once at both ends:

| Corpus | From | Names at both ends | Hash changed |
|---|---|---|---|
| vtm5e | the first commit of `0.5/` (2026-09-13) | 1,026 | 1,025 |
| vtm5e | mid-history (2026-09-23) | 5,710 | 104 |
| root | the first commit (2026-09-20) | 1,751 | 29 |
| arm5e | the first commit (2026-07-27) | 3,017 | 11 |
| invisiblesun | mid-history (2026-09-20) | 9,036 | 6 |
| tor2e; l5r5e | the first commit | 505; 1,036 | 1; 1 |
| dnd5.5e, draw-steel, daggerheart, teeth | the first commit | 1,169 to 1,951 | 0 |

*Applied.* The spec: §0 item 37; DECISION-50; a bullet in §5's hash rules; a clause in §19;
the note on example IDs loses "and are regenerated during re-conversion". Text only.

*Agent's calls, to confirm:* a major version is read as the number of the content-version
directory (`0.5`); the rule covers a rename, a move to another file and a rebuild.

*Not done.* No tool checks the rule; it takes two states of a corpus (F30).

**Part 7, two leftover forms: ruled 2026-11-13 and applied as DECISION-51.** The
agent first recommended keeping both forms illegal, then changed the first on looking at it.
The owner was asked "Part 7: allow EMPHASIS in a guidance ENTRY, and keep BASE reserved?" and
answered "Yes, both".

- **`EMPHASIS` in a guidance `ENTRY` is legal.** 194 blocks in 52 files (pendragon6e 45 files,
  marvelmultiverse 7). An entry's `TEXT` is verbatim, and emphasis is recorded beside verbatim
  text.
- **`BASE` stays reserved.** arm5e and armdef write `BASE n` 749 times in 36 files, all in
  `LEVEL_CALCULATION` blocks. The rename goes with F5, which rebuilds those blocks.

*Applied.* The spec: §0 item 38; DECISION-51; §22's entry gains the block and a rule that each
span is in the entry's `TEXT`. `ttrpg.peg`: an entry's fields include `EMPHASIS_BLOCK`. No
validator change; `check_references.py` already read the block.

| Check | Result |
|---|---|
| `tests/guidance-good` in the validator, the grammar, `check_references.py`, `check_constructs.py` | 0 errors and 0 warnings; accepted; 0 errors; 0 errors. The grammar before refuses it |
| `tests/guidance-bad` in `check_references.py` | 2 errors: a span in no text, and a span that is in the DEF's `DESCRIPTION` and not in its entry's `TEXT` |
| every other fixture set, both grammar gates | unchanged; 58 of 58 accepted, 17 of 17 refused |
| `check_references.py` on the two embedded-reference fixtures rewritten under part 4 | the same counts as the committed versions |
| grammar before against after, 22 corpus directories | nothing newly refused; 52 more accepted (pendragon6e 45, marvelmultiverse 7): 5,563 of 7,055 |

The fixture run now also runs `check_references.py` and `check_constructs.py` on every entry
of `tests/`.

*Agent's calls, to confirm:* `LABEL` is not added to an entry (no corpus writes one there);
the block is allowed in a bridge's guidance entry too, which is the same construct.

*Not done.* The synthesist's guidance reader does not read the block (the corpora's working
rules record that it misreads it). F5 gains the `BASE` rename.

### C6. Specified and unused

**Status:** closed 2026-11-14 by the owner. Committed and pushed on branch `0.6`. Its seven
parts were ruled one at a time: no "provisional" status; three forms removed (DECISION-52);
four forms marked as likely to be replaced (DECISION-53); two hook levels and `TRIGGER` marked
the same way (DECISION-54); the three `USES_` lines folded into `DEPENDS_ON` (DECISION-55); the
rule form `WHEN […] THEN` removed (DECISION-56); an alias as a second name of a hash
(DECISION-57). The corpus work is F31 to F34.

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

**Evidence, recounted 2026-11-14.** Two counts, by token, with comments and strings left out:
the 22 corpus directories (7,055 files), and seven repos outside them (202 files: six
third-party repos and expanse, which is still 0.4). The three bridge files were counted for
the bridge keywords. Every keyword of §15 and §18 was counted, so the list of what nothing
writes is taken from the spec's own lists.

The first table was wrong in three rows, and its scope left out the third-party repos.

| Construct | First table | The 22 directories | The seven other repos |
|---|---|---|---|
| `ALIAS ^"A" FOR ^"B"` | 0 | 4 (armdef) | 0 |
| `OVERRIDE` | 0 | 0 | 3 (l5r5e-3rdparty, three errata files) |
| `ADD … DEF` | 0 | 0 | 74 (l5r5e-3rdparty 72, dnd5e-3rdparty 2) |
| `REFERENCED BY` | 0 | 0 | 0 |
| `@n` occurrence index | 0 | 0 | 0 |
| `.selections` files | 0 | 0 | 0 |
| `HOOKS` | 3 | 3 (arm5e), each `FORMALITY TAGGED` | 0 |
| `OPTIONAL { }` | 15 | 16 in six corpora, 15 of them `DEFAULT off` | 1 |
| bound reference `^"X"(…)` | 2 | 109, in three armdef files | 0 |
| `PARAMETERS { }` | 176 | 263 (armdef 87, arm5e 86, vtm5e 80, callofcthulhu7e 9, l5r5e 1) | 10 |
| a rule `WHEN […] THEN` | 23 | 23 in seven corpora | 4 (expanse) |
| a rule with a label and text | 1,374 | 1,374 (l5r5e) | 141 (l5r5e-3rdparty) |
| a rule with a label alone | | 15 (armdef 14, arm5e 1) | 49 (l5r5e-3rdparty) |
| bare constraint (§9) | 110 | 105 (l5r5e 60, eight others 45) | 7 (expanse) |
| `MODIFY` | 392 | 603 (arm5e 316, armdef 211, l5r5e 69, vtm5e 7) | 39 |

- **Most `MODIFY` blocks add guidance.** 567 of the 603 hold a `GUIDANCE` block and nothing
  else. 33 hold a `SET` and 38 a `PROPERTIES` block.
- **l5r5e and vtm5e write `ALIAS "name"` inside a DEF,** 9 times, for a second spelling of the
  entity's own name (`^"Ninjō" DEF { ALIAS "Ninjo" …`). §5b's `ALIAS` is a statement outside the
  DEF, and §15 reserves the word everywhere. No tool reports the 9 lines.
- **Every bridge keyword is written** in at least one of the three bridges.

**What nothing writes.** These forms are older than 0.6, and no file in the 29 directories or
the three bridges writes them.

| Form | Fixture | What reads it |
|---|---|---|
| `ADD_TO`, `REMOVE_FROM` (§13) | two fixture files | the validator checks both; the synthesist parses them |
| `#hash MODIFY: label NOW REFERENCES …` (§13, "MODIFY in Rules") | none | nothing |
| `REFERENCED BY` (§5c) | one fixture, one sample | `check_references.py` checks it against the `REFERENCES` it mirrors |
| `"surface"@n` (§5c) | none | `check_references.py` reads past the number and does not use it |
| `MENTIONS` (§5c, the 0.4 name of `REFERENCES`) | none | read as `REFERENCES` |
| `SELECTIONS`, `SELECT` (§24) | the sample file | `check_constructs.py`; the synthesist does not |
| `FORMALITY PROSE`, `CONDITIONAL`, `FORMAL`; `TRIGGER` in a `HOOK` (§23) | the sample has `CONDITIONAL` | `check_constructs.py` checks the level is one of the four; nothing reads a `TRIGGER` |
| `USES_SETTING`, `USES_FRAME` (§16) | none | nothing |

- **One case in the corpora is what `@n` is for.** arm5e's *Realms of Power: Magic* lists the
  surface "Magical Meditation" twice in one `REFERENCES` block, with two hashes (mirrored in
  armdef). It is the only surface with two targets in 3,694 blocks.
- **`USES_EXTENSION` is written and read by nothing.** 17 lines (teeth 14, l5r5e 2,
  curseborne 1). Three of the 15 ids they name are declared by no file (`teeth-cotillion`,
  `teeth-hogmen`, `teeth-stranger`). DECISION-36 names `DEPENDS_ON` and the header `EXTENDS`
  as what a file depends on, and says nothing of a `USES_` line.
- **The 27 `WHEN […] THEN` rules are written by the converter, in its own words.** They sit in
  eight core base files (`WHEN [^"Character" makes an attack roll] THEN roll 1d20 + ability
  modifier + …`). No tool reads the condition or the action. l5r5e's first one,
  `WHEN [^"Entity" CREATED] THEN REQUIRE ^"Name"`, is what `REQUIRED` now says (DECISION-34).
- **New in 0.6 and not yet written:** `TRANSFORM`, `SITUATIONAL`, `REF OF`, `AXIS`, `AT`,
  `WEIGHT`, `NEXT`, `WITH`, `INDISTINCT`, `LABEL`, `EMPHASIS BOLD` and `ITALIC`, and `ORIGIN`
  in a port. The corpora declare 0.5, and the follow-ups hold their migrations (F4, F6, F7,
  F9, F14, F24, F26). l5r5e already writes `CHOOSE` (308), `DISTINCT` (4), `FACES` (2) and
  `ROLL` (7).

*Proposed 2026-11-14,* and ruled one part at a time, below.

1. The spec gains no "provisional" status: each form nothing writes is either removed or kept.
2. Remove four: the rule form `MODIFY: … NOW REFERENCES`; `REFERENCED BY`; `MENTIONS`;
   `USES_SETTING` and `USES_FRAME`. Each is an older form: a warning below 0.6 and an error
   from 0.6.
3. Keep four as they are: `ADD_TO` and `REMOVE_FROM`; `@n`; `.selections`; `OVERRIDE` and
   `ADD … DEF` (written in the third-party repos).
4. Hooks keep two levels, `PROSE` and `TAGGED`. `CONDITIONAL`, `FORMAL` and the `TRIGGER`
   overlay go: the spec gives a `TRIGGER` no shape, so no tool can check one.
5. `USES_EXTENSION` is a dependency like `DEPENDS_ON`, and the validator checks that it names
   a loaded file.
6. The rule form `WHEN […] THEN` goes. A rule is a label with the book's text, or a DEF with
   a `DESCRIPTION`.
7. `ALIAS "name"` inside a DEF is reported: `ALIAS` is the §5b statement.

**Part 1, ruled 2026-11-14: no "provisional" status.** Owner: "I agree to no provisional
status". The spec gains no mark for a form nothing writes, and candidate improvement 7 is not
taken. Each such form is ruled on its own in parts 2 to 4. Nothing in the spec, the grammar or
a tool changes for this part.

He asked for two things to be taken up once the C findings are done. They are listed under
*To revisit once C1 to C9 are closed*, after C9.

**Part 2, ruled 2026-11-14: three forms removed (DECISION-52).** Owner: "a. remove the form.
b. remove. c. remove the alias, and rewrite that half of §5c with REFERENCES."

Before he ruled, the agent took `USES_SETTING` and `USES_FRAME` out of this part and put them
with `USES_EXTENSION` in part 5, so that one rule covers the three lines. He ruled on the three
forms that were left.

- **a. The rule form `#hash MODIFY: label NOW REFERENCES …`.** §13's "MODIFY in Rules" is now
  "Changing a rule": a `MODIFY` changes a rule by writing it whole, under its hash, in a `RULES`
  block, and the entry replaces the rule. The example is l5r5e's 2020 erratum to the Rhinoceros
  rule `rhino_charge`, which is written that way.
- **b. `REFERENCED BY`.** §5c no longer defines it. What refers to an entity is read from the
  `REFERENCES` blocks that name it.
- **c. `MENTIONS`.** The alias is gone, and the half of §5c that still taught the block under
  its 0.4 name is written with `REFERENCES`.

Each of the three is a warning in a file that declares a `SPEC_VERSION` below 0.6, or none, and
an error in one that declares 0.6 or later.

*Applied.* Spec: §0 item 39, DECISION-52, §5c, §5d's list of sites, §13, §15, and a note on the
0.5 record and on DECISION-11. Validator: one finding for each form. `check_references.py`
reads past a `REFERENCED BY` block and no longer checks it against the `REFERENCES` it
mirrored; the bookkeeping for that check is removed. The grammar changes in its comments
only: it still reads `MENTIONS` and `REFERENCED BY` for a file below 0.6, and it has refused
the `MODIFY:` rule form since B1, so the spec's own §13 example never passed its grammar. Guidelines: two lines.
README: the tool table and the fixture list. `tests/embedded-good` and the 0.5 sample each lose
their `REFERENCED BY` block. New: `tests/removed-good` and `tests/removed-bad`.

| Check | Result |
|---|---|
| `tests/removed-good` in the validator, `check_references.py`, the grammar | 0 errors and 0 warnings; 0 errors; accepted |
| `tests/removed-bad` in the validator | 3 errors (the file that declares 0.6) and 3 warnings (the one that declares 0.5) |
| `tests/removed-bad` in the validator before the change | 0 errors, 0 warnings |
| the §13 example, with a DEF for it to modify, run as a file | validator 0 errors, 0 warnings; grammar accepted |
| the fixture run against the run at the C5 commit | the same, but for the two new sets, `embedded-good`'s `referenced-by` count (1, now 0) and the grammar's count |
| both grammar gates | 59 of 59 good files accepted; 17 of 17 planted faults refused |
| `samples/` in the four tools | validator 0 errors, 0 warnings; `check_references.py` 0 errors; `check_constructs.py` 0 errors; grammar 3 of 3 accepted |
| validator, before against after, 22 corpus directories | identical output in all 22: 39 errors, 22,518 warnings |
| `check_references.py`, before against after, 22 corpus directories | identical output in all 22 |

*Agent's calls, to confirm.* (1) `MENTIONS`, `REFERENCED` and `BY` stay reserved words, as
`STRING` did. (2) §13 says what an entry under an existing rule's hash does. It says nothing of
an entry under a hash the target has no rule for; no corpus writes one in a `MODIFY`. (3) None
of the three findings takes a `FIAT`. (4) Five example strings in §5c ran over a raw line
break, which DECISION-48 made an older form. C5's sweep missed them. Each is now one line.

*Not done.* The validator does not check that a rule written in a `MODIFY` carries the hash of
a rule its target has. The synthesist still reads `REFERENCED BY` (F31).

**Part 3, ruled 2026-11-14: four forms marked as likely to be replaced (DECISION-53).** Owner:
"flag all four of these as likely to be replaced and make them WARN if present, but we won't do
the replacements just yet."

The agent had proposed to keep the four as they are. He marked them.

- **a. `ADD_TO` and `REMOVE_FROM`** (§13).
- **b. The `@n` occurrence index** (§5c).
- **c. The `.selections` file** (§24).
- **d. `OVERRIDE` and `ADD … DEF`** (§13).

Each reads as it did. The validator raises a warning wherever one is written, whatever
`SPEC_VERSION` the file declares. No replacement is ruled for any of them.

*Applied.* Spec: §0 item 40, DECISION-53, a mark at each form (§5c; the two headings and two
bullets of §13; the heading in §24; the `.selections` row of §2's table), §15 and §20.
Validator: one warning for each form. It finds a `.selections` file and reports it, and still
does not read one. The grammar, `check_references.py` and `check_constructs.py` are unchanged.
README: the fixture list. `tests/mods-good.ttrpg` and `tests/mods-bad.ttrpg` hold the four §13
forms, so each shows four more warnings, and their header notes say so. New: `tests/marked`.

| Check | Result |
|---|---|
| `tests/marked` in the validator | 0 errors, 7 warnings: two `@n`, `ADD_TO`, `REMOVE_FROM`, `OVERRIDE`, `ADD … DEF`, and the `.selections` file |
| `tests/marked` in the validator before the change | 0 errors, 0 warnings |
| `tests/marked` in `check_references.py`, `check_constructs.py`, the grammar | 0 errors; 0 errors; 2 of 2 accepted |
| the fixture run against the run after part 2 | the same, but for the new set and four more warnings on `good.ttrpg` with `mods-good.ttrpg` (0, now 4) and on `bad.ttrpg` with `mods-bad.ttrpg` (3, now 7) |
| both grammar gates | 59 of 59 good files accepted; 17 of 17 planted faults refused |
| `samples/` in the validator | 0 errors, 1 warning, for the `.selections` file; before the change, 0 and 0 |
| validator, before against after, 22 corpus directories | identical output in all 22: 39 errors, 22,518 warnings |
| validator, before against after, the seven other repos | five identical. l5r5e-3rdparty: 75 more warnings (72 `ADD … DEF`, 3 `OVERRIDE`), 125 to 200. dnd5e-3rdparty: 2 more (`ADD … DEF`), 277 to 279. No other line of output differs, and each count is the count of the form in that repo |

*Agent's calls, to confirm.* (1) The ruling is written as DECISION-53, in his words: "likely to
be replaced". Part 1 ruled out a status for every unused form; this marks four named ones.
(2) The warning is the same at every `SPEC_VERSION`, and no `FIAT` waives it. (3) The validator
reports a `.selections` file; `check_constructs.py`, which reads them, prints nothing new.
(4) The mark is on the statement `ADD … DEF`. `ADD` as a method of `TRANSFORM` (§8) is not
touched. (5) §24's `OPTIONAL` block is not marked: he named the four forms of part 3, and §24
is on his list for after C9.

*Not done.* No replacement is ruled. No corpus is changed: l5r5e-3rdparty and dnd5e-3rdparty
carry the new warnings until one is. The grammar accepts `OVERRIDE "name"`, with a string for
the caret, which the spec does not show; the validator does not report that spelling, and no
file in the 29 directories writes it. The synthesist is unchanged.

**Part 4, ruled 2026-11-14: two hook levels and `TRIGGER` marked as likely to be replaced
(DECISION-54).** Owner: "mark as likely to replace and warn."

The agent had proposed to remove `CONDITIONAL`, `FORMAL` and `TRIGGER`, and gave the part 3
treatment as the alternative. He took the alternative.

`FORMALITY CONDITIONAL`, `FORMALITY FORMAL` and a `TRIGGER` inside a `HOOK` each read as they
did. The validator raises a warning wherever one is written, whatever `SPEC_VERSION` the file
declares. `PROSE` and `TAGGED` are not marked. No replacement is ruled.

*Applied.* Spec: §0 item 41, DECISION-54, a bullet in §23, §15 and §20. Validator: one warning
for each of the three, read inside a `HOOK` only. The grammar, `check_references.py` and
`check_constructs.py` are unchanged. README: the fixture list. `tests/marked` gains four hooks,
one at each level, and a system's `TRIGGER` outside a hook.

| Check | Result |
|---|---|
| `tests/marked` in the validator | 0 errors, 10 warnings: the seven of part 3, and `FORMALITY CONDITIONAL`, `TRIGGER` in a hook, `FORMALITY FORMAL` |
| `tests/marked` in the validator before the change | 0 errors, 7 warnings |
| in that fixture, the `PROSE` hook, the `TAGGED` hook, and `TRIGGER` in a system's block outside a hook | no warning |
| `tests/marked` in `check_references.py`, `check_constructs.py`, the grammar | 0 errors; 0 errors, 4 hooks; 2 of 2 accepted |
| the fixture run against the run after part 3 | the same, but for `tests/marked` |
| both grammar gates | 59 of 59 good files accepted; 17 of 17 planted faults refused |
| `samples/` in the validator | 0 errors, 3 warnings: the `.selections` file, and the sample hook's `CONDITIONAL` and `TRIGGER`; before the change, 0 and 1 |
| validator, before against after, 22 corpus directories | identical output in all 22: 39 errors, 22,518 warnings |
| validator, before against after, the seven other repos | identical output in all seven |

*Agent's calls, to confirm.* (1) Written as DECISION-54, apart from DECISION-53. (2) The same
terms as part 3: a warning at every `SPEC_VERSION`, and no `FIAT`. (3) `TRIGGER` is marked
inside a `HOOK` only; outside one it is a system's keyword (§15). (4) §23's example, which is a
`CONDITIONAL` hook with a `TRIGGER`, stands as it was, and so does the sample that copies it.

*Not done.* No replacement is ruled. §23 still says every `TRIGGER` reference resolves, and no
tool reads a `TRIGGER`. Found while writing the fixture and not fixed: `check_constructs.py`
skips a `FORMALITY` line that ends in a comment, so `FORMALITY BOGUS  # note` passes it with 0
hooks counted; the grammar refuses that line. No corpus is changed, and the synthesist is
unchanged.

**Part 5, ruled 2026-11-14: the three `USES_` lines fold into `DEPENDS_ON` (DECISION-55).**
Owner: "Fold into DEPENDS_ON".

The agent had proposed to keep the three keywords and check them as dependencies, and gave the
fold as the alternative. He took the fold.

The count the proposal rested on, taken again over the 29 directories: `USES_EXTENSION` is
written 26 times, 17 in the 22 corpus directories (teeth 14, l5r5e 2, curseborne 1) and 9 in
third-party repos (dnd5e-3rdparty 4, troika-3rdparty 5). `USES_SETTING` and `USES_FRAME` are
written nowhere. Three of the 26, one in each TEETH one-shot, name an id no file declares:
`teeth-hogmen`, `teeth-stranger`, `teeth-cotillion`. Five, in troika-3rdparty, stand in
`.ttrpg` files, where §16 never defined the line.

A file names every file it needs with `DEPENDS_ON`: a container's BASE, and each EXTENSION,
SETTING or FRAME, one line for each. A `USES_` line is an older form: a warning in a file that
declares a `SPEC_VERSION` below 0.6, or none, and an error in one that declares 0.6 or later.

*Applied.* Spec: §0 item 42, DECISION-55, a paragraph in §3, and in §16 the three templates,
their field lists, two examples, *Cross-Container References*, the dependency table and rules 2
to 4; §18's keyword list. Validator: one finding for each `USES_` line; and a `DEPENDS_ON` may
now name a SETTING, a FRAME, an ARC or a CAMPAIGN, where before it had to name a BASE or an
EXTENSION and any other id was an error. README: the fixture list. A comment in
`tests/narrative-good/story.arc`. New: `tests/uses-good` and `tests/uses-bad`.

| Check | Result |
|---|---|
| `tests/uses-good` in the validator, the grammar | 0 errors, 0 warnings; 6 of 6 accepted |
| `tests/uses-good` in the validator before the change | 4 errors: each `DEPENDS_ON` that names the setting or the frame |
| `tests/uses-bad` in the validator | 4 errors and 3 warnings: three `USES_` lines in files that declare 0.6, three in files that declare 0.5, and one `DEPENDS_ON` that names no file |
| `tests/uses-bad` in the validator before the change | 2 errors, 0 warnings, and no `USES_` line reported |
| the fixture run against the run after part 4 | the same, but for the two new sets and the grammar's count |
| both grammar gates | 65 of 65 good files accepted; 17 of 17 planted faults refused |
| validator, before against after, 22 corpus directories | 19 identical. Three gain the `USES_` warnings and nothing else: teeth 14 (233 to 247), l5r5e 2 (198 to 200), curseborne 1 (231 to 232). Totals: 39 errors, as before; 22,535 warnings, 17 more |
| validator, before against after, the seven other repos | five identical. dnd5e-3rdparty gains 4 warnings (279 to 283) and troika-3rdparty 5 (66 to 71), each a `USES_` line; no other line of output differs |
| the lines rewritten as `DEPENDS_ON` in copies of teeth, curseborne, wyldwolf and Down In Yongardy | every `USES_` warning goes; teeth gains 3 errors, the three ids that name no file; no cycle; nothing else changes |
| the same in a copy of l5r5e 0.5 | the two `USES_` warnings go and nothing else changes: 27 errors, 198 warnings |

*Agent's calls, to confirm.* (1) A `USES_` line is reported and is not itself read as a
dependency: its id is checked once the line is rewritten. So the three TEETH ids show as three
"older form" warnings now and as errors after the rewrite. (2) `DEPENDS_ON` accepts the id of
any loaded file, which is what §3 already said ("Each names a file in the loaded set"); the
validator had accepted a BASE or an EXTENSION only. (3) `USES_EXTENSION`, `USES_SETTING` and
`USES_FRAME` stay reserved. (4) Rules 2 to 4 of §16 keep "exactly one BASE", "optionally one
SETTING" and "optionally one FRAME"; only the keyword changes. No tool checks those counts,
before or after. (5) The grammar is unchanged: it reads a `USES_` line as it reads any line of
a keyword and a string, at every version.

*Not done.* No corpus is changed: the 26 lines are F32. With one keyword, a reader of a file
no longer sees from the line what kind of file is named.

**Part 6, ruled 2026-11-14: the rule form `WHEN […] THEN` is removed (DECISION-56).** Owner:
"Yes, remove".

Two counts in the proposal were short, and he was told both. The audit and the first proposal
gave 27 such rules; there are 31. Four in Draw Steel's core base are written with no hash, and
the count had looked for a hash. By system: Call of Cthulhu 4, Daggerheart 2, D&D 2014 2, D&D
2024 2, Draw Steel 4, The Expanse 4, Invisible Sun 3, L5R 7, Root 3. And the other form, a
label with the source's text, is written about 1,500 times, but in l5r5e and l5r5e-3rdparty
only: no other system writes it. He was given the second fact after he ruled.

A rule is a label with the source's text, or a DEF with a `DESCRIPTION`. The removed form is a
warning in a file that declares a `SPEC_VERSION` below 0.6, or none, and an error in one that
declares 0.6 or later. `WHEN` and `THEN` stay a hook's keywords.

*Applied.* Spec: §0 item 43, DECISION-56, §12 (its example, its list of forms and its last
paragraph), the example in §14, §15, the two worked examples in §17, and a note on
DECISION-18's record. Validator: one finding for a rule, where `WHEN [` opens it; and the
warning for a rule with no text no longer offers "a structured WHEN … THEN". Grammar: a
comment. README: the fixture list. New: `tests/rules-good` and `tests/rules-bad`.

| Check | Result |
|---|---|
| `tests/rules-good` in the validator, the grammar | 0 errors, 0 warnings; accepted |
| `tests/rules-bad` in the validator | 3 errors (the file that declares 0.6) and 3 warnings (the one that declares 0.5): a rule under a hash, one with no hash, and one with two conditions, reported once |
| `tests/rules-bad` in the validator before the change | 0 errors, 0 warnings |
| the fixture run against the run after part 5 | the same, but for the two new sets, the grammar's count, and one more warning on `bad.ttrpg`, which holds a rule in the removed form |
| both grammar gates | 66 of 66 good files accepted; 17 of 17 planted faults refused |
| the two rules the spec now quotes, against l5r5e | each found once, character for character: `minion_critical_strike_rules` in the core base, `ref_condition_compromised` in the GM screen reference |
| validator, before against after, 22 corpus directories | 14 identical. Eight gain one warning for each rule in the removed form and no other finding: Call of Cthulhu 4, Daggerheart 2, D&D 2014 2, D&D 2024 2, Draw Steel 4, Invisible Sun 3, L5R 7, Root 3. Totals: 39 errors, as before; 22,562 warnings, 27 more. The reworded no-text warning (15 lines, in arm5e and armdef) is read as the same line |
| validator, before against after, the seven other repos | six identical, with l5r5e-3rdparty's 49 reworded no-text warnings read as the same lines; expanse gains 4 warnings (20 to 24), its four rules |

*Agent's calls, to confirm.* (1) §12's example and §14's now quote two rules from the l5r5e
corpus. (2) In §17's L5R example the rule `REQUIRE ^"Clan", ^"School"` is gone and `School`
is marked `REQUIRED`, as `Clan` already was; the "compromised" rule is the corpus's. (3) In
§17's VTM example the `RULES` block is deleted: its two rules were in the converter's words and
the vtm5e corpus holds no rule text to put in their place. (4) §15 loses its "Rule structure"
line; `WHEN` and `THEN` are listed with the hook keywords. (5) The finding is for `WHEN [`
wherever it opens a statement, in a `RULES` block or outside one; every one in the 29
directories is in a `RULES` block. (6) The grammar still reads the form, for a file below 0.6.
It refuses a rule with no hash, as it always has.

*Not done.* No corpus is changed: the 31 rules are F33.

**Part 7, ruled 2026-11-14: an alias is a second name of a hash (DECISION-57).** The proposal
was to report `ALIAS "name"` inside a DEF, which nine definitions write and no tool reads, and
to have the nine rewritten as §5b's statement. Before ruling, the owner asked: "would it make
sense instead to have ALIAS function kind of like "ALIAS [hash] [alias name]", so that it's a
separate name that resolves to the same hash?" A test showed the gap his question points at:
with a valid alias in the 0.5 form, a reference through it that carries the entity's hash,
`#hash ^"Ninjo"`, was an error in `check_references.py`: the hash names "Ninjō" and the caret
says "Ninjo". He was given two spellings, his own `ALIAS #hash ^"name"` and
`ALIAS ^"name" FOR #hash`, and chose: "ALIAS name FOR #hash".

He did not say in words that the line inside a DEF is to be reported. The agent's message had
said that part 7 "is unchanged by this: the nine `ALIAS "name"` lines inside a DEF are still
reported, and they are rewritten in whichever spelling you pick", and he then picked the
spelling. The report is applied on that reading, to confirm.

- **The form.** `ALIAS ^"name" FOR #hash`. The entity's own name may follow the hash on the
  same line, which is how the four alias statements in armdef are written; they stay valid.
- **What it means.** The alias is a name of the entity that carries the hash. `#hash ^"name"`
  is a pair that agrees, wherever a reference is written.
- **Older forms.** An alias `FOR` a name with no hash, and `ALIAS "name"` inside a DEF. Each is
  a warning in a file that declares a `SPEC_VERSION` below 0.6, or none, and an error in one
  that declares 0.6 or later.

*Applied.* Spec: §0 item 44, DECISION-57, §5b's *Aliases* rewritten, a line of §5d, and a note
on the records of DECISION-6 and DECISION-14. Validator: the alias statement reads `FOR #hash`
with or without a name after it; an alias is a name of its hash in the check of a hash against
a name; one finding for each older form. `check_references.py` and `check_constructs.py`: the
same, in each place a hash is checked against a name, and `check_references.py` counts an alias
`FOR #hash` as a site whose hash must be an anchor. Grammar: the statement's rule. Guidelines:
one line. README: the fixture list. Three older fixtures that wrote an alias with no hash in a
file declaring 0.6 are brought to the new form (`tests/decision6.ttrpg`,
`tests/values-good/instances.ttrpg`) or set to declare 0.5 (`tests/values-bad/10-alias-cycle.ttrpg`,
since a cycle can now be written only in the older form). New: `tests/alias-good` and
`tests/alias-bad`.

| Check | Result |
|---|---|
| `tests/alias-good` in the four tools | validator 0 errors, 0 warnings; `check_references.py` 0 errors; `check_constructs.py` 0 errors; grammar accepted |
| `tests/alias-good` before the change | validator 1 error (a list member `#hash ^"Ninjo"`); `check_references.py` 2 errors (two `REFERENCES` lines); `check_constructs.py` 1 error (a hook's `THEN`) |
| `tests/alias-bad` in the validator | 3 errors (the file that declares 0.6: the line in a DEF, `FOR` a name, a hash that is no anchor) and 2 warnings (the file that declares 0.5); before the change, 0 and 0 |
| `tests/alias-bad` in `check_references.py` | 3 errors: a hash that is no anchor, a hash with another entity's name after it, and `#hash ^"Yearning"` where no alias gives that name |
| the fixture run against the run after part 6 | the same, but for the two new sets, the grammar's count, two more warnings in `values-bad` and one in `mods-bad.ttrpg` (aliases `FOR` a name, in files below 0.6) |
| both grammar gates | 67 of 67 good files accepted; 17 of 17 planted faults refused |
| the nine lines rewritten as statements in copies of l5r5e and vtm5e (run before the tools changed) | validator and `check_references.py`: the same findings as the corpora as written |
| validator, before against after, 29 directories | 27 identical. l5r5e gains 8 warnings and vtm5e 1, the nine `ALIAS "name"` lines, and no other finding. Totals over the 22: 39 errors, as before; 22,571 warnings, 9 more |
| `check_references.py`, before against after, 29 directories | identical output in all 29 |
| `check_constructs.py`, before against after, 29 directories | identical output in all 29 |

*Agent's calls, to confirm.* (1) The report of `ALIAS "name"` inside a DEF, as above. (2) An
alias `FOR` a name with no hash is an older form; the proposal's table said "hash required".
(3) The target's name is read only on the hash's line (§8, *Where a statement ends*), so a
caret that opens the next line is the next statement. (4) A list member that is an alias with
a hash is now warned when it is written with no hash, as any member is; before, every alias was
exempt because it had no hash to carry. (5) The validator does not check that a name written
after the hash is the anchor's; `check_references.py` does. (6) §5b still says an alias may
target a bound reference; how that is written with a hash is not ruled. (7) A bridge's sided
aliases are untouched.

*Not done.* No corpus is changed: the nine lines are F34. The synthesist is unchanged (F34).

### C7. The base spec reserves L5R mechanics

**Status:** closed 2026-11-14 by the owner. Committed and pushed on branch `0.6`. A check and
a reward are the system's, and the base spec defines neither (DECISION-58). The corpus work
is F35.

Design principle 5 is system-agnostic grammar. §16 and §18 reserve `RING`, `RING_TN`, `TN`,
`APPROACH`, `XP_BASE` and `XP` for scenes, and fix scene types to a list that includes "Intrigue".
A `CHECK` cannot hold a VtM dice pool against a Difficulty, a D&D DC with an ability and skill, or a
CoC difficulty level. `CHECK` is used in l5r5e (59) and curseborne (13). The 448 scenes in vtm5e,
callofcthulhu7e, draw-steel, teeth and tor2e have none.

**Evidence, recounted 2026-11-14** over the 22 corpus directories and seven other repos.

| | Checks | Notes |
|---|---|---|
| l5r5e | 60 | `SKILL`, `RING` 21, `TN` 68, `RING_TN` 65, `ALTERNATIVE` 8. The audit's first count was 59 |
| curseborne | 13 | in L5R's words: `SKILL "Culture"`, `RING "Cunning"`, `TN 3`; `APPROACH` 10 |
| dnd5e-3rdparty (Wyldwolf Axis) | 10 | `SKILL "Perception"`, `DC 10`: a field §16 does not list. Not in the audit's first count, which left out third-party repos |

`REWARDS`, `XP_BASE` and `XP` are written by l5r5e only, in two arcs. The 448 scenes in vtm5e,
callofcthulhu7e, draw-steel, teeth and tor2e hold no check. Neither the grammar, the validator,
`check_references.py`, `check_constructs.py` nor the synthesist mentions `CHECKS`, `CHECK`,
`RING`, `TN`, `RING_TN`, `APPROACH`, `ON_SUCCESS`, `ON_FAILURE`, `REWARDS`, `XP_BASE` or `XP`:
the reservation was the spec's text and nothing else. The fixed list of scene types, with
"Intrigue" on it, went with DECISION-23.

**Ruled 2026-11-14: a check and a reward are the system's (DECISION-58).** The agent proposed
that the base keep the frame of a check (`CHECKS`, `CHECK`, `ALTERNATIVE`, `ON_SUCCESS`,
`ON_FAILURE`, and `REWARDS`, `CONDITIONAL_REWARDS`, `REWARD`) and give its fields to the system,
and offered generic fields as the alternative. Owner: "why isn't it entirely delegated to the
system? I don't think generic fields are helpful here, these should be system-specific. The
base spec can provide a couple examples, but those examples are not part of the base spec."

The frame had been kept so that a consumer could find every check and its outcomes without
knowing the system. That does not hold: no tool reads the frame, three systems write one, and
success against failure is itself one game's shape (Root's own rule has three results). A
named block is a target through its hash whatever its keyword (§20), so a system's `CHECK`
needs nothing from the base.

*Applied.* Spec only: §0 item 45, DECISION-58; in §16, the `CHECKS` block is out of the ARC
template and the scene template, the `REWARDS` block out of the ARC template, and the field
list for `CHECKS` is replaced by *A system's own blocks*, with two checks as examples; §18's
ARC and SCENE lists; and §15's example of a block keyword a system uses elsewhere, which was
`SKILL` and is now `TRIGGER`. No tool, fixture or corpus file is changed, so no gate was rerun.

| Check | Result |
|---|---|
| the l5r5e example in §16, against `l5r5e-0.5-gm-kit-dark-tides.arc` | found once, character for character |
| the Wyldwolf example in §16, against `wyldwolf-axis-mikko-0.5-adventure.arc` | found once, character for character |
| what the commit touches | the spec and this audit; `git status` shows no tool, fixture or sample changed |

*Agent's calls, to confirm.* (1) `REWARDS`, `CONDITIONAL_REWARDS`, `REWARD`, `XP_BASE` and `XP`
go with the check. He spoke of the check; C7 names `XP_BASE` and `XP` beside it, and only l5r5e
writes them. (2) The l5r5e arc that §16 shows as its example keeps its `CHECKS` and `REWARDS`,
labelled as l5r5e's. (3) §16's rules for when to write `SKILL`, `RING`, `TN`, `RING_TN`,
`ALTERNATIVE` and the two outcomes are out of the spec (F35). (4) `MONTAGE` and `MOMENT`, which
only l5r5e writes (2 and 6 times), are left in §18: C7 does not name them. (5) `CLUES`,
`CONFLICT`, `OBJECTIVES` and `RESOLUTIONS` are left: five or six systems write each.

*Not done.* No corpus is changed. Curseborne's 13 checks stay in L5R's words (F35).

### C8. Edition identity is load-bearing and undeclared

**Status:** closed 2026-11-14 by the owner. Committed and pushed on branch `0.6`. Its three
parts were ruled one at a time: every file declares its edition (DECISION-59); a codex
declares it the same way (DECISION-60); the `VERSION` beside an edition is its corpus's
content version (DECISION-61). The corpus work is F36 and F37.

The edition is the namespace for hash identity (§19), the scope of coherence (§20) and the key of
`--corpus`. No file declares its edition. Three constructs point at one, each with its own syntax:
`FOR "arm5e" VERSION "0.5"` (`.selections`), `FOR EDITION "tor2e"` (`.codex`),
`ORIGIN "dnd5e" VERSION "0.4"` (`.bridge`). The binding is the directory name and a command-line
argument. The `VERSION` in those lines is the content-version directory, a third meaning beside the
file's own `VERSION` and `SPEC_VERSION`.

**Evidence, recounted 2026-11-14** over the 22 corpus directories, the third-party repos, the
bridges and the tools.

| What names an edition | Count | What reads it |
|---|---|---|
| a file declaring its own edition | 0 | |
| `.codex`: `FOR EDITION "l5r5e"` | 69 files in l5r5e; one `"tor2e"` fixture | no tool |
| `.bridge`: `ORIGIN "x" VERSION "y"`, `DESTINATION …` | 3 bridges, 6 sides | the validator, as the key of `--corpus x=<dir>`; the `VERSION` is read by nothing |
| port: `ORIGIN "x" <KIND> "id"` | 0 in the corpora (F14 is not done) | the validator, as the key of `--corpus` |
| `.selections`: `FOR "x" VERSION "y"` | 1 sample; the `tests/marked` fixture writes a BASE's id there and nothing objects | no tool |
| synthesist manifest: `"edition": "arm5e"` | outside the DSL | the synthesist |

- **The directory does not give the edition for a third-party tree.**
  `titterpig-dsl-dnd5e-3rdparty/wyldwolf/5.5` depends on `Dnd5_5e_Core_Base`, the D&D 2024
  base. Every tree in `titterpig-dsl-arm5e-3rdparty` depends on `ARMDef_…` files, the armdef
  edition.
- **The `VERSION` beside an edition has three meanings in three bridges:** `"arm5e" VERSION
  "0.4"` (the corpus is at 0.5), `"pendragon6e" VERSION "0.5.1"` (a file's version),
  `"arm4" VERSION "4"`.
- **An edition has from 1 to 19 BASE files:** one in 18 of the 22 directories, 8 in arm5e, 12
  in armdef, 19 in l5r5e.
- **Every file's `VERSION` in the 22 directories begins with its directory's version.** The
  corpus's content version can be read from a file.

*Proposed 2026-11-14,* to be ruled one part at a time.

1. An edition is declared in the files. Either each BASE file declares it and every other
   file takes the edition of the BASE its dependencies reach (recommended), or every file
   declares it.
2. The lines that point at an edition are checked against what the files declare, and their
   three spellings are looked at together.
3. What the `VERSION` beside an edition means.

**Part 1, ruled 2026-11-14: every file declares its edition (DECISION-59).** Owner: "In every
file". The agent had recommended a declaration in BASE files that the rest would inherit, with
this as the alternative.

`EDITION "id"` stands in the header of every BASE, EXTENSION, FRAME, ARC and CAMPAIGN. A file
with none is a warning where it declares a `SPEC_VERSION` below 0.6, or none, and an error from
0.6.

*Applied.* Spec: §0 item 46, DECISION-59, the rule in §19, a sentence in §20, §3's three
templates and field list, the field lists of §16's four containers, §15, and the header of nine
examples that declare 0.6. Validator: the header line is read; a new pass reports a file with
no edition, `EDITION` written twice, a run that holds two editions, and a `--corpus x=<dir>`
directory that declares another. Grammar: the header takes `EDITION "id"`. Guidelines: two
lines. README: the fixture list. 158 fixture and sample files gain the line, so that each set
stays as it was. New: `tests/edition-good` and `tests/edition-bad`.

| Check | Result |
|---|---|
| `tests/edition-good` in the validator, the grammar | 0 errors, 0 warnings; 4 of 4 accepted |
| `tests/edition-good`, given as `--corpus other=<dir>` | 1 error: three files there declare "edition-demo" |
| `tests/edition-bad` in the validator | 3 errors and 1 warning: no `EDITION` at 0.6; none at 0.5; `EDITION` twice; a second edition in the run. Before the change, 0 and 0 |
| the fixture run against the run after C6, once the 158 files carry the line | identical, but for the two new sets and the grammar's count |
| both grammar gates | 71 of 71 good files accepted; 17 of 17 planted faults refused |
| validator, before against after, 22 corpus directories | every directory gains one warning for each file that must declare an edition and no other finding: 6,280 in all. Totals: 39 errors, as before; 28,851 warnings |
| validator, before against after, the seven other repos | the same: 200 new warnings between the seven, and no other finding |

*Agent's calls, to confirm.* (1) The keyword is `EDITION`, which a codex already writes in
`FOR EDITION`. (2) A file below 0.6 with no edition is a warning, as every new requirement of
0.6 has been; that is one warning for each of 6,280 files in the 22 directories. (3) A SETTING
may declare an edition or none: §16 calls it system-agnostic, with no dependencies. 38 exist.
(4) The dice module declares none. (5) A codex and a bridge are not read by the new pass: each
points at editions, which is part 2. (6) Two editions in one run is one error, at every
version, reported once. (7) An edition id is any string; the 22 directory names are the ids in
use, and nothing checks an id against a list. (8) A bare `.actor` file has no header to hold
the line; it gets one with its wrapper (F17).

*Not done.* No corpus is changed: F36. The validator does not check that an extension declares
the edition of the files it depends on, except through the rule that a run holds one edition.

**Part 2, ruled 2026-11-14: a codex declares its edition as every file does (DECISION-60).**
Owner: "Yes, fold it".

Four lines name an edition. Two name the file's own: `EDITION` (part 1) and a codex's optional
`FOR EDITION`, which 69 codex files write, all in l5r5e, and no tool read. Two name another
edition: a bridge's sides and a port's `ORIGIN`. Those two share a keyword already, and part
1's check on `--corpus x=<dir>` covers both. `.selections` writes a fifth, `FOR "x" VERSION
"y"`; it is marked as likely to be replaced (DECISION-53) and is left.

A codex writes `EDITION "id"` in its header. `FOR EDITION "id"` is read as the same line and is
a warning in a file that declares a `SPEC_VERSION` below 0.6, or none, and an error from 0.6. A
codex with neither is reported as any file is.

*Applied.* Spec: §0 item 47, DECISION-60, §25's header and its paragraph on the line, a bullet
of §19, §15. Validator: a codex is one of the files of the edition pass; `FOR EDITION` is
reported and read as the codex's edition. Grammar: a comment. README: the fixture list, and
`samples/`, which holds two editions and is validated as two. Four codex fixtures and the codex
sample gain the line. `tests/edition-good` and `tests/edition-bad` gain codex files.

| Check | Result |
|---|---|
| `tests/edition-good`, with a codex that declares `EDITION` | validator 0 errors, 0 warnings; grammar 5 of 5 accepted |
| `tests/edition-bad` in the validator | 5 errors and 2 warnings; the three new findings are `FOR EDITION` at 0.6 (error), `FOR EDITION` at 0.5 (warning) and a codex with no edition at 0.6 (error). Before the change, 3 and 1 |
| the fixture run against the run after part 1, once the codex fixtures carry the line | identical, but for the two edition sets and the grammar's count |
| both grammar gates | 72 of 72 good files accepted; 17 of 17 planted faults refused |
| `samples/` as one run | 1 error: it holds "arm5e" and "tor2e". Each half alone: 0 errors |
| validator, before against after, 22 corpus directories | 21 identical. l5r5e gains 69 warnings, its 69 codex files' `FOR EDITION`, and no other finding (312 to 381). Totals: 39 errors, as before; 28,920 warnings |
| validator, before against after, the seven other repos | identical output in all seven |

*Agent's calls, to confirm.* (1) A codex with no edition is reported as any file is; the line
was optional before, and he was told so in the proposal. (2) `FOR EDITION` in a file below 0.6
is read as the codex's edition, so the 69 l5r5e codex files count as "l5r5e" in the rule that
a run holds one edition. (3) `samples/` is two editions and is validated as two; the codex
sample is about tor2e and the conformance sample about arm5e. (4) A bridge's sides, a port's
`ORIGIN` and a `.selections` file's `FOR` are untouched.

*Not done.* No corpus is changed: the 69 codex files are in F36.

**Part 3, ruled 2026-11-14: the `VERSION` beside an edition is its corpus's content version
(DECISION-61).** Owner: "Define and check it". The alternative put to him was to remove the
`VERSION` from a bridge's side.

A corpus has a content version, the `0.5` of its directory and file names, and DECISION-50 made
it the span in which a hash is stable. The `VERSION` of every file in the 22 corpus directories
begins with its directory's version, so the version is in the files. The `VERSION` beside an
edition names it: a file belongs to the corpus when its own `VERSION` begins with that version,
part for part. The validator checks a bridge's side against the files given as
`--corpus <edition>=<dir>`: a warning in a bridge that declares a `SPEC_VERSION` below 0.6, or
none, and an error from 0.6.

The proposal said two of the three bridges would be reported. It is all three: the D&D bridge
writes `"0.4"` on both sides and both corpora are at 0.5. He is told with the result.

*Applied.* Spec: §0 item 48, DECISION-61, §19's third axis and a paragraph under *Editions &
version namespaces*, a sentence of §21, a bullet of §20. Validator: a new pass over a bridge's
sides. README: the fixture list. New: `tests/sides`, two bridges and two small corpora.

| Check | Result |
|---|---|
| `tests/sides/good.bridge` with its two corpora | 0 errors, 0 warnings; one corpus holds files at 0.5.1 and 0.5.10 under a side that says `"0.5"` |
| `tests/sides/bad.bridge` with the same corpora | 2 errors: `"0.4.9"` against a file at 0.4.2, and `"0.4"` against files at 0.5. Before the change, 0 |
| `tests/sides` in the grammar | 5 of 5 accepted |
| the fixture run against the run after part 2 | identical, but for the two new lines |
| both grammar gates | 72 of 72 good files accepted; 17 of 17 planted faults refused |
| the D&D bridge, with the dnd5e and dnd5.5e corpora | 2 new warnings: both sides say `"0.4"`; all 12 and all 14 files are at 0.5 |
| the arm4 to arm5e bridge, with the arm5e corpus | 1 new warning: `"arm5e"` at `"0.4"`; all 2,435 files are at 0.5. The `"arm4"` side is `EXTERNAL` and is not checked |
| the Pendragon bridge, with both corpora | 1 new warning: `"pendragon6e"` at `"0.5.1"`; 266 of 270 files do not begin with it. `"pendragon5e"` at `"0.5"` passes |
| validator, before against after, 29 directories | identical output in all 29; the 22 corpus directories stand at 39 errors and 28,920 warnings |

*Agent's calls, to confirm.* (1) "Begins with" is exact on the parts given, numbers as
numbers: `"0.5"` is met by 0.5.10 and not by 0.4.2. It is not DECISION-35's "at least". (2) A
file that declares no `VERSION` is not counted. (3) Within a corpus, nothing checks that its
files share a content version; the check runs only where a side names one. (4) A side with no
`VERSION` is not reported. (5) A `.selections` file's `FOR "x" VERSION "y"` is left
(DECISION-53). (6) §21's example bridge keeps `"0.4"` on its sides; it declares `SPEC_VERSION
"0.4"`.

*Not done.* No bridge is changed: F37.

### C9. Smaller gaps

**Status:** closed 2026-11-16 by the owner. Committed on branch `0.6`. Its nine bullets were
recounted against the spec as it stood after C1 to C8 and put to the owner one at a time. Six
are ruled: each edition has a `.system` file (bullet 1, DECISION-62); a guidance entry may
hold `REFERENCES` (bullet 3, DECISION-63); a codex entity is its hash, lore and mechanics
keep separate identities, and every codex edge cites its own source (bullet 6, DECISION-64,
DECISION-65, DECISION-66); a bridge `MAP` needs no `DISPOSITION` and `SCALE` states no
rounding (bullet 7, DECISION-67, DECISION-68); a name is not empty and holds no control
character (bullet 8, DECISION-69). He deferred bullet 4 and the fourth part of bullet 6.
Bullets 5 and 9, and what is left of bullet 2, are on the list *To revisit once C1 to C9 are
closed*. The corpus work is F38 to F42.

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

**Recounted 2026-11-14** over the 22 corpus directories and seven other repos, against the spec
at commit `58c45b8`.

| # | Bullet | Settled since it was written | Still open | Evidence |
|---|---|---|---|---|
| 1 | System vocabulary | nothing | a system's keywords are declared nowhere | 316 distinct system keywords in the 22 directories, 217 of them in l5r5e; 132 are written once in their corpus. A scan for rare keywords within two letters of a base keyword or a common one finds 15, and none reads as a misspelling (`OUTCOMES`, `PHASES`, `TYPES`, `COSTS`, …) |
| 2 | `MODIFY`'s reach | the rule form (DECISION-52): a rule is replaced in a `RULES` block | another text field, a system sub-block, a nested property by path, a removal | l5r5e-3rdparty's three `OVERRIDE`s each restate a technique to change one sub-block (`OPPORTUNITIES`). `OVERRIDE` is marked as likely to be replaced (DECISION-53) |
| 3 | `GUIDANCE` entries | `EMPHASIS` in an entry (DECISION-51); 194 entries write one | `REFERENCES` in an entry; a kind; a position | of 13,536 `ENTRY` blocks none holds `REFERENCES` or `^"Page"`; 285 hold a `TYPE` |
| 4 | `HOOKS` | `TRIGGER` and the two upper levels are marked (DECISION-54) | whether `WHEN` is the source's text; a pointer to the sentence | the three corpus hooks each write a `WHEN` that stands word for word in their file's text |
| 5 | `OPTIONAL` and `.selections` | `.selections` is marked (DECISION-53) | all of it | on the owner's list, below |
| 6 | `.codex` | a codex declares its edition (DECISION-60) | a link from an `ENTITY` to a DEF; facts that are not entities; an edge's source; "the first `ENTITY`" | l5r5e: 69 files, 1,496 `ENTITY` blocks, 1,361 names; 114 names are declared by more than one block; 80 names are also a DEF's (first counted as 52; recounted in the bullet's block below) |
| 7 | `.bridge` | the `VERSION` on a side (DECISION-61) | `MAP` needs a `DISPOSITION`; `SCALE` and rounding | two of the three bridges declare no dispositions and write no `MAP`: 21 `PROCEDURE`s, 19 `UNCHANGED INTO`. `SCALE` is written three times, all in the arm4 bridge (`6 OVER 5`, `5`, `1 OVER 3`) |
| 8 | Names | `\"` in a name (DECISION-25) | an empty name; `^","` | the validator and the grammar accept `^""` and `^" "` with no finding. `^","` is a DEF's name in three files (invisiblesun 1; arm5e and armdef 1 each, the same nested DEF) |
| 9 | `ADD` | `ADD … DEF` is marked (DECISION-53) | its replacement | on the owner's list, with `OVERRIDE` |

Bullets 5 and 9, and what is left of bullet 2, belong with the list *To revisit once C1 to C9
are closed*: each waits on a replacement that list is to rule. Bullets 1, 3, 4, 6, 7 and 8 are
put to the owner in turn.

**Bullet 1, direction given 2026-11-14: a `.system` file.** The agent recommended leaving the
vocabulary undeclared, since the scan found no misspelling. Owner: "Let's do something like
this: l5r5e.system adds the system-specific primitives and also holds the index of any/all
files associated with it".

What a system knows about itself sits in three places today, none of them DSL: a prose spec
file in four repos (`l5r5e-dsl-spec.md`, 1,453 lines; also arm5e, root, vtm5e), which documents
the system's keywords; a synthesist manifest (15 manifests for 9 editions), which names the
edition and lists files in load order (l5r5e's lists 73 of its 166 DSL files); and `sources.json` in 8
repos. No `.system` file and no `SYSTEM` keyword exists.

The concrete shape was put to him before anything was applied, with a recommendation on each
choice in it. Owner: "Yes, apply it".

**Bullet 1, ruled 2026-11-14: the `.system` file (DECISION-62).** One file for each edition,
`l5r5e.system`, in the corpus's folder: `SYSTEM "l5r5e" { NAME, VERSION, SPEC_VERSION,
RELEASE_DATE, KEYWORDS [ … ], FILES [ … ] }`.

- **`SYSTEM "id"`** is the edition that a file's `EDITION` names (DECISION-59). Its `VERSION`
  is the corpus's content version (DECISION-61).
- **`KEYWORDS`** lists the system's own keywords, each by its name alone.
- **`FILES`** lists the system's files by path from the system file's folder. It is an index
  and gives no order.
- **With a system file in the run** the validator reports a keyword that neither the base spec
  nor the system declares, a file of the system that `FILES` leaves out, and a `VERSION` that
  does not begin with the system's: each a warning in a file that declares a `SPEC_VERSION`
  below 0.6, or none, and an error from 0.6.
- **With none in the run** nothing of this is checked, and a note says so.

*Applied.* Spec: §0 item 49, DECISION-62, a new section in §19, the file table of §2, §1, §15
(a list for the system file, and the paragraph on system keywords), two sentences of §20.
Validator: `.system` is read; a new pass does the checks above; the base spec's keywords are a
list in the tool, taken from §15 and §18. Grammar: the `SYSTEM` block; `check_grammar.py` reads
the extension. README: the fixture list. New: `tests/system-good` and `tests/system-bad`.

| Check | Result |
|---|---|
| `tests/system-good` in the validator, the grammar | 0 errors, 0 warnings; 4 of 4 accepted |
| `tests/system-bad` in the validator | 7 errors and 1 warning: a keyword no one declares (0.6 error, 0.5 warning), a file not in `FILES`, a `VERSION` that does not begin with the system's, an `EDITION` the system file does not declare (and the two-edition error with it), a base keyword in `KEYWORDS`, a listed file that is not there. Before the change, 1 error |
| the fixture run against the run after C8 | identical, but for the two new sets and the grammar's count |
| both grammar gates | 76 of 76 good files accepted; 17 of 17 planted faults refused |
| a system file generated for copies of teeth, dnd5e, curseborne and root, with an empty `KEYWORDS` | every system word is reported once for each file that writes it (37, 5, 22 and 188 findings); no `FILES` or `VERSION` finding |
| the same, with `KEYWORDS` generated from the files | the findings are those of the corpus as it stands, in all four; each generated file passes the grammar |
| the generated lists, read | teeth 5 words, dnd5e 2, curseborne 17, root 18; none is a base keyword |
| validator, before against after, 29 directories | 28 identical. l5r5e, the one corpus whose files name an edition, gains the note that no system file is in the run, and no finding. The 22 corpus directories stand at 39 errors and 28,920 warnings. (This row stood as a placeholder until 2026-11-14, when it was filled from the saved run.) |

*Agent's calls, to confirm.* (1) With no system file in the run the validator prints a note
and raises no warning; the proposal said "one warning". A warning would stand on every fixture
set and on every run of a single file. (2) The base spec's keywords are a list of 173 words in
the validator: the 172 of §15 and §18, and `ROW`, the row of the older `TABLE` grid, which 13
corpora write 12,394 times and which is no system's. (3) A base keyword that a system uses
outside its block (`TRIGGER`, `TYPE`, `TAGS`) is not declared in `KEYWORDS`. (4) A keyword is
one that opens a statement: a capitalised word first on its line. (5) A file that declares no
edition is held to the run's system file only when the run has exactly one. (6) A bare
`.actor` file has no header and is not held to it. (7) A system file's id is not a file id: a
`BASE "teeth"` and a `SYSTEM "teeth"` stand together. (8) The file's own `VERSION` is checked
against the system's, which DECISION-61 had left unchecked inside a corpus.

*Not done.* No corpus has a system file: F38. A third-party book's files and keywords are not
covered; that is with the campaign's load file, on the list below. The generator used for the
pilot is a script in the session's scratch folder and is not in the repo.

**Bullet 3, ruled 2026-11-14: `REFERENCES` in a guidance entry; its kind is a topic
(DECISION-63).** Owner: "Yes, both".

Of the bullet's four points two were settled already: `EMPHASIS` in an entry (DECISION-51), and
the entry's place, which DECISION-45 gave every block as `^"Page"`. Counted over 11,027
guidance entries (7,673 in arm5e): none holds `REFERENCES`, an embedded reference or `^"Page"`;
94 carry a page in a comment (F28). The kind is written as a topic: `"errata"` and its two
variants 2,943 times, `"Margin Note"` 316, `"Sidebar"` 266 and `"sidebar"` 76, `"Example"` 152.

- **`REFERENCES`** is legal in an entry, on the terms of `EMPHASIS`: each surface form is in
  that entry's `TEXT`.
- **The kind** stays one of the entry's `TOPICS`. The base spec fixes no list.

*Applied.* Spec: §0 item 50, DECISION-63, §22's template and two bullets. Grammar: a guidance
entry takes a `REFERENCES` block and a `^"Page"`. The validator, `check_references.py` and
`check_constructs.py` are unchanged: they read both already. `tests/guidance-good` gains an
entry with a `REFERENCES` block and a page; `tests/guidance-bad` gains two faults.

| Check | Result |
|---|---|
| `tests/guidance-good` in the four tools | validator 0 errors, 0 warnings; `check_references.py` 0 errors, 1 reference read; `check_constructs.py` 0 errors; grammar accepted |
| `tests/guidance-good` in the grammar before the change | refused, at the entry's `^"Page"` line |
| `tests/guidance-bad` in `check_references.py` | 4 errors: the two of DECISION-51, a `REFERENCES` span that is not in its entry's `TEXT`, and a target that is no entity |
| the fixture run against the run after bullet 1 | identical, but for the two guidance lines |
| both grammar gates | 76 of 76 good files accepted; 17 of 17 planted faults refused |

*Agent's calls, to confirm.* (1) The grammar reads `^"Page"` in an entry. DECISION-45 gave
every block a page and the grammar refused one here. (2) The grammar was not rerun over the
corpora: the change lets an entry hold two things more, and no corpus entry holds either.
(3) The two spellings `"Sidebar"` and `"sidebar"` are noted for the corpora and not ruled.

*Not done.* No corpus is changed.

**Bullet 4, deferred 2026-11-14.** Owner: "I think we need to defer a decision here, flag it
for follow-up".

What was put to him. `TRIGGER` and the two upper levels were marked already (DECISION-54). Two
points stayed open: §23 calls `WHEN` "the human-readable condition (a string)" and does not say
whether the string is the source's wording or the converter's, and a hook does not point at the
sentence it was drawn from. The corpora write three hooks, all in arm5e and all `TAGGED`, in
the DEFs `^"Activities While Injured"`, `^"Aiming"` and `^"Certamen"`; each `WHEN` stands word
for word in the text of the DEF that holds it. The agent proposed that §23 say so, with
`check_constructs.py` checking it, and gave as the alternative a free `WHEN` beside a new field
that quotes the source.

Nothing is ruled and nothing changes: the spec, the grammar and the tools read a hook as they
did after DECISION-54. The question is on the list below.

**Bullet 6, measured 2026-11-14 and put to the owner in four parts**: a repeated entity, an
entity that is also a DEF, an edge's source, a date or a number as a fact. All counts are of
`titterpig-dsl-l5r5e/0.5`, the one corpus with a codex: 69 files, 1,496 `ENTITY` blocks, 1,361
names, 1,282 edges.

- **A repeated entity.** §25 says a later file restates `ENTITY #hash ^"Name"`, "same hash, same
  name", and that the first block is the canonical one. No hash is written on two `ENTITY`
  lines. 114 names are declared by two to five blocks, 249 blocks in all, each under a hash of
  its own. 114 blocks hold no `IS`, and the hash of each is written nowhere else. Of the 114
  names, 94 have one block with `IS` and the rest without; 20 have two or three blocks with
  `IS`. 204 edges name one of the 114 as their object, by name alone.
- **How it came about.** Before commit `c7abe91` of the l5r5e repo (2026-09-23, "H1: every
  unhashed entity hashed") 127 `ENTITY` lines carried no hash: a later file added to an entity
  by its name. That commit gave each of them a new hash.
- **What the tools say.** The validator reports nothing on any of this: it does not check that
  an entity has an `IS`, and one name under two hashes is two entities (DECISION-27). The
  grammar reads an `ENTITY` with no hash; the spec's template always writes one.
- **An entity that is also a DEF.** 80 entity names are also the name of a DEF outside the
  codex (49 in `.ttrpg` files, 34 in `.arc`, 3 in `.actor`; a name may be in two). 54 edges
  name one as their object. The table above first gave 52; that count is superseded.
- **An edge's source.** Every one of the 1,496 blocks holds exactly one `SOURCE`. 1,237 edges
  carry `FROM`: 1,088 stand word for word in their block's `.lore` file (white space, quote
  style and Markdown emphasis set aside); 65 join pieces with an ellipsis, and in 59 of those
  every piece is found; 84 are not found.
- **A date or a number.** No edge's object holds a digit, and none of the 42 predicates in use
  is about a date or a quantity. Of the 50 blocks that are an `^"Event"`, 2 have a year
  within 300 characters of the event's name in the section their `SOURCE` names
  (`^"Battle of Kyūden Tonbo"`, "In the year 704"; `^"Ride of the Unicorn"`, "in the year
  815"), 11 more have a year somewhere in the section, 36 have none and 1 names no heading.

The measuring scripts are in the session's scratch folder (`c9/codex_measure*.py`) and are not
in the repo.

**Bullet 6, part 1, ruled 2026-11-14: an entity is its hash, and its name under another hash
is a collision (DECISION-64).** The agent proposed that a file add to an entity by restating
its hash and that no block be first, and left one name under two hashes as two entities, as
DECISION-27 has it for DEFs. Owner: "a later file should only modify an existing hash,
otherwise it's a collision and it should flag an error. Please let me know if I'm missing
anything."

- **An `ENTITY` writes its hash.** One name is one entity under one hash.
- **A file adds to an entity** by restating `ENTITY #hash ^"Name"`. The node is what all its
  blocks say together; no block is first.
- **The same name under another hash is a collision.**
- **At least one block of an entity holds `IS`.**

*Applied.* Spec: §0 item 51 and a note on item 14, DECISION-64, §25 (the `#hash` and `IS`
bullets, the template's comment, the validation table, one sentence on split graphs).
Validator: a new pass over the run's `ENTITY` blocks reports the collision at every block of
the name, an `ENTITY` with no hash, and an entity none of whose blocks holds `IS`. Grammar: a
comment; the hash stays optional there so that an older file is read. README: the fixture
list. New: `tests/entity-good` and `tests/entity-bad`. `tests/anchors-good/lore.codex`, an
older fixture at 0.6, declared an entity with no `IS` and gains one.

| Check | Result |
|---|---|
| `tests/entity-good` (a second file adds to an entity by its hash, with no `IS` of its own) | validator 0 errors, 0 warnings; grammar accepted |
| `tests/entity-bad` in the validator | 5 errors and 1 warning: "Harrow Ford" under two hashes (an error at each of its two blocks), "Odile" under two (an error in the 0.6 file, a warning in the 0.5 file), an `ENTITY` with no hash, an entity with no `IS`. Before the change, 0 errors and 0 warnings |
| the fixture run against the run after bullet 3 | identical, but for the two new sets and the grammar's count |
| both grammar gates | 78 of 78 good files accepted; 17 of 17 planted faults refused |
| l5r5e in the validator | 27 errors as before; 630 warnings, 249 more: one at each block of the 114 names |
| validator, before against after, 29 directories | 28 identical. l5r5e gains 249 warnings, each the collision, and no other finding. Totals over the 22: 39 errors, as before; 29,169 warnings, 249 more. The working validator is the copy that was run |

*What the owner asked to be told.* (1) The rule is stricter for a codex entity than
DECISION-27 is for a DEF: two DEFs of one name under two hashes are two entities, and two
entities of one name are now a collision. Two things that share a name have to be named apart
in a codex. Of the 20 l5r5e names declared in full more than once, each reads as one subject
declared twice (`^"Amaterasu"`, `^"Fu Leng"`, `^"Otosan Uchi"`); `^"Brotherhood of Shinsei"`
is a `^"Faction"` in one block and an `^"Organization"` in the other. (2) The validator knows
no load order, so it cannot say which block is the later one; it reports every block of the
name. (3) An entity whose name is also a DEF's (80 names) is not touched by this ruling; it is
part 2.

*Agent's calls, to confirm.* (1) "Modify an existing hash" is read as restating
`ENTITY #hash ^"Name"`, which is §25's form, and not as the `MODIFY` statement of §13. (2) The
collision is a warning in a file that declares a `SPEC_VERSION` below 0.6, or none, and an
error from 0.6, as each new check of this audit is; the owner said "flag an error". l5r5e's
codex files declare 0.5, so its 249 findings are warnings. (3) The proposal's other two checks
are applied with it, at the same levels: an `ENTITY` with no hash, and an entity with no `IS`.
He did not speak to them. (4) An entity with no `IS` is not reported when its name is in
collision, since giving the block its entity's hash answers both. (5) Two names are the same
by the rule of DECISION-33.

*Not done.* No corpus is changed: F39. `check_references.py` and `check_constructs.py` are
unchanged.

**Part 1, the level, ruled 2026-11-14.** On call (2) the owner: "first of all, I'm ok with the
stricter interpretation; the l5r5e situation where you have two different defs of the same
thing means that there's an error in those files, so we should throw an error." The collision
is an error at every version. An `ENTITY` with no hash and an entity with no `IS` stay a
warning below 0.6 and an error from 0.6; he did not speak to those two. The table above shows
part 1 as first applied. After this change `tests/entity-bad` and l5r5e stand as the table
under part 2 gives them.

**Bullet 6, part 2, ruled 2026-11-14: lore and mechanics keep separate identities
(DECISION-65).** The agent proposed carrying part 1 across: an entity whose subject is a DEF
writes the DEF's hash, and a DEF's name under a new hash is a collision. Owner: "We should
consider separating identities between lore and mechanics, because they are often only
semi-overlapping. In general and for now, it should be normal for there to be the same thing
named in multiple places meaning distinct things. Context and hash references should be
sufficient to distinguish. I don't think we need a more rigorous approach defined in the base
spec." And: "Let's mark for a review the idea of a parallel unique ID system in lore, but
that's not immediately in scope."

- **An entity and a DEF of one name are two things**, each under its own hash.
- **The base spec defines no link** between them, and no tool compares them.
- **A set of unique identifiers for lore** is on the list for review, below.

The 80 l5r5e names, by what the entity is and what the DEF is: a person and a stat block, a
pregenerated character or an arc's cast entry, 35; a place and an entry in an `.arc` file, 24;
an artifact, tradition, document, organization, title or faction and an item or technique, 15;
a race and a stat block, 4; a person and a family (`^"Isawa"`, `^"Shosuro"`), 2. The 93 DEFs
are all hashed.

*What the tools did already.* A run with an entity and a DEF both named `^"Isawa"` drew no
finding for the shared name from the validator or `check_references.py`: the ruling is what
they did. One thing stood against it. An edge's object could not be written with a hash: the
grammar refused `^"founder-of" -> #hash ^"Isawa"` and the validator read it as two edges with
no object. So in a codex a hash could not tell the two apart.

*Applied.* Spec: §0 item 52, DECISION-65, §25 (a bullet on an entity and a DEF of one name;
the edge's object and the template; two rows of the validation table), and the levels of
DECISION-64 in item 51, its record, the `#hash` bullet and the table. Validator: the
collision is an error at every version; an edge's object may carry a hash, which is checked
as at any site (the hash is an anchor; the name is its anchor's). Grammar: an edge's object
is a reference with an optional hash. `tests/entity-good` gains a DEF named as an entity is
and an edge that tells them apart by the hash; `tests/entity-bad` gains two bad hashes on an
edge's object and an `ENTITY` with no hash in a 0.5 file.

| Check | Result |
|---|---|
| `tests/entity-good`, three files | validator 0 errors, 0 warnings; grammar accepted; `check_references.py` 0 errors. In the tools as they stood after part 1: validator 2 errors, grammar refused the file with the hashed object |
| `tests/entity-bad` | 8 errors and 1 warning: the two collisions, at each block, one of them in the 0.5 file; a hash on an object that is no anchor; a hash that is another name's anchor; an `ENTITY` with no hash (an error at 0.6, a warning at 0.5); an entity with no `IS` |
| the fixture run against the run after part 1 | identical, but for the two entity sets and the grammar's count |
| both grammar gates | 79 of 79 good files accepted; 17 of 17 planted faults refused |
| l5r5e in the validator, part 1's tool against this one | 276 errors and 381 warnings, where part 1 gave 27 and 630: the 249 collisions are errors. With the level set aside the two outputs are the same |
| l5r5e in the grammar, before against after | the same output: 136 of 166 files accepted |
| the other 28 directories | not rerun. None holds a `.codex` file, and both changes are inside the codex reader. By that, the 22 corpus directories stand at 288 errors and 28,920 warnings; the sum is not from a run |

*Agent's calls, to confirm.* (1) The hash on an edge's object. He ruled that hash references
are enough to tell two things apart, and an edge could not carry one. It is the pair of
DECISION-44, at that decision's levels. Told of it, the owner did not rule on the form and
put the question on the to-do: "we should update codex to handle this adequately, which
probably involves some kind of disambiguation." The hash on the object stands as the form for
the meantime. (2) An edge's object written with no hash is read as
before: a warning when it names nothing, and nothing when two things carry the name. (3) §25
still lets a category, an `IS` and an edge's object name a game DEF. That is a reference from
lore to mechanics and is left as it was. (4) Spec text is added for the ruling (item 52, a
bullet in §25), so that a reader of §25 learns the two may share a name.

*Not done.* No corpus is changed. `check_references.py` reads a codex edge as it did.

**Bullet 6, part 3, ruled 2026-11-14: an edge cites its own source (DECISION-66).** The agent
proposed that a block hold one `SOURCE` and that its edges be read as drawn from it. Owner: "a
block may likely have multiple sources, as in situations where later sourcebooks add to facts
about a given entity. so how would we support that?" The agent answered that an entity takes a
block for each source, and gave several `SOURCE` lines in one block as the alternative. Owner:
"why can't we invert it; each edge cites its source?" Asked whether an edge that cites none
should take its block's, he ruled: "Always on the edge".

Measured for his question, over the 1,237 `FROM` phrases of l5r5e: 870 stand under the heading
their block's `SOURCE` names, before the next heading; 73 in a sub-section of it; 71 elsewhere
in the same file; 74 are in a block that names a file and no heading; 149 are not word for
word in the file (the 84 and the 65 of the measurement above). The block's heading does not
place 71 facts.

Asked first what sources and edges are used for, the agent searched the Titterpig utilities:
the validator is the one tool that reads them as structure; doublecheck counts a codex's
strings as coverage; three maintenance scripts treat a codex as any DSL file; the synthesist,
the rules-lawyer, the engine and the dashboard have no code that reads a `.codex` file. The
campaign sites were not searched.

- **Every edge writes its source**, `SOURCE "file" [AT "heading"]`, after its object and its
  `FROM`.
- **An edge does not take its block's source.**
- **A block's `SOURCE`** is where the subject is described, and a block may hold more than one.

*Applied.* Spec: §0 item 53, DECISION-66, §25 (the template, the `SOURCE` and `RELATIONSHIPS`
bullets with an example from l5r5e, two rows of the validation table). Validator: an edge's
source is read; an edge with none is reported; its heading is checked against the `.lore`
file as a block's is. Grammar: an edge takes `SOURCE "file"` and an optional `AT`. New:
`tests/source-good` and `tests/source-bad`, each with a `.lore` file so that the heading check
runs. Every edge of `tests/good.codex`, `tests/bad.codex`, `tests/entity-good` and
`tests/entity-bad` gains a source, as do eight of the nine edges of
`samples/lore-codex/tor2e-eriador.codex`.

| Check | Result |
|---|---|
| `tests/source-good` (edges with a source; one with no heading; a block with two `SOURCE` lines) | validator 0 errors, 0 warnings; grammar accepted. The grammar before the change refused it |
| `tests/source-bad` | 1 error and 2 warnings: an edge with no source at 0.6, the same at 0.5, a heading that is not in the file. Before the change, 0 and 0 |
| the fixture run against the run after part 2 | identical, but for the two new sets and the grammar's count |
| both grammar gates | 80 of 80 good files accepted; 17 of 17 planted faults refused |
| the sample's eight phrases, searched in `tor2e-0.2-core-eriador.lore` | each stands under the heading its edge now cites |
| the sample in the validator | 0 errors, 1 warning: the edge of `^"Bilbo Baggins"`, whom the essay does not name, cites no source |
| l5r5e in the validator, part 2's tool against this one | 276 errors as before; 1,663 warnings, 1,282 more, one for each edge and no other finding |
| l5r5e in the grammar, before against after | the same output: 136 of 166 files accepted |
| the other 28 directories | not rerun. None holds a `.codex` file. By that, the 22 corpus directories stand at 288 errors and 30,202 warnings; the sum is not from a run |

*Agent's calls, to confirm.* (1) The form, `SOURCE "file" AT "heading"` after `FROM`. It was
shown to the owner as an example, with the keyword left to him; he ruled where the source
goes and named no keyword. (2) `AT` is optional on an edge, as on a block: 74 l5r5e edges
stand in a block that names no heading. (3) A block may hold more than one `SOURCE`; the
grammar and the validator read several already. (4) `FROM` stays optional and is checked by
no tool, as before. (5) The sample's file name, `tor2e-0.4-core-eriador.lore`, is kept; the
file in the tor2e repo is `tor2e-0.2-core-eriador.lore`. (6) The sample's edge for Bilbo is
left with no source and a comment, since the essay does not name Bilbo.

*Not done.* No corpus is changed: F40.

**Bullet 6, part 4, deferred 2026-11-14.** Owner: "defer decision on this."

What was put to him. An edge points from one named thing to another, so a fact whose other end
is a year or a quantity cannot be written short of an entity made for the number. The counts
are in the measurement above: no edge's object holds a digit, and of 50 `^"Event"` blocks 2
have a year beside the event's name in their lore section and 11 more have one somewhere in
it. The two options were to leave it, the date staying in the prose that the sources lead to,
or to let an edge's object be a value (`^"occurred-in" -> "704"`). The agent recommended
leaving it.

Nothing is ruled and nothing changes. The question is on the list below.

**Bullet 7, measured 2026-11-16 and put to the owner in two points**: a `MAP` with no
`DISPOSITION`, and what `SCALE` says of rounding.

- **The three bridges.** dnd5e to dnd5.5e declares `DISPOSITIONS` and writes 573 `MAP`s and 7
  `REMAINDER`s, no `PROCEDURE`. arm4 to arm5e and pendragon5e to pendragon6e declare none and
  write no `MAP`: 7 and 14 `PROCEDURE`s, 12 and 51 `CONVERT`s.
- **Where the rule is.** §21 makes `DISPOSITION` the one required field of a `MAP`, and the
  validator reports "MAP needs a DISPOSITION" as an error. The grammar does not require it.
  The Pendragon bridge's header says so of itself: the appendix "declares no change-tag
  vocabulary, so this bridge has no DISPOSITIONS -- and so no MAP or REMAINDER, which require
  one".
- **What goes into `CONVERT` for want of a `MAP`.** Of the 19 `UNCHANGED INTO` lines, 10 carry
  a value under one name (`^"SIZ"` to `^"SIZ"`) and 9 name two things, all in the Pendragon
  bridge (`^"Appearance (attribute)"` to `^"Appeal (APP)"`, `^"Attributes"` to
  `^"Characteristics"`, `^"Siege"` to `^"Siegecraft"`). The same bridge writes a merge as three
  `MANUAL` lines into `^"One-Handed Hafted"`, four removed Skills as `MANUAL` lines with no
  `INTO`, and a new Characteristic as a `MANUAL` on the destination alone. Each is a shape §21
  lists for a `MAP`: a rename, a merge, an omission, an introduction.
- **`SCALE`.** Written three times, all in the arm4 bridge: `6 OVER 5` ("add 20% to a Fourth
  Edition character's age"), `5` ("multiply remaining XP by five"), `1 OVER 3` ("Divide the
  number of Twilight Points by three, and use this as the Warping Score"). None of the three
  source sentences states a rounding, and the word does not occur in the bridge's conversion
  units.
- **Readers.** `gen_bridge.py` and `check_verbatim.py` in titterpig-mastra write and check a
  bridge. No tool in the utilities reads one to convert anything.

**Bullet 7, point 1, ruled 2026-11-16: a `MAP` may stand with no `DISPOSITION`
(DECISION-67).** The agent proposed it and gave the alternative, to leave the rule and say
that a `CONVERT … INTO` is how a document with no tags records a correspondence. Owner:
"Let's go with this", quoting the proposal: "Make DISPOSITION optional on a MAP. A MAP with
none asserts the correspondence and nothing about the kind of change. REMAINDER keeps
requiring one, since a tag is all it says."

- **A `MAP` with no `DISPOSITION`** asserts the correspondence and says nothing about the kind
  of change.
- **A `REMAINDER`** still requires `SCOPE` and `DISPOSITION`.

*Applied.* Spec: §0 item 54, DECISION-67, §21 (the `DISPOSITIONS` section, the `MAP` field
list and table with the Pendragon rename as the example, the substitution paragraph, the
`REMAINDER` section, the first paragraph of `PROCEDURE`). Validator: the error "MAP needs a
DISPOSITION" is removed; the `REMAINDER` error says why it stays. Grammar: comments only, since
it never required the field. `AUTHORING-GUIDELINES.md` and the repo's skill file each gain a
sentence. `tests/good.bridge` gains three untagged `MAP`s (a rename, a merge, an omission);
`tests/bad.bridge` gains one, which is to raise nothing, and its `MAP` with no referents now
raises one error where it raised two.

| Check | Result |
|---|---|
| `tests/good.bridge` with the three untagged `MAP`s | new validator 0 errors, 0 warnings. The validator before the change: 3 errors, "MAP needs a DISPOSITION" on each |
| `tests/bad.bridge` | 21 errors, 22 before. Its `REMAINDER` with no tag is still an error; its untagged `MAP` raises nothing; a tag that is not declared and a tag written as a string are errors as before |
| the fixture run against the run after bullet 6 part 3 | identical but for that one line |
| both grammar gates | 80 of 80 good files accepted; 17 of 17 planted faults refused |
| the three bridges in two-corpus mode, old validator against new | the same output for each: Pendragon 0 errors and 9 warnings, Ars Magica 0 and 12, D&D 0 and 87 |
| a scratch copy of the Pendragon bridge with `^"Appearance (attribute)"` to `^"Appeal (APP)"` and `^"Attributes"` to `^"Characteristics"` as untagged `MAP`s, and a third with the origin name misspelled, against the two Pendragon corpora | new validator: 1 error, the misspelled name, so an untagged `MAP`'s names are gated. Old validator: 4 errors. The grammar accepts the file. The pendragon6e repo is untouched (`git status` shows nothing) |

*Agent's calls, to confirm.* (1) The rule is not gated by version: it removes an error and
adds none, so there is nothing for an older file to be warned of. (2) A `MAP` may go untagged
in a document that does declare tags, where the document states the correspondence and tags
nothing. No check ties the two. (3) §21 now says that a consumer reads the kind of change of
an untagged 1 to 1 `MAP` from its `TEXT` and, where the `TEXT` does not say, does not take it
for a rename. (4) §21 now says that a thing renamed, merged, removed or added is a `MAP` in a
document with no tags too, and that a renamed thing whose value also carries across takes
both the `MAP` and the `CONVERT … UNCHANGED INTO`.

*Not done.* No bridge is changed. The Pendragon bridge's renames, merges, omissions and
introductions are F41, which counts them; the measurement above named one merge and one
introduction, and the file holds four merges and three destination-only lines. The Ars Magica bridge has none: its three `UNCHANGED INTO` lines keep
one name on both sides, and its `MANUAL` lines concern values.

**Bullet 7, point 2, ruled 2026-11-16: `SCALE` states no rounding (DECISION-68).** The agent
proposed one sentence, that `SCALE` states the arithmetic and that a rounding the document
gives is written as a `MANUAL` line. Owner: "Most games have standard rules for how to handle
rounding; by default, we should defer to those procedures if they exist. Otherwise this is
something that can optionally be flagged as something of possible concern but would need
adjudication from some source if there were no default heuristics to use."

Measured for his rule, by a search of each corpus for a sentence that states a rounding
(`round up`, `rounded down`, `to the nearest`, `fractions are dropped` and the like; a
phrasing outside the pattern is not counted):

| Corpus | Sentences stating a rounding | A rule for the game as a whole |
|---|---|---|
| dnd5.5e | 52: 38 down, 13 up, 1 other | `^"Round Down"`, glossary, page 187: "Whenever you divide or multiply a number in the game, round down if you end up with a fraction, even if the fraction is one-half or greater." |
| pendragon6e | 26: 16 up, 9 nearest or other, 1 down | `^"Rounding Numbers"`, page 26: "Values and dice outcomes are always rounded to the nearest whole number." |
| arm5e, the 42 core files | 22, all up; each read, each for one calculation or an erratum to one | none found |
| dnd5e | 24: 13 down, 11 up | none found by the pattern; the sentences were not each read |
| pendragon5e | 5 | not looked for; it is an origin |

The three `SCALE` lines are all in the bridge whose destination is arm5e, so none of them has
a general rule to take. `SCALE 5` gives a whole number; `SCALE 6 OVER 5` and `SCALE 1 OVER 3`
can give a fraction.

- **`SCALE` states the arithmetic** and takes no rounding keyword.
- **The game's general rounding rule applies** where the game prints one.
- **Where it prints none**, the bridge supplies none; a reader may flag the conversion as one
  that wants a ruling from a source outside the bridge.

*Applied.* Spec: §0 item 55, DECISION-68, three paragraphs in §21 after the `CONVERT`
operations. The grammar gains a comment and no tool changes, since there is nothing new to parse
and no check.

*Agent's calls, to confirm.* (1) "The game" is the destination edition, since the result is a
value on a destination sheet. The owner said "most games" and named no side. (2) No field is
added for a system's general rounding rule, and the spec says that none exists and that a
reader finds the rule in the corpus as the book prints it. A tool therefore cannot tell
"prints a rule" from "prints none" unaided, and the flag he allowed is left to the reader;
the validator reports nothing. (3) The spec names arm5e as a destination with no general
rule, worded as "none was found". (4) What a bridge does when the conversion document itself
states a rounding is not written. None of the three source sentences states one, and the
agent's `MANUAL` proposal was not what he ruled.

**Bullet 8, measured 2026-11-16 and put to the owner in three points**: an empty name, a
name with no letter or digit, a control character in a name.

Counted with the validator's own tokenizer over the 22 corpus directories and the seven other
repos: 7,257 DSL files, 760,929 caret names written, 114,703 of them a DEF's name, 81,888
distinct. A name inside a string is not counted.

- **Empty.** 3, all in one file,
  `titterpig-dsl-dnd5e-3rdparty/historica-arcanum/the-serpentine-door/historica-serpentine-door-0.4-adventure.arc`,
  lines 71, 79 and 83. Each is a quote that is not escaped:
  `SCENE ^""They Are Here" — Frederick's Clandestine Meeting"`. The validator reads the name as
  empty and reports nothing on those lines; the grammar refuses the file. No name is blank
  (spaces only).
- **What the two gates say of a planted file** holding `^""`, `^" "`, `^","` and a name with
  U+0007 in it, each a DEF at 0.6: validator 0 errors and 0 warnings; grammar accepted.
- **No letter and no digit.** 9 distinct names, 15 written: 10 as a DEF's name and 5 as an
  entry's label. Read in place:

  | Name | Where | What it is |
  |---|---|---|
  | `^"—"` | tor2e `core-adventurers`, a table's `ENTRIES` | the row's own label; its `^"Skill"` is "Unskilled" |
  | `^"—"` | vtm5e `succubus-club-chapter-five` | a DEF whose description opens "Rudi, a local Gangrel Anarch" |
  | `^","` | arm5e and armdef `the-church … the-corrupt-demons` (the same nested DEF); invisiblesun `teratology` | a power with `^"Cost"` "*3 points"; a `^"Rule"` |
  | `^"&"`, `^"(  )"`, `^")"`, `^"<-"` | invisiblesun `teratology`, `the-nightside`, `enchiridion-of-the-path` | four `^"Rule"` DEFs |
  | `^":"` | vtm5e `children-of-the-blood-new-advantages` | a `^"Flaw"` |
  | `^"▪"` | vtm5e `gehenna-war-chapter-four`, twice | a guidance entry's label |
  | `^"“"`, `^"”"` | arm5e-3rdparty `a-vanilla-covenant`, three sidebars | a guidance entry's label |

  The tor2e row reads as what the book prints. The agent reads the other 14 as conversion
  slips; none was checked against its PDF.
- **A control character.** 10 names, 11 written, in tor2e `realms-days-darken` (9),
  `ruins-gathering-storm` (1) and `ruins-landmarks` (1): U+0007 after the year, `^"2973: ␇confrontation at the Black Lake"`.
- **Space.** 5 names are written with a space at one end and 1 with a run of spaces. §14 sets
  both aside when two names are compared, so nothing is put for them.
- **Length.** 70 distinct names are longer than 120 characters, 67 of them a DEF's: sentences
  used as names. Nothing is put for them.

**Bullet 8, ruled 2026-11-16: what a name holds (DECISION-69).** The agent put three points:
an empty name refused, a name with no letter and no digit warned of, a control character in a
name refused. Owner: "Yes, all three".

- **An empty name**, once white space is folded, is a warning below 0.6 and an error from 0.6.
- **A control character in a name** is gated the same way.
- **A name with no letter and no digit** is a warning at every version and never an error.

*Applied.* Spec: §0 item 56, DECISION-69, a new part of §14, "What a name holds". Validator:
the three checks, made where a caret name is read, so they cover a definition, a reference
and an entry's label in every kind of file. Grammar: a comment; the rule keeps `^""` so that
an older file is still read. New: `tests/nameform-good` and `tests/nameform-bad`.

| Check | Result |
|---|---|
| `tests/nameform-good` (punctuation beside a letter, one letter, one digit, a letter of another script, an escaped quote, a space at the end) | validator 0 errors, 0 warnings; grammar accepted |
| `tests/nameform-bad` | 4 errors and 7 warnings. At 0.6: two empty names, two names with U+0007 as errors, and four names with no letter and no digit as warnings. At 0.5: an empty name, U+0007 and `^":"`, each a warning. The validator before the change: 0 and 0 |
| the fixture run against the run after bullet 7 | identical, but for the two new sets and the grammar's count |
| both grammar gates | 81 of 81 good files accepted; 17 of 17 planted faults refused |
| the 29 directories, bullet 7's validator against this one | 22 identical. Seven gain 29 warnings and nothing else: 15 for a name with no letter and no digit, 3 for an empty name, 11 for a control character. They are the 15, 3 and 11 of the measurement. No error is added, since every file concerned declares a version below 0.6 |
| the 22 corpus directories, from that run | 288 errors and 30,225 warnings; 288 and 30,202 before, which is the sum the note under bullet 6 part 3 gave by arithmetic |

The seven: arm5e and armdef 1 each, invisiblesun 5, tor2e 12, vtm5e 4, arm5e-3rdparty 3,
dnd5e-3rdparty 3.

*Agent's calls, to confirm.* (1) One decision number for the three points. (2) A control
character is one of Unicode's category Cc. A tab or a line break in a name is white space
under §14 and is not reported; a format character (a zero-width space) is not reported
either. (3) The no-letter warning is made at a reference and an entry's label as well as at
a definition. (4) The grammar does not refuse `^""`. (5) Nothing waives the warning on a
name a book does print; the tor2e row keeps it.

*Not done.* No corpus is changed: F42. `check_references.py` and `check_constructs.py` are
unchanged; their own pattern for a caret name already skips an empty one.

### To revisit once C1 to C9 are closed

Asked for by the owner, 2026-11-14, while ruling C6 part 1: "I would like to follow up on the
following issues once we're done with the C# items".

- **§24, Optional & variant rules.** (He quoted the heading as the proposal had shown it,
  `## 24. Optional & variant rules *(provisional)*`.)
- **`ADD_TO`, `REMOVE_FROM`, `@n`, `.selections`.** The four forms C6 found that no file writes
  and that part 3 proposes to keep.

He gave the list and no more. What is to be decided about each is his to say when it is taken
up.

Part 3 of C6, ruled the same day, marked those four forms as likely to be replaced, and
`OVERRIDE` and `ADD … DEF` with them (DECISION-53). The replacements are not ruled.

Added 2026-11-14, while ruling C9's first bullet. Owner: "we should flag a follow-up so that a
campaign can declare appropriate systems/settings/etc to have all the necessary
primitives/select rule variants/etc. Probably a ".campaign" load file that tells how to build
the codex, etc, maybe? discussion for later."

- **A campaign's load file.** What a campaign loads: its systems and settings, the primitives
  those bring, the rule variants it selects. It touches `.selections` and §24 above, the
  synthesist's manifests (three of the 15 already compose a third-party book over a base), and
  where a third-party book's own files and keywords are declared.

Deferred by the owner while C9's fourth bullet was put to him, 2026-11-14: "I think we need
to defer a decision here, flag it for follow-up".

- **A hook's `WHEN`.** Whether it is the source's own sentence or the converter's wording, and
  how a hook points at the sentence it was drawn from. It goes with the replacements for
  `TRIGGER` and the two upper `FORMALITY` levels (DECISION-54). The proposal he deferred is
  under C9, bullet 4.

Asked for by the owner while ruling C9's sixth bullet, 2026-11-14: "Let's mark for a review
the idea of a parallel unique ID system in lore, but that's not immediately in scope."

- **A set of unique identifiers for lore, beside those of the mechanics.** DECISION-65 keeps
  the two identities apart and defines no link. What the review would touch: §25 lets a
  category, an `IS` and an edge's object name a game DEF; a codex entity's hash is drawn from
  the same space as a DEF's, and a hash shared between the two is an error; DECISION-24 makes
  an entity's name one that any file may use.

Deferred by the owner while the fourth part of C9's sixth bullet was put to him, 2026-11-14:
"defer decision on this."

- **A date or a number as a fact in a codex.** Whether an edge's object may be a value. The
  two options he deferred are under C9, bullet 6, part 4.

Recorded from C9's recount, 2026-11-14: bullets 5 (`OPTIONAL` and `.selections`) and 9 (`ADD`)
of C9, and what is left of bullet 2 (what `MODIFY` cannot reach, which today takes a whole
`OVERRIDE`), wait on the items of this list.

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
| 7 | Mark unused constructs provisional until a corpus and a consumer use them. *Not taken: C6 part 1, 2026-11-14.* | C6 | none for corpora |

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

**Added from A3 (2026-11-12).**

- **Define the setting.** Owner, 2026-11-12: l5r5e core should define the setting as Rokugan. It
  does not: the corpus has no `SETTING` container, no `.setting` file and no `USES_SETTING`. Nine
  arcs carry a free-text line instead (`SETTING "Tsuma, a small Crane fishing town, during the
  three days of the Topaz Championship"`), which uses the container's keyword for a where-and-when
  string.
- **The Lost Writer arc** (`l5r5e-0.5-children-of-five-winds-lost-writer.arc`), which §16 now
  shows in corrected form:
  - all three `OPPONENTS` references point at hashes declared nowhere
    (`#kaeru_haya_60be37c72620`, `#shinjo_higuchi_df4e0cc491ff`, `#adventure_ifrit_d9edc116c2e9`);
  - `^"Miya Tetsua"` and `^"Adventure Ifrit"` are defined in the arc and again in the GM file under
    other hashes; the arc should import them with `FROM EXTENSION "L5R5e_Children_of_Five_Winds_GM"`;
  - its cast is attached with `APPLIES TO [ ^"NPC" ]` where the GM file writes `EXTENDS ^"NPC"`;
  - two `OPTIONAL` objectives are written twice in "The Possessed Author".
- **Skills as a property.** NPCs hold `^"Skills" LIST OF STRING ["Artisan 3", "Martial 2", …]`, and
  three actor types in `l5r5e-0.5-core-base.ttrpg` declare `^"Skills" LIST OF ^"Skill"`. Both become
  a keyed block (`^"Skills" DEF { ^"Artisan" INTEGER 3 … }`), declared on the type. The `^"NPC"`
  type declares no properties today.
- **To-do from A7 (owner, 2026-11-12): move `^"Historical Persona"` out of the actor file.**
  `l5r5e-0.5-blood-of-the-lioness-pregens.actor` declares the type
  `#t84d75db874b40237553ca ^"Historical Persona"` (line 24) and six instances of it. An `.actor`
  holds instances only (DECISION-28), so the type goes to a `.ttrpg` the file depends on. The
  validator warns today, and will fail the file once it declares `SPEC_VERSION "0.6"`.
- **14 arcs and frames** open with `ARC "id" EXTENDS "l5r5e" {` and have no `DEPENDS_ON`.

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

### F6. Corpora: move dice out of strings

**From:** A1, DECISION-18. **Status:** open, not started.

3,251 short `STRING` property values in 13 corpora hold a dice expression: callofcthulhu7e 984,
daggerheart 696, pendragon6e 522, dnd5.5e 447, dnd5e 379, pendragon5e 174, and seven smaller. Each
becomes a `ROLL n OF ^"die"` with `TRANSFORM`, `SET` and `REF` steps (§8). Each system's BASE
declares `DEPENDS_ON "Titterpig_Dice"` and its `gates.sh` passes `modules/0.6/`. A system whose
book prints `D6` may `ALIAS` the module's die or define its own.

l5r5e (with F1): `^"Ring Die"` and `^"Skill Die"` already hold `FACES` blocks and need
`EXTENDS ^"Die"`; 7 `ROLL "1d10"` / `ROLL "d100"` lines become `ROLL 1 OF`.

**To-do (owner, 2026-11-11): the Blank face is a DEF.** l5r5e writes the blank face as the string
`"Blank"`. It should be an entity, as Opportunity is, because other rules name it (Inversions and
similar). The faces then read `1 #hash ^"Blank"`. The same applies to the other symbols the dice
show (`(op)`, `(su)`, `(st)`, `(ex)`), which are strings today.

The synthesist (F3) needs `FACES`, `ROLL` and `NEXT`.

### F7. Eight corpora: move Markdown emphasis out of strings

**From:** A2, DECISION-19. **Status:** open, not started.

vtm5e, arm5e (and armdef by retarget), tor2e, daggerheart, draw-steel, dnd5.5e, dnd5e and troika
write `**bold**` and `*italic*` inside strings: about 5,500 strings with bold and 7,600 with
italic. Each marked span becomes an entry in an `EMPHASIS BOLD`, `EMPHASIS ITALIC` or
`EMPHASIS BOLD ITALIC` block beside the string, and each run-in label (2,273 of the bold spans by
position) an entry in a `LABEL` block. vtm5e and tor2e are generated, so the change is made in
their generators.

- The validator now reports them (counted 2026-11-12): 11,566 strings flagged, all as warnings
  because every corpus declares a version below 0.6. vtm5e 4,143, arm5e 2,525, tor2e 1,516,
  dnd5.5e 1,154, dnd5e 816, daggerheart 624, draw-steel 563, troika 216, invisiblesun 5, root 4.
  armdef mirrors arm5e with 2,618 more. Each becomes an error when its file declares 0.6. root's 4
  and invisiblesun's 5 are leftovers in corpora that otherwise record emphasis beside the text.
- The 1,305 paragraphs and strings set wholly in italic have nowhere to go yet (to-do below).
- The asterisks a book prints stay: arm5e's footnote marks, pendragon6e's `Chirurgery 20*`.
- The vtm5e VTT turns `**…**` into bold on screen (`system/vtm5e/entity.js:31`,
  `engine/gm-text.js:41`). It has to read `EMPHASIS` before its corpus loses the markers. The other
  VTTs were not checked.
- The synthesist has no code that names `EMPHASIS`; consumers find the blocks under an entity's
  generic `blocks`. It needs the kind and `LABEL` with its depth (add to F3). Its `GUIDANCE` parser
  does not accept `EMPHASIS` inside an `ENTRY` (recorded 2026-11-02 for mythic-gme2).

### F11. Corpora: name the kind on every `FROM`

**From:** A3, DECISION-22. **Status:** open, not started. The validator now reports these.

18 `FROM "id"` lines name no kind: callofcthulhu7e 13, curseborne 2, teeth 2, tor2e 1. Each is a
warning today and an error once its file declares 0.6. Three of them name a container that is not
in their corpus and are errors now: curseborne's `Curseborne_Wolf_You_Feed_NPCs` and
`Curseborne_Wolf_You_Feed_Adversaries`, and tor2e's `tor2e-adversaries`
(`tor2e-0.5-core-star-of-the-mist.arc:16`). curseborne goes from 0 errors to 2 and tor2e from 0 to 1.

### F13. arm5e and l5r5e: what the two tiers now report

**From:** A4, DECISION-24. **Status:** open, not started. Both tools now fail these.

- **arm5e (and armdef): 4 errors.** Four hashes each sit on two or three different sidebar
  entries: `#t1ed6d9b1394ac006d6d3be` on "New Virtues (Mythic Islam)", "New Virtues (Mythic
  Judaism)" and "New Virtues (Realms of Power: The Divine)"; `#t040be207d050bed657aca4` on the
  three "New Flaws" entries; `#tbfbaa4c8f66731c72ab45c` on two "New Abilities" entries;
  `#t8dd814b6b5cd82a1b96418` on two "New Shape and Material Bonuses" entries. Two more hashes are
  written twice in one file on the same name (`ENTRY ^"sidebar on page 15"`), which is not an
  error and wants a look.
- **l5r5e: 10 errors in the validator.** Every one is an `OPPONENTS` reference to a hash declared
  nowhere, in two arcs (the Lost Writer's three, and `#azif_9fc007a20ec3`, `#yaguro_b9b70348c102`,
  `#yumiko_81f780d897df` and `#gaku_f6b1b6e5d2c8` elsewhere). The validator goes from 17 errors to
  27. The reference gate gains one: an embedded `^"Mahō"` is now ambiguous, because the name is
  both a DEF and a codex entity.
- **callofcthulhu7e: resolved by DECISION-25.** Its one new error was an import of a DEF named
  `^"Mrinmoy \"Vidyapati\" Mishra"`, which neither tool could see until a caret name was allowed
  an escaped quote. It is back to 0 errors.

### F14. arm5e: the retarget writes an `ORIGIN` line into every ported file

**From:** A5, DECISION-26. **Status:** open, not started. Nothing fails today: a port with no
declaration cannot be told from any other file.

- `retarget_armdef.py` adds `ORIGIN "arm5e" <KIND> "<the arm5e file's id>"` to the header of each
  file it generates: 2,390 files (2,372 `EXTENSION`, 18 `SETTING`). `verify_armdef.py` strips that
  line as it strips the other structural rewrites.
- `armdef-grogs-0.5-aging-subtype.ttrpg` has no arm5e source and declares nothing.
- armdef's gate then passes `--corpus arm5e=…/arm5e/0.5` to the validator, or the run carries one
  warning that 2,390 ports were not checked. The scratch run above took the corpus and found no
  fault.
- The line needs `SPEC_VERSION "0.6"` to be honest about the spec it follows. The validator reads
  it at any version.

### F15. invisiblesun and root: re-mint so the two corpora share no hash

**From:** A5. **Status:** open, not started. Added at the owner's request on 2026-11-12: "fi[x]
invisiblesun and root's hashes to be unique/distinct".

- `invisiblesun/0.5` and `root/0.5` have 1,508 DEF hashes in common. None carries the same name
  in both, so the two were minted alike by accident. They sit in 9 invisiblesun files and 6 root
  files.
- Neither tool reports it: under DECISION-26 a hash two editions share outside a port has no
  meaning and is legal. The owner wants them distinct all the same.
- One side re-mints its 1,508 and every reference to them. root is the smaller corpus (2,695
  hashed DEFs against 10,553). Which side changes is the owner's call, and so is what happens to
  anything outside the corpus that cites the old hashes. UNVERIFIED: I have not looked for such
  consumers, or for how the two came to match.
- Done when a recount of the 22 corpus directories shows arm5e and armdef as the only pair with a
  hash in common.

### F16. synthesist and six corpora: stop the name match, and triage the pairs it merged

**From:** A6, DECISION-27. **Status:** open, not started. The synthesist still replaces an earlier
DEF with a later one of the same name, so every built JSON still carries the merges.

- **synthesist.** `register` in `internal/resolve/collect.go` stops replacing on a name match: a
  DEF whose hash is new becomes its own entity. The hash match goes too, since a second DEF under
  a declared hash is now an error upstream. `type_equivalence` in the five arm5e and armdef
  manifests, `typesCompatible`, and the README's "matched by hash then name" go with them.
  `--collect` should keep listing same-name DEFs, since that list is the triage.
- **Triage, per composition** (entities merged today): arm5e-0.5-full 114, armdef-0.5-full 125,
  callofcthulhu7e-0.5 18, dnd5.5e-0.5 13, l5r5e-0.5 6, tor2e-0.5 25. Each pair is one of two
  things.
  - One entity written twice (l5r5e's `^"Daidoji Shin"`, short in one file and full in another):
    keep one DEF and make the other a `REPRINT`, an `ALIAS` or a `MODIFY`.
  - Two entities of one name (tor2e's core `^"Combat"` and Strider Mode's heading; arm5e's
    `ACTOR "Magus"` and the rules entry `^"Magus"`): both stay, and every reference to the name
    carries a hash.
- **Order.** Triage a composition before its JSON is rebuilt without the name match. Rebuilt
  first, a pair meant as one entity arrives as two.
- **What consumers see.** tor2e's JSON regains the core Combat chapter. Every composition gains
  entities, and a consumer that looks an entity up by name finds two where it found one.
  UNVERIFIED: which consumers look up by name.
- arm5e sourcebook pairs are fixed in `arm5e/0.5` and reach armdef through the retarget.

### F17. Seven corpora: give 670 bare `.actor` files the `EXTENSION` wrapper

**From:** A7, DECISION-28. **Status:** open, not started. The validator warns on each.

- tor2e 311, marvelmultiverse 211, aegean 50, troika 36, coyotecrow 31, root 24, curseborne 7.
- Each file gains `EXTENSION "<id>" EXTENDS "<the system's base id>" {`, a `NAME`, a `VERSION`,
  a `SPEC_VERSION` and a `RELEASE_DATE`, and its DEF moves inside. The file's leading
  `# source:` comment stays with the DEF. pendragon6e's actor files are the model.
- The ids are new and must be unique in the corpus. A file that already depends on a sourcebook
  file names it with `DEPENDS_ON`.
- tor2e's and troika's synthesist manifests list these files by name (311 and 36). The file
  names do not change. UNVERIFIED: that every consumer of a bare file reads a wrapped one. The
  synthesist does, for arm5e.
- Done when the validator gives no bare-file warning in any of the seven.

### F18. draw-steel: a DEF's prose becomes `DESCRIPTION`

**From:** A8, DECISION-30. **Status:** open, not started. The validator warns on each.

- 3,513 statements in `titterpig-dsl-draw-steel/0.5` write `TEXT "…"` directly in a DEF. Each
  becomes `DESCRIPTION "…"`. The string does not change, so the verbatim text is untouched.
- `TEXT` inside an `ENTRY`, an `OPTIONAL` block or a system block stays.
- 32 DEFs in the corpus already hold a `DESCRIPTION`. UNVERIFIED: whether any DEF would end up
  with two after the rename. None holds both today.
- Done when the validator gives no "TEXT directly in a DEF" finding there.

### F19. Corpora: what the grammar still refuses

**From:** B1, DECISION-31. **Status:** open, not started. No gate runs on the corpora yet:
1,898 of 7,055 corpus files are refused. Each file is counted once, by the first thing the grammar could not
read, so a file may hold further forms behind that one.

| Files | What stands at the refusal | Where | What it needs |
|---|---|---|---|
| 665 | a file that opens with a bare DEF | tor2e 311, marvelmultiverse 211, aegean 50, troika 36 | F17 wraps them |
| 580 | a string and a number as a pair: `"Hungry" +6` | arm5e 290, armdef 290 | a ruling: the spec has no such pair, and no `+` on an integer |
| 368 | an unnamed `DEF { … }` as an item of a list | pendragon6e 194, pendragon5e 103, teeth 36, aegean 19 | a ruling: the spec has no such item |
| 47 | `^"Level" ENUM "Chapter"`: an `ENUM` with one value and no list | invisiblesun 13, callofcthulhu7e 10, mythic-gme2 8, tor2e 6 | a ruling: §8 gives `ENUM` a bracket list only |
| 41 | an `EMPHASIS` block inside a guidance `ENTRY` | pendragon6e 34, marvelmultiverse 7 | a ruling: §22 gives an entry `CONCERNS`, `TOPICS` and `TEXT` |
| 32 | `BASE 3` as a system's field | arm5e 16, armdef 16 | a ruling, or a rename: `BASE` is reserved everywhere |
| 30 | a hash before the keyword: `#hash ENTRY ^"…" {` | callofcthulhu7e | a corpus fix |
| 29 | a name and a bare reference: `^"Attribute" ^"Attribute"` | teeth 16, daggerheart 6 | `REF` (DECISION-17) |
| 19 | an unquoted word in a list: `[kata]` | l5r5e | a corpus fix |
| 87 | other, each on a few files | arm5e, armdef, l5r5e, curseborne | among them `LIST OF [` with no type (11), `ALIAS "…"` with no `FOR` (4), `CHOICE` (6) |

- A corpus's `gates.sh` can run `check_grammar.py` once its own count is zero.
- The four rulings belong with C5 (in heavy use and not in the spec).
- 2026-11-13, DECISION-51: the `EMPHASIS`-in-`ENTRY` row is ruled legal, and its files are
  accepted. The `BASE 3` row is ruled: `BASE` stays reserved and arm5e renames (F5). With
  DECISION-51's grammar 1,492 of 7,055 files are refused.
- 2026-11-13, DECISION-40: the `"Hungry" +6` row is ruled. It is a `SET` or a `TRANSFORM`,
  decided in conversion (F26). DECISION-41: the unnamed `DEF { … }` row is ruled legal, and
  the grammar accepts it: 351 of that row's 368 files are now accepted, and 1,544 of 7,055
  are refused in all. The other 17 stop at a further form.
- 2026-11-13, DECISION-39: the `ENUM "Chapter"` row is ruled. From 0.6 the value is written
  alone, `^"Level" "Chapter"`. The counts above are from B1 and were not retaken. With
  DECISION-39's grammar 1,895 files are refused, three fewer.

### F20. Seven corpora: what the value checks now report

**From:** B2, DECISION-32. **Status:** open, not started. All are warnings today, in files that
declare `SPEC_VERSION "0.5"`. Each becomes an error when its file declares 0.6.

| Corpus | New warnings | What |
|---|---|---|
| armdef | 306 | as arm5e |
| arm5e | 301 | 205 values written `STRING` where the type declares `INTEGER` (`^"Soak" STRING "+21 (hardened bronze statue)"`); 63 values outside an `ENUM` (`^"Magnitude"` "Major/Minor"); 33 properties written twice |
| l5r5e | 118 | hashes with an underscore; F2 replaces them |
| draw-steel | 74 | 50 values outside an `ENUM` (`^"Action Type"` "Triggered"; the list has "Triggered action"); 22 type mismatches; 2 out of range (Ajax the Invincible is `Level 11`) |
| curseborne | 14 | members of a `LIST OF ^"Being a Ghost"` that do not extend it |
| teeth | 1 | `^"Tallow candle"` in a `LIST OF ^"Courtier Item"` |
| daggerheart | 1 | a `^"Complexity Rating"` of 4 where the type says 1 to 3 |

- For each: fix the value, widen the type's declaration, or mark it `FIAT "reason"` where the
  book prints it so. Which of the three is a call on the source, entry by entry.
- 2026-11-13, DECISION-39: the type mismatches are no longer findings. That removes 432 of
  the warnings above: arm5e 205, armdef 205, draw-steel 22.
- arm5e's are fixed in `arm5e/0.5` and reach armdef through the retarget.

### F21. callofcthulhu7e, l5r5e and the synthesist: follow the one name rule

**From:** B3, DECISION-33. **Status:** open, not started. The two corpora's gates fail on these
today.

- **callofcthulhu7e, 4 references**, each reported by `check_references.py` and by
  `check_constructs.py`. Each `CONCERNS` line gives a hash and a name that is not the anchor's:
  - `keeper-ch4-skills-pushing.ttrpg:246`: `^"PILOT"`, and the anchor is `^"Pilot"`.
  - `keeper-ch7-chases.ttrpg:511`: `^"Key"`, and the anchor is `^"Key:"`.
  - `keeper-ch3-creating.ttrpg:562` and `:567`: `^"When crafting background entries, be
    specific, emotional and emphatic"`, and the anchor capitalises the title and has a comma
    after "Emotional".
- **l5r5e, 1 reference.** `writ-of-wilds-mechanics.ttrpg:895` embeds `^"Tent [Small]"`; the
  definition is `^"Tent (Small)"`.
- **synthesist.** It compares names exactly. Under DECISION-33 it folds Unicode form, white
  space and quote style first. UNVERIFIED: whether any composition changes; the validator's
  output did not change in any corpus when it took the rule.

### F22. Four corpora, and every `ACTOR` type: what `REQUIRED` now reports

**From:** B4, DECISION-34. **Status:** open, not started. All are warnings today, in files that
declare `SPEC_VERSION "0.5"`.

| Corpus | Instances reported | Mostly |
|---|---|---|
| armdef | 196 | `^"Laboratory Virtue".^"Category"` 70 and `^"Laboratory Flaw".^"Category"` 64 (*Covenants*' entries carry `^"Group"`); `^"Ability".^"Ability Type"` 31; `^"Hermetic Form".^"Abbreviation"` 10 |
| arm5e | 55 | `^"Ability".^"Ability Type"` 31 (sourcebook abilities with a source and a page and nothing else); `^"Virtue".^"Category"` 10 |
| l5r5e | 41 | `^"School".^"Clan"` 27 (*Path of Waves* traditions belong to no clan); `^"Samurai"`'s `^"School"` 8, `^"Clan"` 7 and `^"Family"` 7 |
| draw-steel | 10 | the ten classes, which extend `^"Hero"` and so owe `^"Ancestry"`, `^"Class"` and `^"Kit"` |

- **Each finding is one of three things.** The conversion dropped a field the book gives: add
  it. The type requires what not every entry has: drop `REQUIRED` from the declaration. The book
  prints this one entry without it: an element-level `FIAT "reason"`.
- **Review the 53 `REQUIRED` declarations on `ACTOR` types.** One that states a rule of
  character creation (`^"Samurai"`: `^"Clan"`, `^"Family"`, `^"School"`; `^"Hero"`:
  `^"Ancestry"`, `^"Class"`, `^"Kit"`; `^"Magus"`: `^"House"`) loses the word, and the rule is
  written as a `CHOOSE` in the creation procedure if it is not there already.
- **The 239 `^"Name" … REQUIRED` declarations may stay.** The DEF's name answers each.
- arm5e's are fixed in `arm5e/0.5` and reach armdef through the retarget. armdef's own 126
  (the laboratory categories and the abbreviations) come from the Definitive core's types.
- 2026-11-13, DECISION-42: 12 more warnings, for DEFs that something extends (vtm5e 3,
  teeth 4, arm5e 2, armdef 2, l5r5e 1). C2 lists them. Eleven are subtypes that declare
  nothing, and each takes an element-level `FIAT` or a declared field; l5r5e's
  `^"Treasure Hunter"` is a school with no `^"Clan"`.

### F23. Five corpora and two manifests: what the dependency rules report

**From:** B5, DECISION-36 and DECISION-37. **Status:** open, not started. The corpus findings
are warnings today, in files that declare `SPEC_VERSION "0.5"`.

| Where | Findings | What |
|---|---|---|
| l5r5e | 16 | 14 arcs and frames open `… EXTENDS "l5r5e"`, and no file declares that id (F1 has this too); 2 cast files are extensions with no parent |
| teeth | 11 | header `EXTENDS` that name an id no file declares |
| armdef | 8 | 5 errata files with no parent; 3 files declared `BASE` that depend on `ARMDef_Core_Base` (`armdef-0.5-core-character-creation.ttrpg`, `armdef-0.5-core-concepts.ttrpg`, `armdef-0.5-sourcebook-compat.ttrpg`) |
| arm5e | 5 | errata files with no parent (`arm5e-errata-0.5-apprentices.ttrpg`) |
| root | 4 | an id declared by an `.arc` and a `.frame` (`"PellenickyGlade"`, `"HacksawDell"`) |

- **synthesist manifests.** `armdef-0.5-full` lists 18 files before a file they depend on, and
  `arm5e-0.5-full` lists 1 (`arm5e-covenants-0.5-example-laboratories.ttrpg` before
  `arm5e-covenants-0.5-laboratory.ttrpg`). Reorder them. The synthesist can check the rule
  itself when it loads a manifest: it has the order and the files.
- UNVERIFIED: whether any of the 19 changes a built JSON. Order decides something only where
  two files change the same thing.

### F24. The corpora: values that differ by situation, still in strings

**From:** C1, DECISION-38. **Status:** open, not started.

9,709 string values give a number and then qualify it (arm5e and armdef 7,280, vtm5e 838,
callofcthulhu7e 504). They have not been sorted by kind. Sort them first:

| Kind | Example | Form |
|---|---|---|
| a value that differs by situation | tor2e `^"Injury"` `"16 (1h)/18 (2h)"` | a value and a `SITUATIONAL` block |
| a change with a limit | l5r5e `^"Status Award"` `"+5 (to a minimum of 20)"` | `TRANSFORM ADD 5 MIN 20` |
| an alternative | draw-steel `^"Size"` `"2 or 3"` | none ruled |
| a number and a unit; a list of thresholds | arm5e `^"Wound Penalties"` | none ruled |

- coyotecrow's stat lines print a changed value with no condition (`^"Physical Defense"`
  `"6(8)"`). `SITUATIONAL` needs a condition, so the converter finds it in the book or the
  value stays a string.
- UNVERIFIED: how many of the 9,709 are of the first kind.
- The generators under `Titterpig/Temp` write these strings; the change belongs there for a
  generated corpus.

### F30. A check that hashes hold within a major version

**From:** C5 part 6, DECISION-50. **Status:** open, not started.

- **The check.** Given two states of one content-version directory, report each entity whose
  hash differs. The validator sees one state and cannot do it. The comparison made for the
  audit matched DEFs by name, which misses a renamed entity; a check needs the generator's
  own record of which entity is which.
- **Generators that mint from the path.** tor2e's hash is the SHA-1 of the entity's path, so
  a rename or a move mints a new one. Under the rule the generator carries the old hash
  forward. UNVERIFIED: how the other generators mint.
- **vtm5e.** A re-conversion inside `0.5/` replaced 1,025 of 1,026 hashes between 2026-09-13
  and today. Anything saved against the earlier hashes points at nothing.

### F29. Six corpora and two bridges: longer text as one string

**From:** C5 part 4, DECISION-48. **Status:** open, not started. Owner, 2026-11-13: "we should
ultimately convert the other approaches over." All are warnings today.

| What | Count | Where |
|---|---|---|
| a triple-quoted block | 1,897 | draw-steel 1,889, callofcthulhu7e 3, daggerheart 2, dnd5.5e 1, dnd5e 1, root 1 |
| the same, in this repo's bridges | 96 | `dnd5e-to-dnd5.5e` 85, `arm4-to-arm5e` 11 |
| a single-quoted string over a raw line break | 93 | arm5e 46 (four True Lineages spell files), armdef 46, draw-steel 1 |

- Each becomes one single-quoted string: `\n\n` between paragraphs, `\n` for a line break kept
  inside one, `\"` for a quote.
- **Indentation.** 580 of the triple-quoted blocks have every line indented. Whether that
  indent is the text's or the file's layout is decided when each is converted; draw-steel
  writes 1,283 blocks at the margin to keep indent out.
- **Backslashes.** A triple-quoted block reads no escapes, so a backslash in one becomes
  `\\` in the single-quoted string. draw-steel's blocks hold 11.
- draw-steel is generated: the change is made in its generator.
- **l5r5e's strings in a row.** 413 runs of bare strings sit in `EFFECT`, `OPPORTUNITIES` and
  like blocks. They are legal as separate entries. Where a run is the paragraphs of one text,
  it is one string by this decision; which runs are is a call on the source.

### F28. The corpora and their generators: the page as `^"Page"`

**From:** C4, DECISION-45. **Status:** open, not started. Nothing fails: no tool checks it.

| What | Count | Where |
|---|---|---|
| a page in a comment (`# source: chapter opening (page 243)`) | 40,672 lines | vtm5e 12,202, invisiblesun 4,704, pendragon6e 4,410, tor2e 3,146, callofcthulhu7e 2,605, pendragon5e 2,085, marvelmultiverse 1,959, root 1,655, daggerheart 1,592, dnd5.5e 1,429, teeth 1,334 |
| `^"Pages"` to rename | 1,916 | pendragon6e 827, pendragon5e 764, coyotecrow 176, marvelmultiverse 149 |
| `^"Source Page"` to rename | 42 | l5r5e; `titterpig-doublecheck/scripts/errata_gen.py` and the dashboard's l5r5e errata overlay read this name |
| the book repeated on each entity (`^"Source"`, `^"Book"`) | 31,619 | arm5e, armdef, invisiblesun, root |

- The comments are written by the conversion generators. The change is made there: the
  generator writes `^"Page"` on the DEF and may keep the comment as a note.
- A `# source:` comment also says what kind of unit it came from ("adversary stat block",
  "chapter opening"). That part has no property and stays a comment.
- Whether the per-entity book properties go is each corpus's call. Nothing in the spec asks
  for them or forbids them.

### F27. Five corpora: what the new reference checks report

**From:** C3, DECISION-44. **Status:** open, not started. All are warnings today, in files that
declare `SPEC_VERSION` below 0.6. Each but the first becomes an error when its file declares
0.6.

| Corpus | Warnings | What to do |
|---|---|---|
| curseborne | 194 | add the hash to each list member; every name resolves to one entity |
| armdef | 169 | 141 as curseborne; 28 names that several entities carry need the hash chosen. Fix in arm5e where the list comes from arm5e, then retarget |
| root | 48 | 40 as curseborne; 6 names that name nothing (`^"Blinside"` is `^"Blindside"`); 2 DEF names with an unescaped quote in `sundew-bend.frame` |
| daggerheart | 26 | as curseborne |
| teeth | 15 | 12 list members carry a hash no DEF has (`^"Dogmaker and Vulpids"`), 3 a hash that belongs to another name. The entities are missing or the hashes are stale |

- The hash for a name that resolves to one entity can be added by script.
- **Hashless references in system blocks.** 1,264 names after a system keyword or alone in a
  system block name one entity and carry no hash (arm5e and armdef `VIRTUES` and `FLAWS`,
  l5r5e `KATA`, `SHUJI`, `RITUAL` and `RANK`). Nothing resolves them until they carry it.
  l5r5e's `RANK` and `FAMILIES` blocks hold 109 names that name nothing.

### F26. The corpora: signed numbers and names with numbers become `SET` or `TRANSFORM`

**From:** C1, DECISION-40. **Status:** open, not started. Owner, 2026-11-13: "This will likely
be an adjudication process as part of the conversion."

| What | Count | Where |
|---|---|---|
| a signed number in a string (`^"Initiative" STRING "+5"`) | 5,865 values, 251 list items | armdef 2,025, arm5e 1,941, marvelmultiverse 1,512 |
| a string and a signed number on a line (`"Convivial" +3`) | 2,581 lines | armdef 1,340, arm5e 1,241; 580 files refused by the grammar |
| a signed number and a string (`+2 "Voice"`) | 1,754 lines | armdef 884, arm5e 870 (F5) |
| an entity's name and a number in one string (`"Artisan 0"`) | 1,116 values, 723 list items | pendragon6e 383, marvelmultiverse 351; l5r5e 637 list items |

- Each is a `SET` (the value is the number) or a `TRANSFORM` (a value changes by it). The call
  is on the source, entry by entry.
- A change's target is a reference or a `CHOOSE` (§8). `"Convivial"` is a string and no entity
  of that name exists in arm5e. Whether such a trait becomes an entity or stays as written is
  part of the adjudication, and is not ruled.
- Until an entry is decided it stays a string as printed. The 2,581 and 1,754 bare lines are
  not strings today and are refused by the grammar as they stand.

### F25. Every corpus, its generators and its consumers: the type keywords

**From:** C1, DECISION-39. **Status:** open, not started. Nothing fails today: every corpus
declares `SPEC_VERSION` below 0.6, where the keywords stay legal and unreported. A file that
moves to 0.6 must drop them.

| What | Size |
|---|---|
| corpus lines where `STRING`, `INTEGER` or `BOOLEAN` stands before a value | 371,111 |
| `ENUM` before a single value | 10,601 (invisiblesun 7,497, root 1,654) |
| `LIST` before a list | 9,393 |
| `LIST OF STRING` with items | 21,228 |
| declarations: a keyword alone 2,204; with modifiers 1,923; `LIST OF STRING` alone 339 | 4,466 |
| `OF STRING` in `PARAMETERS` | 94 (arm5e 43, armdef 42, callofcthulhu7e 9) |
| bare constraints in a DEF's body (`INTEGER MIN 1`) | 58 |
| conversion scripts under `Titterpig/Temp` that write the keywords | 504 |

- The rewrite is mechanical: delete the word. The script used on this repo's fixtures and on
  the spec's examples is not in any repo. It reads a file's `SPEC_VERSION` and rewrites code
  only, never a string or a comment.
- A generated corpus is changed in its generator, and armdef through the retarget.
- teeth has 88 entries that give a value as `ENUM ["Wealthy Estates"]`, a declaration with one
  allowed value. Each is a value and should be written as one.
- Eight corpora write `^"Class" ^"Class"` in a `PROPERTIES` block for a property and its type.
  The form is `REF OF ^"Class"` (DECISION-17; F19 has 29 files refused on it).
- **The synthesist's resolved JSON** gives each property a `"type"`. With no keyword it can
  take the type from the literal. UNVERIFIED: which consumers act on that field.

### F12. Seven corpora: scene and conflict types become entities

**From:** A3, DECISION-23. **Status:** open, not started. The validator now reports these.

483 `TYPE "…"` strings sit in `SCENE` and `CONFLICT` blocks (478 and 5): tor2e 181,
callofcthulhu7e 143, draw-steel 60, teeth 54, l5r5e 21, curseborne 14, vtm5e 10. armdef has 5
more. Each is a warning today and an error once its file declares 0.6. Each system's BASE defines
`^"Scene Type"` and its scene types, and `^"Conflict Type"` where it has conflicts, and each
string becomes `TYPE #hash ^"Name"`. The values in use are Roleplay 293, Combat 86,
Investigation 32, Exploration 28, Travel 26, Intrigue 11 and Montage 2; all 181 of tor2e's are
Roleplay, which its generator writes for every scene.

**Added 2026-11-12, from the smaller §16 fixes:**

- curseborne's one `MODIFICATIONS` block holds `entanglement DEFAULT 1`, `held_curse_dice DEFAULT 1`
  and `maximum_curse_dice DEFAULT 5`: lowercase words that point by spelling at real properties.
  Each becomes `#hash ^"Entanglement" SET 1`.
- 14 `RULE ^"Name" ADDS_TO PARENT { DESCRIPTION "…" }` blocks in four frames (curseborne 5, l5r5e
  9) become §12 rules. l5r5e's nine are named "Hook", "Rising Action" and the like and hold
  adventure-seed prose, so they are `ENTRY` blocks and not rules.

### F9. Corpora: move tables into `TABLE` blocks

**From:** A2, DECISION-21. **Status:** open, not started. Nothing forces it until a file declares
`SPEC_VERSION "0.6"`.

No corpus uses the primitive. What exists today (counted 2026-11-12, armdef left out):

- 973 `TABLE { COLUMNS [ … ] ROW [ … ] }` grids of strings, 12,384 rows, in 13 corpora (tor2e 269,
  vtm5e 172, callofcthulhu7e 130, dnd5.5e 109, dnd5e 85, mythic-gme2 75). 397 are roll lookups
  whose first column is a range in a string, and become a roll axis with `AT` cells. The rest are
  tables of records or printed layouts and need a type before they can be a `COLUMNS` table.
- 667 arm5e `TABLE { "Light" "1 Fatigue level" }` blocks of string pairs.
- 6,507 Pendragon `^"Table Row"` DEFs holding `^"Cells" LIST OF STRING`.
- mythic-gme2's 162 `^"Fate Chart Cell"` DEFs, which already hold their coordinates as properties
  and convert directly.
- l5r5e's roll-keyed blocks (164 keyed lines, 30 `SUB_TABLE`), teeth's 473 `^"Roll Table Entry"`,
  aegean's and mythic-gme2's 60 `^"Roll Result"`, daggerheart's 21 `ROLL_TABLE`.

The synthesist needs `TABLE` (add to F3).

### F10. l5r5e and armdef: embedded references that resolve to nothing, or to more than one entity

**From:** A2, DECISION-20. **Status:** open, not started. Both tools now fail these.

l5r5e holds 420 embedded references. The validator reports 14 as undefined (10 names:
`Shadowlands Taint` 4, `Otherworldly` 2, eight more once each), taking the corpus from 3 errors to
17. `check_references.py` reports 29 errors: 13 unresolved, and 16 hashless references to a name
with more than one anchor (`Compromised` 9, `Games` 2, `Righteousness (Gi)` 2, `Strike` 2,
`Sixth Sense` 1). The other 391 are hashless and WARN. armdef holds 4, one unresolved
(`^"Hermetic Art"`, `armdef-0.5-core-concepts.ttrpg:101`).

The synthesist should emit each embedded reference as a link (add to F3).

### F8. draw-steel: Markdown passages inside strings

**From:** A2. **Repo:** `titterpig-dsl-draw-steel`. **Status:** open, not started. Its tables can
now be written as `TABLE` blocks (F9).

The source is Markdown, and the strings hold it whole: 285 strings with tables (1,447 rows), 338
with `####` headings, 68 with links, 871 `- ` list lines. One caret name is 1,317 characters long
and holds an entire ability (`draw-steel-0.5-core-ancestries.ttrpg:388`).

### F5. arm5e: spell magnitudes, derived level, and Range / Duration / Target as entities

**From:** A1. **Repo:** `titterpig-dsl-arm5e` (and armdef by retarget). **Status:** open, not started.

Owner, 2026-11-11: track both a spell's magnitudes and its level, the level derived from the
magnitudes; the rule is more complex than five levels a magnitude. Each Range, Duration and Target
becomes an entity that carries its change to the spell's magnitudes, and a spell points at them
with `REF`. Today 405 `LEVEL_CALCULATION` blocks hold 870 lines such as `+2 "Voice"`; the grammar
has no `+` on a number and the validator drops it. `^"Technique" STRING "Creo"` and
`^"Form" STRING "Ignem"` become `REF`; arm5e already defines `^"Creo"` and `^"Ignem"`. Waits on the
two parameter to-dos below.

2026-11-13, C5 part 7: the same blocks open with `BASE n` (749 lines in 36 files of arm5e and
armdef). `BASE` is a file-level keyword and stays reserved (DECISION-29, DECISION-51), so the
line takes another word when the blocks are rebuilt.

### F31. synthesist: what C6 removed

`REFERENCED BY` was removed in 0.6 (DECISION-52). The synthesist's parser, its AST and both of
its emitters read the block (`internal/ttrpg/parser.go`, `ast.go`, `internal/emit/ttrpg.go`,
`json.go`). No corpus writes it, so no output changes when the reading is dropped. The
synthesist reads neither `MENTIONS` nor the `MODIFY:` rule form.

### F32. Five repos, two generators and the synthesist: `USES_` lines become `DEPENDS_ON`

DECISION-55 folds the three `USES_` lines into `DEPENDS_ON`. 26 `USES_EXTENSION` lines are to
be rewritten: teeth 14, l5r5e 2, curseborne 1, dnd5e-3rdparty 4 (Wyldwolf Axis), troika-3rdparty
5 (Down In Yongardy). Each is a warning until then, since every file that writes one declares
`SPEC_VERSION` 0.5.

- **teeth.** Three of its lines name an id no file declares (`teeth-hogmen`, `teeth-stranger`,
  `teeth-cotillion`), and each becomes an error once it is a `DEPENDS_ON`. The Hogmen folder's
  file is `EXTENSION "teeth-hogmen-base"`. The lines are written by
  `titterpig-dsl-teeth/support/gen_oneshot.py`, which is where to fix them.
- **Down In Yongardy.** Its conversion scripts write the line
  (`Temp/yongardy-conversion/scripts/`).
- **synthesist.** It does not read a `USES_` line. It holds one `DEPENDS_ON` for a file
  (`internal/ttrpg/ast.go`, `parser.go`), so a container with several keeps one of them.

### F33. Nine core base files: 31 rules in the removed `WHEN […] THEN` form

DECISION-56 removes the form. Each of the 31 is a warning until its file declares 0.6: Call of
Cthulhu 4, Daggerheart 2, D&D 2014 2, D&D 2024 2, Draw Steel 4, The Expanse 4 (a 0.4 corpus),
Invisible Sun 3, L5R 7, Root 3. Each is rewritten against its book, since the text has to be
the source's.

- **A restatement of the core mechanic** (most of them) becomes a label with the book's
  sentence, or a DEF with a `DESCRIPTION`.
- **l5r5e's three `REQUIRE` rules** say what `REQUIRED` on a property says (§8, DECISION-34).
- **Draw Steel's four lines** give an echelon for a range of levels. They have no hash, and the
  grammar refuses them.
- **synthesist.** It carries whatever follows a rule's colon as the rule's text, so a consumer
  gets a rule in the removed form in the field that holds the book's wording
  (`internal/ttrpg/parser.go`, `parseRuleEntry`).

### F34. l5r5e, vtm5e and the synthesist: aliases under DECISION-57

- **Nine lines.** `ALIAS "name"` inside a DEF, in l5r5e (8, each the unaccented spelling of a
  name with a macron) and vtm5e (1, "Descendants of the Baron" on "The Nation of Blood"),
  becomes `ALIAS ^"name" FOR #hash` beside the DEF. Each is a warning until then. Rewritten in
  copies, the two corpora validate as before.
- **`Ichiro`.** In l5r5e the name is also a codex entity's
  (`l5r5e-0.5-path-of-waves-twin-blessings.codex`). §5b forbids an alias that already names a
  different entity, and the validator did not report this one in the copy. Whether the two are
  one character is to be checked against the books.
- **synthesist.** `parseAliasStatement` (`internal/ttrpg/parser.go`) reads the target as it was
  written in 0.5. It has to accept `FOR #hash` with no name, and carry the alias as a name of
  the hash.
- **armdef's four statements** carry a hash and the target's name, and need no change.

### F35. l5r5e and curseborne: a check is the system's own

DECISION-58 takes the check and the reward out of the base spec.

- **l5r5e.** The rules §16 held for writing a check are l5r5e's and belong in its own
  documentation: repeat `SKILL` or `RING` where the text allows either; write `RING` only where
  the text requires that ring; `RING_TN` for a ring with its own TN; `ALTERNATIVE` for a second
  way to make the check; an outcome only where the text states one. The wording is in §16 of
  the spec at commit `2410656`.
- **curseborne.** Its 13 checks are written with L5R's keywords (`RING "Cunning"`, `TN 3`).
  Whether to respell them in Curseborne's own terms is a question for its book.

### F36. Every corpus, its generators and the synthesist: the `EDITION` line

DECISION-59 has every BASE, EXTENSION, FRAME, ARC and CAMPAIGN declare its edition. 6,480 files
in the 29 directories need the line (6,280 in the 22 corpus directories), and each is a
warning until it has it.

- **The id.** The 22 directory names are the ids in use: `arm5e`, `armdef`, `dnd5e`,
  `dnd5.5e`, and so on. A third-party tree declares the edition it depends on, whatever repo it
  sits in: Wyldwolf Axis is `dnd5.5e`, and the trees of `titterpig-dsl-arm5e-3rdparty` are
  `armdef`.
- **Generators.** Each writes the header and has to write the line; the arm5e retarget writes
  `armdef` into what it derives.
- **Bare `.actor` files** (670, F17) get the line with their wrapper.
- **l5r5e's 69 codex files** write `FOR EDITION "l5r5e"`, the older form under DECISION-60,
  and change it to `EDITION "l5r5e"`.
- **synthesist.** Its manifest names the edition (`"edition": "arm5e"`). It can check that
  against what the files declare.
- **Found in passing, pendragon5e.** `pendragon5e-0.5-core-chapter-5-game-mechanics.ttrpg` holds
  a NUL byte on line 1129. The validator reads past it; `grep` treats the file as binary, which
  is how a count by `grep` came out one short of the validator's.

### F37. Three bridges: the `VERSION` on four sides

Under DECISION-61 the `VERSION` beside an edition is its corpus's content version. Four sides
name another, and each is a warning until corrected to `"0.5"`: `"dnd5e"` and `"dnd5.5e"` at
`"0.4"` in the D&D bridge, `"arm5e"` at `"0.4"` in the arm4 bridge, and `"pendragon6e"` at
`"0.5.1"` in the Pendragon bridge. `bridges/sources.json` records the same versions and
changes with them.

### F38. Every system: its `.system` file

DECISION-62 gives each edition a `.system` file. 22 are to be written, one in each corpus
folder, and they can be generated: the keywords from what the files write (316 distinct over
the 22; l5r5e 217, of which 109 are written once and want reading), the index from the folder
(l5r5e 166 files, teeth 94, arm5e 2,435), the `VERSION` from the folder's name.

- **Generators** keep the index current as they write files; the arm5e retarget writes
  armdef's.
- **The prose spec files** of arm5e, l5r5e, root and vtm5e document the same keywords and can
  point at the system file.
- **synthesist.** Its manifests name the edition and list files in load order. The system file
  holds the edition and the index; what a manifest adds is a selection and an order, which is
  the campaign's load file on the owner's list.
- **Third-party repos** have no system file of their own under this decision.

### F39. l5r5e: one hash for each codex entity

DECISION-64 makes an entity's name under a second hash a collision, an error at every
version. l5r5e has 114 such names, 249 blocks, and stands at 276 errors where it had 27. Commit `c7abe91` (2026-09-23) gave a new hash to each block that until then added
to an entity by its name.

- **94 names** have one block with `IS`. Each of their other blocks takes that block's hash.
  None of the 114 hashes to be dropped is written anywhere else in the corpus.
- **20 names** have two or three blocks with `IS`: the same subject declared in full more than
  once. One hash is chosen for each, and the `IS` lines are reconciled (`^"Brotherhood of
  Shinsei"` is a `^"Faction"` in one block and an `^"Organization"` in another).
- **The pass that hashes unhashed entities** is to leave a block that adds to an entity
  alone, or give it its entity's hash.

**Status:** open, not started.

### F40. l5r5e: a source on each codex edge

DECISION-66 has every edge cite its own source. l5r5e's 1,282 edges cite none.

- **943 edges** have a `FROM` phrase that stands under their block's heading or in a
  sub-section of it. Each takes its block's file and heading.
- **71 edges** have a phrase that stands elsewhere in the file. The heading is found by
  searching for the phrase.
- **74 edges** are in a block that names no heading, and take the file, with a heading where
  the phrase is found under one.
- **149 edges** have a phrase that is not word for word in the file: 65 join pieces with an
  ellipsis, 84 are not found. Three of the 84 were read, and each leaves a parenthesis out of
  the sentence. They want reading; §25 calls `FROM` the verbatim source phrase.
- **45 edges** have no `FROM` and want reading to be placed.

**Status:** open, not started.

### F41. pendragon6e: the bridge's renames, merges, omissions and introductions as `MAP`s

DECISION-67 lets a `MAP` stand with no `DISPOSITION`. The Pendragon 5e to 6e bridge was
written under the older rule and holds no `MAP`. In
`bridges/0.5/pendragon5e-to-pendragon6e-0.5-notes-on-the-new-edition.bridge`:

Counted in the file's 51 `CONVERT` lines on 2026-11-16:

- **9 of its 16 `UNCHANGED INTO` lines** write two different names (`^"Appearance (attribute)"`
  to `^"Appeal (APP)"`, `^"Attributes"` to `^"Characteristics"`, `^"Siege"` to
  `^"Siegecraft"`, `^"Lance [Knightly]"` to `^"Charge"`). One of the nine, `^"Orate [Knightly]"`
  to `^"Orate"`, differs only by the origin corpus's bracket. Which of them the appendix states
  as a rename is read from its text; each that is takes a `MAP`, and the `CONVERT` stays where
  the value carries across.
- **9 `MANUAL` lines** quote "In the case of Skills that have been combined" into four
  destinations: three into `^"One-Handed Hafted"`, two each into `^"Folklore"`, `^"Recognize"`
  and `^"Sword"`. Each destination is one merge, a `MAP` with its origins listed.
- **4 `MANUAL` lines** quote "Skills that no longer exist (Boating, Romance, Swimming,
  Tourney)" and have no `INTO`. Each is a `MAP` with an origin alone.
- **3 `CONVERT` lines** stand on the destination alone: `^"Brawling Damage"`, `^"Station"`,
  `^"Chivalry"`. Each is a `MAP` with a destination alone, where the appendix calls it new.
- **1 `MANUAL` line** quotes "Dagger becomes your Brawling Skill, 10 minimum".

A scratch copy with two of the renames as `MAP`s validates against both corpora (bullet 7,
point 1). The bridge's header comment, which says it has no `MAP` because a `MAP` requires a
`DISPOSITION`, is rewritten with it.

**Status:** open, not started.

### F42. Names the corpora write that hold nothing a reader can use

DECISION-69 reports three kinds of name. The corpora hold 29, each a warning today.

- **3 empty names**, dnd5e-3rdparty `historica-serpentine-door-0.4-adventure.arc`, lines 71,
  79 and 83: each is `^""They Are Here" — …"` and wants its quotes escaped. The grammar
  refuses the file for the same lines.
- **11 names with U+0007**, tor2e `realms-days-darken` (9), `ruins-gathering-storm` (1) and
  `ruins-landmarks` (1): the character is removed. One of the eleven is a reference and
  changes with its definition.
- **14 names with no letter and no digit** that read as slips, each to be checked against its
  source: `^","` (arm5e and armdef `the-church`, invisiblesun `teratology`), `^"&"`, `^"(  )"`,
  `^")"`, `^"<-"` (invisiblesun), `^"—"` and `^":"` (vtm5e, one each), `^"▪"` twice (vtm5e),
  `^"“"` and `^"”"` three times (arm5e-3rdparty `a-vanilla-covenant`). The arm5e name is fixed
  in arm5e and carried to armdef by the retarget.
- **1 name left as it is**, tor2e `core-adventurers`: the table row `^"—"`.

**Status:** open, not started.

### To-do recorded in the spec

- **Nested conditions in `WITH`** (§5b). `A AND (B OR C)` is not defined; a `WITH` that mixes `AND`
  and `OR` is an error until it is. Owner, 2026-11-11. With one value per term, "Major or Minor, and
  Supernatural" is such a condition and cannot be written in one `WITH` until this is done.

- **The two uses of `SET`** (§8, §13). Flagged for review by the owner, 2026-11-11. The validator
  tells them apart by position: a `SET` directly inside a `MODIFY` body is the §13 directive; a
  `SET` with a reference or a `CHOOSE` before it on the same line is a change. All 43 `SET`s in the
  corpora today are the §13 kind.
- **Dice amounts** for `SET` and `TRANSFORM` (§8). Not defined; they wait on a dice literal (C1).
  Counted 2026-11-11, third pass, with uppercase `D` and spaces allowed: 3,251 short `STRING`
  property values in 13 corpora hold a dice expression (callofcthulhu7e 984, daggerheart 696,
  pendragon6e 522, dnd5.5e 447, dnd5e 379, pendragon5e 174). By shape: 1,491 are one dice term
  with an optional modifier (`2d6`, `d20`, `4d8 + 8`, `2D6+4`), 625 of those printed with an
  uppercase `D`; 667 are dice and one word (`1d6+2 phy`); 276 are a number with dice and a
  multiplier (`50 (3D6 ×5)`); 138 are a signed bonus (`+1D4`); 40 are two dice terms
  (`1D6+1D4`); 49 add another value (`1D6 + damage bonus`). No `d%`, `d66`, keep-highest or
  exploding form appears as a property value. The two earlier figures (694, then 866) counted
  lowercase `d` only.

- **A change that targets a property of a parameter** (§5b, §8). §17's `^"Voice"` declares
  `PARAMETERS { ^"spell" OF ^"Spell" }` and holds `^"Magnitudes" TRANSFORM ADD 2`. Nothing in the
  DSL yet says that `^"Magnitudes"` there means the Magnitudes of the incoming spell. The validator
  reads a change's target as an entity name, so it reports `^"Magnitudes"` as undefined unless an
  entity of that name exists.
- **Binding the referring definition to an incoming parameter** (§5b). A spell takes Voice as
  `^"Range" REF ^"Voice"`. §5b binds a parameter with an argument, `^"Voice"(…)`; it has no rule
  that the definition holding the reference is itself the argument.
- **A spell's Magnitudes and derived Level** (arm5e, F5). §17's Pilum of Fire gives the printed
  `Level 20` and `BASE 10`. The spell type's `Magnitudes` property and the rule that derives Level
  from it are not written.
- **What a roll of symbol dice is worth** (§8). §8 says a roll's value is the sum where the faces
  are numbers. It does not say what the value is for a die whose faces are symbols, such as
  l5r5e's Ring Die.
- **The printed form of a roll** (§8). "4d8 + 12" no longer appears once it is written as steps.
  The owner agreed it may be kept beside the structure; no convention is set.
- **Dice forms not covered** (§8): keep-highest, drop-lowest, exploding and step dice. None appears
  as a property value in any corpus today.

- **Kinds of emphasis beyond bold and italic** (§5c). Underline, strike-through and small capitals
  are not defined. pendragon5e records the Book of Knights & Ladies' underlines and strike-throughs
  as typed properties, because there they carry rules.
- **A whole paragraph set in one face** (§5c). Owner agreed 2026-11-12 that this is a to-do. 1,305
  such spans sit in the corpora as `*…*` today (vtm5e 789, draw-steel 316, troika 72).
- **A campaign's order of play** (§16). The real Children of Fear campaign holds a `FLOW` with
  `PHASE`, `TRAVERSAL`, `NODES`, `GATE` and `EDGES`, because its middle chapters are played in any
  order. §16 gives a CAMPAIGN only `FROM ARC` lines and `PROGRESSION`, so the spec's example
  leaves that block out. Nothing in the spec defines it.
- **`TYPE` tags on an `ENTRY`** (§16). 285 `ENTRY` blocks carry `TYPE "hook"`, `"gm-guidance"`,
  `"special-rule"` and four more values as strings. Left as they are; belongs with C7.
- **An arc that adds detail to a setting's location** (§16). A location is imported with
  `FROM SETTING "id" INCLUDE [ … ]` and referenced. Nothing yet lets an arc or frame extend it.
  The form this replaced, `FROM SETTING` inside a `LOCATION`, had no corpus uses.
- **Tables: what is not covered** (§5e). Column headings in more than one tier; footnote marks on
  a cell (57 of the corpora's string grids carry them); whether every point of an axis has a cell,
  which the validator does not check; a result given as a bare value in place of a block.

### Known gaps left by this change

- **Nothing in this repo checks that a string is verbatim** (DECISION-47). The rule is stated
  for converters and for the tools that hold the source.

- **A hashless name in a system block is never resolved** (DECISION-44, by decision). A typo
  in one is not seen.
- **`check_references.py` does not count a list member or a stray hash and name pair as a
  reference site.** The validator checks them.
- **An unescaped quote in a DEF's name is reported as a hash that is no anchor,** and only
  because the name's first part reads as a stray reference. Nothing reports the quote itself.

- **The type keywords are not reported in a `.bridge` or a `.codex`.** Each has its own reader
  in the validator.
- **A declared name with nothing after it is read only in a `PROPERTIES` block or a property
  `DEF`.** Directly in a definition's body it is left alone, as a reference might be.
- **A value on the line after its name is not read as that property's value** (DECISION-39's
  line rule). No corpus line was found that writes one.

- **Nothing checks that a `SITUATIONAL` block's own-property target has a value outside the
  block.** `SITUATIONAL "2h" { ^"Load" SET 4 }` passes where a type declares `^"Load"` and the
  definition gives it no value.
- **Two `SITUATIONAL` blocks with the same condition in one definition are not reported.**
- **`check_references.py` does not count a `SITUATIONAL` condition or a change's target as a
  reference site.** The validator resolves both.

- **A narrative container's `FROM` and `USES_*` lines are not counted as dependencies.** §16
  makes a `FROM` line the declaration of what an arc draws on. The cycle check and the
  load-order rule read `DEPENDS_ON` and the header `EXTENDS` only.
- **§16's own dependency rules are not checked:** that a `FRAME`, an `ARC` and a `CAMPAIGN`
  each depend on exactly one `BASE`.
- **Load order is checked by nothing here.** The validator is given a directory and no order.
- **A file validated alone reports its parents as missing,** as it always has for
  `DEPENDS_ON`. A corpus is validated as a directory.

- **A `REQUIRED` on a property with no name of its own is not seen.** `REF OF ^"Clan" REQUIRED`
  declares a property named for its type; the validator's collector reads property lines that
  open with a caret. §17's worked examples use that form.
- **A required field inside a nested DEF is not checked** (`^"Rings" DEF { ^"Air" INTEGER
  REQUIRED }`).
- **What is a type and what is an instance is read from the DEF,** as `check_structure.py` read
  it. A DEF that extends a type, declares nothing and is extended by nothing counts as an
  instance, which is why draw-steel's classes are reported.
- **`check_structure.py` passes arm5e, armdef and draw-steel now.** Their only failure there was
  the `REQUIRED` check, which the validator reports as warnings until those files declare 0.6.

- **The name rule is written three times,** once in each of three tools, and nothing checks
  that the three copies stay the same. The fixtures would catch a copy that drifted on the
  cases they hold.
- **`apply_references.py` still folds names its own way** (lower case, letters and digits only,
  and "X, the" turned round). It searches prose for mentions and proposes references; it is not
  a gate. UNVERIFIED: that what it writes is always the definition's own name.
- **The validator's messages print a name as folded:** a curly apostrophe shows as a straight
  one.
- **The 43 pairs of definitions that are now one name** (`Jupiter's Touch` / `Jupiter’s Touch`)
  were not looked at one by one. Each is two entities of one name, or one entity written twice.

- **Six of the probe's 24 violations still pass every tool:** a `REQUIRED` property left out
  (B4), a `DEPENDS_ON` version that is not the parent's (B5), `SPEC_VERSION "9.9"`, two
  misspelt keywords (`PROPERTEIS`, `EXTEND`) and a value for a property no type declares. None
  has a rule the validator could apply without a ruling.
- **The value checks follow a chain by name where there is no hash,** and stop at a name two
  definitions share. An instance of an ambiguous type is not checked.
- **A nested or unnamed DEF's fields are not checked.** `^"Rings" DEF { ^"Air" INTEGER 9 }` is
  not compared with the type's nested declaration, and the records in a list body are not read.
- **A bound reference's caret arguments are not checked against the parameter's type,** only
  its string arguments against a list of strings.
- **`check_constructs.py` still matches by line.** A `FORMALITY` or `DEFAULT` not alone on its
  line is not seen. It normalises names its own way (B3).
- **The hash-format gating applies to DSL files the validator reads as `.ttrpg`.** A short hash
  in a `.bridge` or a `.codex` is still a warning at every version.

- **The grammar's reserved list is not §15's word for word.** `RESERVED_WORD` holds 45 words.
  It leaves out `NAME`, `VERSION` and `ORIGIN`, which have rules of their own that any body may
  use, and the short words that only stand inside another rule (`OF`, `TO`, `MIN`, `MAX`,
  `AND`, `OR`, `NOT`). It adds the openers of the annotation blocks (`REFERENCES`, `EMPHASIS`,
  `LABEL`, `GUIDANCE`, `HOOKS`, `FACES`), which DECISION-29 did not name either way.
- **The grammar accepts more than the spec means in three places.** Metadata (`NAME "x"`) may
  stand in any block. A keyword alone on a line is a statement. The old `TABLE "name" { … }`
  and a `HOOKS`-less `TRIGGER "…"` are read as a system's keywords. Each is a choice for a
  looser grammar over a refusal the validator already makes or the owner has excused.
- **The grammar and the validator are not checked against each other.** A file the grammar
  refuses can pass the validator (the 1,898 above), and the validator's token scanner is not
  derived from the grammar.
- **The spec's own example blocks are not run through the grammar.**
- **A keyword statement's arguments must begin on its line.** No corpus file was seen refused
  for that. It is a rule the spec's prose does not state outside DECISION-31.
- **`check_grammar.py` is slow by design** (a memo entry per rule and position). The 22 corpus
  directories take about three minutes in all. A file that takes over 30 seconds is counted
  as refused, and no file took that long.

- **The guidelines are still titled "(v0.4)"** and have not been revised for the 0.5 or 0.6
  constructs.
- **`TEXT` is also accepted as a property type.** The validator reads `^"Name" TEXT "…"` as it
  reads `STRING`, and 170 corpus lines write it. §8's type table does not list it, and
  DECISION-30 does not touch it.
- **Nothing checks the layout or the filenames** that §2 and §19 now describe.
- **Nothing checks where a block's keyword stands.** DECISION-29 is a statement of what the
  grammar already allows; no tool reports a block keyword misused.
- **The spec's title, status line and footer still say v0.5.** That holds until 0.6 is released.

- **An `.actor` instance's type is not checked for being a type.** The validator asks only that
  each top-level DEF has an `EXTENDS`. It does not ask what the target is, and it does not
  require an `ACTOR` type (arm5e's creatures and covenants extend plain DEFs).
- **Only the listed statements are refused in an `.actor`:** a type, an `ACTOR` or `TEMPLATE`
  definition, `MODIFY`, `OVERRIDE`, `ADD`, `REPRINT`, `ALIAS`. Any other top-level block passes.
  No corpus file has one.
- **A bare `.actor` can only warn.** It declares no `SPEC_VERSION`, so the 0.6 error never
  applies to it.
- **The reference gate, `check_constructs.py` and `check_structure.py` do not look at how an
  `.actor` opens.** The synthesist still parses a bare file.
- **The atlas skill still describes "headerless `.actor` fragments"** as a normal form.

- **The reference gate does not report a DEF hash declared twice.** `check_references.py` gives
  0 errors on `tests/restate-bad`. The validator gives 3.
- **The synthesist still applies a hash match and a name match as replacements** (F16). No
  corpus restates a DEF's hash, so the hash rule never fires today. The name rule fires 301
  times in six compositions.
- **A hashless `REFERENCES` target to a name two entities share only warns in the gate.** §5d
  rule 3 makes it an error. On a scratch copy of `tests/restate-good` with the hashes stripped
  from its two arrows, `check_references.py` gives 0 errors and 2 hashless WARNs, and the
  validator gives nothing. The gate does fail the same name after `EXTENDS` (1 error). Belongs
  with C3. It matters more now: once the synthesist stops merging, these references are where a
  duplicated name should surface.
- **No tool lists same-name DEFs for triage** except the synthesist's `--collect -v`.
- **`titterpig-mastra/TASKS.md` still holds an open task** to make the validator accept a
  restated hash ("Validator: scope the duplicate-anchor check", line 59). DECISION-27 makes it
  moot. Not edited: it is in another repo.

- **An undeclared port is invisible.** The validator checks a file that says `ORIGIN`. It cannot
  find a file that is a port and does not say so, and armdef's 2,390 say nothing until F14.
- **A shared hash outside a port is not reported.** invisiblesun and root share 1,508 by
  accident. That is legal and no tool counts it; F15 makes the two distinct. The cause is
  UNVERIFIED: two conversions that seeded one generator alike would produce it, and I have not
  looked.
- **An edition id is bound only on the command line.** `ORIGIN "arm5e"` means the directory given
  as `--corpus arm5e=<dir>`, as in a bridge. No file declares its own edition (C8), so the
  validator cannot check that a port and its origin are in fact two editions.
- **`ORIGIN` in a port takes no `VERSION`.** A bridge's `ORIGIN` may pin one.
- **The port check reads the origin a file at a time.** A file that holds two containers lends
  its anchors to both. UNVERIFIED whether any corpus file holds two.
- **A ported `.lore` file declares nothing.** It has no header.
- **Only the validator reads `ORIGIN`.** `check_references.py`, `check_constructs.py` and
  `check_structure.py` pass over the line (run on `tests/ports-good`: no finding about it). The
  synthesist and the VTT parsers are unchecked. A `.codex` or `.selections` file with an `ORIGIN`
  line is not read as a port.
- **The 280 arm5e sourcebook DEFs with no armdef counterpart** were not checked one by one
  against the `REPRINT` / `ALIAS` / `MODIFY` table that should account for them.
- The guidelines and the atlas skill say nothing about ports.

- **§16's SETTING and FRAME examples are still invented.** They carry `SPEC_VERSION`, opaque
  hashes and the 0.6 forms, and their content is unchanged. A real setting waits on l5r5e's Rokugan
  (F1). The invented FRAME's NPC extends `^"Adversary"` with no hash, which the reference gate
  WARNs on. The CAMPAIGN example is real but partial: the real file has no `RECURRING_CAST`, so the
  example no longer shows one, and its `FLOW` is left out (see the to-do).
- **A scene type is checked for membership only where the parent is defined.** The validator
  resolves `TYPE #hash ^"Name"` always, and checks that the entity is a `^"Scene Type"` or a
  `^"Conflict Type"` only when the loaded set defines that parent.
- **An escaped quote in a caret name is read by the validator and the reference gate only.**
  `check_constructs.py`, `check_structure.py`, the synthesist and the VTT parsers were not checked
  for it. 33 lines in five corpora write such a name (arm5e 16, callofcthulhu7e 8, draw-steel 6,
  teeth 2, vtm5e 1).
- **A reference by name alone to a block raises no warning yet.** §20 says it WARNs as any
  hashless reference does. The validator resolves it inside its file and says nothing, because the
  hashless warning lives in `check_references.py`, which does not count the references between
  narrative blocks as §5d sites. 69 scene `LOCATION ^"Name"` lines are of this kind (draw-steel 60,
  curseborne 9).
- **The same hash on the same name is accepted as a restatement, for blocks.** §5 allows it
  across files, and l5r5e's 2020 errata restates 13 entries of the 2019 errata that way. The
  validator still flags every repeated DEF hash, which the spec already records as pending. One
  block and one DEF share a hash and a name (l5r5e's `CHECK` and DEF "Stir the Leaves", and
  `SCHOOL_ABILITY` "Way of the Carp"); those pass as restatements.
- **A codex category is a name in the validator and not in the gate.** The gate now indexes
  codex entities; it does not read `CATEGORIES`.
- A lowercase bare word in `MODIFICATIONS` (`entanglement DEFAULT 1`) raises no finding.
- **What the validator still does not check in a narrative file.** `USES_SETTING`, `USES_FRAME`
  and `USES_EXTENSION` targets; cycles through `FROM` (rule 5); a hash-only reference to a scene,
  a location or a cast member, because block hashes are not registered as anchors. An `INCLUDE`
  item written as `#hash ^"Name"` is resolved; one written as a bare hash is not. Belongs with B2
  and C3.
- `EMPHASIS` kinds and `LABEL` are read by `check_references.py` only where the keyword starts a
  line, as every block that gate reads is. The validator checks the words before the brace and
  nothing else about them.
- **Embedded references.** The validator resolves the name and the hash; that a hash and a name
  agree, and that a hashless name is one entity, are checked by `check_references.py` only, as for
  every other reference. Neither tool reads embedded references in `.bridge` or `.codex` strings
  in the validator, and the gate's hashless-and-ambiguous rule is stricter for an embedded
  reference (ERROR, as §5d says) than for a `REFERENCES` target (WARN, as the gate has always done).
- **Tables.** `check_references.py` does not count an `AXIS … OF` type, an axis point or a
  coordinate as a §5d site. The validator resolves all three.
- `AUTHORING-GUIDELINES.md` and the hub skill say nothing about `EMPHASIS`, `LABEL`, embedded
  references or `TABLE`. They did not cover `EMPHASIS` before either.

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
- `check_references.py` does not count a `ROLL`'s die, a face's reference, a `REF`'s type or
  entity, or a change's target as §5d sites either. The validator resolves all of them.
- No corpus `gates.sh` passes the dice module yet. A corpus that adopts dice must validate with
  `modules/0.6/` alongside it, or its `DEPENDS_ON "Titterpig_Dice"` is an undefined file id.
- `check_references.py` does not yet count `CHOOSE` options or the `OF` type as §5d sites, so a
  hashless option raises no warning there. The validator resolves them. Belongs with C3.
- The grammar change is unproven: no tool runs `ttrpg.peg` (B1).
- The atlas skill's `references/spec-map.md` gives line numbers into the spec, and every edit to
  the spec moves them. Refresh it when the 0.6 edits settle.
- **How a codex tells apart two things of one name** (§25). Owner, 2026-11-14: "we should update
  codex to handle this adequately, which probably involves some kind of disambiguation. Add
  this to the to-do." An entity and a DEF may share a name (DECISION-65). A codex names its
  targets by name in four places: an edge's object, an `IS`, a `DOMAIN` and a `RANGE`. Since
  DECISION-65 an edge's object may carry a hash, which is the agent's form for the meantime;
  the other three take a name alone in the grammar. No form of disambiguation is ruled. It
  goes with the review of unique identifiers for lore, on the list after C9.

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
| A1 | 2026-11-11 | A `REF` property implicitly takes its type's name, and a name may always be written, the type's own included, with no warning. The warning is removed. | Owner's call, replacing the agent's reading. |
| A1 | 2026-11-11 | Voice's change to the spell's magnitudes takes the spell as an incoming parameter: `PARAMETERS { ^"spell" OF ^"Spell" }`. | Owner: "now we're starting to need them". |
| A1 | 2026-11-11 | Deriving a spell's Level from its Magnitudes is a to-do for arm5e (F5). The rule is more complex than "multiply by 5". | Owner's call. |
| A1 | 2026-11-11 | §17's Pilum of Fire fixed as far as the DSL allows: `BASE 10`, the invented `DAMAGE` and `RANGE_MODIFIER` lines removed, the book's description, Range / Duration / Target as `REF`, and a `^"Voice"` entity that carries the +2 magnitudes. What could not be written is in the to-do list. | Owner: "fix as much as you are able, and mark anything you can't fix in the todo". |
| A1 | 2026-11-11 | Dice forms agreed and written into §8 as DECISION-18: a die is a DEF that `EXTENDS ^"Die"` with a `FACES` block (a range for a numeric die; weight 1 unless `WEIGHT n`); a roll is `ROLL n OF ^"die"`, its value the sum where the faces are numbers; a step's result is named by the property it sits under; `NEXT` before each later step; one module file defining `^"Die"` and d2, d3, d4, d6, d8, d10, d20, d100. | Owner agreed to all five forms. `NEXT` over `THEN`: `THEN` already means the consequence of a `WHEN` (31 uses in 9 corpora). |
| A1 | 2026-11-11 | The dice module is edition-neutral: its hashes are the same wherever it is included (§19), and a system's BASE may declare `DEPENDS_ON "Titterpig_Dice"` (§3). A corpus that uses it is validated with the module passed alongside. | Owner agreed to the mechanism. |
| A1 | 2026-11-11 | A1 is closed. The branch is committed and pushed. A2 is not to be started yet. | Owner's call. |
| A1 | 2026-11-11 | To-do for l5r5e: the Blank face of its dice is a DEF, like Opportunity, since Inversions and similar rules name it. Logged under F6. | Owner's call. |
| A1 | 2026-11-11 | A face may be followed by what it shows, a string or a reference (`1 "Blank"`). An older `ROLL "1d10"` is left alone in a file below 0.6 and is an error from 0.6 on. | Agent's calls, to confirm. The first keeps l5r5e's existing `FACES` blocks valid as written; the second follows the owner's `CHOICE` ruling. |
| A1 | 2026-11-11 | The spec ships a dice module that every edition includes. | Owner's call, over the agent's lean toward each system defining its own dice. |
| A1 | 2026-11-11 | The printed form of a roll may be kept beside the structure; no convention is set yet. Two or three lines per dice value is acceptable. | Owner's call. |
| A1 | 2026-11-11 | Dice are DEFs, starting with d2, d3, d4, d6, d8, d10, d20 and d100, each a list of values with a weight of 1. A thing that needs a roll declares the dice, transforms the value, stores the sum, and may add a property (a damage type). | Owner's direction, replacing the agent's proposal of a dice literal and a `DICE` type, which is withdrawn. The exact forms are not yet settled. |
| A1 | 2026-11-11 | `REF` is the property type for a reference to one entity: `REF OF ^"Type"` on the type, `REF ^"Entity"` on an instance. Written into §8 as DECISION-17. The example's `^"Clan" STRING "Crab"` is now `^"Clan" REF #… ^"Crab"`. | Owner asked for the string to become a reference and chose `REF` from four candidate terms. |
| A2 | 2026-11-12 | Embedded references (`^\"Name\"` inside a string) stay in the DSL and are to be better supported. | Owner's call, over the agent's recommendation to remove them. What the support covers is a proposal awaiting his choice; nothing is applied yet. |
| A2 | 2026-11-12 | `EMPHASIS` takes its kind after the keyword: `EMPHASIS BOLD { … }`, `EMPHASIS ITALIC { … }`, `EMPHASIS BOLD ITALIC { … }`. Written into §5c as DECISION-19. | Owner chose this from three options. |
| A2 | 2026-11-12 | A run-in label is recorded in a `LABEL` block, with an optional depth after the keyword (`LABEL 2`), 1 when none is written. | Owner's call, replacing the agent's proposal to record a label as emphasis. |
| A2 | 2026-11-12 | A whole paragraph set in one face is a to-do, stated in §5c. | Owner agreed. |
| A2 | 2026-11-12 | Tables get a coherent structure that carries more than rows and columns: a special DEF with a list of coordinates and the results at them. | Owner's direction. Proposals requested; nothing is applied yet. |
| A2 | 2026-11-12 | The kinds are `BOLD` and `ITALIC` only, in either order, each at most once, and a block with no kind stays legal. A depth-2 label sits under the depth-1 label before it. A label may be a line of its own as well as the opening words of a paragraph. | Agent's calls, to confirm. Needed to write the text; the owner named the form and not these details. |
| A2 | 2026-11-12 | The `EMPHASIS` and `LABEL` approach is confirmed, including the three details the agent had flagged. | Owner: "Confirming our approach on EMPHASIS". |
| A2 | 2026-11-12 | Tables: the coordinate table and the table of records are adopted. The specified grid of printed strings is not. | Owner chose ideas 1 and 2 of three. |
| A2 | 2026-11-12 | The table is a primitive of the DSL and not a hashed definition that tables extend. | Owner's call. The agent agrees: it had proposed a shipped `^"Table"` DEF by analogy with the dice, and the analogy fails. A die DEF carries data (its faces); a table type would carry none, and would add a module every corpus must load. |
| A2 | 2026-11-12 | An embedded reference may point at a DEF and keep a different literal text, so that it works as an index and the text a reader sees is unchanged. Form: `^\"Enraged\"/\"state of rage\"`. Written as DECISION-20. | Owner's direction and proposed form ("could be one approach"), adopted as proposed. This replaces the agent's proposal to leave differing words to the `REFERENCES` block. |
| A2 | 2026-11-12 | Tables, as written (DECISION-21): a `TABLE { }` block in a DEF's body; `AXIS ^"Name"` with points `OF ^"Type"`, `lo-hi`, `INTEGER`, `ROLL n OF ^"die"` or a list; `AT [ … ] { … }` with coordinates that are a number, a range, `MIN n`, `MAX n`, an entity, a string or `ANY`; the result is always a block; `COLUMNS [ ^"Property", … ]` for a table of records. Two cells that cover the same coordinates are an error. A `TABLE` with no `AXIS` is left alone below 0.6 and is an error from 0.6. | Agent's calls, to confirm. The owner saw `AXIS`, `AT [ … ]`, ranges, `MIN`, `ANY` and `COLUMNS` in the proposal and chose the ideas; he did not rule on each word. `AXIS` and not `AXES`, because l5r5e has an `AXES { }` block for its axe weapons. |
| A2 | 2026-11-12 | Embedded references, as written (DECISION-20): the literal's quotes are escaped inside an ordinary string, as the name's are, and bare inside a triple-quoted one; a `#hash` may stand before the caret; §5d applies unchanged (hashless WARNs, hashless and ambiguous is an ERROR); each counts as a reference for `REFERENCED BY`; the `REFERENCES` block stays legal; an empty literal is an error. | Agent's calls, to confirm. The first is forced by the lexer: an unescaped quote ends the string. |
| A2 | 2026-11-12 | The table forms (DECISION-21) and the embedded-reference forms (DECISION-20) stand as written, including the agent's calls in the two rows above: a result is always a block, overlapping cells are an error, an older `TABLE` grid is an error from 0.6, and a hashless embedded reference follows §5d unchanged. | Owner: "Yes, as written". |
| A2 | 2026-11-12 | Markdown emphasis inside a string is flagged by the validator: a warning in a file below 0.6, an error from 0.6. A `FIAT` with its reason excuses asterisks the source prints. Written into DECISION-19 and §5c. | Owner: "Yes, flag it", choosing this over a warning at every version. |
| A2 | 2026-11-12 | What reads as a span: a paired `**…**` or `*…*` on one line of text. An asterisk followed by a space, or preceded by a letter, a digit or a closing bracket, does not open one. One finding per string. | Agent's calls, to confirm. They keep footnote marks, bullets and `Chirurgery 20*` from being flagged; the closing-bracket rule was added after the one false alarm found in the corpora (pendragon6e's `Courtesy 20 (+1)*`). |
| A2 | 2026-11-12 | A2 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's call on what reads as a Markdown span (the row above) was reported to him before he closed and was not separately ruled on. |
| A3 | 2026-11-12 | §16's examples carry opaque hashes of 16 or more characters. | Owner: "opaque hashes please". |
| A3 | 2026-11-12 | §16's examples are worked from the real Lost Writer arc (`l5r5e-0.5-children-of-five-winds-lost-writer.arc`). | Owner's call. Not yet applied: the rebuilt example depends on the rulings still open under A3. |
| A3 | 2026-11-12 | Imports: option A. A `FROM` names its container's kind and is itself the declaration; rule 7's second declaration in the header is withdrawn. A `FROM "id"` with no kind is a warning below 0.6 and an error from 0.6. Written as DECISION-22. | Owner: "Let's go with option A". |
| A3 | 2026-11-12 | Declaration order: both orders are legal for a block, and the convention stays (name, then hash). | Owner: "allow both, keep the convention". |
| A3 | 2026-11-12 | A skill group is a property of a character. §16's NPC shows `^"Skills" DEF { ^"Artisan" INTEGER 1 … }`, and §17's schema and §8's type illustration no longer declare `^"Skills" LIST OF ^"Skill"`. | Owner's call, on the agent's corrected recommendation: l5r5e has no entity for a skill group. |
| A3 | 2026-11-12 | l5r5e core should define the setting as Rokugan. It does not, so it is logged as a to-do under F1. | Owner's call. Checked: no `SETTING` container, `.setting` file or `USES_SETTING` in l5r5e. |
| A3 | 2026-11-12 | In the rebuilt examples every reference to a scene, a location or a cast member is the §5d pair, `#hash ^"Name"`, where §16 showed a bare hash. The validator does not flag a bare hash. A `FROM` whose container is not in the loaded set is an error at every version, as an undefined `DEPENDS_ON` is. `FROM BASE` is accepted beside the four kinds named in the text. Every §16 block and example now declares `SPEC_VERSION`. | Agent's calls, to confirm. The first was recommended on 2026-11-12 and not ruled on; the example had to be written one way. |
| A3 | 2026-11-12 | The stale clause in §16's DECISION-2 note is deleted. | Owner: "1, delete". |
| A3 | 2026-11-12 | `MODIFICATIONS` holds a starting value as `#hash ^"Property" SET value` and a range as a property declaration with `MIN` / `MAX`. `RANGE(…)` is gone and `RANGE` leaves the FRAME keyword list (it stays a codex keyword). | Owner agreed. |
| A3 | 2026-11-12 | A frame's `RULES` use §12's form. `RULE name ADDS_TO PARENT` is removed from §16. | Owner chose option A. |
| A3 | 2026-11-12 | A setting's location is imported with `FROM SETTING "id" INCLUDE [ #hash ^"Location" ]`. `FROM SETTING` inside a `LOCATION` is removed. An arc adding detail to a setting's location is a to-do. | Owner agreed. |
| A3 | 2026-11-12 | The dependency diagram is replaced by one line per container and a table of every edge with the keyword that makes it. | Owner agreed. The agent's reading of "redraw": a table carries the labels more reliably than drawn arrows. |
| A3 | 2026-11-12 | How a type slot is written (the pipe in `CONFLICT`) is not fixed yet. | Owner: "let's review this more closely, probably should be a choice". |
| A3 | 2026-11-12 | The CAMPAIGN example is taken from the real Children of Fear campaign (callofcthulhu7e). | Owner's call. |
| A3 | 2026-11-12 | Scene types and conflict types are entities each system defines, and a scene or conflict points at one: `TYPE #hash ^"Investigation"`. The base spec fixes no list. Written as DECISION-23. | Owner chose option C of three. |
| A3 | 2026-11-12 | A string in a scene's or conflict's `TYPE` is a warning below 0.6 and an error from 0.6. The parents are named `^"Scene Type"` and `^"Conflict Type"`, and membership is checked only where the loaded set defines the parent. The CAMPAIGN example shows only what §16 defines, so the real file's `FLOW` of phases and edges is left out. The SETTING and FRAME examples stay invented. | Agent's calls, to confirm. The first follows the owner's pattern for every form replaced in 0.6. The last was recommended on 2026-11-12 and not objected to. |
| A3 | 2026-11-12 | A3 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's calls in the rows above marked "to confirm" were reported to him before he closed and were not separately ruled on. |
| A4 | 2026-11-12 | Two tiers. A definition (DEF, `ACTOR`, `TEMPLATE`, `ALIAS`, codex `ENTITY`) is a name every file may use. A named block is a target through its hash, and its name is a label inside the file that declares it. Written as DECISION-24. | Owner: "Yes, two tiers", choosing option B of three. |
| A4 | 2026-11-12 | Any named block that carries a hash is an anchor, whatever its keyword. A hash declared on two different names is an error; on the same name it is a restatement and legal. The one block that shares a hash and a name with a DEF therefore passes. | Agent's calls, to confirm. The second replaces what the agent told the owner beforehand (that the shared `CHECK` / DEF hash would be a duplicate): l5r5e's errata files restate 13 entries under the same hash and name, which §5 allows, so repeating a hash could not be the error. |
| A4 | 2026-11-12 | A caret name may hold an escaped quote: `^"Mrinmoy \"Vidyapati\" Mishra"`. Written as DECISION-25, and read that way by the validator, the reference gate and the grammar. | Owner: "Yes, allow it", over renaming the 31 definitions that carry one. |
| A4 | 2026-11-12 | A4 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's calls in the A4 row marked "to confirm" were reported to him before he closed and were not separately ruled on. |
| A5 | 2026-11-12 | A port keeps its source's hashes, and a port declares its source. Written as DECISION-26 in §3, §5, §13, §15, §19, §20 and §21, in the grammar and in the validator. | Owner: "ports keep them but there should be a port declaration". The alternative was to re-mint 10,275 armdef anchors and keep a map. |
| A5 | 2026-11-12 | The declaration is `ORIGIN "edition" <KIND> "id"`, as in `ORIGIN "arm5e" EXTENSION "ArM5_Grogs_Abilities"`. | Owner: "Yes, as written". It reuses the bridge's keyword. |
| A5 | 2026-11-12 | Agent's calls, to confirm. They were reported to the owner beside the wording and not separately ruled on. (2) A hash a port shares with its origin must carry the same name in both. (3) A port and its origin in one loaded set is an error. (4) With no corpus for the origin's edition the validator gives one warning per edition id, where a bridge gives an error. (5) No `VERSION` on the line. (6) A port may add definitions of its own and may leave entities out. (7) The audit's first count for A5 (8,299 of 9,959) is replaced by a recount (10,275 of 11,965). | (2) to (6): the smallest rule that makes the declaration checkable; all 10,275 real pairs satisfy (2). (7): the first count could not be reproduced. |
| A5 | 2026-11-12 | invisiblesun and root are to be re-minted so that they share no hash. Recorded as F15. | Owner: "add to the todo to fi[x] invisiblesun and root's hashes to be unique/distinct". The spec does not require it. |
| A5 | 2026-11-12 | A5 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's calls in the A5 row marked "to confirm" were reported to him before he closed and were not separately ruled on. |
| A6 | 2026-11-12 | Part 1: the implicit override is dropped. A DEF's hash stands once in a corpus, and a replacement is written `OVERRIDE`, `MODIFY` or `REPRINT`. Written as DECISION-27 in §5, §5d, §13 and §20. | Owner: "Yes, drop it". No corpus restates a DEF's hash, and the validator has always rejected it. |
| A6 | 2026-11-12 | Agent's calls, to confirm. (1) A named block stated again under its own hash and name, and a codex `ENTITY` restated to add sources, stay legal; §20 now says so. (2) §13's list of overlapping printings loses "a draft and a definitive edition", which are two editions under §19 and cannot be in one set. (3) The validator's `duplicate anchor` message now names the statements to write. | (1) was reported to the owner with the question and follows A4; l5r5e's 2020 errata repeats 13 entries of its 2019 errata. (2) and (3) follow from the ruling. |
| A6 | 2026-11-12 | Part 2: a DEF of the same name under another hash is a second entity and replaces nothing; a consumer must not merge the two. Written into DECISION-27 and §13. The synthesist and the corpora follow in F16. | Owner: "Yes, two entities". The name match dropped 356 definitions in six compositions, and tor2e's built JSON lost its core Combat chapter. |
| A6 | 2026-11-12 | Agent's calls, to confirm. (4) Both rulings are one decision, DECISION-27. (5) F16 says to triage a composition before rebuilding its JSON without the name match. (6) The gate's weaker treatment of a hashless `REFERENCES` target is logged as a gap and not fixed here. | (4): one subject. (5): a pair meant as one entity would otherwise arrive as two. (6): fixing it would raise new findings across the corpora, which was not asked for. |
| A6 | 2026-11-12 | A6 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's calls in the A6 rows marked "to confirm" were reported to him before he closed and were not separately ruled on. |
| A7 | 2026-11-12 | An `.actor` file always opens with the `EXTENSION` wrapper; it holds one or more DEFs; it holds instances only. Written as DECISION-28 in §2, §3 and §5, and checked by the validator. Moving l5r5e's `^"Historical Persona"` is a to-do in F1. | Owner: "part 1: always wrapped / part 2: one or more / part 3: instances only. mark historical persona as a todo". |
| A7 | 2026-11-12 | Agent's calls, to confirm. (1) A bare `.actor` is a warning, and replaces the missing-`SPEC_VERSION` warning. (2) A type or a modification in an `.actor` is a warning below 0.6 and an error from 0.6. (3) An `.actor` that opens with a container other than `EXTENSION` gets the same treatment. (4) The type an instance extends need not be an `ACTOR` type. (5) An instance may extend another instance in the same file. (6) The guidelines' file-type row is updated. (7) The audit's first count (2,420 wrapped) is replaced by a recount (2,407). | (1) and (2): the owner's pattern for an older form. (4) was put to the owner with part 3. (5): four arm5e DEFs do it. (6): the row stated the withdrawn rule. |
| A7 | 2026-11-12 | A7 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's calls in the A7 row marked "to confirm" were reported to him before he closed and were not separately ruled on. |
| A8 | 2026-11-12 | Six fixes with one obvious answer are applied: the footer date, §19's version label and the validator's header, "Four additions", "unique within an edition" in the guidelines, §15's missing keywords, and §8's type table. | Owner: "Yes, apply them". |
| A8 | 2026-11-12 | Agent's calls, to confirm. (1) `TRIGGER` is listed as reserved inside a `HOOK` and kept as a system keyword outside one; the proposal had been to move it to the reserved list outright. (2) The guidelines' "(v0.4)" title is left. (3) The grammar's `ENUM` and `LIST` rules take modifiers. | (1): 438 corpus lines use `TRIGGER` as a system field. (2) was put to the owner with the list. (3): item 10's rule, in the grammar. |
| A8 | 2026-11-12 | Items 5, 6, 9 and 11: §2 shows the real layout; §19 puts the content version in the directory and the filename; a block's keywords are reserved inside that block (DECISION-29); a definition's prose is `DESCRIPTION` and `TEXT` is not its alias (DECISION-30). | Owner: "accept all recommendations". On 11 the agent's recommendation had changed to withdrawing the alias, once the count showed one corpus uses it. |
| A8 | 2026-11-12 | Agent's calls, to confirm. (4) `TEXT` directly in a DEF is a warning below 0.6 and an error from 0.6; `TEXT` in any block that is not a DEF is left alone, including a system block such as `READ_ALOUD`. (5) Items 5 and 6 are written as description, with no decision number. (6) §10's example of `TEXT` is l5r5e's errata entry. | (4) was put to the owner with item 11. (5): no language rule changes. (6): a real example. |
| A8 | 2026-11-12 | `tests/markdown-bad.ttrpg` wrote one of its faulty strings as `TEXT` directly in a DEF, which DECISION-30 now also reports (7 errors where the fixture states 6). The field is renamed `EFFECT` so the fixture holds only its own kind of fault. | Agent's call, found on the pre-commit run and reported with the close. |
| A8 | 2026-11-12 | A8 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's calls in the A8 rows marked "to confirm" were reported to him before he closed and were not separately ruled on. |
| B1 | 2026-11-12 | The grammar is run and gated on the repo's fixtures. `check_grammar.py` is added; `ttrpg.peg` is repaired until it accepts all 35 good fixture files and refuses twelve planted syntax faults. The corpora are measured (5,157 of 7,055 accepted) and not gated. Written as DECISION-31. | Owner: "Yes, make it run". The alternatives were to demote the grammar to a sketch or delete it. |
| B1 | 2026-11-12 | Agent's calls, to confirm. (1) A keyword statement's arguments begin on the keyword's line. (2) `RESERVED_WORD` adds the annotation-block openers and leaves out the words listed in the gaps. (3) A list may be empty. (4) A DEF's hash may follow its name. (5) Forms the spec does not define stay refused: `ENUM "x"`, an unnamed `DEF { }` in a list, `"text" +6`, an annotation block in an `ENTRY`. (6) The interpreter is written here, with no dependency. | (1): it stops a statement from taking the next line's first token. (2): a malformed annotation block was being read as a system keyword. (3) and (4): the corpora and A3's convention. (5): a grammar that accepts what the spec lacks would hide F19. (6): the repo's tools are plain Python. |
| B1 | 2026-11-12 | B1 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's calls in the B1 row marked "to confirm" were reported to him before he closed and were not separately ruled on. |
| B2 | 2026-11-12 | The validator gains six groups of checks: cycles, bound references, list members, values against the inherited declaration, a property written twice, and the hash format. `check_constructs.py` reads every DSL file type and wrapped lists. Written as DECISION-32. `REQUIRED` and version pins are left to B4 and B5. | Owner: "Yes, add them". The alternative was to cut the spec's claims down to what was checked. |
| B2 | 2026-11-12 | Agent's calls, to confirm. (1) The list-member rule is gated by version; it was to be an error everywhere, and the corpora hold 15. (2) `EXTENDS` is declared acyclic in §6; the spec had not said. (3) A hash-format finding takes no `FIAT`. (4) A name two definitions share is not followed up a chain. (5) `check_constructs.py` counts a named block's hash as an anchor and reads a list that a comment follows. | (1): the zero came from a prototype that skipped definitions with no parent. (2): the owner approved the check. (3): a hash is not content. (4): §5d. (5): DECISION-24, and a comment was hiding a list from the check. |
| B2 | 2026-11-12 | B2 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's calls in the B2 row marked "to confirm" were reported to him before he closed and were not separately ruled on. |
| B3 | 2026-11-12 | Two names are the same when their characters are the same after Unicode normal form, a run of white space read as one space, and a curly quote read as a straight one; case, punctuation and accents count. Written as DECISION-33 in §14, and the validator, the reference gate and `check_constructs.py` compare names that one way. | Owner: "Yes, that rule". The alternatives were fully exact, and the gates' fold. It follows his ruling of 2026-09-29 that quote style is not content. |
| B3 | 2026-11-12 | Agent's calls, to confirm. (1) The rule is not gated by `SPEC_VERSION`: callofcthulhu7e's and l5r5e's gates fail on five references today. (2) `apply_references.py` keeps its looser match. (3) A no-break space counts as white space. | (1): the owner was shown the five before he ruled, and a name rule that depended on the file's version would give two answers for one reference. (2): it proposes references and gates nothing. (3): it is a difference a reader cannot see. |
| B3 | 2026-11-12 | B3 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's calls in the B3 row marked "to confirm" were reported to him before he closed and were not separately ruled on. |
| B4 | 2026-11-13 | `REQUIRED` keeps one meaning: every entry of the type has the property. It is not used for a rule of character creation, and the DEF's own name answers a required `^"Name"`. The validator checks it for every instance; `check_structure.py` drops its looser check. Written as DECISION-34. | Owner: "Yes, that meaning only", after asking how the word is used today and whether it should be used at all. 782 of 835 uses already carry this meaning. |
| B4 | 2026-11-13 | `tests/tables-bad.ttrpg` held a helper, `^"Chain Mail"`, that extends `^"Armor"` and lacked the `^"Protection"` its type requires. The new check reported it (21 errors where the fixture states 20). The helper now has the property, so the fixture holds only its own faults. | Agent's call, found on the fixture run before the close was asked for. |
| B4 | 2026-11-13 | Agent's calls, to confirm. (1) A `TEMPLATE` counts as a type and owes nothing. (2) An entry written inside another DEF is checked. (3) One finding per instance and declaring type, naming every missing property. (4) The 280 lines of `check_structure.py` that served the old check are removed. (5) The 239 `^"Name" … REQUIRED` declarations are left in the corpora. | (1): a template leaves fields open by design; it removes 25 findings the census counted. (2): books' entries are often nested in their section's DEF. (4): they are in the repo's history. (5): they are true and cost nothing. |
| B4 | 2026-11-13 | B4 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's calls in the B4 rows marked "to confirm" were reported to him before he closed and were not separately ruled on. |
| B5 | 2026-11-13 | Part 1: a version pin means "at least". The loaded parent must be at the pinned version or a later one; a pin with fewer parts is met by any version that begins with it. Written as DECISION-35, and the validator checks it. | Owner: "Yes, at least". All 459 pins pass, and the rule to bump `VERSION` on every edit cannot break one. |
| B5 | 2026-11-13 | Agent's calls, to confirm. (1) An older parent is an error at every version, with no gating. (2) A parent with no `VERSION` is a warning. (3) Versions split at dots and hyphens, and a part that is not a number compares as text. | (1): no corpus has one. (2): the pin cannot be checked. (3): §19 allows date-based versions. |
| B5 | 2026-11-13 | Part 2: a file depends on every `DEPENDS_ON` it writes and on the id its header `EXTENDS`, any number of them; each names a loaded file, no two files depend on each other, a file id is declared once, an `EXTENSION` names a parent and a `BASE` does not. Part 3: a dependency loads before the file that names it; any further order is the consumer's, and the spec defines no manifest. Written as DECISION-36 and DECISION-37. | Owner: "Yes, both". Both forms are kept because migrating either would touch 923 or 5,012 files for no gain. |
| B5 | 2026-11-13 | Agent's calls, to confirm. (4) The `EXTENSION`-needs-a-parent rule is not applied to `SETTING`, `FRAME`, `ARC` or `CAMPAIGN` files, which §16 governs. (5) 14 helper files in two older fixtures were given a `DEPENDS_ON`. (6) `FROM` and `USES_*` are not counted as dependencies. | (4): 36 settings name no parent by design. (5): they were extensions with no parent, which the new rule reports. (6): not ruled on. |
| B5 | 2026-11-13 | B5 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's calls in the B5 rows marked "to confirm" were reported to him before he closed and were not separately ruled on. |
| C1 | 2026-11-13 | No value types are added. Directions: introduce `SITUATIONAL`, a value changed under a stated situation by an ordinary `TRANSFORM` with a condition; remove the `STRING` and `INTEGER` keywords "etc." | Owner: "in many, many, many games, even some something starts as a straightforward integer there are inevitably exceptions that are not integers". Measured: 75 of 329 mostly-numeric properties hold a non-number somewhere. The keyword removal is not yet ruled into a scope. |
| C1 | 2026-11-13 | `SITUATIONAL <condition> { <changes> }`: the condition is a string in the source's words or a reference to an entity; the changes are ordinary `SET` and `TRANSFORM` statements, one or more; it stands wherever a change may; the value outside the block holds otherwise; a consumer applies nothing itself. Written as DECISION-38, and the grammar and the validator check it. | Owner: "Yes, as written", to the form shown with tor2e's Long Sword (`"16 (1h)/18 (2h)"`). The reference condition was put to him as the agent's addition, "yours to strike", and he did not strike it. The inline form (`^"Injury" INTEGER 16 SITUATIONAL "2h" SET 18`) was offered and not taken. |
| C1 | 2026-11-13 | The type keywords go: `STRING`, `INTEGER`, `BOOLEAN`, `LIST` before a list and `ENUM` before a single value. `ENUM [ … ]`, `LIST OF ^"Type"` and `REF OF ^"Type"` stay as declarations. Written as DECISION-39; the grammar reads both forms and the validator refuses the old ones from 0.6. | Owner: "Yes, that scope", to "Drop STRING, INTEGER, BOOLEAN and instance-side LIST and ENUM, keeping the declaration constraints?". He had been shown the census (371,111 redundant lines; 75 of 329 mostly-numeric properties with a non-number) and a table of what each open form would become. |
| C1 | 2026-11-13 | Signed numbers and names paired with numbers get no form. Each is a `SET` or a `TRANSFORM`, decided when the source is converted; until then it stays a string as printed. Written as DECISION-40. | Owner: "Signed numbers should either be set or be transforms. This will likely be an adjudication process as part of the conversion. They will be left as strings mechanically, since we're not doing integers, etc." and, of a name with a value in a block, "Again, these are SET or TRANSFORMS". The agent had recommended a `+` on a number and a name-and-value form; neither is adopted. |
| C1 | 2026-11-13 | The entries of a list need not be named; the list is. An item of a list may be a `DEF { … }` with no name. Written as DECISION-41, and the grammar accepts it. | Owner: "List entries need not be named, just the list itself." 24,133 corpus records are written so. This replaces the agent's call (5) under B1, which kept the form refused. |
| C1 | 2026-11-13 | Agent's calls, to confirm. (1) An unnamed entry takes what a DEF's body takes. (2) It has no hash. (3) It is allowed in any bracket list, with or without `LIST OF`. (4) Its fields are still not checked against the list's type. (5) The `-` on a number stays. | (1): the corpus records hold nested properties and prose. (2) and (3): the corpora write them so. (4): not asked for. (5): `SET -1` needs it. |
| C1 | 2026-11-13 | Gating: the type keywords are legal and unreported in a file that declares a `SPEC_VERSION` below 0.6, and an error from 0.6. | Owner: "Yes, silent below". The usual warning would add about 371,000 lines to the corpus reports. It had been applied as the agent's call (1) in the next row before he ruled. |
| C1 | 2026-11-13 | Agent's calls, to confirm. (1) Gating, since ruled (row above); that the error takes no `FIAT` is still the agent's call. (2) A declaration is the name and its constraints anywhere, and the name alone only in a `PROPERTIES` block or a property `DEF`, on a line of its own. (3) `LIST` alone stays as a declaration; `LIST OF STRING` with items becomes the list. (4) `LIST OF ^"Type"` with items stays legal on an entry. (5) A parameter with no domain replaces `OF STRING`. (6) An axis with no points replaces `AXIS … INTEGER`. (7) §9's constraints stand alone. | (1): a keyword is not content. (2) was in the table he was shown; two names on a line already mean a property and its type in eight corpora. (3) to (7): what is left when the word is deleted. (6) makes an axis with no points legal, where it was an error. |
| C1 | 2026-11-13 | Agent's calls, to confirm. (8) A value stands on its statement's line: a property's value, a `REF`'s entity, the amount of a `SET` or `TRANSFORM`. §8's statement rule is rewritten around it. (9) The check of a value's kind against the type it inherits is removed at every version; `INTEGER "heavy"` is still reported below 0.6. (10) `MIN` / `MAX` bind a value only when it is a number. (11) A keyed `CHOOSE` takes a bare value. (12) Fixtures: `values-bad/03` now declares 0.5 and `04` is deleted; `tables-bad` T13 plants a different fault; `decision6.ttrpg` puts two declared names on two lines. (13) The records of earlier decisions keep the keywords they describe. | (8): with no keyword, a name alone after `REF OF ^"Type"` could be read as its entity. (9): the owner's reason for the ruling. (10): follows (9). (12): the checks those fixtures planted no longer exist at 0.6. |
| C1 | 2026-11-13 | Agent's calls, to confirm. (1) A target with no hash that names a property of the enclosing definition, written there or declared by a type it extends, is that property; any other target is a reference as before. (2) The block holds changes only, at least one, and no `SITUATIONAL` inside another. (3) Every fault is an error at every version. (4) The word is reserved everywhere in the grammar. (5) Follow-up F24 is added for the corpus strings. | (1): the approved example writes `^"Injury" SET 18`, and a property is not an entity, so the old reference check failed it. (2): the owner's form shows changes only. (3): no corpus uses the word. (4): as `TRANSFORM` and `NEXT` are. |
| C1 | 2026-11-13 | C1 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's calls in the C1 rows marked "to confirm" were reported to him before he closed and were not separately ruled on. The row order below is not the order of the day: `SITUATIONAL` was ruled first, then the keywords' scope, then their gating, then the last three forms. |
| C2 | 2026-11-13 | An entry may extend an entry: a variant that starts from the parent's values. Being extended does not make a DEF a type, and both entries are checked for what their type requires. Written as DECISION-42. | Owner: "yes.", to that proposal. 1,178 `EXTENDS` lines join an entry to a DEF that gives values. |
| C2 | 2026-11-13 | No second namespace and no path syntax. | Owner: "no change". A reference resolves by hash (DECISION-13), which already keeps apart the 50 names a type and an entry share. |
| C2 | 2026-11-13 | No marker for a type. §5 says a type is told from an entry by what it holds. Written as DECISION-43. | Owner: "why do we need a "TYPE" or "KIND" at all?", then "Yes, no marker". Measured: without a marker the rule misplaces 11 of 111,333 DEFs; a marker would be written on 1,304. The agent had recommended the marker and withdrew it. |
| C2 | 2026-11-13 | Agent's calls, to confirm. (5) §5 states the validator's exact rule: a type declares fields and gives no value of its own, or marks a field `REQUIRED`, or carries `ACTOR` or `TEMPLATE`. The question the owner answered said only "declares a field". (6) A subtype that adds no field declares one or takes an element-level `FIAT`. (7) §5 keeps its title and calls an instance an entry as well. | (5): the looser wording would make types of 282 corpus entries that hold a declaration-shaped line. (6): the two means the language already has. (7): §16 and §17 refer to the section by its title. |
| C2 | 2026-11-13 | Agent's calls, to confirm. (1) A validator defect is fixed: a type keyword on the line after a name was read as that name's type. (2) A variant has a property when the entry it extends gives it. (3) A parent's `FIAT` does not cover its variant. (4) §5's sentence on definitions and instances was left until the marker question was settled, and is now rewritten (row above). | (1): found while counting; a probe shows it and no corpus result changes. (2): §8 already let a type in between give the value. (3): `FIAT` covers a DEF and what is inside it. (4): it depends on that answer. |
| C2 | 2026-11-13 | C2 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's calls in the C2 rows marked "to confirm" were reported to him before he closed and were not separately ruled on. |
| C3 | 2026-11-13 | Four rules for references that no keyword marks. (1) A `#hash ^"Name"` pair that declares nothing is a reference wherever it stands. (2) A name that is an item of a list is a reference, with or without its hash. (3) Elsewhere in a system block a name with no hash is the system's own and is not resolved. (4) §5d's list names the places the tools already checked. A miss is a warning below 0.6 and an error from 0.6. Written as DECISION-44. | Owner: "Yes, all four". 10,290 of 730,196 corpus carets stood where no tool looked; 15 hashes in teeth were broken; of 2,249 hashless names in system blocks, 771 name nothing, so checking them all would mix broken references with labels. |
| C3 | 2026-11-13 | Agent's calls, to confirm. (1) The validator applies §5d's rules to the new places, and `check_references.py` is left as it is. (2) A list member with no hash that names one entity is a warning at every version. (3) A member that is an `ALIAS` draws no hash warning. (4) `FIAT` waives each finding. (5) A name inside an unnamed record of a list is the record's property. (6) `tests/decision6.ttrpg` is unchanged; the alias rule (3) came from it. | (1): the validator has the bracket context, the file's version and the waivers. (2): §5d rule 2 says a hashless reference warns. (3): an alias has no hash to carry. (4): as for every gated finding. (5): DECISION-41. |
| C3 | 2026-11-13 | C3 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's calls in the C3 row marked "to confirm" were reported to him before he closed and were not separately ruled on. |
| C4 | 2026-11-13 | No construct for provenance. (1) The page is the property `^"Page"`: a number, or what the source prints as text. (2) No field for the book. (3) §4 keeps its rule: a page in a comment is a note that no tool reads. Written as DECISION-45. | Owner: "Yes, all three". The corpora already write `^"Page"` 23,932 times; one tool reads a page; the file's `NAME` and `sources.json` name the book. |
| C4 | 2026-11-13 | Agent's calls, to confirm. (1) No check is added for the page. (2) §4 drops "page references, source attributions" from what comments are for, and says a comment may still mention them. (3) The spec says a corpus's register names the book and does not state that a file holds one source. (4) Renaming `^"Pages"` and `^"Source Page"` is corpus work (F28). | (1): not asked for; a value is not typed. (2): the ruling's part 3. (3): one source per file is the corpora's rule and is not in the spec. |
| C4 | 2026-11-13 | C4 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's calls in the C4 row marked "to confirm" were reported to him before he closed and were not separately ruled on. |
| C5 | 2026-11-13 | Part 1, tables: nothing more to rule. An open-ended key is `AT [ MIN n ]`; a d66 is a die a system defines and is not added to the shared dice module. | Owner: "Agreed". `TABLE` has had its form since DECISION-21, and only troika uses d66. |
| C5 | 2026-11-13 | Part 2, string escapes: §10 lists the seven the grammar names (`\"`, `\\`, `\/`, `\n`, `\r`, `\t`, `\uXXXX`); a backslash before anything else is a warning below 0.6 and an error from 0.6; a triple-quoted string reads no escapes. Written as DECISION-46. | Owner: "Yes, seven". The corpora use four of the seven and no other; the alternative of listing only those four was not taken. |
| C5 | 2026-11-13 | Part 3, what verbatim allows: a string matches its source after five allowances and no others: Unicode form (NFC); white space; quote style; the repair of page layout (line-end hyphenation, soft hyphens, ligature glyphs); decoded HTML entities. The kind of a dash, punctuation, capitals and wording are content. Written as DECISION-47. | Owner: "Yes, those five". §5c named a "standard normalisation" that nothing defined. The first three allowances are the name rule of DECISION-33. |
| C5 | 2026-11-13 | Part 4, text of several paragraphs: one method only, a single string with `\n\n` between paragraphs. The other approaches are to be converted: a triple-quoted block and a string over a raw line break are a warning below 0.6 and an error from 0.6. Written as DECISION-48. | Owner: "let's just use the Paragraphs method; we should ultimately convert the other approaches over." The agent had proposed four rules, among them a dedent rule that kept triple-quoted blocks; that rule is not adopted. |
| C5 | 2026-11-13 | Agent's calls, to confirm. (1) "The other approaches" is read to include the triple-quoted block, which becomes an error from 0.6. (2) Strings in a row stay legal as separate entries and are not reported. (3) A validator crash on bridges with an `ALIASES` block, present since B2, is fixed. (4) The agent's fixture run now includes the bridge and codex fixtures and the two real bridges. | (1): §10 gave three approaches and he kept one. (2): no tool can tell a list of entries from a text split into strings. (3) and (4): the crash went unseen for six commits because those files were not run. |
| C5 | 2026-11-13 | Part 5, order: the order of statements in a block carries meaning only in a `NEXT` chain, in the items of a list and in bare strings in a row. A file keeps its source's order for display. Headings get no form of their own. Written as DECISION-49. | Owner: "Yes, as stated". The spec's one sentence on order sat in the dice section and denied any order. |
| C5 | 2026-11-13 | Part 6, hash stability: a hash is stable within a major version. Every state of a system's `0.5` corpus gives an entity the same hash; a new major version may mint new ones. Written as DECISION-50. | Owner: "Hashes are considered stable within same major versions (ie, all 0.5 instances should be hash-stable)." The agent had proposed stability from publication on, with no bound; his rule sets the bound at the major version. |
| C5 | 2026-11-13 | Part 7: an `EMPHASIS` block is legal in a guidance `ENTRY`, each span being in that entry's `TEXT`; `BASE` stays reserved everywhere and arm5e's `BASE n` lines are renamed with F5. Written as DECISION-51. | Owner: "Yes, both". The agent had first recommended keeping `EMPHASIS` out and changed that before he ruled: an entry's `TEXT` is verbatim, and emphasis is recorded beside verbatim text. |
| C5 | 2026-11-13 | C5 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's calls in the C5 section and rows marked "to confirm" were reported to him before he closed and were not separately ruled on. |
| C6 | 2026-11-14 | Part 1: the spec gains no "provisional" status for a form nothing writes. Candidate improvement 7 is not taken; each unused form is ruled on its own in parts 2 to 4. To be taken up once C1 to C9 are closed: §24 (Optional & variant rules), and `ADD_TO`, `REMOVE_FROM`, `@n` and `.selections`. | Owner: "I agree to no provisional status, but I would like to follow up on the following issues once we're done with the C# items", with that list. The agent had recommended no status: the list is eight forms, a status needs rules of its own, and it would also mark the forms new in 0.6. |
| C6 | 2026-11-14 | Part 2: three forms are removed. (a) The rule form `#hash MODIFY: label NOW REFERENCES …`; a `MODIFY` changes a rule by writing it whole under its hash. (b) `REFERENCED BY`. (c) `MENTIONS`, with the second half of §5c rewritten under `REFERENCES`. Each is a warning below 0.6 and an error from 0.6. Written as DECISION-52. | Owner: "a. remove the form. b. remove. c. remove the alias, and rewrite that half of §5c with REFERENCES." No file in 29 corpus directories writes any of the three. The first was shown once in §13 and defined nowhere, and the grammar refused it. The second repeated a `REFERENCES` line. The third was the block's 0.4 name. |
| C6 | 2026-11-14 | Agent's calls, to confirm. (1) `USES_SETTING` and `USES_FRAME` were taken out of part 2 before he ruled and put with `USES_EXTENSION` in part 5. (2) `MENTIONS`, `REFERENCED` and `BY` stay reserved. (3) §13 is silent on a rule entry under a hash the target has no rule for. (4) No `FIAT` waives the three findings. (5) `check_references.py` reads past a `REFERENCED BY` block and checks nothing in it. (6) Five example strings in §5c that ran over a raw line break are joined to one line each. | (1): one rule should cover the three `USES_` lines. (2): the same treatment as `STRING` under DECISION-39. (3): he ruled on replacement, and no corpus adds a rule in a `MODIFY`. (4): the other older forms take none. (5): the validator reports the block. (6): DECISION-48 made the form an older one and C5's sweep of the spec missed these five. |
| C6 | 2026-11-14 | Part 3: four forms are marked as likely to be replaced, and the validator warns wherever one is written, at any `SPEC_VERSION`: `ADD_TO` and `REMOVE_FROM`; the `@n` occurrence index; the `.selections` file; `OVERRIDE` and `ADD … DEF`. Each reads as it did. No replacement is ruled. Written as DECISION-53. | Owner: "flag all four of these as likely to be replaced and make them WARN if present, but we won't do the replacements just yet." The agent had recommended keeping the four unchanged. None of the 22 corpus directories writes any of them; third-party corpora write `OVERRIDE` 3 times and `ADD … DEF` 74 times. |
| C6 | 2026-11-14 | Agent's calls on part 3, to confirm. (1) Written as DECISION-53, in the words "likely to be replaced". (2) The warning is the same at every `SPEC_VERSION` and takes no `FIAT`. (3) The validator reports a `.selections` file without reading it; `check_constructs.py` is unchanged. (4) `ADD` as a `TRANSFORM` method is not marked. (5) §24's `OPTIONAL` block is not marked. | (1): part 1 ruled out a status for every unused form, and this marks four named ones. (2): he said "WARN if present" and named no version. (3): the validator is the tool that counts warnings. (4): the form in part 3 was `ADD … DEF`. (5): he named the four forms of part 3, and §24 is on his list for after C9. |
| C6 | 2026-11-14 | Part 4: `FORMALITY CONDITIONAL`, `FORMALITY FORMAL` and a `TRIGGER` inside a `HOOK` are marked as likely to be replaced, and the validator warns wherever one is written, at any `SPEC_VERSION`. Each reads as it did. `PROSE` and `TAGGED` are not marked. No replacement is ruled. Written as DECISION-54. | Owner: "mark as likely to replace and warn." The agent had recommended removing the three: the corpora write three hooks, all `TAGGED`, and §23 gives a `TRIGGER` no shape. He chose the part 3 treatment. |
| C6 | 2026-11-14 | Agent's calls on part 4, to confirm. (1) Written as DECISION-54. (2) A warning at every `SPEC_VERSION`, with no `FIAT`. (3) `TRIGGER` is marked inside a `HOOK` only. (4) §23's example and the 0.5 sample keep their `CONDITIONAL` hook and `TRIGGER`. | (1): a second ruling on other forms. (2): the terms of part 3. (3): outside a hook the word is a system's own (§15). (4): the forms still read, and he ruled no rewrite. |
| C6 | 2026-11-14 | Part 5: `USES_EXTENSION`, `USES_SETTING` and `USES_FRAME` fold into `DEPENDS_ON`. A file names every file it needs with `DEPENDS_ON`, and the id may be that of any loaded file. Each `USES_` line is a warning below 0.6 and an error from 0.6. Written as DECISION-55. The 26 lines in five repos are F32. | Owner: "Fold into DEPENDS_ON". The agent had recommended keeping the keywords and checking them. No tool read the lines, three of the 26 name no file, and `DEPENDS_ON` is the same statement with a check behind it. |
| C6 | 2026-11-14 | Agent's calls on part 5, to confirm. (1) A `USES_` line is reported and not read as a dependency. (2) `DEPENDS_ON` accepts the id of a SETTING, a FRAME, an ARC or a CAMPAIGN. (3) The three keywords stay reserved. (4) §16's rules keep their counts ("exactly one BASE"), which no tool checks. (5) The grammar is unchanged. | (1): the line's id is checked once it is rewritten, and an older form is reported once. (2): §3 already said "Each names a file in the loaded set", and the fold needs it. (3): as `STRING` and `MENTIONS`. (4): he ruled on the keyword. (5): it never named the three keywords. |
| C6 | 2026-11-14 | Part 6: the rule form `WHEN [condition] THEN action` is removed. A rule is a label with the source's text, or a DEF with a `DESCRIPTION`. A warning below 0.6 and an error from 0.6. `WHEN` and `THEN` stay a hook's keywords. Written as DECISION-56. The 31 rules in nine core base files are F33. | Owner: "Yes, remove". The agent had recommended it: no tool read the condition or the action, and each of the 31 is in the converter's words. The proposal's count was 27; four more, with no hash, are in Draw Steel. |
| C6 | 2026-11-14 | Agent's calls on part 6, to confirm. (1) §12 and §14 quote two rules from the l5r5e corpus. (2) §17's L5R example marks `School` `REQUIRED` in place of its `REQUIRE` rule. (3) §17's VTM example loses its `RULES` block. (4) §15's "Rule structure" line goes; `WHEN` and `THEN` are hook keywords. (5) `WHEN [` is reported wherever it opens a statement. (6) The grammar still reads the form. (7) The no-text warning no longer offers the removed form. | (1): an example of a rule should be a rule a book prints. (2): the rule said both were required. (3): its two rules were paraphrase, and the corpus has no text for them. (4): the rule use is gone. (5): every one in the 29 directories is in a `RULES` block. (6): as it does `MENTIONS`, for files below 0.6. (7): it would have told an author to write a removed form. |
| C6 | 2026-11-14 | Part 7: an alias is a second name of a hash, written `ALIAS ^"name" FOR #hash`; the entity's own name may follow the hash. `#hash ^"name"` is a pair that agrees. An alias `FOR` a name with no hash, and `ALIAS "name"` inside a DEF, are older forms: a warning below 0.6 and an error from 0.6. Written as DECISION-57. The nine corpus lines are F34. | Owner, on the proposal to report the in-DEF line: "would it make sense instead to have ALIAS function kind of like \"ALIAS [hash] [alias name]\", so that it's a separate name that resolves to the same hash?"; then, given two spellings: "ALIAS name FOR #hash". A reference through an alias that carried the entity's hash was an error in `check_references.py`. His own spelling reads as a hash-name pair that disagrees, which every tool reports; the one chosen keeps armdef's four statements valid. |
| C6 | 2026-11-14 | Agent's calls on part 7, to confirm. (1) `ALIAS "name"` inside a DEF is reported, though he ruled on the spelling and did not say so in words. (2) `FOR` a name with no hash is an older form. (3) The target's name is read on the hash's line only. (4) A hashed alias written as a list member with no hash is warned like any member. (5) The validator leaves the check of a name after the hash to `check_references.py`. (6) An alias of a bound reference is left as §5b had it. (7) Bridge aliases are untouched. | (1): the agent's message said the nine lines "are still reported" whichever spelling he picked, and he picked one. (2): the table he chose from said "hash required". (3): §8's rule for where a statement ends. (4): the exemption existed because an alias had no hash. (5): as before the change. (6): no corpus writes one, and it was named to him as open. (7): they are sided and by name, and he was told they would be left. |
| C6 | 2026-11-14 | C6 is closed. The branch is committed and pushed. | Owner: "commit and push, then move on to the next". He did not say "close"; the agent read moving on as closing it. The agent's calls marked "to confirm" in parts 2 to 6 were reported to him as each part was applied, and those of part 7 with the commit; none was separately ruled on. |
| C7 | 2026-11-14 | A check and a reward are the system's: the base spec defines neither and reserves none of their keywords, and §16 shows two systems' checks as examples that are no part of it. Written as DECISION-58. No file changes. | Owner: "why isn't it entirely delegated to the system? I don't think generic fields are helpful here, these should be system-specific. The base spec can provide a couple examples, but those examples are not part of the base spec." The agent had proposed to keep the frame of a check in the base. No tool reads the frame, three systems write a check, and one of them already uses its own field. |
| C7 | 2026-11-14 | Agent's calls, to confirm. (1) `REWARDS` and its fields go with the check. (2) §16's l5r5e example arc keeps its `CHECKS` and `REWARDS`, labelled as l5r5e's. (3) §16's rules for writing an L5R check leave the spec (F35). (4) `MONTAGE` and `MOMENT` stay in §18. (5) `CLUES`, `CONFLICT`, `OBJECTIVES` and `RESOLUTIONS` stay. (6) §15's example of a block keyword used elsewhere is now `TRIGGER`. | (1): C7 names `XP_BASE` and `XP`, and only l5r5e writes them. (2): it is a real l5r5e arc. (3): they are L5R's rules. (4): C7 does not name them. (5): five or six systems write each. (6): `SKILL` is no longer a base keyword. |
| C7 | 2026-11-14 | C7 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's calls in the row above were reported to him before he closed and were not separately ruled on. |
| C8 | 2026-11-14 | Part 1: every file declares its edition. `EDITION "id"` stands in the header of every BASE, EXTENSION, FRAME, ARC and CAMPAIGN; without it a file is a warning below 0.6 and an error from 0.6. A run holds one edition, and a `--corpus x=<dir>` directory holds edition `x`. Written as DECISION-59. The corpus work is F36. | Owner: "In every file". The agent had recommended a declaration in BASE files only, about 55 lines against about 6,500, with nothing restated. No file named its edition, and the directory name is wrong for two third-party trees. |
| C8 | 2026-11-14 | Agent's calls on part 1, to confirm. (1) The keyword is `EDITION`. (2) Absence below 0.6 is a warning, one for each of 6,280 files in the 22 directories. (3) A SETTING may declare none. (4) The dice module declares none. (5) A codex and a bridge are left to part 2. (6) Two editions in a run is one error. (7) An id is any string. (8) A bare `.actor` gets the line with its wrapper. | (1): a codex already writes `FOR EDITION`. (2): the terms of every new requirement in 0.6. (3): §16 calls a setting system-agnostic. (4): §19 calls it edition-neutral. (5): each points at editions. (6): §19 says nothing resolves across one. (7): no list of editions exists. (8): it has no header. |
| C8 | 2026-11-14 | Part 2: a codex declares its edition as every file does, `EDITION "id"`. `FOR EDITION "id"` is the older form: read as the same line, a warning below 0.6 and an error from 0.6. A bridge's sides and a port's `ORIGIN` are unchanged. Written as DECISION-60. | Owner: "Yes, fold it". The agent had recommended it: `FOR EDITION` named the codex's own edition in a second spelling, 69 files write it and no tool read it. |
| C8 | 2026-11-14 | Agent's calls on part 2, to confirm. (1) A codex with no edition is reported. (2) `FOR EDITION` below 0.6 is read as the codex's edition. (3) `samples/` is validated as two editions. (4) A bridge's sides, a port's `ORIGIN` and `.selections` are untouched. | (1): the proposal said so, and he ruled on it. (2): an older form is read. (3): its two samples are about two games. (4): the first two share a keyword and are covered by part 1's `--corpus` check; the third is marked as likely to be replaced. |
| C8 | 2026-11-14 | Part 3: the `VERSION` beside an edition is its corpus's content version, the version each of the corpus's files' `VERSION` begins with. The validator checks a bridge's side against the corpus it is given: a warning below 0.6 and an error from 0.6. Written as DECISION-61. Four sides of the three bridges are reported: F37. | Owner: "Define and check it". §21 said a side pins "a content `VERSION`" and no tool read it; the three bridges meant three things by it. DECISION-50 makes an edition and a content version the span of a hash. |
| C8 | 2026-11-14 | Agent's calls on part 3, to confirm. (1) "Begins with" is exact on the parts given. (2) A file with no `VERSION` is not counted. (3) Nothing checks that a corpus's files share a content version. (4) A side with no `VERSION` is not reported. (5) `.selections` is left. (6) §21's example keeps `"0.4"`. | (1): a hash namespace is one version, where a dependency pin is a floor. (2): there is nothing to compare. (3): he ruled on the line beside an edition. (4): §21 makes it optional. (5): it is marked as likely to be replaced. (6): it is a 0.4 example. |
| C8 | 2026-11-14 | C8 is closed. The branch is committed and pushed. | Owner: "Close, commit, push". The agent's calls marked "to confirm" in parts 1 to 3 were reported to him as each part was applied and were not separately ruled on. |
| C9 | 2026-11-14 | Bullet 1: each edition has a `.system` file. `SYSTEM "id"` is the edition; `KEYWORDS` lists the system's own keywords by name; `FILES` is the index of its files by path. With one in the run the validator reports an undeclared keyword, a file the index leaves out and a `VERSION` that does not begin with the system's: a warning below 0.6, an error from 0.6. Written as DECISION-62. The 22 system files are F38. | Owner: "Let's do something like this: l5r5e.system adds the system-specific primitives and also holds the index of any/all files associated with it"; then, on the concrete shape: "Yes, apply it". The agent had recommended leaving the vocabulary undeclared, since a scan of 7,055 files found no misspelling. |
| C9 | 2026-11-14 | Added to the list for after C9: a campaign's load file. | Owner: "we should flag a follow-up so that a campaign can declare appropriate systems/settings/etc to have all the necessary primitives/select rule variants/etc. Probably a \".campaign\" load file that tells how to build the codex, etc, maybe? discussion for later." |
| C9 | 2026-11-14 | Agent's calls on bullet 1, to confirm. (1) No system file in the run gives a note, not a warning. (2) The validator holds the base keywords as a list of 173, with `ROW`. (3) A base keyword used outside its block is not declared. (4) A keyword is a capitalised word that opens a statement. (5) A file with no edition is held to the system file only when the run has one. (6) A bare `.actor` is not held to it. (7) A system's id is not a file id. (8) A file's `VERSION` is checked against the system's. | (1): a warning would stand on every fixture and single-file run. (2): the tool cannot read the spec, and `ROW` is the older table form. (3): §15 already lets a system use it. (4): that is where the corpora write theirs. (5): two systems in a run cannot say whose it is. (6): it has no header. (7): nine BASE files are named for their edition. (8): the system file states the version. |
| C9 | 2026-11-14 | Bullet 3: a guidance entry may hold `REFERENCES`, each surface form being in that entry's `TEXT`; its kind stays one of its `TOPICS`, with no list in the base spec. Its place is its `^"Page"`, as DECISION-45 has it. Written as DECISION-63. | Owner: "Yes, both". `check_references.py` read the block already and §22 did not allow it; none of 11,027 entries writes one. The corpora write the kind as a topic. |
| C9 | 2026-11-14 | Agent's calls on bullet 3, to confirm. (1) The grammar reads `^"Page"` in an entry. (2) The grammar was not rerun over the corpora. (3) `"Sidebar"` and `"sidebar"` are noted and not ruled. | (1): DECISION-45 gave every block a page. (2): no corpus entry holds either new form. (3): a corpus matter. |
| C9 | 2026-11-14 | Bullet 4 (`HOOKS`) deferred: whether a hook's `WHEN` is the source's own sentence, and how a hook points at it. Nothing in the spec or a tool changes. Added to the list for after C9. | Owner: "I think we need to defer a decision here, flag it for follow-up". The agent had proposed a verbatim `WHEN` checked against the enclosing DEF's text; the three corpus hooks already comply. |
| C9 | 2026-11-14 | Bullet 6, part 1: a codex entity is its hash. An `ENTITY` writes its hash; a file adds to an entity by restating that hash and name; no block is first; the same name under another hash is a collision; at least one block of an entity holds `IS`. Written as DECISION-64. The 114 l5r5e names are F39. | Owner: "a later file should only modify an existing hash, otherwise it's a collision and it should flag an error. Please let me know if I'm missing anything." The agent had proposed adding by hash and had left one name under two hashes as two entities. |
| C9 | 2026-11-14 | Agent's calls on bullet 6 part 1, to confirm. (1) "Modify" is read as restating `ENTITY #hash ^"Name"`, with no `MODIFY` statement. (2) The collision is a warning below 0.6 and an error from 0.6. (3) An `ENTITY` with no hash and an entity with no `IS` are reported at the same levels. (4) No `IS` finding for a name in collision. (5) An older fixture, `tests/anchors-good/lore.codex`, gains an `IS`. | Recorded under the bullet. |
| C9 | 2026-11-14 | Bullet 6, part 1, the level: the collision is an error at every version. The other two checks stay a warning below 0.6 and an error from 0.6. | Owner: "first of all, I'm ok with the stricter interpretation; the l5r5e situation where you have two different defs of the same thing means that there's an error in those files, so we should throw an error." The agent had made it a warning below 0.6. |
| C9 | 2026-11-14 | Bullet 6, part 2: lore and mechanics keep separate identities. A codex entity and a DEF of one name are two things, each under its own hash; the base spec defines no link and no tool compares them. Written as DECISION-65. | Owner: "We should consider separating identities between lore and mechanics, because they are often only semi-overlapping. In general and for now, it should be normal for there to be the same thing named in multiple places meaning distinct things. Context and hash references should be sufficient to distinguish. I don't think we need a more rigorous approach defined in the base spec." The agent had proposed that such an entity write the DEF's hash. |
| C9 | 2026-11-14 | Added to the list for after C9: a set of unique identifiers for lore, beside those of the mechanics. | Owner: "Let's mark for a review the idea of a parallel unique ID system in lore, but that's not immediately in scope." |
| C9 | 2026-11-14 | Agent's calls on bullet 6 part 2, to confirm. (1) An edge's object may carry its hash, checked as at any site; the grammar and the validator had refused one. (2) An object with no hash is read as before. (3) A category, an `IS` and an edge's object may still name a game DEF. (4) Spec text is added for the ruling. | Recorded under the bullet. |
| C9 | 2026-11-14 | Added to the to-do: how a codex tells apart two things of one name. The hash on an edge's object stands for the meantime; no form of disambiguation is ruled. | Owner: "we should update codex to handle this adequately, which probably involves some kind of disambiguation. Add this to the to-do." |
| C9 | 2026-11-14 | Bullet 6, part 3: every codex edge cites its own source, `SOURCE "file" [AT "heading"]` after its object and its `FROM`. It does not take its block's. A block's `SOURCE` is where the subject is described and may be written more than once. Written as DECISION-66. The 1,282 l5r5e edges are F40. | Owner: "why can't we invert it; each edge cites its source?"; then, on whether an edge with none takes its block's: "Always on the edge". The agent had proposed one `SOURCE` to a block with its edges read as drawn from it, and then a source on the edge with the block's as the fallback. |
| C9 | 2026-11-14 | Agent's calls on bullet 6 part 3, to confirm. (1) The form is `SOURCE "file" AT "heading"` after `FROM`. (2) `AT` is optional on an edge. (3) A block may hold more than one `SOURCE`. (4) `FROM` stays optional and unchecked. (5) The sample keeps its lore file's name. (6) The sample's Bilbo edge is left with no source. | Recorded under the bullet. |
| C9 | 2026-11-14 | Bullet 6, part 4 deferred: whether a codex may record a date or a number as a fact. Nothing in the spec or a tool changes. Added to the list for after C9. | Owner: "defer decision on this." The agent had recommended leaving it. |
| C9 | 2026-11-16 | Bullet 7, point 1: `DISPOSITION` is optional on a bridge `MAP`. A `MAP` with none asserts the correspondence and nothing about the kind of change. A `REMAINDER` still requires one. Written as DECISION-67. The Pendragon bridge is F41. | Owner: "Let's go with this", on the agent's proposal as put. |
| C9 | 2026-11-16 | Agent's calls on bullet 7 point 1, to confirm. (1) Not gated by version. (2) A `MAP` may go untagged in a document that declares tags. (3) A consumer does not take an untagged 1 to 1 `MAP` for a rename where its `TEXT` does not say. (4) A renamed thing whose value carries across takes a `MAP` and a `CONVERT`. | Recorded under the bullet. |
| C9 | 2026-11-16 | Bullet 7, point 2: `SCALE` states the arithmetic and no rounding. A result that is not whole is rounded by the game's general rounding rule where it prints one; where it prints none, a reader may flag the conversion as wanting a ruling. No keyword and no check. Written as DECISION-68. | Owner: "Most games have standard rules for how to handle rounding; by default, we should defer to those procedures if they exist. Otherwise this is something that can optionally be flagged as something of possible concern but would need adjudication from some source if there were no default heuristics to use." The agent had proposed that a document's stated rounding go in a `MANUAL` line. |
| C9 | 2026-11-16 | Agent's calls on bullet 7 point 2, to confirm. (1) The game whose rule applies is the destination edition. (2) No field names a system's general rounding rule; the spec says so, and the validator reports nothing. (3) The spec names arm5e as a destination with no general rule found. (4) A rounding stated by the conversion document itself is not written. | Recorded under the bullet. |
| C9 | 2026-11-16 | Bullet 8: what a name holds. An empty name and a control character in a name are each a warning below 0.6 and an error from 0.6; a name with no letter and no digit is a warning at every version. Written as DECISION-69. The corpora's 29 names are F42. | Owner: "Yes, all three", on the agent's three points as put. |
| C9 | 2026-11-16 | Agent's calls on bullet 8, to confirm. (1) One decision number. (2) A control character is Unicode category Cc; a tab, a line break and a format character are not reported. (3) The no-letter warning is made at a reference and an entry's label too. (4) The grammar does not refuse `^""`. (5) Nothing waives the warning on the tor2e row. | Recorded under the bullet. |
| C9 | 2026-11-16 | C9 is closed. The branch is committed and not pushed. | Owner: "Close and commit". The agent's calls marked "to confirm" under bullets 1, 3, 6, 7 and 8 were reported to him as each was applied and were not separately ruled on; he was told that they stand as written if C9 is closed without going through them. |

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
