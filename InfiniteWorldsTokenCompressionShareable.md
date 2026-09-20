# Infinite Worlds Game Compression Guide

Hand this file to an AI agent along with a game JSON. The agent needs nothing else.

**Job:** Cut recurring storyteller token cost on fields sent every turn, without losing rule fidelity or player experience.

**Not the job:** Shrink JSON file size. Rewrite store-card prose. Telegraph player-visible literary voice.

**Safety default:** Compress **AI-facing rules only**. Never rewrite player-visible story voice, headings, store card, or image copy-strings. Optional telegraph applies only to remaining unique rule text.

Play is the final judge. A shorter prompt that drops a constraint is a failure.

---

## 1. Goal

Lower the text the storyteller sees **every turn**. Duplicate rules, restated trackers, sample paragraphs, and retired-field reminders are the usual waste.

Method: structural levers first (dedupe, routing, strip examples), then optional prose rewrite of leftover unique law. Do not skip to telegraph while copies remain.

---

## 2. What costs tokens every turn

JSON file size is not turn cost. Designer comments `<#…#>` are ignored and never reach the storyteller.

**Chosen** playable bio is one always-on slot; **unchosen** playables are not sent. Compress **every** playable bio at design time because any may be chosen.

### Every turn (storyteller)

After turn 1 the platform roughly sends:

- `instructions`
- every `instructionBlocks[].content` (cost is **text**, not block count)
- `descriptionRequest`
- `evaluationRequest`
- `summaryRequest` (always-on text; the summarizer job runs on fold, not every turn)
- `authorStyle` / `authorStyleExtension`
- **hot** tracked items (`everyone` / `ai_only`): display `name` + current value, and typically `description` / `updateInstructions`
- **`hidden` / `hidden_boring` are not auto-sent** — cold store; PawScript still reads/writes
- **chosen playable** — `possibleCharacters[].description` (+ skills) for the selected character only
- **`NPCs[]` roster** — when populated, listed NPC text fields (`detail`, `one_liner`, `appearance`, `secret_info`, `img_appearance`, `img_clothing`) auto-send every turn. Empty roster = zero cost
- last few `outcomeDescription` + `secretInfo` **verbatim** (credit UI: **Short-term memory**)
- compressed summary of older turns (credit UI: **Long-term memory** — empty until the first `summaryRequest` fold)
- current player input

**`<<…>>` timing:** Expressions in author fields resolve **before** the storyteller prompt is built. The storyteller never sees raw `<<>>`, cannot write `<<>>`, and output is not injected. A small derived snippet injects a small result. A full-item `<<$player_appearance>>` dumps the whole tracker into the prompt (double-pay with hot auto-send). Do **not** teach `FORBID: <<>> dump` to the model. Remove author dump expressions instead.

### Sometimes

- `loreBookEntries[].content` — keyword match only, not every turn
- `background` — player pop-up + storyteller **until first summary**
- `effectGiveInfo` — injects when the trigger fires
- `effectModifyInstructionBlock` — replaces one extra instruction block

### Never storyteller (do not compress “to save tokens”)

- Store `description` (player world-card only)
- `designNotes`
- Unchosen `possibleCharacters` bios / portraits at **runtime** (still compress them at design time)
- Image **Pre/Post** wrappers — image model only (~1024 tokens / ~780 words including Pre/Post; separate meter)

### Growing (the expensive future)

- `secretInfo` rewritten every turn; last few turns arrive intact
- YAML maps that accrete keys (skills, appearance, inventory)
- **Short-term memory** — recent verbatim window; grows until a fold
- **Long-term memory** — compressed summary blob; empty until first `summaryRequest` run

Typical cadence: ~8-turn short-term window; first long-term blob around **turn 9**. The fold turn is not cheap (summarizer + storyteller). Compress **rules** resent every turn, and the **template/dialect** of fields that grow. Do not telegraph player-visible `outcomeDescription`.

---

