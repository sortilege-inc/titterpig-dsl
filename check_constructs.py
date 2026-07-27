#!/usr/bin/env python3
"""DSL 0.5 gate for the GUIDANCE / HOOKS / OPTIONAL constructs and .selections files.

  1. HOOKS: every HOOK's `FORMALITY` is one of PROSE|TAGGED|CONDITIONAL|FORMAL; every `THEN [...]`
     mechanic ref resolves.
  2. OPTIONAL: `DEFAULT` is on|off; every `SCOPE [...]` item resolves as a ref, or is the literal GLOBAL.
  3. GUIDANCE: every `CONCERNS [...]` ref resolves.
  4. .selections (SELECTIONS files): every `SELECT #hash on|off` names an on|off value AND #hash
     resolves to a DEF that carries an OPTIONAL block.

Refs may be hash-qualified (`#hash ^"Name"`) or bare (`^"Name"`); a hash must be a declared anchor
whose name matches. (The strict-hash WARN is REFERENCES-only, per owner decision B — see
check_references.py.) Exit 1 on any ERROR.

  usage: check_constructs.py <corpus-dir>
"""
import os, re, sys

root = sys.argv[1]
FORMALITY = {'PROSE', 'TAGGED', 'CONDITIONAL', 'FORMAL'}
POSTURE = {'on', 'off'}

DEFLINE = re.compile(r'^\s*(?:(#\S+)\s+)?(?:\^"([^"]+)"|(?:TEMPLATE|ACTOR)\s+"([^"]+)")\s+DEF\b')
REF = re.compile(r'(?:(#\S+)\s+)?\^"([^"]+)"')     # optional hash + caret, found anywhere
nk = lambda s: re.sub(r'[^a-z0-9]+', '', s.strip().replace('’', "'").lower())

ttrpg = [os.path.join(dp, f) for dp, _, fs in os.walk(root) for f in fs if f.endswith('.ttrpg')]
sel_files = [os.path.join(dp, f) for dp, _, fs in os.walk(root) for f in fs if f.endswith('.selections')]

# Pass 1: declared names/anchors + which hashed DEFs carry an OPTIONAL block.
names, hash_name, optional_hashes = {}, {}, set()
for f in ttrpg:
    cur_hash = None
    for l in open(f, encoding='utf-8'):
        m = DEFLINE.match(l)
        if m:
            cur_hash = m.group(1); k = nk(m.group(2) or m.group(3))
            names.setdefault(k, set())
            if cur_hash:
                names[k].add(cur_hash); hash_name[cur_hash] = k
        if re.match(r'^\s*OPTIONAL\s*\{', l) and cur_hash:
            optional_hashes.add(cur_hash)

errors = 0
def err(msg):
    global errors; errors += 1; print(f'  ERROR {msg}')

def resolve(hsh, name, where):
    k = nk(name)
    if hsh:
        if hsh not in hash_name:
            err(f'{where}: hash {hsh} is not a declared anchor')
        elif hash_name[hsh] != k:
            err(f'{where}: hash {hsh} names "{hash_name[hsh]}" but ^"{name}"')
    elif k not in names:
        err(f'{where}: unresolved ref ^"{name}"')

def resolve_list(inner, where):
    for hsh, name in REF.findall(inner):
        resolve(hsh, name, where)

# Pass 2: field checks over .ttrpg. Field keywords are unambiguous on their own line.
n_hook = n_opt = n_guid = 0
for f in ttrpg:
    b = os.path.basename(f)
    in_optional = 0        # brace depth bookkeeping so DEFAULT/SCOPE are scoped to OPTIONAL
    depth = 0
    for ln, l in enumerate(open(f, encoding='utf-8').read().split('\n'), 1):
        where = f'{b}:{ln}'
        mo = re.match(r'^\s*OPTIONAL\s*\{', l)
        if mo:
            in_optional = depth + 1; n_opt += 1
        mf = re.match(r'^\s*FORMALITY\s+(\S+)\s*$', l)
        if mf:
            n_hook += 1
            if mf.group(1) not in FORMALITY:
                err(f'{where}: FORMALITY "{mf.group(1)}" not one of {sorted(FORMALITY)}')
        mt = re.match(r'^\s*THEN\s+\[(.*)\]\s*$', l)
        if mt:
            resolve_list(mt.group(1), f'{where} (HOOK THEN)')
        mc = re.match(r'^\s*CONCERNS\s+\[(.*)\]\s*$', l)
        if mc:
            n_guid += 1
            resolve_list(mc.group(1), f'{where} (GUIDANCE CONCERNS)')
        md = re.match(r'^\s*DEFAULT\s+(\w+)\s*$', l)
        if md and in_optional:
            if md.group(1) not in POSTURE:
                err(f'{where}: OPTIONAL DEFAULT "{md.group(1)}" must be on|off')
        ms = re.match(r'^\s*SCOPE\s+\[(.*)\]\s*$', l)
        if ms and in_optional:
            inner = ms.group(1)
            for hsh, name in REF.findall(inner):
                resolve(hsh, name, f'{where} (OPTIONAL SCOPE)')
            # GLOBAL literal is allowed and needs no ref
        # brace bookkeeping
        depth += l.count('{') - l.count('}')
        if in_optional and depth < in_optional:
            in_optional = 0

# Pass 3: .selections files.
n_sel = 0
for f in sel_files:
    b = os.path.basename(f)
    for ln, l in enumerate(open(f, encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'^\s*SELECT\s+(#\S+)\s+(\w+)', l)
        if m:
            n_sel += 1
            h, posture = m.group(1), m.group(2)
            if posture not in POSTURE:
                err(f'{b}:{ln}: SELECT posture "{posture}" must be on|off')
            if h not in optional_hashes:
                if h in hash_name:
                    err(f'{b}:{ln}: SELECT {h} ("{hash_name[h]}") is not an OPTIONAL rule')
                else:
                    err(f'{b}:{ln}: SELECT {h} resolves to no DEF')

print(f'CONSTRUCTS: {n_hook} hook(s) | {n_opt} optional(s) | {n_guid} guidance | {n_sel} selection(s) '
      f'| {len(optional_hashes)} optional-DEF(s) | {errors} error(s)')
sys.exit(1 if errors else 0)
