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
# A surface form has to be found in the prose it annotates, and not every
# corpus writes that prose on a bare DESCRIPTION line. Root holds a move's
# commentary in `^"Description" STRING "..."` inside PROPERTIES, its trigger in
# TRIGGER, and a weapon tag's whole rule in an OPTIONS string; TEETH holds a
# location's hooks in `^"Text" STRING "..."` inside nested ENTRY blocks. A gate
# that reads only DESCRIPTION finds nothing to check in any of them and passes
# every entry without looking, which is worse than not checking. So the prose of
# a DEF is every string literal in its body -- the DEF's own name line excepted,
# and the REFERENCES block excepted, since an entry there would otherwise let
# every surface form prove its own presence.
QUOTED = re.compile(r'"((?:[^"\\]|\\.)*)"')
OPEN  = re.compile(r'^\s*(REFERENCES|MENTIONS|REFERENCED\s+BY|EMPHASIS)\s*\{')
# §5c EMPHASIS: a marked span with no referent, so there is nothing to resolve.
# The one rule it shares with REFERENCES is the one that matters -- the surface
# form has to be in the prose it claims to mark.
# The surface form may itself contain an escaped quote -- the book prints dialogue --
# so it is read with the same escape-aware body as QUOTED. "[^"]+" stops at the first
# backslash-quote and reports a legal entry as unparseable.
EMPH  = re.compile(r'^\s*"((?:[^"\\]|\\.)*)"(?:@\d+)?\s*$')
# A block with one entry is legal on one line -- `EMPHASIS { "…" }` -- and is
# how a corpus with one span per DEF reads best. Its closing brace is not on a
# line of its own, so a reader that only closes on a bare `}` never closes it
# and swallows the rest of the file.
ONELINE = re.compile(r'^\s*(REFERENCES|MENTIONS|REFERENCED\s+BY|EMPHASIS)\s*\{(.*)\}\s*$')
CLOSE = re.compile(r'^\s*\}\s*$')
# "surface" -> [#hash] ^"Target"      (optional @n occurrence index tolerated on surface)
REF   = re.compile(r'^\s*"((?:[^"\\]|\\.)*)"(?:@\d+)?\s*->\s*(?:(#\S+)\s+)?\^"([^"]+)"\s*$')
# ["surface"] <- [#hash] ^"Referrer"
RBY   = re.compile(r'^\s*(?:"((?:[^"\\]|\\.)*)"\s*)?<-\s*(?:(#\S+)\s+)?\^"([^"]+)"\s*$')

nk = lambda s: re.sub(r'[^a-z0-9]+', '', s.strip().replace('’', "'").lower())

# Every DSL container, not just .ttrpg: a REFERENCES target may be declared in a
# narrative container (l5r5e's ^"Mountain Song Temple" is a LOCATION in an .arc),
# and indexing only .ttrpg reported such a target as an undeclared anchor.
PART_A_EXT = ('.ttrpg', '.actor', '.arc', '.frame', '.setting', '.campaign', '.bridge', '.codex')
files = [os.path.join(dp, f) for dp, _, fs in os.walk(root) for f in fs if f.endswith(PART_A_EXT)]
context = [os.path.join(dp, f) for w in WITH for dp, _, fs in os.walk(w) for f in fs if f.endswith(PART_A_EXT)]

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
errors = warns = total = rby_total = emph_total = 0
ref_pairs = set()      # (referrer_defkey, target_namekey)
rby_claims = []        # (target_defkey, referrer_namekey, referrer_hash, surface, file, line)

def err(msg):
    global errors; errors += 1; print(f'  ERROR {msg}')
def warn(msg):
    global warns; warns += 1
    if SHOW_WARNS: print(f'  WARN  {msg}')

# A referrer's prose is the prose of its WHOLE body, nested entities included --
# something whose text is carried in sub-entries (TEETH's nested ENTRY `^"Text"`,
# Root's ENTRY blocks, a rule whose examples are children) is one entity, and a
# reference on the parent annotates the parent's text wherever it sits. Reading
# the file flat -- letting each DEF header clobber the prose so far -- attributed
# a parent's REFERENCES block to whichever child happened to close last, which is
# every nested DEF's REFERENCES block, since the block conventionally follows the
# children. So scope by braces and take the subtree.
#
# Scope by BRACES, not by keyword: REFERENCES is legal on anything that holds
# prose, and a narrative container (an .arc's SCENE, a LOCATION, an ENTRY) is not
# a DEF. A reader that only opens a scope on `DEF` finds no prose at all on those
# and reports every one of them as unprosed.
QSTRIP = re.compile(r'"(?:[^"\\]|\\.)*"')
CARET = re.compile(r'\^"([^"]+)"')

