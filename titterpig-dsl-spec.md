# Titterpig DSL Specification v4

> **Status: v4 (current, canonical).** Supersedes v0.3. Historical docs live in `archive/`;
> `AUTHORING-GUIDELINES.md` holds system-specific authoring best-practices. The `ttrpg.peg`
> grammar and `ttrpg_validator.py` are v0.3-era and **pending realignment** to v4.

## 0. What changed in v4

v4 is a consistency/clarity pass over v0.3's grammar — not a redesign. Key changes:

1. **Structure over prose (new core principle).** Mechanically-critical data must be structured,
   never buried in opaque strings or comments (§1 → *Structural Representation*;
   `AUTHORING-GUIDELINES.md`).
2. **Canonical instance form** is `^"Name" DEF { PROPERTIES { ... } }`. Flat `key: value` /
   `METADATA`-style property forms seen in some sourcebook files are **non-canonical** and are
   migration targets.
3. **Hash IDs are opaque, globally unique, `≥16` chars, and carry no semantics** a tool relies on
   (§5, §14). Short/prefixed IDs in the examples below are illustrative and predate this rule.
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

## 1. Overview & Design Principles

Titterpig is a domain-specific language (DSL) for defining tabletop role-playing game (TTRPG) systems, content, and narrative structures. The base specification defines a **system-agnostic syntax toolkit** — it owns the grammar, while each game system owns its vocabulary.

### Design Principles

1. **Readable**: Files should read like game rules documentation
2. **Declarative**: Describe what exists, not how to compute it
3. **Composable**: Definitions can be layered, extended, and combined across files
4. **Type-safe**: Properties carry type information and constraints
5. **System-agnostic**: The same grammar supports L5R, VTM, Ars Magica, and any other TTRPG — without changes to the base spec
6. **Structured, not prose** *(v4)*: Mechanically-critical data is represented as structured DEFs/properties, never buried in opaque strings or comments (see *Structural Representation* below)

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

### Structural Representation *(v4)*

The base spec is permissive: the grammar accepts almost any well-formed block. That flexibility must **not** be used to bury data in prose. **Mechanically-critical data — anything a tool will read (bonuses, costs, dice, ranks, stats, prerequisites) — must be represented structurally, not packed into free-text strings or comments.**

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
| `.lore` | (none — Markdown) | **Free narrative prose / flavor** — no DSL syntax *(v4)* |

The `.actor` extension is a convenience alias: an `.actor` file is a `.ttrpg` file scoped to exactly one character definition (a single `DEF` block). It uses identical syntax to a DEF within an EXTENSION but exists as a standalone file, making it easy to share, version, or reference individual characters independently of the containers they appear in.

### Structured Narrative vs. Free Prose (`.setting`/`.frame` vs `.lore`) *(v4)*

Narrative content splits by whether tools need to *query* it:

- **Structured narrative → `.setting`, `.frame`, `.arc`, `.campaign`** (DSL syntax). Use these when the content has addressable, cross-referenced parts a tool consumes — locations, factions, NPC stat blocks, scenes, hooks, timelines. These carry hash IDs and caret references.
- **Free prose → `.lore`** (Markdown, no DSL). Use this for readable flavor and world description meant for humans — history essays, cultural color, fiction. A `.lore` file is **not** parsed as DSL.

Rule of thumb: if a tool must look something up in it, it's `.setting`/`.frame`; if it's just meant to be read, it's `.lore`. The same subject may appear in both (a mechanical `.setting`/`.ttrpg` entry plus a `.lore` essay).

### File Organization

Files are organized as:
- `systems/{system_id}/core.ttrpg` — Base system definitions
- `extensions/{system_id}/{extension_id}.ttrpg` — Extensions, errata, sourcebooks, house rules
- `settings/{setting_id}.setting` — World-building and lore
- `frames/{system_id}/{frame_id}.frame` — Campaign scaffolds
- `arcs/{system_id}/{arc_id}.arc` — Playable adventures
- `campaigns/{system_id}/{campaign_id}.campaign` — Multi-arc campaigns
- `actors/{character_id}.actor` — Individual character definitions (PC or NPC)

---

## 3. File-Level Structure

