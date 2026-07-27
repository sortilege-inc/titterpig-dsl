# RESUME PROMPT — arm5e supplements → 0.5.0 (parity with core)

Paste this into a new chat to continue.

---

Continue converting the **5 arm5e supplements** to a good 0.5.0 (parity with the already-finished
arm5e core + armdef core). Supplements, in the owner's order: **hedge-magic, covenants, RoP Magic,
Grogs, RoP Faerie** — they live in `titterpig-dsl-arm5e/arm5e/0.4/{hedge-magic,covenants,rop-magic,grogs,rop-faerie}/`
and are EXTENSIONs depending on arm5e core.

## READ FIRST
- `~/CLAUDE.md` (working agreement: truth-in-reporting with command+result; deterministic-first,
  pilot-before-scale; no long background agents; drive to completion or hand off; keep the worklog
  current; **never convert a subset and call it done**; decisions come executive-ready).
- `titterpig-dsl/DSL-0.5-worklog.md` (the running decision log / source of truth).
- The `titterpig-dsl` skill (validation, migration recipe, git conventions).

## ENV / PATHS
- Corpus: `~/Working/Titterpig DSL/titterpig-dsl-arm5e/arm5e/0.4` (core = 34 root .ttrpg + `spells/`;
  supplements = the 5 subdirs).
- Gates live in `~/Working/Titterpig DSL/titterpig-dsl`: `ttrpg_validator.py`, `check_references.py`,
  `check_constructs.py`, `apply_references.py`.
- Coverage: `~/Working/Titterpig Utilities/titterpig-mastra/scripts/coverageAudit.ts` — needs
  `TOR2E_04="/home/hewhocutsdown/Working/Titterpig DSL/titterpig-dsl-tor2e/0.4"`. Supplement manifests:
  `titterpig-mastra/coverage/arm5e-{covenants,grogs,hedge-magic,rop-faerie,rop-magic}.manifest.json`.
- Supplement source HTML (for GUIDANCE verbatim): `~/Working/arm5e-sourcebook-conversions/<name>/*.html`.
- Run validator/references/constructs on the whole `arm5e/0.4` dir (cross-file refs resolve there).

## STATE — all committed + pushed (git clean, 0 unpushed). Latest arm5e commit `73bb309`.
Both **cores are done at 0.5.0** (gates green). Supplements progress:
- **DONE — version + REFERENCES-hash (all 5)** (commit `2b3bb94`): every supplement file at
  `SPEC_VERSION "0.5"` / `VERSION "0.5.0"`; MENTIONS→REFERENCES-hashed via
  `apply_references.py <arm5e/0.4> --only=<subdir>` (new `--only` flag: resolves anchors against
  core-root + that supplement, writes only that supplement — does NOT re-touch core / regress core
  disambiguation). Validator 100 files 0/0, 0 ref errors.
