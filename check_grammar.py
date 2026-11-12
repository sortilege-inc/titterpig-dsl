#!/usr/bin/env python3
"""
Titterpig DSL grammar check: run ttrpg.peg against files.

The grammar is the formal statement of the DSL's syntax. This tool is what runs it: a small
packrat interpreter for Bryan Ford's PEG notation, with no dependency. It reads ttrpg.peg as
written and parses each file whole, from the rule FILE.

  1. THE GRAMMAR ITSELF. Every rule a rule names must be defined, and every rule must be
     reachable from FILE or from an entry the grammar declares with a line
         # @entry RULE_NAME
     (a sub-grammar applied to part of a file, such as the text of a string). Either fault is
     an error and nothing is parsed.
  2. EACH FILE. Accepted, or refused with the line and column the parse could not get past
     and what the grammar wanted there. The position is the farthest any alternative reached.

The grammar says what is well-formed. It does not resolve a reference, check a type or count
anything: that is ttrpg_validator.py and check_references.py.

Usage:  check_grammar.py <file-or-dir> [more ...] [--grammar <ttrpg.peg>] [--expect-refused]
                         [--quiet] [--seconds N]

  --expect-refused   the files are syntax faults on purpose: the run fails if any is accepted
  --quiet            print the summary and the refusals only
  --seconds N        give up on a file after N seconds (default 30); counted as refused

Exit status: 0 when every file is accepted (or, with --expect-refused, every file is refused),
1 otherwise, 2 when the grammar itself is at fault or no file is found.
"""
import os
import re
import sys
import threading
import time

SPACE_RULES = ('_', 'SP', 'WHITESPACE', 'COMMENT', 'LINE_COMMENT', 'SLASH_COMMENT', 'EOL', 'B')
DSL_EXT = ('.ttrpg', '.actor', '.arc', '.frame', '.setting', '.campaign', '.bridge', '.codex',
           '.selections')
ESC = {'n': '\n', 't': '\t', 'r': '\r'}


class GrammarError(Exception):
    pass


class GaveUp(Exception):
    pass


def read_grammar(text):
    """ttrpg.peg -> (rules: name -> node, entries declared with `# @entry`)."""
    entries = re.findall(r'^#\s*@entry\s+([A-Za-z_][A-Za-z0-9_]*)', text, re.M)
    toks, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
        elif c == '#':                                   # a comment runs to the end of the line
            j = text.find('\n', i)
            i = n if j < 0 else j
        elif c in '\'"':                                 # a literal
            j, buf = i + 1, []
            while j < n and text[j] != c:
                if text[j] == '\\':
                    buf.append(ESC.get(text[j + 1], text[j + 1]))
                    j += 2
                else:
                    buf.append(text[j])
                    j += 1
            toks.append(('lit', ''.join(buf)))
            i = j + 1
        elif c == '[':                                   # a character class
            j, items = i + 1, []
            neg = text[j] == '^'
            if neg:
                j += 1

            def one(j):
                if text[j] == '\\':
                    return ESC.get(text[j + 1], text[j + 1]), j + 2
                return text[j], j + 1
            while text[j] != ']':
                a, j = one(j)
                if text[j] == '-' and text[j + 1] != ']':
                    b, j = one(j + 1)
                    items.append((a, b))
                else:
                    items.append((a, a))
            toks.append(('cls', (tuple(items), neg)))
            i = j + 1
        elif text.startswith('<-', i):
            toks.append(('arrow', None))
            i += 2
        elif c in '/&!?*+().':
            toks.append((c, None))
            i += 1
        else:
            m = re.match(r'[A-Za-z_][A-Za-z0-9_]*', text[i:])
            if not m:
                line = text.count('\n', 0, i) + 1
                raise GrammarError('line %d: %r is not PEG notation' % (line, text[i:i + 24].split('\n')[0]))
            toks.append(('id', m.group()))
            i += len(m.group())
    rules, p = {}, 0

    def at_rule_start(q):
        return q + 1 < len(toks) and toks[q][0] == 'id' and toks[q + 1][0] == 'arrow'

    def choice():
        nonlocal p
        alts = [sequence()]
        while p < len(toks) and toks[p][0] == '/':
            p += 1
            alts.append(sequence())
        return alts[0] if len(alts) == 1 else ('alt', alts)

    def sequence():
        nonlocal p
        items = []
        while p < len(toks) and toks[p][0] not in ('/', ')') and not at_rule_start(p):
            items.append(prefix())
        return items[0] if len(items) == 1 else ('seq', items)

    def prefix():
        nonlocal p
        k = toks[p][0]
        if k in ('&', '!'):
            p += 1
            return ('and' if k == '&' else 'not', suffix())
        return suffix()

    def suffix():
        nonlocal p
        x = primary()
        while p < len(toks) and toks[p][0] in ('?', '*', '+'):
            x = ({'?': 'opt', '*': 'star', '+': 'plus'}[toks[p][0]], x)
            p += 1
        return x

    def primary():
        nonlocal p
        if p >= len(toks):
            raise GrammarError('the grammar ends in the middle of a rule')
        k, v = toks[p]
        p += 1
        if k == 'id':
            return ('ref', v)
        if k in ('lit', 'cls'):
            return (k, v)
        if k == '.':
            return ('any',)
        if k == '(':
            x = choice()
            if p >= len(toks) or toks[p][0] != ')':
                raise GrammarError('a "(" is not closed')
            p += 1
            return x
        raise GrammarError('unexpected %r in a rule' % (k,))

    while p < len(toks):
        if not at_rule_start(p):
            raise GrammarError('expected "NAME <-", found %r' % (toks[p],))
        name = toks[p][1]
        p += 2
        if name in rules:
            raise GrammarError('rule %s is defined twice' % name)
        rules[name] = choice()
    return rules, entries