Every `.ttrpg` file opens with either a `BASE` or `EXTENSION` declaration. These are the only two file-level wrappers.

### BASE — Standalone Module

A BASE defines a self-contained ruleset module. It has no parent.

```
BASE "FileID" {
    NAME "Human-readable Name"
    VERSION "0.1"
    SPEC_VERSION "4.0"
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
- `SPEC_VERSION` *(v4)*: The DSL-spec version this file targets (e.g., `"4.0"`). Distinct from `VERSION`; lets tooling detect spec conformance.
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

**Rule (v4): comments MUST NOT carry data a tool needs.** Anything a parser or downstream tool must read — corrections, values, stats, cross-references — belongs in structured DSL, not a comment. Corrections in particular go in machine-readable errata files (§13), never as `# … should read …` notes. A comment must be safe to strip without losing meaning.

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

### ACTOR Definition (character template)

```
#hashID ACTOR "Name" DEF {
    # body
}
```

`ACTOR` is an optional semantic marker indicating this DEF represents a character template (PC or NPC archetype). It has no syntactic effect — it's documentation for humans and tooling. ACTOR DEFs typically have PROPERTIES and RULES blocks defining the character schema.

### Hash IDs *(v4 rules)*

Hash IDs are optional cross-reference anchors on any DEF or rule. When present:

- **Opaque:** the ID carries no semantics a tool relies on. Do **not** encode system, category, or sequence meaning that code parses out of the ID — that information lives in fields.
- **Globally unique** across the whole corpus.
- **Format:** `#` followed by `≥16` alphanumeric characters (`[A-Za-z0-9]{16,}`).
- A short, non-semantic readability prefix is *tolerated* (e.g. `#L5R…`) but must not be depended on; two files' IDs must never collide.

```
#L5Rk3nP8mQ2vX7wZ9tB4cD1    ← opaque, ≥16 chars, globally unique
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

### Definitions vs. Instances *(v4)*

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

Both forms are valid. **`EXTENDS ^"Name"` (by name) is canonical and sufficient;** the hash is optional and adds cross-file traceability. When both are present they must refer to the same definition. *(v4: validation must accept the by-name form — the v0.3-era validator wrongly required a hash. That is a validator bug to fix, not a spec rule.)*

---

## 7. Scope (APPLIES TO)

`APPLIES TO` declares which actor types a definition can be attached to. This is a scope constraint, not inheritance.

> **DECISION-1 (resolved, v4):** `APPLIES TO` has historically been overloaded for three jobs — scope (attachment), type inheritance, and category tagging. **v4 restricts it to scope only.** Use `EXTENDS` for type / `is-a` relationships, and a dedicated tag (e.g. `^"Category" ENUM [...]` or `TAGS [...]`) for categorization. Files that used `APPLIES TO` for inheritance or tagging are migration targets.

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
| BOOLEAN | `BOOLEAN [DEFAULT true\|false]` | True/false |
| ENUM | `ENUM ["val1", "val2", ...]` | Constrained choice |
| LIST | `LIST ["val1", "val2"]` | Literal list of values |
| LIST OF | `LIST OF ^"TypeName"` | Typed collection referencing another DEF |
| LIST OF STRING | `LIST OF STRING [values]` | Typed collection of strings with optional defaults |
| DEF (nested) | `^"Name" DEF { ... }` | Nested structured object |

### Modifiers (apply to any type)

- `REQUIRED` — must be provided
- `FIXED` — cannot be changed after creation
- `DEFAULT value` — default value if not provided
- `MIN n` / `MAX n` — range constraints (INTEGER)
- `FIAT "reason"` *(v4)* — waive validation for this value (intentional exception; see *FIAT* below)

### Inline Value Assignment

A property can include its value inline at declaration time:

```
^"School Name" STRING "Hida Defender" FIXED
^"Clan" STRING "Crab"
^"Combat Conflict Rank" INTEGER 2
^"In-Clan Disciplines" LIST OF STRING ["Celerity", "Potence", "Presence"]
```

### FIAT — Intentional Exceptions *(v4)*

`FIAT` is an author's assertion that a value or element is **intentionally correct and complete**, even where it would otherwise fail validation. It suppresses validation findings — both **constraint** violations (`MIN`/`MAX`/`ENUM`/type) and **completeness** requirements (`REQUIRED` / missing fields) — within its scope. A **reason string is required**: `FIAT` is a documented, auditable exception, never a silent mute. (It is the machine-readable way to record intent — a `# this is fine` comment is not valid, since comments carry no data in v4.)

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
    ^"Hida" "+1 Earth or Fire, +1 Command, +1 Tactics, Glory 44, 4 koku"
}

