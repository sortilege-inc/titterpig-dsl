# Titterpig DSL Specification v0.1

## Overview

Titterpig is a domain-specific language (DSL) for defining tabletop role-playing game (TTRPG) systems and rules. The language is designed to be:

- **Natural language-like**: Easy to read and understand
- **Modular**: Systems and extensions are separate files
- **Composable**: Extensions can stack and override parent rules
- **System-agnostic**: Supports diverse RPG mechanics (L5R, Draw Steel, Root, etc.)

## File Format

Files use the `.ttrpg` extension and are organized as:
- `systems/{system_id}/core.ttrpg` - Base system definitions
- `extensions/{system_id}/{extension_id}.ttrpg` - Extensions, errata, sourcebooks, house rules

## Basic Syntax

### Comments
```
# This is a comment
// This is also a comment
```

### System Declaration

```
SYSTEM "SystemID" {
    NAME "Human-readable System Name"
    VERSION "1.0.0"
    RELEASE_DATE "YYYY-MM-DD"
    
    ATTRIBUTES { ... }
    MECHANICS { ... }
    RULES { ... }
}
```

**Fields:**
- `SystemID`: Unique identifier (e.g., "L5R5e", "DrawSteel", "Root")
- `NAME`: Full display name
- `VERSION`: Semantic version
- `RELEASE_DATE`: ISO date format

## Attributes Section

Defines character statistics, resources, and calculated values.

### Attribute Types

#### Integer Range
```
attribute_name AS integer_range(min, max)
```
- Supports negative numbers: `integer_range(-4, 4)`
- Example: `honor AS integer_range(0, 100)`

#### Map (Nested Attributes)
```
attribute_name AS map {
    sub_attribute1 AS integer_range(min, max)
    sub_attribute2 AS integer_range(min, max)
}
```

Example:
```
rings AS map {
    air AS integer_range(1, 5)
    earth AS integer_range(1, 5)
    fire AS integer_range(1, 5)
    water AS integer_range(1, 5)
    void AS integer_range(1, 5)
}
```

#### Enum
```
attribute_name AS enum ["value1", "value2", "value3"]
```

Example:
```
current_clearing AS enum ["fox", "rabbit", "mouse"]
```

#### Resource Range
```
attribute_name AS resource_range(min, max)
```
- Similar to integer_range but semantically represents consumable resources
- Example: `hero_tokens AS resource_range(0, 5)`

#### Boolean
```
attribute_name AS boolean DEFAULT value
```

Example:
```
edge AS boolean DEFAULT false
```

#### Calculated Attributes
```
attribute_name AS calculated {
    formula = expression
}
```

Example:
```
composure AS calculated {
    formula = earth + (water * 2)
}

stamina AS calculated {
    formula = 9 + might + presence
}
```

### Full Attributes Example

```
ATTRIBUTES {
    rings AS map {
        air AS integer_range(1, 5)
        earth AS integer_range(1, 5)
        fire AS integer_range(1, 5)
        water AS integer_range(1, 5)
        void AS integer_range(1, 5)
    }
    
    skills AS map {
        artisan AS integer_range(0, 5)
        martial AS integer_range(0, 5)
        scholar AS integer_range(0, 5)
        social AS integer_range(0, 5)
        trade AS integer_range(0, 5)
    }
    
    honor AS integer_range(0, 100)
    glory AS integer_range(0, 100)
    status AS integer_range(0, 100)
    
    composure AS calculated {
        formula = earth + (water * 2)
    }
}
```

## Mechanics Section

Defines dice rolling systems and resolution mechanics.

### Mechanic Definition

```
mechanic_name {
    dice = "dice_type"
    pool_size = expression
    keep = value
    keep_system = "method"
    success_condition = expression
    modifiers = ["mod1", "mod2", "mod3"]
}
```

**Common Fields:**
- `dice`: Die type (e.g., "d6", "d20", "d10")
- `pool_size`: Number of dice to roll
- `keep`: How many dice to keep
- `keep_system`: Method for keeping dice ("highest", "lowest", "sum", "ring_value", "exploding")
- `success_condition`: When a roll succeeds
- `modifiers`: List of applicable modifiers

