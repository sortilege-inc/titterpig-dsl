#!/usr/bin/env python3
"""
Titterpig DSL validator (v0.5, with the v0.6 working draft).

Two levels of validation over one or more .ttrpg files (or directories):

  LINT (spec adherence, per file)
    - lexical correctness + brace/bracket balance
    - hash IDs are >= 16 characters
    - FIAT requires a reason string
    - SPEC_VERSION is declared
    - an inline INTEGER value lies within a same-declaration MIN/MAX

  COHERENCE (referential integrity, across the whole corpus)
    - no duplicate definition anchors (#hash): a DEF's hash stands once in a corpus, and a
      second DEF under it is an error whatever its name (v0.6, DECISION-27; the implicit
      override is withdrawn). A named block stated again under its own hash and name, and a
      codex ENTITY restated to add sources, are not duplicates.
    - EXTENDS / APPLIES TO / LIST OF targets resolve to a defined ^"Name"
    - DEPENDS_ON targets resolve to a defined file id
    - DECISION-6: bound-ref bases & arguments, PARAMETERS OF types, and ALIAS FOR
      targets all resolve (an ALIAS name is itself a resolvable name)
    - CHOOSE n (v0.6, DECISION-15): the count is written and is 1 or more; entity
      options and the OF type resolve; a DISTINCT choice from a list does not pick
      more than are listed; every WITH property is a property of the type; a WITH
      does not mix AND and OR (nested conditions are a to-do) and each term takes one
      value.
    - REF (v0.6, DECISION-17): the OF type and the entity resolve; where a type up the
      chain declares the property REF OF a type, the entity is of that type.
    - Embedded references (v0.6, DECISION-20): every ^\"Name\" inside a string resolves,
      with or without a #hash before it and a /\"literal\" after it; a literal is not empty.
    - TABLE (v0.6, DECISION-21): at least one AXIS; each AT gives one coordinate per axis,
      of a kind the axis takes and inside its range or list; no two cells cover the same
      coordinates; an entity on an axis OF a type is of that type; COLUMNS needs one axis
      OF a type and names its properties. A TABLE with no AXIS is left alone below 0.6.
    - Named blocks (v0.6, DECISION-24, §20): the hash of a named block (SCENE, LOCATION,
      ENTRY, …) is an anchor like a DEF's: unique, and referenceable from any file. A
      block's name is a label local to its file. SCENE_REF, LEADS_TO, COMPLETED_SCENES,
      OPPONENTS and a scene's LOCATION are reference sites and resolve.
    - TYPE of a SCENE or CONFLICT (v0.6, DECISION-23, §16): a reference that resolves and,
      where ^"Scene Type" / ^"Conflict Type" is defined, names one. A string is a warning
      below 0.6 and an error from 0.6.
    - FROM (v0.6, DECISION-22, §16): the import names its container's kind, the container
      is in the loaded set and is of that kind, and each INCLUDE item resolves. A bare
      FROM "id" is a warning below 0.6 and an error from 0.6.
    - Markdown emphasis in a string (v0.6, DECISION-19): a paired **…** or *…* is a warning
      in a file below 0.6 and an error from 0.6; FIAT excuses asterisks the source prints.
    - EMPHASIS / LABEL (v0.6, DECISION-19): the words before the brace are a kind
      (BOLD, ITALIC, each once) or a depth (a whole number, 1 or more). That each span
      is in its DEF's prose is check_references.py's rule, not this tool's.
    - Dice (v0.6, DECISION-18): FACES lists at least one face, a range runs low to high,
      a WEIGHT is a positive integer; ROLL n OF ^"die" has a count of 1 or more and a die
      that resolves and EXTENDS ^"Die"; NEXT has a statement before and after it.
    - SET / TRANSFORM (v0.6, DECISION-16): a target precedes it on the line and resolves;
      the method is ADD, SUBTRACT, MULTIPLY, DIVIDE or MANUAL "…"; the amount is an
      integer or a reference that resolves. A SET directly inside a MODIFY body is the
      §13 directive and is checked there. CHOICE, which CHOOSE replaced, still has its options resolved; it is a
      WARNING in a file declaring SPEC_VERSION below 0.6 (or none) and an ERROR in
      one declaring 0.6 or later.
    - MODIFICATION SYSTEM (spec §13) — see below
    - REPRINT ^"X" (v0.5 addendum, DECISION-14): X must resolve; a file must not
      both REPRINT and DEF the same entity

MODIFICATION SYSTEM (spec §13). An overlay that names a target which does not exist
modifies nothing, silently, forever; these checks are the gate against that.

  - MODIFY ^"X" { } / OVERRIDE ^"X" { } / bare OVERRIDE ^"X" — X must resolve to a
    definition somewhere in the loaded corpus (normally the DEPENDS_ON parent).
    Unresolvable target = ERROR.
  - ADD ^"X" DEF { } introduces content the parent does not have; if X is already
    defined elsewhere in the corpus it is a WARNING, not an error — the loaded set is
    not necessarily the consumer's composition set (§13 Composition & Precedence), so
    the collision may be with a sourcebook that would never be co-loaded. The message
    points at OVERRIDE / MODIFY, which is what a deliberate replacement should say.
  - Inside MODIFY (§13, decided 2026-07-25):
      SET ^"P" <type>       changes a property the target ALREADY declares (its own,
                            or one inherited through EXTENDS). Naming an undeclared
                            property is an ERROR — that is how a typo'd SET is caught.
      PROPERTIES { ... }    introduces new properties on the target. This is the form
                            the l5r5e errata corpus already uses, and it is the only
                            way to widen a type with a field it never had.
      ADD_TO ^"P" v         P must exist and be a LIST (ERROR otherwise).
      REMOVE_FROM ^"P" v    P must exist and be a LIST (ERROR otherwise); if P declares
                            literal members and v is not among them, WARNING — an
                            earlier layer's ADD_TO may legitimately have put it there.
      SET DESCRIPTION "…"   replaces the target's whole DESCRIPTION with a variant
                            printing's text (v0.5 addendum); it must be followed by a
                            string (ERROR otherwise).
  - SET ^"P" ENUM [...] that DROPS a value warns for every loaded definition extending
    the target that still assigns a dropped value — narrowing an enum is legal, but
    orphaning a live instance with it is a mistake.

FIAT: a value or element marked  FIAT "reason"  is exempt from the COHERENCE and
inline-range findings it would otherwise raise. An element-level FIAT (a `FIAT "reason"`
statement alone on a line in a DEF body) cascades over that DEF's whole subtree; a
property-level FIAT (trailing a property declaration) waives just that line. FIAT does
NOT waive structural/lexical lint (unbalanced braces, a missing reason, etc.). It does
waive the Markdown-emphasis finding, for asterisks the source prints.

BRIDGES (spec §21) — .bridge files are checked in TWO-CORPUS mode. A bridge spans two
edition namespaces, so an ORIGIN-side caret reference is resolved against the ORIGIN
edition's corpus and a DESTINATION-side one against the DESTINATION edition's corpus;
neither is ever checked against the other, and a bridge's own definitions (its declared
dispositions, its guidance labels) belong to neither edition. Supply a corpus per
edition id:

    ttrpg_validator.py bridges/0.5/ --corpus dnd5e=<dir> --corpus dnd5.5e=<dir>

A side declared EXTERNAL "reason" has no titterpig corpus; its references are counted
and reported, never silently passed. A non-EXTERNAL side with no --corpus mapping is an
ERROR: "not checked" must never read as "checked and fine". An untyped referent (a plain
string where a caret ref could have gone) is not gated, but WARNS if it would in fact
have resolved — so quoting cannot be used to dodge the reference gate.

PROSE FIELDS (spec §10, DECISION-30). A definition's prose is DESCRIPTION. TEXT "…" as a
statement directly in a DEF is a WARNING in a file that declares SPEC_VERSION below 0.6, or
none, and an ERROR from 0.6. TEXT inside an ENTRY or any other block is not looked at.

ACTOR FILES (spec §2, DECISION-28). An .actor file is an EXTENSION file of instances.

  - it opens with the EXTENSION wrapper. A file that opens with a bare DEF is the form older
    than 0.6: one WARNING, which stands in for the missing-SPEC_VERSION warning.
  - every top-level DEF extends a type; an ACTOR or TEMPLATE definition, a DEF that extends
    nothing, and a MODIFY / OVERRIDE / ADD / REPRINT / ALIAS belong in a .ttrpg (WARNING in a
    file that declares SPEC_VERSION below 0.6, ERROR from 0.6).
  - a wrapped .actor declares SPEC_VERSION as any file does.

VALUES AGAINST DECLARATIONS (spec §5, §5b, §6, §8, DECISION-32).

  - errors at every version: an EXTENDS cycle; an ALIAS cycle; a bound reference with more
    arguments than its base declares PARAMETERS, with arguments where the base declares none,
    or with a string outside a parameter's list.
  - WARNING in a file that declares SPEC_VERSION below 0.6, ERROR from 0.6, waived by FIAT: an
    INTEGER outside the MIN / MAX it inherits; a value outside the ENUM it inherits; a value
    of another kind than its type, or than the type it inherits; a named member of a
    LIST OF ^"Type" that does not extend the type; one property written twice in a definition.
  - a hash shorter than 16 characters, or with an underscore: the same gating, not waivable.
  - REQUIRED (§8, DECISION-34), the same gating and waived by an element-level FIAT: an
    instance that lacks a property a type up its chain declares REQUIRED. ^"Name" is answered
    by the DEF's own name.
  - not checked: a DEPENDS_ON VERSION pin (audit B5), a value for a property no type
    declares, and the fields of a nested or unnamed DEF.
  - a name two definitions share is not followed up an EXTENDS chain; give the hash (§5d).

PORTS (spec §19, DECISION-26). A file made from another edition's file declares it in its
header:  ORIGIN "arm5e" EXTENSION "ArM5_Grogs_Abilities".  A port keeps its origin's hashes.

  - lint: the line names an edition id, a container kind and a container id; it stands in
    the header; a file has at most one.
  - a port and its origin in one loaded set is an ERROR (they are two editions' files).
  - with --corpus <edition>=<dir> for the origin's edition: the origin container must exist
    there and be of the kind named, and every hash the port shares with it must carry the
    same name in both (ERROR otherwise).
  - with no corpus for that edition the claim is not checked: one WARNING per edition id.

Usage:  ttrpg_validator.py <file-or-dir> [more ...] [--corpus <edition>=<dir> ...]
Exit:   0 = no errors (warnings allowed); 1 = one or more errors; 2 = bad invocation.
"""
from __future__ import annotations
import sys
import os
import re
import unicodedata
from dataclasses import dataclass

HASH_MIN_BODY = 16

# Property types the spec declares (§8). A caret followed by one of these inside a
# PROPERTIES block is a property declaration; anything else is not.
PROP_TYPE_KW = ('STRING', 'INTEGER', 'BOOLEAN', 'ENUM', 'LIST', 'DEF', 'TEXT', 'REF', 'ROLL')

# What may open the statement AFTER a `REF [OF ^"Type"]`: a reference followed by one of
# these belongs to that next statement and is not the REF's value (§8, DECISION-17).
NEXT_STATEMENT_KW = PROP_TYPE_KW + ('CHOOSE', 'SET', 'TRANSFORM', 'MODIFY')
CHANGE_METHODS = ('ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE')
EMPHASIS_KINDS = ('BOLD', 'ITALIC')      # v0.6, DECISION-19 (§5c)
CONTAINER_KINDS = ('BASE', 'EXTENSION', 'SETTING', 'FRAME', 'ARC', 'CAMPAIGN')    # §3, §16
# Keywords whose `#hash ^"Name" {` names something that exists already, and so declare no block.
NOT_A_BLOCK = ('DEF', 'MODIFY', 'OVERRIDE', 'ADD', 'EXTENDS', 'ALIAS', 'FOR', 'OF', 'REF', 'FROM',
               'INCLUDE', 'TO', 'REPRINT', 'SELECT', 'CONCERNS', 'ENTITY', 'AXIS', 'AT', 'ROLL',
               'CHOOSE', 'WITH', 'TYPE', 'SCENE_REF', 'LEADS_TO', 'OPPONENTS', 'COMPLETED_SCENES')
# References between narrative blocks (§16, §5d): keyword -> what the finding calls it.
BLOCK_REF_ONE = {'SCENE_REF': 'scene ref'}
BLOCK_REF_LIST = {'LEADS_TO': 'leads-to', 'COMPLETED_SCENES': 'completed scene', 'OPPONENTS': 'opponent'}
# Markdown emphasis inside a string (§5c, DECISION-19): a paired **…** or *…* on one line of
# text. An asterisk with a space after it (a footnote mark, a bullet) or a letter or digit
# or a closing bracket before it (`20*`, `5*3`, `20 (+1)*`) does not open a span, so the
# asterisks books print mostly pass.
MD_BOLD = re.compile(r'\*\*(?=[^\s*])((?:(?!\\n|\*\*).)+?)(?<=[^\s*])\*\*')
MD_ITALIC = re.compile(r'(?<![*\w\\)\]])\*(?=[^\s*])((?:(?!\\n)[^*\n])+?)(?<=[^\s*])\*(?![*\w])')
# An embedded reference inside a string (§5c, DECISION-20): [#hash ]^\"Name\"[/\"literal\"].
# In an ordinary string the quotes are escaped; in a triple-quoted one they are not. Group 2
# is whichever quote form opened the name, and the closers must match it.
EMBEDDED_REF = re.compile(r'(?:(#[A-Za-z0-9_]+)[ \t]+)?\^(\\?")((?:(?!\\?").)+?)\2'
                          r'(?:/\2((?:(?!\\?").)*?)\2)?', re.S)


def parse_ref(toks, j):
    """toks[j] is the token after `REF`. Returns (type, type_hash, type_line, value,
    value_hash, value_line, next index) for `REF [OF [#h] ^"Type"] [[#h] ^"Entity"]`."""
    ty = th = tl = val = vh = vl = None
    if j < len(toks) and toks[j].kind == 'ID' and toks[j].val == 'OF':
        j += 1
        if j < len(toks) and toks[j].kind == 'HASH':
            th = toks[j].val; j += 1
        if j < len(toks) and toks[j].kind == 'CARET':
            ty, tl = toks[j].val, toks[j].line; j += 1
    k = j
    h = None
    if k < len(toks) and toks[k].kind == 'HASH':
        h = toks[k].val; k += 1
    if k < len(toks) and toks[k].kind == 'CARET':
        nxt = toks[k + 1] if k + 1 < len(toks) else None
        if not (nxt is not None and nxt.kind == 'ID' and nxt.val in NEXT_STATEMENT_KW):
            val, vh, vl = toks[k].val, h, toks[k].line
            j = k + 1
    return ty, th, tl, val, vh, vl, j


@dataclass
class Tok:
    kind: str  # STR HASH CARET INT BOOL ID LBRACE RBRACE LBRACK RBRACK COMMA COLON
    val: str
    line: int


@dataclass
class Finding:
    file: str
    level: str  # 'lint' | 'coherence'
    sev: str    # 'error' | 'warning'
    line: int
    msg: str


def name_key(name):
    """When two names are the same (§14, DECISION-33): the same characters once what a reader
    cannot see, or should not care about, is folded. Unicode normal form; a run of white space
    as one space; a curly quote as a straight one; \" read as the quote it writes. Case,
    punctuation and accents count. check_references.py and check_constructs.py carry the same
    function."""
    s = unicodedata.normalize('NFC', name).replace('\\"', '"')
    s = s.replace('\u2019', "'").replace('\u2018', "'").replace('\u201c', '"').replace('\u201d', '"')
    return re.sub(r'\s+', ' ', s).strip()


def tokenize(text, fname, findings):
    toks = []
    i, n, line = 0, len(text), 1
    while i < n:
        c = text[i]
        if c == '\n':
            line += 1; i += 1; continue
        if c in ' \t\r':
            i += 1; continue
        if c == '/' and i + 1 < n and text[i + 1] == '/':
            while i < n and text[i] != '\n':
                i += 1
            continue
        if c == '#':
            # a hash id is '#' + alphanumeric; anything else ('# ', EOL, '##', '#-') is a comment
            if i + 1 >= n or not text[i + 1].isalnum():
                while i < n and text[i] != '\n':
                    i += 1
                continue
            j = i + 1
            while j < n and (text[j].isalnum() or text[j] == '_'):
                j += 1
            toks.append(Tok('HASH', text[i:j], line)); i = j; continue
        if c == '^' and i + 1 < n and text[i + 1] == '"':
            j, start = i + 2, line
            while j < n and text[j] != '"':
                # a quote inside a name is written \" (v0.6, DECISION-25), as in a string
                if text[j] == '\\' and j + 1 < n:
                    j += 2
                    continue
                if text[j] == '\n':
                    line += 1
                j += 1
            if j >= n:
                findings.append(Finding(fname, 'lint', 'error', start, "unterminated caret reference"))
                break
            toks.append(Tok('CARET', name_key(text[i + 2:j]), start)); i = j + 1; continue
        if c == '"':
            if text[i:i + 3] == '"""':
                j = text.find('"""', i + 3)
                if j < 0:
                    findings.append(Finding(fname, 'lint', 'error', line, "unterminated triple-quoted string"))
                    break
                toks.append(Tok('STR', text[i + 3:j], line))
                line += text[i:j + 3].count('\n'); i = j + 3; continue
            j, start = i + 1, line
            while j < n and text[j] != '"':
                if text[j] == '\\' and j + 1 < n:
                    j += 2; continue
                if text[j] == '\n':
                    line += 1
                j += 1
            if j >= n:
                findings.append(Finding(fname, 'lint', 'error', start, "unterminated string"))
                break
            toks.append(Tok('STR', text[i + 1:j], start)); i = j + 1; continue
        simple = {'{': 'LBRACE', '}': 'RBRACE', '[': 'LBRACK', ']': 'RBRACK', ',': 'COMMA', ':': 'COLON',
                  '(': 'LPAREN', ')': 'RPAREN', '=': 'EQ'}
        if c in simple:
            toks.append(Tok(simple[c], c, line)); i += 1; continue
        if c.isdigit() or (c == '-' and i + 1 < n and text[i + 1].isdigit()):
            j = i + 1
            while j < n and text[j].isdigit():
                j += 1
            toks.append(Tok('INT', text[i:j], line)); i = j; continue
        if c.isalpha() or c == '_':
            j = i + 1
            while j < n and (text[j].isalnum() or text[j] == '_'):
                j += 1
            w = text[i:j]
            toks.append(Tok('BOOL' if w in ('true', 'false') else 'ID', w, line)); i = j; continue
        i += 1  # unknown char — skip
    return toks


# ═══════════════════════════════════════════════════════════════════════════
# BRIDGE analysis (spec §21)
# ═══════════════════════════════════════════════════════════════════════════

SIDE_KW = ('ORIGIN', 'DESTINATION')
UNIT_KW = ('MAP', 'REMAINDER', 'PROCEDURE')
CONVERT_OPS = ('UNCHANGED', 'SCALE', 'RESTATE', 'MANUAL')