## 3. Never rewrite

Leave these exact.

**Schema / code**

- JSON keys, `trigger*` / `effect*` `type` strings, ids, `variableName`, `positionInList`
- PawScript in `effectRunScript` and `<<>>` expressions (author-side; do not mention `<<>>` in storyteller-facing rules)
- YAML **keys**
- Tracked item **display names**

**Image** (storyteller rules may be shortened; these strings stay exact)

- `IWBeautiful`, `IWBeautiful2`, `IWUpscaleFace`, `IWUpscaleFaceSmooth`
- `imageStyleCharacterPre` / `Post` wrappers
- Camera / lens / film menus and banned-word lists if the world uses them
- Face-lock celebrity names in lore or Appearance YAML
- Clothing / appearance strings that get copied into image fields
- Cache-bust lines the image engine requires (for example `illustrClothesChanged: TRUE`)

**Player-facing**

- Store `description`, `background`, `charSelectText`, playable `description` **voice** (you may drop duplicated appearance paragraphs; do not telegraph the remaining backstory)
- `firstInput` and `effectChangeFirstAction` player prompts
- `outcomeDescription` headings and literary voice
- Defeat / victory player text
- `authorStyle` **voice** line

**Lore matching**

- `loreBookEntries[].keywords` and `.name`

---

## 4. How to measure

Count **characters** of always-on text (not JSON kilobytes). Strip `<#…#>` comments first. Rough tokens ≈ chars / 4.

**Rules always-on** = sum of:

- `instructions`
- each enabled `instructionBlocks[].content`
- `descriptionRequest`
- `evaluationRequest`
- `summaryRequest`
- `authorStyle` + `authorStyleExtension`
- hot tracked items: `name` + `description` + `updateInstructions` + current/initial value

**Effective always-on** (design-time session budget) = rules always-on + longest playable bio + all `NPCs[]` roster text fields.

Record before and after. Success needs a drop **and** the quality gate **and** play parity.

---

## 5. Levers (apply in order)

1. **Dedupe.** One home per rule. Pointers elsewhere. Duplicate rules multiply cost linearly.
2. **Playable bio vs Appearance YAML.** Drop appearance paragraphs when a hot Player Appearance / Cast / NPC Appearance tracker already holds them (seed via `initialValue` / `initialPCValue`). Keep identity and backstory.
3. **Omission over negation.** Retiring a pattern: delete the positive instruction. Do **not** add `FORBID:` for the retired name. See §6.
4. **Lore book for static facts.** Keyword-triggered ≠ every-turn cost. Do not duplicate listed NPC sheets as lore **and** roster. Prefer specific keywords over encyclopedia dumps.
5. **Strip examples** from always-on fields. Examples teach once; rules persist every turn. One GOOD/BAD YAML sample is enough if a block teaches writes.
6. **Cap growing templates** (optional — test). Line budgets on `secretInfo` / summary dialect trade recall for cost. World-specific. Play through turn 20 before trusting a cap.
7. **Delta not full rewrite** (optional — test). Per-turn hidden state: teach changes, not unchanged rows. Next turn must still have the needed board.
8. **Mutable EIB / GiveInfo for branches.** Only active path law every turn, not every season/role/floor. Stub default + `effectModifyInstructionBlock` or inject with `effectGiveInfo`.
9. **Seal spent story** (optional — test). When an act bible is done: stub it, move the tracker to `hidden_boring`, keyword-arm the baseline if still needed, shrink the late EIB. Spent text must not reappear as briefing.
10. **No full-tracker `<<$item>>` dumps** in author fields. Hot trackers already auto-send. Storyteller refers by **display name**. Derived snippets are fine.
11. **Lean `summaryRequest`.** Do not tell the summarizer to restate hot tracked items (they auto-send and copies go stale). Teach **how** to keep non-tracker facts: plot beats, promises, NPC attitude, injuries/debts, schemes, player-established facts with no tracker key. Field is always-on; the job runs on fold (~turn 9+). STM-only turns do not prove a summary recut.
12. **Prose telegraph last.** Optional rewrite of leftover unique rule text. See §9.
13. **Never compress frozen or player voice.** See §3.

