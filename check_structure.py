#!/usr/bin/env python3
"""DSL 0.5 gate for STRUCTURE — the thing no other gate measures.

The validator asks whether a file is well-formed. `coverageAudit.ts` asks whether
every source unit is represented. The verbatim QA asks whether the text is the book's.
A corpus of heading-shaped prose blobs answers yes to all three and is still unusable:
coyotecrow shipped 2026-09-22 with 561 DEFs carrying 39 PROPERTIES blocks against 451
DESCRIPTION blobs, and every gate passed.

Two checks:

  1. SHAPE     DESCRIPTION must not outnumber PROPERTIES. When it does, the mechanics
               are in prose and the conversion is not done.
  2. REQUIRED  A property a type declares REQUIRED, populated on ZERO instances of that
               type, is a modelling error announcing itself -- it is usually not an
               oversight but a sign the type is the wrong shape (coyotecrow declared
               `Kind ENUM ["Gift","Burden"] REQUIRED` for a book that enumerates
               eleven kinds, each available either way).

What is a type and what is an instance (spec §5 "Definitions vs. Instances"), read from
the DEF itself rather than from the file it sits in:

  - a TYPE is an ACTOR DEF; a root DEF in a BASE; a DEF whose PROPERTIES declare
    (fields with no values, or any REQUIRED field); or a DEF another DEF EXTENDS.
    A subtype declared in an EXTENSION is a type, not an instance of its parent.
  - an INSTANCE is any other DEF that EXTENDS something. It counts against every type
    up its EXTENDS chain, so an instance of a subtype answers the supertype's REQUIRED.

An instance fills a REQUIRED property when it carries the property; when a type above
it fixes a value for it; when it binds it as a PARAMETERS slot (§5b, the reference site
supplies it); or, for ^"Name", by its DEF header -- the spec's own instance (Ide Tadaji)
is named only there. An element-level FIAT waives the instance (§8).

    python3 check_structure.py <dir> [--min-ratio 1.0]
"""
import collections, glob, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ttrpg_validator import tokenize, PROP_TYPE_KW   # one tokenizer for every gate

EXTS = ('.ttrpg', '.actor', '.arc', '.frame', '.setting', '.campaign', '.codex')
VALUES = ('STR', 'INT', 'BOOL')


def files(d):
    return sorted(p for p in glob.glob(os.path.join(d, '**', '*'), recursive=True)
                  if os.path.isfile(p) and p.endswith(EXTS))


# --- the DEF tree -----------------------------------------------------------------

def _close(toks, j):
    """toks[j] opens a bracket; the index of its partner."""
    o = toks[j].kind
    c = {'LBRACE': 'RBRACE', 'LBRACK': 'RBRACK', 'LPAREN': 'RPAREN'}[o]
    d = 0
    for k in range(j, len(toks)):
        if toks[k].kind == o:
            d += 1
        elif toks[k].kind == c:
            d -= 1
            if d == 0:
                return k
    return len(toks) - 1


def parse_prop(toks, k, end):
    """toks[k] is the caret naming a property. Consume one §8 statement -- type, value,
    modifiers -- and say whether it declares a field or carries a value."""
    rec = {'required': False, 'declared': False, 'value': False}
    at = lambda i, kind, val=None: i < end and toks[i].kind == kind \
        and (val is None or toks[i].val == val)
    j = k + 1
    if at(j, 'ID') and toks[j].val in PROP_TYPE_KW:
        ty = toks[j].val
        j += 1
        if ty == 'DEF':
            if at(j, 'LBRACE'):
                rb = _close(toks, j)
                rec['value'] = any(t.kind in VALUES for t in toks[j + 1:rb])
                rec['declared'] = not rec['value']
                j = rb + 1
        elif ty == 'ENUM':
            if at(j, 'LBRACK'):
                j = _close(toks, j) + 1
                if at(j, 'STR'):            # ENUM ["A", "B"] "A": the set, then the value
                    j += 1
                    rec['value'] = True
                else:
                    rec['declared'] = True
            elif at(j, 'STR'):
                j += 1
                rec['value'] = True
        elif ty == 'LIST':
            if at(j, 'ID', 'OF'):
                j += 1
                if at(j, 'HASH'):
                    j += 1
                if at(j, 'CARET') or at(j, 'ID'):
                    j += 1
            if at(j, 'LBRACK'):
                j = _close(toks, j) + 1
                rec['value'] = True
            else:
                rec['declared'] = True
        else:
            want = {'INTEGER': 'INT', 'BOOLEAN': 'BOOL'}.get(ty, 'STR')
            if at(j, want) or (ty == 'BOOLEAN' and at(j, 'ID') and toks[j].val in ('TRUE', 'FALSE')):
                j += 1
                rec['value'] = True
            else:
                rec['declared'] = True
    else:
        # value forms: ^"P" ^"Ref", ^"P" #hash ^"Type" [ ... ], ^"P" "x", ^"P" [ ... ]
        if at(j, 'HASH'):
            j += 1
        if at(j, 'CARET'):
            j += 1
            if at(j, 'LPAREN'):
                j = _close(toks, j) + 1
        elif at(j, 'STR') or at(j, 'INT') or at(j, 'BOOL'):
            j += 1
        if at(j, 'LBRACK'):
            j = _close(toks, j) + 1
        rec['value'] = j > k + 1
    while j < end:                          # REQUIRED FIXED DEFAULT x MIN n MAX n FIAT "r"
        t = toks[j]
        if t.kind == 'ID' and t.val in ('REQUIRED', 'FIXED'):
            rec['required'] |= t.val == 'REQUIRED'
            j += 1
        elif t.kind == 'ID' and t.val in ('DEFAULT', 'MIN', 'MAX', 'FIAT') and j + 1 < end:
            j += 2
        else:
            break
    return rec, max(j, k + 1)


