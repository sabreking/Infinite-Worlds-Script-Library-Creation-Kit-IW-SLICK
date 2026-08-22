#!/usr/bin/env python3
"""Build the IW-SLICK site and The Script Library paste kit from 2.38 JSON.

docs/index.html is the repo home (contributions). Library pages are the paste kit.
Teaching copy stays in amateur English. Module bodies are html.escape of the export.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "library" / "The Script Library 2.38.json"
DOCS = ROOT / "docs"

LIB_NAV = [
    ("library.html", "Looks"),
    ("writing.html", "Story voice"),
    ("extras.html", "Add-ons"),
]

CREDITS = (
    "KaapstadMK, with pieces from Xyphrax, Thyr, TWNT, Tori, Funky Munky, "
    "MrDrunkinDragon, WolfishGrimm, and SpacemanSpiff"
)

FRAME_FIELDS = [
    ("imageStyleCharacterPre", "Image style — people — prefix"),
    ("imageStyleCharacterPost", "Image style — people — suffix"),
    ("imageStyleNonCharacterPre", "Image style — not people — prefix"),
    ("imageStyleNonCharacterPost", "Image style — not people — suffix"),
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


def page_shell(title: str, description: str, body: str, mode: str = "library") -> str:
    if mode == "home":
        nav = ""
        footer = (
            "<p>IW-SLICK is a public copy-paste kit for "
            '<a href="https://infiniteworlds.app">Infinite Worlds</a> world creators. '
            "Contributions from the community. More will land here.</p>"
            "<p>License: GPL-3.0</p>"
        )
    else:
        nav = "\n".join(f'<a href="{href}">{esc(label)}</a>' for href, label in LIB_NAV)
        footer = (
            f"<p>The Script Library — copy from these pages into Infinite Worlds. "
            f"A contribution from <strong>{esc(CREDITS)}</strong>.</p>"
            '<p>Shared world: <a href="https://infiniteworlds.app/shared/7zDKHR">'
            "infiniteworlds.app/shared/7zDKHR</a> · "
            '<a href="index.html">IW-SLICK home</a></p>'
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
<a class="logo" href="index.html">IW-SLICK</a>
<nav>{nav}</nav>
</div>
</header>
<main class="wrap">
{body}
<footer>
{footer}
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
    bits = [
        boxes.box("Name this item exactly", item["name"]),
        (
            '<div class="ok"><p><strong>Settings on the Items to track screen</strong></p>'
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


SCRIPTS = [
    {
        "file": "pd.html",
        "hub": "Photos of people",
        "hub_line": "Photographs, live-action stills, video-game photos.",
        "title": "Photos of people",
        "block": "PD Condensed (new main)",
        "frame": "photo",
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
        "frame": "paint",
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
        "frame": "photo",
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
        "frame": "manga",
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
        "frame": "mixed",
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
        "frame": "mixed",
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
        "frame": "mixed",
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
        "frame": "mixed",
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

SCRIPT_BY_FILE = {s["file"]: s for s in SCRIPTS}

LIB_GROUPS = [
    ("Photographs — pick one", ["pd.html", "lean.html"]),
    ("Painted / comic — pick one", ["artist.html", "manga.html"]),
    ("Crowd / two people — pick one", ["bob-ross.html", "dual.html"]),
    ("One remembered face — pick one", ["single.html", "bareback.html"]),
]


def exact_name(script: dict, blocks: dict) -> str:
    return blocks[script["block"]]["name"]


def look_card(script: dict, blocks: dict) -> str:
    exact = exact_name(script, blocks)
    face = (
        "The game remembers the face"
        if script["family"] == "none"
        else "A new picture every time"
    )
    space = " The name ends with a space — copy it exactly." if exact.endswith(" ") else ""
    return (
        f'<a class="card" href="{script["file"]}">'
        f"<strong>{esc(script['hub'])}</strong>"
        f'<p class="chip">{esc(exact)}</p>'
        f"<p>{esc(script['hub_line'])}</p>"
        f'<p class="face">{esc(face)}.{esc(space)}</p>'
        f'<span class="btn">OPEN THIS</span></a>'
    )


def frame_keep(kind: str) -> str:
    extra = (
        "<li>If the game does not show sex in pictures, delete sexually stylized / erotic / genitalia phrases.</li>"
        "<li>Hidden labels like <code>&lt;#TONE#&gt;</code> are ignored. Everything after a label is live until you delete that paragraph.</li>"
    )
    if kind == "photo":
        body = (
            "<li>Keep tone and lines that sound like photos or CGI.</li>"
            "<li>Delete the manga/comic-only paragraph.</li>"
        )
    elif kind == "paint":
        body = (
            "<li>Keep paint and brush words.</li>"
            "<li>Delete camera-film words and Unreal Engine lines unless you truly want a game screenshot.</li>"
            "<li>Delete the manga/comic-only paragraph.</li>"
        )
    elif kind == "manga":
        body = (
            "<li>Keep the manga/comic paragraph.</li>"
            "<li>Delete Unreal Engine lines.</li>"
        )
    else:
        body = (
            "<li>This look can be photos or a painting. Keep the paragraphs that match the side you filled in the picture rules. Delete the other.</li>"
            "<li>Delete the manga/comic-only paragraph unless you actually want comic pages (you probably wanted the manga look instead).</li>"
        )
    return f'<div class="panel"><p><strong>Keep or delete for this look</strong></p><ul>{body}{extra}</ul></div>'


def frame_boxes(boxes: Boxes, game: dict) -> str:
    bits = []
    for key, label in FRAME_FIELDS:
        bits.append(f"<h3>{esc(label)}</h3>")
        bits.append(boxes.box(label, game[key]))
    return "\n".join(bits)


def notebook_step(script: dict, trackers: dict, boxes: Boxes) -> str:
    if script["family"] == "none":
        return (
            '<div class="ok"><p><strong>Create no appearance notebooks.</strong> '
            "The game remembers the face without them. Skip this step.</p></div>"
        )
    if script["family"] == "pd":
        player = trackers["Player Appearance"]
        small = trackers["NPC Appearance small cast"]
        large = trackers["NPC Appearance (large cast)"]
        rel = trackers["Relationship Tracker"]
        few_h = "A few people — copy this one, skip the large list"
        many_h = "Many people — copy these two, skip the small list"
    else:
        player = trackers["Player Appearance for Bob Ross/Wrangler"]
        small = trackers["NPC Appearance small, for Bob Ross/Wrangler"]
        large = trackers["NPC Appearance large, for Bob Ross/Wrangler"]
        rel = trackers["Relationship Tracker"]
        few_h = "A few people — copy this one, skip the large list"
        many_h = "Many people — copy these two, skip the small list (the large name ends with a space)"
    return (
        "<p>Always copy the player notebook. Then copy <strong>either</strong> the few-people list "
        "<strong>or</strong> the many-people pair — not both.</p>"
        f"<h3>Always — player</h3>\n{tracker_boxes(boxes, player)}\n"
        '<div class="or-split">'
        f"<section><h3>{esc(few_h)}</h3>\n{tracker_boxes(boxes, small)}</section>"
        f"<section><h3>{esc(many_h)}</h3>\n{tracker_boxes(boxes, large)}\n"
        f"{tracker_boxes(boxes, rel)}</section>"
        "</div>"
    )


def write_script_page(script: dict, blocks: dict, trackers: dict, game: dict) -> None:
    boxes = Boxes()
    block = blocks[script["block"]]
    exact = block["name"]
    space = (
        "<p><strong>The name ends with a space.</strong> Copy it exactly from the box.</p>"
        if exact.endswith(" ")
        else ""
    )
    done = """
