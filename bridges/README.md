# bridges/ — cross-edition conversions

`.bridge` files, spec **§21**. They live here, in the canonical DSL repo, rather than in either
game's repo: a bridge belongs to **neither** edition.

An edition is an *identity namespace* (§19): hash identity is stable within it and carries none
across it. Every other container has exactly one dependency lineage. A published
edition-conversion document asserts the thing §19 forbids inside a namespace — *this older-edition
thing became that newer-edition thing* — and inherently has **two**. That is the gap `.bridge` fills.

A bridge does not re-establish identity across editions. It records a **directed, third-party
assertion of correspondence**, machine-readable, so that §19's "derived artifact, not an automatic
overlay" can actually be generated and audited.

## Contents

| File | Origin → Destination | Shape |
|---|---|---|
| `0.4/dnd5e-to-dnd5.5e-0.5-srd-conversion.bridge` | `dnd5e` → `dnd5.5e` | The **rich** case: WotC's *Converting to System Reference Document 5.2.1*, entity-keyed throughout — 573 `MAP`s, 7 `REMAINDER`s, 85 `GUIDANCE` entries, the document's own four-tag disposition vocabulary. |
| `0.4/arm4-to-arm5e-0.5-appendix-i.bridge` | `arm4` *(EXTERNAL)* → `arm5e` | The **sparse** case: *Ars Magica Fifth Edition*, Appendix I — ~85% prose, no mapping table at all. No `MAP`, no `REMAINDER`, no `DISPOSITIONS`; 7 field-level `PROCEDURE`s + 11 `GUIDANCE` entries. |

The two are complementary on purpose: one is a publisher-facing *content changelog*, the other a
table-facing *character-conversion procedure*. The same grammar holds both.

## When the document and the edition disagree

WotC's own conversion guide names three things differently from the SRDs it describes —
`Contract Patron` (SRD: *Contact* Patron), `Dark One's Own Blessing` (SRD: Dark One's Blessing) and
`Perfect Body` (SRD 5.1: Perfect Self). The bridge keeps the guide's wording at the point of use and
reconciles it in an `ALIASES` block (spec §21), so nothing is silently retyped and no real
correspondence is left untyped. The corpora are right; the guide is wrong.

## A bridge lives here, not in either corpus

A `.bridge` belongs to **neither** edition. Inside an edition's directory its origin references
would not resolve and its own names would pollute that namespace. The validator enforces the
separation: a bridge's names never join the single-edition namespace, and its references are
resolved per side.

## Validating

Two-corpus mode. Each side's references resolve against **that side's** corpus, never the other's
and never the union:

```bash
# from titterpig-dsl/bridges/
python3 ../ttrpg_validator.py 0.4/ \
    --corpus dnd5e="../../titterpig-dsl-dnd5e/0.5" \
    --corpus dnd5.5e="../../titterpig-dsl-dnd5.5e/0.5" \
    --corpus arm5e="../../titterpig-dsl-arm5e/arm5e/0.5"
```

A non-`EXTERNAL` side with no `--corpus` mapping is an **error**, not a pass: an unchecked
cross-edition reference is exactly the rot a bridge exists to prevent. A side declared
`EXTERNAL "reason"` (Ars Magica 4th has no titterpig corpus) reports how many of its references
could not be verified, rather than passing them silently.

## All gates

Validation is not completeness. Run everything:

```bash
bash "../../../Titterpig Utilities/titterpig-mastra/scripts/bridge/gates.sh"
```

1. **Validator**, two-corpus mode, plus the `tests/good.bridge` / `tests/bad.bridge` fixtures.
2. **Coverage** — every enumerable unit of each source document covered or dispositioned with a
   reason (`coverage/dnd5e-to-dnd5.5e-bridge.manifest.json`,
   `coverage/arm4-to-arm5e-bridge.manifest.json`), and the arm5e corebook gate still green with
   Appendix I now dispositioned *converted elsewhere* instead of deferred.
3. **Verbatim** — every paragraph and every bullet of the SRD 5.2.1 document reproduced character
   for character. Headings are excluded on purpose: a unit heading is a structured assertion
   (referent + disposition tag set), and copying `"D20 Test [New Name]"` as a literal string would be
   the data-trapped-in-a-string the spec forbids.

## Regenerating the D&D bridge

It is generated, not hand-written — `titterpig-mastra/scripts/bridge/`:

```bash
python3 parse_srd521.py      # PDF XML -> blocks.json     (font-driven, no wording heuristics)
python3 units_srd521.py      # blocks  -> units.json      (a unit is any heading carrying a [Tag])
python3 index_corpus.py <edition-dir> idx-<edition>.json
python3 gen_bridge.py        # units + corpus indexes -> .bridge + inventory + routing report
```

The ArM5 bridge is hand-authored; at 44 source units, a generator would be more code than content.