Skipping to lever 12 while duplicates remain wastes the pass.

---

## 6. Omission over FORBID

Default to **positive law, one home**. Negation reminds the model of the bad prior and costs tokens every turn.

**Do this**

- State what to copy or do. Delete the stock list; do not name the retired source.
- One home per rule. Pointers elsewhere; no restated copy-law in image fields + YAML + `descriptionRequest`.
- Drop a hedge by deleting it. Do not replace `adult` with `young` / `teen` / `not Ethiopian`.

**Do not do this**

- Stack `FORBID:` / `Never` laundry for things the model *might* invent (site→skin, extra limbs, wool, kimono, habesha, schoolgirl, minors, legal age).
- Add `FORBID: Compendium` after omitting Compendium from the character-data line.
- Repeat the same negation in three fields.

**`FORBID:` is allowed only when all of these hold**

1. The model can still **do** that live behaviour (not a retired name, not a guessed ethnicity).
2. **Once**, in **one** home.
3. Platform-breaking or puppeting: `$push` at `name`, list-of-lists, fade the sex scene, decide the PC’s line.

Right: `Copy ethnicity, skin, hair, wings, and garments from that Other characters record.`

Wrong: `FORBID inventing from site (no Ethiopian-from-Addis, no habesha, no extra arms).`

Right: `Anatomy: two arms, two legs. Wings sit on the back.`

Wrong: `FORBID extra limbs, fused limbs, wings-as-arms.`

Right: `APPEARANCE: = Player Appearance YAML only.`

Wrong: `FORBID restate appearance here.`

**Omission QA (after every recut)**

- [ ] Retired pattern → zero mentions in EIBs, `summaryRequest`, secretInfo template — not `FORBID:` elsewhere
- [ ] No trailing FORBID laundry restating numbered PER-TURN / IF steps above it
- [ ] Each live FORBID exists once (tracker `updateInstructions` **or** EIB **or** `descriptionRequest` — not all three)
- [ ] Hot tracker authoritative → `=` pointer only, not `FORBID restate`

---

## 7. Intent gate

Fidelity over brevity. Dense text may **expand** under structured rewrite. If it is already one fact per line, stop.

Semantic rewrite beats token deletion. Do not run perplexity/classifier deletion on rule blocks — it drops negation, connectives, and qualifiers. Compression is not summarization: keep every obligation, do not keep the gist.

### FORCE-KEEP (never strip or abbreviate away meaning)

| Category | Keep verbatim or explicit | Failure if dropped |
|----------|---------------------------|-------------------|
| Negation | `!=`, `FORBID:`, `no`, `without`, `except` | Rule silently allows the ban |
| Modals / obligation | `MUST`, `MAY`, `ONLY`, `Req:` | Permission vs requirement swap |
| Quantifiers | `all`, `any`, `Cap n`, `every`, `none` | Scope collapse |
| Comparatives / bands | `>>`, `0..Need`, numeric thresholds | Difficulty drift |
| Numbers + units | `calendar_day`, `≈1.5h`, `30 calendar days` | Wrong unit or precision |
| Named entities | proper nouns, tracker display names, YAML keys | Pronoun antecedent lost |
| XOR / exclusivity | `XOR`, `\|` with explicit branches | Both branches true |
| Conditional logic | `IF … THEN`, `unless`, `when` | Dead or inverted branches |

### Constraint diff (before accepting any rewrite)

1. List every constraint in the **source** (FORBID, IF, Cap, numeric bound, named entity, modal).
2. Mark each **present / absent / weakened** in the draft.
3. Any absent or weakened → expand until pass, or abandon compression for that block.

### 12-point quality gate

Run after every compressed block:

