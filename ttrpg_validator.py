#!/usr/bin/env python3
"""
Titterpig DSL validator (v0.5, with the v0.6 working-draft CHOOSE construct).

Two levels of validation over one or more .ttrpg files (or directories):

  LINT (spec adherence, per file)
    - lexical correctness + brace/bracket balance
    - hash IDs are >= 16 characters
    - FIAT requires a reason string
    - SPEC_VERSION is declared
    - an inline INTEGER value lies within a same-declaration MIN/MAX

  COHERENCE (referential integrity, across the whole corpus)
    - no duplicate definition anchors (#hash)
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
NOT waive structural/lexical lint (unbalanced braces, a missing reason, etc.).

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

Usage:  ttrpg_validator.py <file-or-dir> [more ...] [--corpus <edition>=<dir> ...]
Exit:   0 = no errors (warnings allowed); 1 = one or more errors; 2 = bad invocation.
"""
from __future__ import annotations
import sys
import os
import re
from dataclasses import dataclass

HASH_MIN_BODY = 16

# Property types the spec declares (§8). A caret followed by one of these inside a
# PROPERTIES block is a property declaration; anything else is not.
PROP_TYPE_KW = ('STRING', 'INTEGER', 'BOOLEAN', 'ENUM', 'LIST', 'DEF', 'TEXT', 'REF')

# What may open the statement AFTER a `REF [OF ^"Type"]`: a reference followed by one of
# these belongs to that next statement and is not the REF's value (§8, DECISION-17).
NEXT_STATEMENT_KW = PROP_TYPE_KW + ('CHOOSE', 'SET', 'TRANSFORM', 'MODIFY')
CHANGE_METHODS = ('ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE')


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
                if text[j] == '\n':
                    line += 1
                j += 1
            if j >= n:
                findings.append(Finding(fname, 'lint', 'error', start, "unterminated caret reference"))
                break
            toks.append(Tok('CARET', text[i + 2:j], start)); i = j + 1; continue
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


def load_corpus_names(path):
    """Every ^"Name" / ACTOR / TEMPLATE / ALIAS name defined in an edition corpus."""
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
    next_lbrace_is_modify = False

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
            frames.append({'open': t.line, 'is_def': next_lbrace_is_def, 'waived': False,
                           'def_name': next_lbrace_def_name, 'is_modify': next_lbrace_is_modify})
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
        elif w == 'SPEC_VERSION':
            has_spec_version = True
        elif w == 'DEF':
            k = idx - 1
            if k >= 0 and toks[k].kind in ('CARET', 'STR'):
                name = toks[k].val; k -= 1
                if k >= 0 and toks[k].kind == 'ID' and toks[k].val in ('ACTOR', 'TEMPLATE'):
                    k -= 1
                hsh = toks[k].val if k >= 0 and toks[k].kind == 'HASH' else None
                defined_names.setdefault(name, []).append(t.line)
                if hsh:
                    anchors.setdefault(hsh, []).append(t.line)
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
            if named and rty is not None and toks[idx - 1].val == rty:
                findings.append(Finding(fname, 'lint', 'warning', t.line,
                                        "^\"%s\" REF OF ^\"%s\" writes the name twice: "
                                        "REF OF ^\"%s\" declares the same property (§8)" % (rty, rty, rty)))
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
            if isinstance(tgt, tuple):
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
    for tk in toks:
        if tk.kind == 'HASH' and len(tk.val) - 1 < HASH_MIN_BODY:
            findings.append(Finding(fname, 'lint', 'warning', tk.line,
                                    "hash id '%s' shorter than %d chars" % (tk.val, HASH_MIN_BODY)))
    if not has_spec_version and not fname.endswith('.actor'):
        # .actor files are bare single-DEF fragments with no metadata wrapper
        findings.append(Finding(fname, 'lint', 'warning', 1, "no SPEC_VERSION declared"))

    return {
        'file': fname, 'kind': 'ttrpg', 'names': defined_names, 'anchors': anchors, 'refs': refs,
        'depends': depends, 'file_ids': file_ids,
        'waived_ranges': waived_ranges, 'waived_lines': waived_lines,
        'def_props': def_props, 'def_extends': def_extends, 'mods': mods, 'adds': adds,
        'reprints': reprints, 'aliases': aliases, 'chooses': chooses, 'ref_values': ref_values,
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

    # A codex ENTITY anchor may recur across section files as an amend (§13): a
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
                                    "duplicate anchor %s (%s)" % (h, where)))

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
            if name not in corpus_names and not is_waived(line, d):
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

    corpora = {}
    for spec in corpus_args:
        if '=' not in spec:
            print("--corpus expects <edition>=<dir>, got %r" % spec, file=sys.stderr)
            return 2
        ed, d = spec.split('=', 1)
        if not os.path.isdir(d):
            print("--corpus %s: not a directory: %s" % (ed, d), file=sys.stderr)
            return 2
        corpora[ed] = load_corpus_names(d)

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