def analyze_bridge(fname, text, findings):
    """Structure a .bridge file. Every reference is SIDE-QUALIFIED: the side comes
    from the enclosing slot keyword or an inline ORIGIN/DESTINATION qualifier, and
    is never inferred. A header side declaration (`ORIGIN "dnd5e" VERSION "0.4"`)
    is distinguished from a referent slot (`DESTINATION "Tiers of Play"`) by brace
    depth — the header sits at depth 1, referents at depth >= 2."""
    toks = tokenize(text, fname, findings)
    n = len(toks)
    sides = {}                    # 'ORIGIN'/'DESTINATION' -> {edition, version, external, line}
    defined_names, anchors = {}, {}
    local_refs = []               # DISPOSITION refs -> resolve against this file's own names
    sided_refs = []               # (side, typed, name, line)
    topics = []                   # (string, line) — untyped, ungated by design
    aliases = {}                  # side -> {alias name} the document uses (§21 ALIASES)
    file_ids = []
    has_spec_version = False
    depth = 0
    block_stack = []              # names of the enclosing bridge blocks
    pending = None                # a keyword that may open the next '{'
    unit = None                   # field bag for the open MAP/REMAINDER/PROCEDURE/ENTRY
    units = []
    unit_at = {}                  # brace depth -> unit opened there
    waived_ranges = []            # line ranges of FIAT-waived units (§8)

    i = 0
    while i < n:
        t = toks[i]
        if t.kind == 'LBRACE':
            depth += 1
            block_stack.append(pending or '?')
            if pending in UNIT_KW or pending == 'ENTRY':
                unit = {'kind': pending, 'line': t.line, 'fields': set(), 'converts': 0}
                units.append(unit)
                unit_at[depth] = unit
            pending = None
            i += 1
            continue
        if t.kind == 'RBRACE':
            closing = unit_at.pop(depth, None)
            if closing and closing.get('waived'):
                waived_ranges.append((closing['line'], t.line))
            depth -= 1
            if block_stack:
                block_stack.pop()
            unit = unit_at.get(max(unit_at), None) if unit_at else None
            i += 1
            continue
        if t.kind != 'ID':
            i += 1
            continue
        w = t.val

        if w == 'BRIDGE' and i + 1 < n and toks[i + 1].kind == 'STR':
            file_ids.append(toks[i + 1].val)
        elif w == 'SPEC_VERSION':
            has_spec_version = True
        elif w in SIDE_KW and depth <= 1:
            # ── header side declaration ──
            if i + 1 < n and toks[i + 1].kind == 'STR':
                rec = {'edition': toks[i + 1].val, 'version': None,
                       'external': None, 'line': t.line}
                k = i + 2
                while k < n and toks[k].kind == 'ID' and toks[k].val in ('VERSION', 'EXTERNAL'):
                    kw = toks[k].val
                    if k + 1 < n and toks[k + 1].kind == 'STR':
                        rec['version' if kw == 'VERSION' else 'external'] = toks[k + 1].val
                        k += 2
                    else:
                        if kw == 'EXTERNAL':
                            findings.append(Finding(fname, 'lint', 'error', t.line,
                                                    "EXTERNAL requires a reason string"))
                        k += 1
                if w in sides:
                    findings.append(Finding(fname, 'lint', 'error', t.line,
                                            "duplicate %s declaration" % w))
                sides[w] = rec
                i = k
                continue
            findings.append(Finding(fname, 'lint', 'error', t.line,
                                    "%s must name an edition id (a string)" % w))
        elif w in SIDE_KW:
            # ── referent slot: SIDE ref | SIDE [ref, ref, ...] ──
            if unit is not None:
                unit['fields'].add(w if block_stack and block_stack[-1] in UNIT_KW else 'SIDED')
            k = i + 1
            if k < n and toks[k].kind == 'LBRACK':
                k += 1
                while k < n and toks[k].kind != 'RBRACK':
                    if toks[k].kind in ('CARET', 'STR'):
                        sided_refs.append((w, toks[k].kind == 'CARET', toks[k].val, toks[k].line))
                    k += 1
                i = k + 1
                continue
            if k < n and toks[k].kind in ('CARET', 'STR'):
                sided_refs.append((w, toks[k].kind == 'CARET', toks[k].val, toks[k].line))
                i = k + 1
                continue
            findings.append(Finding(fname, 'lint', 'error', t.line,
                                    "%s slot needs a referent (^\"Name\" or \"Name\")" % w))
        elif w == 'DISPOSITION':
            if unit is not None:
                unit['fields'].add('DISPOSITION')
            k = i + 1
            if k >= n or toks[k].kind != 'LBRACK':
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "DISPOSITION takes a list — a disposition is a SET, not one value"))
            else:
                k += 1
                while k < n and toks[k].kind != 'RBRACK':
                    if toks[k].kind == 'CARET':
                        local_refs.append(('disposition', toks[k].val, toks[k].line))
                    elif toks[k].kind == 'STR':
                        findings.append(Finding(fname, 'lint', 'error', toks[k].line,
                                                "disposition \"%s\" must be a caret reference into "
                                                "DISPOSITIONS, not a bare string" % toks[k].val))
                    k += 1
                i = k + 1
                continue
        elif w == 'TOPICS':
            if unit is not None:
                unit['fields'].add('TOPICS')
            k = i + 1
            if k < n and toks[k].kind == 'LBRACK':
                k += 1
                while k < n and toks[k].kind != 'RBRACK':
                    if toks[k].kind == 'STR':
                        topics.append((toks[k].val, toks[k].line))
                    k += 1
                i = k + 1
                continue
        elif w == 'CONCERNS':
            if unit is not None:
                unit['fields'].add('CONCERNS')
            k = i + 1
            if k < n and toks[k].kind == 'LBRACK':
                bare = 0
                k += 1
                while k < n and toks[k].kind != 'RBRACK':
                    if toks[k].kind in ('CARET', 'STR') and not (
                            toks[k - 1].kind == 'ID' and toks[k - 1].val in SIDE_KW):
                        bare += 1
                    k += 1
                if bare:
                    findings.append(Finding(fname, 'lint', 'error', t.line,
                                            "CONCERNS entries must be side-qualified "
                                            "(ORIGIN ^\"X\" / DESTINATION ^\"X\") — %d bare" % bare))
                i = k + 1
                continue
        elif w == 'CONVERT':
            if unit is not None:
                unit['converts'] += 1
            k = i + 1
            if not (k + 1 < n and toks[k].kind == 'ID' and toks[k].val in SIDE_KW):
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "CONVERT target must be side-qualified"))
            else:
                k += 2   # side keyword handled by the SIDE_KW branch on its own pass
            # find the operation on this line
            op = None
            k = i + 1
            while k < n and toks[k].line == t.line:
                if toks[k].kind == 'ID' and toks[k].val in CONVERT_OPS:
                    op = toks[k].val
                    break
                k += 1
            if op is None:
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "CONVERT needs an operation (%s)" % '/'.join(CONVERT_OPS)))
            elif op == 'SCALE':
                if not (k + 1 < n and toks[k + 1].kind == 'INT'):
                    findings.append(Finding(fname, 'lint', 'error', t.line,
                                            "SCALE needs an integer factor"))
            elif op == 'MANUAL':
                if not (k + 1 < n and toks[k + 1].kind == 'STR'):
                    findings.append(Finding(fname, 'lint', 'error', t.line,
                                            "MANUAL requires the source's verbatim instruction"))
        elif w == 'TEXT':
            if unit is not None:
                unit['fields'].add('TEXT')
            if not (i + 1 < n and toks[i + 1].kind == 'STR'):
                findings.append(Finding(fname, 'lint', 'error', t.line, "TEXT requires a string"))
        elif w in ('SCOPE', 'SUBJECT'):
            if unit is not None:
                unit['fields'].add(w)
            if not (i + 1 < n and toks[i + 1].kind == 'ID' and toks[i + 1].val in SIDE_KW):
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "%s must be side-qualified (ORIGIN/DESTINATION)" % w))
        elif w == 'FIAT':
            # §8 in a bridge: a reasoned, auditable "this referent is untyped on
            # purpose" — e.g. the 5.1 weapon property Light, whose only ^"Light"
            # in that edition is the spell. Waives the enclosing unit's coherence
            # findings; the reason is required.
            if not (i + 1 < n and toks[i + 1].kind == 'STR'):
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "FIAT requires a reason string"))
            if unit is not None:
                unit['waived'] = True
            else:
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "FIAT must sit inside a MAP / REMAINDER / PROCEDURE / ENTRY"))
        elif w == 'ASPECT':
            if unit is not None:
                unit['fields'].add('ASPECT')
        elif w == 'EXHAUSTIVE':
            if unit is not None:
                unit['fields'].add('EXHAUSTIVE')
        elif w == 'DEF':
            k = i - 1
            if k >= 0 and toks[k].kind in ('CARET', 'STR'):
                name = toks[k].val
                k -= 1
                hsh = toks[k].val if k >= 0 and toks[k].kind == 'HASH' else None
                defined_names.setdefault(name, []).append(t.line)
                if hsh:
                    anchors.setdefault(hsh, []).append(t.line)
            pending = 'DEF'
        elif w == 'ALIAS':
            # §21 ALIASES: a name the DOCUMENT uses that the edition it describes
            # does not. `ALIAS ^"Contract Patron" FOR DESTINATION ^"Level 9: Contact
            # Patron"` — the alias name then resolves on that side, so units keep the
            # document's own vocabulary; the FOR target is gated like any other ref.
            k = i + 1
            if not (k < len(toks) and toks[k].kind == 'CARET'):
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "ALIAS needs a ^\"name\""))
                i += 1
                continue
            alias_name = toks[k].val
            k += 1
            if not (k + 2 < len(toks) and toks[k].kind == 'ID' and toks[k].val == 'FOR'
                    and toks[k + 1].kind == 'ID' and toks[k + 1].val in SIDE_KW
                    and toks[k + 2].kind == 'CARET'):
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "ALIAS ^\"name\" FOR <ORIGIN|DESTINATION> ^\"target\" — "
                                        "the target must be side-qualified"))
                i += 1
                continue
            side = toks[k + 1].val
            aliases.setdefault(side, set()).add(alias_name)
            sided_refs.append((side, True, toks[k + 2].val, toks[k + 2].line))
            i = k + 3
            continue
        elif w == 'ENTRY':
            # a guidance ENTRY's caret is a LOCAL LABEL, not a reference
            if i + 1 < n and toks[i + 1].kind == 'CARET':
                defined_names.setdefault(toks[i + 1].val, []).append(t.line)
                if i + 2 < n and toks[i + 2].kind == 'HASH':
                    anchors.setdefault(toks[i + 2].val, []).append(t.line)
            else:
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "GUIDANCE ENTRY needs a ^\"label\""))
            pending = 'ENTRY'
        elif w in UNIT_KW or w in ('DISPOSITIONS', 'ALIASES', 'CONVERSION', 'GUIDANCE'):
            pending = w
        i += 1

    # ── structural lint on the units ──
    for u in units:
        f, ln = u['fields'], u['line']
        if u['kind'] == 'MAP':
            if not ({'ORIGIN', 'DESTINATION'} & f):
                findings.append(Finding(fname, 'lint', 'error', ln,
                                        "MAP needs at least one of ORIGIN / DESTINATION"))
            if 'DISPOSITION' not in f:
                findings.append(Finding(fname, 'lint', 'error', ln, "MAP needs a DISPOSITION"))
        elif u['kind'] == 'REMAINDER':
            if 'SCOPE' not in f:
                findings.append(Finding(fname, 'lint', 'error', ln,
                                        "REMAINDER needs a SCOPE — otherwise 'what is not listed' is undefined"))
            if 'DISPOSITION' not in f:
                findings.append(Finding(fname, 'lint', 'error', ln, "REMAINDER needs a DISPOSITION"))
        elif u['kind'] == 'PROCEDURE':
            if 'SUBJECT' not in f:
                findings.append(Finding(fname, 'lint', 'error', ln, "PROCEDURE needs a SUBJECT"))
            if not u['converts']:
                findings.append(Finding(fname, 'lint', 'error', ln,
                                        "PROCEDURE needs at least one CONVERT"))
        elif u['kind'] == 'ENTRY':
            if 'TEXT' not in f:
                findings.append(Finding(fname, 'lint', 'error', ln, "GUIDANCE ENTRY needs TEXT"))

    for w in SIDE_KW:
        if w not in sides:
            findings.append(Finding(fname, 'lint', 'error', 1,
                                    "BRIDGE must declare %s — a bridge is directed and is not "
                                    "reversible by inspection (§21)" % w))
    if not has_spec_version:
        findings.append(Finding(fname, 'lint', 'warning', 1, "no SPEC_VERSION declared"))
    for tk in toks:
        if tk.kind == 'HASH' and len(tk.val) - 1 < HASH_MIN_BODY:
            findings.append(Finding(fname, 'lint', 'warning', tk.line,
                                    "hash id '%s' shorter than %d chars" % (tk.val, HASH_MIN_BODY)))

    return {
        'file': fname, 'kind': 'bridge', 'names': defined_names, 'anchors': anchors,
        'refs': [], 'depends': [], 'file_ids': file_ids,
        'waived_ranges': waived_ranges, 'waived_lines': set(),
        'sides': sides, 'sided_refs': sided_refs, 'local_refs': local_refs, 'topics': topics,
        'aliases': aliases,
    }


def bridge_coherence(files_data, corpora, findings, notes):
    """Two-corpus coherence (§20). ORIGIN refs resolve in the ORIGIN edition's corpus,
    DESTINATION refs in the DESTINATION edition's. Never against each other, never
    against the union."""
    for d in files_data:
        if d.get('kind') != 'bridge':
            continue
        own = set(d['names'])
        for kind, name, line in d['local_refs']:
            if name not in own and not is_waived(line, d):
                findings.append(Finding(d['file'], 'coherence', 'error', line,
                                        "%s references ^\"%s\", which this bridge never declares "
                                        "in DISPOSITIONS" % (kind, name)))
        unverified = {}
        for side, rec in d['sides'].items():
            ed = rec['edition']
            if rec['external']:
                continue
            if ed not in corpora:
                findings.append(Finding(d['file'], 'coherence', 'error', rec['line'],
                                        "%s edition \"%s\" has no corpus: pass --corpus %s=<dir>, or "
                                        "declare the side EXTERNAL with a reason (§21)" % (side, ed, ed)))
        for side, typed, name, line in d['sided_refs']:
            rec = d['sides'].get(side)
            if rec is None or is_waived(line, d):
                continue
            if rec['external']:
                unverified[side] = unverified.get(side, 0) + 1
                continue
            names = corpora.get(rec['edition'])
            if names is None:
                continue
            # a name this document uses that the edition does not (§21 ALIASES)
            # resolves on the side it was declared for
            names = names | d.get('aliases', {}).get(side, set())
            if typed:
                if name not in names:
                    findings.append(Finding(d['file'], 'coherence', 'error', line,
                                            "%s reference ^\"%s\" is not defined in edition \"%s\""
                                            % (side.lower(), name, rec['edition'])))
            else:
                if name in names:
                    findings.append(Finding(d['file'], 'coherence', 'warning', line,
                                            "%s referent \"%s\" is untyped but DOES resolve in edition "
                                            "\"%s\" — use ^\"%s\" so it is gated"
                                            % (side.lower(), name, rec['edition'], name)))
        for side, rec in d['sides'].items():
            if rec['external']:
                notes.append("%s: %s side \"%s\" is EXTERNAL — %d reference(s) unverifiable. %s"
                             % (os.path.basename(d['file']), side, rec['edition'],
                                unverified.get(side, 0), rec['external']))


def load_corpus_names(path, index=None):
    """Every ^"Name" / ACTOR / TEMPLATE / ALIAS name defined in an edition corpus.
    `index`, when given, is filled with  container id -> {'kinds', 'anchors', 'file'}:
    the kinds declared under that id and hash -> {names} for the file that declares it
    (what a port is checked against, §19)."""
    names = set()
    scratch = []
    for root, _dirs, files in os.walk(path):
        for nm in sorted(files):
            if not nm.endswith(('.ttrpg', '.actor', '.setting', '.arc', '.frame', '.campaign', '.codex')):
                continue
            p = os.path.join(root, nm)
            try:
                with open(p, encoding='utf-8') as fh:
                    data = analyze_file(p, fh.read(), scratch)
            except OSError:
                continue
            names.update(data['names'])
            if index is not None:
                anchors = {}
                for src in (data.get('anchor_names', {}), data.get('block_anchors', {}),
                            data.get('entity_anchors', {})):
                    for h, nms in src.items():
                        anchors.setdefault(h, set()).update(nms)
                for cid, kind in data.get('containers', {}).items():
                    rec = index.setdefault(cid, {'kinds': set(), 'anchors': {}, 'file': p})
                    rec['kinds'].add(kind)
                    for h, nms in anchors.items():
                        rec['anchors'].setdefault(h, set()).update(nms)
    return names


# ═══════════════════════════════════════════════════════════════════════════
# Property declarations (§8) — the table the §13 modification checks read
# ═══════════════════════════════════════════════════════════════════════════

def _bracket_strings(toks, k):
    """toks[k] is '['. Return (list of STR values at bracket depth 1, index past ']')."""
    vals, depth = [], 0
    while k < len(toks):
        if toks[k].kind == 'LBRACK':
            depth += 1
        elif toks[k].kind == 'RBRACK':
            depth -= 1
            if depth == 0:
                return vals, k + 1
        elif toks[k].kind == 'STR' and depth == 1:
            vals.append(toks[k].val)
        k += 1
    return vals, k


def parse_prop_decl(toks, k):
    """toks[k] is the CARET naming a property. Returns (record, next index), or
    (None, k+1) when this caret does not open a property declaration.

    The record captures what the §13 checks need: the declared type, an ENUM's
    permitted values, whether it is a list (and its literal members, if any), and
    an inline value — an *instance* restates a parent's ENUM field as a concrete
    `^"Size" STRING "Minor"`, which is what an enum-narrowing check must look at."""
    name = toks[k].val
    j = k + 1
    if j >= len(toks) or toks[j].kind != 'ID' or toks[j].val not in PROP_TYPE_KW:
        return None, k + 1
    ty = toks[j].val
    rec = {'name': name, 'type': ty, 'enum': None, 'is_list': False,
           'members': None, 'value': None, 'line': toks[k].line}
    j += 1
    if ty == 'ENUM':
        if j < len(toks) and toks[j].kind == 'LBRACK':
            rec['enum'], j = _bracket_strings(toks, j)
        elif j < len(toks) and toks[j].kind == 'STR':
            rec['value'] = toks[j].val
            j += 1
    elif ty == 'LIST':
        rec['is_list'] = True
        if j < len(toks) and toks[j].kind == 'ID' and toks[j].val == 'OF':
            j += 1
            if j < len(toks) and toks[j].kind in ('CARET', 'ID'):
                j += 1          # LIST OF ^"Type" | LIST OF STRING
        if j < len(toks) and toks[j].kind == 'LBRACK':
            rec['members'], j = _bracket_strings(toks, j)
    elif ty in ('STRING', 'TEXT'):
        if j < len(toks) and toks[j].kind == 'STR':
            rec['value'] = toks[j].val
            j += 1
    elif ty == 'INTEGER':
        if j < len(toks) and toks[j].kind == 'INT':
            rec['value'] = toks[j].val
            j += 1
    elif ty == 'BOOLEAN':
        if j < len(toks) and toks[j].kind == 'BOOL':
            rec['value'] = toks[j].val
            j += 1
    elif ty == 'REF':
        rty, _th, _tl, rval, _vh, _vl, j = parse_ref(toks, j)
        rec['ref_of'], rec['value'] = rty, rval
    elif ty == 'ROLL':
        # ROLL n OF [#h] ^"Die"  (§8, DECISION-18). An older `ROLL "1d10"` is a system keyword
        # use, not a roll; leave it to the main loop.
        if j < len(toks) and toks[j].kind == 'INT':
            j += 1
            if j < len(toks) and toks[j].kind == 'ID' and toks[j].val == 'OF':
                j += 1
                if j < len(toks) and toks[j].kind == 'HASH':
                    j += 1
                if j < len(toks) and toks[j].kind == 'CARET':
                    rec['value'] = toks[j].val
                    j += 1
    return rec, j