TRIPLE = '"""'
CODE, IN_TRIPLE, IN_STR = 0, 1, 2


def braces(l, state):
    """Braces this line opens/closes in CODE, and the scanner state it ends in.

    A brace is structure only outside a string and outside a comment, and a
    string is not always on one line: some 0.4 corpora hold a record's whole
    write-up in a \"\"\"block\"\"\", and a caret name that swallowed a Markdown
    heading runs a plain "string" across five lines. Counting either as code
    threw the scoping off by as much as 24 levels."""
    op = cl = 0
    i, n = 0, len(l)
    while i < n:
        c = l[i]
        if state == IN_TRIPLE:
            if l.startswith(TRIPLE, i):
                state = CODE; i += 3
            else:
                i += 1
        elif state == IN_STR:
            if c == '\\':
                i += 2
            elif c == '"':
                state = CODE; i += 1
            else:
                i += 1
        elif l.startswith(TRIPLE, i):
            state = IN_TRIPLE; i += 3
        elif c == '"':
            state = IN_STR; i += 1
        elif c == '#' and (i + 1 >= n or l[i + 1].isspace()):
            break                         # `# comment`; `#anchor` is not one
        else:
            if c == '{':
                op += 1
            elif c == '}':
                cl += 1
            i += 1
    return op, cl, state


