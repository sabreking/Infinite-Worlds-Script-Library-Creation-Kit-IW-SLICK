# Infinite Worlds Game Compression Guide (Lite)

Hand this file to an AI agent along with a game JSON. The agent needs nothing else.

**Job:** Cut recurring storyteller token cost **in place**. Same fields, same blocks, same trackers, fewer tokens. Do not lose rule fidelity or player experience.

**Not the job:** Shrink JSON file size. Rewrite store-card prose. Telegraph player-visible literary voice. **Change the game’s structure.**

**This pass is in-place only.** Recut text that already exists. Do not add, remove, split, rename, or retarget extra instruction blocks, tracked items, lore entries, or triggers. Do not move facts into lore, GiveInfo, or `hidden` / `hidden_boring`.

**Safety default:** Compress **AI-facing rules only**. Never rewrite player-visible story voice, headings, store card, or image copy-strings. Optional telegraph applies only to remaining unique rule text **in the same field**.

Play is the final judge. A shorter prompt that drops a constraint is a failure.

---

## 1. Goal

Lower the text the storyteller sees **every turn**. Duplicate rules, full-tracker dumps, restated hot YAML in `summaryRequest`, and retired-field `FORBID:` reminders are the usual waste.

Method: dedupe and omit first, strip author dumps, lean `summaryRequest` in place, then optional prose rewrite of leftover unique law. Do not skip to telegraph while copies remain.

---

## 2. Hard bans

Do **not**:

- Move facts into `loreBookEntries` or add lore entries
- Add, remove, or fire `effectGiveInfo` / `effectModifyInstructionBlock` to swap path law
- Change tracker visibility (`hidden` / `hidden_boring`) or seal spent story
- Add line caps, delta-only `secretInfo` templates, or new YAML schema
- Strip playable-bio appearance because an Appearance YAML exists
- Delete example paragraphs unless they are a **duplicate** of another already-on home (that is dedupe)
- Add, remove, split, or rename extra instruction blocks, tracked items, or triggers

Same field, fewer tokens, same structure.

---

## 3. What costs tokens every turn

JSON file size is not turn cost. Designer comments `<#…#>` are ignored and never reach the storyteller.

**Chosen** playable bio is one always-on slot; **unchosen** playables are not sent.

### Every turn (storyteller)

- `instructions`
- every `instructionBlocks[].content` (cost is **text**, not block count)
- `descriptionRequest`
- `evaluationRequest`
- `summaryRequest` (always-on text; the summarizer job runs on fold, not every turn)
- `authorStyle` / `authorStyleExtension`
- **hot** tracked items (`everyone` / `ai_only`): display `name` + current value, and typically `description` / `updateInstructions`
- **`hidden` / `hidden_boring` are not auto-sent** — do not change that
- **chosen playable** — `possibleCharacters[].description` (+ skills) for the selected character only
- **`NPCs[]` roster** — when populated, listed NPC text fields auto-send every turn
- last few `outcomeDescription` + `secretInfo` **verbatim** (credit UI: **Short-term memory**)
- compressed summary of older turns (credit UI: **Long-term memory** — empty until the first `summaryRequest` fold)
- current player input

**`<<…>>` timing:** Expressions in author fields resolve **before** the storyteller prompt is built. The storyteller never sees raw `<<>>` and cannot write it. A small derived snippet injects a small result. A full-item `<<$player_appearance>>` dumps the whole tracker into the prompt (double-pay with hot auto-send). Do **not** teach `FORBID: <<>> dump` to the model. Remove author dump expressions instead.

Typical cadence: ~8-turn short-term window; first long-term blob around **turn 9**. Prove a `summaryRequest` recut after the first fold.

Do not telegraph player-visible `outcomeDescription`. Do not compress store `description`, `designNotes`, or image Pre/Post wrappers (image model meter, not storyteller).

---

## 4. Never rewrite

Leave these exact.

**Schema / code:** JSON keys, `trigger*` / `effect*` `type` strings, ids, `variableName`, `positionInList`, PawScript in `effectRunScript` and `<<>>` expressions, YAML **keys**, tracked item **display names**.