def parse_properties_block(toks, k):
    """toks[k] is 'PROPERTIES' and toks[k+1] is '{'. Return the declarations at the
    block's own level; a nested `^"Rings" DEF { ... }` is one property here, and its
    interior fields belong to *it*, not to the enclosing DEF."""
    out = {}
    if k + 1 >= len(toks) or toks[k + 1].kind != 'LBRACE':
        return out
    depth, j = 0, k + 1
    while j < len(toks):
        t = toks[j]
        if t.kind == 'LBRACE':
            depth += 1
        elif t.kind == 'RBRACE':
            depth -= 1
            if depth == 0:
                break
        elif t.kind == 'CARET' and depth == 1:
            rec, j = parse_prop_decl(toks, j)
            if rec is not None:
                out[rec['name']] = rec
            continue
        elif t.kind == 'ID' and t.val == 'REF' and depth == 1 \
                and j + 1 < len(toks) and toks[j + 1].kind == 'ID' and toks[j + 1].val == 'OF':
            # REF OF ^"Type"  (§8): no name of its own, so the property takes the type's name.
            # A named REF never reaches here: parse_prop_decl consumed it with its name.
            rty, _th, _tl, rval, _vh, _vl, j2 = parse_ref(toks, j + 1)
            if rty is not None:
                out[rty] = {'name': rty, 'type': 'REF', 'enum': None, 'is_list': False,
                            'members': None, 'value': rval, 'ref_of': rty, 'line': t.line}
            j = j2
            continue
        j += 1
    return out


def scan_modify_body(toks, lb):
    """toks[lb] is a MODIFY block's '{'. Collect the SET / ADD_TO / REMOVE_FROM
    operations at the block's own level. A `PROPERTIES { }` inside the block is not an
    operation — it declares new properties on the target and is picked up by the normal
    §8 handling, which is exactly the split §13 draws between changing and introducing."""
    ops, depth, j = [], 0, lb
    while j < len(toks):
        t = toks[j]
        if t.kind == 'LBRACE':
            depth += 1
        elif t.kind == 'RBRACE':
            depth -= 1
            if depth == 0:
                break
        elif depth == 1 and t.kind == 'ID' and t.val == 'SET' \
                and j + 1 < len(toks) and toks[j + 1].kind == 'ID' \
                and toks[j + 1].val == 'DESCRIPTION':
            # v0.5 addendum (DECISION-14): a variant printing replaces the whole text.
            ok = j + 2 < len(toks) and toks[j + 2].kind == 'STR'
            ops.append({'op': 'SET DESCRIPTION', 'ok': ok, 'line': t.line})
            j += 3 if ok else 2
            continue
        elif depth == 1 and t.kind == 'ID' and t.val in ('SET', 'ADD_TO', 'REMOVE_FROM') \
                and j + 1 < len(toks) and toks[j + 1].kind == 'CARET':
            prop = toks[j + 1].val
            if t.val == 'SET':
                # `SET ^"P" ENUM [...]` parses as a declaration; `SET ^"P" DEFAULT 45`
                # does not, and simply carries no type information.
                rec, j = parse_prop_decl(toks, j + 1)
                ops.append({'op': 'SET', 'prop': prop, 'rec': rec, 'line': t.line})
                continue
            val = None
            if j + 2 < len(toks) and toks[j + 2].kind in ('STR', 'INT', 'BOOL'):
                val = toks[j + 2].val
            ops.append({'op': t.val, 'prop': prop, 'value': val, 'line': t.line})
        j += 1
    return ops

# ═══════════════════════════════════════════════════════════════════════════
# Values against declarations (§5, §5b, §6, §8, DECISION-32)
# ═══════════════════════════════════════════════════════════════════════════

VALUE_TYPES = ('STRING', 'INTEGER', 'BOOLEAN', 'ENUM', 'LIST', 'REF', 'ROLL', 'TEXT')
VALUE_FAMILY = {'STRING': 'text', 'TEXT': 'text', 'ENUM': 'text', 'INTEGER': 'number', 'BOOLEAN': 'boolean'}
TOKEN_FAMILY = {'STR': 'text', 'INT': 'number', 'BOOL': 'boolean'}


def collect_definitions(fname, toks):
    """One pass over a file's tokens, for the checks in value_pass.

    -> (defs, bound). A def records its name, hash, what it EXTENDS, its PARAMETERS and every
    property line at its own level or in its PROPERTIES block: the type keyword, an inline
    value, MIN / MAX, an ENUM's values, and a LIST OF type with its named members. A DEF
    inside another DEF's body is recorded as nested and is not checked. `bound` is every
    bound reference ^"Base"(args): the base, the number of arguments, the string arguments
    by position and by name."""
    n = len(toks)
    defs, bound, stack, pending = [], [], [], None

    def same_line(j, line):
        return j < n and toks[j].line == line

    for i, t in enumerate(toks):
        if t.kind == 'ID':
            w = t.val
            if w == 'DEF' and i >= 1 and toks[i - 1].kind in ('CARET', 'STR'):
                k, marker = i - 2, None
                if k >= 0 and toks[k].kind == 'ID' and toks[k].val in ('ACTOR', 'TEMPLATE'):
                    marker, k = toks[k].val, k - 1
                pending = {'name': name_key(toks[i - 1].val),
                           'hash': toks[k].val if k >= 0 and toks[k].kind == 'HASH' else None,
                           'marker': marker, 'children': set(),
                           'extends': [], 'props': {}, 'params': None, 'file': fname, 'line': t.line,
                           'nested': any(fr['kind'] in ('DEF', 'PROPS') for fr in stack)}
                # a DEF written inside another is that one's field of the same name
                for fr in reversed(stack):
                    if fr['kind'] in ('DEF', 'PROPS'):
                        if fr['def'] is not None:
                            fr['def']['children'].add(pending['name'])
                        break
            elif w == 'EXTENDS' and stack and stack[-1]['kind'] == 'DEF':
                j, hsh = i + 1, None
                if j < n and toks[j].kind == 'HASH':
                    hsh, j = toks[j].val, j + 1
                if j < n and toks[j].kind == 'CARET':
                    stack[-1]['def']['extends'].append((toks[j].val, hsh, t.line))
            elif w == 'PARAMETERS' and stack and stack[-1]['kind'] == 'DEF' \
                    and i + 1 < n and toks[i + 1].kind == 'LBRACE':
                params, j, depth = [], i + 2, 1
                while j < n and depth:
                    if toks[j].kind == 'LBRACE':
                        depth += 1
                    elif toks[j].kind == 'RBRACE':
                        depth -= 1
                    elif toks[j].kind == 'CARET' and j + 1 < n and toks[j + 1].kind == 'ID' \
                            and toks[j + 1].val == 'OF':
                        values = None
                        if j + 2 < n and toks[j + 2].kind == 'LBRACK':
                            values, q = [], j + 3
                            while q < n and toks[q].kind != 'RBRACK':
                                if toks[q].kind == 'STR':
                                    values.append(toks[q].val)
                                q += 1
                        params.append({'name': toks[j].val, 'values': values})
                    j += 1
                stack[-1]['def']['params'] = params
        if t.kind == 'CARET':
            # a bound reference: ^"Base"( "x", ^"slot" = "y" )
            if i + 1 < n and toks[i + 1].kind == 'LPAREN':
                q, depth, nargs, pos, named, slot, seen = i + 2, 1, 0, [], {}, None, False
                while q < n and depth:
                    tk = toks[q]
                    if tk.kind == 'LPAREN':
                        depth += 1
                    elif tk.kind == 'RPAREN':
                        depth -= 1
                    elif depth == 1:
                        if tk.kind == 'COMMA':
                            nargs, seen, slot = nargs + 1, False, None
                        elif tk.kind == 'CARET' and q + 1 < n and toks[q + 1].kind == 'EQ':
                            slot = tk.val
                        elif tk.kind in ('STR', 'CARET'):
                            seen = True
                            if tk.kind == 'STR':
                                if slot is not None:
                                    named[slot] = tk.val
                                else:
                                    pos.append((nargs, tk.val))
                    q += 1
                bound.append({'base': t.val, 'nargs': nargs + 1 if (seen or nargs) else 0,
                              'pos': pos, 'named': named, 'line': t.line})
            # a property line: ^"Name" TYPE [value] [modifiers]
            if stack and stack[-1]['kind'] in ('DEF', 'PROPS') and stack[-1]['def'] is not None \
                    and i + 1 < n and toks[i + 1].kind == 'ID' and toks[i + 1].val in VALUE_TYPES \
                    and not (i >= 1 and toks[i - 1].kind == 'ID'
                             and toks[i - 1].val in ('AXIS', 'OF', 'SET', 'NEXT', 'COLUMNS')):
                ty, j = toks[i + 1].val, i + 2
                rec = {'type': ty, 'value': None, 'vkind': None, 'min': None, 'max': None,
                       'enum': None, 'of': None, 'of_hash': None, 'members': None, 'line': t.line,
                       'required': False}
                if ty == 'LIST' and j < n and toks[j].kind == 'ID' and toks[j].val == 'OF':
                    j += 1
                    if j < n and toks[j].kind == 'HASH':
                        rec['of_hash'], j = toks[j].val, j + 1
                    if j < n and toks[j].kind == 'CARET':
                        rec['of'], j = toks[j].val, j + 1
                    elif j < n and toks[j].kind == 'ID':
                        j += 1                                   # LIST OF STRING
                if same_line(j, t.line) and toks[j].kind == 'LBRACK':
                    items, q, depth, braces = [], j + 1, 1, 0
                    while q < n and depth:
                        tk = toks[q]
                        if tk.kind == 'LBRACK':
                            depth += 1
                        elif tk.kind == 'RBRACK':
                            depth -= 1
                        elif tk.kind == 'LBRACE':
                            braces += 1
                        elif tk.kind == 'RBRACE':
                            braces -= 1
                        elif depth == 1 and braces == 0:
                            if tk.kind == 'STR':
                                items.append(('STR', tk.val, None, tk.line))
                            elif tk.kind == 'CARET':
                                hsh = toks[q - 1].val if toks[q - 1].kind == 'HASH' else None
                                items.append(('CARET', tk.val, hsh, tk.line))
                        q += 1
                    if ty == 'ENUM':
                        rec['enum'] = [v for kind, v, _h, _l in items if kind == 'STR']
                    else:
                        rec['members'] = [(v, h, ln) for kind, v, h, ln in items if kind == 'CARET']
                    j = q
                elif same_line(j, t.line) and toks[j].kind in ('STR', 'INT', 'BOOL'):
                    rec['value'], rec['vkind'] = toks[j].val, toks[j].kind
                    j += 1
                while same_line(j, t.line) and toks[j].kind == 'ID' \
                        and toks[j].val in ('REQUIRED', 'FIXED', 'DEFAULT', 'MIN', 'MAX', 'FIAT'):
                    m = toks[j].val
                    if m in ('MIN', 'MAX') and j + 1 < n and toks[j + 1].kind == 'INT':
                        rec[m.lower()] = int(toks[j + 1].val)
                    elif m == 'REQUIRED':
                        rec['required'] = True
                    j += 1 if m in ('REQUIRED', 'FIXED') else 2
                stack[-1]['def']['props'].setdefault(t.val, []).append(rec)
        if t.kind == 'LBRACE':
            prev = toks[i - 1] if i else None
            if pending is not None and prev is not None and prev.kind == 'ID' and prev.val == 'DEF':
                stack.append({'kind': 'DEF', 'def': pending})
                defs.append(pending)
                pending = None
            elif prev is not None and prev.kind == 'ID' and prev.val == 'PROPERTIES':
                owner = stack[-1]['def'] if stack and stack[-1]['kind'] == 'DEF' else None
                stack.append({'kind': 'PROPS', 'def': owner})
            else:
                stack.append({'kind': 'OTHER', 'def': None})
        elif t.kind == 'RBRACE' and stack:
            stack.pop()
    return defs, bound


def check_actor_file(fname, toks, spec_version, findings):
    """An .actor file (§2, DECISION-28): the EXTENSION wrapper, and instances only.
    Returns True when the file opens with a bare DEF (the form older than 0.6)."""
    if not toks:
        return False
    sev = 'error' if spec_version >= (0, 6) else 'warning'
    first = toks[0]
    wrapped = first.kind == 'ID' and first.val in CONTAINER_KINDS
    if not wrapped:
        findings.append(Finding(fname, 'lint', 'warning', first.line,
                                'an .actor file opens with EXTENSION "id" { ... }, as a .ttrpg does; '
                                'this one opens with a bare DEF, so it declares no SPEC_VERSION and '
                                'names no parent (§2)'))
    elif first.val != 'EXTENSION':
        findings.append(Finding(fname, 'lint', sev, first.line,
                                'an .actor file opens with EXTENSION; this one opens with %s (§2)'
                                % first.val))
    base, depth = (1 if wrapped else 0), 0
    for i, t in enumerate(toks):
        if t.kind == 'LBRACE':
            depth += 1
        elif t.kind == 'RBRACE':
            depth -= 1
        elif t.kind == 'ID' and depth == base:
            if t.val in ('MODIFY', 'OVERRIDE', 'REPRINT', 'ALIAS', 'ADD'):
                findings.append(Finding(fname, 'lint', sev, t.line,
                                        'an .actor file holds instances only; %s belongs in a '
                                        '.ttrpg (§2)' % t.val))
            elif t.val == 'DEF' and i > 0 and toks[i - 1].kind in ('CARET', 'STR'):
                name, k = toks[i - 1].val, i - 2
                decl = toks[k].val if k >= 0 and toks[k].kind == 'ID' \
                    and toks[k].val in ('ACTOR', 'TEMPLATE') else None
                if decl:
                    k -= 1
                if k >= 0 and toks[k].kind == 'HASH':
                    k -= 1
                if k >= 0 and toks[k].kind == 'ID' and toks[k].val == 'ADD' and toks[k].line == t.line:
                    continue                      # reported once, as the ADD
                if decl:
                    findings.append(Finding(fname, 'lint', sev, t.line,
                                            'an .actor file holds instances only; %s "%s" defines a '
                                            'type and belongs in a .ttrpg (§2)' % (decl, name)))
                    continue
                extends, d, j = False, 0, i + 1
                while j < len(toks):
                    if toks[j].kind == 'LBRACE':
                        d += 1
                    elif toks[j].kind == 'RBRACE':
                        d -= 1
                        if d <= 0:
                            break
                    elif d == 1 and toks[j].kind == 'ID' and toks[j].val == 'EXTENDS':
                        extends = True
                        break
                    j += 1
                if not extends:
                    findings.append(Finding(fname, 'lint', sev, t.line,
                                            'an .actor file holds instances only; ^"%s" extends '
                                            'nothing, so it is a type and belongs in a .ttrpg (§2)'
                                            % name))
    return not wrapped