HERITAGE_TABLE {
    1 ^"Famous Deed" DEF {
        MODIFIERS { ^"Glory" "+3" }
        SUB_TABLE "1d10" {
            "1-2" "A famous weapon: Receive one weapon of rarity 7 or lower"
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
- `#hashID: label_name` — named rule placeholder (description lives in comments or documentation)

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

Within a `MODIFY` block:
- `SET` — change a property value or constraint
- `ADD_TO` — append to a list property
- `REMOVE_FROM` — remove from a list property

### MODIFY in Rules

Extensions can also modify individual rules within a DEF:

```
^"Blood Potency" MODIFY {
    RULES {
        #5Gpn6DrSZp MODIFY: blood_surge_mechanics NOW REFERENCES #YD4PosF ^"Blood Surge Table"
    }
}
```

### Errata & Corrections *(v4)*

Errata and corrections are **data, not commentary.** They MUST be expressed as machine-readable `MODIFY` / `OVERRIDE` / `ADD` inside a dedicated **errata EXTENSION file** named `*-errata-*` that depends on the corrected module. Source files stay pristine; tooling composes the overlay deterministically.

```
EXTENSION "L5R5e_Core_Errata" EXTENDS "L5R5e_Core" {
    NAME "L5R5e Core — Errata"
    VERSION "2020.1"
    SPEC_VERSION "4.0"

    MODIFY ^"Hida Defender" {
        SET ^"Starting Honor" DEFAULT 45   # p.65 correction (annotation only)
    }
}
```

Writing a correction *as* a comment (`# p.65 … should read …`) is **non-conformant** — comment-only corrections are lost the moment a tool strips comments.

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

**Definition:** `DEF`, `ACTOR`, `PROPERTIES`, `RULES`

**Types:** `STRING`, `INTEGER`, `BOOLEAN`, `ENUM`, `LIST`, `OF`

**Modifiers:** `REQUIRED`, `FIXED`, `DEFAULT`, `MIN`, `MAX`, `FIAT`

**Scope:** `APPLIES`, `TO`, `ALIAS`

**Rule structure:** `WHEN`, `THEN`

**Modification:** `OVERRIDE`, `ADD`, `MODIFY`, `SET`, `ADD_TO`, `REMOVE_FROM`

**Text:** `DESCRIPTION`, `TEXT`

**Narrative containers:** `SETTING`, `FRAME`, `ARC`, `CAMPAIGN`, `SCENE`, `LOCATION` (and their sub-keywords as defined in §16)

All other keywords — `CURRICULUM`, `SCHOOL_ABILITY`, `POWERS`, `AMALGAMS`, `TRIGGER`, `CHARACTERISTICS`, `HERITAGE_TABLE`, `FACES`, `ACTIVATION`, `OPPORTUNITIES`, `PREDATOR_TEMPLATES`, `DICE_POOL`, `COST`, `DURATION`, etc. — are **system-defined**. They belong to L5R5e, VTM5e, or whatever system uses them.

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

> **DECISION-2 (resolved, v4):** NPCs are **instances** — write them with the canonical instance form (§5, *Definitions vs. Instances*): a `#hash ^"Name" DEF` that `EXTENDS` its actor type with a `PROPERTIES` block of inline typed values. The looser `DEF ^"Name" #id { TYPE "npc" … STATS { rings.air = 4 } }` form in the illustrative FRAME/ARC blocks below — reversed order, `=` assignment, dotted paths, `TYPE`-as-tag — is **deprecated** and left as-is only pending re-conversion. No new grammar is added.

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
            APPROACH "approach_name"       # optional
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
- `SKILL`: The skill used for the check
- `RING`: The ring or attribute used
- `TN`: Target number for success
- `APPROACH`: Optional specific approach (system-dependent)
- `ON_SUCCESS` / `ON_FAILURE`: Narrative consequences

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
            ^"Clan" STRING REQUIRED
            ^"School" STRING
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
            ^"Clan" STRING "Crab" FIXED
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
            ^"Clan" STRING REQUIRED
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
            ^"Parent" STRING "Dominate"
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
            ^"In-Clan Disciplines" LIST OF STRING ["Celerity", "Potence", "Presence"]
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
            ^"House" STRING REQUIRED
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

    ^"Pilum of Fire" DEF {
        EXTENDS ^"Formulaic Spell"
        PROPERTIES {
            ^"Technique" STRING "Creo" FIXED
            ^"Form" STRING "Ignem" FIXED
            ^"Level" INTEGER 20
            ^"Range" STRING "Voice"
            ^"Duration" STRING "Momentary"
            ^"Target" STRING "Individual"
        }
        LEVEL_CALCULATION {
            BASE 5
            RANGE_MODIFIER "+2 Voice"
            DAMAGE "+10"
        }
        DESCRIPTION "A bolt of fire shoots from your hand, inflicting +15 damage on the target."
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

**SCENE:** `TYPE`, `PREREQUISITES`, `MINIMUM_CLUES`, `COMPLETED_SCENES`, `CONDITION`, `OBJECTIVES`, `REQUIRED`, `OPTIONAL`, `CHECKS`, `CHECK`, `SKILL`, `RING`, `TN`, `APPROACH`, `ON_SUCCESS`, `ON_FAILURE`, `CLUES`, `CLUE`, `DISCOVERED_BY`, `CONFLICT`, `STAKES`, `OPPONENTS`, `RESOLUTIONS`, `RESOLUTION`, `OUTCOME`, `MONTAGE`, `MOMENT`

**LOCATION:** `TAGS`

**CAMPAIGN:** `RECURRING_CAST`, `PROGRESSION`, `BETWEEN`, `AND`, `DOWNTIME`, `ADVANCEMENT`

**Cross-container:** `DEPENDS_ON`, `USES_SETTING`, `USES_FRAME`, `USES_EXTENSION`, `FROM`, `INCLUDE`, `LEADS_TO`

---

## 19. Versioning *(v4)*

Three distinct version axes, kept separate:

- **DSL-spec version** — the version of *this specification* (v4). Files pin the spec they target via `SPEC_VERSION`.
- **File content `VERSION`** — the version of a file's game content (semantic or date-based), independent of the spec version.
- **Directory organization** — systems organize files under a content-version directory (e.g. `0.3/`, `1.0/`). Version lives in the directory, not re-encoded redundantly in every filename.

`DEPENDS_ON "Parent" VERSION "x"` pins a required parent *content* version. Tooling treats `SPEC_VERSION` as the conformance target.

## 20. Validation *(v4)*

Validation of `.ttrpg`/`.lore` files has two levels, both operating on the files themselves:

1. **Lint — spec adherence.** Does the file conform to this grammar/spec (structure, types, reserved-word usage, canonical forms)? One source of truth: the linter is derived from / checked against the grammar.
2. **Coherence / consilience — referential integrity.** Across the corpus: is everything referenced actually defined? Do `^"Name"`, `#hash`, `EXTENDS`, `APPLIES TO`, `DEPENDS_ON` resolve to real, correctly-typed targets? No duplicate or dangling anchors.

**Intentional exceptions:** both levels honor `FIAT` (§8) — a value or element marked `FIAT "reason"` is exempt from the findings it would otherwise raise (constraint violations and, cascading, completeness). Because each `FIAT` carries a reason, the full set is reportable for audit.

**Out of scope for the DSL:** *sophisticated rules validation* (evaluating whether game rules are internally consistent or produce legal characters) runs **downstream**, in the tools that consume `.ttrpg`/`.lore`, and is built later. The DSL guarantees a well-formed, coherent knowledge base — not a rules engine.

---

**Spec Version:** 4.0
**Last Updated:** 2026-07-12
**Status:** Canonical (supersedes v0.3)