def parse_defs(path, text):
    """Every DEF in a file, nested ones included: its header, what it EXTENDS, its
    properties, its PARAMETERS slots, and whether a FIAT waives it."""
    toks = tokenize(text, path, [])
    is_base = bool(toks) and toks[0].kind == 'ID' and toks[0].val == 'BASE'
    defs = []

    def header(j, lo):
        """toks[j] is DEF before '{': the DEF's record, or None for an unnamed DEF."""
        k = j - 1
        if k < lo or toks[k].kind not in ('CARET', 'STR'):
            return None
        d = {'name': toks[k].val, 'marker': None, 'hash': None, 'file': path,
             'line': toks[j].line, 'base': is_base, 'extends': [], 'props': {},
             'params': set(), 'fiat': False}
        k -= 1
        if k >= lo and toks[k].kind == 'ID' and toks[k].val in ('ACTOR', 'TEMPLATE'):
            d['marker'] = toks[k].val
            k -= 1
        if k >= lo and toks[k].kind == 'HASH':
            d['hash'] = toks[k].val
        return d

    def walk(lo, hi):
        j = lo
        while j < hi:
            if toks[j].kind == 'ID' and toks[j].val == 'DEF' and j + 1 < hi \
                    and toks[j + 1].kind == 'LBRACE':
                rb = _close(toks, j + 1)
                d = header(j, lo)
                if d:
                    defs.append(d)
                    body(j + 2, rb, d)
                else:
                    walk(j + 2, rb)
                j = rb + 1
                continue
            j += 1

    def body(lo, hi, d):
        j, depth = lo, 0
        while j < hi:
            t = toks[j]
            if t.kind == 'LBRACE':
                depth += 1
            elif t.kind == 'RBRACE':
                depth -= 1
            elif t.kind == 'ID' and t.val == 'DEF' and j + 1 < hi and toks[j + 1].kind == 'LBRACE':
                rb = _close(toks, j + 1)
                walk(max(lo, j - 3), rb + 1)          # a nested DEF, with its header
                j = rb + 1
                continue
            elif depth == 0 and t.kind == 'ID':
                if t.val == 'EXTENDS':
                    k = j + 1
                    h = None
                    if k < hi and toks[k].kind == 'HASH':
                        h = toks[k].val
                        k += 1
                    if k < hi and toks[k].kind == 'CARET':
                        d['extends'].append((h, toks[k].val))
                    j = k + 1
                    continue
                if t.val == 'FIAT' and toks[j - 1].line != t.line:
                    d['fiat'] = True
                if t.val in ('PROPERTIES', 'PARAMETERS') and j + 1 < hi and toks[j + 1].kind == 'LBRACE':
                    rb = _close(toks, j + 1)
                    k = j + 2
                    while k < rb:
                        if toks[k].kind != 'CARET':
                            k += 1
                        elif t.val == 'PARAMETERS':
                            if toks[k + 1].kind == 'ID' and toks[k + 1].val == 'OF':
                                d['params'].add(toks[k].val)
                            k += 1
                        else:
                            rec, k2 = parse_prop(toks, k, rb)
                            d['props'][toks[k].val] = rec
                            walk(k + 1, k2)           # DEFs listed inside a property
                            k = k2
                    j = rb + 1
                    continue
            elif depth == 0 and t.kind == 'CARET' and toks[j - 1].line != t.line \
                    and j + 1 < hi and toks[j + 1].kind == 'ID' \
                    and toks[j + 1].val in PROP_TYPE_KW and toks[j + 1].val != 'DEF':
                rec, j = parse_prop(toks, j, hi)      # a property set in the DEF body
                d['props'].setdefault(t.val, rec)
                continue
            j += 1

    walk(0, len(toks))
    return defs


