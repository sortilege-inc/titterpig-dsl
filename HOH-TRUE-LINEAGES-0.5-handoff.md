# RESUME — 0.5 version-dir migration, then Houses of Hermes: True Lineages → DSL 0.5

Authoritative plan + state for the next session. The paste-able kickoff prompt is at the bottom.

---

## WHERE WE ARE (all PROVEN; committed + pushed unless noted)

**Both arm5e editions are complete at DSL 0.5**, gates green:
- arm5e: validator 105 files 0/0 · check_references 1801 refs / 0 err / **0 hashless** · check_constructs 0 err · coverage **core + 5 supplements ALL PASS**
- armdef: validator 41/0/0 · refs 1431 / 0 err / 0 hashless · constructs 0 err · coverage PASS
- Latest commits: arm5e `94f914e` · mastra `234bb21` · dsl `df12989`. All three repos clean, 0 unpushed.

**Done in the previous session** (detail in `DSL-0.5-worklog.md`): grogs GUIDANCE (131 editorial
records), the 217-sidebar backfill across 4 supplements, full hashless disambiguation (150→0,
owner-reviewed per cluster), duplicate-table consolidation, and the core Houses restructure
(mechanical DEF + verbatim `arm5e-0.5-houses.lore`).

**Houses of Hermes: True Lineages** — extraction DONE + verified; DSL foundation laid:
- Source HTML + toc at `~/Working/arm5e-sourcebook-conversions/houses-true-lineages/`
  (`toc.txt` = 528 units: 428 Heading / 93 Text Box / 7 Table).
- Pipeline profile `houses-true-lineages` added to `arm5e-sourcebook-conversions/scripts/books.py`.
- Corpus dir + `…-core-ext.ttrpg` created (currently under `arm5e/0.5/houses-true-lineages/`).
- Coverage manifest `titterpig-mastra/coverage/arm5e-houses-true-lineages.manifest.json` created.
  **Baseline: 586 inventory units, 576 UNCOVERED** (489 Heading, 91 Text Box, 6 Table) = the scope.

---

## PHASE 0 — 0.5 version-dir migration — **DONE + PROVEN 2026-07-27** (detail in `DSL-0.5-worklog.md`)

Owner-confirmed decisions (2026-07-27):
1. **`git mv` rename, not copy+freeze.** The files in `0.4/` are already `SPEC_VERSION "0.5"` /
   `VERSION "0.5.0"`, so the dir name is simply stale; the true 0.4-spec state is preserved in git
   history. No frozen `0.4/` snapshot is left behind. (`arm5e/0.1`, `0.2`, `0.3` stay as-is.)
2. **Both editions, each to its OWN 0.5 dir** — `arm5e/0.5` → `arm5e/0.5` and `armdef/0.5` →
   `armdef/0.5`. **Keep the edition-first structure**; do NOT create a top-level `0.5/` with
   `arm5e`/`armdef` children (the owner confirmed the current layout is deliberate).
3. **Rename the `-0.4-` filename segment to `-0.5-`** (201 files).

Steps:
- `git mv` the two dirs, then `git mv` each file `*-0.4-*` → `*-0.5-*` (preserves history).
- Update in-repo references: `sources.json` (153 entries — the arm5e one; armdef has none),
  plus any `.ttrpg`/`.lore` comment text naming a `-0.4-` file (74 files mention "0.4" — most will
  be VERSION strings that must NOT change, so match on the filename pattern, not bare "0.4").
  `DEPENDS_ON` uses file-IDs, not filenames — verify it is unaffected.
- Update external references (~15 files):
  `titterpig-mastra/coverage/*.manifest.json` (7: arm5e-corebook, -covenants, -grogs, -hedge-magic,
  -rop-faerie, -rop-magic, -houses-true-lineages, + armdef.manifest.json) → `corpusDirs`;
  `titterpig-mastra/scripts/` (genArm5eCore.ts, buildRopMagic.ts, buildRopMagicGaps.ts,
  genArm5eRopMagicLore.ts, genArmdefCoreBase.ts, genArmdefCoreCreation.ts, genArmdefLore.ts,
  addArmdefParamAbilities.ts, migrateArmdefDecision6Phase1.ts, gates.sh, arm5eFinalGates.sh);
  `titterpig-dsl/DSL-0.5-worklog.md`.
- **Leave `TOR2E_04` alone** — it points at `titterpig-dsl-tor2e/0.4`, a different repo still at spec 0.4.
- **Prove it:** re-run validator / check_references / check_constructs on `arm5e/0.5` + `armdef/0.5`,
  and all 8 coverage manifests. Expect the same numbers as above (105/0/0, 41/0/0, 0 hashless, all PASS).
  Commit + push all three repos.

---

## PHASE 1 — True Lineages → DSL 0.5 (the book itself)