1. Every source constraint has a matching line or operator.
2. One atomic fact per line (no multi-claim sentences).
3. Max ~3 consecutive operators per line; split if opaque.
4. Repeat entity names on each line (no stranded `he/she/they`).
5. Negation scope unchanged from source.
6. Numbers, units, comparators unchanged.
7. Frozen tokens from §3 untouched.
8. No private cipher / invented codes (`HX`, `T&S`).
9. No meta in AI-facing text ("saves tokens", "REMOVABLE block").
10. Player-facing voice/headings unchanged.
11. Readable to a human designer in ~30 seconds.
12. If ratio gain is under ~15% and text is already labelled, **stop**.

---

## 8. Per-field jobs

### `instructions`

Always-on. Keep unique world law not duplicated elsewhere. Pointer form is enough (`Skills three-pass = Skill Resolve block.`). Empty `instructions` (`""`) is valid when law lives in extra instruction blocks + `descriptionRequest` + trackers. Cut restated chapters.

### Extra instruction blocks

All enabled **content** every turn. Telegraph unique law. `<#…#>` comments are free. Mutable blocks: stub default, swap in the chosen path only. Do not keep a live block for a branch the world never needs — test before deleting.

### `descriptionRequest`

Hybrid: rules compress; **player-printed headings and markdown stay exact.** Delete sample paragraphs. Point at shared engines instead of restating. Trust tracked items: read the value, do not recalculate against memory. Do not restate tracker contents here.

### `evaluationRequest`

Always-on. Omit may re-inject the platform default eval. Light telegraph of **custom** eval only.

### `summaryRequest`

Always-on text; summarizer job is **not** every turn. Two-layer memory: recent turns verbatim (short-term); this field guides older-turn compression (long-term). Do not restate hot YAML. Owns plot, promises, attitude, injuries/debts, schemes, untracked player facts. A KEEP/FORBID list alone is weak — teach **how** to write kept facts (dialect, caps, skeleton). Prove after first fold (~turn 9+).

### `authorStyle`

Voice line is frozen. Permits live in extra instruction blocks, not here.

### Tracked item `description` / `updateInstructions`

Ride with the auto-sent item every turn. One-line shape + unique constraints + live `FORBID: $push` / dash-list if that is a real write bug. Point at a shared YAML map-update engine; do not repeat the engine on every item.

### Lore `content`

Safe to tighten. Keywords and `.name` stay English and exact. Face-lock lines stay byte-exact.

### `possibleCharacters[].description`

Chosen slot every turn. Telegraph IDENTITY + STORY. Pointer to hot Appearance YAML. Remove appearance paragraphs that duplicate `initialPCValue` / Player Appearance `initialValue`. Keep voice/backstory readable on character select.

### `NPCs[]` roster rows

When populated, row text rides every turn. Move static franchise facts to keyword lore. Keep listed NPCs lean. Use hot Appearance YAML for walk-ons. Do not duplicate the same sheet in roster **and** lore.

### Triggers

Compress `effectGiveInfo` and `effectModifyInstructionBlock` **content** strings. Frozen: PawScript, id lists, player `firstInput` replacements.

### `secretInfo` template (in instructions / extra blocks)

Rewritten every turn; last few turns verbatim (**growing**). You may tighten the **template** (labels, delta vs full rewrite, line cap). Player `outcomeDescription` stays literary.

---

## 9. Optional telegraph dialect

Use only on leftover unique **rule** text after structural levers. Pick **one** variant per block and stay consistent: ASCII operators **or** tight imperative English.

ASCII only. Rare Unicode arrows cost extra tokens.

| Meaning | Write |
|---------|--------|
| causes / then / leads to | `->` |
| results in final state | `=>` |
| increase | `^` |
| decrease | `v` |
| is / equals | `=` |
| not | `!=` |
| much stronger / better | `>>` |
| both / and | `&` or `+` |
| or | `\|` |
| contrast (never causal) | `VS` |
| prerequisite | `Req:` |
| conditional | `IF … THEN` |
| scope pin | `ONLY` / `EXCEPT` |
| never | `FORBID:` |
| maximum count | `Cap n` |
| one or the other, not both | `XOR` |
| approximate | `≈` |

