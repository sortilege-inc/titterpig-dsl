# SUPERSEDED / HISTORICAL — v0.3-era regex validator, NOT part of v4.
# A v4 validator (lint + coherence) replaces it at ../ttrpg_validator.py.

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
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional
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


# ===========================================================================
# Corpus-mode symbol tables (cross-file resolution)
# ===========================================================================

@dataclass
class FileInfo:
    file_id: str            # The string after BASE/EXTENSION/ARC/etc.
    kind: str               # "BASE" | "EXTENSION" | "ARC" | "SETTING" | "FRAME" | "CAMPAIGN"
    path: Path
    line: int               # Line where the wrapper opens


@dataclass
class HashInfo:
    hash_id: str
    def_name: str           # The ^"Name" this hash anchors
    path: Path
    line: int


@dataclass
class DefInfo:
    name: str
    path: Path
    line: int
    is_anchor: bool         # Empty-bodied DEF used as a metatype anchor
    hash_id: Optional[str]


@dataclass
class CorpusSymbols:
    files: Dict[str, FileInfo] = field(default_factory=dict)
    hashes: Dict[str, HashInfo] = field(default_factory=dict)
    defs: Dict[str, List[DefInfo]] = field(default_factory=lambda: defaultdict(list))
    aliases: Dict[str, str] = field(default_factory=dict)        # alias → canonical name
    issues_by_path: Dict[Path, List[ValidationIssue]] = field(default_factory=lambda: defaultdict(list))
    global_issues: List[ValidationIssue] = field(default_factory=list)

    def resolve_def(self, name: str) -> Optional[DefInfo]:
        """Resolve a ^"Name" reference, following aliases. Returns the non-anchor DEF
        if one exists; otherwise the first anchor; otherwise None."""
        target = name
        if target not in self.defs and target in self.aliases:
            target = self.aliases[target]
        candidates = self.defs.get(target, [])
        if not candidates:
            return None
        for c in candidates:
            if not c.is_anchor:
                return c
        return candidates[0]


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


# ===========================================================================
# Corpus mode: Pass 1 (build symbols) and Pass 2 (resolve references)
# ===========================================================================

# Patterns for symbol extraction
_FILE_DECL_RE   = re.compile(r'^\s*(BASE|EXTENSION|ARC|SETTING|FRAME|CAMPAIGN)\s+"([^"]+)"')
_DEF_ANCHORED   = re.compile(r'^\s*(#[A-Za-z0-9]+)\s+\^"([^"]+)"\s+DEF\s*\{')
_DEF_PLAIN      = re.compile(r'^\s*\^"([^"]+)"\s+DEF\s*\{')
_ACTOR_ANCHORED = re.compile(r'^\s*(#[A-Za-z0-9]+)\s+ACTOR\s+"([^"]+)"\s+DEF\s*\{')
_ACTOR_PLAIN    = re.compile(r'^\s*ACTOR\s+"([^"]+)"\s+DEF\s*\{')
_ALIAS_RE       = re.compile(r'^\s*ALIAS\s+"([^"]+)"\s*$')

_EXTENDS_RE     = re.compile(r'EXTENDS\s+(#[A-Za-z0-9]+)\s+\^"([^"]+)"')
_APPLIES_TO_RE  = re.compile(r'APPLIES\s+TO\s+\[([^\]]+)\]')
_LIST_OF_TYPE_RE = re.compile(r'LIST\s+OF\s+\^"([^"]+)"')
_DEPENDS_ON_RE   = re.compile(r'DEPENDS_ON\s+"([^"]+)"')
_USES_EXTENSION_RE = re.compile(r'USES_EXTENSION\s+"([^"]+)"')
_USES_SETTING_RE   = re.compile(r'USES_SETTING\s+"([^"]+)"')
_USES_FRAME_RE     = re.compile(r'USES_FRAME\s+"([^"]+)"')


def _strip_line_comment(line: str) -> str:
    """Drop `# comment` portion while preserving #hashIDs (which have no space after #)."""
    out = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '#':
            # hash ID iff next char is alphanumeric (no space)
            if i + 1 < len(line) and line[i + 1].isalnum():
                out.append(ch)
                i += 1
            else:
                break  # rest of line is a comment
        else:
            out.append(ch)
            i += 1
    return ''.join(out)


