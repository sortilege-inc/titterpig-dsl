# DECISION-6 (DRAFT) — Parameterized references, aliases, and choices

> **Status: proposal for Jordan's review.** Not yet in the spec/grammar/validator.
> Motivated by the armdef conversion (character templates & mythic companions carry
> virtue/flaw references the current grammar can't express) and by Jordan's VtM-1200s
> campaign (setting-level renames). Once ratified, folds into `titterpig-dsl-spec.md`,
> `ttrpg.peg`, `ttrpg_validator.py`, and `AUTHORING-GUIDELINES.md`.

## 1. The problem

A caret reference today is a bare name: `CARET_REF <- '^' '"' Name '"'`. Three real needs can't be
expressed, so the armdef converter had to store them as opaque verbatim strings that resolve to
nothing:

**(a) Parameterization** — one base entity with a variable slot bound at the point of use. These
are pervasive in Ars Magica: `Puissant Single Weapon`, `Great Stamina`, `Affinity with Ignem`,
`Ways of the Forest`, `Area Lore` → `Normandy Lore`. The base entity (`Puissant`, `Great`, `Area
Lore`) is defined once; the printed form binds a parameter (an Ability, a Characteristic, an Art, a
place). The bound reference is a *derived instance* of the base.

**(b) Aliasing / rename** — the *same* entity under a different label, with **no** parameter,
chosen at the edition/setting level. Jordan's example: a VtM 1200s campaign renames the `Drive`
skill to `Ride`. `Drive` and `Ride` are one entity; only the display label differs. This is
distinct from parameterization (no slot) and from override/errata (no value change).

**(c) Choice** — "A or B" and quantified open slots. Mythic Companion required virtues include
`Demonic Might or Demonic Powers` and `either one more Major Supernatural Virtue or three Minor
Supernatural Virtues`. A downstream consumer must be able to present these as a decision, not read
them as flat prose.

All three are fundamentally about **references that carry more than a name**. DECISION-6 extends the
reference/value grammar to cover them, keeping the bare `^"Name"` form as the common case.

## 2. Design

### 2.1 Parameterized definitions and bound references

A DEF may declare **parameters** — named, typed slots that instances bind. Declaration adds an
optional `PARAMETERS { }` block to a DEF body:

```
#hash ^"Puissant" DEF {
    EXTENDS ^"Virtue"
    PARAMETERS { ^"subject" OF ^"Ability" }        # one param, ranges over Ability entities
    PROPERTIES { ^"Size" STRING "Minor" FIXED  ^"Category" STRING "General" FIXED }
    DESCRIPTION "Add 2 to rolls using the chosen Ability ..."
}

#hash ^"Great" DEF {
    EXTENDS ^"Virtue"
    PARAMETERS { ^"subject" OF ^"Characteristic" }
    ...
}

#hash ^"Area Lore" DEF {
    EXTENDS ^"Ability"
    PARAMETERS { ^"area" OF STRING }               # free-text domain (no Land entities exist)
    ...
}
```

A parameter's domain is either a caret type (`OF ^"Ability"` — the bound value must resolve to an
entity of that type) or `OF STRING` (free text, e.g. a place name). Multiple parameters are
allowed (`PARAMETERS { ^"a" OF ^"Art"  ^"b" OF ^"Form" }`).

A **bound reference** appends a parenthesized argument list to a caret ref, wherever a caret ref is
legal (list items, values, EXTENDS targets):

```
^"Puissant"(^"Single Weapon")        # bind the Ability entity "Single Weapon"
^"Great"(^"Stamina")                 # bind the Characteristic "Stamina"
^"Area Lore"("Normandy")             # bind a free-text area  ->  "Normandy Lore"
^"Affinity with"(^"Ignem")           # bind the Art "Ignem"
```

Arguments bind positionally (or by name for clarity: `^"Puissant"(^"subject" = ^"Single Weapon")`).
The **derived display name** is a per-system rendering of base + bindings (`Puissant Single
Weapon`, `Normandy Lore`); the DSL stores the structured form and lets consumers render it.

> This replaces the current placeholder-in-the-name convention (`^"Great (Characteristic)"`,
> `^"Student of (Realm)"`, `^"Puissant Ability"` / `^"Puissant Art"`). Those become
> `^"Great"` / `^"Student of"` / `^"Puissant"` with a `PARAMETERS` block — see migration (§5).

### 2.2 Aliases (setting/edition renames)

A top-level `ALIAS` statement declares one name to be a **display synonym** of an existing entity:

```
ALIAS ^"Ride" FOR ^"Drive"
```

Semantics: references to `^"Ride"` resolve to the `Drive` entity (same hash, same rules), but the
label `Ride` is preserved for display. An alias adds **no** properties and changes **no** values —
it is purely a naming layer, distinct from `MODIFY`/`OVERRIDE` (which patch an entity) and from a
new DEF (which is a different entity). Aliases are edition-scoped like everything else, so a
setting can ship an `*-aliases-*` extension file that renames vocabulary without touching the base
definitions. An alias may also target a parameterized/bound reference:

```
ALIAS ^"Chariot Driving" FOR ^"Area Lore"("the hippodrome")   # (contrived, but legal)
```

### 2.3 Choices

A `CHOICE` is a **value** — usable anywhere a bracket-list item or value is (inside a `^"Required
Virtues"` list, a `CHOICES` block, a property):

```
CHOICE [ ^"Demonic Might", ^"Demonic Powers" ]          # pick exactly one of these entities
```

Options may be quantified typed **slots** for the open-allotment case:

