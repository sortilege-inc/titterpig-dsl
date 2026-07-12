# TTRPG Validator Tool

## Overview

The TTRPG Validator is a comprehensive syntax and structure validation tool for `.ttrpg` files using the Titterpig DSL. It checks for common errors, structural issues, and DSL violations to ensure your files are well-formed and valid.

## Usage

### Validate a Single File

```bash
python ttrpg_validator.py <file.ttrpg>
```

Example:
```bash
python ttrpg_validator.py 0.1.7/vtm5e-0.1.7-core.ttrpg
```

### Validate All Files in a Directory

```bash
python ttrpg_validator.py <directory>
```

Example:
```bash
python ttrpg_validator.py 0.1.7
```

### Verbose Output

Add `--verbose` or `-v` to see additional context for each issue:

```bash
python ttrpg_validator.py 0.1.7/vtm5e-0.1.7-world.ttrpg --verbose
```

## What It Checks

### Structural Checks

1. **Brace Matching**
   - Ensures all `{` have matching `}`
   - Detects orphaned closing braces
   - Reports unclosed blocks at end of file

2. **Indentation Consistency**
   - Warns about mixed tabs and spaces
   - Reports inconsistent indentation styles

### Syntax Checks

3. **ACTOR Definitions**
   - Validates `ACTOR "Name" DEF {` syntax
   - Ensures proper quoting of names

4. **DEF/MODIFY Blocks**
   - Validates `^"Name" DEF {` or `^"Name" MODIFY {` syntax
   - Checks for unquoted definition names

5. **EXTENDS Clauses**
   - Validates `EXTENDS #hash ^"Name"` syntax
   - Ensures both hash ID and actor reference are present

6. **APPLIES TO Clauses**
   - Validates `APPLIES TO [^"Name"]` syntax
   - Checks for properly formatted actor references
   - Ensures at least one actor is referenced

7. **Hash ID Format**
   - Validates hash IDs follow format: `#` followed by 16+ alphanumeric characters
   - Warns if hash IDs are too short (e.g., `#vamily` with only 7 chars)

### Property Validation

8. **Property Type Constraints**
   - Checks INTEGER properties have valid MIN/MAX/DEFAULT values
   - Ensures MIN ≤ DEFAULT ≤ MAX
   - Ensures MIN ≤ MAX

9. **String Quoting**
   - Validates that names and references are properly quoted
   - Checks for missing quotes in definitions

## Error Categories

### ERROR (❌ / [X])
Critical issues that make the file invalid:
- Brace mismatches
- Invalid syntax in ACTOR, DEF, MODIFY, EXTENDS, or APPLIES TO
- Constraint violations (e.g., MIN > MAX)
- Missing required quotes

### WARNING (⚠️ / [!])
Non-critical issues that should be reviewed:
- Hash IDs that don't follow standard format
- Mixed indentation styles

### INFO (ℹ️ / [i])
Informational messages:
- Style inconsistencies
- Best practice recommendations

## Exit Codes

- `0`: All files validated successfully (no errors)
- `1`: Validation failed (one or more files have errors)

## Example Output

```
======================================================================
Validating: vtm5e-0.1.7-core.ttrpg
======================================================================
Lines: 808
Errors: 0
Warnings: 0
Status: [VALID]

[OK] No issues found!
```

With errors:
```
======================================================================
Validating: vtm5e-0.1.7-world.ttrpg
======================================================================
Lines: 5952
Errors: 3
Warnings: 0
Status: [INVALID]

----------------------------------------------------------------------
ISSUES FOUND:
----------------------------------------------------------------------

[X] ERROR [SYNTAX_ERROR] @ Line 3924
   Invalid EXTENDS syntax. Expected: EXTENDS #hash ^"Name"

[X] ERROR [SYNTAX_ERROR] @ Line 4273
   Invalid EXTENDS syntax. Expected: EXTENDS #hash ^"Name"

[X] ERROR [SYNTAX_ERROR] @ Line 4505
   Invalid EXTENDS syntax. Expected: EXTENDS #hash ^"Name"
```

With verbose mode:
```
[X] ERROR [SYNTAX_ERROR] @ Line 3924
   Invalid EXTENDS syntax. Expected: EXTENDS #hash ^"Name"
   Context: EXTENDS ^"Project"
```

## Common Issues and Fixes

### 1. Missing Hash ID in EXTENDS

**Error:**
```
[X] ERROR [SYNTAX_ERROR] @ Line 3924
   Invalid EXTENDS syntax. Expected: EXTENDS #hash ^"Name"
```

**Cause:**
```
EXTENDS ^"Project"
```

