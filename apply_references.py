#!/usr/bin/env python3
"""Apply the DSL 0.5 REFERENCES treatment to an edition's DEF descriptions
(supersedes apply_mentions.py; DECISION-11).

For every DEF with a DESCRIPTION in the edition tree:
  1. Strip cross-rulebook page citations "(ArM5, page 179)" / "(see ArM5 p42)"
     / "(RoP:Magic, page 30)" — the DEF reference supersedes them.
  2. Emit a stand-off REFERENCES block: for each DECLARED entity name in THIS edition
     that appears in the (stripped) description, emit
        "<surface form>" -> #hash ^"Target"
     including the target's #hash when the name resolves to exactly ONE anchor
     (unambiguous). When the name has zero or several anchors, the hash is omitted and
     the entry is hashless — which check_references.py flags as a WARN for a human to
     resolve (the strict-hash rule, DECISION-11 B).

Deterministic: only MULTI-WORD declared names are linked (single common words over-link).
References resolve WITHIN the edition (hash namespaces reset across editions) — run once
per edition dir, never cross. Idempotent: an existing REFERENCES (or legacy MENTIONS)
block is stripped and regenerated, so re-runs don't stack.

Usage: apply_references.py <edition-dir>          # writes in place
       apply_references.py <edition-dir> --dry    # report only
"""
import os
import re
import sys

DEF_RE = re.compile(r'^(\s*)(?:(#\S+)\s+)?(?:\^"([^"]+)"|(?:TEMPLATE|ACTOR)\s+"([^"]+)")\s+DEF\b')
DESC_RE = re.compile(r'^(\s*)DESCRIPTION\s+"(.*)"\s*$')
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


def declared_maps(root):
    """nameKey -> canonical printed name (multi-word only), and nameKey -> set(hash)."""
    names, anchors = {}, {}
    for f in edition_files(root):
        for line in open(f, encoding='utf-8'):
            m = DEF_RE.match(line)
            if m:
                h = m.group(2); name = m.group(3) or m.group(4)
                if len(name.split()) >= 2:
                    k = name_key(name)
                    names.setdefault(k, name)
                    anchors.setdefault(k, set())
                    if h:
                        anchors[k].add(h)
    return names, anchors


def build_matcher(names):
    vals = sorted(set(names.values()), key=lambda n: -len(n))
    if not vals:
        return None
    return re.compile(r'(?<![A-Za-z])(' + '|'.join(re.escape(n) for n in vals) + r')(?![A-Za-z])')


def find_references(desc, rx, names, self_key):
    hits, used = [], []
    for m in rx.finditer(desc):
        if any(s < m.end() and m.start() < e for s, e in used):
            continue
        k = name_key(m.group(1))
        canonical = names.get(k)
        if not canonical or k == self_key:
            continue
        used.append((m.start(), m.end()))
        hits.append((m.group(1), k, canonical))
    return hits


def process(root, dry):
    names, anchors = declared_maps(root)
    rx = build_matcher(names)
    n_files = n_defs = n_stripped = n_refs = n_hashed = n_hashless = 0
    for f in edition_files(root):
        lines = open(f, encoding='utf-8').read().split('\n')
        out = []
        cur_key = None
        changed = False
        skip = False
        for line in lines:
            # Strip any pre-existing REFERENCES (or legacy MENTIONS) block so a re-run
            # regenerates it cleanly. Block is `<indent>KEYWORD {` … `<indent>}`, no nesting.
            if skip:
                changed = True
                if line.strip() == '}':
                    skip = False
                continue
            if line.strip() in ('REFERENCES {', 'MENTIONS {'):
                skip = True
                changed = True
                continue
            dm = DEF_RE.match(line)
            if dm:
                cur_key = name_key(dm.group(3) or dm.group(4))
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
                refs = find_references(stripped, rx, names, cur_key) if rx else []
                if refs:
                    n_refs += len(refs)
                    changed = True
                    out.append(f'{indent}REFERENCES {{')
                    for surface, k, canonical in refs:
                        hs = anchors.get(k, set())
                        if len(hs) == 1:
                            out.append(f'{indent}    "{surface}" -> {next(iter(hs))} ^"{canonical}"')
                            n_hashed += 1
                        else:
                            out.append(f'{indent}    "{surface}" -> ^"{canonical}"')
                            n_hashless += 1
                    out.append(f'{indent}}}')
                continue
            out.append(line)
        n_files += 1
        if changed and not dry:
            open(f, 'w', encoding='utf-8').write('\n'.join(out))
    tag = 'DRY' if dry else 'WROTE'
    print(f'[{tag}] {root}')
    print(f'  files {n_files}  defs-with-description {n_defs}  page-cites-stripped {n_stripped}  '
          f'references {n_refs} ({n_hashed} hashed, {n_hashless} hashless→WARN)  '
          f'(declared multi-word names: {len(names)})')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('usage: apply_references.py <edition-dir> [--dry]')
    process(sys.argv[1], '--dry' in sys.argv)
