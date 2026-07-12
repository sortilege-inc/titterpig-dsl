<!-- ============================================================
     SUPERSEDED / HISTORICAL — NOT part of the current v4 spec.
     Critique of the v0.2 state; historical rationale that informed v4.
     Canonical spec: ../titterpig-dsl-spec.md
     ============================================================ -->

# Titterpig DSL v0.2 Critique & Proposals

Based on analysis of:
- Base DSL spec (`titterpig-dsl-spec.md` v0.2)
- L5R5e spec + 45 `.ttrpg` files (v0.2 directory)
- VTM5e spec + 25 `.ttrpg` files (v0.1.9 directory)

---

## Part 1: The Spec vs The Implementations

### 1.1 The base spec and the implementations are different languages

The base DSL spec v0.2 defines a grammar using `SYSTEM`, `ATTRIBUTES { ... AS integer_range() }`, `MECHANICS`, and `RULE name { WHEN ... LET ... ROLL ... }`. Neither implementation uses this grammar. Both L5R5e and VTM5e use `BASE`/`EXTENSION` (not `SYSTEM`), `^"Name" DEF { PROPERTIES { ^"Attr" INTEGER MIN 1 MAX 5 } }` (not `AS integer_range()`), and `#hashid: label` rules (not `RULE name { ... }`).

The base spec reads like an early prototype that was superseded organically. The L5R5e and VTM5e implementations converged on a shared-ish grammar (`BASE`, `DEF`, `PROPERTIES`, `^"refs"`, hash IDs) that is nowhere formally specified in the base spec.

**Proposal:** The v0.2 spec should be rewritten to describe the grammar that actually exists in the implementations, not the prototype grammar. The `SYSTEM`/`AS integer_range()` syntax should either be formally deprecated or reconciled.

### 1.2 Two implementations, two dialects

Even setting the base spec aside, L5R5e and VTM5e diverge from each other:

| Feature | L5R5e | VTM5e (core format) | VTM5e (sourcebook format) |
|---------|-------|---------------------|--------------------------|
| File declaration | `BASE "Name" { }` | `BASE "Name" { }` | `METADATA { title: "..." }` |
| Definition | `^"Name" DEF { }` | `^"Name" DEF { }` | `DEF #hash { name: "..." }` |
| Property syntax | `^"Attr" INTEGER MIN 1 MAX 5` | `key: value` or `^"Attr" TYPE ...` | `key: value` |
| Hash ID format | `#L5R001aB2cD4eF...` (prefix+3dig+alphanum) | `#VnK8MrPxWbGh...` (random) | `#prince0000000001` (descriptive) |
| Dependencies | Implicit (file ordering in sources.json) | `DEPENDS_ON "Name"` | `NEGATE: "filename"` |
| Multi-line text | Not supported (comments used instead) | Not supported | `description: \|` (pipe) |

VTM5e itself has two incompatible internal formats (core vs sourcebook), meaning a parser needs format detection just within one game system.

**Proposal:** Unify on one syntax for definitions, properties, and references. The `^"Name" DEF { PROPERTIES { } }` pattern from L5R5e core files is the most mature and should be the standard. The VTM5e sourcebook format (`DEF #hash { key: value }`) should be migrated.

---

## Part 2: Structural Problems in L5R5e

### 2.1 Schools use four different structural patterns

This is the single most impactful inconsistency. Core schools, extension schools, and the Mantis Clan file each define schools differently:

**Core schools** (crab, crane, etc.):
```
^"Hida Defender" DEF {
    EXTENDS ^"School"
    PROPERTIES { ^"School Name" STRING "Hida Defender" FIXED }
    STARTING_TECHNIQUES { ... }
    SCHOOL_ABILITY "Way of the Crab" { ... }
    MASTERY_ABILITY ^"The Mountain Does Not Fall" { ... }
    STARTING_OUTFIT [ ... ]
    CURRICULUM {
        RANK 1 { SKILL_GROUP "Martial Skills" ... ^"Technique" [kata] }
    }
}
```