for f in files:
    b = os.path.basename(f)
    lines = open(f, encoding='utf-8').read().split('\n')

    # Pass A -- brace-scoped spans and the prose of each line.
    # A span is [start, end, kind, namekey]; kind 'ref' is a REFERENCES /
    # MENTIONS / REFERENCED BY / EMPHASIS block, which owns no prose and is never
    # a referrer -- the entity around it is.
    spans = []
    prose_line = [''] * len(lines)
    stack, depth, block, broken, st = [], 0, None, False, CODE
    for i, l in enumerate(lines):
        mid = st != CODE               # this line starts inside a string
        if mid:
            # A continuation line is the entity's prose, verbatim.
            prose_line[i] = l
        d = None if mid else DEF.match(l)
        ol = None if mid else ONELINE.match(l)
        # Never inside a REFERENCES / REFERENCED BY / EMPHASIS block: an entry
        # line is itself `"surface" -> ^"Target"`, and folding that into the
        # prose would let every surface form prove its own presence.
        if not mid and block is None and not d and not ol and '->' not in l and '<-' not in l:
            q = QUOTED.findall(l)
            if q:
                prose_line[i] = ' '.join(q)
        refblock = not mid and bool(OPEN.match(l))      # incl. the one-line form
        opener = refblock and not ol
        if opener:
            block = 'X'
        elif block and not mid and CLOSE.match(l):
            block = None
        op, cl, st = braces(l, st)
        if op:
            # The name a reference is filed under: the DEF's, else the caret name
            # this line declares (SCENE ^"..." {), else none -- inherited below.
            nm = (nk(d.group(2) or d.group(3)) if d
                  else nk(CARET.search(l).group(1)) if CARET.search(l) else None)
            for k in range(op):
                spans.append([i, len(lines), 'ref' if (refblock and k == 0) else 'entity',
                              nm if k == 0 else None])
                stack.append((len(spans) - 1, depth + k))
        depth += op - cl
        while stack and depth <= stack[-1][1]:
            spans[stack.pop()[0]][1] = i + 1
        if depth < 0:
            broken = True
    if depth != 0 or broken:
        # Brace accounting that does not return to zero means the spans are
        # guesses. Say so rather than checking against the wrong prose.
        err(f'{b}: unbalanced braces \u2014 scoping unreliable, prose not checked')
        continue

    def owner(i, _spans=spans):
        best = None
        for sp in _spans:
            if sp[2] == 'ref' or not (sp[0] <= i < sp[1]):
                continue
            if best is None or sp[0] > best[0]:
                best = sp
        return best

    def referrer(i, _spans=spans):
        # The nearest NAMED enclosing entity -- PROPERTIES / TABLE and the like
        # open a scope but declare nothing, so they inherit their parent's name.
        best = None
        for sp in _spans:
            if sp[2] == 'ref' or sp[3] is None or not (sp[0] <= i < sp[1]):
                continue
            if best is None or sp[0] > best[0]:
                best = sp
        return best[3] if best else None

    def prose_at(i, _lines=prose_line):
        s = owner(i)
        return None if s is None else ' '.join(x for x in _lines[s[0]:s[1]] if x)

    def check_ref(m, ln):
        global total
        total += 1
        surface, thash, tname = m.group(1), m.group(2), m.group(3)
        tk = nk(tname)
        if thash:
            if thash not in hash_name:
                err(f'{b}:{ln} target hash {thash} is not a declared anchor')
            elif hash_name[thash] != tk:
                err(f'{b}:{ln} hash {thash} names "{hash_name[thash]}" but caret says ^"{tname}"')
        elif tk not in names:
            err(f'{b}:{ln} unresolved target ^"{tname}"')
        else:
            warn(f'{b}:{ln} hashless target ^"{tname}" (strict: add #hash; name has '
                 f'{len(names[tk])} anchor(s))')
        p = prose_at(ln - 1)
        if p is None:
            err(f'{b}:{ln} surface "{surface}" has no prose in this DEF to appear in')
        elif surface not in p:
            err(f'{b}:{ln} surface "{surface}" not a substring of its DEF\'s prose')
        rf = referrer(ln - 1)
        if rf:
            ref_pairs.add((rf, tk))

    block = None            # 'REF' | 'RBY' | 'EMP' | None
    for ln, l in enumerate(lines, 1):
        ol = ONELINE.match(l)
        if ol:
            kind = ol.group(1)
            inner = ol.group(2).strip()
            if kind == 'EMPHASIS':
                em = EMPH.match(' ' + inner)
                if not em:
                    err(f'unparseable EMPHASIS entry in {b}:{ln}: {inner}')
                else:
                    emph_total += 1
                    p = prose_at(ln - 1)
                    if p is None:
                        err(f'{b}:{ln} emphasis "{em.group(1)}" has no prose in this DEF to mark')
                    elif em.group(1) not in p:
                        err(f'{b}:{ln} emphasis "{em.group(1)}" not a substring of its DEF\'s prose')
            elif kind.startswith('REFERENCED'):
                rm = RBY.match(' ' + inner)
                if not rm:
                    err(f'unparseable {kind} entry in {b}:{ln}: {inner}')
                else:
                    rby_total += 1
            else:
                rm = REF.match(' ' + inner)
                if not rm:
                    err(f'unparseable {kind} entry in {b}:{ln}: {inner}')
                else:
                    # A block with one entry is legal on one line. Counting it
                    # and moving on left it unresolved and unchecked -- the one
                    # shape of the construct the gate never looked at.
                    check_ref(rm, ln)
            continue
        o = OPEN.match(l)
        if o:
            block = ('RBY' if o.group(1).startswith('REFERENCED')
                     else 'EMP' if o.group(1) == 'EMPHASIS' else 'REF')
            continue
        if block and CLOSE.match(l):
            block = None; continue
        if block == 'REF':
            m = REF.match(l)
            if not m:
                if l.strip() and not l.strip().startswith('#'):
                    err(f'unparseable REFERENCES entry in {b}:{ln}: {l.strip()}')
                continue
            check_ref(m, ln)
        elif block == 'EMP':
            m = EMPH.match(l)
            if not m:
                if l.strip() and not l.strip().startswith('#'):
                    err(f'unparseable EMPHASIS entry in {b}:{ln}: {l.strip()}')
                continue
            emph_total += 1
            surface = m.group(1)
            p = prose_at(ln - 1)
            if p is None:
                err(f'{b}:{ln} emphasis "{surface}" has no prose in this DEF to mark')
            elif surface not in p:
                err(f'{b}:{ln} emphasis "{surface}" not a substring of its DEF\'s prose')
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
            rf = referrer(ln - 1)
            if rf:
                rby_claims.append((rf, rk, f'{b}:{ln}'))

# Consistency: every REFERENCED BY(target=X, referrer=Y) needs a REFERENCES(Y -> X).
for target_def, referrer, loc in rby_claims:
    if (referrer, target_def) not in ref_pairs:
        err(f'{loc} REFERENCED BY claims "{referrer}" references this entry, but no REFERENCES '
            f'from "{referrer}" -> "{target_def}" exists')