def _is_anchor_body(lines: List[str], open_line_idx: int) -> bool:
    """A DEF is an anchor if its body (between { and matching }) contains
    only comments and whitespace — no PROPERTIES, RULES, ALIAS, sub-blocks, etc.
    `open_line_idx` is the 0-indexed line containing the opening `{`.
    """
    depth = 0
    started = False
    for j in range(open_line_idx, len(lines)):
        stripped_line = _strip_line_comment(lines[j])
        opens = stripped_line.count('{')
        closes = stripped_line.count('}')
        new_depth = depth + opens - closes
        if not started and opens > 0:
            started = True
            # Anything after the `{` on the same line counts as body content
            # (but only the part *after* the first `{`)
            tail = stripped_line.split('{', 1)[1] if '{' in stripped_line else ''
            tail = tail.rstrip()
            # Strip a trailing `}` if depth ends at 0 on this line (empty inline body)
            if new_depth == 0 and tail.endswith('}'):
                tail = tail[:-1].rstrip()
            if tail:
                return False
            depth = new_depth
            if depth == 0:
                return True
            continue
        if not started:
            depth = new_depth
            continue
        # Inside body
        if new_depth < depth:
            # We're closing; check content of this line up to the closing }
            head = stripped_line.split('}', 1)[0].strip()
            if head:
                return False
            return True
        # Same depth or deeper — any non-whitespace content disqualifies
        if stripped_line.strip():
            return False
        depth = new_depth
    return True  # Shouldn't get here on a balanced file


def build_corpus_symbols(files: List[Path]) -> CorpusSymbols:
    """Pass 1: walk every .ttrpg file in the corpus and build symbol tables.

    Records:
      - File-level declarations (BASE / EXTENSION / ARC / SETTING / FRAME / CAMPAIGN)
      - Top-level DEFs (i.e., DEFs at brace-depth 1 inside the file wrapper)
      - Hash IDs anchoring those DEFs
      - ALIAS lines within DEF bodies
    Detects global integrity issues (duplicate FileIDs, duplicate hashes, etc.).
    """
    symbols = CorpusSymbols()

    for path in files:
        try:
            text = path.read_text(encoding='utf-8')
        except Exception as e:
            symbols.global_issues.append(ValidationIssue(
                line_number=0,
                severity=Severity.ERROR,
                category="FILE_ACCESS",
                message=f"Cannot read {path}: {e}",
            ))
            continue
        lines = text.split('\n')

        # Track brace depth (line by line, comments stripped)
        depth = 0
        current_def_name: Optional[str] = None
        current_def_depth: Optional[int] = None

        for i, raw in enumerate(lines):
            line = _strip_line_comment(raw)
            line_no = i + 1

            # Detect file-level wrapper
            m = _FILE_DECL_RE.match(line)
            if m and depth == 0:
                kind, file_id = m.group(1), m.group(2)
                if file_id in symbols.files:
                    prior = symbols.files[file_id]
                    symbols.global_issues.append(ValidationIssue(
                        line_number=line_no,
                        severity=Severity.ERROR,
                        category="DUPLICATE_FILE_ID",
                        message=f'FileID "{file_id}" already declared in {prior.path.name}:{prior.line}',
                        context=raw.strip(),
                    ))
                else:
                    symbols.files[file_id] = FileInfo(file_id, kind, path, line_no)

            # Detect top-level DEF starts (only at depth 1 — directly inside wrapper)
            if depth == 1:
                hash_id: Optional[str] = None
                def_name: Optional[str] = None

                m = _DEF_ANCHORED.match(line)
                if m:
                    hash_id, def_name = m.group(1), m.group(2)
                else:
                    m = _DEF_PLAIN.match(line)
                    if m:
                        def_name = m.group(1)
                    else:
                        m = _ACTOR_ANCHORED.match(line)
                        if m:
                            hash_id, def_name = m.group(1), m.group(2)
                        else:
                            m = _ACTOR_PLAIN.match(line)
                            if m:
                                def_name = m.group(1)

                if def_name is not None:
                    is_anchor = _is_anchor_body(lines, i)
                    info = DefInfo(
                        name=def_name, path=path, line=line_no,
                        is_anchor=is_anchor, hash_id=hash_id,
                    )
                    symbols.defs[def_name].append(info)

                    if hash_id is not None:
                        if hash_id in symbols.hashes:
                            prior = symbols.hashes[hash_id]
                            symbols.global_issues.append(ValidationIssue(
                                line_number=line_no,
                                severity=Severity.ERROR,
                                category="DUPLICATE_HASH",
                                message=f'Hash {hash_id} also defined for ^"{prior.def_name}" at {prior.path.name}:{prior.line}',
                                context=raw.strip(),
                            ))
                        else:
                            symbols.hashes[hash_id] = HashInfo(hash_id, def_name, path, line_no)

                    current_def_name = def_name
                    current_def_depth = depth

            # Detect ALIAS inside a DEF body
            if current_def_name is not None and depth >= 1:
                am = _ALIAS_RE.match(line)
                if am:
                    alias_name = am.group(1)
                    if alias_name in symbols.aliases and symbols.aliases[alias_name] != current_def_name:
                        symbols.global_issues.append(ValidationIssue(
                            line_number=line_no,
                            severity=Severity.WARNING,
                            category="DUPLICATE_ALIAS",
                            message=f'Alias "{alias_name}" maps to both ^"{symbols.aliases[alias_name]}" and ^"{current_def_name}"',
                            context=raw.strip(),
                        ))
                    else:
                        symbols.aliases[alias_name] = current_def_name

            # Update depth at end-of-line
            new_depth = depth + line.count('{') - line.count('}')
            if current_def_depth is not None and new_depth <= current_def_depth:
                current_def_name = None
                current_def_depth = None
            depth = new_depth

    # Global integrity checks: duplicate DEF names (non-anchor vs non-anchor)
    for name, entries in symbols.defs.items():
        non_anchors = [e for e in entries if not e.is_anchor]
        if len(non_anchors) > 1:
            locations = ", ".join(f"{e.path.name}:{e.line}" for e in non_anchors)
            symbols.global_issues.append(ValidationIssue(
                line_number=non_anchors[1].line,
                severity=Severity.WARNING,
                category="DUPLICATE_DEF_NAME",
                message=f'^"{name}" has {len(non_anchors)} non-anchor definitions: {locations}',
            ))

    return symbols