def names_in(node, acc):
    if node[0] == 'ref':
        acc.add(node[1])
    elif node[0] in ('seq', 'alt'):
        for x in node[1]:
            names_in(x, acc)
    elif node[0] in ('not', 'and', 'opt', 'star', 'plus'):
        names_in(node[1], acc)
    return acc


def grammar_faults(rules, entries, start='FILE'):
    """-> (undefined rule names, unreachable rule names)."""
    used = set()
    for body in rules.values():
        names_in(body, used)
    reach, todo = set(), [start] + list(entries)
    while todo:
        r = todo.pop()
        if r in reach or r not in rules:
            continue
        reach.add(r)
        todo.extend(names_in(rules[r], set()))
    undefined = sorted((used | set(entries) | {start}) - set(rules))
    return undefined, sorted(set(rules) - reach)


class Parser:
    def __init__(self, rules, seconds=30):
        self.rules, self.seconds = rules, seconds

    def parse(self, text, start='FILE'):
        self.t, self.n = text, len(text)
        self.memo, self.far, self.want, self.stack = {}, 0, [], []
        self.calls, self.deadline = 0, time.time() + self.seconds
        return self.rule(start, 0)

    def rule(self, name, pos):
        key = (name, pos)
        if key in self.memo:
            return self.memo[key]
        self.calls += 1
        if self.calls % 20000 == 0 and time.time() > self.deadline:
            raise GaveUp()
        self.stack.append(name)
        r = self.m(self.rules[name], pos)
        self.stack.pop()
        self.memo[key] = r
        return r

    def miss(self, pos, what):
        # the farthest point any alternative reached, and what the grammar wanted there;
        # a miss while skipping space says nothing about the statement, so it is not kept
        if pos >= self.far:
            if pos > self.far:
                self.far, self.want = pos, []
            if self.stack and self.stack[-1] not in SPACE_RULES:
                entry = (what, self.stack[-1])
                if entry not in self.want and len(self.want) < 6:
                    self.want.append(entry)
        return -1

    def m(self, node, pos):
        k = node[0]
        if k == 'lit':
            return pos + len(node[1]) if self.t.startswith(node[1], pos) else self.miss(pos, repr(node[1]))
        if k == 'ref':
            return self.rule(node[1], pos)
        if k == 'seq':
            for x in node[1]:
                pos = self.m(x, pos)
                if pos < 0:
                    return -1
            return pos
        if k == 'alt':
            for x in node[1]:
                r = self.m(x, pos)
                if r >= 0:
                    return r
            return -1
        if k in ('star', 'plus'):
            if k == 'plus':
                pos = self.m(node[1], pos)
                if pos < 0:
                    return -1
            while True:
                r = self.m(node[1], pos)
                if r < 0 or r == pos:
                    return pos
                pos = r
        if k == 'opt':
            r = self.m(node[1], pos)
            return pos if r < 0 else r
        if k == 'not':
            far, want = self.far, self.want
            r = self.m(node[1], pos)
            self.far, self.want = far, want
            return pos if r < 0 else -1
        if k == 'and':
            return pos if self.m(node[1], pos) >= 0 else -1
        if k == 'any':
            return pos + 1 if pos < self.n else self.miss(pos, 'more text')
        if k == 'cls':
            if pos < self.n:
                c = self.t[pos]
                items, neg = node[1]
                if any(a <= c <= b for a, b in items) != neg:
                    return pos + 1
            return self.miss(pos, 'another character')
        raise AssertionError(k)