Target: `titterpig-dsl-arm5e/arm5e/0.5/houses-true-lineages/`, files
`arm5e-houses-true-lineages-0.5-<facet>.{ttrpg,lore}`, EXTENSIONs on arm5e core.
**Built at 0.5 from the start** — there is no separate "migrate later" step.

The book is **narrative-heavy with a modest mechanical set** (unlike record-dense RoP:Magic), so the
approach is **deterministic hand-conversion in the main loop**, NOT the mastra LLM pipeline.

Chapter map (from `toc.txt`):
| Ch | House | pp | Mechanical content to look for |
|---|---|---|---|
| 1 | **Bonisagus** | 4–34 | House Acclaim & folios, Original Research, Example Discoveries, Seekers |
| 2 | **Guernicus** | 35–77 | Code of Hermes, Tribunal Procedures, Penalties, Quaesitorial Magic, **Fenicil's Rituals** |
| 3 | **Mercere** | 78–109 | Redcaps, Magical Merceres, Laboratory Rules, **Spells**, Magic Rules, V/F |
| 4 | **Tremere** | 110–143 | Structure, Promotion by Force, **Dueling** (Certamen), **New Spells** |
| — | Appendix | 144 | Timeline |

Per chapter, in this order:
1. **Narrative → `.lore`**, verbatim slices (bulk of the book). Its in-chapter headings are then
   matched by `.lore` basename in coverage.
2. **Mechanical records → `.ttrpg`**, verbatim: new Virtues/Flaws (they fit core `^"Virtue"`/`^"Flaw"`
   unchanged), spells (fit core `^"Hermetic Spell"`), House systems. Declare any genuinely-new type in
   the `core-ext` file as you go.
3. **Sidebars → `GUIDANCE`** (91 of them: Story Seeds, `Exempli Gratia` worked examples, rules boxes,
   `Optional Rule:` boxes → consider `OPTIONAL`).
4. **Tables → structured `TABLE` DEFs** — never flatten a table into a prose string (prime directive).
5. **Disposition** any remaining headings in the manifest, with reasons.

**These records point at the canonical `^"House X"` DEFs** in `arm5e-0.5-houses.ttrpg` (Bonisagus
`#tEpsENC1YOKKY8hnFvGCRIgs`, Guernicus `#t8lCseUrOPStliSwafwQWbgT`, Mercere `#tcY8OdMIdtd4uJOImrJcxvsl`,
Tremere `#tcrOTdy0EVl42G3i0XxK9qJC`) — just restructured, so they are clean anchor targets.

**Pilot before scaling:** do Chapter One (Bonisagus) end-to-end, verify verbatim + gates + its slice of
coverage, THEN repeat the proven shape for Guernicus / Mercere / Tremere.

---

## PHASE 2 — finalize True Lineages
Coverage to **0 uncovered** (or explicitly deferred/excluded *with a reason*, the owner's call — never
rubber-stamp). `sources.json` synced. All gates green on the whole `arm5e/0.5` dir. Commit + push.
Update `DSL-0.5-worklog.md`.

