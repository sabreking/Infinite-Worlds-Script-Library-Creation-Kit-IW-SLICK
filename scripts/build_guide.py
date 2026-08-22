#!/usr/bin/env python3
"""Build the amateur copy-paste HTML kit from The Script Library 2.38.json.

The website is the kit. Visitors copy from boxes into Infinite Worlds.
Teaching copy stays in amateur English. Module bodies are html.escape of the export.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "library" / "The Script Library 2.38.json"
DOCS = ROOT / "docs"

NAV = [
    ("index.html", "Pick a look"),
    ("start.html", "First time"),
    ("writing.html", "Story voice"),
    ("extras.html", "Extra writing"),
    ("bodies.html", "Bodies"),
    ("creatures.html", "Creatures"),
    ("frame.html", "Picture frame"),
    ("dont.html", "Never mix"),
]


def esc(text: str) -> str:
    return html.escape(text or "", quote=False)


def load_game() -> dict:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def block_map(game: dict) -> dict[str, dict]:
    out = {}
    for block in game["instructionBlocks"]:
        out[block["name"].strip()] = block
        out[block["name"]] = block
    return out


def tracker_map(game: dict) -> dict[str, dict]:
    out = {}
    for item in game["trackedItems"]:
        out[item["name"].strip()] = item
        out[item["name"]] = item
    return out


def split_gm(game: dict) -> str:
    raw = game["instructions"]
    marker = "Image style prefix"
    if marker in raw:
        return raw.split(marker)[0].strip()
    return raw.strip()


def page_shell(title: str, description: str, body: str) -> str:
    nav = "\n".join(
        f'<a href="{href}">{esc(label)}</a>' for href, label in NAV
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bangers&family=Nunito:wght@600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/guide.css">
</head>
<body>
<header class="top">
<div class="row">
<a class="logo" href="index.html">THE SCRIPT LIBRARY</a>
<nav>{nav}</nav>
</div>
</header>
<main class="wrap">
{body}
<footer>
<p>Copy from the boxes on these pages into Infinite Worlds. A contribution from <strong>KaapstadMK</strong>, with pieces from Xyphrax, Thyr, TWNT, Tori, Funky Munky, MrDrunkinDragon, WolfishGrimm, and SpacemanSpiff.</p>
<p>Shared world: <a href="https://infiniteworlds.app/shared/7zDKHR">infiniteworlds.app/shared/7zDKHR</a></p>
</footer>
</main>
<script src="assets/copy.js"></script>
</body>
</html>
"""


class Boxes:
    def __init__(self) -> None:
        self.n = 0

    def box(self, title: str, text: str) -> str:
        self.n += 1
        i = f"c{self.n}"
        return (
            f'<div class="copybox"><header><span>{esc(title)}</span>'
            f'<button type="button" class="sticker" data-copy="{i}">COPY</button></header>'
            f'<pre id="{i}">{esc(text)}</pre></div>'
        )


def vis_line(item: dict) -> str:
    vis = item.get("visibility") or "everyone"
    if vis == "ai_only":
        return "Visible to: AI only (the player does not see this notebook)"
    if vis == "hidden" or vis == "hidden_boring":
        return "Visible to: hidden"
    return "Visible to: everyone"


def auto_line(item: dict) -> str:
    return "Auto-update: on" if item.get("autoUpdate") else "Auto-update: off"


def tracker_boxes(boxes: Boxes, item: dict) -> str:
    name = item["name"]
    bits = [
        boxes.box("Name this item exactly", name),
        (
            "<div class=\"ok\"><p><strong>Settings on the Items to track screen</strong></p>"
            f"<ul><li>Type: YAML</li><li>{esc(vis_line(item))}</li>"
            f"<li>{esc(auto_line(item))}</li></ul></div>"
        ),
    ]
    labels = [
        ("description", "Description (what this notebook is for)"),
        ("updateInstructions", "Update rules (when to change it)"),
        ("formatExample", "Example of how it should look"),
        ("formatSchema", "The shape it should keep"),
        ("initialValue", "Starting value"),
    ]
    for key, label in labels:
        val = item.get(key) or ""
        if val.strip():
            bits.append(boxes.box(label, val))
    return "\n".join(bits)