def check_file(parser, path):
    """-> ('accepted', None) or ('refused', (line, column, line text, wanted, in rules))."""
    with open(path, encoding='utf-8', errors='replace') as fh:
        text = fh.read()
    try:
        end = parser.parse(text)
    except GaveUp:
        return 'refused', (0, 0, '', 'gave up after %d seconds' % parser.seconds, ())
    except RecursionError:
        return 'refused', (0, 0, '', 'nested too deeply to parse', ())
    if end == len(text):
        return 'accepted', None
    pos = max(parser.far, end)
    line = text.count('\n', 0, pos) + 1
    start = text.rfind('\n', 0, pos) + 1
    stop = text.find('\n', pos)
    stop = len(text) if stop < 0 else stop
    if parser.want and pos == parser.far:
        what = ' or '.join(sorted({w for w, _ in parser.want}))
        inside = tuple(sorted({r for _, r in parser.want}))
    else:
        what, inside = 'the end of the file', ()
    return 'refused', (line, pos - start + 1, text[start:stop].strip()[:120], what, inside)


def collect(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, names in os.walk(p):
                out.extend(os.path.join(root, nm) for nm in names if nm.endswith(DSL_EXT))
        elif os.path.isfile(p):
            out.append(p)
        else:
            print('no such file or directory: %s' % p, file=sys.stderr)
    return sorted(out)


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__))
    grammar, paths, expect_refused, quiet, seconds = os.path.join(here, 'ttrpg.peg'), [], False, False, 30
    it = iter(argv[1:])
    for a in it:
        if a == '--grammar':
            grammar = next(it, '')
        elif a == '--expect-refused':
            expect_refused = True
        elif a == '--quiet':
            quiet = True
        elif a == '--seconds':
            seconds = int(next(it, '30'))
        else:
            paths.append(a)
    try:
        with open(grammar, encoding='utf-8') as fh:
            rules, entries = read_grammar(fh.read())
    except (OSError, GrammarError) as exc:
        print('GRAMMAR: cannot read %s: %s' % (grammar, exc), file=sys.stderr)
        return 2
    undefined, unreachable = grammar_faults(rules, entries)
    print('GRAMMAR: %d rule(s) in %s | %d undefined | %d unreachable'
          % (len(rules), os.path.basename(grammar), len(undefined), len(unreachable)))
    for nm in undefined:
        print('  ERROR rule %s is named and not defined' % nm)
    for nm in unreachable:
        print('  ERROR rule %s is reachable from neither FILE nor an @entry' % nm)
    if undefined or unreachable:
        return 2
    if not paths:
        print('usage: check_grammar.py <file-or-dir> [more ...] [--grammar <ttrpg.peg>] '
              '[--expect-refused] [--quiet] [--seconds N]', file=sys.stderr)
        return 0
    files = collect(paths)
    if not files:
        print('no DSL files found', file=sys.stderr)
        return 2
    parser = Parser(rules, seconds)
    accepted = refused = 0
    for path in files:
        status, info = check_file(parser, path)
        if status == 'accepted':
            accepted += 1
            if expect_refused:
                print('  ERROR %s: accepted, and it is a planted syntax fault' % path)
            elif not quiet:
                print('  ok      %s' % path)
        else:
            refused += 1
            line, col, src, what, inside = info
            tag = 'refused' if expect_refused else 'ERROR  '
            if not (quiet and expect_refused):
                print('  %s %s:%d:%d  wanted %s%s' % (tag, path, line, col, what,
                                                      ' (in %s)' % ', '.join(inside) if inside else ''))
                if src:
                    print('          %s' % src)
    print('GRAMMAR: %d file(s) | %d accepted | %d refused' % (len(files), accepted, refused))
    bad = accepted if expect_refused else refused
    return 1 if bad else 0


def _run():
    sys.setrecursionlimit(200000)
    threading.stack_size(512 * 1024 * 1024)       # the parser recurses as deep as the file nests
    box = []
    th = threading.Thread(target=lambda: box.append(main(sys.argv)))
    th.start()
    th.join()
    sys.exit(box[0] if box else 2)


if __name__ == '__main__':
    _run()