def check_cross_file_references(file_path: Path, lines: List[str],
                                symbols: CorpusSymbols) -> List[ValidationIssue]:
    """Pass 2: resolve EXTENDS hashes, APPLIES TO names, LIST OF types,
    DEPENDS_ON / USES_* file IDs against the symbol tables."""
    issues: List[ValidationIssue] = []
    for i, raw in enumerate(lines, 1):
        line = _strip_line_comment(raw)

        # EXTENDS #hash ^"Name"
        for m in _EXTENDS_RE.finditer(line):
            hash_id, name = m.group(1), m.group(2)
            if hash_id not in symbols.hashes:
                issues.append(ValidationIssue(
                    line_number=i, severity=Severity.ERROR,
                    category="UNRESOLVED_EXTENDS_HASH",
                    message=f'EXTENDS hash {hash_id} does not anchor any DEF in the corpus',
                    context=raw.strip(),
                ))
            elif symbols.hashes[hash_id].def_name != name:
                expected = symbols.hashes[hash_id].def_name
                issues.append(ValidationIssue(
                    line_number=i, severity=Severity.ERROR,
                    category="EXTENDS_HASH_NAME_MISMATCH",
                    message=f'EXTENDS hash {hash_id} anchors ^"{expected}", not ^"{name}"',
                    context=raw.strip(),
                ))

        # APPLIES TO [^"X", ^"Y"]
        for m in _APPLIES_TO_RE.finditer(line):
            for ref in re.findall(r'\^"([^"]+)"', m.group(1)):
                if symbols.resolve_def(ref) is None:
                    issues.append(ValidationIssue(
                        line_number=i, severity=Severity.ERROR,
                        category="UNRESOLVED_APPLIES_TO",
                        message=f'APPLIES TO references ^"{ref}" which is not defined in the corpus',
                        context=raw.strip(),
                    ))

        # LIST OF ^"Type"  (LIST OF STRING is fine, no caret ref)
        for m in _LIST_OF_TYPE_RE.finditer(line):
            type_name = m.group(1)
            if symbols.resolve_def(type_name) is None:
                issues.append(ValidationIssue(
                    line_number=i, severity=Severity.WARNING,
                    category="UNRESOLVED_LIST_TYPE",
                    message=f'LIST OF ^"{type_name}" — type is not defined in the corpus',
                    context=raw.strip(),
                ))

        # DEPENDS_ON "FileID" (must be a BASE)
        m = _DEPENDS_ON_RE.search(line)
        if m:
            file_id = m.group(1)
            if file_id not in symbols.files:
                issues.append(ValidationIssue(
                    line_number=i, severity=Severity.ERROR,
                    category="UNRESOLVED_DEPENDS_ON",
                    message=f'DEPENDS_ON "{file_id}" — no file with that ID in the corpus',
                    context=raw.strip(),
                ))
            elif symbols.files[file_id].kind != "BASE":
                actual = symbols.files[file_id].kind
                issues.append(ValidationIssue(
                    line_number=i, severity=Severity.ERROR,
                    category="DEPENDS_ON_WRONG_KIND",
                    message=f'DEPENDS_ON "{file_id}" expects a BASE, but that ID is a {actual}',
                    context=raw.strip(),
                ))

        # USES_EXTENSION (must be an EXTENSION)
        m = _USES_EXTENSION_RE.search(line)
        if m:
            file_id = m.group(1)
            if file_id not in symbols.files:
                issues.append(ValidationIssue(
                    line_number=i, severity=Severity.ERROR,
                    category="UNRESOLVED_USES_EXTENSION",
                    message=f'USES_EXTENSION "{file_id}" — no file with that ID in the corpus',
                    context=raw.strip(),
                ))
            elif symbols.files[file_id].kind != "EXTENSION":
                actual = symbols.files[file_id].kind
                issues.append(ValidationIssue(
                    line_number=i, severity=Severity.ERROR,
                    category="USES_EXTENSION_WRONG_KIND",
                    message=f'USES_EXTENSION "{file_id}" expects an EXTENSION, but that ID is a {actual}',
                    context=raw.strip(),
                ))

        # USES_SETTING (must be a SETTING)
        m = _USES_SETTING_RE.search(line)
        if m:
            file_id = m.group(1)
            if file_id not in symbols.files:
                issues.append(ValidationIssue(
                    line_number=i, severity=Severity.ERROR,
                    category="UNRESOLVED_USES_SETTING",
                    message=f'USES_SETTING "{file_id}" — no file with that ID in the corpus',
                    context=raw.strip(),
                ))
            elif symbols.files[file_id].kind != "SETTING":
                actual = symbols.files[file_id].kind
                issues.append(ValidationIssue(
                    line_number=i, severity=Severity.ERROR,
                    category="USES_SETTING_WRONG_KIND",
                    message=f'USES_SETTING "{file_id}" expects a SETTING, but that ID is a {actual}',
                    context=raw.strip(),
                ))

        # USES_FRAME (must be a FRAME)
        m = _USES_FRAME_RE.search(line)
        if m:
            file_id = m.group(1)
            if file_id not in symbols.files:
                issues.append(ValidationIssue(
                    line_number=i, severity=Severity.ERROR,
                    category="UNRESOLVED_USES_FRAME",
                    message=f'USES_FRAME "{file_id}" — no file with that ID in the corpus',
                    context=raw.strip(),
                ))
            elif symbols.files[file_id].kind != "FRAME":
                actual = symbols.files[file_id].kind
                issues.append(ValidationIssue(
                    line_number=i, severity=Severity.ERROR,
                    category="USES_FRAME_WRONG_KIND",
                    message=f'USES_FRAME "{file_id}" expects a FRAME, but that ID is a {actual}',
                    context=raw.strip(),
                ))

    return issues


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
        print("When given a directory, also performs corpus-wide cross-file checks")
        print("(EXTENDS hash resolution, DEPENDS_ON / USES_* targets, etc.).")
        return 1

    path_arg = sys.argv[1]
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    path = Path(path_arg)

    if not path.exists():
        print(f"ERROR: Path does not exist: {path}")
        return 1

    validator = TTRPGValidator()
    results = []

    # Collect files to validate. In corpus mode we also scan .arc/.setting/.frame/.campaign
    # so their file-level wrappers and references contribute to the symbol table.
    if path.is_file():
        files = [path]
        corpus_files: List[Path] = []
        corpus_mode = False
    elif path.is_dir():
        files = sorted(path.glob('**/*.ttrpg'))
        if not files:
            print(f"No .ttrpg files found in {path}")
            return 1
        corpus_files = sorted(
            list(path.glob('**/*.ttrpg'))
            + list(path.glob('**/*.arc'))
            + list(path.glob('**/*.setting'))
            + list(path.glob('**/*.frame'))
            + list(path.glob('**/*.campaign'))
        )
        corpus_mode = True
    else:
        print(f"ERROR: Invalid path: {path}")
        return 1

    # Pass 1: build symbol tables (corpus mode only)
    symbols: Optional[CorpusSymbols] = None
    if corpus_mode:
        symbols = build_corpus_symbols(corpus_files)
        print(f"\n{'=' * 70}")
        print(f"CORPUS PASS 1: SYMBOL TABLE")
        print(f"{'=' * 70}")
        print(f"Files indexed:       {len(symbols.files)}")
        print(f"Top-level DEFs:      {sum(len(v) for v in symbols.defs.values())}")
        print(f"Hash anchors:        {len(symbols.hashes)}")
        print(f"Aliases:             {len(symbols.aliases)}")
        print(f"Global integrity:    {len(symbols.global_issues)} issue(s)")
        if symbols.global_issues:
            for issue in symbols.global_issues:
                sev_symbol = {Severity.ERROR: "[X]", Severity.WARNING: "[!]", Severity.INFO: "[i]"}[issue.severity]
                loc = f"Line {issue.line_number}" if issue.line_number > 0 else "File"
                print(f"\n{sev_symbol} {issue.severity.value} [{issue.category}] @ {loc}")
                print(f"   {issue.message}")
                if issue.context and verbose:
                    print(f"   Context: {issue.context[:100]}")

    # Pass 2: per-file validation (existing) + cross-file checks (corpus mode)
    for file_path in files:
        result = validator.validate_file(file_path)
        if corpus_mode and symbols is not None:
            try:
                lines = file_path.read_text(encoding='utf-8').split('\n')
                xrefs = check_cross_file_references(file_path, lines, symbols)
                result.issues.extend(xrefs)
                result.issues.sort(key=lambda x: x.line_number)
            except Exception as e:
                result.issues.append(ValidationIssue(
                    line_number=0, severity=Severity.ERROR,
                    category="FILE_ACCESS",
                    message=f"Cross-file pass could not read file: {e}",
                ))
        results.append(result)
        print_validation_result(result, verbose=verbose)

    # Summary for multiple files
    if len(results) > 1 or corpus_mode:
        print(f"\n{'=' * 70}")
        print("SUMMARY")
        print(f"{'=' * 70}")
        print(f"Total files: {len(results)}")
        print(f"Valid: {sum(1 for r in results if r.is_valid)}")
        print(f"Invalid: {sum(1 for r in results if not r.is_valid)}")
        print(f"Total errors: {sum(r.error_count for r in results)}")
        print(f"Total warnings: {sum(r.warning_count for r in results)}")
        if corpus_mode and symbols is not None:
            print(f"Global integrity issues: {len(symbols.global_issues)}")

    # Exit code: bad if any per-file ERROR OR any global ERROR
    global_errors = (
        sum(1 for i in (symbols.global_issues if symbols else []) if i.severity == Severity.ERROR)
    )
    per_file_ok = all(r.is_valid for r in results)
    return 0 if (per_file_ok and global_errors == 0) else 1


if __name__ == "__main__":
    exit(main())