def block_box(boxes: Boxes, block: dict, title: str | None = None) -> str:
    name = block["name"]
    heading = title or f"Paste into Extra Instruction Blocks — name it exactly: {name}"
    return boxes.box(heading, block["content"])


PD_FAMILY = [
    "Player Appearance",
    "NPC Appearance small cast",
    "NPC Appearance (large cast)",
    "Relationship Tracker",
]
WRANGLER_FAMILY = [
    "Player Appearance for Bob Ross/Wrangler",
    "NPC Appearance small, for Bob Ross/Wrangler",
    "NPC Appearance large, for Bob Ross/Wrangler",
    "Relationship Tracker",
]

SCRIPTS = [
    {
        "file": "pd.html",
        "hub": "Photos of people",
        "hub_line": "Photographs, live-action stills, video-game photos.",
        "title": "Photos of people",
        "block": "PD Condensed (new main)",
        "when": (
            "Use this when you want the pictures to look like photographs — "
            "movie stills, camera language, realistic people. A new picture is "
            "drawn every time, so you keep a notebook of how people look."
        ),
        "avoid": (
            "Do not turn on any other picture script. Do not also use Lean Director "
            "(that is the cheaper photo script — pick one). Do not make appearance "
            "notebooks whose names include “for Bob Ross/Wrangler”."
        ),
        "family": "pd",
        "after": (
            "<ul>"
            "<li>Find hidden notes wrapped in <code>&lt;# … #&gt;</code>. The game ignores those until you delete the wrap.</li>"
            "<li>Fill the budget / Hollywood-or-indie / genre line in square brackets, then unwrap it.</li>"
            "<li>Write 3 to 5 mood words, then unwrap that line too.</li>"
            "<li>Unwrap sex or fight pose packs only if the game actually shows those scenes.</li>"
            "</ul>"
        ),
    },
    {
        "file": "artist.html",
        "hub": "A painting",
        "hub_line": "Oil, watercolor, illustration — drawn art, not a camera.",
        "title": "A painting",
        "block": "Artist script",
        "when": (
            "Use this when you want the pictures to look painted or drawn — "
            "oil, watercolor, print, illustration. Same “new picture every time” "
            "job as the photo script, with painter words instead of camera words."
        ),
        "avoid": (
            "Do not turn on any other picture script. Do not pick this just because "
            "you want comic pages — that is the manga script. Do not make appearance "
            "notebooks whose names include “for Bob Ross/Wrangler”."
        ),
        "family": "pd",
        "after": (
            "<ul>"
            "<li>Fill the period / region / master-or-folk / patron / artwork line in square brackets, then unwrap the hidden wrap.</li>"
            "<li>Write 3 to 5 mood words and unwrap that line.</li>"
            "<li>Unwrap sex or fight pose packs only if the game actually shows those scenes.</li>"
            "</ul>"
        ),
    },
    {
        "file": "lean.html",
        "hub": "Cheap photos",
        "hub_line": "Same photo look, shorter rules, still a new picture every time.",
        "title": "Cheap photos",
        "block": "Lean Director",
        "when": (
            "Use this when you still want photographs, but a shorter rule sheet. "
            "A new picture is drawn every time, so you still keep appearance notebooks."
        ),
        "avoid": (
            "Do not also use PD Condensed (new main). Do not turn on any other picture "
            "script. Do not make appearance notebooks whose names include “for Bob Ross/Wrangler”."
        ),
        "family": "pd",
        "after": (
            "<ul>"
            "<li>Fill the budget / Hollywood-or-indie / genre line, then unwrap it.</li>"
            "<li>Write 3 to 5 mood words and unwrap that line.</li>"
            "<li>Unwrap sex or fight pose packs only if the game actually shows those scenes.</li>"
            "</ul>"
        ),
    },
    {
        "file": "manga.html",
        "hub": "Manga pages",
        "hub_line": "Three comic panels with talk bubbles.",
        "title": "Manga pages",
        "block": "Manga (Artist Base)",
        "when": (
            "Use this when you want comic pages — three panels and talk bubbles. "
            "A new picture is drawn every time, so you keep appearance notebooks."
        ),
        "avoid": (
            "Do not turn on any other picture script. The painting script is one still "
            "picture, not comic pages. Do not make appearance notebooks whose names include “for Bob Ross/Wrangler”."
        ),
        "family": "pd",
        "after": (
            "<ul>"
            "<li>Fill the tradition line (Shonen / Seinen / manga / manhwa, and so on) in square brackets, then unwrap it.</li>"
            "<li>Write 3 to 5 mood words and unwrap that line.</li>"
            "<li>Unwrap sex or fight pose packs only if the game actually shows those scenes.</li>"
            "</ul>"
        ),
    },
    {
        "file": "bob-ross.html",
        "hub": "A crowded scene",
        "hub_line": "Lots of people arranged in one picture.",
        "title": "A crowded scene",
        "block": "Bob Ross script",
        "when": (
            "Use this when the shot is a crowd arranged in space, not two people "
            "talking in close-up. A new picture is drawn every time. Use the appearance "
            "notebooks whose names say “for Bob Ross/Wrangler”."
        ),
        "avoid": (
            "Do not turn on any other picture script. Do not use the notebooks named "
            "only Player Appearance or NPC Appearance (those belong to the photo / painting / manga scripts)."
        ),
        "family": "wrangler",
        "after": (
            "<ul>"
            "<li>There is a photo-or-painting slot. Fill one side, delete the other, then unwrap it.</li>"
            "<li>Write 3 to 5 mood words and unwrap that line.</li>"
            "<li>Unwrap sex or fight pose packs only if the game actually shows those scenes.</li>"
            "</ul>"
        ),
    },
    {
        "file": "dual.html",
        "hub": "Two people",
        "hub_line": "Two named people in the picture, cheaper than the photo script.",
        "title": "Two people",
        "block": "Vanilla Bean IW Wrangler (Dual subject)",
        "when": (
            "Use this when two named people share the picture and you want a cheaper "
            "rule sheet than the photo script. A new picture is drawn every time. "
            "Use the “for Bob Ross/Wrangler” notebooks."
        ),
        "avoid": (
            "Do not turn on any other picture script. This is not “the one-person script plus a second person.” "
            "Do not use the notebooks named only Player Appearance or NPC Appearance."
        ),
        "family": "wrangler",
        "after": (
            "<ul>"
            "<li>There is a photo-or-painting slot. Fill one side, delete the other, then unwrap it.</li>"
            "<li>Write 3 to 5 mood words and unwrap that line.</li>"
            "<li>Unwrap sex or fight pose packs only if the game actually shows those scenes.</li>"
            "</ul>"
        ),
    },
    {
        "file": "single.html",
        "hub": "One person the game remembers",
        "hub_line": "One face that stays the same from picture to picture.",
        "title": "One person the game remembers",
        "block": "Vanilla IW Wrangler (Single subject)",
        "when": (
            "Use this when there is one named person and you want the game to remember "
            "the face. Create no appearance notebooks."
        ),
        "avoid": (
            "Do not turn on any other picture script. Do not also use Bareback Wrangler. "
            "Do not create Player Appearance or NPC Appearance notebooks — those stop the game from remembering the face."
        ),
        "family": "none",
        "after": (
            "<ul>"
            "<li>Keep spelling the person’s name the same way every turn.</li>"
            "<li>Leave the hidden “clothes changed” note wrapped. Do not unwrap it.</li>"
            "<li>There is a photo-or-painting slot. Fill one side, delete the other, then unwrap it.</li>"
            "<li>Write 3 to 5 mood words and unwrap that line.</li>"
            "</ul>"
        ),
    },
    {
        "file": "bareback.html",
        "hub": "One person, lean language",
        "hub_line": "One remembered face, with shorter picture rules.",
        "title": "One person, lean language",
        "block": "Bareback Wrangler",
        "when": (
            "Use this when there is one named person, you want the game to remember "
            "the face, and you want shorter picture rules. Create no appearance notebooks."
        ),
        "avoid": (
            "Do not turn on any other picture script. Do not also use the one-person Wrangler. "
            "Do not create appearance notebooks."
        ),
        "family": "none",
        "after": (
            "<ul>"
            "<li>Delete the live line that says to pull appearance from tracked items. That line does not belong on this script.</li>"
            "<li>There is a photo-or-painting slot. Fill one side, delete the other, then unwrap it.</li>"
            "<li>Write 3 to 5 mood words and unwrap that line.</li>"
            "<li>Unwrap sex or fight pose packs only if the game actually shows those scenes.</li>"
            "</ul>"
        ),
    },
]