def analyze_file(fname, text, findings):
    if fname.endswith('.bridge'):
        return analyze_bridge(fname, text, findings)
    if fname.endswith('.codex'):
        return analyze_codex(fname, text, findings)
    toks = tokenize(text, fname, findings)
    defined_names, anchors = {}, {}     # name/hash -> [lines]
    refs, depends, file_ids = [], [], []
    has_spec_version = False
    frames = []                          # {open, is_def, waived, def_name}
    waived_ranges, waived_lines = [], set()
    next_lbrace_is_def = False
    next_lbrace_def_name = None
    def_props = {}                       # name -> {prop -> record}   (§8 declarations)
    def_extends = {}                     # name -> [parent names]
    mods = []                            # §13 MODIFY blocks and their operations
    adds = []                            # §13 ADD ^"X" DEF sites: (name, line)
    reprints = []                        # REPRINT ^"X" sites: (name, line)  (DECISION-14)
    aliases = []                         # ALIAS ^"A" FOR ^"B" sites: (alias, target, line)  (§5b)
    chooses = []                         # CHOOSE n OF ^"T" WITH { } sites  (§5b, DECISION-15)
    ref_values = []                      # ^"P" REF ^"Entity" sites: (owner, prop, entity, line)  (§8)
    rolls = []                           # ROLL n OF ^"Die" sites: (die, line)  (§8, DECISION-18)
    step_names = set()                   # (enclosing DEF, name) of each property a roll sits under:
                                         # a later step names the result by it, so it is not a ref
    next_lbrace_is_modify = False
    tables = []                          # TABLE { AXIS … AT … } blocks  (§5e, DECISION-21)
    block_names = {}                     # names of named blocks in this file: local labels  (§20)
    block_anchors = {}                   # hash -> {name} for each hashed named block  (§20)
    block_anchor_lines = {}              # hash -> [(name, line)]
    anchor_names = {}                    # DEF hash -> {name}: to tell a restatement from a clash
    hash_refs = []                       # a reference written as a bare hash: (kind, hash, line)
    block_types = []                     # TYPE of a SCENE / CONFLICT: (block kw, entity, line)  (§16)
    containers = {}                      # container id -> kind (BASE, EXTENSION, SETTING, …)  (§16)
    origins = []                         # (edition, kind, container id, line): a port's source (§19)
    froms = []                           # FROM [KIND] "id" imports: (kind or None, id, line)  (§16)

    # Embedded references (§5c, DECISION-20): every ^\"Name\" inside a string is a reference
    # site and resolves like any other. Before v0.6 no tool read inside a string.
    for _tk in toks:
        if _tk.kind != 'STR' or '^' not in _tk.val:
            continue
        for _m in EMBEDDED_REF.finditer(_tk.val):
            refs.append(('embedded reference', name_key(_m.group(3)), _m.group(1), _tk.line))
            if _m.group(4) is not None and not _m.group(4).strip():
                findings.append(Finding(fname, 'lint', 'error', _tk.line,
                                        'embedded reference ^"%s" has an empty literal after the '
                                        'slash (§5c)' % _m.group(3)))

    def change_target(idx):
        """toks[idx] is SET or TRANSFORM. Return 'choose' when what precedes it on the line is a
        CHOOSE, the (name, hash, line) of a reference target, 'bound' for a bound reference, or
        None when nothing on the line can be a target."""
        p = idx - 1
        if p < 0 or toks[p].line != toks[idx].line:
            return None
        if toks[p].kind == 'RPAREN':
            return 'bound'
        if toks[p].kind == 'RBRACK':
            depth, k = 0, p
            while k >= 0:
                if toks[k].kind == 'RBRACK':
                    depth += 1
                elif toks[k].kind == 'LBRACK':
                    depth -= 1
                    if depth == 0:
                        break
                k -= 1
            k -= 1
            if k >= 0 and toks[k].kind == 'INT':
                k -= 1
                if k >= 0 and toks[k].kind == 'ID' and toks[k].val in ('DISTINCT', 'INDISTINCT'):
                    k -= 1
                if k >= 0 and toks[k].kind == 'ID' and toks[k].val == 'CHOOSE':
                    return 'choose'
            return None
        if toks[p].kind == 'RBRACE':        # CHOOSE n OF ^"Type" WITH { … }
            k = p
            while k >= 0 and toks[k].kind != 'LBRACE':
                k -= 1
            if k >= 1 and toks[k - 1].kind == 'ID' and toks[k - 1].val == 'WITH':
                return 'choose'
            return None
        if toks[p].kind == 'CARET':
            h = toks[p - 1].val if p >= 1 and toks[p - 1].kind == 'HASH' else None
            k = p - (2 if h else 1)
            if k >= 0 and toks[k].kind == 'ID' and toks[k].val == 'OF':
                return 'choose'             # CHOOSE n OF ^"Type"
            return (toks[p].val, h, toks[p].line)
        return None

    def change_amount(k, line):
        """An amount at toks[k]: an integer, or a reference to another value. Returns the next
        index, or None when there is no amount."""
        if k < len(toks) and toks[k].kind == 'INT':
            return k + 1
        h = None
        if k < len(toks) and toks[k].kind == 'HASH':
            h = toks[k].val
            k += 1
        if k < len(toks) and toks[k].kind == 'CARET':
            nxt = toks[k + 1] if k + 1 < len(toks) else None
            if nxt is not None and nxt.kind == 'ID' and nxt.val in NEXT_STATEMENT_KW:
                return None       # that reference opens the next statement; no amount here
            if h is None and (cur_def(), toks[k].val) in step_names:
                return k + 1      # the result of an earlier step, named by its property (§8)
            refs.append(('change amount', toks[k].val, h, toks[k].line))
            return k + 1
        return None
    # The SPEC_VERSION the file declares, as (major, minor); (0, 0) when it declares none.
    spec_version = (0, 0)
    for _i, _t in enumerate(toks[:-1]):
        if _t.kind == 'ID' and _t.val == 'SPEC_VERSION' and toks[_i + 1].kind == 'STR':
            _m = re.match(r'\s*(\d+)\.(\d+)', toks[_i + 1].val)
            if _m:
                spec_version = (int(_m.group(1)), int(_m.group(2)))
            break

    def cur_def():
        for fr in reversed(frames):
            if fr['def_name']:
                return fr['def_name']
        return None

    def caret_earlier_on_line(idx):
        ln = toks[idx].line
        k = idx - 1
        while k >= 0 and toks[k].line == ln:
            if toks[k].kind == 'CARET':
                return True
            k -= 1
        return False

    for idx, t in enumerate(toks):
        if t.kind == 'LBRACE':
            # the keyword that opened this block: SCENE ^"Name" #hash {  ->  SCENE
            _k = idx - 1
            while _k >= 0 and toks[_k].kind in ('CARET', 'HASH', 'STR', 'INT'):
                _k -= 1
            _kw = toks[_k].val if _k >= 0 and toks[_k].kind == 'ID' else None
            # A named block (§20, DECISION-24): SCENE ^"Name" #hash {  or  SCENE #hash ^"Name" {.
            # Its hash is an anchor, referenceable from anywhere; its name is a label local to
            # this file. Keywords that name an entity which already exists declare nothing.
            if _kw and _kw not in NOT_A_BLOCK and toks[_k].line == t.line:
                _carets = [x for x in toks[_k + 1:idx] if x.kind == 'CARET']
                _hashes = [x for x in toks[_k + 1:idx] if x.kind == 'HASH']
                if len(_carets) == 1 and len(_hashes) <= 1 \
                        and all(x.kind in ('CARET', 'HASH') for x in toks[_k + 1:idx]):
                    block_names.setdefault(_carets[0].val, []).append(t.line)
                    if _hashes:
                        block_anchors.setdefault(_hashes[0].val, set()).add(_carets[0].val)
                        block_anchor_lines.setdefault(_hashes[0].val, []).append((_carets[0].val, t.line))
            frames.append({'open': t.line, 'is_def': next_lbrace_is_def, 'waived': False,
                           'def_name': next_lbrace_def_name, 'is_modify': next_lbrace_is_modify,
                           'kw': _kw})
            next_lbrace_is_modify = False
            next_lbrace_is_def = False
            next_lbrace_def_name = None
            continue
        if t.kind == 'RBRACE':
            if not frames:
                findings.append(Finding(fname, 'lint', 'error', t.line, "unmatched '}'"))
            else:
                fr = frames.pop()
                if fr['waived']:
                    waived_ranges.append((fr['open'], t.line))
            continue
        if t.kind == 'CARET':
            # bound reference (DECISION-6): ^"Base"(args). The base must resolve
            # and declare PARAMETERS; caret arguments must resolve too. A caret
            # immediately followed by '=' inside the parens is a parameter NAME
            # (local), not a ref.
            if idx + 1 < len(toks) and toks[idx + 1].kind == 'LPAREN':
                refs.append(('bound ref', t.val, None, t.line))
                depth, k = 0, idx + 1
                while k < len(toks):
                    tk = toks[k]
                    if tk.kind == 'LPAREN':
                        depth += 1
                    elif tk.kind == 'RPAREN':
                        depth -= 1
                        if depth == 0:
                            break
                    elif tk.kind == 'CARET' and depth == 1 \
                            and not (k + 1 < len(toks) and toks[k + 1].kind == 'EQ') \
                            and not (k + 1 < len(toks) and toks[k + 1].kind == 'LPAREN'):
                        refs.append(('bound argument', tk.val, None, tk.line))
                    k += 1
            continue
        if t.kind != 'ID':
            continue
        w = t.val
        if w in ('BASE', 'EXTENSION'):
            if idx + 1 < len(toks) and toks[idx + 1].kind == 'STR':
                file_ids.append(toks[idx + 1].val)
        # A container's id and kind (§16). Only where the keyword opens the container: the id is
        # followed by its brace, or by EXTENDS "base" and the brace. `FROM ARC "id"` and a
        # `SETTING "free text"` line inside an arc are not declarations.
        if w in CONTAINER_KINDS and idx + 2 < len(toks) and toks[idx + 1].kind == 'STR' \
                and not (idx > 0 and toks[idx - 1].kind == 'ID' and toks[idx - 1].val == 'FROM'):
            k = idx + 2
            if toks[k].kind == 'ID' and toks[k].val == 'EXTENDS' and k + 2 < len(toks) \
                    and toks[k + 1].kind == 'STR':
                k += 2
            if toks[k].kind == 'LBRACE':
                containers[toks[idx + 1].val] = w
        if w == 'TYPE' and frames and frames[-1].get('kw') in ('SCENE', 'CONFLICT'):
            # A scene's type and a conflict's type are entities the system defines (§16,
            # DECISION-23): TYPE [#hash] ^"Name", or a CHOOSE where the source leaves it open.
            # A string here is the older form: a warning below 0.6, an error from 0.6.
            k = idx + 1
            bh = None
            if k < len(toks) and toks[k].kind == 'HASH':
                bh = toks[k].val
                k += 1
            if k < len(toks) and toks[k].kind == 'CARET':
                refs.append(('%s type' % frames[-1]['kw'].lower(), toks[k].val, bh, toks[k].line))
                block_types.append((frames[-1]['kw'], toks[k].val, toks[k].line))
            elif k < len(toks) and toks[k].kind == 'STR':
                findings.append(Finding(fname, 'lint', 'error' if spec_version >= (0, 6) else 'warning',
                                        t.line, 'the TYPE of a %s is a reference to an entity the system '
                                        'defines (TYPE #hash ^"%s"), not a string (§16)'
                                        % (frames[-1]['kw'], toks[k].val)))
        # References between narrative blocks (§16; reference sites under §5d, DECISION-24).
        if w in BLOCK_REF_ONE or (w == 'LOCATION' and frames and frames[-1].get('kw') == 'SCENE'):
            what = BLOCK_REF_ONE.get(w, 'scene location')
            k = idx + 1
            rh = None
            if k < len(toks) and toks[k].kind == 'HASH' and toks[k].line == t.line:
                rh = toks[k].val
                k += 1
            if k < len(toks) and toks[k].kind == 'CARET' and toks[k].line == t.line \
                    and not (k + 1 < len(toks) and toks[k + 1].kind in ('LBRACE', 'HASH')):
                refs.append((what, toks[k].val, rh, t.line))
            elif rh and not (k < len(toks) and toks[k].kind in ('CARET', 'LBRACE')):
                hash_refs.append((what, rh, t.line))
        elif w in BLOCK_REF_LIST and idx + 1 < len(toks) and toks[idx + 1].kind == 'LBRACK':
            k = idx + 2
            while k < len(toks) and toks[k].kind != 'RBRACK':
                if toks[k].kind == 'CARET':
                    rh = toks[k - 1].val if toks[k - 1].kind == 'HASH' else None
                    refs.append((BLOCK_REF_LIST[w], toks[k].val, rh, toks[k].line))
                elif toks[k].kind == 'HASH' and not (k + 1 < len(toks) and toks[k + 1].kind == 'CARET'):
                    hash_refs.append((BLOCK_REF_LIST[w], toks[k].val, toks[k].line))
                k += 1
        if w == 'FROM':
            # FROM <KIND> "id" [INCLUDE [ #hash ^"Name", … ]]  (§16, DECISION-22). The line is
            # itself the declaration of the dependency. The kind is always named; a bare
            # FROM "id" is the older spelling: a warning below 0.6, an error from 0.6.
            k = idx + 1
            kind = None
            if k < len(toks) and toks[k].kind == 'ID' and toks[k].val in CONTAINER_KINDS:
                kind = toks[k].val
                k += 1
            if k < len(toks) and toks[k].kind == 'STR' and toks[k].line == t.line:
                cid = toks[k].val
                froms.append((kind, cid, t.line))
                if kind is None:
                    findings.append(Finding(fname, 'lint', 'error' if spec_version >= (0, 6) else 'warning',
                                            t.line, 'FROM "%s" does not name the kind of container: write '
                                            'FROM EXTENSION, FROM FRAME, FROM ARC or FROM SETTING (§16)' % cid))
                k += 1
                if k + 1 < len(toks) and toks[k].kind == 'ID' and toks[k].val == 'INCLUDE' \
                        and toks[k + 1].kind == 'LBRACK':
                    k += 2
                    while k < len(toks) and toks[k].kind != 'RBRACK':
                        if toks[k].kind == 'CARET':
                            ih = toks[k - 1].val if toks[k - 1].kind == 'HASH' else None
                            refs.append(('include', toks[k].val, ih, toks[k].line))
                        elif toks[k].kind == 'HASH' and not (k + 1 < len(toks) and toks[k + 1].kind == 'CARET'):
                            hash_refs.append(('include', toks[k].val, toks[k].line))
                        k += 1
        elif w == 'SPEC_VERSION':
            has_spec_version = True
        elif w == 'DEF':
            k = idx - 1
            if k >= 0 and toks[k].kind in ('CARET', 'STR'):
                name = name_key(toks[k].val); k -= 1
                if k >= 0 and toks[k].kind == 'ID' and toks[k].val in ('ACTOR', 'TEMPLATE'):
                    k -= 1
                hsh = toks[k].val if k >= 0 and toks[k].kind == 'HASH' else None
                defined_names.setdefault(name, []).append(t.line)
                if hsh:
                    anchors.setdefault(hsh, []).append(t.line)
                    anchor_names.setdefault(hsh, set()).add(name)
                next_lbrace_is_def = True
                next_lbrace_def_name = name
        elif w == 'PROPERTIES':
            # §8 declarations. The owner is the nearest enclosing DEF — or, when this
            # block sits inside a MODIFY/OVERRIDE, the entity being modified, which is
            # how §13 introduces a property the target never had.
            owner = cur_def()
            if owner:
                def_props.setdefault(owner, {}).update(parse_properties_block(toks, idx))
        elif w == 'EXTENDS':
            k = idx + 1
            hsh = None
            if k < len(toks) and toks[k].kind == 'HASH':
                hsh = toks[k].val; k += 1
            if k < len(toks) and toks[k].kind == 'CARET':
                refs.append(('extends', toks[k].val, hsh, t.line))
                owner = cur_def()
                if owner:
                    def_extends.setdefault(owner, []).append(toks[k].val)
        elif w == 'APPLIES':
            k = idx + 1
            if k < len(toks) and toks[k].kind == 'ID' and toks[k].val == 'TO':
                k += 1
                if k < len(toks) and toks[k].kind == 'LBRACK':
                    k += 1
                    while k < len(toks) and toks[k].kind != 'RBRACK':
                        if toks[k].kind == 'CARET':
                            refs.append(('applies to', toks[k].val, None, toks[k].line))
                        k += 1
        elif w == 'LIST':
            k = idx + 1
            if k < len(toks) and toks[k].kind == 'ID' and toks[k].val == 'OF' \
               and k + 1 < len(toks) and toks[k + 1].kind == 'CARET':
                refs.append(('list of', toks[k + 1].val, None, toks[k + 1].line))
        elif w == 'ALIAS':
            # ALIAS ^"new" FOR ^"existing"  (DECISION-6): the alias name resolves
            # as a defined name; the FOR target must resolve.
            k = idx + 1
            if k < len(toks) and toks[k].kind == 'CARET':
                defined_names.setdefault(toks[k].val, []).append(t.line)
                k += 1
                if k < len(toks) and toks[k].kind == 'ID' and toks[k].val == 'FOR':
                    k += 1
                    hsh = None
                    if k < len(toks) and toks[k].kind == 'HASH':
                        hsh = toks[k].val; k += 1
                    if k < len(toks) and toks[k].kind == 'CARET':
                        refs.append(('alias target', toks[k].val, hsh, toks[k].line))
                        aliases.append((toks[idx + 1].val, toks[k].val, t.line))
        elif w == 'REPRINT':
            # REPRINT [#hash] ^"existing"  (v0.5 addendum, DECISION-14): a pointer to an
            # entity this book prints unchanged. It declares nothing; the target resolves.
            k = idx + 1
            hsh = None
            if k < len(toks) and toks[k].kind == 'HASH':
                hsh = toks[k].val; k += 1
            if k < len(toks) and toks[k].kind == 'CARET':
                refs.append(('reprint target', toks[k].val, hsh, toks[k].line))
                reprints.append((toks[k].val, t.line))
            else:
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "REPRINT needs a ^\"name\" (the entity reprinted)"))
        elif w == 'PARAMETERS':
            # PARAMETERS { ^"slot" OF ^"Type" ... }  (DECISION-6): each OF type
            # must resolve; the slot-name carets are local and not refs.
            k = idx + 1
            if k < len(toks) and toks[k].kind == 'LBRACE':
                depth = 0
                while k < len(toks):
                    tk = toks[k]
                    if tk.kind == 'LBRACE':
                        depth += 1
                    elif tk.kind == 'RBRACE':
                        depth -= 1
                        if depth == 0:
                            break
                    elif tk.kind == 'ID' and tk.val == 'OF' \
                            and k + 1 < len(toks) and toks[k + 1].kind == 'CARET':
                        refs.append(('parameter type', toks[k + 1].val, None, toks[k + 1].line))
                    k += 1
        elif w == 'REF':
            # REF OF [#h] ^"Type"                 declares a property named for its type
            # ^"P" REF OF [#h] ^"Type"            declares one whose name differs from its type
            # ^"P" REF [#h] ^"Entity"             gives the value
            # (v0.6, DECISION-17). The type and the entity are reference sites.
            named = idx > 0 and toks[idx - 1].kind in ('CARET', 'STR') and toks[idx - 1].line == t.line
            rty, rth, rtl, rval, rvh, rvl, _j = parse_ref(toks, idx + 1)
            if rty is None and rval is None:
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "REF needs OF ^\"Type\", an ^\"Entity\", or both (§8)"))
                continue
            if not named and rty is None:
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "a REF with no property name before it needs OF ^\"Type\"; "
                                        "to give a value write ^\"Name\" REF ^\"Entity\" (§8)"))
            if rty is not None:
                refs.append(('ref type', rty, rth, rtl))
            if rval is not None:
                refs.append(('ref value', rval, rvh, rvl))
                ref_values.append((cur_def(), toks[idx - 1].val if named else rty, rval, rvl))
        elif w in ('SET', 'TRANSFORM') and not (w == 'SET' and frames and frames[-1].get('is_modify')):
            # A change to a value (v0.6, DECISION-16): <target> SET n | <target> TRANSFORM METHOD n.
            # FOR REVIEW: SET is also the §13 directive, written BEFORE its target directly
            # inside a MODIFY body; that use is left to scan_modify_body and skipped here.
            tgt = change_target(idx)
            if tgt is None:
                if w == 'TRANSFORM':
                    findings.append(Finding(fname, 'lint', 'error', t.line,
                                            "TRANSFORM needs a target before it on the line: a "
                                            "reference, or a CHOOSE (§8)"))
                continue          # a SET with no target on its line is not a change
            if isinstance(tgt, tuple) and not (tgt[1] is None and (cur_def(), tgt[0]) in step_names):
                refs.append(('change target', tgt[0], tgt[1], tgt[2]))
            k = idx + 1
            if w == 'SET':
                if change_amount(k, t.line) is None:
                    findings.append(Finding(fname, 'lint', 'error', t.line,
                                            "SET needs an amount: an integer, or a reference to "
                                            "another value (§8)"))
                continue
            meth = toks[k].val if k < len(toks) and toks[k].kind == 'ID' else None
            if meth == 'MANUAL':
                if not (k + 1 < len(toks) and toks[k + 1].kind == 'STR'):
                    findings.append(Finding(fname, 'lint', 'error', t.line,
                                            "TRANSFORM MANUAL needs the source's words as a string (§8)"))
                continue
            if meth not in CHANGE_METHODS:
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "TRANSFORM needs a method: ADD, SUBTRACT, MULTIPLY, DIVIDE, "
                                        "or MANUAL \"…\" (§8)"))
                continue
            k = change_amount(k + 1, t.line)
            if k is None:
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "TRANSFORM %s needs an amount: an integer, or a reference "
                                        "to another value (§8)" % meth))
                continue
            while k < len(toks) and toks[k].line == t.line and toks[k].kind == 'ID' \
                    and toks[k].val in ('ROUND', 'MIN', 'MAX'):
                if toks[k].val == 'ROUND':
                    if not (k + 1 < len(toks) and toks[k + 1].kind == 'ID'
                            and toks[k + 1].val in ('UP', 'DOWN', 'NEAREST')):
                        findings.append(Finding(fname, 'lint', 'error', t.line,
                                                "ROUND is followed by UP, DOWN or NEAREST (§8)"))
                        break
                elif not (k + 1 < len(toks) and toks[k + 1].kind == 'INT'):
                    findings.append(Finding(fname, 'lint', 'error', t.line,
                                            "%s is followed by an integer (§8)" % toks[k].val))
                    break
                k += 2
        elif w == 'ROLL':
            # [^"Name"] ROLL n OF [#h] ^"Die"  (v0.6, DECISION-18). The die is a reference site.
            # A ROLL not followed by a count is the older system-keyword use (l5r5e's
            # `ROLL "1d10"`): legal vocabulary in a file below 0.6, an error from 0.6 on.
            k = idx + 1
            if not (k < len(toks) and toks[k].kind == 'INT'):
                if spec_version >= (0, 6):
                    findings.append(Finding(fname, 'lint', 'error', t.line,
                                            "ROLL needs a count and a die: ROLL n OF ^\"die\" (§8)"))
                continue
            if int(toks[k].val) < 1:
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "ROLL needs a count of 1 or more (§8)"))
            k += 1
            if not (k < len(toks) and toks[k].kind == 'ID' and toks[k].val == 'OF'):
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "ROLL n must be followed by OF ^\"die\" (§8)"))
                continue
            k += 1
            hsh = None
            if k < len(toks) and toks[k].kind == 'HASH':
                hsh = toks[k].val
                k += 1
            if not (k < len(toks) and toks[k].kind == 'CARET'):
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "ROLL n OF needs a ^\"die\" (§8)"))
                continue
            refs.append(('roll die', toks[k].val, hsh, toks[k].line))
            rolls.append((toks[k].val, toks[k].line))
            if idx > 0 and toks[idx - 1].kind in ('CARET', 'STR') and toks[idx - 1].line == t.line:
                step_names.add((cur_def(), toks[idx - 1].val))
        elif w == 'NEXT':
            # NEXT <statement>  (v0.6, DECISION-18): the statement is a step that follows the
            # one above it. It needs one above and one after.
            prev = toks[idx - 1] if idx > 0 else None
            nxt = toks[idx + 1] if idx + 1 < len(toks) else None
            if prev is None or prev.kind == 'LBRACE':
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "NEXT has no statement before it in this block (§8)"))
            if nxt is None or nxt.kind == 'RBRACE' or (nxt.kind == 'ID' and nxt.val == 'NEXT'):
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "NEXT needs a statement after it (§8)"))
        elif w == 'TABLE' and idx + 1 < len(toks) and toks[idx + 1].kind == 'LBRACE':
            # TABLE { AXIS … AT [ … ] { … } … }  /  TABLE { AXIS ^"X" OF ^"Type"  COLUMNS [ … ] }
            # (v0.6, DECISION-21, §5e). A TABLE block with no AXIS in a file below 0.6 is the
            # older system-defined block (COLUMNS / ROW grids, string pairs) and is left alone.
            end, depth = idx + 1, 0
            while end < len(toks):
                if toks[end].kind == 'LBRACE':
                    depth += 1
                elif toks[end].kind == 'RBRACE':
                    depth -= 1
                    if depth == 0:
                        break
                end += 1
            body_has_axis, k, depth = False, idx + 2, 0
            while k < end:
                if toks[k].kind == 'LBRACE':
                    depth += 1
                elif toks[k].kind == 'RBRACE':
                    depth -= 1
                elif depth == 0 and toks[k].kind == 'ID' and toks[k].val == 'AXIS':
                    body_has_axis = True
                k += 1
            if not body_has_axis:
                if spec_version >= (0, 6):
                    findings.append(Finding(fname, 'lint', 'error', t.line,
                                            'a TABLE declares at least one AXIS; the older COLUMNS / ROW '
                                            'grid of strings is not the v0.6 form (§5e)'))
                continue
            tbl = {'line': t.line, 'axes': [], 'cells': [], 'columns': None, 'owner': cur_def()}
            tables.append(tbl)

            def terr(line, msg):
                findings.append(Finding(fname, 'lint', 'error', line, msg + ' (§5e)'))

            def int_span(k):
                """An integer or a range lo-hi at k (a range lexes as lo then -hi). -> (lo, hi, next k)"""
                lo = int(toks[k].val)
                if k + 1 < end and toks[k + 1].kind == 'INT' and toks[k + 1].val.startswith('-') \
                        and toks[k + 1].line == toks[k].line:
                    hi = -int(toks[k + 1].val)
                    if hi < lo:
                        terr(toks[k].line, "a range runs from low to high")
                    return lo, hi, k + 2
                return lo, lo, k + 1

            k = idx + 2
            stray = False
            while k < end:
                tk = toks[k]
                if tk.kind == 'ID' and tk.val == 'AXIS':
                    k += 1
                    if not (k < end and toks[k].kind in ('CARET', 'STR')):
                        terr(tk.line, 'AXIS needs a name: AXIS ^"Name" …')
                        continue
                    ax = {'name': toks[k].val, 'line': tk.line, 'kind': None}
                    tbl['axes'].append(ax)
                    k += 1
                    if k < end and toks[k].kind == 'ID' and toks[k].val == 'OF':
                        k += 1
                        hsh = None
                        if k < end and toks[k].kind == 'HASH':
                            hsh = toks[k].val; k += 1
                        if k < end and toks[k].kind == 'CARET':
                            ax['kind'], ax['type'] = 'type', toks[k].val
                            refs.append(('axis type', toks[k].val, hsh, toks[k].line))
                            k += 1
                        else:
                            terr(tk.line, 'AXIS … OF needs a ^"Type"')
                    elif k < end and toks[k].kind == 'INT' and toks[k].line == tk.line:
                        lo, hi, k = int_span(k)
                        ax['kind'], ax['lo'], ax['hi'] = 'range', lo, hi
                    elif k < end and toks[k].kind == 'ID' and toks[k].val == 'ROLL':
                        ax['kind'] = 'number'          # the ROLL handler checks the count and the die
                        k += 1
                        while k < end and toks[k].line == tk.line and (
                                toks[k].kind in ('INT', 'HASH', 'CARET')
                                or (toks[k].kind == 'ID' and toks[k].val == 'OF')):
                            k += 1
                    elif k < end and toks[k].kind == 'ID' and toks[k].val == 'INTEGER':
                        ax['kind'] = 'number'
                        k += 1
                    elif k < end and toks[k].kind == 'LBRACK':
                        ax['kind'], ax['points'] = 'list', set()
                        k += 1
                        while k < end and toks[k].kind != 'RBRACK':
                            if toks[k].kind == 'STR':
                                ax['points'].add(('s', toks[k].val))
                            elif toks[k].kind == 'CARET':
                                ph = toks[k - 1].val if toks[k - 1].kind == 'HASH' else None
                                refs.append(('axis point', toks[k].val, ph, toks[k].line))
                                ax['points'].add(('e', toks[k].val))
                            k += 1
                        k += 1
                        if not ax['points']:
                            terr(tk.line, 'AXIS ^"%s" lists no point' % ax['name'])
                    else:
                        terr(tk.line, 'AXIS ^"%s" needs its points: OF ^"Type", a range lo-hi, '
                                      'INTEGER, ROLL n OF ^"die", or a list [ … ]' % ax['name'])
                elif tk.kind == 'ID' and tk.val == 'AT':
                    if not (k + 1 < end and toks[k + 1].kind == 'LBRACK'):
                        terr(tk.line, 'AT is followed by its coordinates: AT [ … ] { … }')
                        k += 1
                        continue
                    coords, k, cur = [], k + 2, None
                    while k < end and toks[k].kind != 'RBRACK':
                        c = toks[k]
                        if c.kind == 'COMMA':
                            if cur is None:
                                terr(c.line, 'a coordinate is missing before a comma')
                            cur = None
                            k += 1
                            continue
                        if cur is not None and not (cur[0] == 'pending_hash'):
                            terr(c.line, 'coordinates are separated by commas')
                        if c.kind == 'INT':
                            lo, hi, k = int_span(k)
                            cur = ('n', lo, hi)
                        elif c.kind == 'ID' and c.val in ('MIN', 'MAX'):
                            if k + 1 < end and toks[k + 1].kind == 'INT':
                                n1 = int(toks[k + 1].val)
                                cur = ('n', n1, float('inf')) if c.val == 'MIN' else ('n', float('-inf'), n1)
                                k += 2
                            else:
                                terr(c.line, '%s in a coordinate is followed by a whole number' % c.val)
                                cur = ('bad',)
                                k += 1
                        elif c.kind == 'ID' and c.val == 'ANY':
                            cur = ('any',)
                            k += 1
                        elif c.kind == 'HASH':
                            cur = ('pending_hash',)
                            k += 1
                            continue
                        elif c.kind == 'CARET':
                            ch = toks[k - 1].val if toks[k - 1].kind == 'HASH' else None
                            refs.append(('table coordinate', c.val, ch, c.line))
                            cur = ('e', c.val)
                            k += 1
                        elif c.kind == 'STR':
                            cur = ('s', c.val)
                            k += 1
                        else:
                            terr(c.line, 'a coordinate is a number, a range, MIN n, MAX n, an entity, '
                                         'a string or ANY')
                            cur = ('bad',)
                            k += 1
                        if cur[0] != 'pending_hash':
                            coords.append(cur)
                    k += 1                                    # past ]
                    tbl['cells'].append((coords, tk.line))
                    if not (k < end and toks[k].kind == 'LBRACE'):
                        terr(tk.line, 'AT [ … ] is followed by its result in a block { … }')
                        if k < end and toks[k].kind in ('STR', 'INT', 'CARET'):
                            k += 1
                        continue
                    depth = 0
                    while k < end:                            # skip the result; the main loop reads it
                        if toks[k].kind == 'LBRACE':
                            depth += 1
                        elif toks[k].kind == 'RBRACE':
                            depth -= 1
                            if depth == 0:
                                break
                        k += 1
                    k += 1
                elif tk.kind == 'ID' and tk.val == 'COLUMNS' and k + 1 < end and toks[k + 1].kind == 'LBRACK':
                    cols, k = [], k + 2
                    while k < end and toks[k].kind != 'RBRACK':
                        if toks[k].kind == 'CARET':
                            cols.append((toks[k].val, toks[k].line))
                        elif toks[k].kind == 'STR':
                            terr(toks[k].line, 'COLUMNS lists properties of the axis type as ^"Name", '
                                               'not strings')
                        k += 1
                    k += 1
                    tbl['columns'] = (cols, tk.line)
                else:
                    if not stray:
                        terr(tk.line, 'a TABLE holds AXIS lines and then AT cells or COLUMNS; '
                                      'the older COLUMNS / ROW grid of strings is not the v0.6 form')
                        stray = True
                    # step over a bracket list or a block so one stray statement is one finding
                    if tk.kind in ('LBRACK', 'LBRACE'):
                        opener, closer = tk.kind, 'RBRACK' if tk.kind == 'LBRACK' else 'RBRACE'
                        depth = 0
                        while k < end:
                            if toks[k].kind == opener:
                                depth += 1
                            elif toks[k].kind == closer:
                                depth -= 1
                                if depth == 0:
                                    break
                            k += 1
                    k += 1

            axes = tbl['axes']
            if not axes:
                terr(t.line, 'a TABLE declares at least one AXIS')
                continue
            if tbl['columns'] is not None:
                if tbl['cells']:
                    terr(tbl['columns'][1], 'a TABLE has AT cells or COLUMNS, not both')
                if len(axes) != 1 or axes[0]['kind'] != 'type':
                    terr(tbl['columns'][1], 'COLUMNS needs exactly one axis, and that axis OF ^"Type"')
            elif not tbl['cells']:
                terr(t.line, 'a TABLE lists AT cells, or COLUMNS for a table of records')
            typed = []                    # (entity, type, line) for table_pass
            for coords, cline in tbl['cells']:
                if len(coords) != len(axes):
                    terr(cline, 'AT gives %d coordinate(s) and the table has %d axis/axes'
                                % (len(coords), len(axes)))
                    continue
                for c, ax in zip(coords, axes):
                    if c[0] in ('any', 'bad') or ax['kind'] is None:
                        continue
                    if ax['kind'] in ('range', 'number'):
                        if c[0] != 'n':
                            terr(cline, 'axis ^"%s" takes numbers' % ax['name'])
                        elif ax['kind'] == 'range':
                            lo = ax['lo'] if c[1] == float('-inf') else c[1]
                            hi = ax['hi'] if c[2] == float('inf') else c[2]
                            if lo < ax['lo'] or hi > ax['hi']:
                                terr(cline, 'coordinate is outside axis ^"%s", which runs %d-%d'
                                            % (ax['name'], ax['lo'], ax['hi']))
                    elif ax['kind'] == 'list':
                        if c[0] not in ('s', 'e') or (c[0], c[1]) not in ax['points']:
                            terr(cline, 'coordinate is not one of the points axis ^"%s" lists' % ax['name'])
                    elif ax['kind'] == 'type':
                        if c[0] != 'e':
                            terr(cline, 'axis ^"%s" takes an entity of ^"%s"' % (ax['name'], ax['type']))
                        else:
                            typed.append((c[1], ax['type'], cline))
            tbl['typed'] = typed

            def meets(a, b):
                if a[0] == 'any' or b[0] == 'any':
                    return True
                if a[0] == 'n' and b[0] == 'n':
                    return a[1] <= b[2] and b[1] <= a[2]
                return a[0] == b[0] and a[0] in ('s', 'e') and a[1] == b[1]

            good = [(c, ln) for c, ln in tbl['cells'] if len(c) == len(axes) and all(x[0] != 'bad' for x in c)]
            for i2 in range(len(good)):
                for i1 in range(i2):
                    if all(meets(a, b2) for a, b2 in zip(good[i1][0], good[i2][0])):
                        terr(good[i2][1], 'this cell and the one on line %d cover the same coordinates'
                                          % good[i1][1])
                        break
        elif w in ('EMPHASIS', 'LABEL'):
            # EMPHASIS [BOLD] [ITALIC] { "span" … }  /  LABEL [depth] { "span" … }
            # (v0.6, DECISION-19, §5c). Only the words before the brace are checked here; that
            # each span is in the DEF's prose is check_references.py's rule.
            k = idx + 1
            head = []
            while k < len(toks) and toks[k].kind in ('ID', 'INT') and toks[k].line == t.line and len(head) < 4:
                head.append(toks[k]); k += 1
            if k < len(toks) and toks[k].kind == 'LBRACE':
                if w == 'EMPHASIS':
                    for h in head:
                        if h.val not in EMPHASIS_KINDS:
                            findings.append(Finding(fname, 'lint', 'error', h.line,
                                                    f'EMPHASIS kind "{h.val}" is not one of '
                                                    f'{", ".join(EMPHASIS_KINDS)} (§5c)'))
                    for kind in EMPHASIS_KINDS:
                        if [h.val for h in head].count(kind) > 1:
                            findings.append(Finding(fname, 'lint', 'error', t.line,
                                                    f'EMPHASIS kind {kind} is written more than once (§5c)'))
                elif len(head) > 1 or (head and not (head[0].kind == 'INT' and int(head[0].val) >= 1)):
                    findings.append(Finding(fname, 'lint', 'error', t.line,
                                            'LABEL depth is a whole number of 1 or more (§5c)'))
        elif w == 'FACES' and idx + 1 < len(toks) and toks[idx + 1].kind == 'LBRACE':
            # FACES { face … }  (v0.6, DECISION-18): a face is a number or a range low-high, then
            # optionally what it shows (a string or a reference), then optionally WEIGHT n.
            k = idx + 2
            nfaces = 0
            last = None           # 'face', 'shows' or 'weight': what the previous element was
            while k < len(toks) and toks[k].kind != 'RBRACE':
                tk = toks[k]
                if tk.kind == 'INT':
                    nfaces += 1
                    last = 'face'
                    lo = int(tk.val)
                    # `1-8` lexes as 1 then -8
                    if k + 1 < len(toks) and toks[k + 1].kind == 'INT' and toks[k + 1].val.startswith('-') \
                            and toks[k + 1].line == tk.line:
                        if -int(toks[k + 1].val) < lo:
                            findings.append(Finding(fname, 'lint', 'error', tk.line,
                                                    "a FACES range runs from low to high (§8)"))
                        k += 1
                elif tk.kind == 'CARET':
                    fh = toks[k - 1].val if toks[k - 1].kind == 'HASH' else None
                    refs.append(('face value', tk.val, fh, tk.line))
                    last = 'shows'
                elif tk.kind == 'STR':
                    last = 'shows'
                elif tk.kind == 'ID' and tk.val == 'WEIGHT':
                    if last not in ('face', 'shows'):
                        findings.append(Finding(fname, 'lint', 'error', tk.line,
                                                "WEIGHT has no face before it (§8)"))
                    last = 'weight'
                    if not (k + 1 < len(toks) and toks[k + 1].kind == 'INT' and int(toks[k + 1].val) >= 1):
                        findings.append(Finding(fname, 'lint', 'error', tk.line,
                                                "WEIGHT is followed by a positive integer (§8)"))
                    else:
                        k += 1
                elif tk.kind != 'HASH':
                    findings.append(Finding(fname, 'lint', 'error', tk.line,
                                            "a face is a number or a range, then optionally what it "
                                            "shows and WEIGHT n (§8)"))
                    break
                k += 1
            if nfaces == 0:
                findings.append(Finding(fname, 'lint', 'error', t.line, "FACES lists no face (§8)"))
        elif w == 'CHOOSE':
            # CHOOSE [DISTINCT|INDISTINCT] n ( [ options ] | OF [#hash] ^"Type" [WITH { … }] )
            # (v0.6, DECISION-15; replaces CHOICE / PICK / WHERE). Entity options and the OF
            # type are reference sites; a WITH names properties of the type.
            k = idx + 1
            distinct = True
            if k < len(toks) and toks[k].kind == 'ID' and toks[k].val in ('DISTINCT', 'INDISTINCT'):
                distinct = toks[k].val == 'DISTINCT'
                k += 1
            if k >= len(toks) or toks[k].kind != 'INT' or int(toks[k].val) < 1:
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "CHOOSE needs a count of 1 or more: CHOOSE n [ … ] or "
                                        "CHOOSE n OF ^\"Type\" (§5b)"))
                continue
            n = int(toks[k].val)
            k += 1
            if k < len(toks) and toks[k].kind == 'LBRACK':
                depth, brace, items, in_item, nested = 0, 0, 0, False, False
                while k < len(toks):
                    tk = toks[k]
                    if tk.kind == 'LBRACK':
                        depth += 1
                    elif tk.kind == 'RBRACK':
                        depth -= 1
                        if depth == 0:
                            break
                    elif tk.kind == 'LBRACE':
                        brace += 1
                    elif tk.kind == 'RBRACE':
                        brace -= 1
                    elif depth == 1 and brace == 0:
                        if tk.kind == 'COMMA':
                            in_item = nested = False
                        else:
                            if not in_item:
                                items += 1
                                in_item = True
                            if tk.kind == 'ID' and tk.val == 'CHOOSE':
                                nested = True     # an option that is itself a CHOOSE: its own
                                                  # handler resolves what it names
                            elif tk.kind == 'CARET' and not nested \
                                    and not (k + 1 < len(toks) and toks[k + 1].kind == 'LPAREN'):
                                hsh = toks[k - 1].val if toks[k - 1].kind == 'HASH' else None
                                refs.append(('choose option', tk.val, hsh, tk.line))
                    k += 1
                if distinct and n > items:
                    refs.append(('__msg__', "CHOOSE %d from a list of %d: a DISTINCT choice cannot pick "
                                 "more than are listed (INDISTINCT lets an option be picked again)"
                                 % (n, items), None, t.line))
            elif k < len(toks) and toks[k].kind == 'ID' and toks[k].val == 'OF':
                k += 1
                hsh = None
                if k < len(toks) and toks[k].kind == 'HASH':
                    hsh = toks[k].val
                    k += 1
                if k >= len(toks) or toks[k].kind != 'CARET':
                    findings.append(Finding(fname, 'lint', 'error', t.line,
                                            "CHOOSE n OF needs a ^\"Type\" (§5b)"))
                    continue
                tname = toks[k].val
                refs.append(('choose type', tname, hsh, toks[k].line))
                k += 1
                if k < len(toks) and toks[k].kind == 'ID' and toks[k].val == 'WHERE':
                    findings.append(Finding(fname, 'lint', 'error', toks[k].line,
                                            "WHERE was replaced by WITH in v0.6: "
                                            "WITH { ^\"Property\" [ values ] AND … } (§5b)"))
                elif k + 1 < len(toks) and toks[k].kind == 'ID' and toks[k].val == 'WITH' \
                        and toks[k + 1].kind == 'LBRACE':
                    wline = toks[k].line
                    k += 2
                    joins, wprops, ok, want_term, many_values = set(), [], True, True, False
                    while k < len(toks) and toks[k].kind != 'RBRACE':
                        tk = toks[k]
                        if want_term:
                            if tk.kind == 'ID' and tk.val == 'NOT':
                                k += 1
                                continue
                            if tk.kind != 'CARET' or k + 1 >= len(toks) or toks[k + 1].kind != 'LBRACK':
                                ok = False
                                break
                            wprops.append((tk.val, tk.line))
                            k += 2
                            nvals = 0
                            while k < len(toks) and toks[k].kind != 'RBRACK':
                                if toks[k].kind in ('STR', 'INT', 'BOOL'):
                                    nvals += 1
                                elif toks[k].kind == 'CARET':
                                    nvals += 1
                                    vh = toks[k - 1].val if toks[k - 1].kind == 'HASH' else None
                                    refs.append(('with value', toks[k].val, vh, toks[k].line))
                                elif toks[k].kind not in ('COMMA', 'HASH'):
                                    ok = False
                                k += 1
                            if nvals == 0:
                                ok = False
                            elif nvals > 1:
                                many_values = True
                            k += 1
                            want_term = False
                        else:
                            if tk.kind == 'ID' and tk.val in ('AND', 'OR'):
                                joins.add(tk.val)
                                want_term = True
                                k += 1
                            else:
                                ok = False
                                break
                    if not ok or want_term:
                        findings.append(Finding(fname, 'lint', 'error', wline,
                                                "malformed WITH: each term is ^\"Property\" [ values ], "
                                                "optionally after NOT, joined by AND or OR (§5b)"))
                    elif many_values:
                        findings.append(Finding(fname, 'lint', 'error', wline,
                                                "a WITH term takes one value: a comma is not an implicit "
                                                "OR; write ^\"P\" [\"A\"] OR ^\"P\" [\"B\"] (§5b)"))
                    elif len(joins) > 1:
                        findings.append(Finding(fname, 'lint', 'error', wline,
                                                "WITH mixes AND and OR: nested conditions are not yet "
                                                "defined (§5b to-do); use AND throughout or OR throughout"))
                    else:
                        chooses.append({'type': tname, 'props': wprops, 'line': wline})
            else:
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "CHOOSE n must be followed by a list [ … ] or OF ^\"Type\" (§5b)"))
        elif w == 'CHOICE':
            # CHOICE [ options ]  (DECISION-6) was replaced by CHOOSE n in v0.6 (DECISION-15).
            # Its options are still resolved so nothing goes unchecked before a corpus migrates;
            # carets inside a WHERE { } are field names (local, skipped).
            # A file that declares SPEC_VERSION 0.6 or later has no business writing it: error.
            # One that declares less, or nothing, is a 0.5 file awaiting migration: warning.
            findings.append(Finding(fname, 'lint', 'error' if spec_version >= (0, 6) else 'warning',
                                    t.line,
                                    "CHOICE was removed in v0.6: write CHOOSE n [ … ], with the count "
                                    "(§5b, DECISION-15)"))
            k = idx + 1
            if k < len(toks) and toks[k].kind == 'ID' and toks[k].val == 'PICK':
                k += 2
            if k < len(toks) and toks[k].kind == 'LBRACK':
                depth, where_depth = 0, 0
                while k < len(toks):
                    tk = toks[k]
                    if tk.kind == 'LBRACK':
                        depth += 1
                    elif tk.kind == 'RBRACK':
                        depth -= 1
                        if depth == 0:
                            break
                    elif tk.kind == 'LBRACE':
                        where_depth += 1
                    elif tk.kind == 'RBRACE':
                        where_depth -= 1
                    elif tk.kind == 'CARET' and where_depth == 0 \
                            and not (k + 1 < len(toks) and toks[k + 1].kind == 'LPAREN'):
                        refs.append(('choice option', tk.val, None, tk.line))
                    k += 1
        elif w == 'MODIFY':
            # §13 has two block spellings — `MODIFY ^"X" { }` and `^"X" MODIFY { }` —
            # and one non-statement use, `#hash MODIFY: rule text` inside RULES, which
            # names no target and must not be mistaken for either.
            nxt = toks[idx + 1] if idx + 1 < len(toks) else None
            tgt, hsh, lb = None, None, None
            if nxt is None or nxt.kind == 'COLON':
                pass
            elif nxt.kind in ('CARET', 'HASH'):
                k = idx + 1
                if toks[k].kind == 'HASH':
                    hsh = toks[k].val; k += 1
                if k + 1 < len(toks) and toks[k].kind == 'CARET' \
                        and toks[k + 1].kind == 'LBRACE':
                    tgt, lb = toks[k].val, k + 1
            elif nxt.kind == 'LBRACE' and idx > 0 and toks[idx - 1].kind == 'CARET':
                tgt, lb = toks[idx - 1].val, idx + 1
            if tgt is not None:
                refs.append(('modify target', tgt, hsh, t.line))
                mods.append({'target': tgt, 'line': t.line, 'ops': scan_modify_body(toks, lb)})
                next_lbrace_is_modify = True
                next_lbrace_is_def = True
                next_lbrace_def_name = tgt
        elif w == 'OVERRIDE':
            # Both the §13 block form and the bare `OVERRIDE ^"X"` statement the corpus
            # uses inside a variant DEF: either way the target has to exist.
            k = idx + 1
            hsh = None
            if k < len(toks) and toks[k].kind == 'HASH':
                hsh = toks[k].val; k += 1
            if k < len(toks) and toks[k].kind == 'CARET':
                refs.append(('override target', toks[k].val, hsh, t.line))
                if k + 1 < len(toks) and toks[k + 1].kind == 'LBRACE':
                    next_lbrace_is_def = True
                    next_lbrace_def_name = toks[k].val
        elif w == 'ADD':
            k = idx + 1
            if k < len(toks) and toks[k].kind == 'HASH':
                k += 1
            if k + 1 < len(toks) and toks[k].kind == 'CARET' \
                    and toks[k + 1].kind == 'ID' and toks[k + 1].val == 'DEF':
                adds.append((toks[k].val, toks[k + 1].line))
        elif w == 'DEPENDS_ON':
            if idx + 1 < len(toks) and toks[idx + 1].kind == 'STR':
                depends.append((toks[idx + 1].val, t.line))
        elif w == 'TEXT' and idx + 1 < len(toks) and toks[idx + 1].kind == 'STR' \
                and frames and frames[-1].get('kw') == 'DEF' and not caret_earlier_on_line(idx):
            # A definition's prose is DESCRIPTION (§10, DECISION-30). TEXT is the prose field
            # of an ENTRY and of other blocks that are not definitions.
            findings.append(Finding(fname, 'lint', 'error' if spec_version >= (0, 6) else 'warning',
                                    t.line, "TEXT directly in a DEF: a definition's prose is "
                                    "DESCRIPTION; TEXT is the prose field of an ENTRY and of "
                                    "other blocks that are not definitions (§10)"))
        elif w == 'ORIGIN' and idx + 1 < len(toks) and toks[idx + 1].kind == 'STR':
            # A port's source (§19, DECISION-26): ORIGIN "edition" <KIND> "id", in the header.
            # `ORIGIN {` with no string is a block some frozen pre-0.4 files use, and is left alone.
            kind_tok = toks[idx + 2] if idx + 2 < len(toks) else None
            id_tok = toks[idx + 3] if idx + 3 < len(toks) else None
            if not (kind_tok is not None and kind_tok.kind == 'ID' and kind_tok.val in CONTAINER_KINDS
                    and kind_tok.line == t.line
                    and id_tok is not None and id_tok.kind == 'STR' and id_tok.line == t.line):
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        'ORIGIN names an edition, a kind of container and its id: '
                                        'ORIGIN "arm5e" EXTENSION "ArM5_Grogs_Abilities" (§19)'))
            elif len(frames) != 1:
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        'ORIGIN stands in the file\'s header, beside VERSION and '
                                        'DEPENDS_ON (§19)'))
            elif origins:
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        'a file declares one ORIGIN; the first is on line %d (§19)'
                                        % origins[0][3]))
            else:
                origins.append((toks[idx + 1].val, kind_tok.val, id_tok.val, t.line))
        elif w == 'FIAT':
            nxt = toks[idx + 1] if idx + 1 < len(toks) else None
            if nxt is None or nxt.kind != 'STR':
                findings.append(Finding(fname, 'lint', 'error', t.line, "FIAT requires a reason string"))
            if caret_earlier_on_line(idx):
                waived_lines.add(t.line)                       # property-level
            else:
                for fr in reversed(frames):                    # element-level: nearest DEF
                    if fr['is_def']:
                        fr['waived'] = True
                        break
        elif w == 'INTEGER':
            k = idx + 1
            val = None
            if k < len(toks) and toks[k].kind == 'INT':
                val = int(toks[k].val); k += 1
            mn = mx = None
            while k < len(toks) and toks[k].line == t.line:
                if toks[k].kind == 'ID' and toks[k].val in ('MIN', 'MAX') \
                   and k + 1 < len(toks) and toks[k + 1].kind == 'INT':
                    if toks[k].val == 'MIN':
                        mn = int(toks[k + 1].val)
                    else:
                        mx = int(toks[k + 1].val)
                    k += 2; continue
                k += 1
            if val is not None and ((mn is not None and val < mn) or (mx is not None and val > mx)):
                refs.append(('__range__', f"{val} outside [{mn},{mx}]", None, t.line))

    for fr in frames:
        findings.append(Finding(fname, 'lint', 'error', fr['open'], "unclosed '{'"))
    # §12: a rule states itself. `#hash: slug` alone on its line — a name with no text, the
    # rule only described in a comment beside it — carries nothing a tool can read (the L5R
    # corpus held 980 of them, 2026-09-23).
    for k in range(len(toks) - 2):
        a, b, c = toks[k], toks[k + 1], toks[k + 2]
        if a.kind == 'HASH' and b.kind == 'COLON' and c.kind == 'ID' and a.line == b.line == c.line \
                and (k + 3 >= len(toks) or toks[k + 3].line != a.line):
            findings.append(Finding(fname, 'lint', 'warning', a.line,
                                    "rule %s (%s) has no text: give it the source's statement of the rule, "
                                    "or a structured WHEN … THEN (§12)" % (a.val, c.val)))
    # Markdown emphasis inside a string (§5c, DECISION-19). The span belongs in an EMPHASIS or
    # LABEL block beside the text. A warning in a file below 0.6, an error from 0.6. A FIAT on
    # the property's line, or on the DEF around it, excuses asterisks the source prints.
    for tk in toks:
        if tk.kind != 'STR' or '*' not in tk.val:
            continue
        nbold = len(MD_BOLD.findall(tk.val))
        nital = len(MD_ITALIC.findall(MD_BOLD.sub('', tk.val)))
        if not (nbold or nital):
            continue
        last = tk.line + tk.val.count('\n')
        if tk.line in waived_lines or last in waived_lines \
                or any(a <= tk.line <= b for a, b in waived_ranges):
            continue
        what = ' and '.join(x for x in ('%d bold' % nbold if nbold else '',
                                        '%d italic' % nital if nital else '') if x)
        findings.append(Finding(fname, 'lint', 'error' if spec_version >= (0, 6) else 'warning', tk.line,
                                'string holds Markdown emphasis (%s): record each span in an EMPHASIS '
                                'or LABEL block beside the text, or FIAT "reason" where the source '
                                'prints the asterisks (§5c)' % what))
    for tk in toks:
        # A hash is `#` and 16 or more of [A-Za-z0-9] (§5). Shorter, or with an underscore:
        # a warning in a file below 0.6, an error from 0.6 (DECISION-32).
        if tk.kind == 'HASH' and len(tk.val) - 1 < HASH_MIN_BODY:
            findings.append(Finding(fname, 'lint', 'error' if spec_version >= (0, 6) else 'warning', tk.line,
                                    "hash id '%s' shorter than %d chars" % (tk.val, HASH_MIN_BODY)))
        elif tk.kind == 'HASH' and '_' in tk.val:
            findings.append(Finding(fname, 'lint', 'error' if spec_version >= (0, 6) else 'warning', tk.line,
                                    "hash id '%s' holds an underscore: a hash is letters and digits (§5)"
                                    % tk.val))
    bare_actor = fname.endswith('.actor') and check_actor_file(fname, toks, spec_version, findings)
    vdefs, bound = collect_definitions(fname, toks)
    if not has_spec_version and not bare_actor:
        # a bare .actor has its own warning (§2), which says it declares no SPEC_VERSION
        findings.append(Finding(fname, 'lint', 'warning', 1, "no SPEC_VERSION declared"))

    return {
        'file': fname, 'kind': 'ttrpg', 'names': defined_names, 'anchors': anchors, 'refs': refs,
        'depends': depends, 'file_ids': file_ids,
        'waived_ranges': waived_ranges, 'waived_lines': waived_lines,
        'def_props': def_props, 'def_extends': def_extends, 'mods': mods, 'adds': adds,
        'reprints': reprints, 'aliases': aliases, 'chooses': chooses, 'ref_values': ref_values,
        'rolls': rolls, 'tables': tables, 'containers': containers, 'froms': froms,
        'block_types': block_types, 'block_names': block_names, 'block_anchors': block_anchors,
        'block_anchor_lines': block_anchor_lines, 'anchor_names': anchor_names, 'origins': origins,
        'vdefs': vdefs, 'bound': bound, 'spec_version': spec_version,
        'hash_refs': hash_refs,
    }


