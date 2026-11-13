#!/usr/bin/env python3
"""DSL 0.5 gate for STRUCTURE — the thing no other gate measures.

The validator asks whether a file is well-formed. `coverageAudit.ts` asks whether
every source unit is represented. The verbatim QA asks whether the text is the book's.
A corpus of heading-shaped prose blobs answers yes to all three and is still unusable:
coyotecrow shipped 2026-09-22 with 561 DEFs carrying 39 PROPERTIES blocks against 451
DESCRIPTION blobs, and every gate passed.

One check:

  SHAPE     DESCRIPTION must not outnumber PROPERTIES. When it does, the mechanics are in
            prose and the conversion is not done.

REQUIRED is no longer checked here. Until v0.6 this file failed a property that a type declared
REQUIRED and that no instance of the type filled, and only noted one that some instances left
out. DECISION-34 gives the word one meaning (every instance of the type has the property) and
ttrpg_validator.py checks it for every instance.

    python3 check_structure.py <dir> [--min-ratio 1.0]
"""
import glob, os, re, sys

EXTS = ('.ttrpg', '.actor', '.arc', '.frame', '.setting', '.campaign', '.codex')


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
        + len(re.findall(r'^\s*\^"Description"\s+(?:STRING\s|")', blob, re.M))
    n_def = len(re.findall(r'DEF\s*\{', blob))
    n_table = len(re.findall(r'\bTABLE\s*\{', blob))
    n_list = len(re.findall(r'\bLIST OF\b', blob))
    n_empty = len(re.findall(r'DEF\s*\{\s*\}', blob))
    ratio = n_prop / n_desc if n_desc else float('inf')

    errs = []

    print(f'STRUCTURE: {len(texts)} file(s) | {n_def} DEF | {n_prop} PROPERTIES | '
          f'{n_desc} DESCRIPTION | ratio {ratio:.1f} | {n_table} TABLE | '
          f'{n_list} LIST OF | {n_empty} empty DEF')
    if ratio < min_ratio:
        errs.append(f'SHAPE: {n_desc} DESCRIPTION vs {n_prop} PROPERTIES '
                    f'(ratio {ratio:.2f} < {min_ratio}) — the mechanics are in prose')
    for e in errs:
        print(f'  ERROR {e}')
    print(f'STRUCTURE GATE: {"FAIL" if errs else "PASS"}')
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())