def shopping_html(script: dict, blocks: dict) -> str:
    block = blocks[script["block"]]
    exact = block["name"]
    space_note = ""
    if exact.endswith(" "):
        space_note = (
            "<p><strong>The name ends with a space.</strong> Copy it exactly from the box below.</p>"
        )
    if script["family"] == "none":
        notes = (
            "<p><strong>Items to track:</strong> create none for appearance. "
            "The game remembers the face without those notebooks.</p>"
        )
    elif script["family"] == "pd":
        notes = """
<p><strong>Items to track</strong> — Type: YAML, Visible to: everyone, Auto-update: on.</p>
<ul>
<li>Always: <strong>Player Appearance</strong></li>
<li>A few people: <strong>NPC Appearance small cast</strong></li>
<li>Many people: <strong>NPC Appearance (large cast)</strong> and also <strong>Relationship Tracker</strong> (that last one is visible to AI only)</li>
</ul>
"""
    else:
        notes = """
<p><strong>Items to track</strong> — Type: YAML, Visible to: everyone, Auto-update: on. Use the names that say “for Bob Ross/Wrangler”.</p>
<ul>
<li>Always: <strong>Player Appearance for Bob Ross/Wrangler</strong></li>
<li>A few people: <strong>NPC Appearance small, for Bob Ross/Wrangler</strong></li>
<li>Many people: <strong>NPC Appearance large, for Bob Ross/Wrangler</strong> (this name ends with a space) and also <strong>Relationship Tracker</strong> (visible to AI only)</li>
</ul>
"""
    return f"""
<div class="panel">
<p>One Extra Instruction Block. Name it exactly:</p>
<p><strong>{esc(exact)}</strong></p>
{space_note}
{notes}
</div>
"""