# --- check 2 ----------------------------------------------------------------------

def check_required(texts):
    defs = [d for p, t in texts.items() for d in parse_defs(p, t)]
    by_hash, by_name = {}, collections.defaultdict(list)
    for d in defs:
        by_name[d['name']].append(d)
        if d['hash']:
            by_hash.setdefault(d['hash'], d)

    def declares(d):
        ps = d['props'].values()
        if any(r['declared'] and r['required'] for r in ps):
            return True                     # an instance never declares a REQUIRED field
        return any(r['declared'] for r in ps) and not any(r['value'] for r in ps)

    def own_evidence(d):
        return d['marker'] == 'ACTOR' or (d['base'] and not d['extends']) or declares(d)

    def resolve(h, n):
        # §5d: the hash is the referent; a hashless name naming several DEFs means
        # the ones that are types on their own evidence
        if h and h in by_hash:
            return [by_hash[h]]
        c = by_name.get(n, [])
        return ([d for d in c if own_evidence(d)] or c) if len(c) > 1 else c

    extended = {id(p) for d in defs for h, n in d['extends'] for p in resolve(h, n)}

    def is_type(d):
        return own_evidence(d) or id(d) in extended

    def ancestors(d):
        seen, todo, out = set(), list(d['extends']), []
        while todo:
            for p in resolve(*todo.pop(0)):
                if id(p) not in seen:
                    seen.add(id(p))
                    out.append(p)
                    todo.extend(p['extends'])
        return out

    required = collections.defaultdict(list)            # type name -> [property]
    for d in defs:
        if is_type(d):
            for pn, r in d['props'].items():
                if r['required'] and pn not in required[d['name']]:
                    required[d['name']].append(pn)

    inst = collections.Counter()
    filled = collections.defaultdict(collections.Counter)
    counted = set()
    for d in defs:
        if is_type(d) or not d['extends'] or d['fiat']:
            continue
        key = d['hash'] or (d['file'], d['line'])
        anc = ancestors(d)
        for ty in dict.fromkeys(a['name'] for a in anc):
            if ty not in required or (key, ty) in counted:
                continue
            counted.add((key, ty))
            inst[ty] += 1
            for pn in required[ty]:
                if pn in d['props'] or pn in d['params'] or pn == 'Name' \
                        or any(pn in a['params'] or a['props'].get(pn, {}).get('value')
                               for a in anc):
                    filled[ty][pn] += 1
    return required, inst, filled


def main():
    d = sys.argv[1]
    min_ratio = 1.0
    if '--min-ratio' in sys.argv:
        min_ratio = float(sys.argv[sys.argv.index('--min-ratio') + 1])
    texts = {p: open(p, encoding='utf-8', errors='replace').read() for p in files(d)}
    blob = '\n'.join(texts.values())

    n_prop = len(re.findall(r'^\s*PROPERTIES\s*\{', blob, re.M))
    n_desc = len(re.findall(r'^\s*DESCRIPTION\s', blob, re.M)) \
        + len(re.findall(r'^\s*\^"Description"\s+STRING\s', blob, re.M))
    n_def = len(re.findall(r'DEF\s*\{', blob))
    n_table = len(re.findall(r'\bTABLE\s*\{', blob))
    n_list = len(re.findall(r'\bLIST OF\b', blob))
    n_empty = len(re.findall(r'DEF\s*\{\s*\}', blob))
    ratio = n_prop / n_desc if n_desc else float('inf')

    errs = []
    required, inst, filled = check_required(texts)

    print(f'STRUCTURE: {len(texts)} file(s) | {n_def} DEF | {n_prop} PROPERTIES | '
          f'{n_desc} DESCRIPTION | ratio {ratio:.1f} | {n_table} TABLE | '
          f'{n_list} LIST OF | {n_empty} empty DEF')
    if ratio < min_ratio:
        errs.append(f'SHAPE: {n_desc} DESCRIPTION vs {n_prop} PROPERTIES '
                    f'(ratio {ratio:.2f} < {min_ratio}) — the mechanics are in prose')
    for ty, props in sorted(required.items()):
        if not inst[ty]:
            continue
        for prop in props:
            got = filled[ty][prop]
            if got == 0:
                errs.append(f'REQUIRED: ^"{prop}" is REQUIRED on ^"{ty}" and populated '
                            f'on 0 of {inst[ty]} instances')
            elif got < inst[ty]:
                print(f'   note: ^"{ty}".^"{prop}" REQUIRED, on {got}/{inst[ty]}')
    for e in errs:
        print(f'  ERROR {e}')
    print(f'STRUCTURE GATE: {"FAIL" if errs else "PASS"}')
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())