**Extension schools** (Shadowlands, Courts of Stone, etc.):
```
^"Asako Inquisitor School" DEF {
    APPLIES TO [^"Samurai"]
    PROPERTIES { ^"School" STRING "Asako Inquisitor" FIXED }
    # Starting techniques, ability, mastery as STRING properties
    ^"Ability Name" DEF { ... }
    CURRICULUM {
        ^"Rank 1" { "Scholar" SKILL_GROUP ... "Name (type)" TECHNIQUE }
    }
}
```

**Key differences:**
- `EXTENDS ^"School"` vs bare `APPLIES TO`
- `^"School Name"` vs `^"School"` property names
- `^"Roles" LIST` vs `^"School Roles" LIST OF STRING`
- `^"Ring Increase"` vs `^"Starting Rings"`
- `STARTING_TECHNIQUES { }` block vs `^"Starting Techniques" STRING`
- `SCHOOL_ABILITY "Name" { }` block vs `^"School Ability" STRING` property
- `RANK 1 { }` vs `^"Rank 1" { }`
- `SKILL_GROUP "Martial Skills"` vs `"Martial" SKILL_GROUP`
- `^"Name" [kata]` vs `"Name (kata)" TECHNIQUE`
- `TECHNIQUE_GROUP` vs `TECH_GROUP`

**Proposal:** Pick one school pattern and migrate all files. The core pattern is more structured and better for parsing. Standardize on:
- Always `EXTENDS ^"School"`
- Always keyword-first curriculum syntax: `RANK N`, `SKILL_GROUP`, `SKILL`, `TECHNIQUE_GROUP`, `TECHNIQUE`
- Always structured blocks: `STARTING_TECHNIQUES`, `SCHOOL_ABILITY`, `MASTERY_ABILITY`, `STARTING_OUTFIT`
- Consistent property names across all files

### 2.2 Curriculum entries have two incompatible syntaxes

Keyword-first (core): `SKILL_GROUP "Martial Skills"`, `SKILL "Command"`, `^"Name" [kata]`
Value-first (extensions): `"Martial" SKILL_GROUP`, `"Command" SKILL`, `"Name (kata)" TECHNIQUE`

These require fundamentally different parsing logic. The current Go ingest has to handle both.

**Proposal:** Standardize on keyword-first. It's more readable, more grep-friendly, and the keyword comes first for syntax highlighting.

### 2.3 Structured data buried in strings

Many properties encode parseable structured data as opaque strings:

- **Family entries**: `"+1 Earth or Fire, +1 Command, +1 Tactics, Glory 44, 4 koku"` -- five+ fields packed into one string
- **Weapon grips**: `"1-hand: no bonus; 2-hand: Damage +2, Deadliness +2"` -- multiple grip modes with stat modifiers
- **Starting skills**: `"choose 5: +1 Fitness, +1 Martial Arts [Melee], ..."` -- choice count + skill list
- **Ring bonuses**: `"+1 Air, +1 Water"` -- parsed by the Go ingest with regex
- **NPC advantages**: `"Wealth and Resources (Water) [Trade; Material]"` -- name, ring, and categories in ad-hoc format
- **NPC weapons**: `"Katana: Range 1, Damage 4, Deadliness 5/7, Ceremonial"` -- full stat block as string
- **Formulas**: `"(Earth + Fire) x 2"` -- mathematical expression as string

The Go ingest code has to use complex regex patterns to extract data from these strings. This is fragile and has caused bugs (the Q3 equipment picker issue was partly related to inconsistent formatting).

**Proposal:** Promote the most common string-encoded patterns to first-class DSL structures:

```
# Instead of: ^"Hida" "+1 Earth or Fire, +1 Command, +1 Tactics, Glory 44, 4 koku"
# Write:
^"Hida" FAMILY {
    RING_BONUS "+1 Earth or Fire"
    SKILL_BONUS "+1 Command"
    SKILL_BONUS "+1 Tactics"
    GLORY 44
    WEALTH "4 koku"
}

# Instead of: ^"Grips" STRING "1-hand: no bonus; 2-hand: Damage +2, Range 1-2"
# Write:
GRIPS {
    "1-hand" { }
    "2-hand" { DAMAGE +2, RANGE "1-2" }
}
```