<div class="ok">
<p><strong>Pictures are done</strong> when those four steps are in your game. Optional next:</p>
<p><a class="btn" href="writing.html">STORY VOICE</a>
<a class="btn" href="extras.html">EXTRA WRITING</a>
<a class="btn" href="bodies.html">BODIES</a>
<a class="btn" href="creatures.html">CREATURES</a></p>
</div>
"""
    body = f"""
<p class="bubble">STAY ON THIS PAGE</p>
<h1>{esc(script["title"])}</h1>
<p class="chip">{esc(exact)}</p>
<p class="lede">{esc(script["when"])}</p>
<nav class="toc">
<a href="#step1">1. Picture rules</a>
<a href="#step2">2. Notebooks</a>
<a href="#step3">3. Fill blanks</a>
<a href="#step4">4. Image style</a>
</nav>
<section class="step" id="step1">
<h2>Step 1 — Extra Instruction Blocks</h2>
<div class="warn"><p>{esc(script["avoid"])}</p></div>
{space}
{block_box(boxes, block)}
</section>
<section class="step" id="step2">
<h2>Step 2 — Items to track</h2>
{notebook_step(script, trackers, boxes)}
</section>
<section class="step" id="step3">
<h2>Step 3 — Fill blanks on what you pasted</h2>
<div class="panel">{script["after"]}</div>
</section>
<section class="step" id="step4">
<h2>Step 4 — Image style</h2>
<p>Paste these four boxes into Image style prefix and suffix. Then keep or delete paragraphs for <em>this</em> look.</p>
{frame_keep(script["frame"])}
{frame_boxes(boxes, game)}
</section>
{done}
"""
    (DOCS / script["file"]).write_text(
        page_shell(
            f"{script['title']} — The Script Library",
            script["hub_line"],
            body,
        ),
        encoding="utf-8",
    )


def picker_body(blocks: dict, intro: str) -> str:
    groups = []
    for heading, files in LIB_GROUPS:
        cards = "".join(look_card(SCRIPT_BY_FILE[f], blocks) for f in files)
        groups.append(f'<div class="group"><h2>{esc(heading)}</h2><div class="grid">{cards}</div></div>')
    quiet = """