# ═══════════════════════════════════════════════════════════════════════════
# CODEX analysis (spec §25) — the stand-off lore knowledge graph
# ═══════════════════════════════════════════════════════════════════════════

def analyze_codex(fname, text, findings):
    """Structure a .codex file: a CATEGORIES taxonomy, a declared RELATIONS
    predicate vocabulary, and ENTITY nodes with typed edges. Category and entity
    NAMES join the corpus namespace (so ^"Name" resolves to them anywhere and
    entity->entity links ride the ordinary caret machinery); IS categories and
    category EXTENDS parents are raised as ordinary refs (hard errors if
    unresolved). Predicate declarations, edges, domain/range and SOURCE bindings
    are checked in codex_coherence (some are warnings, not errors).

    The tokenizer drops the '->' arrow (both chars are non-tokens), so an edge
    `^"pred" -> ^"obj"` reaches us as two adjacent CARETs — same as §5c."""
    toks = tokenize(text, fname, findings)
    n = len(toks)
    names, anchors, refs, depends, file_ids = {}, {}, [], [], []
    entity_anchors = {}   # hash -> set(entity names): codex ENTITY anchors may
                          # recur across files as §13 amends (one hash, one name)
    relations = {}    # predicate name -> {inverse, domain, range, symmetric, transitive, line}
    edges = []        # (subject, predicate, object, line)
    dr_refs = []      # (category-name, line) — DOMAIN/RANGE targets, checked as warnings
    sources = []      # (entity, lore-file, heading-slug, line)
    has_spec_version = False

    ctx = []          # stack of (label, name) frames, aligned with brace depth
    pending = None    # (label, name) for the next '{'
    depth = 0

    def nearest(label):
        for lbl, nm in reversed(ctx):
            if lbl == label:
                return nm
        return None

    i = 0
    while i < n:
        t = toks[i]
        if t.kind == 'LBRACE':
            depth += 1
            ctx.append(pending or ('?', None))
            pending = None
            i += 1
            continue
        if t.kind == 'RBRACE':
            if ctx:
                ctx.pop()
            depth -= 1
            i += 1
            continue

        top = ctx[-1][0] if ctx else None

        if t.kind == 'ID':
            w = t.val
            if w == 'CODEX' and i + 1 < n and toks[i + 1].kind == 'STR':
                file_ids.append(toks[i + 1].val)
            elif w == 'SPEC_VERSION':
                has_spec_version = True
            elif w == 'DEPENDS_ON' and i + 1 < n and toks[i + 1].kind == 'STR':
                depends.append((toks[i + 1].val, t.line))
            elif w == 'SOURCES':
                pending = ('SOURCES', None)
            elif w == 'CATEGORIES':
                pending = ('CATEGORIES', None)
            elif w == 'RELATIONS':
                pending = ('RELATIONS', None)
            elif w == 'RELATIONSHIPS':
                pending = ('RELATIONSHIPS', None)
            elif w == 'ENTITY':
                k = i + 1
                hsh = None
                if k < n and toks[k].kind == 'HASH':
                    hsh = toks[k].val
                    k += 1
                if k < n and toks[k].kind == 'CARET':
                    nm = toks[k].val
                    names.setdefault(nm, []).append(t.line)
                    if hsh:
                        anchors.setdefault(hsh, []).append(t.line)
                        entity_anchors.setdefault(hsh, set()).add(nm)
                    pending = ('ENTITY', nm)
                    i = k + 1
                    continue
            elif w == 'IS' and top == 'ENTITY':
                k = i + 1
                while k < n and toks[k].kind == 'CARET':
                    refs.append(('entity IS', toks[k].val, None, toks[k].line))
                    k += 1
                i = k
                continue
            elif w == 'SOURCE' and top == 'ENTITY':
                k, srcfile, slug = i + 1, None, None
                if k < n and toks[k].kind == 'STR':
                    srcfile = toks[k].val
                    k += 1
                if k + 1 < n and toks[k].kind == 'ID' and toks[k].val == 'AT' \
                        and toks[k + 1].kind == 'STR':
                    slug = toks[k + 1].val
                    k += 2
                sources.append((nearest('ENTITY'), srcfile, slug, t.line))
                i = k
                continue
            elif w == 'EXTENDS' and top == 'CAT_ENTRY':
                k, hsh = i + 1, None
                if k < n and toks[k].kind == 'HASH':
                    hsh = toks[k].val
                    k += 1
                if k < n and toks[k].kind == 'CARET':
                    refs.append(('category EXTENDS', toks[k].val, hsh, toks[k].line))
                    i = k + 1
                    continue
            elif w in ('INVERSE', 'DOMAIN', 'RANGE') and top == 'REL_ENTRY':
                rel = relations.get(nearest('REL_ENTRY'))
                if i + 1 < n and toks[i + 1].kind == 'CARET' and rel is not None:
                    val = toks[i + 1].val
                    rel[w.lower()] = val
                    if w in ('DOMAIN', 'RANGE'):
                        dr_refs.append((val, toks[i + 1].line))
                    i += 2
                    continue
            elif w in ('SYMMETRIC', 'TRANSITIVE') and top == 'REL_ENTRY':
                rel = relations.get(nearest('REL_ENTRY'))
                if rel is not None:
                    rel[w.lower()] = True
            i += 1
            continue

        if t.kind == 'CARET':
            if top == 'CATEGORIES':
                # category declaration: [#hash] ^"Name" DEF { ... }
                if i + 1 < n and toks[i + 1].kind == 'ID' and toks[i + 1].val == 'DEF':
                    hsh = toks[i - 1].val if i > 0 and toks[i - 1].kind == 'HASH' else None
                    names.setdefault(t.val, []).append(t.line)
                    if hsh:
                        anchors.setdefault(hsh, []).append(t.line)
                    pending = ('CAT_ENTRY', t.val)
                    i += 2   # past the DEF keyword; the next '{' opens CAT_ENTRY
                    continue
            elif top == 'RELATIONS':
                # predicate declaration: ^"pred" { ... }
                if i + 1 < n and toks[i + 1].kind == 'LBRACE':
                    if t.val in relations:
                        findings.append(Finding(fname, 'lint', 'error', t.line,
                                                "duplicate relation ^\"%s\"" % t.val))
                    relations[t.val] = {'inverse': None, 'domain': None, 'range': None,
                                        'symmetric': False, 'transitive': False, 'line': t.line}
                    pending = ('REL_ENTRY', t.val)
                    i += 1   # position at the '{'
                    continue
            elif top == 'RELATIONSHIPS':
                # edge: ^"pred" -> ^"obj" [FROM "surface"]   (arrow is a non-token)
                if i + 1 < n and toks[i + 1].kind == 'CARET':
                    edges.append((nearest('ENTITY'), t.val, toks[i + 1].val, t.line))
                    k = i + 2
                    if k + 1 < n and toks[k].kind == 'ID' and toks[k].val == 'FROM' \
                            and toks[k + 1].kind == 'STR':
                        k += 2
                    i = k
                    continue
                findings.append(Finding(fname, 'lint', 'error', t.line,
                                        "relationship ^\"%s\" has no object" % t.val))
            i += 1
            continue

        i += 1

    # INVERSE + SYMMETRIC is contradictory (§25)
    for rel, rec in relations.items():
        if rec['inverse'] and rec['symmetric']:
            findings.append(Finding(fname, 'lint', 'error', rec['line'],
                                    "relation ^\"%s\" declares both INVERSE and SYMMETRIC" % rel))
    if ctx:
        for lbl, _ in ctx:
            findings.append(Finding(fname, 'lint', 'error', 1, "unclosed '{' (%s)" % lbl))
    for tk in toks:
        if tk.kind == 'HASH' and len(tk.val) - 1 < HASH_MIN_BODY:
            findings.append(Finding(fname, 'lint', 'warning', tk.line,
                                    "hash id '%s' shorter than %d chars" % (tk.val, HASH_MIN_BODY)))
    if not has_spec_version:
        findings.append(Finding(fname, 'lint', 'warning', 1, "no SPEC_VERSION declared"))

    return {
        'file': fname, 'kind': 'codex', 'names': names, 'anchors': anchors, 'refs': refs,
        'depends': depends, 'file_ids': file_ids,
        'waived_ranges': [], 'waived_lines': set(),
        'def_props': {}, 'def_extends': {}, 'mods': [], 'adds': [],
        'entity_anchors': entity_anchors,
        'relations': relations, 'edges': edges, 'dr_refs': dr_refs, 'sources': sources,
    }


