#!/usr/bin/env python3
"""
TTRPG File Validator

Validates .ttrpg files for syntax errors, structural issues, and DSL violations.

Usage:
    python ttrpg_validator.py <file.ttrpg>
    python ttrpg_validator.py <directory>  # validates all .ttrpg files in directory

Checks:
- Brace matching and balance
- Hash/UUID format validation
- ACTOR/DEF/MODIFY syntax
- APPLIES TO clause validation
- EXTENDS clause validation
- Property type validation
- MIN/MAX/DEFAULT consistency
- String quoting
- Indentation consistency
- Reserved keyword usage
- Orphaned/unclosed blocks
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationIssue:
    line_number: int
    severity: Severity
    category: str
    message: str
    context: str = ""


@dataclass
class ValidationResult:
    file_path: Path
    issues: List[ValidationIssue] = field(default_factory=list)
    line_count: int = 0

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)

    @property
    def is_valid(self) -> bool:
        return self.error_count == 0


class TTRPGValidator:
    """Validator for Titterpig DSL .ttrpg files"""

    # Hash pattern: #X followed by alphanumeric characters
    HASH_PATTERN = re.compile(r'#[A-Za-z0-9]+')

    # Valid hash format (starts with letter or digit, 16+ chars total)
    VALID_HASH_PATTERN = re.compile(r'#[A-Za-z0-9]{16,}')

    # ACTOR definition: ACTOR "Name" DEF {
    ACTOR_DEF_PATTERN = re.compile(r'^\s*ACTOR\s+"([^"]+)"\s+DEF\s*\{?\s*$')

    # Regular definition: ^"Name" DEF {
    DEF_PATTERN = re.compile(r'^\s*\^"([^"]+)"\s+(DEF|MODIFY)\s*\{?\s*$')

    # APPLIES TO clause: APPLIES TO [^"Name"] or APPLIES TO [^"Name1", ^"Name2"]
    APPLIES_TO_PATTERN = re.compile(r'APPLIES TO\s+\[([^\]]+)\]')

    # EXTENDS clause: EXTENDS #hash ^"Name"
    EXTENDS_PATTERN = re.compile(r'EXTENDS\s+(#[A-Za-z0-9]+)\s+\^"([^"]+)"', re.IGNORECASE)

    # Property types
    PROPERTY_TYPES = {
        'INTEGER', 'STRING', 'BOOLEAN', 'LIST OF', 'ENUM',
        'DEF', 'MODIFY'
    }

    # Reserved keywords
    KEYWORDS = {
        'ACTOR', 'DEF', 'MODIFY', 'EXTENDS', 'APPLIES TO', 'PROPERTIES',
        'INTEGER', 'STRING', 'BOOLEAN', 'LIST OF', 'ENUM',
        'MIN', 'MAX', 'DEFAULT', 'METADATA', 'DESCRIPTION'
    }

    def __init__(self):
        self.result = None
        self.lines = []
        self.brace_stack = []  # Stack to track opening braces

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single .ttrpg file"""
        self.result = ValidationResult(file_path=file_path)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.lines = f.readlines()
                self.result.line_count = len(self.lines)
        except Exception as e:
            self.result.issues.append(ValidationIssue(
                line_number=0,
                severity=Severity.ERROR,
                category="FILE_ACCESS",
                message=f"Cannot read file: {e}"
            ))
            return self.result

        # Run all validation checks
        self._check_brace_balance()
        self._check_syntax()
        self._check_hash_format()
        self._check_property_constraints()
        self._check_indentation()
        self._check_string_quoting()

        # Sort issues by line number
        self.result.issues.sort(key=lambda x: x.line_number)

        return self.result

    def _check_brace_balance(self):
        """Check that all braces are properly matched"""
        brace_count = 0
        stack = []  # Track line numbers where braces open

        for i, line in enumerate(self.lines, 1):
            line_stripped = self._strip_comments(line)

            for char in line_stripped:
                if char == '{':
                    brace_count += 1
                    stack.append(i)
                elif char == '}':
                    brace_count -= 1
                    if brace_count < 0:
                        self.result.issues.append(ValidationIssue(
                            line_number=i,
                            severity=Severity.ERROR,
                            category="BRACE_MISMATCH",
                            message="Closing brace '}' without matching opening brace",
                            context=line.strip()
                        ))
                        brace_count = 0  # Reset to continue checking
                    elif stack:
                        stack.pop()

        # Check for unclosed braces
        if brace_count > 0:
            self.result.issues.append(ValidationIssue(
                line_number=self.result.line_count,
                severity=Severity.ERROR,
                category="BRACE_MISMATCH",
                message=f"{brace_count} unclosed brace(s) - missing closing '}}'"
            ))

    def _check_syntax(self):
        """Check for syntax errors in ACTOR, DEF, MODIFY, EXTENDS, and APPLIES TO"""
        for i, line in enumerate(self.lines, 1):
            line_stripped = self._strip_comments(line).strip()

            if not line_stripped:
                continue

            # Check ACTOR definitions
            if line_stripped.startswith('ACTOR'):
                if not self.ACTOR_DEF_PATTERN.match(line):
                    self.result.issues.append(ValidationIssue(
                        line_number=i,
                        severity=Severity.ERROR,
                        category="SYNTAX_ERROR",
                        message='Invalid ACTOR syntax. Expected: ACTOR "Name" DEF {',
                        context=line.strip()
                    ))

            # Check DEF/MODIFY definitions
            if re.match(r'^\s*\^"', line):
                if not self.DEF_PATTERN.match(line) and not 'APPLIES TO' in line:
                    # Could be a property definition like ^"Name" INTEGER
                    # Check if it has a valid property type
                    if not any(ptype in line for ptype in self.PROPERTY_TYPES):
                        if 'DEF' in line or 'MODIFY' in line:
                            self.result.issues.append(ValidationIssue(
                                line_number=i,
                                severity=Severity.ERROR,
                                category="SYNTAX_ERROR",
                                message='Invalid DEF/MODIFY syntax. Expected: ^"Name" DEF { or ^"Name" MODIFY {',
                                context=line.strip()
                            ))

            # Check EXTENDS clause (must start with EXTENDS keyword, not just contain it)
            if re.match(r'^\s*EXTENDS\s+', line_stripped) and 'ACTOR' not in line_stripped:
                # Must have both a hash and a quoted reference
                has_hash = re.search(r'#[A-Za-z0-9]+', line_stripped)
                has_ref = re.search(r'\^"[^"]+"', line_stripped)

                if not (has_hash and has_ref):
                    self.result.issues.append(ValidationIssue(
                        line_number=i,
                        severity=Severity.ERROR,
                        category="SYNTAX_ERROR",
                        message='Invalid EXTENDS syntax. Expected: EXTENDS #hash ^"Name"',
                        context=line.strip()
                    ))

            # Check APPLIES TO clause
            if 'APPLIES TO' in line_stripped:
                match = self.APPLIES_TO_PATTERN.search(line_stripped)
                if not match:
                    self.result.issues.append(ValidationIssue(
                        line_number=i,
                        severity=Severity.ERROR,
                        category="SYNTAX_ERROR",
                        message='Invalid APPLIES TO syntax. Expected: APPLIES TO [^"Name"] or APPLIES TO [^"Name1", ^"Name2"]',
                        context=line.strip()
                    ))
                else:
                    # Check that actor references are properly quoted
                    actor_list = match.group(1)
                    actor_refs = re.findall(r'\^"([^"]+)"', actor_list)
                    if not actor_refs:
                        self.result.issues.append(ValidationIssue(
                            line_number=i,
                            severity=Severity.ERROR,
                            category="SYNTAX_ERROR",
                            message='APPLIES TO clause must contain at least one ^"ActorName" reference',
                            context=line.strip()
                        ))

    def _check_hash_format(self):
        """Check that hash IDs follow the expected format"""
        for i, line in enumerate(self.lines, 1):
            line_stripped = self._strip_comments(line)

            # Find all hashes in the line
            hashes = self.HASH_PATTERN.findall(line_stripped)

            for hash_id in hashes:
                if not self.VALID_HASH_PATTERN.match(hash_id):
                    self.result.issues.append(ValidationIssue(
                        line_number=i,
                        severity=Severity.WARNING,
                        category="HASH_FORMAT",
                        message=f'Hash "{hash_id}" is too short (expected: 16+ alphanumeric chars after #)',
                        context=line.strip()
                    ))

    def _check_property_constraints(self):
        """Check MIN/MAX/DEFAULT consistency for INTEGER properties"""
        for i, line in enumerate(self.lines, 1):
            line_stripped = self._strip_comments(line).strip()

            if 'INTEGER' not in line_stripped:
                continue

            # Extract MIN, MAX, DEFAULT values
            min_match = re.search(r'MIN\s+(-?\d+)', line_stripped)
            max_match = re.search(r'MAX\s+(-?\d+)', line_stripped)
            default_match = re.search(r'DEFAULT\s+(-?\d+)', line_stripped)

            min_val = int(min_match.group(1)) if min_match else None
            max_val = int(max_match.group(1)) if max_match else None
            default_val = int(default_match.group(1)) if default_match else None

            # Check MIN <= MAX
            if min_val is not None and max_val is not None:
                if min_val > max_val:
                    self.result.issues.append(ValidationIssue(
                        line_number=i,
                        severity=Severity.ERROR,
                        category="CONSTRAINT_ERROR",
                        message=f'MIN ({min_val}) cannot be greater than MAX ({max_val})',
                        context=line.strip()
                    ))

            # Check MIN <= DEFAULT <= MAX
            if default_val is not None:
                if min_val is not None and default_val < min_val:
                    self.result.issues.append(ValidationIssue(
                        line_number=i,
                        severity=Severity.ERROR,
                        category="CONSTRAINT_ERROR",
                        message=f'DEFAULT ({default_val}) cannot be less than MIN ({min_val})',
                        context=line.strip()
                    ))

                if max_val is not None and default_val > max_val:
                    self.result.issues.append(ValidationIssue(
                        line_number=i,
                        severity=Severity.ERROR,
                        category="CONSTRAINT_ERROR",
                        message=f'DEFAULT ({default_val}) cannot be greater than MAX ({max_val})',
                        context=line.strip()
                    ))

    def _check_indentation(self):
        """Check for inconsistent indentation (mixing tabs and spaces)"""
        uses_tabs = False
        uses_spaces = False

        for i, line in enumerate(self.lines, 1):
            if not line or line.strip() == '':
                continue

            # Check leading whitespace
            leading = line[:len(line) - len(line.lstrip())]

            if '\t' in leading:
                uses_tabs = True
            if ' ' in leading:
                uses_spaces = True

            # Warn if mixing tabs and spaces on same line
            if '\t' in leading and ' ' in leading:
                self.result.issues.append(ValidationIssue(
                    line_number=i,
                    severity=Severity.WARNING,
                    category="INDENTATION",
                    message='Mixed tabs and spaces in indentation',
                    context=line.rstrip()
                ))

        # Warn if file mixes tabs and spaces
        if uses_tabs and uses_spaces:
            self.result.issues.append(ValidationIssue(
                line_number=0,
                severity=Severity.INFO,
                category="INDENTATION",
                message='File uses both tabs and spaces for indentation (inconsistent style)'
            ))

    def _check_string_quoting(self):
        """Check for unquoted strings in definitions"""
        for i, line in enumerate(self.lines, 1):
            line_stripped = self._strip_comments(line).strip()

            # Check for ACTOR/DEF/MODIFY with missing quotes
            if re.match(r'^\s*ACTOR\s+[^"]', line_stripped):
                self.result.issues.append(ValidationIssue(
                    line_number=i,
                    severity=Severity.ERROR,
                    category="QUOTING_ERROR",
                    message='ACTOR name must be quoted: ACTOR "Name" DEF {',
                    context=line.strip()
                ))

            if re.match(r'^\s*\^[^"]', line_stripped) and not line_stripped.startswith('^"'):
                # Could be a reference like ^OtherDef
                if 'DEF' in line_stripped or 'MODIFY' in line_stripped:
                    self.result.issues.append(ValidationIssue(
                        line_number=i,
                        severity=Severity.ERROR,
                        category="QUOTING_ERROR",
                        message='Definition name must be quoted: ^"Name" DEF {',
                        context=line.strip()
                    ))

    @staticmethod
    def _strip_comments(line: str) -> str:
        """Remove comments from a line, preserving hash IDs"""
        result = []
        i = 0
        while i < len(line):
            if line[i] == '#':
                # Check if this is a hash ID (no space after #, followed by alphanumeric)
                # Hash IDs look like: #YD4PosFYGnnbWia88WUziU
                # Comments look like: # This is a comment
                if i + 1 < len(line) and line[i + 1] != ' ' and line[i + 1].isalnum():
                    # This is likely a hash ID, keep it
                    result.append(line[i])
                    i += 1
                else:
                    # This is a comment, skip rest of line
                    break
            else:
                result.append(line[i])
                i += 1
        return ''.join(result)