Not everything needs to be structured -- descriptions and narrative text should remain strings. But data that the parser has to extract should be structured.

### 2.4 NPC stat blocks are almost entirely unstructured

NPC abilities are defined as comment-only DEF blocks:
```
^"Massive Bones" DEF {
    # A gashadokuro is an Otherworldly, Tainted being...
}
```

NPC skills use a flat group format (`"Martial 5"`) that's incompatible with the per-skill property definitions players use. NPC weapons and advantages are packed strings. There's no structured way to express NPC stat blocks that a parser can consume.

**Proposal:** Define an NPC stat block structure:
```
^"Gashadokuro" DEF {
    EXTENDS ^"Adversary"
    PROPERTIES {
        ^"Conflict Rank" INTEGER 8
        ^"Endurance" INTEGER 20
    }
    RINGS { AIR 1, EARTH 6, FIRE 2, WATER 4, VOID 0 }
    SKILLS { MARTIAL 6, SCHOLAR 0, SOCIAL 0 }
    ABILITIES {
        ^"Massive Bones" {
            EFFECT "The first time it would be defeated..."
        }
    }
    GEAR {
        ^"Barbed Hair" WEAPON { RANGE "0-2", DAMAGE 3, DEADLINESS 6, QUALITIES ["Snaring", "Unholy"] }
    }
}
```

### 2.5 Errata is all comments with no structured override mechanism

Errata files express corrections as comments:
```
^"Core Rulebook Errata (2019)" DEF {
    # p. 65, Kakita Duelist (Rank 1): "Iaijutsu Cut: Crossing Cut"
    # should read "Iaijutsu Cut: Crossing Blade."
}
```

There's no machine-readable way to apply these corrections. The RULES block creates hash labels but the actual correction is in a comment.

**Proposal:** The base spec already has `OVERRIDES PARENT` and `MODIFIES PARENT`. Use them:
```
EXTENSION "L5R5e_Errata_2020" EXTENDS "L5R5e_Core" {
    MODIFY ^"Kakita Duelist" {
        # In STARTING_TECHNIQUES, replace:
        OVERRIDE ^"Starting Techniques" {
            KATA ^"Iaijutsu Cut: Crossing Blade"
        }
    }
}
```

### 2.6 The Twenty Questions are defined twice and they disagree

`core-character.ttrpg` and `core-chargen.ttrpg` both define the Twenty Questions with different mechanical effects. Q9-Q13 are especially wrong in core-character (conflating skills with advantages). The chargen file is marked as authoritative.

**Proposal:** Remove the duplicate from core-character. The Twenty Questions should exist in exactly one place.

### 2.7 Hash ID format varies across files

The prefix, digit count, and suffix length all vary:
- Core: `#L5R` + 3 digits + 12 alphanum (25 chars total)
- Shadowlands: `#L5RSL` + 2 digits + 12 alphanum
- Path of Waves: `#L5RPW` + 2 digits + 14 alphanum (longer)
- Mass Battle: `#L5RFVMB` + 2 digits + 10 alphanum

**Proposal:** Standardize the format. A consistent pattern like `#PREFIX_NNN_XXXXXXXXXXXX` (underscore-separated, fixed lengths) would be easier to validate. Or, allow flexible-length IDs but require a minimum length and validate uniqueness.

### 2.8 APPLIES TO vs EXTENDS confusion

`EXTENDS` is for type inheritance. `APPLIES TO` declares which actors a DEF affects. In practice they're used inconsistently:

- Core schools use both: `EXTENDS ^"School"` + `APPLIES TO [^"Samurai"]`
- Extension schools use only: `APPLIES TO [^"Samurai"]`
- NPCs use: `APPLIES TO [^"NPC"]`
- Techniques use: `APPLIES TO [^"Technique"]`
- Errata uses: `APPLIES TO [^"Game Rules"]`
- Some definitions use neither

When `APPLIES TO [^"Technique"]` is written, is "Technique" a type being extended, or a category being tagged? The semantics are muddled.

**Proposal:** Clarify the distinction:
- `EXTENDS ^"Type"` = "this DEF inherits properties from Type" (structural inheritance)
- `CATEGORY "Technique"` or `TYPE "kata"` = "this DEF belongs to this category" (tagging)
- `APPLIES TO [^"Samurai"]` = "this rule/modifier affects these actor types" (scoping)