**Image:** `IWBeautiful`, `IWBeautiful2`, `IWUpscaleFace`, `IWUpscaleFaceSmooth`; `imageStyleCharacterPre` / `Post`; camera / lens / film menus and banned-word lists; face-lock celebrity names; clothing / appearance strings copied into image fields; required cache-bust lines (for example `illustrClothesChanged: TRUE`).

**Player-facing:** store `description`, `background`, `charSelectText`, playable `description` **voice**, `firstInput`, `effectChangeFirstAction` player prompts, `outcomeDescription` headings and literary voice, defeat / victory text, `authorStyle` **voice** line.

**Lore matching:** `loreBookEntries[].keywords` and `.name`. Do not add, remove, or retarget lore entries.

---

## 5. How to measure

Count **characters** of always-on text (not JSON kilobytes). Strip `<#…#>` comments first. Rough tokens ≈ chars / 4.

**Rules always-on** = `instructions` + each enabled `instructionBlocks[].content` + `descriptionRequest` + `evaluationRequest` + `summaryRequest` + `authorStyle` / `authorStyleExtension` + hot tracker `name` + `description` + `updateInstructions` + current/initial value.

**Effective always-on** = rules always-on + longest playable bio + all `NPCs[]` roster text fields.

Record before and after. Success needs a drop **and** the quality gate **and** play parity **and** unchanged structure (same blocks, trackers, lore entries, triggers).

---

## 6. Levers (apply in order)

1. **Dedupe.** One home per rule. Delete the extra copy; leave a pointer at the surviving home (`Skills three-pass = Skill Resolve block.`). Do not create new lore, trackers, or blocks.
2. **Omission over FORBID.** Retiring a pattern: delete the positive instruction. Do **not** add `FORBID:` for the retired name. See §7.
3. **No full-tracker `<<$item>>` dumps.** Remove author dump expressions. Storyteller refers by **display name**. Derived snippets are fine.
4. **Lean `summaryRequest`.** Recut **that field in place**. Do not tell the summarizer to restate hot tracked items. Teach **how** to keep non-tracker facts: plot beats, promises, NPC attitude, injuries/debts, schemes, player-established facts with no tracker key. Do not move summary jobs into lore / GiveInfo / hidden items. Prove after first fold (~turn 9+).
5. **Prose telegraph last.** Optional rewrite of leftover unique **rule** text in the **same** field. See §10.
6. **Never compress frozen or player voice.** See §4.

Skipping to lever 5 while copies remain wastes the pass.

---

## 7. Omission over FORBID

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

Right: `APPEARANCE: = Player Appearance YAML only.`

Wrong: `FORBID restate appearance here.`

**Omission QA**

- [ ] Retired pattern → zero mentions — not `FORBID:` elsewhere
- [ ] No trailing FORBID laundry restating numbered steps above it
- [ ] Each live FORBID exists once
- [ ] Hot tracker authoritative → `=` pointer only

---

## 8. Intent gate

Fidelity over brevity. If text is already one fact per line, stop. Semantic rewrite beats token deletion. Compression is not summarization: keep every obligation.

### FORCE-KEEP

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

### Constraint diff

1. List every constraint in the **source**.
2. Mark each **present / absent / weakened** in the draft.
3. Any absent or weakened → expand until pass, or abandon compression for that block.

### 12-point quality gate

1. Every source constraint has a matching line or operator.
2. One atomic fact per line.
3. Max ~3 consecutive operators per line; split if opaque.
4. Repeat entity names on each line (no stranded `he/she/they`).
5. Negation scope unchanged.
6. Numbers, units, comparators unchanged.
7. Frozen tokens from §4 untouched.
8. No private cipher / invented codes.
9. No meta in AI-facing text ("saves tokens").
10. Player-facing voice/headings unchanged.
11. Readable to a human designer in ~30 seconds.
12. If ratio gain is under ~15% and text is already labelled, **stop**.
13. **Structure unchanged:** same extra instruction blocks, trackers, lore entries, and triggers as the source JSON.

---

## 9. Per-field jobs (recut in place only)

