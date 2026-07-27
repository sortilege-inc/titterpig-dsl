import os,re,sys
root=sys.argv[1]
DEF=re.compile(r'^\s*(?:#\S+\s+)?(?:\^"([^"]+)"|(?:TEMPLATE|ACTOR)\s+"([^"]+)")\s+DEF\b')
DESC=re.compile(r'^\s*DESCRIPTION\s+"(.*)"\s*$')
MENT=re.compile(r'^\s*"([^"]+)"\s*->\s*\^"([^"]+)"\s*$')
nk=lambda s:re.sub(r'[^a-z0-9]+','',s.strip().replace('’',"'").lower())
declared=set()
files=[os.path.join(dp,f) for dp,_,fs in os.walk(root) for f in fs if f.endswith('.ttrpg')]
for f in files:
    for l in open(f,encoding='utf-8'):
        m=DEF.match(l)
        if m: declared.add(nk(m.group(1) or m.group(2)))
bad_t=bad_s=total=0
for f in files:
    desc=None
    for l in open(f,encoding='utf-8').read().split('\n'):
        d=DESC.match(l)
        if d: desc=d.group(1)
        m=MENT.match(l)
        if m:
            total+=1; surface,target=m.group(1),m.group(2)
            if nk(target) not in declared: bad_t+=1; print(f'  UNRESOLVED target ^"{target}" in {os.path.basename(f)}')
            if desc is not None and surface not in desc: bad_s+=1; print(f'  SURFACE not in desc: "{surface}" ({os.path.basename(f)})')
print(f'MENTIONS: {total} total | {bad_t} unresolved targets | {bad_s} surface-not-in-desc')
sys.exit(1 if bad_t or bad_s else 0)