### Examples

#### L5R Ring & Skill Roll
```
MECHANICS {
    ring_skill_roll {
        dice = "d6"
        pool_size = ring_value + skill_value
        keep = ring_value
        success_condition = kept_dice >= target_number
    }
}
```

#### Draw Steel d20 Test
```
MECHANICS {
    d20_test {
        dice = "d20"
        modifiers = ["advantage", "disadvantage", "edge"]
        success_condition = total >= target_number
    }
}
```

#### Root 2d6 Roll
```
MECHANICS {
    basic_move {
        dice = "2d6"
        modifiers = ["help", "interfere", "injury", "exhaustion"]
        success_thresholds = [7, 10]
    }
}
```

## Rules Section

Defines game rules, triggers, and actions. (Parser implementation in progress)

### Rule Structure (Proposed)

```
RULES {
    RULE rule_name {
        WHEN trigger_condition
        REQUIRES prerequisite
        LET variable = expression
        ROLL dice_expression
        IF condition THEN
            action
        ELSIF condition THEN
            action
        ELSE
            action
        END
        UPDATE attribute = value
        RETURN result WITH data
    }
}
```

### Rule Keywords

- `RULE`: Defines a rule block
- `WHEN`: Trigger condition
- `REQUIRES`: Prerequisites that must be met
- `LET`: Define local variables
- `ROLL`: Execute dice roll
- `IF/ELSIF/ELSE/END`: Conditional logic
- `UPDATE`: Modify character/game state
- `RETURN`: Return result with optional data
- `GRANT`: Give temporary benefits

### Example Rules

```
RULES {
    RULE composure_calculation {
        WHEN character.created OR character.rings.earth.changed OR character.rings.water.changed
        UPDATE character.composure = character.rings.earth + (character.rings.water * 2)
    }
    
    RULE basic_skill_roll {
        REQUIRES character.rings[ring] >= 1
        LET pool_size = character.rings[ring] + character.skills[skill]
        LET keep_dice = character.rings[ring]
        ROLL pool_size d6 KEEP keep_dice
        IF kept_sum >= target_number THEN
            RETURN success WITH opportunities = count_symbols(rolled_dice, "opportunity")
        ELSE
            RETURN failure WITH strife = count_symbols(rolled_dice, "strife")
        END
    }
    
    RULE spend_hero_token {
        REQUIRES character.hero_tokens > 0
        UPDATE character.hero_tokens -= 1
        GRANT advantage ON next_roll
    }
}
```

## Extension Syntax

Extensions modify or add to base systems.

```
EXTENSION "ExtensionID" EXTENDS "ParentSystemID" {
    NAME "Extension Name"
    VERSION "version"
    RELEASE_DATE "date"
    
    RULES {
        RULE existing_rule OVERRIDES PARENT {
            # Modified rule definition
        }
        
        RULE new_rule ADDS_TO PARENT {
            # New rule definition
        }
    }
}
```

### Extension Actions

- `OVERRIDES PARENT`: Completely replaces parent rule
- `ADDS_TO PARENT`: Adds new behavior alongside parent rule
- `MODIFIES PARENT`: Partially modifies parent rule (future)

### Example Extension

```
EXTENSION "L5R5e_Errata_2024" EXTENDS "L5R5e" {
    NAME "2024 Official Errata"
    VERSION "2024.09.22"
    RELEASE_DATE "2024-09-22"
    
    RULES {
        RULE composure_calculation OVERRIDES PARENT {
            WHEN character.created OR character.rings.earth.changed OR character.rings.water.changed
            LET base_composure = character.rings.earth + (character.rings.water * 2)
            LET composure_bonus = character.advantages.composure_bonus OR 0
            UPDATE character.composure = base_composure + composure_bonus
        }
        
        RULE honor_loss_cap ADDS_TO PARENT {
            WHEN character.honor.would_decrease
            IF honor_loss > 5 THEN
                SET honor_loss = 5
                NOTIFY "Honor loss capped at 5 per scene (Errata 2024)"
            END
        }
    }
}
```

