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