**Fix:**
```
EXTENDS #YourHashId ^"Project"
```

### 2. Brace Mismatch

**Error:**
```
[X] ERROR [BRACE_MISMATCH] @ Line 398
   Closing brace '}' without matching opening brace
```

**Cause:** Unbalanced braces in the file.

**Fix:** Check that every `{` has a matching `}` and vice versa.

### 3. MIN/MAX/DEFAULT Constraint Violation

**Error:**
```
[X] ERROR [CONSTRAINT_ERROR] @ Line 45
   DEFAULT (7) cannot be greater than MAX (5)
```

**Cause:**
```
^"Attribute" INTEGER MIN 0 MAX 5 DEFAULT 7
```

**Fix:**
```
^"Attribute" INTEGER MIN 0 MAX 10 DEFAULT 7
```

### 4. Short Hash ID

**Warning:**
```
[!] WARNING [HASH_FORMAT] @ Line 796
   Hash "#vamily" is too short (expected: 16+ alphanumeric chars after #)
```

**Cause:** Hash ID is less than 16 characters.

**Fix:** Use a properly generated hash ID with 16+ characters:
```
#vamilyABCDEF123456
```

## Validation Results from v0.1.7

Running the validator on v0.1.7 files:

```
Total files: 16
Valid: 12
Invalid: 4
Total errors: 19
Total warnings: 1
```

**Valid Files (12):**
- vtm5e-0.1.7-character.ttrpg
- vtm5e-0.1.7-clans.ttrpg
- vtm5e-0.1.7-core.ttrpg
- vtm5e-0.1.7-disciplines.ttrpg
- vtm5e-0.1.7-systems.ttrpg
- vtm5e-0.1.7-traits.ttrpg
- vtm5e-players-guide-0.1.7-clans.ttrpg
- vtm5e-players-guide-0.1.7-disciplines.ttrpg
- vtm5e-players-guide-0.1.7-traits.ttrpg
- vtm5e-errata-0.1.7.ttrpg
- wod-storyteller-expanded-mechanics-0.1.7.ttrpg

**Invalid Files (4):**
- vtm5e-0.1.7-world.ttrpg (3 EXTENDS syntax errors)
- vtm5e-players-guide-0.1.7-core.ttrpg (2 EXTENDS syntax errors)
- vtm5e-players-guide-0.1.7-systems.ttrpg (2 EXTENDS syntax errors)
- vtm5e-players-guide-0.1.7-world.ttrpg (12 EXTENDS syntax errors)

**Issues Found:**
- 19 missing hash IDs in EXTENDS clauses
- 1 short hash ID warning (`#vamily` - only 7 characters)

## Integration with Build Process

You can integrate the validator into your build process or CI/CD pipeline:

```bash
# Validate all files before committing
python ttrpg_validator.py 0.1.7
if [ $? -eq 0 ]; then
    echo "All files valid, proceeding with commit"
    git commit -m "Your commit message"
else
    echo "Validation failed, please fix errors before committing"
    exit 1
fi
```

## Implementation Details

### Comment Handling

The validator properly distinguishes between:
- **Hash IDs**: `#YD4PosFYGnnbWia88WUziU` (no space after `#`)
- **Comments**: `# This is a comment` (space after `#`)

### Brace Tracking

Braces are tracked globally across the entire file with a running count. The validator:
1. Increments count for each `{`
2. Decrements count for each `}`
3. Reports error if count goes negative (orphaned `}`)
4. Reports error if count > 0 at end of file (unclosed blocks)

### Regex Patterns

Key regex patterns used:
- ACTOR: `^\s*ACTOR\s+"([^"]+)"\s+DEF\s*\{?\s*$`
- DEF/MODIFY: `^\s*\^"([^"]+)"\s+(DEF|MODIFY)\s*\{?\s*$`
- EXTENDS: `EXTENDS\s+(#[A-Za-z0-9]+)\s+\^"([^"]+)"`
- APPLIES TO: `APPLIES TO\s+\[([^\]]+)\]`
- Hash ID: `#[A-Za-z0-9]{16,}`

## Future Enhancements

Potential improvements for future versions:
- Cross-file reference validation (check if referenced ACTORs exist)
- Semantic validation (ensure property types match usage)
- Style guide enforcement
- Auto-fix capability for common issues
- JSON/XML output format for CI integration
- Incremental validation (only check changed files)

## License

This tool is part of the VtM Core v0.1 project.

## Support

If you encounter issues or have feature requests, please check:
1. This README for common issues
2. The validation output for specific error messages
3. The source code comments for implementation details