<p class="quiet">After pictures work:
<a href="writing.html">Story voice</a> ·
<a href="extras.html">Extra writing</a> ·
<a href="bodies.html">Bodies</a> ·
<a href="creatures.html">Creatures</a></p>
"""
    return f"""
<p class="bubble">THE SCRIPT LIBRARY</p>
<h1>Pick one look.</h1>
<p class="lede">{esc(intro)}</p>
<p class="ok">Stay on that look’s page until pictures work. Come back later for story voice or add-ons.</p>
{"".join(groups)}
{quiet}
"""


def write_index() -> None:
    body = f"""
<p class="bubble">IW-SLICK</p>
<h1>Copy-paste kit.</h1>
<p class="lede">A public kit for Infinite Worlds world creators. Contributions from the community. More will land here.</p>
<h2>Contributions</h2>
<div class="grid">
<a class="card" href="library.html">
<strong>The Script Library</strong>
<p>Picture scripts, story voice, extras — copy from the page into Infinite Worlds.</p>
<p>From {esc(CREDITS)}.</p>
<span class="btn">OPEN THIS</span>
</a>
<div class="card soon">
<strong>More later</strong>
<p>Other contributions will show up on this board. This home is for the whole kit, not only one library.</p>
</div>
</div>
"""
    (DOCS / "index.html").write_text(
        page_shell(
            "IW-SLICK — Infinite Worlds copy-paste kit",
            "IW-SLICK is a public copy-paste kit for Infinite Worlds. Contributions from the community.",
            body,
            mode="home",
        ),
        encoding="utf-8",
    )


def write_library(blocks: dict) -> None:
    intro = (
        "Open one picture look. The card shows the exact Extra Instruction Block name. "
        "Copy everything on that page. You do not open a JSON file."
    )
    (DOCS / "library.html").write_text(
        page_shell(
            "The Script Library — pick a look",
            "Pick one picture script by name. Stay on that page until pictures work.",
            picker_body(blocks, intro),
        ),
        encoding="utf-8",
    )


def write_start(blocks: dict) -> None:
    intro = (
        "You are in The Script Library. Open a look below. Stay on that page until pictures work. "
        "The card shows the exact Extra Instruction Block name."
    )
    (DOCS / "start.html").write_text(
        page_shell(
            "The Script Library — pick a look",
            "Open one picture look and finish pictures on that page.",
            picker_body(blocks, intro),
        ),
        encoding="utf-8",
    )


def write_writing(game: dict, blocks: dict) -> None:
    boxes = Boxes()
    story = blocks["Storymaster + SecretInfo"]
    body = f"""