def write_script_page(script: dict, blocks: dict, trackers: dict) -> None:
    boxes = Boxes()
    block = blocks[script["block"]]
    body = f"""
<p class="bubble">PICTURE SCRIPT</p>
<h1>{esc(script["title"])}</h1>
<div class="panel">
<h2>Use this when</h2>
<p class="lede">{esc(script["when"])}</p>
</div>
<div class="warn">
<h2>Do not use with</h2>
<p>{esc(script["avoid"])}</p>
</div>
<h2>Shopping list</h2>
{shopping_html(script, blocks)}
<h2>After you paste</h2>
<div class="panel">{script["after"]}</div>
<h2>Copy boxes</h2>
{block_box(boxes, block)}
"""
    if script["family"] == "pd":
        names = PD_FAMILY
    elif script["family"] == "wrangler":
        names = WRANGLER_FAMILY
    else:
        names = []
    for name in names:
        item = trackers[name]
        body += f"<h3>Notebook: {esc(item['name'])}</h3>\n"
        body += tracker_boxes(boxes, item)
    (DOCS / script["file"]).write_text(
        page_shell(
            f"{script['title']} — The Script Library",
            script["hub_line"],
            body,
        ),
        encoding="utf-8",
    )


def write_index() -> None:
    cards = []
    for script in SCRIPTS:
        cards.append(
            f'<a class="card" href="{script["file"]}">'
            f'<strong>{esc(script["hub"])}</strong>'
            f'<p>{esc(script["hub_line"])}</p>'
            f'<span class="btn">OPEN THIS</span></a>'
        )
    extras = [
        ("start.html", "First time", "Six steps. No file talk."),
        ("writing.html", "Story voice", "Main Instructions, Storymaster, Description, Evaluation, Summarization."),
        ("extras.html", "Extra writing rules", "Characterization, pacing, sex, period, craft, Lion, Leopard."),
        ("bodies.html", "Body add-ons", "Expanded female, cups, male, futa, hypertrophy."),
        ("creatures.html", "Creature add-ons", "Monstergirl, Pokégirl, Alien."),
        ("frame.html", "Picture frame words", "The four Image style prefix and suffix boxes."),
        ("dont.html", "Never mix these", "The short list of fights."),
    ]
    more = []
    for href, title, line in extras:
        more.append(
            f'<a class="card" href="{href}"><strong>{esc(title)}</strong>'
            f"<p>{esc(line)}</p><span class=\"btn\">OPEN THIS</span></a>"
        )
    body = f"""
<p class="bubble">PICK A LOOK</p>
<h1>Copy from the page.</h1>
<p class="lede">This website is the kit. Open a look, press COPY, paste into Infinite Worlds. You do not open a JSON file.</p>
<p class="ok">Pick <strong>one</strong> picture look. Then add story voice, extra writing, bodies, or creatures if you want them.</p>
<div class="grid">
{"".join(cards)}
</div>
<h2>Also on the board</h2>
<div class="grid">
{"".join(more)}
</div>
"""
    (DOCS / "index.html").write_text(
        page_shell(
            "The Script Library — pick a look",
            "Amateur copy-paste kit for Infinite Worlds. Copy scripts from the page, not from a JSON file.",
            body,
        ),
        encoding="utf-8",
    )


