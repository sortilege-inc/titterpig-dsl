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

FIAT: a value or element marked  FIAT "reason"  is exempt from the COHERENCE and
inline-range findings it would otherwise raise. An element-level FIAT (a `FIAT "reason"`
statement alone on a line in a DEF body) cascades over that DEF's whole subtree; a
property-level FIAT (trailing a property declaration) waives just that line. FIAT does
NOT waive structural/lexical lint (unbalanced braces, a missing reason, etc.).

Usage:  ttrpg_validator.py <file-or-dir> [more ...]
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
        simple = {'{': 'LBRACE', '}': 'RBRACE', '[': 'LBRACK', ']': 'RBRACK', ',': 'COMMA', ':': 'COLON'}
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


def analyze_file(fname, text, findings):
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
        'file': fname, 'names': defined_names, 'anchors': anchors, 'refs': refs,
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
    exts = ('.ttrpg', '.actor', '.arc')
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
    if len(argv) < 2:
        print(__doc__.strip().splitlines()[0])
        print("usage: ttrpg_validator.py <file-or-dir> [more ...]", file=sys.stderr)
        return 2
    paths = collect_paths(argv[1:])
    if not paths:
        print("no .ttrpg files found", file=sys.stderr)
        return 2

    findings, files_data = [], []
    for path in paths:
        try:
            with open(path, encoding='utf-8') as fh:
                text = fh.read()
        except OSError as exc:
            print("cannot read %s: %s" % (path, exc), file=sys.stderr)
            return 2
        files_data.append(analyze_file(path, text, findings))
    coherence_pass(files_data, findings)

    findings.sort(key=lambda f: (f.file, f.line, f.level, f.sev))
    errors = sum(1 for f in findings if f.sev == 'error')
    warnings = sum(1 for f in findings if f.sev == 'warning')
    cur = None
    for f in findings:
        if f.file != cur:
            cur = f.file
            print("\n%s" % f.file)
        print("  %-10s %-5s L%-4d %s" % (f.level, f.sev.upper(), f.line, f.msg))
    print("\n%d file(s) checked — %d error(s), %d warning(s)." % (len(paths), errors, warnings))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