## LATER — the other two Houses of Hermes books
Extraction not started. Each needs its **own** pipeline profile (same GoudyTextMT-LombardicCap/Weiss
family, different heading sizes — do NOT copy True Lineages' thresholds blind):
- **Societates**: 28 (H1) / 18 (H2) / 14 (verify: House titles vs Contents/running-header furniture).
- **Mystery Cults**: three levels — 48 (H1) / 28 (H2) / 18 (H3).
Recipe + calibration notes in `arm5e-sourcebook-conversions/STATE-OF-PLAY.md`.

---

## TOOLING + METHOD (proven last session; now in durable homes)

- **Extraction**: `arm5e-sourcebook-conversions/scripts/` — `run_extract.py <book-key>`,
  `render_html.py` (reads `ARM5E_BOOK` env), `make_toc.py <book-key>`, `survey_fonts.py <pdf> [pages]`,
  profiles in `books.py`. Python is `arm5e-sourcebook-conversions/pdfenv/bin/python` (PyMuPDF).
- **Verbatim source-slicing**: `scripts/srcextract.py` (copied from session scratchpad, verified on
  True Lineages: 514 headings indexed). `build_index()` bounds a body at the next heading **OR the
  enclosing sidebar `</div>`** (this was the crux — without it, 32 grogs records over-grabbed into main
  text), coalesces truncated heading-fragments, preserves emphasis (`<em>`→`*`, `<strong>`→`**`), and
  rejoins PDF span-split words. `parse_table()` → (columns, rows) for TABLE DEFs.
  `scripts/backfill_sidebars.py` emits GUIDANCE + TABLE DEFs from a list of uncovered units.
- **Verbatim assertion**: token-subsequence check against the source with the same normalizations —
  every emitted TEXT must pass. This is what caught the paraphrase/stub cases.
- **Gates** (in `titterpig-dsl`, run on the whole edition dir):
  `ttrpg_validator.py`, `check_references.py` (`--show-warns` lists hashless), `check_constructs.py`,
  `apply_references.py`. Coverage: `titterpig-mastra/scripts/coverageAudit.ts <manifest>` with
  `TOR2E_04="/home/hewhocutsdown/Working/Titterpig DSL/titterpig-dsl-tor2e/0.4"`.

### Hard-won rules — do not relearn these
- **Never re-run `apply_references.py --only=<subdir>` on a supplement after its disambiguation** — it
  strips the manual `#hash`es (it did exactly this to grogs' House refs last session).
- **A `GUIDANCE ENTRY` is NOT a ref-able anchor.** Both gates collect anchors only from `DEF` lines, so
  converting a referenced DEF into GUIDANCE breaks inbound refs. Check inbound refs first.
- **Coverage matches by name** — keep the source's unit name as the `ENTRY`/DEF name or the unit falls
  uncovered. And a coverage PASS on an EMPTY inventory is vacuous: always check `inventory units:` > 0.
- **Validation ≠ completeness.** Coverage is measured against the source's enumerable sets.

---

## DISCIPLINE
Main loop; deterministic-first; pilot one unit and verify byte-for-byte before scaling; report
**PROVEN / UNVERIFIED / FAILED** with the command and its result in the same message; no long-running
agents; keep `DSL-0.5-worklog.md` current as you go. **Ask the owner for context instead of spinning
out on investigation** — bring decisions executive-ready (concrete example, trade-off, recommendation)
in one pass, and review nuanced clusters one at a time.

---

## KICKOFF PROMPT (paste this into the fresh context)

> Continue the Ars Magica work in `titterpig-dsl-arm5e`. Two jobs, in order.
>
> **READ FIRST:** `~/CLAUDE.md`; `titterpig-dsl/HOH-TRUE-LINEAGES-0.5-handoff.md` (authoritative plan
> — read it fully); `titterpig-dsl/DSL-0.5-worklog.md`; the `titterpig-dsl` skill.
>
> **Phase 0 — 0.5 version-dir migration.** Both editions are complete at DSL 0.5 but still live in
> `0.4/` dirs with `-0.4-` filenames. Owner-confirmed: `git mv arm5e/0.5 → arm5e/0.5` and
> `armdef/0.5 → armdef/0.5` (keep the edition-first layout — do NOT create a top-level `0.5/`);
> rename the 201 `-0.4-` filenames to `-0.5-`; update `sources.json`, the 8 mastra coverage manifests,
> the mastra scripts/gates, and the worklog. Leave `TOR2E_04` (different repo) alone. Prove every gate
> matches the pre-migration numbers (arm5e 105/0/0 · 0 hashless · armdef 41/0/0 · all 8 coverage PASS),
> then commit + push all three repos.
>
> **Phase 1 — Houses of Hermes: True Lineages → DSL 0.5.** Extraction is done and verified; the corpus
> foundation + coverage manifest exist (baseline 586 units / 576 uncovered). Convert the book
> deterministically in the main loop into `arm5e/0.5/houses-true-lineages/`, built at 0.5 from the
> start. Pilot **Chapter One (House Bonisagus)** end-to-end — narrative → verbatim `.lore`, new
> Virtues/Flaws + House Acclaim/folios/Original Research → `.ttrpg`, Story-Seed and worked-example
> sidebars → `GUIDANCE`, tables → structured `TABLE` DEFs — verify verbatim + gates + coverage, then
> repeat for Guernicus, Mercere, Tremere.
>
> Discipline: deterministic-first, pilot-before-scale, prove every gate with command + result
> (PROVEN/UNVERIFIED/FAILED), no long agents, keep the worklog current, and **ask me rather than
> spinning out** — surface decisions executive-ready, one cluster at a time.


---

# STOPPED HERE (2026-07-27) — Phase 0 + the Chapter One pilot are DONE, PROVEN, committed, pushed.

**Done and green:** Phase 0 version-dir migration; the arm4→arm5e bridge fix (owner: revert
`^"Starting Character Age"` to a DEF) + the bridge wired into `arm5eFinalGates.sh`; Chapter One
(House Bonisagus, pp.4–34) fully converted with named characters as `.actor` (owner decision).
Commits: arm5e `e8f3597` · mastra `d397f4a` · dsl `481e3f3`. All three clean, 0 unpushed.

**Remaining: Chapters 2–4** — Guernicus (pp.35–77) · Mercere (78–109) · Tremere (110–143) ·
Appendix Timeline (144). Book-wide coverage is 89 covered / 40 excluded / **457 uncovered** = exactly
those three chapters. Nothing else is outstanding.

## The tooling is durable and PROVEN — reuse it, do not rebuild it
All in `arm5e-sourcebook-conversions/scripts/` (moved out of the session scratchpad and re-verified
from that location: re-running the generator reproduces the committed Chapter One corpus **byte for
byte**, `git diff` empty).

| File | What it does |
|---|---|
| `pageslice.py` | **The slicer.** Partitions every unit on a page range into exactly one main section or sidebar, from the page JSON's explicit `box_open`/`box_close` stream. Complete by construction. Also `rejoin()` (emphasis-split hyphenation) and `deligature()`. |
| `dslemit.py` | DSL emission + the **verbatim gate** (`verbatim()` — token-subsequence vs the de-ligatured source; `report()` exits 1 on any failure), `clean_grid`, `fit_columns`, `hid`, `q`. |
| `covercheck.py` | **The completeness gate.** `covercheck.py <lo> <hi> <corpus files…>` — every source unit on those pages must be present; reports LOST tokens and exits 1. Split-tolerant, so structuring a stat block into typed fields is not mistaken for loss. |
| `pagecheck.py` | Stricter contiguous-only variant; use it to see what got structured. |
| `repair.py` | Contiguity helper for column-order artifacts (see the caveat below). |
| `gen_hoh_bonisagus.py` + `hoh_bonisagus_spec.py` | **The worked example — copy this shape for each chapter.** |

## Recipe per chapter (this is exactly what Chapter One did)
1. `python3 scripts/pageslice.py <lo> <hi>` — read the section/sidebar map.
2. **Find the column-order artifacts.** A display heading set mid-column makes the stream emit the
   heading BEFORE the preceding column's tail paragraphs. Detector: a section whose first paragraph
   starts lowercase / mid-sentence, or an h1 with 0 units. For Chapter Two this flags exactly four —
   **p42 `Organization`, p59 `Penalties`, p69 `Running Stories for a Quaesitor`, p70 `Quaesitorial
   Magic`** (each visibly continues the previous section: p42's begins `"eral conflict…"` completing
   `"…in times of gen-"`). ⚠ `repair.py`'s automatic contiguity proof does NOT fire here — the source
   HTML interleaves the sidebar between them, so the two paragraphs are not adjacent in the HTML token
   stream either. **Render the page and confirm by eye**, then encode an explicit `REASSIGN` entry
   exactly as `hoh_bonisagus_spec.py` does:
   `pdftoppm -f <pg> -l <pg> -r 120 -png "~/Working/Arm5e Sourcebooks/Houses of Hermes - True Lineages.pdf" out/p`
3. Write `gen_hoh_<house>.py` on the `gen_hoh_bonisagus.py` shape: narrative → verbatim `.lore`;
   mechanics → typed DEFs; every sidebar → GUIDANCE / OPTIONAL / TABLE DEF; named characters → the
   `.actor`. Declare any genuinely new type in `core-ext`.
4. **Gate, in this order:** the generator's own verbatim gate → `covercheck.py <lo> <hi> …` must report
   **0 WITH LOST TOKENS** → `ttrpg_validator.py arm5e/0.5` → `check_references.py` → `check_constructs.py`
   → `coverageAudit.ts` (chapter slice must be 0 uncovered) → sync `sources.json`.

## What Chapter Two contains (surveyed: 140 main sections, 27 sidebars)
Narrative (History, Organization, Guernicus Magi, Running Stories) → `.lore`. Mechanical sets that are
**enumerable and must each become a record**: the **17 Code of Hermes clauses** (Deprivation of Magical
Power … Enemies and Allies) · the Peripheral Code (3) · Tribunal Procedures (Preparing/Presenting a
Case, Acquittal, Conviction) · Penalties (Damages/Fines/Punishments + 6 punishments incl. Loss/Death of
Familiar) · Quaesitorial Duties and Powers (~10) · **~25 new spells** in Quaesitorial Magic, each with
an `R:/D:/T:/Level` stat line to parse into Technique/Form/Level like
`^"Reveal the Lingering Spirit"` · 5 guideline blocks · **Fenicil's Rituals** (3 Greater + 5 Lesser) ·
Shroud Magic. Note pp.61/70/76 have h1 headings with 0 units whose following h4s belong to the
*previous* section (Loss/Death of Familiar are Punishments) — grouping only, no text is lost.

## Also flagged
- ⚠ **`books.py` extraction-profile gap:** the `houses-true-lineages` profile does not de-ligature
  (`reﬁne`), unlike every other arm5e book — the committed corpus contains zero ligature characters.
  Chapter One normalizes downstream in `dslemit`/`pageslice`. **Fix the profile before extracting
  Societates and Mystery Cults**, or they inherit the same defect.
- The other two Houses of Hermes books still need extraction; each needs its OWN profile (heading
  thresholds in the section above — do not copy True Lineages' blind).