def write_start() -> None:
    body = """
<p class="bubble">FIRST TIME</p>
<h1>Six steps.</h1>
<p class="lede">Use the words you already see on the Infinite Worlds screen.</p>
<ol class="steps">
<li><strong>Open your game.</strong> Stay in the editor. You are going to paste into fields that already exist.</li>
<li><strong>Main Instructions</strong> — paste the Split Game Master voice from the Story voice page. Fill the square brackets with how the story should sound.</li>
<li><strong>Extra Instruction Blocks</strong> — add <em>one</em> picture script from Pick a look. Name the block exactly as the shopping list says. Optional extra writing, bodies, and creatures are more Extra Instruction Blocks, each with its own name.</li>
<li><strong>Items to track</strong> — only the notebooks on that picture page. Type: YAML. Follow Visible to and Auto-update on the page. The one-person looks create no appearance notebooks.</li>
<li><strong>Description / Evaluation / Summarization</strong> — paste those three boxes from the Story voice page. Do not paste the story-voice Description over a Description you already wrote for pictures.</li>
<li><strong>Image style</strong> — paste the four prefix and suffix boxes from Picture frame words, then keep or delete paragraphs as that page says.</li>
</ol>
<p class="warn">Never turn on two picture scripts. If two looks both sound right, read Never mix these, then pick one.</p>
<p><a class="btn" href="index.html">PICK A LOOK</a> <a class="btn" href="dont.html">NEVER MIX</a></p>
"""
    (DOCS / "start.html").write_text(
        page_shell("First time — The Script Library", "Six steps to paste the Script Library into Infinite Worlds.", body),
        encoding="utf-8",
    )


def write_writing(game: dict, blocks: dict) -> None:
    boxes = Boxes()
    story = blocks["Storymaster + SecretInfo"]
    body = f"""
<p class="bubble">STORY VOICE</p>
<h1>How the story talks.</h1>
<p class="lede">These paste into Main Instructions, Extra Instruction Blocks, Author style, Evaluation, Description, and Summarization.</p>
<h2>Split Game Master</h2>
<p>Paste into <strong>Main Instructions</strong>. Fill <code>[insert full author style here]</code> with the same voice you put in Author style.</p>
{boxes.box("Main Instructions — Split Game Master", split_gm(game))}
<h2>Storymaster</h2>
<p>One Extra Instruction Block. Name it exactly <strong>{esc(story['name'])}</strong> (the name ends with a space). After you paste, fill the square brackets: genres, tone, themes, conflicts, how many turns, length of time.</p>
{block_box(boxes, story)}
<h2>Author style</h2>
<p>Paste into the <strong>Author style</strong> field.</p>
{boxes.box("Author style", game["authorStyle"])}
<h2>Evaluation</h2>
<p>Paste into <strong>Evaluation</strong>.</p>
{boxes.box("Evaluation", game["evaluationRequest"])}
<h2>Description</h2>
<p>Paste into <strong>Description</strong>. This is story voice, not picture rules. If you already wrote Description instructions for images, do not overwrite them with this.</p>
{boxes.box("Description", game["descriptionRequest"])}
<h2>Summarization</h2>
<p>Paste into <strong>Summarization</strong>.</p>
{boxes.box("Summarization", game["summaryRequest"])}
"""
    (DOCS / "writing.html").write_text(
        page_shell("Story voice — The Script Library", "Split Game Master, Storymaster, Author style, Evaluation, Description, Summarization.", body),
        encoding="utf-8",
    )