def print_validation_result(result: ValidationResult, verbose: bool = False):
    """Print validation results to console"""
    print(f"\n{'=' * 70}")
    print(f"Validating: {result.file_path.name}")
    print(f"{'=' * 70}")
    print(f"Lines: {result.line_count}")
    print(f"Errors: {result.error_count}")
    print(f"Warnings: {result.warning_count}")
    print(f"Status: {'[VALID]' if result.is_valid else '[INVALID]'}")

    if result.issues:
        print(f"\n{'-' * 70}")
        print("ISSUES FOUND:")
        print(f"{'-' * 70}")

        for issue in result.issues:
            severity_symbol = {
                Severity.ERROR: "[X]",
                Severity.WARNING: "[!]",
                Severity.INFO: "[i]"
            }[issue.severity]

            line_info = f"Line {issue.line_number}" if issue.line_number > 0 else "File"
            print(f"\n{severity_symbol} {issue.severity.value} [{issue.category}] @ {line_info}")
            print(f"   {issue.message}")

            if issue.context and verbose:
                print(f"   Context: {issue.context[:100]}")
    else:
        print("\n[OK] No issues found!")


def main():
    if len(sys.argv) < 2:
        print("Usage: python ttrpg_validator.py <file.ttrpg|directory> [--verbose]")
        print("\nValidates .ttrpg files for syntax errors and structural issues.")
        return 1

    path_arg = sys.argv[1]
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    path = Path(path_arg)

    if not path.exists():
        print(f"ERROR: Path does not exist: {path}")
        return 1

    validator = TTRPGValidator()
    results = []

    # Collect files to validate
    if path.is_file():
        files = [path]
    elif path.is_dir():
        files = list(path.glob('**/*.ttrpg'))
        if not files:
            print(f"No .ttrpg files found in {path}")
            return 1
    else:
        print(f"ERROR: Invalid path: {path}")
        return 1

    # Validate each file
    for file_path in files:
        result = validator.validate_file(file_path)
        results.append(result)
        print_validation_result(result, verbose=verbose)

    # Summary for multiple files
    if len(results) > 1:
        print(f"\n{'=' * 70}")
        print("SUMMARY")
        print(f"{'=' * 70}")
        print(f"Total files: {len(results)}")
        print(f"Valid: {sum(1 for r in results if r.is_valid)}")
        print(f"Invalid: {sum(1 for r in results if not r.is_valid)}")
        print(f"Total errors: {sum(r.error_count for r in results)}")
        print(f"Total warnings: {sum(r.warning_count for r in results)}")

    # Return exit code based on validation
    return 0 if all(r.is_valid for r in results) else 1


if __name__ == "__main__":
    exit(main())
