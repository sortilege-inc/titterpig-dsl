#!/usr/bin/env python3
"""Apply the DECISION-7 MENTIONS treatment to an edition's DEF descriptions.

For every DEF with a DESCRIPTION in the edition tree:
  1. Strip cross-rulebook page citations "(ArM5, page 179)" / "(see ArM5 p42)"
     / "(RoP:Magic, page 30)" — the DEF reference supersedes them.
  2. Add a stand-off MENTIONS block: for each DECLARED entity name in THIS
     edition that appears in the (stripped) description, emit
     "<surface form> -> ^"Target"".  Surface form is the exact text as printed;
     verbatim DESCRIPTION is otherwise untouched.

Deterministic and high-precision: only MULTI-WORD declared names are linked
(single common words like "Wealth"/"Road" would over-link — those are left for
an LLM refinement pass).  MENTIONS resolve WITHIN the edition (hash namespaces
reset across editions, spec §5) — run once per edition dir, never cross.

Usage: apply_mentions.py <edition-dir>            # writes in place
       apply_mentions.py <edition-dir> --dry      # report only
"""
import os
import re
import sys

DEF_RE = re.compile(r'^(\s*)(?:#\S+\s+)?(?:\^"([^"]+)"|(?:TEMPLATE|ACTOR)\s+"([^"]+)")\s+DEF\b')
DESC_RE = re.compile(r'^(\s*)DESCRIPTION\s+"(.*)"\s*$')
# page citations to strip: (ArM5, page N) / (see ArM5 p. N) / (RoP:Faerie, page N)
PAGE_RE = re.compile(r'\s*\((?:see\s+)?(?:ArM5|RoP:[A-Za-z& ]+)[,.]?\s*p(?:age|\.)?\s*\d+\)')


def name_key(name: str) -> str:
    s = name.strip().replace('’', "'").replace('‘', "'")
    m = re.match(r'^(.*),\s*(the|a|an)$', s, re.I)
    if m:
        s = f'{m.group(2)} {m.group(1)}'
    return re.sub(r'[^a-z0-9]+', '', s.lower())


def edition_files(root):
    for dp, _, fns in os.walk(root):
        for fn in fns:
            if fn.endswith('.ttrpg'):
                yield os.path.join(dp, fn)


def declared_map(root):
    """nameKey -> canonical printed name, for every DEF in the edition.  Only
    MULTI-WORD names are kept (single words over-link)."""
    out = {}
    for f in edition_files(root):
        for line in open(f, encoding='utf-8'):
            m = DEF_RE.match(line)
            if m:
                name = m.group(2) or m.group(3)
                if len(name.split()) >= 2:          # multi-word only
                    out.setdefault(name_key(name), name)
    return out


def build_matcher(declared):
    names = sorted(set(declared.values()), key=lambda n: -len(n))
    if not names:
        return None
    return re.compile(r'(?<![A-Za-z])(' + '|'.join(re.escape(n) for n in names) + r')(?![A-Za-z])')


def find_mentions(desc, rx, declared, self_key):
    hits, used = [], []
    for m in rx.finditer(desc):
        if any(s < m.end() and m.start() < e for s, e in used):
            continue
        canonical = declared.get(name_key(m.group(1)))
        if not canonical or name_key(m.group(1)) == self_key:
            continue
        used.append((m.start(), m.end()))
        hits.append((m.group(1), canonical))
    return hits


def process(root, dry):
    declared = declared_map(root)
    rx = build_matcher(declared)
    n_files = n_defs = n_stripped = n_mentions = 0
    for f in edition_files(root):
        lines = open(f, encoding='utf-8').read().split('\n')
        out = []
        cur_key = None
        changed = False
        skip_mentions = False
        for line in lines:
            # Strip any pre-existing stand-off MENTIONS block so a re-run
            # regenerates it cleanly instead of stacking a second copy. The block
            # is `<indent>MENTIONS {` ... `<indent>}` with no nested braces.
            if skip_mentions:
                changed = True
                if line.strip() == '}':
                    skip_mentions = False
                continue
            if line.strip() == 'MENTIONS {':
                skip_mentions = True
                changed = True
                continue
            dm = DEF_RE.match(line)
            if dm:
                cur_key = name_key(dm.group(2) or dm.group(3))
            desc = DESC_RE.match(line)
            if desc and cur_key is not None:
                n_defs += 1
                indent, body = desc.group(1), desc.group(2)
                stripped = PAGE_RE.sub('', body)
                stripped = re.sub(r'  +', ' ', stripped).replace(' .', '.').replace(' ,', ',')
                if stripped != body:
                    n_stripped += 1
                    changed = True
                out.append(f'{indent}DESCRIPTION "{stripped}"')
                ment = find_mentions(stripped, rx, declared, cur_key) if rx else []
                if ment:
                    n_mentions += len(ment)
                    changed = True
                    out.append(f'{indent}MENTIONS {{')
                    for surface, target in ment:
                        out.append(f'{indent}    "{surface}" -> ^"{target}"')
                    out.append(f'{indent}}}')
                continue
            out.append(line)
        n_files += 1
        if changed and not dry:
            open(f, 'w', encoding='utf-8').write('\n'.join(out))
    tag = 'DRY' if dry else 'WROTE'
    print(f'[{tag}] {root}')
    print(f'  files {n_files}  defs-with-description {n_defs}  '
          f'page-cites-stripped {n_stripped}  mentions-added {n_mentions}  '
          f'(declared multi-word names: {len(declared)})')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('usage: apply_mentions.py <edition-dir> [--dry]')
    process(sys.argv[1], '--dry' in sys.argv)