EXTRAS = [
    ("Characterization", "People stay in character."),
    ("Pacing", "Scenes do not rush or stall for no reason."),
    ("Sexual Content", "Sex writing rules. The block name ends with a space."),
    ("Period Knowledge", "Fill [time period] after you paste."),
    ("Narrative Craft", "Prose craft rules."),
    ("Lion Bugfixes", "Fixes for Lion-family models. The name ends with a space."),
    ("Leopard Bugfixes", "Fixes for Leopard models. The name ends with a space."),
]


def write_extras(blocks: dict) -> None:
    boxes = Boxes()
    bits = [
        """
<p class="bubble">EXTRA WRITING</p>
<h1>Optional story rules.</h1>
<p class="lede">Each one is its own Extra Instruction Block. Copy only the ones your game needs. More blocks cost more every turn.</p>
<div class="warn"><p><strong>Lion and Leopard:</strong> in Infinite Worlds settings, turn on “AI-specific extra instructions”. If that switch is off, Lion and Leopard hit every model.</p></div>
"""
    ]
    for name, blurb in EXTRAS:
        block = blocks[name]
        bits.append(f"<h2>{esc(block['name'].strip())}</h2>")
        bits.append(f"<p>{esc(blurb)}</p>")
        bits.append(f"<p>Name the Extra Instruction Block exactly: <strong>{esc(block['name'])}</strong></p>")
        bits.append(block_box(boxes, block))
    (DOCS / "extras.html").write_text(
        page_shell("Extra writing rules — The Script Library", "Characterization, Pacing, Sexual Content, Period Knowledge, Narrative Craft, Lion, Leopard.", "".join(bits)),
        encoding="utf-8",
    )


BODIES = [
    ("Expanded female appearance", "More body-size language for women."),
    ("WG's Bra Cup Sizing System", "Letter cup sizes in the picture rules."),
    ("Male Description (alternate for baseline female description in PD/Manga)", "Swap in male body language."),
    ("Futanari description block", "Futa body language."),
    ("Hypermasc/Hypertrophy module", "Very large male muscle and size language."),
]


def write_bodies(blocks: dict, trackers: dict) -> None:
    boxes = Boxes()
    cups = trackers["Cup Sizes"]
    bits = [
        """
<p class="bubble">BODY ADD-ONS</p>
<h1>Bodies.</h1>
<p class="lede">These are extra Extra Instruction Blocks. They fit the photo, painting, and manga scripts. Do not stack every body add-on at once.</p>
"""
    ]
    for name, blurb in BODIES:
        block = blocks[name]
        bits.append(f"<h2>{esc(block['name'])}</h2>")
        bits.append(f"<p>{esc(blurb)}</p>")
        bits.append(block_box(boxes, block))
    bits.append("<h2>Cup Sizes notebook</h2>")
    bits.append(
        "<p>Optional Items to track row if you want cup letters to persist. "
        "Type: YAML. Visible to: everyone. <strong>Auto-update: off</strong>.</p>"
    )
    bits.append(tracker_boxes(boxes, cups))
    (DOCS / "bodies.html").write_text(
        page_shell("Body add-ons — The Script Library", "Expanded female, cups, male, futa, hypertrophy, Cup Sizes notebook.", "".join(bits)),
        encoding="utf-8",
    )


CREATURES = [
    ("monstergirl plugin 1/3", "Monstergirl part 1 of 3. Paste all three."),
    ("Monstergirl plug-in 2/3", "Monstergirl part 2 of 3."),
    ("Monstergirl Plugin 3/3", "Monstergirl part 3 of 3."),
    ("Pokegirl plug in 1/2", "Pokégirl part 1 of 2. Paste both."),
    ("Pokegirl plug in 2/2", "Pokégirl part 2 of 2."),
    ("Alien plug-in 1/2", "Alien part 1 of 2. Paste both."),
    ("Alien plug-in 2/2", "Alien part 2 of 2."),
]