**Rules**

- Label-first lines: `Rule:`, `Board:`, `FORBID:`
- One claim, one delta, or one labelled edge per line
- Keep exact: proper nouns, tracker display names, YAML field keys
- Drop filler, **not** constraints. Deleting a ban is not compression
- AI-facing text is runtime rules only. Lab notes → `designNotes`
- Do not put PawScript / `<<>>` / injection syntax in AI-facing text

**Tokenizer**

- `the` / `a` / `is` are often one token. Article-only stripping has poor return and raises misread risk
- Invented codes are often *more* tokens than the real word; models forget glossaries
- Measure parsed string length, not raw JSON escaping
- Store-card emoji do not hit the storyteller

**Before**

When the player rests for a full night, advance the calendar by one day unless they are in a combat encounter. Resting restores health by 20 points but cannot exceed the maximum. If health is already full, resting still advances time. Never restore health during an active combat turn.

**After**

```
Rest: full night -> calendar_day^1 EXCEPT active combat
Rest => health^20 Cap max_health
IF health = max THEN rest still advances time
FORBID: health restore during combat turn
```

If a model misreads symbols, use tight imperative English instead. Same constraints, no operators.

---

## 10. Agent workflow

1. **Inventory** always-on fields and measure (§4).
2. **List constraints** for each block you will touch (FORCE-KEEP).
3. **Apply structural levers 1–11.** When testing, change one lever at a time. When building, you may apply several after each representative sample passes the gate.
4. **Optional telegraph** leftover unique law (§9). One dialect per block.
5. **Quality gate** (§7) + omission QA (§6).
6. **Measure again.** Keep the before/after counts.
7. **Play-test** the same playable, same opening:
   - Rule/output levers: 5–10 turns covering the mechanics under test
   - `summaryRequest` levers: play through the first fold (turn 9+)
8. **Parity checklist**
   - [ ] Player heading structure unchanged
   - [ ] Core mechanic writes still obey live FORBID rules (no `$push`, no dash-list if forbidden)
   - [ ] Images: face lock / clothing copy-strings verbatim where applicable
   - [ ] Constraint diff passes on 3 random rules
   - [ ] No drift on safety/agency constraints you care about

If play drifts, revert that block. Do not ship a recut that fails the gate.

---

## 11. Anti-patterns

- Invented glossary codes
- Article-only / stopword stripping on rules
- Fixed compression-ratio targets on dense constraint text
- Token-deletion tools on rule blocks
- Telegraphing image copy-strings, clothing templates, or `authorStyle` voice
- Renaming YAML keys or tracker display names
- Compressing lore **keywords**
- Putting lab meta in AI-facing fields
- One extra instruction block per season/year (all sent every turn) instead of GiveInfo or a mutable block
- A clothing registry with no auto-sent clothing reader
- Generic lore keywords that dump an encyclopedia every turn
- Measuring success by JSON kilobytes
- Compensating `FORBID:` after deleting a positive rule
- Trailing FORBID block that duplicates numbered steps above it
- `FORBID restate X` when hot tracker X is authoritative
- Teaching PawScript / `<<>>` to the storyteller
- Implementing dump prevention as `FORBID: <<>> dump` instead of removing author `<<$item>>` expressions
- Telegraphing `outcomeDescription` or other player-visible story voice

---

## 12. When to stop

- Player-visible story voice and frozen headings
- Image output English, clothing copy-strings, face locks
- Text already atomic and under a justified line cap
- Rules where tone **is** the rule (`authorStyle`, some voice blocks)
- Ratio gain under ~15% on already-labelled text
- Any rewrite that fails constraint diff or play parity
