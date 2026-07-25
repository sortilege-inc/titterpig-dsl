#!/usr/bin/env python3
"""
Titterpig DSL v4 validator.

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
    - DECISION-6: bound-ref bases & arguments, PARAMETERS OF types, CHOICE
      options, and ALIAS FOR targets all resolve (an ALIAS name is itself a
      resolvable name)

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

    ttrpg_validator.py bridges/0.4/ --corpus dnd5e=<dir> --corpus dnd5.5e=<dir>

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
from dataclasses import dataclass

HASH_MIN_BODY = 16


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
            if not nm.endswith(('.ttrpg', '.actor', '.setting', '.arc', '.frame', '.campaign')):
                continue
            p = os.path.join(root, nm)
            try:
                with open(p, encoding='utf-8') as fh:
                    data = analyze_file(p, fh.read(), scratch)
            except OSError:
                continue
            names.update(data['names'])
    return names


def analyze_file(fname, text, findings):
    if fname.endswith('.bridge'):
        return analyze_bridge(fname, text, findings)
    toks = tokenize(text, fname, findings)
    defined_names, anchors = {}, {}     # name/hash -> [lines]
    refs, depends, file_ids = [], [], []
    has_spec_version = False
    frames = []                          # {open, is_def, waived}
    waived_ranges, waived_lines = [], set()
    next_lbrace_is_def = False

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
            frames.append({'open': t.line, 'is_def': next_lbrace_is_def, 'waived': False})
            next_lbrace_is_def = False
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
        elif w == 'EXTENDS':
            k = idx + 1
            hsh = None
            if k < len(toks) and toks[k].kind == 'HASH':
                hsh = toks[k].val; k += 1
            if k < len(toks) and toks[k].kind == 'CARET':
                refs.append(('extends', toks[k].val, hsh, t.line))
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
        elif w == 'CHOICE':
            # CHOICE [ options ]  (DECISION-6): option/slot-type carets must
            # resolve; carets inside a WHERE { } are field names (local, skipped).
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

    for h, locs in all_anchors.items():
        if len(locs) > 1:
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
            if name not in corpus_names and not is_waived(line, d):
                findings.append(Finding(d['file'], 'coherence', 'error', line,
                                        "%s references undefined ^\"%s\"" % (kind, name)))
            if hsh and hsh not in d['anchors'] and hsh not in {a for a in _all_hashes(files_data)} \
               and not is_waived(line, d):
                findings.append(Finding(d['file'], 'coherence', 'error', line,
                                        "extends references undefined hash %s" % hsh))
        for fid, line in d['depends']:
            if fid not in corpus_file_ids and not is_waived(line, d):
                findings.append(Finding(d['file'], 'coherence', 'error', line,
                                        "DEPENDS_ON references undefined file id \"%s\"" % fid))


def _all_hashes(files_data):
    out = set()
    for d in files_data:
        out.update(d['anchors'].keys())
    return out


def collect_paths(args):
    files = []
    exts = ('.ttrpg', '.actor', '.arc', '.frame', '.setting', '.campaign', '.bridge')
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