print(f'REFERENCES: {total} refs | {rby_total} referenced-by | {emph_total} emphasis | '
      f'{errors} error(s) | {warns} hashless WARN(s)')

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
# A narrative container and a GUIDANCE entry declare their anchor AFTER the name:
# `SCENE ^"Rosa's House" #tCUxd... {`, `ENTRY ^"Roleplaying Caitlyn" #to6Pa... {`,
# and some DEFs are written `^"Name" #hash DEF`. 3,302 anchors corpus-wide use
# this shape; indexing only `#hash ^"Name" DEF` made every reference to one of
# them look like a reference to an undeclared anchor.
# ... but NOT when another caret follows the hash on the line. `^"Nature"
# #tJTL3h... ^"Extrovert"` is a PROPERTY whose value is a hash-qualified
# reference (§5d), not a declaration of `^"Nature"`, and indexing it as one
# filed the target's anchor under the property's name -- so the next construct
# that referenced that anchor was told its hash names something else.
POST_HASH = re.compile(r'^\s*(?:[A-Z_]+\s+)?\^"([^"]+)"\s+(#[A-Za-z0-9_]+)\b(?![ \t]*\^")')
for f in all_files + all_ctx:
    for l in open(f, encoding='utf-8', errors='ignore'):
        m = DEF.match(l)
        if m:
            h, k = m.group(1), nk(m.group(2) or m.group(3))
        else:
            m = ADD_DEF.match(l)
            if m:
                h, k = m.group(1), nk(m.group(2))
            else:
                m = POST_HASH.match(l)
                if not m:
                    continue
                h, k = m.group(2), nk(m.group(1))
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
# A property whose value IS a reference -- `^"Nature" #hash ^"Extrovert"`,
# `^"See Also" #hash ^"Aging Rolls"`. It carries a hash, so §5d governs it like
# any other site; without this it was the one reference shape nothing checked,
# which is how root's ^"Paladin" and ^"Luminary" resolved to nothing in silence.
# The hash is required: a hashless `^"Prop" ^"Target"` cannot be told apart
# from two adjacent properties (`^"Category" ^"Wroth"  ^"Rating" INTEGER 3`).
PROP_REF = re.compile(r'^[ \t]*\^"[^"]+"[ \t]+((?:#[A-Za-z0-9_]+[ \t]+)\^"[^"]+")[ \t]*$',
                      re.M)
SITE = re.compile(r'\b(EXTENDS|LIST\s+OF|CONCERNS|OVERRIDE|MODIFY)\b'
                  r'[ \t]*((?:(?:#[A-Za-z0-9_]+[ \t]+)?\^"[^"]+"[ \t]*,?[ \t]*)+)')
# Only APPLIES TO / CONCERNS take a BRACKETED list of references. `LIST OF [`
# is an inline list of VALUES -- `^"Attacks" LIST OF [ ^"Creature Attack" DEF {...} ]`
# -- whose contents are nested definitions and property names, not references to
# anything. `LIST OF ^"Type"` puts its type before the bracket and SITE catches it.
SITE_LIST = re.compile(r'\b(APPLIES\s+TO|CONCERNS)\b[ \t]*\[([^\]]*)\]', re.S)
ALIAS_FOR = re.compile(r'\bALIAS\b[^\n]*?\bFOR\b[ \t]+(?:ORIGIN[ \t]+|DESTINATION[ \t]+)?'
                       r'((?:#[A-Za-z0-9_]+[ \t]+)?\^"[^"]+")')
TARGET = re.compile(r'(#[A-Za-z0-9_]+)?[ \t]*\^"([^"]+)"')

b_err = b_warn = b_sites = 0
amb_by_name = {}
for f in all_files:
    src = open(f, encoding='utf-8', errors='ignore').read()
    base = os.path.relpath(f, root)
    for m in (list(SITE.finditer(src)) + list(SITE_LIST.finditer(src))
              + list(PROP_REF.finditer(src)) + list(ALIAS_FOR.finditer(src))):
        if m.re is PROP_REF:
            kw, targets = 'property', m.group(1)
        elif m.re is ALIAS_FOR:
            kw, targets = 'ALIAS FOR', m.group(1)
        else:
            kw, targets = re.sub(r'\s+', ' ', m.group(1)), m.group(2)
        ln = src.count('\n', 0, m.start()) + 1
        for thash, tname in TARGET.findall(targets):
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