def is_waived(line, data):
    if line in data['waived_lines']:
        return True
    return any(a <= line <= b for a, b in data['waived_ranges'])


def coherence_pass(files_data, findings):
    corpus_names, corpus_file_ids = set(), set()
    all_anchors = {}  # hash -> [(file, line)]
    for d in files_data:
        # A bridge's own names belong to NEITHER edition (§21); they never join the
        # single-edition namespace, and its refs are checked in bridge_coherence.
        if d.get('kind') != 'bridge':
            corpus_names.update(d['names'])
            corpus_file_ids.update(d['file_ids'])
        for h, lines in d['anchors'].items():
            for ln in lines:
                all_anchors.setdefault(h, []).append((d['file'], ln))

    # A codex ENTITY anchor may recur across section files as an amend (§25): a
    # later file re-states `ENTITY #hash ^"Name"` to add SOURCE/RELATIONSHIPS to
    # the same node. That is legal iff every occurrence of the hash is a codex
    # entity anchor AND they all name the SAME entity. A hash mapped to two
    # different entities, or shared between a codex entity and any other anchor,
    # is still a genuine duplicate.
    codex_ent_names = {}   # hash -> set(names)
    codex_ent_locs = {}    # hash -> [(file, line)]
    for d in files_data:
        if d.get('kind') == 'codex':
            for h, nms in d.get('entity_anchors', {}).items():
                codex_ent_names.setdefault(h, set()).update(nms)
                for ln in d['anchors'].get(h, []):
                    codex_ent_locs.setdefault(h, []).append((d['file'], ln))

    for h, locs in all_anchors.items():
        if len(locs) > 1:
            if h in codex_ent_names and len(codex_ent_names[h]) == 1 \
                    and set(codex_ent_locs.get(h, [])) == set(locs):
                continue   # legal cross-file amend of one codex entity
            where = ", ".join("%s:%d" % (os.path.basename(f), ln) for f, ln in locs)
            f0, l0 = locs[0]
            findings.append(Finding(f0, 'coherence', 'error', l0,
                                    "duplicate anchor %s (%s): a DEF's hash stands once in a "
                                    "corpus; to change a definition, name it in OVERRIDE, MODIFY "
                                    "or REPRINT (§13)" % (h, where)))

    block_hash_names = {}     # hash -> names of the named blocks that carry it, corpus-wide
    for d in files_data:
        for h, nms in d.get('block_anchors', {}).items():
            block_hash_names.setdefault(h, set()).update(nms)
    every_hash = set(all_anchors) | set(block_hash_names)
    # One hash, one thing (§5, §20). The same hash on the same name is a restatement, which §5
    # allows (an errata file restating an entry). The same hash on two different names is two
    # things sharing an anchor, whether both are blocks or one is a DEF.
    def_hash_names = {}
    for d in files_data:
        for h, nms in d.get('anchor_names', {}).items():
            def_hash_names.setdefault(h, set()).update(nms)
    reported = set()
    for d in files_data:
        for h, decls in d.get('block_anchor_lines', {}).items():
            names_on_hash = block_hash_names.get(h, set()) | def_hash_names.get(h, set())
            if len(names_on_hash) > 1 and h not in reported:
                reported.add(h)
                findings.append(Finding(d['file'], 'coherence', 'error', decls[0][1],
                                        "hash %s is declared on %d different names: %s"
                                        % (h, len(names_on_hash),
                                           ", ".join('^"%s"' % n for n in sorted(names_on_hash)))))
    for d in files_data:
        for kind, h, line in d.get('hash_refs', []):
            if h not in every_hash and not is_waived(line, d):
                findings.append(Finding(d['file'], 'coherence', 'error', line,
                                        "%s references undefined hash %s" % (kind, h)))

    for d in files_data:
        if d.get('kind') == 'bridge':
            continue
        for kind, name, hsh, line in d['refs']:
            if kind == '__range__':
                if not is_waived(line, d):
                    findings.append(Finding(d['file'], 'coherence', 'error', line,
                                            "value %s" % name))
                continue
            if kind == '__msg__':
                if not is_waived(line, d):
                    findings.append(Finding(d['file'], 'coherence', 'error', line, name))
                continue
            # Two tiers (§20, DECISION-24). A name resolves everywhere if it is a definition; a
            # named block's name resolves inside its own file; and a reference that carries a
            # block's hash resolves from anywhere, the name being checked against that block's.
            by_block_hash = hsh is not None and name in block_hash_names.get(hsh, ())
            if name not in corpus_names and name not in d.get('block_names', ()) \
                    and not by_block_hash and not is_waived(line, d):
                findings.append(Finding(d['file'], 'coherence', 'error', line,
                                        "%s references undefined ^\"%s\"" % (kind, name)))
            if hsh and hsh not in d['anchors'] and hsh not in {a for a in _all_hashes(files_data)} \
               and not is_waived(line, d):
                findings.append(Finding(d['file'], 'coherence', 'error', line,
                                        "%s references undefined hash %s" % (kind, hsh)))
        for fid, line in d['depends']:
            if fid not in corpus_file_ids and not is_waived(line, d):
                findings.append(Finding(d['file'], 'coherence', 'error', line,
                                        "DEPENDS_ON references undefined file id \"%s\"" % fid))

    codex_coherence(files_data, corpus_names, findings)