Remove the use of `APPLIES TO` for type tagging.

---

## Part 3: Structural Problems in VTM5e

### 3.1 Two incompatible DSL formats in one game system

The core files use `BASE`/`EXTENSION` with `^"Name" DEF { }` syntax. The sourcebook files use `METADATA { }` with `DEF #hash { name: "...", type: "..." }` syntax. These are structurally incompatible.

**Proposal:** Migrate all sourcebook files to the core format. The `METADATA` block information can be expressed as:
```
EXTENSION "VTM5e_Camarilla" EXTENDS "VTM5e_Core" {
    NAME "Camarilla"
    VERSION "0.1.9"
    # content using ^"Name" DEF { } syntax
}
```

### 3.2 Version number chaos

- Directory: `0.1.9`
- Core file VERSION headers: `"0.1.8"`
- Sourcebook METADATA: `"0.1.9"`
- Sortilege homebrew: `"0.1"`
- DSL spec: `"0.3"`

**Proposal:** All files in a directory version should declare the same version. Use a single authoritative version.

### 3.3 Source configuration references wrong filenames

The sources file references `vtm5e-core-0.1.9.ttrpg` but the actual file is `vtm5e-0.1.9-core.ttrpg`.

**Proposal:** Fix the references. Also standardize naming: `{system}-{version}-{topic}.ttrpg` for all files.

### 3.4 APPLIES TO values are systematically wrong

Clan compulsions have APPLIES TO values that are off-by-one from the correct clan:
- Cryptophilia has `APPLIES TO: Gangrel` but `CLAN: Nosferatu`
- Obsession has `APPLIES TO: Gangrel` but `CLAN: Toreador`

**Proposal:** Fix the values. Add validation that APPLIES TO matches CLAN.

### 3.5 In Memoriam uses Markdown in a .ttrpg file

`vtm5e-in-memoriam-0.1.9.ttrpg` uses Markdown formatting (bold, headers, paragraphs) rather than any DSL syntax.

**Proposal:** Either convert it to DSL syntax or rename it to `.lore`.

---

## Part 4: Cross-Cutting Problems

### 4.1 Comments doing structural work

Across both implementations, comments carry critical data that should be structured:

- NPC abilities (L5R5e): Entire mechanical effects in comments
- Errata corrections (both): Page references and corrections in comments
- GM reference material (L5R5e): Summary data in comments
- School descriptions (L5R5e): Narrative text in comments
- Opportunity effects (L5R5e NPC files): Dice spend options in comments

Comments should be for documentation, not data. A parser that strips comments (as the L5R5e `stripComments()` does) loses this data.

**Proposal:** Introduce a `DESCRIPTION` or `TEXT` block type for narrative content that is data, not documentation:
```
^"Hida Defender" DEF {
    TEXT "Producing the most stalwart protectors of Rokugan..."
    # This comment is a development note, not game content
}
```

### 4.2 No multi-line text support

Neither implementation has a way to express multi-line text blocks. Long descriptions are either:
- Single-line strings that wrap poorly
- Split across multiple comment lines
- Using `|` pipe syntax (VTM5e sourcebook format only, not in L5R5e)

**Proposal:** Add heredoc or pipe-delimited text blocks to the base spec:
```
DESCRIPTION |
    This is a multi-line description.
    It preserves line breaks.
    Indentation relative to the pipe is stripped.
|
```

Or use triple-quote syntax:
```
DESCRIPTION """
    This is a multi-line description.
    It preserves line breaks.
"""
```

### 4.3 No formal MODIFY/OVERRIDE mechanism

The base spec defines `OVERRIDES PARENT`, `ADDS_TO PARENT`, and `MODIFIES PARENT` for extensions. Neither implementation uses them. L5R5e errata is all comments. VTM5e has `MODIFY`/`EXTEND`/`OVERRIDE`/`ADD` keywords defined in its spec but used inconsistently.