- **DONE — Power-types + House disambiguation (owner-reviewed)** (commit `73bb309`):
  - **Power types (rop-magic), per-reference with owner:** Greater 36 (7 Virtue / 29 Magic Quality),
    Personal 13 (all MQ), Lesser 12 (7 V / 5 MQ), Ritual 21 (all MQ), Focus 7 (1 V = *Wizard's
    Communion*, source-flagged / 6 MQ). **RULE (owner-confirmed):** a "[X] Power" reference inside a
    **Thing of Virtue** or a **character Virtue/Flaw** entry = the **Virtue** (item/character holds
    it); a **creature's own power stat-line** (creature-powers / common-magic-powers, form
    `"…: Greater Power (N levels, –M Might cost)"`) = the **Magic Quality**. Read each — the by-file
    rule breaks (Wizard's Communion is in creature-powers but the source says "to be taken as a Virtue").
  - **Houses (all 5 supplements):** 32 refs pointed at the **canonical `houses.ttrpg` DEF**
    (`EXTENDS "Hermetic House"`) per owner ruling.
- Hashless: **274 → 153 remain.**

## REMAINING WORK

### A. Finish supplement hashless disambiguation (153) — ONE AT A TIME with the owner
Owner wants each nuanced cluster reviewed individually (like the Power types), not blanket-applied.
Workflow per name: (1) list the hashless refs — `grep -rn '"<Name>" -> \^"<Name>"$' <supp>/*.ttrpg`;
(2) for each, show enclosing DEF + the DESCRIPTION sentence (context) so the owner can judge;
(3) find candidate anchors — `grep -rnoE '#\w+ \^"<Name>" DEF' arm5e/0.4/*.ttrpg <supp>/*.ttrpg`
(EXTENDS line tells you Virtue vs Ability vs Magic Quality vs House);
(4) apply the chosen `#hash` per-reference by replacing `-> ^"<Name>"` with `-> #hash ^"<Name>"`
(per-DEF or per-file as the context dictates); (5) verify `validator 0/0` + that name's hashless = 0.

Remaining clusters (count = hashless refs) with the proposed target — **CONFIRM each with owner**:
- **The Gift 54, The Church 6, Parma Magica 4** → the core **concept** in `core-systems.ttrpg`
  (not the incidental re-mentions in hermetic-magic / virtues / mythic-europe). Likely low-nuance but review.
- **Second Sight 18, Animal Ken 4, Wilderness Sense 3, Magic Sensitivity 2, Magical Meditation 2**
  → the **Ability** (abilities.ttrpg) rather than the same-named Virtue. **CAUTION: may have the same
  Ability-vs-Virtue nuance as the Power types** — read each (a ref granting/being the character trait
  may mean the Virtue). Magical Meditation's other anchor is a Magic Quality, not a Virtue.
- **Faerie Blood 16** (rop-faerie) → 3 anchors: core Virtue (virtues.ttrpg), `rop-faerie-0.4-blood.ttrpg`,
  and a re-export stub `#tFaerieBloodRoPFaerieBaseXX` in `rop-faerie-0.4-core-ext.ttrpg`. Owner call.
- **Elementalist Water/Fire/Earth/Air 19** (hedge-magic) → the **Hedge Art** (`hedge-arts.ttrpg`) vs the
  **Virtue** (`virtues-flaws.ttrpg`). Read each — likely a mix. Owner call.
- **Failed Apprentice 11** (grogs) → the core **Virtue** (virtues.ttrpg) vs the grog **Training Package**
  (`grogs-0.4-training-packages.ttrpg`). Owner call.
- **True Faith 4** → the **Virtue** (virtues.ttrpg), not the realms mention. **Ghostly Warder 2** → the
  **Virtue**, not the bestiary-magic creature.
- **Animal Trainer 2** (grogs) → only one anchor (grog Training Package) — point there.
- **4 rop-faerie faerie-powers** — *Endless Wine, Extend Glamour, Focus (Domestic Work),
  Transform into Object (Plant)* — targets are faerie powers written **inside creature stat blocks**
  with no standalone hashed DEF. Recommend **leave hashless** (harmless WARN) unless owner wants the
  statblock powers hashed.
- **Advancement Table 1** (covenants) → long-term-events vs character-creation table (owner call).
  **Damage Table 1** (hedge) → two damage-table records in obstacles.ttrpg (owner call which).

### B. Grogs GUIDANCE + caption strip (105 editorial-prefix records) — owner approved
Grogs is the only supplement with editorial-prefix DESCRIPTIONs (`"The source presents this as…"` /
`"Presented in the source as…"`). Same proven treatment as core:
- Guidance sidebars → `GUIDANCE { ENTRY ^"name" #hash { CONCERNS […] TEXT "<verbatim>" } }`, TEXT
  extracted **verbatim from the Grogs source HTML** (`~/Working/arm5e-sourcebook-conversions/grogs/Grogs - Extracted Data.html`)
  by `<h_>` heading (stop at next heading or `</div>`; drop the editorial prefix — it is NOT source).
- Table records → **strip** the editorial caption DESCRIPTION (data stays in the TABLE block).
- Worked examples → GUIDANCE. Watch for the **paraphrase-contamination** class (corpus text may be
  reworded vs source — verify each TEXT is a verbatim substring of the source before committing).
- Note: converting a DEF→GUIDANCE folds its in-DEF REFERENCES into CONCERNS; do grogs GUIDANCE, then
  re-run `apply_references.py … --only=grogs` to re-derive grogs refs, then finish grogs disambiguation.
- Verify: validator 0/0, `check_constructs` 0 err, coverage.

### C. Coverage gates (5 supplement manifests)
Run `npx tsx scripts/coverageAudit.ts coverage/arm5e-<name>.manifest.json` (with TOR2E_04 set) for each
of the 5; disposition/backfill any gaps to green each gate. The supplements had a prior record-gap pass
(memory `arm5e-supplements-recordgap`), so they may be close. Never rubber-stamp a disposition — verify
against the source (see the armdef rescan lesson: heading-name matching over-/under-counts; check the
draft/source text). Keep `sources.json` in sync.

### D. CORE HOUSES RESTRUCTURE — owner-directed, separate focused task (re-opens finalized 0.5.0 core)
Owner rulings: (1) each House defined **once**; the `houses.ttrpg` DEF (`EXTENDS "Hermetic House"`) is
canonical; (2) **the long narrative descriptions become `.lore` that points to the DEF.**
- `houses.ttrpg ^"House X"` keeps `EXTENDS "Hermetic House"` + PROPERTIES (House Type, Benefit, Source);
  **remove its long DESCRIPTION prose.**
- Create `arm5e-0.4-houses.lore` — one section per House, verbatim narrative, pointing to `^"House X"`.
- The two writeups differ (houses.ttrpg fuller ~1286 chars; order-of-hermes shorter ~953, some unique
  sentences each; both "Source: Core Rules") → **reconcile to a single verbatim-complete narrative per
  House, checked against the arm5e core source** (the shorter order-of-hermes ones may be paraphrased —
  keep the verbatim text; union any genuinely-unique content).
- **Drop the 12 duplicate `^"House X"` DEFs in `order-of-hermes.ttrpg`** (content now in the lore).
- Bump touched core files' `VERSION` to **0.5.1** (content edit post-0.5.0 per
  [[feedback-bump-content-version-on-corpus-edits]]).
- Verify: validator, references, and BOTH coverage gates green (House headings stay covered by the DEF +
  lore). Note: supplement House refs already point at the canonical `houses.ttrpg` DEF (done).
- ⚠ There may be OTHER duplicate-DEF smells (e.g. the Order-of-Hermes chapter re-defining core entities)
  — same pattern; flag/handle if found.

### E. Finalize
Re-run all gates both editions (validator, check_references → 0 hashless in supplement scope,
check_constructs, coverage). Bump any remaining unversioned supplement facets. Commit + push
(per-repo identity `Jordan Peacock <jordan@sortilege.online>`; `git pull --rebase --autostash origin main
&& git push`). Update `DSL-0.5-worklog.md`.

## DISCIPLINE
Main loop, deterministic-first, prove every gate (fault-inject when adding a new checker path), report
PROVEN/UNVERIFIED/FAILED with command+result, no long agents, keep the worklog current. The owner reviews
the nuanced disambiguation clusters ONE AT A TIME — surface each with concrete context + a recommendation;
do not blanket-apply.