def codex_coherence(files_data, corpus_names, findings):
    """Coherence for .codex graphs (spec §25). IS categories and category EXTENDS
    parents ride the ordinary ref machinery in coherence_pass (hard errors). Left
    here: predicates must be declared (error); edge objects should resolve (warn);
    DOMAIN/RANGE should name a declared category (warn); a SOURCE ... AT slug should
    match a heading in the referenced .lore, when that file can be found (warn)."""
    codices = [d for d in files_data if d.get('kind') == 'codex']
    if not codices:
        return
    # Predicates and categories are pooled corpus-wide, so a data-codex may use a
    # schema-codex's vocabulary (imported via DEPENDS_ON).
    corpus_relations, corpus_categories = set(), set()
    for d in codices:
        corpus_relations.update(d['relations'])
        for rec in d['relations'].values():
            if rec['inverse']:
                corpus_relations.add(rec['inverse'])   # the inverse name is usable too
        corpus_categories.update(d['names'])           # entity+category names of this codex

    for d in codices:
        for subj, pred, obj, line in d['edges']:
            if pred not in corpus_relations:
                findings.append(Finding(d['file'], 'coherence', 'error', line,
                                        "relationship uses undeclared predicate ^\"%s\" "
                                        "(declare it in a RELATIONS block)" % pred))
            if obj not in corpus_names:
                findings.append(Finding(d['file'], 'coherence', 'warning', line,
                                        "relationship object ^\"%s\" does not resolve" % obj))
        for cat, line in d['dr_refs']:
            if cat not in corpus_categories and cat not in corpus_names:
                findings.append(Finding(d['file'], 'coherence', 'warning', line,
                                        "DOMAIN/RANGE ^\"%s\" is not a declared category" % cat))
        for entity, srcfile, slug, line in d['sources']:
            if not srcfile or not slug:
                continue
            lore_path = _find_lore(d['file'], srcfile)
            if lore_path is None:
                continue                                # cannot verify — do not warn
            if slug not in _heading_slugs(lore_path):
                findings.append(Finding(d['file'], 'coherence', 'warning', line,
                                        "SOURCE AT \"%s\" matches no heading in %s"
                                        % (slug, os.path.basename(srcfile))))


def _find_lore(codex_file, srcfile):
    """Locate a .lore referenced by SOURCE: as given, beside the codex, or by
    basename within the codex's directory tree. Returns a path or None."""
    if os.path.isabs(srcfile) and os.path.isfile(srcfile):
        return srcfile
    base_dir = os.path.dirname(os.path.abspath(codex_file))
    cand = os.path.join(base_dir, srcfile)
    if os.path.isfile(cand):
        return cand
    target = os.path.basename(srcfile)
    for root, _dirs, files in os.walk(base_dir):
        if target in files:
            return os.path.join(root, target)
    return None


def _slugify(heading):
    """GitHub-style heading slug: lowercase, drop non-word/space/hyphen, spaces→hyphens."""
    s = heading.strip().lower()
    s = re.sub(r'[^\w\s-]', '', s, flags=re.UNICODE)
    s = re.sub(r'\s+', '-', s)
    return s.strip('-')


def _heading_slugs(lore_path):
    slugs = set()
    try:
        with open(lore_path, encoding='utf-8') as fh:
            for ln in fh:
                m = re.match(r'\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$', ln)
                if m:
                    slugs.add(_slugify(m.group(2)))
    except OSError:
        pass
    return slugs


def _resolve_prop(name, prop, props, extends, seen=None):
    """A property declaration on `name`, or on anything up its EXTENDS chain."""
    if seen is None:
        seen = set()
    if name in seen:
        return None
    seen.add(name)
    rec = props.get(name, {}).get(prop)
    if rec is not None:
        return rec
    for parent in extends.get(name, ()):
        rec = _resolve_prop(parent, prop, props, extends, seen)
        if rec is not None:
            return rec
    return None


def _descendants(name, children, seen=None):
    """Every definition that extends `name`, transitively."""
    if seen is None:
        seen = set()
    for child in children.get(name, ()):
        if child in seen:
            continue
        seen.add(child)
        _descendants(child, children, seen)
    return seen


def choose_pass(files_data, findings):
    """CHOOSE n OF ^"Type" WITH { … } (§5b, DECISION-15): every property a WITH names must be
    one the type declares, its own or inherited. A misspelled property would otherwise be a
    condition nothing can meet, and the choice would silently offer nothing."""
    props, extends, known = {}, {}, set()
    for d in files_data:
        if d.get('kind') != 'ttrpg':
            continue
        for nm, table in d['def_props'].items():
            props.setdefault(nm, {}).update(table)
        for nm, parents in d['def_extends'].items():
            extends.setdefault(nm, []).extend(parents)
        known.update(d['names'])
    for d in files_data:
        if d.get('kind') != 'ttrpg':
            continue
        for c in d.get('chooses', []):
            if c['type'] not in known:
                continue        # unresolved type: already reported as a ref
            for pname, line in c['props']:
                if _resolve_prop(c['type'], pname, props, extends) is None and not is_waived(line, d):
                    findings.append(Finding(d['file'], 'coherence', 'error', line,
                                            "WITH names ^\"%s\", which ^\"%s\" does not declare "
                                            "(its own properties or inherited)" % (pname, c['type'])))


def ref_pass(files_data, findings):
    """^"P" REF ^"Entity" (§8, DECISION-17): where a type up the owner's EXTENDS chain declares
    ^"P" REF OF ^"Type", the entity must be of that type: Type itself, or something that
    EXTENDS it, directly or through a chain."""
    props, extends = {}, {}
    for d in files_data:
        if d.get('kind') != 'ttrpg':
            continue
        for nm, table in d['def_props'].items():
            bucket = props.setdefault(nm, {})
            for pname, rec in table.items():
                if rec.get('ref_of') or pname not in bucket:
                    bucket[pname] = rec
        for nm, parents in d['def_extends'].items():
            extends.setdefault(nm, []).extend(parents)

    def declared_type(owner, prop, seen):
        if owner in seen:
            return None
        seen.add(owner)
        rec = props.get(owner, {}).get(prop)
        if rec is not None and rec.get('ref_of'):
            return rec['ref_of']
        for parent in extends.get(owner, ()):
            found = declared_type(parent, prop, seen)
            if found:
                return found
        return None

    def is_a(entity, ty, seen):
        if entity == ty:
            return True
        if entity in seen:
            return False
        seen.add(entity)
        return any(is_a(parent, ty, seen) for parent in extends.get(entity, ()))

    known = set()
    for d in files_data:
        if d.get('kind') == 'ttrpg':
            known.update(d['names'])
    for d in files_data:
        if d.get('kind') != 'ttrpg':
            continue
        for owner, prop, entity, line in d.get('ref_values', []):
            if owner is None or is_waived(line, d):
                continue
            ty = declared_type(owner, prop, set())
            if ty and entity in known:      # an unresolved entity is already reported as a ref
                if not is_a(entity, ty, set()):
                    findings.append(Finding(d['file'], 'coherence', 'error', line,
                                            "^\"%s\" REF ^\"%s\": the property is declared REF OF "
                                            "^\"%s\", and ^\"%s\" is not one" % (prop, entity, ty, entity)))


def roll_pass(files_data, findings):
    """ROLL n OF ^"X" (§8, DECISION-18): X must be a die, a DEF that EXTENDS ^"Die" directly or
    through a chain. Checked only when ^"Die" is in the loaded set; when it is not, the dice
    module was not passed, and the roll's die is already reported as an undefined reference."""
    extends, known = {}, set()
    for d in files_data:
        if d.get('kind') != 'ttrpg':
            continue
        known.update(d['names'])
        for nm, parents in d['def_extends'].items():
            extends.setdefault(nm, []).extend(parents)
    if 'Die' not in known:
        return

    def is_die(name, seen):
        if name == 'Die':
            return True
        if name in seen:
            return False
        seen.add(name)
        return any(is_die(parent, seen) for parent in extends.get(name, ()))

    for d in files_data:
        if d.get('kind') != 'ttrpg':
            continue
        for die, line in d.get('rolls', []):
            if die in known and not is_die(die, set()) and not is_waived(line, d):
                findings.append(Finding(d['file'], 'coherence', 'error', line,
                                        "ROLL n OF ^\"%s\": ^\"%s\" is not a ^\"Die\"" % (die, die)))


def from_pass(files_data, findings):
    """FROM <KIND> "id" (§16, DECISION-22): the container exists in the loaded set and is of
    the kind named. A FROM with no kind is checked for existence only."""
    kinds = {}
    for d in files_data:
        for cid, kind in d.get('containers', {}).items():
            kinds.setdefault(cid, set()).add(kind)
    for d in files_data:
        for kind, cid, line in d.get('froms', []):
            if is_waived(line, d):
                continue
            if cid not in kinds:
                findings.append(Finding(d['file'], 'coherence', 'error', line,
                                        'FROM names "%s", and no container of that id is in the '
                                        'loaded set (§16)' % cid))
            elif kind and kind not in kinds[cid]:
                findings.append(Finding(d['file'], 'coherence', 'error', line,
                                        'FROM %s "%s": that container is %s, not %s (§16)'
                                        % (kind, cid, ' / '.join(sorted(kinds[cid])), kind)))


def port_pass(files_data, corpus_index, findings):
    """A port and its origin (§19, DECISION-26). `corpus_index` is  edition id ->
    {container id -> {'kinds', 'anchors', 'file'}}  for each --corpus given."""
    declared = {}                                   # container id -> {files that declare it}
    for d in files_data:
        for cid in d.get('containers', {}):
            declared.setdefault(cid, set()).add(d['file'])
    unchecked = {}                                  # edition id -> [(file, line)]
    for d in files_data:
        for edition, kind, cid, line in d.get('origins', []):
            others = declared.get(cid, set()) - {d['file']}
            if others:
                findings.append(Finding(d['file'], 'coherence', 'error', line,
                                        'ORIGIN names %s "%s", and %s declares it in this loaded set: '
                                        'a port and its origin are files of two editions and are not '
                                        'loaded together (§13, §19)'
                                        % (kind, cid, os.path.basename(sorted(others)[0]))))
            if edition not in corpus_index:
                unchecked.setdefault(edition, []).append((d['file'], line))
                continue
            rec = corpus_index[edition].get(cid)
            if rec is None:
                findings.append(Finding(d['file'], 'coherence', 'error', line,
                                        'ORIGIN names %s "%s", and the corpus given for edition "%s" '
                                        'has no container of that id (§19)' % (kind, cid, edition)))
                continue
            if kind not in rec['kinds']:
                findings.append(Finding(d['file'], 'coherence', 'error', line,
                                        'ORIGIN %s "%s": in edition "%s" that container is %s (§19)'
                                        % (kind, cid, edition, ' / '.join(sorted(rec['kinds'])))))
            mine = {}                               # hash -> ({names}, line)
            for h, nms in d.get('anchor_names', {}).items():
                mine[h] = (set(nms), d['anchors'].get(h, [line])[0])
            for h, decls in d.get('block_anchor_lines', {}).items():
                nms, ln = mine.get(h, (set(), decls[0][1]))
                mine[h] = (nms | {nm for nm, _ in decls}, ln)
            for h, (nms, ln) in sorted(mine.items(), key=lambda kv: kv[1][1]):
                theirs = rec['anchors'].get(h)
                if theirs and not (nms & theirs):
                    findings.append(Finding(d['file'], 'coherence', 'error', ln,
                                            'hash %s is ^"%s" here and ^"%s" in the origin (%s "%s", '
                                            'edition "%s"): a hash a port shares with its origin '
                                            'carries the same name in both (§19)'
                                            % (h, sorted(nms)[0], sorted(theirs)[0], kind, cid, edition)))
    for edition, where in sorted(unchecked.items()):
        f, line = sorted(where)[0]
        findings.append(Finding(f, 'coherence', 'warning', line,
                                'ORIGIN "%s": no corpus was given for that edition, so %d port(s) in '
                                'this run were not checked against their origin; pass '
                                '--corpus %s=<dir> (§20)' % (edition, len(where), edition)))