<p class="bubble">STORY VOICE</p>
<h1>How the story talks.</h1>
<p class="lede">Do this <strong>once</strong>, not once per picture look. Paste in the order of the Infinite Worlds screen.</p>
<nav class="toc">
<a href="#w1">1. Main Instructions</a>
<a href="#w2">2. Storymaster</a>
<a href="#w3">3. Author style</a>
<a href="#w4">4. Evaluation</a>
<a href="#w5">5. Description</a>
<a href="#w6">6. Summarization</a>
</nav>
<section class="step" id="w1">
<h2>Step 1 — Main Instructions</h2>
<p>Fill <code>[insert full author style here]</code> with the same voice you put in Author style.</p>
{boxes.box("Main Instructions — Split Game Master", split_gm(game))}
</section>
<section class="step" id="w2">
<h2>Step 2 — Extra Instruction Blocks (Storymaster)</h2>
<p>Name it exactly <strong>{esc(story['name'])}</strong> (the name ends with a space). After you paste, fill the square brackets: genres, tone, themes, conflicts, how many turns, length of time.</p>
{block_box(boxes, story)}
</section>
<section class="step" id="w3">
<h2>Step 3 — Author style</h2>
{boxes.box("Author style", game["authorStyle"])}
</section>
<section class="step" id="w4">
<h2>Step 4 — Evaluation</h2>
{boxes.box("Evaluation", game["evaluationRequest"])}
</section>
<section class="step" id="w5">
<h2>Step 5 — Description</h2>
<p>This is story voice, not picture rules. If you already wrote Description instructions for images, do not overwrite them with this.</p>
{boxes.box("Description", game["descriptionRequest"])}
</section>
<section class="step" id="w6">
<h2>Step 6 — Summarization</h2>
{boxes.box("Summarization", game["summaryRequest"])}
</section>
<p class="quiet">Optional add-ons:
<a href="extras.html">Extra writing</a> ·
<a href="bodies.html">Bodies</a> ·
<a href="creatures.html">Creatures</a> ·
<a href="library.html">Back to looks</a></p>
"""
    (DOCS / "writing.html").write_text(
        page_shell(
            "Story voice — The Script Library",
            "Split Game Master, Storymaster, Author style, Evaluation, Description, Summarization.",
            body,
        ),
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
<p class="bubble">ADD-ONS</p>
<h1>Optional extras.</h1>
<p class="lede">Use these after pictures work. Each one is its own Extra Instruction Block. Copy only what your game needs. More blocks cost more every turn.</p>
<p class="quiet"><a href="extras.html">Extra writing</a> · <a href="bodies.html">Bodies</a> · <a href="creatures.html">Creatures</a></p>
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
        page_shell(
            "Add-ons — The Script Library",
            "Characterization, Pacing, Sexual Content, Period Knowledge, Narrative Craft, Lion, Leopard.",
            "".join(bits),
        ),
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
<p class="quiet"><a href="extras.html">Extra writing</a> · <a href="bodies.html">Bodies</a> · <a href="creatures.html">Creatures</a></p>
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
        page_shell(
            "Body add-ons — The Script Library",
            "Expanded female, cups, male, futa, hypertrophy, Cup Sizes notebook.",
            "".join(bits),
        ),
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
<p class="quiet"><a href="extras.html">Extra writing</a> · <a href="bodies.html">Bodies</a> · <a href="creatures.html">Creatures</a></p>
"""
    ]
    for name, blurb in CREATURES:
        block = blocks[name]
        bits.append(f"<h2>{esc(block['name'])}</h2>")
        bits.append(f"<p>{esc(blurb)}</p>")
        bits.append(f"<p>Name it exactly: <strong>{esc(block['name'])}</strong></p>")
        bits.append(block_box(boxes, block))
    (DOCS / "creatures.html").write_text(
        page_shell(
            "Creature add-ons — The Script Library",
            "Monstergirl, Pokégirl, and Alien Extra Instruction Blocks.",
            "".join(bits),
        ),
        encoding="utf-8",
    )


def write_frame(game: dict) -> None:
    boxes = Boxes()
    bits = [
        """
<p class="bubble">BACKUP</p>
<h1>Words around the picture.</h1>
<p class="lede">You do not need this page to finish a look. Each look already has these four boxes and the keep/delete notes for that look. This is the same paste with every look listed.</p>
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
    for key, label in FRAME_FIELDS:
        bits.append(f"<h2>{esc(label)}</h2>")
        bits.append(boxes.box(label, game[key]))
    (DOCS / "frame.html").write_text(
        page_shell("Picture frame words — The Script Library", "Image style prefix and suffix templates.", "".join(bits)),
        encoding="utf-8",
    )


def write_dont() -> None:
    body = """
<p class="bubble">BACKUP</p>
<h1>Never mix these.</h1>
<p class="lede">Each look page already lists the fights for that look. This is the full list.</p>
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
<p><a class="btn" href="library.html">BACK TO LOOKS</a></p>
"""
    (DOCS / "dont.html").write_text(
        page_shell(
            "Never mix these — The Script Library",
            "Conflicts: two picture scripts, Lean+PD, Bareback+Single, both notebook families.",
            body,
        ),
        encoding="utf-8",
    )


def main() -> None:
    game = load_game()
    blocks = block_map(game)
    trackers = tracker_map(game)
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "assets").mkdir(parents=True, exist_ok=True)
    write_index()
    write_library(blocks)
    write_start(blocks)
    for script in SCRIPTS:
        write_script_page(script, blocks, trackers, game)
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
