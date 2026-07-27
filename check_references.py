#!/usr/bin/env python3
"""DSL 0.5 REFERENCES / REFERENCED BY coherence gate (supersedes check_mentions.py).

Per edition-scoped corpus root:
  1. Every REFERENCES / (deprecated) MENTIONS target resolves — by #hash when given
     (the hash must be a declared anchor AND its name must match the caret), else by name.
  2. STRICT hash rule (owner decision B): a target WITHOUT a #hash → WARN (non-fatal). ~207
     arm5e names are multiply-defined; a later same-name entity must not silently re-point a link.
  3. Every surface form appears as a substring of its entry's DESCRIPTION (drift check).
  4. REFERENCED BY (optional inverse mirror): its referrer resolves, AND each entry corresponds to
     a real REFERENCES pointing at this DEF (consistency). Absence of REFERENCED BY is never an error.

Exit 1 on any ERROR (unresolved / bad-hash / name-hash mismatch / surface-drift / mirror-inconsistency).
WARNs (hashless targets) do not fail the gate but are reported and counted.

  usage: check_references.py <edition-dir> [--strict-warn-as-error]
"""
import os, re, sys

root = sys.argv[1]
WARN_FATAL = '--strict-warn-as-error' in sys.argv
SHOW_WARNS = '--show-warns' in sys.argv          # per-line hashless WARNs (noisy on 0.4 corpora)

DEF   = re.compile(r'^\s*(?:(#\S+)\s+)?(?:\^"([^"]+)"|(?:TEMPLATE|ACTOR)\s+"([^"]+)")\s+DEF\b')
DESC  = re.compile(r'^\s*DESCRIPTION\s+"(.*)"\s*$')
OPEN  = re.compile(r'^\s*(REFERENCES|MENTIONS|REFERENCED\s+BY)\s*\{')
CLOSE = re.compile(r'^\s*\}\s*$')
# "surface" -> [#hash] ^"Target"      (optional @n occurrence index tolerated on surface)
REF   = re.compile(r'^\s*"([^"]+)"(?:@\d+)?\s*->\s*(?:(#\S+)\s+)?\^"([^"]+)"\s*$')
# ["surface"] <- [#hash] ^"Referrer"
RBY   = re.compile(r'^\s*(?:"([^"]+)"\s*)?<-\s*(?:(#\S+)\s+)?\^"([^"]+)"\s*$')

nk = lambda s: re.sub(r'[^a-z0-9]+', '', s.strip().replace('’', "'").lower())

files = [os.path.join(dp, f) for dp, _, fs in os.walk(root) for f in fs if f.endswith('.ttrpg')]

# Pass 1: declared entities. name_key -> set(hash); hash -> name_key.
names, hash_name = {}, {}
for f in files:
    for l in open(f, encoding='utf-8'):
        m = DEF.match(l)
        if m:
            h = m.group(1); name = m.group(2) or m.group(3); k = nk(name)
            names.setdefault(k, set())
            if h:
                names[k].add(h); hash_name[h] = k

# Pass 2: collect REFERENCES pairs (referrer_def -> target) and REFERENCED BY claims.
errors = warns = total = rby_total = 0
ref_pairs = set()      # (referrer_defkey, target_namekey)
rby_claims = []        # (target_defkey, referrer_namekey, referrer_hash, surface, file, line)

def err(msg):
    global errors; errors += 1; print(f'  ERROR {msg}')
def warn(msg):
    global warns; warns += 1
    if SHOW_WARNS: print(f'  WARN  {msg}')

for f in files:
    b = os.path.basename(f)
    cur_def = cur_hash = None
    cur_desc = None
    block = None            # 'REF' | 'RBY' | None
    for ln, l in enumerate(open(f, encoding='utf-8').read().split('\n'), 1):
        d = DEF.match(l)
        if d:
            cur_hash = d.group(1); cur_def = nk(d.group(2) or d.group(3)); cur_desc = None
        dm = DESC.match(l)
        if dm:
            cur_desc = dm.group(1)
        o = OPEN.match(l)
        if o:
            block = 'RBY' if o.group(1).startswith('REFERENCED') else 'REF'
            continue
        if block and CLOSE.match(l):
            block = None; continue
        if block == 'REF':
            m = REF.match(l)
            if not m:
                if l.strip() and not l.strip().startswith('#'):
                    err(f'unparseable REFERENCES entry in {b}:{ln}: {l.strip()}')
                continue
            total += 1
            surface, thash, tname = m.group(1), m.group(2), m.group(3)
            tk = nk(tname)
            # resolve
            if thash:
                if thash not in hash_name:
                    err(f'{b}:{ln} target hash {thash} is not a declared anchor')
                elif hash_name[thash] != tk:
                    err(f'{b}:{ln} hash {thash} names "{hash_name[thash]}" but caret says ^"{tname}"')
            else:
                if tk not in names:
                    err(f'{b}:{ln} unresolved target ^"{tname}"')
                else:
                    warn(f'{b}:{ln} hashless target ^"{tname}" (strict: add #hash; name has '
                         f'{len(names[tk])} anchor(s))')
            # surface in description
            if cur_desc is not None and surface not in cur_desc:
                err(f'{b}:{ln} surface "{surface}" not a substring of its DESCRIPTION')
            if cur_def:
                ref_pairs.add((cur_def, tk))
        elif block == 'RBY':
            m = RBY.match(l)
            if not m:
                if l.strip() and not l.strip().startswith('#'):
                    err(f'unparseable REFERENCED BY entry in {b}:{ln}: {l.strip()}')
                continue
            rby_total += 1
            surface, rhash, rname = m.group(1), m.group(2), m.group(3)
            rk = nk(rname)
            if rhash:
                if rhash not in hash_name:
                    err(f'{b}:{ln} REFERENCED BY referrer hash {rhash} is not a declared anchor')
                elif hash_name[rhash] != rk:
                    err(f'{b}:{ln} REFERENCED BY hash {rhash} names "{hash_name[rhash]}" but ^"{rname}"')
            elif rk not in names:
                err(f'{b}:{ln} REFERENCED BY unresolved referrer ^"{rname}"')
            if cur_def:
                rby_claims.append((cur_def, rk, f'{b}:{ln}'))

# Consistency: every REFERENCED BY(target=X, referrer=Y) needs a REFERENCES(Y -> X).
for target_def, referrer, loc in rby_claims:
    if (referrer, target_def) not in ref_pairs:
        err(f'{loc} REFERENCED BY claims "{referrer}" references this entry, but no REFERENCES '
            f'from "{referrer}" -> "{target_def}" exists')

print(f'REFERENCES: {total} refs | {rby_total} referenced-by | {errors} error(s) | {warns} hashless WARN(s)')
sys.exit(1 if errors or (WARN_FATAL and warns) else 0)