def value_pass(files_data, findings):
    """What a definition says against what it extends (DECISION-32).

    Errors at every version: an EXTENDS cycle (§6), an ALIAS cycle (§5b), a bound reference
    that does not fit its base's PARAMETERS (§5b).

    A warning in a file that declares SPEC_VERSION below 0.6, an error from 0.6, and waived by
    FIAT: an INTEGER outside the MIN / MAX it inherits, a value outside the ENUM it inherits,
    a value of another kind than the type declared (§5, §8), a named member of a LIST OF
    ^"Type" that is not of the type (§8), and one property written twice in a definition.

    The same gating, for REQUIRED (§8, DECISION-34): an instance that lacks a property a type
    up its chain declares REQUIRED. An instance is a DEF that extends something and is not a
    type; a type is an ACTOR or TEMPLATE definition, a DEF another DEF extends, or a DEF that
    declares fields and gives no value. The instance has the property when it writes it, when
    a type above gives it a value, when it is a PARAMETERS slot, or, for ^"Name", always: the
    DEF's own name answers.

    A name that two definitions share is not followed: §5d makes it ambiguous without a hash."""
    by_file = {d['file']: d for d in files_data}
    by_name, by_hash = {}, {}
    for d in files_data:
        for x in d.get('vdefs', []):
            if x['nested']:
                continue
            by_name.setdefault(x['name'], []).append(x)
            if x['hash']:
                by_hash.setdefault(x['hash'], []).append(x)

    def resolve(name, hsh):
        if hsh and len(by_hash.get(hsh, [])) == 1:
            return by_hash[hsh][0]
        cands = by_name.get(name, [])
        return cands[0] if len(cands) == 1 else None

    def parents(x):
        return [y for y in (resolve(nm, h) for nm, h, _ln in x['extends']) if y is not None]

    def ancestors(x):
        out, seen, todo = [], {id(x)}, parents(x)
        while todo:
            y = todo.pop(0)
            if id(y) in seen:
                continue
            seen.add(id(y))
            out.append(y)
            todo.extend(parents(y))
        return out

    def gated(x, line):
        d = by_file[x['file']]
        return None if is_waived(line, d) else ('error' if d.get('spec_version', (0, 0)) >= (0, 6) else 'warning')

    def waived(x, line):
        return is_waived(line, by_file[x['file']])

    # EXTENDS cycles (§6)
    in_cycle = set()
    for start in (x for xs in by_name.values() for x in xs):
        path, cur, seen = [start], start, {id(start)}
        while True:
            nxt = parents(cur)
            if not nxt:
                break
            cur = nxt[0]
            if cur is start:
                if id(start) not in in_cycle and not waived(start, start['line']):
                    findings.append(Finding(start['file'], 'coherence', 'error', start['line'],
                                            'EXTENDS cycle: %s (§6)'
                                            % ' → '.join('^"%s"' % y['name'] for y in path + [start])))
                in_cycle.add(id(start))
                break
            if id(cur) in seen:
                break
            seen.add(id(cur))
            path.append(cur)

    # ALIAS cycles (§5b)
    alias_to, alias_site = {}, {}
    for d in files_data:
        for alias, target, line in d.get('aliases', []):
            alias_to[alias] = target
            alias_site[alias] = (d, line)
    for alias in alias_to:
        path, cur = [alias], alias_to[alias]
        while cur in alias_to and cur not in path:
            path.append(cur)
            cur = alias_to[cur]
        if cur == alias:
            d, line = alias_site[alias]
            if not is_waived(line, d):
                findings.append(Finding(d['file'], 'coherence', 'error', line,
                                        'ALIAS cycle: %s — alias chains must be acyclic (§5b)'
                                        % ' → '.join('^"%s"' % a for a in path + [alias])))

    # bound references against PARAMETERS (§5b)
    for d in files_data:
        for b in d.get('bound', []):
            if is_waived(b['line'], d):
                continue
            base = resolve(b['base'], None)
            if base is None:
                continue
            params = base['params']
            if params is None:
                for y in ancestors(base):
                    if y['params'] is not None:
                        params = y['params']
                        break
            if params is None:
                findings.append(Finding(d['file'], 'coherence', 'error', b['line'],
                                        '^"%s" is given arguments and declares no PARAMETERS (§5b)'
                                        % b['base']))
                continue
            if b['nargs'] > len(params):
                findings.append(Finding(d['file'], 'coherence', 'error', b['line'],
                                        '^"%s" is given %d arguments and declares %d parameter(s) (§5b)'
                                        % (b['base'], b['nargs'], len(params))))
            slots = {prm['name']: prm for prm in params}
            pairs = [(params[k], v) for k, v in b['pos'] if k < len(params)] \
                + [(slots[nm], v) for nm, v in b['named'].items() if nm in slots]
            for prm, v in pairs:
                if prm['values'] is not None and v not in prm['values']:
                    findings.append(Finding(d['file'], 'coherence', 'error', b['line'],
                                            '^"%s": "%s" is not a value of ^"%s", which takes %s (§5b)'
                                            % (b['base'], v, prm['name'],
                                               ', '.join('"%s"' % o for o in prm['values']))))

    # REQUIRED (§8, DECISION-34): every instance of the type has the property. Nested
    # definitions count here: a book's entries are often written inside the DEF of their section.
    every = [x for d in files_data for x in d.get('vdefs', [])]
    all_name, all_hash = {}, {}
    for x in every:
        all_name.setdefault(x['name'], []).append(x)
        if x['hash']:
            all_hash.setdefault(x['hash'], []).append(x)

    def declares(x):
        recs = [r for rs in x['props'].values() for r in rs]
        if any(r['required'] for r in recs):
            return True
        return bool(recs) and all(r['value'] is None and r['members'] is None for r in recs)

    def own_type(x):
        return x['marker'] is not None or declares(x)

    def resolve_any(name, hsh):
        if hsh and hsh in all_hash:
            return all_hash[hsh][:1]
        cands = all_name.get(name, [])
        return ([y for y in cands if own_type(y)] or cands) if len(cands) > 1 else cands

    def all_ancestors(x):
        out, seen, todo = [], {id(x)}, list(x['extends'])
        while todo:
            nm, h, _ln = todo.pop(0)
            for y in resolve_any(nm, h):
                if id(y) not in seen:
                    seen.add(id(y))
                    out.append(y)
                    todo.extend(y['extends'])
        return out

    extended = {id(y) for x in every for nm, h, _ln in x['extends'] for y in resolve_any(nm, h)}
    for x in every:
        if not x['extends'] or own_type(x) or id(x) in extended:
            continue                                    # a type, or nothing that extends one
        sev = gated(x, x['line'])
        if not sev:
            continue                                    # an element-level FIAT waives the instance
        anc = all_ancestors(x)
        have = set(x['props']) | x['children'] | {prm['name'] for prm in (x['params'] or [])}
        for y in anc:
            have |= {prm['name'] for prm in (y['params'] or [])}
            have |= {p for p, rs in y['props'].items()
                     if any(r['value'] is not None or r['members'] is not None for r in rs)}
        reported = set()
        for y in anc:
            if not (own_type(y) or id(y) in extended):
                continue
            missing = [p for p, rs in y['props'].items()
                       if any(r['required'] for r in rs) and p not in have and p != 'Name'
                       and p not in reported]
            if missing:
                reported.update(missing)
                findings.append(Finding(x['file'], 'coherence', sev, x['line'],
                                        '^"%s" has no %s, which ^"%s" declares REQUIRED: every entry of '
                                        'a type has what the type requires (§8). An entry the source '
                                        'prints without it takes FIAT "reason"'
                                        % (x['name'], ', '.join('^"%s"' % p for p in missing), y['name'])))

    for xs in by_name.values():
        for x in xs:
            anc = ancestors(x) if id(x) not in in_cycle else []
            for prop, recs in x['props'].items():
                # one property twice in a definition
                for extra in recs[1:]:
                    sev = gated(x, extra['line'])
                    if sev:
                        findings.append(Finding(x['file'], 'coherence', sev, extra['line'],
                                                '^"%s" is written twice in ^"%s"; the first is on line %d (§8)'
                                                % (prop, x['name'], recs[0]['line'])))
                r = recs[0]
                # a named member of LIST OF ^"Type" is of the type (§8)
                if r['of'] and r['members']:
                    want = resolve(r['of'], r['of_hash'])
                    for nm, hsh, ln in r['members']:
                        m = resolve(nm, hsh)
                        if want is None or m is None or m is want or want in ancestors(m):
                            continue
                        msev = gated(x, ln)
                        if not msev:
                            continue
                        findings.append(Finding(x['file'], 'coherence', msev, ln,
                                                '^"%s" is in a LIST OF ^"%s" and is not one: it does not '
                                                'extend ^"%s" (§8)' % (nm, r['of'], r['of'])))
                if r['value'] is None:
                    continue
                sev = gated(x, r['line'])
                if not sev:
                    continue
                if VALUE_FAMILY.get(r['type']) and TOKEN_FAMILY[r['vkind']] != VALUE_FAMILY[r['type']]:
                    findings.append(Finding(x['file'], 'coherence', sev, r['line'],
                                            '^"%s" %s is given a %s value (§8)'
                                            % (prop, r['type'], TOKEN_FAMILY[r['vkind']])))
                    continue
                decl = None
                for y in anc:
                    for cand in y['props'].get(prop, []):
                        if cand['value'] is None:
                            decl = (y, cand)
                            break
                    if decl:
                        break
                if decl is None:
                    continue
                owner, dr = decl
                if dr['type'] == 'INTEGER' and r['vkind'] == 'INT':
                    v = int(r['value'])
                    if (dr['min'] is not None and v < dr['min']) or (dr['max'] is not None and v > dr['max']):
                        lim = ' and '.join(b for b in ('MIN %d' % dr['min'] if dr['min'] is not None else '',
                                                       'MAX %d' % dr['max'] if dr['max'] is not None else '') if b)
                        findings.append(Finding(x['file'], 'coherence', sev, r['line'],
                                                '^"%s" is %d; ^"%s" declares it %s (§5, §8). A value the '
                                                'source prints outside the range takes FIAT "reason"'
                                                % (prop, v, owner['name'], lim)))
                elif dr['enum'] is not None and r['vkind'] == 'STR' and r['value'] not in dr['enum']:
                    findings.append(Finding(x['file'], 'coherence', sev, r['line'],
                                            '^"%s" is "%s"; ^"%s" declares it ENUM [%s] (§8)'
                                            % (prop, r['value'], owner['name'],
                                               ', '.join('"%s"' % o for o in dr['enum'][:8])
                                               + (', …' if len(dr['enum']) > 8 else ''))))
                elif VALUE_FAMILY.get(dr['type']) and VALUE_FAMILY.get(r['type']) \
                        and VALUE_FAMILY[dr['type']] != VALUE_FAMILY[r['type']]:
                    findings.append(Finding(x['file'], 'coherence', sev, r['line'],
                                            '^"%s" is written %s; ^"%s" declares it %s (§8)'
                                            % (prop, r['type'], owner['name'], dr['type'])))


def block_type_pass(files_data, findings):
    """TYPE of a SCENE or a CONFLICT (§16, DECISION-23). Where the loaded set defines ^"Scene Type"
    (or ^"Conflict Type"), the entity named must be one: it, or something that EXTENDS it. Where
    the parent is not defined the reference is resolved and nothing more is checked."""
    parent = {'SCENE': 'Scene Type', 'CONFLICT': 'Conflict Type'}
    extends, known = {}, set()
    for d in files_data:
        if d.get('kind') != 'ttrpg':
            continue
        known.update(d['names'])
        for nm, parents in d['def_extends'].items():
            extends.setdefault(nm, []).extend(parents)

    def is_a(entity, ty, seen):
        if entity == ty:
            return True
        if entity in seen:
            return False
        seen.add(entity)
        return any(is_a(p, ty, seen) for p in extends.get(entity, ()))

    for d in files_data:
        for kw, entity, line in d.get('block_types', []):
            ty = parent[kw]
            if ty in known and entity in known and not is_a(entity, ty, set()) and not is_waived(line, d):
                findings.append(Finding(d['file'], 'coherence', 'error', line,
                                        'TYPE ^"%s": a %s takes a ^"%s", and ^"%s" is not one (§16)'
                                        % (entity, kw, ty, entity)))


def table_pass(files_data, findings):
    """TABLE (§5e, DECISION-21): an entity given as a coordinate on an axis OF ^"Type" is of
    that type, and each of a record table's COLUMNS is a property the axis type declares, its
    own or inherited."""
    props, extends, known = {}, {}, set()
    for d in files_data:
        if d.get('kind') != 'ttrpg':
            continue
        known.update(d['names'])
        for nm, table in d['def_props'].items():
            props.setdefault(nm, {}).update(table)
        for nm, parents in d['def_extends'].items():
            extends.setdefault(nm, []).extend(parents)

    def is_a(entity, ty, seen):
        if entity == ty:
            return True
        if entity in seen:
            return False
        seen.add(entity)
        return any(is_a(parent, ty, seen) for parent in extends.get(entity, ()))

    for d in files_data:
        if d.get('kind') != 'ttrpg':
            continue
        for tbl in d.get('tables', []):
            for entity, ty, line in tbl.get('typed', []):
                if entity in known and ty in known and not is_a(entity, ty, set()) \
                        and not is_waived(line, d):
                    findings.append(Finding(d['file'], 'coherence', 'error', line,
                                            'coordinate ^"%s" is on an axis OF ^"%s" and is not one '
                                            '(§5e)' % (entity, ty)))
            if tbl.get('columns') and len(tbl['axes']) == 1 and tbl['axes'][0].get('type') in known:
                ty = tbl['axes'][0]['type']
                for col, line in tbl['columns'][0]:
                    if _resolve_prop(ty, col, props, extends) is None and not is_waived(line, d):
                        findings.append(Finding(d['file'], 'coherence', 'error', line,
                                                'COLUMNS names ^"%s", which ^"%s" does not declare '
                                                '(its own properties or inherited) (§5e)' % (col, ty)))


def modification_pass(files_data, findings):
    """Coherence for the §13 modification system.

    Target resolution itself rides on the ordinary reference machinery (the
    'modify target' / 'override target' refs raised in analyze_file), so it is checked
    — and FIAT-waivable — exactly like EXTENDS. What is left for this pass is what
    happens *inside* a MODIFY, and whether an ADD is really adding anything."""
    props, extends, name_sites, by_file = {}, {}, {}, {}
    for d in files_data:
        if d.get('kind') != 'ttrpg':
            continue
        by_file[d['file']] = d
        for nm, table in d['def_props'].items():
            bucket = props.setdefault(nm, {})
            for pname, rec in table.items():
                rec = dict(rec, file=d['file'])
                bucket.setdefault(pname, rec)   # the first declaration is the prior one
        for nm, parents in d['def_extends'].items():
            extends.setdefault(nm, []).extend(parents)
        for nm, lines in d['names'].items():
            for ln in lines:
                name_sites.setdefault(nm, []).append((d['file'], ln))

    # every ALIAS declaration site, so an alias is never mistaken for the DEF it collides with
    alias_sites = {(d['file'], ln) for d in files_data if d.get('kind') == 'ttrpg'
                   for _a, _t, ln in d.get('aliases', [])}

    children = {}
    for child, parents in extends.items():
        for parent in parents:
            children.setdefault(parent, []).append(child)

    for d in files_data:
        if d.get('kind') != 'ttrpg':
            continue
        for m in d['mods']:
            tgt = m['target']
            if tgt not in name_sites:
                continue        # unresolvable target: already reported, once, as a ref
            for op in m['ops']:
                if is_waived(op['line'], d):
                    continue
                if op['op'] == 'SET DESCRIPTION':
                    if not op['ok']:
                        findings.append(Finding(
                            d['file'], 'lint', 'error', op['line'],
                            "SET DESCRIPTION must be followed by the variant's text as a "
                            "string (§13, v0.5 addendum)"))
                    continue
                rec = _resolve_prop(tgt, op['prop'], props, extends)
                if op['op'] == 'SET':
                    if rec is None:
                        findings.append(Finding(
                            d['file'], 'coherence', 'error', op['line'],
                            "SET names ^\"%s\", which ^\"%s\" does not declare (directly or "
                            "through EXTENDS) — a MODIFY that introduces a new property "
                            "declares it in a PROPERTIES block (§13)" % (op['prop'], tgt)))
                        continue
                    widened = op['rec']['enum'] if op['rec'] else None
                    if widened is None or not rec.get('enum'):
                        continue
                    dropped = [v for v in rec['enum'] if v not in widened]
                    if not dropped:
                        continue
                    # Narrowing an enum is legal; orphaning a live instance with it is not.
                    for inst in sorted(_descendants(tgt, children)):
                        irec = props.get(inst, {}).get(op['prop'])
                        if irec is None or irec.get('value') not in dropped:
                            continue
                        di = by_file.get(irec['file'])
                        if di is not None and is_waived(irec['line'], di):
                            continue
                        findings.append(Finding(
                            irec['file'], 'coherence', 'warning', irec['line'],
                            "^\"%s\" assigns ^\"%s\" = \"%s\", which %s:%d drops from the enum"
                            % (inst, op['prop'], irec['value'],
                               os.path.basename(d['file']), op['line'])))
                elif rec is None:
                    findings.append(Finding(
                        d['file'], 'coherence', 'error', op['line'],
                        "%s names ^\"%s\", which ^\"%s\" does not declare (directly or through "
                        "EXTENDS)" % (op['op'], op['prop'], tgt)))
                elif not rec['is_list']:
                    findings.append(Finding(
                        d['file'], 'coherence', 'error', op['line'],
                        "%s ^\"%s\": ^\"%s\" declares it %s, not a LIST"
                        % (op['op'], op['prop'], tgt, rec['type'])))
                elif op['op'] == 'REMOVE_FROM' and rec.get('members') is not None \
                        and op['value'] is not None and op['value'] not in rec['members']:
                    # A warning, not an error: an earlier layer's ADD_TO may legitimately
                    # have put the value there (§13 Composition & Precedence).
                    findings.append(Finding(
                        d['file'], 'coherence', 'warning', op['line'],
                        "REMOVE_FROM ^\"%s\" removes \"%s\", which ^\"%s\" does not list"
                        % (op['prop'], op['value'], tgt)))

        for alias, target, line in d.get('aliases', []):
            if is_waived(line, d) or alias == target:
                continue
            # §5b: "an alias name must not already name a *different* entity"
            owners = [(f, ln) for f, ln in name_sites.get(alias, [])
                      if (f, ln) not in alias_sites]
            if owners:
                where = ", ".join("%s:%d" % (os.path.basename(f), ln) for f, ln in owners)
                findings.append(Finding(
                    d['file'], 'coherence', 'error', line,
                    "ALIAS ^\"%s\" names an entity already defined (%s) — an alias name must not "
                    "already name a different entity (§5b)" % (alias, where)))

        for nm, line in d.get('reprints', []):
            if is_waived(line, d):
                continue
            if nm in d['names']:
                findings.append(Finding(
                    d['file'], 'coherence', 'error', line,
                    "REPRINT ^\"%s\" in a file that also defines it — a reprint points at an "
                    "entity defined elsewhere (§5b, DECISION-14)" % nm))

        for nm, line in d['adds']:
            if is_waived(line, d):
                continue
            others = [(f, ln) for f, ln in name_sites.get(nm, [])
                      if not (f == d['file'] and ln == line)]
            if not others:
                continue
            where = ", ".join("%s:%d" % (os.path.basename(f), ln) for f, ln in others)
            findings.append(Finding(
                d['file'], 'coherence', 'warning', line,
                "ADD ^\"%s\" introduces content the corpus already defines (%s) — say "
                "OVERRIDE or MODIFY if replacing it is the intent (§13)" % (nm, where)))


def _all_hashes(files_data):
    out = set()
    for d in files_data:
        out.update(d['anchors'].keys())
        out.update(d.get('block_anchors', {}).keys())
    return out


def collect_paths(args):
    files = []
    exts = ('.ttrpg', '.actor', '.arc', '.frame', '.setting', '.campaign', '.bridge', '.codex')
    for p in args:
        if os.path.isdir(p):
            for root, _, names in os.walk(p):
                for nm in names:
                    if nm.endswith(exts):
                        files.append(os.path.join(root, nm))
        elif p.endswith(exts):
            files.append(p)
        else:
            print("skipping non-DSL path: %s" % p, file=sys.stderr)
    return sorted(files)


def main(argv):
    args, corpus_args = [], []
    it = iter(argv[1:])
    for a in it:
        if a == '--corpus':
            corpus_args.append(next(it, ''))
        elif a.startswith('--corpus='):
            corpus_args.append(a.split('=', 1)[1])
        else:
            args.append(a)
    if not args:
        print(__doc__.strip().splitlines()[0])
        print("usage: ttrpg_validator.py <file-or-dir> [more ...] [--corpus <edition>=<dir> ...]",
              file=sys.stderr)
        return 2
    paths = collect_paths(args)
    if not paths:
        print("no .ttrpg files found", file=sys.stderr)
        return 2

    corpora, corpus_index = {}, {}
    for spec in corpus_args:
        if '=' not in spec:
            print("--corpus expects <edition>=<dir>, got %r" % spec, file=sys.stderr)
            return 2
        ed, d = spec.split('=', 1)
        if not os.path.isdir(d):
            print("--corpus %s: not a directory: %s" % (ed, d), file=sys.stderr)
            return 2
        corpus_index[ed] = {}
        corpora[ed] = load_corpus_names(d, corpus_index[ed])

    findings, files_data, notes = [], [], []
    for path in paths:
        try:
            with open(path, encoding='utf-8') as fh:
                text = fh.read()
        except OSError as exc:
            print("cannot read %s: %s" % (path, exc), file=sys.stderr)
            return 2
        files_data.append(analyze_file(path, text, findings))
    coherence_pass(files_data, findings)
    choose_pass(files_data, findings)
    ref_pass(files_data, findings)
    roll_pass(files_data, findings)
    table_pass(files_data, findings)
    from_pass(files_data, findings)
    block_type_pass(files_data, findings)
    port_pass(files_data, corpus_index, findings)
    value_pass(files_data, findings)
    modification_pass(files_data, findings)
    bridge_coherence(files_data, corpora, findings, notes)

    findings.sort(key=lambda f: (f.file, f.line, f.level, f.sev))
    errors = sum(1 for f in findings if f.sev == 'error')
    warnings = sum(1 for f in findings if f.sev == 'warning')
    cur = None
    for f in findings:
        if f.file != cur:
            cur = f.file
            print("\n%s" % f.file)
        print("  %-10s %-5s L%-4d %s" % (f.level, f.sev.upper(), f.line, f.msg))
    if corpora:
        print("\ncorpora loaded: " + ", ".join(
            "%s (%d names)" % (k, len(v)) for k, v in sorted(corpora.items())))
    for note in notes:
        print("  note: %s" % note)
    print("\n%d file(s) checked — %d error(s), %d warning(s)." % (len(paths), errors, warnings))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
