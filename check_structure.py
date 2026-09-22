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
  2. REQUIRED  A property a BASE declares REQUIRED, populated on ZERO instances of its
               type, is a modelling error announcing itself -- it is usually not an
               oversight but a sign the type is the wrong shape (coyotecrow declared
               `Kind ENUM ["Gift","Burden"] REQUIRED` for a book that enumerates
               eleven kinds, each available either way).

    python3 check_structure.py <dir> [--min-ratio 1.0]
"""
import collections, glob, os, re, sys

EXTS = ('.ttrpg', '.actor', '.arc', '.frame', '.setting', '.campaign', '.codex')
TYPE_DEF = re.compile(r'^\s*(#\w+)\s+(?:ACTOR\s+"([^"]+)"|\^"([^"]+)")\s+DEF\s*\{')
PROP = re.compile(r'^\s*\^"([^"]+)"\s+(?!STRING\s|INTEGER\s|BOOLEAN\s|ENUM\s|LIST\s|DEF)')
DECL = re.compile(r'^\s*\^"([^"]+)"\s+(?:STRING|INTEGER|BOOLEAN|ENUM|LIST OF)\b(.*)$')


def files(d):
    return sorted(p for p in glob.glob(os.path.join(d, '**', '*'), recursive=True)
                  if os.path.isfile(p) and p.endswith(EXTS))


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
    # --- declared types and which of their properties are REQUIRED -----------------
    required = {}          # type name -> [property, ...]
    for text in texts.values():
        cur, depth = None, 0
        for line in text.splitlines():
            m = TYPE_DEF.match(line)
            if m and 'PROPERTIES' in text[text.index(line):text.index(line) + 4000]:
                cur = m.group(2) or m.group(3)
                depth = 0
            if cur:
                md = DECL.match(line)
                if md and 'REQUIRED' in md.group(2):
                    required.setdefault(cur, []).append(md.group(1))
                if re.match(r'^\s{0,4}\}\s*$', line):
                    cur = None

    # --- instances of each type, and which properties they actually carry ----------
    inst = collections.Counter()
    filled = collections.defaultdict(collections.Counter)
    for path, text in texts.items():
        if re.match(r'\s*BASE\s', text):
            continue          # a BASE declares TYPES; a type that EXTENDS another is
                              # not an instance of it
        for m in re.finditer(r'EXTENDS\s+(?:#\w+\s+)?\^"([^"]+)"(.*?)(?=\n\s*EXTENDS\s|\Z)',
                             text, re.S):
            ty, body = m.group(1), m.group(2)[:6000]
            if ty not in required:
                continue
            inst[ty] += 1
            for prop in required[ty]:
                if f'^"{prop}"' in body:
                    filled[ty][prop] += 1

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