**Proposal:** Implement a simple modification syntax:
```
MODIFY ^"Target Name" {
    SET ^"Property" = new_value
    ADD ^"List Property" ["new item"]
    REMOVE ^"List Property" ["old item"]
    REPLACE ^"Sub Block" { ... }
}
```

### 4.4 No standard way to express property constraints

L5R5e uses `INTEGER MIN 1 MAX 5 DEFAULT 1`. VTM5e core uses `RANGE: 0-5`. The base spec uses `integer_range(min, max)`. Three syntaxes for the same concept.

**Proposal:** Pick one. `INTEGER MIN 1 MAX 5 DEFAULT 1` is the most readable and already has the most content written in it.

### 4.5 Metatype anchors are ad-hoc

Both implementations define empty DEF blocks as "metatype anchors" that are then referenced by `APPLIES TO`:
```
^"Game Rules" DEF { # Metatype anchor for game rules }
^"NPC" DEF { }
^"Weapon" DEF { }
```

These serve as type tags but have no formal semantics. Are they types? Categories? Tags? The distinction matters for validation.

**Proposal:** Introduce a `TYPE` keyword distinct from `DEF`:
```
TYPE ^"School" {
    # Defines the shape that all school DEFs must conform to
    PROPERTIES {
        ^"School Name" STRING REQUIRED
        ^"Clan" STRING REQUIRED
        ...
    }
}
```

Then `DEF` with `EXTENDS ^"School"` is an instance of that type.

---

## Part 5: What's Working Well

Not everything needs to change. These patterns are working and should be preserved:

1. **`^"Name"` caret references** -- Intuitive, grep-friendly, clearly distinct from plain strings
2. **`BASE`/`EXTENSION` file declarations** -- Clear intent, good for source management
3. **Hash ID rule references** -- Provide traceability for individual rules
4. **The priority/weight source system** -- Handles errata and conflicting sources well
5. **`CURRICULUM` blocks** (core syntax) -- Clearly express school progression
6. **`STARTING_TECHNIQUES`/`SCHOOL_ABILITY`/`MASTERY_ABILITY`** blocks -- Well-structured
7. **Cross-link references** (`^"Name"` in descriptions) -- Enable compendium navigation
8. **`.lore` file separation** -- Good boundary between narrative and mechanical content
9. **The `ENTRIES` pattern** for grouping related definitions
10. **`ALIAS` for romanization alternatives** -- Practical for Japanese terms

---

## Part 6: Proposed v0.2 Priorities

Ranked by impact and feasibility:

### Must Fix (blocks parser or causes data loss)
1. **Reconcile base spec with implementations** -- The spec should describe what exists
2. **Unify VTM5e's two internal formats** -- One parser, one syntax
3. **Standardize school definition structure** -- One pattern across all files
4. **Standardize curriculum syntax** -- Keyword-first only
5. **Fix VTM5e APPLIES TO errors** -- Data correctness

### Should Fix (significant quality improvement)
6. **Add multi-line text blocks** -- Eliminates comment-as-data pattern
7. **Structure family entries** -- Replace packed strings with blocks
8. **Define NPC stat block format** -- Make NPCs parseable
9. **Add MODIFY/OVERRIDE semantics** -- Make errata machine-readable
10. **Standardize hash ID format** -- Consistent validation

### Nice to Have (polish)
11. **Introduce TYPE declarations** -- Formal type system
12. **Structure weapon grips** -- Replace packed grip strings
13. **Clarify APPLIES TO vs EXTENDS** -- Semantic precision
14. **Remove Twenty Questions duplication** -- Single source of truth
15. **Standardize file naming conventions** -- Consistent across both systems

---

## Part 7: Migration Strategy

A full rewrite of all files is impractical. Suggested approach:

1. **Write the new spec first** -- Document the grammar as it should be
2. **Build a migration validator** -- Flag non-conforming patterns in existing files
3. **Migrate VTM5e sourcebook format** -- Highest ROI, fewest files
4. **Standardize L5R5e extension schools** -- Next highest impact
5. **Add structured text blocks** -- Enables gradual migration of comment-as-data
6. **Migrate family/NPC data** -- Can be done incrementally per file

Each migration step should update the ingest pipeline alongside the DSL files so nothing breaks.