- **`instructions`:** Keep unique law not duplicated elsewhere. Pointer form is enough. Cut restated chapters. Do not empty this field by moving law into new blocks.
- **Extra instruction blocks:** Recut **content** of existing enabled blocks. Do not add, delete, split, or swap blocks.
- **`descriptionRequest`:** Rules compress; **player-printed headings and markdown stay exact.** Point at existing engines instead of restating. Do not delete sample paragraphs unless they duplicate another already-on home. Do not restate tracker contents.
- **`evaluationRequest`:** Light telegraph of custom eval only. Do not omit the field (platform may re-inject a default).
- **`summaryRequest`:** Recut in place. Do not restate hot YAML. Teach how to keep untracked facts. Do not add caps as a new design; keep an existing cap if the source already has one.
- **`authorStyle`:** Voice line is frozen.
- **Tracker `description` / `updateInstructions`:** Recut unique constraints. Point at an **existing** shared engine; do not invent a new one. Live `FORBID: $push` / dash-list only if that is a real write bug.
- **Lore `content`:** Recut existing bodies only. Keywords and `.name` stay exact. Do not add or remove entries.
- **Playable bios:** Do **not** drop appearance paragraphs because YAML exists. Do not telegraph remaining backstory. Dedupe only if the same rule text is already always-on elsewhere.
- **`NPCs[]`:** Recut listed row text in place. Do not move sheets into lore.
- **Triggers:** Recut existing `effectGiveInfo` / `effectModifyInstructionBlock` **content** strings if already present. Do not add, remove, or retarget triggers. Frozen: PawScript, id lists, player `firstInput` replacements.
- **`secretInfo` template:** Recut labels in the existing template. Do not convert it to a new delta/cap design. Player `outcomeDescription` stays literary.

---

## 10. Optional telegraph dialect

Use only on leftover unique **rule** text after levers 1–4. Pick **one** variant per block: ASCII operators **or** tight imperative English.

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

Label-first lines. One claim per line. Keep exact: proper nouns, tracker display names, YAML keys. Drop filler, **not** constraints. Lab notes → `designNotes`. Do not put PawScript / `<<>>` in AI-facing text. Do not invent glossary codes. Article-only stripping is not worth it.

**Before:** When the player rests for a full night, advance the calendar by one day unless they are in a combat encounter. Resting restores health by 20 points but cannot exceed the maximum. If health is already full, resting still advances time. Never restore health during an active combat turn.

**After:**

```
Rest: full night -> calendar_day^1 EXCEPT active combat
Rest => health^20 Cap max_health
IF health = max THEN rest still advances time
FORBID: health restore during combat turn
```

If a model misreads symbols, use tight imperative English instead.

---

## 11. Agent workflow

1. **Inventory** always-on fields and measure (§5). Snapshot the list of extra instruction blocks, tracked items, lore entries, and triggers — structure must match after.
2. **List constraints** for each block you will touch.
3. **Apply levers 1–4** in the same fields. Do not create new homes.
4. **Optional telegraph** leftover unique law (§10).
5. **Quality gate** (§8) + omission QA (§7) + structure check (§2).
6. **Measure again.**
7. **Play-test** the same playable, same opening (5–10 turns; `summaryRequest` through first fold, turn 9+).
8. **Parity checklist**
   - [ ] Same blocks, trackers, lore entries, and triggers as the source
   - [ ] Player heading structure unchanged
   - [ ] Core mechanic writes still obey live FORBID rules
   - [ ] Images: face lock / clothing copy-strings verbatim
   - [ ] Constraint diff passes on 3 random rules
   - [ ] No drift on safety/agency constraints

If play drifts or structure changed, revert that block.

---

## 12. Anti-patterns and when to stop

- Moving rules into lore, GiveInfo, hidden trackers, or new extra instruction blocks
- Changing `hidden` / `hidden_boring` or sealing spent story
- New line caps, delta `secretInfo`, or YAML schema
- Stripping playable-bio appearance because YAML exists
- Deleting examples that are not duplicates
- Invented glossary codes; article-only stripping; token-deletion tools
- Telegraphing image copy-strings, clothing templates, `authorStyle` voice, or `outcomeDescription`
- Renaming YAML keys, tracker display names, or lore keywords
- Compensating `FORBID:` after deleting a positive rule
- Teaching PawScript / `<<>>` to the storyteller, or adding `FORBID: <<>> dump`
- Measuring success by JSON kilobytes

**Stop** when text is already atomic, tone **is** the rule, ratio gain is under ~15% on labelled text, or a rewrite fails constraint diff, play parity, or the structure check.