def write_creatures(blocks: dict) -> None:
    boxes = Boxes()
    bits = [
        """
<p class="bubble">CREATURE ADD-ONS</p>
<h1>Not-human people.</h1>
<p class="lede">Each numbered part is its own Extra Instruction Block. If you want monstergirls, paste 1, 2, and 3. Same idea for Pokégirl and Alien.</p>
"""
    ]
    for name, blurb in CREATURES:
        block = blocks[name]
        bits.append(f"<h2>{esc(block['name'])}</h2>")
        bits.append(f"<p>{esc(blurb)}</p>")
        bits.append(f"<p>Name it exactly: <strong>{esc(block['name'])}</strong></p>")
        bits.append(block_box(boxes, block))
    (DOCS / "creatures.html").write_text(
        page_shell("Creature add-ons — The Script Library", "Monstergirl, Pokégirl, and Alien Extra Instruction Blocks.", "".join(bits)),
        encoding="utf-8",
    )


def write_frame(game: dict) -> None:
    boxes = Boxes()
    fields = [
        ("imageStyleCharacterPre", "Image style — people — prefix"),
        ("imageStyleCharacterPost", "Image style — people — suffix"),
        ("imageStyleNonCharacterPre", "Image style — not people — prefix"),
        ("imageStyleNonCharacterPost", "Image style — not people — suffix"),
    ]
    bits = [
        """
<p class="bubble">PICTURE FRAME</p>
<h1>Words around the picture.</h1>
<p class="lede">These four boxes paste into Image style prefix and suffix. Hidden labels like <code>&lt;#TONE#&gt;</code> are ignored. Everything after a label is live until you delete that paragraph.</p>
<div class="panel">
<p><strong>Keep or delete, in plain English</strong></p>
<ul>
<li><strong>Photographs / cheap photos:</strong> keep tone and image-specific lines that sound like photos or CGI. Delete the manga/comic-only paragraph.</li>
<li><strong>A painting:</strong> keep paint and brush words. Delete camera-film words and Unreal Engine lines unless you truly want a game screenshot.</li>
<li><strong>Manga pages:</strong> keep the manga/comic paragraph. Delete Unreal Engine lines.</li>
<li><strong>A game without sex in the pictures:</strong> delete sexually stylized / erotic / genitalia phrases.</li>
</ul>
</div>
"""
    ]
    for key, label in fields:
        bits.append(f"<h2>{esc(label)}</h2>")
        bits.append(boxes.box(label, game[key]))
    (DOCS / "frame.html").write_text(
        page_shell("Picture frame words — The Script Library", "Image style prefix and suffix templates.", "".join(bits)),
        encoding="utf-8",
    )


def write_dont() -> None:
    body = """
<p class="bubble">HARD NO</p>
<h1>Never mix these.</h1>
<div class="warn">
<ul>
<li>Never two picture scripts in the same game.</li>
<li>Never Lean Director and PD Condensed together. They are the same photo job. Pick one.</li>
<li>Never Bareback Wrangler and the one-person Wrangler together. They are the same remembered-face job. Pick one.</li>
<li>Never both appearance notebook families. Photo / painting / manga / cheap photos use Player Appearance and NPC Appearance. Crowded scene / two people use the names that say “for Bob Ross/Wrangler”.</li>
<li>Never copy Foolproofing, Terminate, or Safeguard. Those stay in the library dump. They are not for a live game.</li>
<li>Never copy the old picture scripts (names that start with Old:). They are leftovers.</li>
<li>Do not overwrite Description instructions you already wrote for pictures with the story-voice Description paste.</li>
</ul>
</div>
<p><a class="btn" href="index.html">BACK TO PICK A LOOK</a></p>
"""
    (DOCS / "dont.html").write_text(
        page_shell("Never mix these — The Script Library", "Conflicts: two picture scripts, Lean+PD, Bareback+Single, both notebook families.", body),
        encoding="utf-8",
    )


def main() -> None:
    game = load_game()
    blocks = block_map(game)
    trackers = tracker_map(game)
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "assets").mkdir(parents=True, exist_ok=True)
    write_index()
    write_start()
    for script in SCRIPTS:
        write_script_page(script, blocks, trackers)
    write_writing(game, blocks)
    write_extras(blocks)
    write_bodies(blocks, trackers)
    write_creatures(blocks)
    write_frame(game)
    write_dont()
    pages = sorted(p.name for p in DOCS.glob("*.html"))
    print(f"Wrote {len(pages)} HTML pages from {JSON_PATH.name}")
    for name in pages:
        print(" ", name)


if __name__ == "__main__":
    main()