```
CHOICE [
    1 OF ^"Virtue" WHERE { ^"Size" "Major",  ^"Category" "Supernatural" },
    3 OF ^"Virtue" WHERE { ^"Size" "Minor",  ^"Category" "Supernatural" }
]
```

A slot is `<count> OF <caret type> WHERE { <field> <value> ... }` — "pick N entities of this type
matching these field constraints." A bare `^"Name"` or `"string"` option is also legal (a specific
entity, or verbatim prose when nothing structured fits — completeness always wins). Optional
`CHOICE PICK n [...]` sets how many options are chosen (default 1).

## 3. Grammar additions (`ttrpg.peg`)

```
# --- 2.1 parameterized refs -------------------------------------------------
CARET_REF        <- '^' '"' (!'"' .)* '"' PARAM_BINDING?
PARAM_BINDING    <- _ '(' _ PARAM_ARG (_ ',' _ PARAM_ARG)* _ ')'
PARAM_ARG        <- (CARET_REF _ '=' _)? (CARET_REF / STRING)

PARAMETERS_BLOCK <- 'PARAMETERS' _ '{' _ PARAM_DECL* _ '}'
PARAM_DECL       <- CARET_REF _ 'OF' _ (CARET_REF / 'STRING')
# ...add PARAMETERS_BLOCK to the DEF body alternatives

# --- 2.2 aliases ------------------------------------------------------------
ALIAS_STATEMENT  <- 'ALIAS' _ CARET_REF _ 'FOR' _ HASH_ID? _ CARET_REF
# ...add ALIAS_STATEMENT to top-level file statements (beside DEF/EXTENSION items)

# --- 2.3 choices ------------------------------------------------------------
CHOICE_VALUE     <- 'CHOICE' (_ 'PICK' _ INTEGER_LIT)? _ '[' _ CHOICE_OPTION (_ ',' _ CHOICE_OPTION)* _ ']'
CHOICE_OPTION    <- CHOICE_SLOT / CARET_REF / STRING
CHOICE_SLOT      <- INTEGER_LIT _ 'OF' _ CARET_REF (_ 'WHERE' _ '{' _ WHERE_PAIR* _ '}')?
WHERE_PAIR       <- CARET_REF _ (STRING / INTEGER_LIT)
# ...add CHOICE_VALUE to VALUE and BRACKET_ITEM alternatives
```

New reserved words: `PARAMETERS`, `ALIAS`, `FOR`, `CHOICE`, `PICK`, `OF` (already reserved),
`WHERE`.

## 4. Validator implications (`ttrpg_validator.py`)

- **Bound refs:** the base name must resolve to a DEF that declares `PARAMETERS`; the argument
  count must match; each `OF ^"Type"` argument must resolve to an entity of that type; `OF STRING`
  arguments accept any string. A bound ref with no matching `PARAMETERS` on the base is an error
  (catches typos and un-parameterized bases).
- **Aliases:** the `FOR` target must resolve (by hash if given, else by name); the alias name must
  not already name a *different* entity (an alias colliding with a real DEF is an error unless it
  targets that same DEF). Alias resolution is transitive but must be acyclic.
- **Choices:** each option's caret refs must resolve; slot `WHERE` fields must be real fields of the
  named type; `PICK n` must not exceed the option count. Verbatim-string options are unchecked
  (they're the completeness escape hatch).
- Coherence (§2067) extends: "everything referenced resolves" now includes bound-ref bases,
  parameter-argument entities, alias targets, and choice-option refs.

## 5. Migration

- **armdef** (the driver): the ~15 parameterized virtue/flaw DEFs (`Puissant`, `Great`, `Affinity
  with`, `Deficient Form`, `Deft Form`, `Student of`, `Ways of the`, `Poor`, `Inoffensive to`,
  `Plagued by Supernatural Entity`, `Cyclic Magic`, `Greater/Lesser Immunity`, `Major/Minor Magical
  Focus`, `Puissant/Deficient` Arts) gain `PARAMETERS` blocks and drop their `(placeholder)` name
  suffixes. Character templates & mythic companions then upgrade their verbatim virtue/flaw strings
  to bound refs + `CHOICE`s. This is exactly the "VF alias table" review item — DECISION-6 is the
  grammar it needs.
- **weapons/armor as equipment DEFs** (deferred review item Q7) rides on the same mechanism: a
  weapon is a DEF, and a template's `COMBAT` block references it — parameterized where the book
  leaves a slot ("any one weapon" specialties).
- Other systems adopt lazily; the bare `^"Name"` form is unchanged, so nothing breaks.

## 6. Open sub-questions for ratification

1. **Binding syntax:** parenthesized `^"Puissant"(^"Single Weapon")` (proposed) vs. a keyword form
   `^"Puissant" WITH ^"Single Weapon"`. Parens are terser and read like function application;
   the keyword is more self-documenting. Which?
2. **Derived display name:** should the DSL store an optional explicit display string
   (`^"Puissant"(^"Single Weapon") AS "Puissant Single Weapon"`) for fidelity to the printed form,
   or leave rendering entirely to consumers? (Completeness principle leans toward allowing the
   explicit verbatim label.)
3. **Typed slots (`WHERE`):** is the `n OF ^"Virtue" WHERE {...}` filter worth the grammar weight,
   or should open-allotment choices stay verbatim strings for now and gain structure later? (The
   armdef corpus has exactly one such case — "one Major or three Minor Supernatural Virtues".)
4. **Alias direction/scope:** `ALIAS ^"new" FOR ^"existing"` (proposed) — confirm the new name is
   the alias and the existing is canonical; confirm aliases live in their own extension files.
5. **Numbering:** this becomes DECISION-6; the parameterized-DEF and choice items currently in
   `TASKS.md` "Open decisions" resolve into it.
