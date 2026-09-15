#!/usr/bin/env python3
"""DSL 0.5 reference coherence gate.

Part A — REFERENCES / REFERENCED BY (DECISION-11).
Part B — every OTHER reference site (§5d, DECISION-13): EXTENDS, APPLIES TO,
LIST OF, CONCERNS, OVERRIDE, MODIFY, ADD, ALIAS ... FOR. The hash is the
referent and the caret name is a readability aid, so a hashless reference whose
name resolves to more than one distinct entity is an ERROR: nothing in the file
says which is meant, and two consumers that invent different tie-breaks disagree
about what the corpus says.

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

  usage: check_references.py <edition-dir> [--strict-warn-as-error] [--with <dir> ...]

  --with <dir>   an additional corpus root (e.g. the base edition a 3rd-party corpus
                 EXTENDS) whose DEFs count as resolution targets. Only the edition-dir's
                 own REFERENCES are checked; the --with roots supply anchors, never claims.
"""
import os, re, sys

root = sys.argv[1]
WITH = [sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == '--with' and i + 1 < len(sys.argv)]
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
context = [os.path.join(dp, f) for w in WITH for dp, _, fs in os.walk(w) for f in fs if f.endswith('.ttrpg')]

# Pass 1: declared entities. name_key -> set(hash); hash -> name_key.
names, hash_name = {}, {}
for f in files + context:
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

# ---------------------------------------------------------------------------
# Part B — §5d / DECISION-13: every other reference site.
# ---------------------------------------------------------------------------
DSL_EXT = ('.ttrpg', '.actor', '.arc', '.frame', '.setting', '.campaign', '.bridge', '.codex')
all_files = [os.path.join(dp, f) for dp, _, fs in os.walk(root)
             for f in fs if f.endswith(DSL_EXT)]
all_ctx = [os.path.join(dp, f) for w in WITH for dp, _, fs in os.walk(w)
           for f in fs if f.endswith(DSL_EXT)]

# Distinct entities behind a name. Two DEFs are the SAME entity when they carry
# the same hash (a legal restatement across files, §13/DECISION-4). Hashless DEFs
# cannot be told apart, so they collapse into at most one further entity.
ent_hashes, ent_nohash, anchor_name = {}, set(), {}
ADD_DEF = re.compile(r'^\s*ADD\s+(?:(#\S+)\s+)?\^"([^"]+)"\s+DEF\b')
for f in all_files + all_ctx:
    for l in open(f, encoding='utf-8', errors='ignore'):
        m = DEF.match(l)
        if m:
            h, k = m.group(1), nk(m.group(2) or m.group(3))
        else:
            m = ADD_DEF.match(l)
            if not m:
                continue
            h, k = m.group(1), nk(m.group(2))
        ent_hashes.setdefault(k, set())
        if h:
            ent_hashes[k].add(h)
            anchor_name[h] = k
        else:
            ent_nohash.add(k)

def distinct(k):
    return len(ent_hashes.get(k, ())) + (1 if k in ent_nohash else 0)

# A reference site: the keyword, then one or more [#hash] ^"Name" targets,
# optionally bracketed and spread over lines. SET/ADD_TO/REMOVE_FROM are NOT
# here: they target a PROPERTY of the entity being modified, not an entity.
# `ADD` is absent on purpose: `ADD #hash ^"Name" DEF {` DECLARES a new entity
# (S13 -- "ADD asserts the content is new"), so its hash is an anchor, not a
# reference to one. `ALIAS ^"New" FOR ^"Existing"` likewise declares its first
# name; only the FOR target is a reference, so ALIAS is matched separately.
# The target list must NOT cross a newline unless the construct opened a `[`.
# `EXTENDS ^"Order Degree"` followed on the next line by the property
# `^"Degree" INTEGER 1` is one reference and one property, not two references.
SITE = re.compile(r'\b(EXTENDS|LIST\s+OF|CONCERNS|OVERRIDE|MODIFY)\b'
                  r'[ \t]*((?:(?:#[A-Za-z0-9_]+[ \t]+)?\^"[^"]+"[ \t]*,?[ \t]*)+)')
SITE_LIST = re.compile(r'\b(APPLIES\s+TO|CONCERNS|LIST\s+OF)\b[ \t]*\[([^\]]*)\]', re.S)
ALIAS_FOR = re.compile(r'\bALIAS\b[^\n]*?\bFOR\b[ \t]+(?:ORIGIN[ \t]+|DESTINATION[ \t]+)?'
                       r'((?:#[A-Za-z0-9_]+[ \t]+)?\^"[^"]+")')
TARGET = re.compile(r'(#[A-Za-z0-9_]+)?[ \t]*\^"([^"]+)"')

b_err = b_warn = b_sites = 0
amb_by_name = {}
for f in all_files:
    src = open(f, encoding='utf-8', errors='ignore').read()
    base = os.path.relpath(f, root)
    for m in list(SITE.finditer(src)) + list(SITE_LIST.finditer(src)) + list(ALIAS_FOR.finditer(src)):
        is_site = m.re in (SITE, SITE_LIST)
        kw = re.sub(r'\s+', ' ', m.group(1)) if is_site else 'ALIAS FOR'
        ln = src.count('\n', 0, m.start()) + 1
        for thash, tname in TARGET.findall(m.group(2) if is_site else m.group(1)):
            b_sites += 1
            k = nk(tname)
            if thash:
                if thash not in anchor_name:
                    b_err += 1
                    print(f'  ERROR {base}:{ln} {kw} hash {thash} is not a declared anchor')
                elif anchor_name[thash] != k:
                    b_err += 1
                    print(f'  ERROR {base}:{ln} {kw} hash {thash} names '
                          f'"{anchor_name[thash]}" but caret says ^"{tname}"')
                continue
            n = distinct(k)
            if n == 0:
                continue          # dangling is the validator's job, not this gate's
            if n > 1:
                b_err += 1
                amb_by_name[tname] = amb_by_name.get(tname, 0) + 1
                if SHOW_WARNS or amb_by_name[tname] <= 1:
                    print(f'  ERROR {base}:{ln} {kw} ^"{tname}" is ambiguous — '
                          f'{n} distinct entities carry this name; add the #hash (§5d)')
            else:
                b_warn += 1
                if SHOW_WARNS:
                    print(f'  WARN  {base}:{ln} {kw} hashless ^"{tname}" (strict: add #hash)')

if amb_by_name and not SHOW_WARNS:
    extra = sum(v - 1 for v in amb_by_name.values() if v > 1)
    if extra:
        print(f'  ... and {extra} further ambiguous reference(s) to the same {len(amb_by_name)} '
              f'name(s) (--show-warns to list every site)')

print(f'REFERENCE SITES (\u00a75d): {b_sites} sites | {b_err} ambiguous/mismatched error(s) '
      f'| {b_warn} hashless WARN(s)')
sys.exit(1 if errors or b_err or (WARN_FATAL and (warns or b_warn)) else 0)