## Parser Implementation Status

### ✅ Implemented
- System declaration parsing
- Attribute definitions (integer_range, map, enum, resource_range, boolean, calculated)
- Basic mechanics parsing (dice type, keep system)
- Negative number support in integer ranges
- Nested map structures

### 🚧 In Progress
- Full mechanics property parsing
- Rule execution logic
- Conditional expressions

### 📋 Planned
- Extension parsing and loading
- Rule conflict detection
- Complete DSL interpreter for rule execution
- Built-in functions (count_symbols, keep_highest, etc.)

## Reserved Keywords

- `SYSTEM`, `EXTENSION`, `EXTENDS`
- `NAME`, `VERSION`, `RELEASE_DATE`
- `ATTRIBUTES`, `MECHANICS`, `RULES`
- `AS`, `map`, `integer_range`, `resource_range`, `enum`, `boolean`, `calculated`
- `RULE`, `WHEN`, `REQUIRES`, `LET`, `ROLL`, `KEEP`
- `IF`, `ELSIF`, `ELSE`, `END`, `THEN`
- `UPDATE`, `RETURN`, `GRANT`, `WITH`, `ON`
- `OVERRIDES`, `ADDS_TO`, `MODIFIES`, `PARENT`
- `OR`, `AND`, `NOT`

## Design Principles

1. **Readability**: Code should read like game rules documentation
2. **Declarative**: Describe what should happen, not how to implement it
3. **Composable**: Rules can be layered and combined
4. **Type-safe**: Attribute types are enforced
5. **System-agnostic**: Support diverse mechanics without hardcoded logic
6. **Conflict-aware**: Flag and resolve rule conflicts explicitly

## Example: Complete L5R System

```
SYSTEM "L5R5e" {
    NAME "Legend of the Five Rings 5th Edition"
    VERSION "1.0.0"
    RELEASE_DATE "2017-10-01"
    
    ATTRIBUTES {
        rings AS map {
            air AS integer_range(1, 5)
            earth AS integer_range(1, 5)
            fire AS integer_range(1, 5)
            water AS integer_range(1, 5)
            void AS integer_range(1, 5)
        }
        
        skills AS map {
            artisan AS integer_range(0, 5)
            martial AS integer_range(0, 5)
            scholar AS integer_range(0, 5)
            social AS integer_range(0, 5)
            trade AS integer_range(0, 5)
        }
        
        honor AS integer_range(0, 100)
        glory AS integer_range(0, 100)
        status AS integer_range(0, 100)
        
        composure AS calculated {
            formula = earth + (water * 2)
        }
    }
    
    MECHANICS {
        ring_skill_roll {
            dice = "d6"
            pool_size = ring_value + skill_value
            keep = ring_value
            success_condition = kept_dice >= target_number
        }
    }
    
    RULES {
        RULE basic_skill_roll {
            REQUIRES character.rings[ring] >= 1
            LET pool_size = character.rings[ring] + character.skills[skill]
            LET keep_dice = character.rings[ring]
            ROLL pool_size d6 KEEP keep_dice
            IF kept_sum >= target_number THEN
                RETURN success WITH opportunities = count_symbols(rolled_dice, "opportunity")
            ELSE
                RETURN failure WITH strife = count_symbols(rolled_dice, "strife")
            END
        }
    }
}
```

## Future Considerations

- **Validation**: Type checking and constraint validation
- **Debugging**: Rule execution tracing
- **Testing**: Unit tests for rule definitions
- **Optimization**: Caching compiled rules
- **Versioning**: Semantic versioning for compatibility
- **Documentation**: Auto-generate documentation from .ttrpg files
- **IDE Support**: Syntax highlighting and autocomplete

---

**Version:** 0.1  
**Last Updated:** 2025-11-16  
**Status:** Active Development