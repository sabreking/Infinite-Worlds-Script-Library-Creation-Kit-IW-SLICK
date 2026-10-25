#!/usr/bin/env python3
"""Build the IW-SLICK site and The Script Library paste kit from the 3.29 JSON.

docs/index.html is the repo home (contributions). Library pages are the paste kit.
Teaching copy stays in amateur English. Module bodies are html.escape of the export.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "library" / "The Script Library 3.29.json"
DOCS = ROOT / "docs"

LIB_NAV = [
    ("library.html", "Looks"),
    ("writing.html", "Story voice"),
    ("extras.html", "Add-ons"),
    ("styles.html", "Styles"),
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

# Last export that still stored selectedAIProfiles (3.16). 3.29 ships the
# block text only, so the page tells people which models to tick.
MODEL_TICKS = {
    "Lion Bugfixes": (
        "smilodon, lynx, massivecat, smilodon-thinking, massivecat-thinking, "
        "lynx-thinking, smilodon-2-experimental, smilodon-2-experimental-thinking, "
        "galaxycat-experimental"
    ),
    "Leopard Bugfixes": "leopard, leopard-2",
    "Caracal Bugfixes": "caracal",
    "Dolphin Bugfixes": "dolphin",
}

SKIP_TRACKERS = {"Safeguard (Library only)"}
SKIP_TRIGGERS = {"Foolproofing (Library only)", "Terminate (library only)"}

STYLE_GROUPS = [
    (
        "Anime and comics",
        [
            "Wyvern Anime 1",
            "Wyvern Anime 2/Honkai Star Rail",
            "Painted Manga",
            "Monochrome manga",
            "Colorized Manga",
            "Shoujo VN",
            "Pulp-Manga Pinup",
        ],
    ),
    (
        "Paintings and drawings",
        [
            "(Improved) Vector Art",
            "Asterix",
            "Airbrushed Fantasy",
            "(Improved) Pulp Fantasy",
            "Surreal Pinup",
            "Impressionist Pinup",
            "Cozy painting",
            "Surreal Watercolor",
            "Gothic Painting",
            "Manuscript illumination",
            "Ancient Art",
            "Field Sketch",
            "Protest Punk Art",
        ],
    ),
    (
        "Dark fantasy",
        [
            "(Improved) Dark Fantasy",
            "Dark Fantasy - Nguni",
            "Dark Fantasy - Polynesian",
            "Dark Fantasy - Mesopotamian",
            "Dark Fantasy - Venda",
            "Dark Fantasy - Andean",
            "Dark Fantasy - Scandinavian",
            "Dark Fantasy - Central Asian",
            "Dark Fantasy - Japanese",
            "Dark Fantasy - Maghrebi",
            "Dark Fantasy - Mapuche",
            "Dark Fantasy - Indonesian",
            "Dark Fantasy - Appalachian",
        ],
    ),
    (
        "Photos and film",
        [
            "(Improved) CGI Animation",
            "Kodachrome",
            "Glamour Photo",
            "IMAX",
            "Firefly",
            "Elizabethan",
        ],
    ),
    (
        "Filmmaker looks",
        [
            "Tim Burton",
            "Guillermo del Toro",
            "Jim Henson",
            "Peter Jackson",
        ],
    ),
]


class Coverage:
    def __init__(self) -> None:
        self.blocks: set[str] = set()
        self.trackers: set[str] = set()
        self.triggers: set[str] = set()
        self.lore: set[str] = set()
        self.video: set[str] = set()


COV = Coverage()


def esc(text: str) -> str:
    return html.escape(text or "", quote=False)


def slug(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")
    return cleaned or "item"


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


def trigger_map(game: dict) -> dict[str, dict]:
    out = {}
    for trigger in game["triggerEvents"]:
        out[trigger["name"].strip()] = trigger
        out[trigger["name"]] = trigger
    return out


def split_gm(game: dict) -> str:
    raw = game["instructions"]
    marker = "Image style prefix"
    if marker in raw:
        return raw.split(marker)[0].strip().rstrip("-").strip()
    return raw.strip()


def split_style(content: str) -> tuple[str, str]:
    """Lore looks label the two halves PREFIX / SUFFIX, with or without a colon."""
    text = content.replace("\r\n", "\n")
    pres = list(re.finditer(r"(?m)^PREFIX:?[ \t]*\n", text))
    sufs = list(re.finditer(r"(?m)^SUFFIX:?[ \t]*\n", text))
    if len(pres) != 1 or len(sufs) != 1 or sufs[0].start() < pres[0].end():
        raise ValueError("style entry has no single PREFIX/SUFFIX split")
    prefix = text[pres[0].end() : sufs[0].start()].strip()
    suffix = text[sufs[0].end() :].strip()
    if not prefix or not suffix:
        raise ValueError("empty prefix or suffix")
    return prefix, suffix


def page_shell(title: str, description: str, body: str, mode: str = "library") -> str:
    if mode == "home":
        nav = ""
        footer = (
            "<p>IW-SLICK is a public copy-paste kit for "
            '<a href="https://infiniteworlds.app">Infinite Worlds</a> world creators, '
            "built by <strong>Sabre</strong>. "
            "To submit something, find Sabre in the Infinite Worlds Discord.</p>"
            "<p>License: GPL-3.0</p>"
        )
    else:
        nav = "\n".join(f'<a href="{href}">{esc(label)}</a>' for href, label in LIB_NAV)
        footer = (
            f"<p>Site by <strong>Sabre</strong>. Scripts by <strong>{esc(CREDITS)}</strong>.</p>"
            "<p>The Script Library 3.29 — copy from these pages into Infinite Worlds.</p>"
            '<p>Shared world: <a href="https://infiniteworlds.app/shared/7zDKHR">'
            "infiniteworlds.app/shared/7zDKHR</a> · "
            '<a href="index.html">IW-SLICK home</a> · '
            '<a href="dont.html">Never mix these</a></p>'
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
        return (
            "Visible to: AI only. The player does not see this notebook. "
            "The story still receives it every turn."
        )
    if vis == "ai_only_boring":
        return (
            "Visible to: AI only, and mark it boring. The story still receives it every turn. "
            "Boring means “this is bookkeeping, not story prose,” so the story should not rewrite it into the scene."
        )
    if vis in ("hidden", "hidden_boring"):
        return (
            "Visible to: hidden. The player does not see this notebook, "
            "and it is not sent to the story as ordinary text."
        )
    return "Visible to: everyone. You and the story can both see this notebook."


def auto_line(item: dict) -> str:
    if item.get("autoUpdate"):
        return (
            "Turn Auto-update on. That lets the story rewrite this notebook after each turn."
        )
    return (
        "Turn Auto-update off. The story will not rewrite this notebook on its own. "
        "The starting text you paste stays until a trigger or you change it."
    )


def space_note(name: str) -> str:
    if name.endswith(" "):
        return (
            " The name ends with a space. Copy that space too. "
            "If you trim it, Infinite Worlds treats it as a different block."
        )
    return ""


def tracker_boxes(boxes: Boxes, item: dict) -> str:
    COV.trackers.add(item["name"])
    bits = [
        boxes.box("Notebook name — create an item and name it exactly this", item["name"]),
        (
            '<div class="ok"><p><strong>Settings on the Items to track screen</strong></p>'
            "<ul><li>Set the type to YAML. YAML is the structured notebook these scripts read. A plain text item will not match the shape they expect.</li>"
            f"<li>{esc(vis_line(item))}</li>"
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
        if str(val).strip():
            bits.append(boxes.box(label, str(val)))
    return "\n".join(bits)


def block_box(boxes: Boxes, block: dict, title: str | None = None) -> str:
    COV.blocks.add(block["name"])
    name = block["name"]
    heading = title or (
        f"Copy this whole text into Extra Instruction Blocks. Name the block exactly: {name}"
    )
    return boxes.box(heading, block["content"])


def trigger_section(boxes: Boxes, trigger: dict) -> str:
    COV.triggers.add(trigger["name"])
    name = trigger["name"]
    cond = trigger["triggerConditions"][0]
    effect = trigger["triggerEffects"][0]
    space = (
        "<p><strong>The name ends with a space.</strong> Copy it exactly from the box.</p>"
        if name.endswith(" ")
        else ""
    )
    once = ""
    if trigger.get("canTriggerMoreThanOnce"):
        once = (
            "<p>Turn on “can trigger more than once.” "
            "That lets the job run again on later turns, whenever a new update row appears. "
            "If you leave it off, the copy happens once and then never again.</p>"
        )
    return "\n".join(
        [
            f"<h3>The trigger</h3>",
            space,
            f"<p>In Triggers, create a new trigger and name it exactly <strong>{esc(name)}</strong>. A trigger is a small automatic job. This one runs after the story writes the Update notebook, and it copies that row onto the real notebook.</p>",
            boxes.box("Trigger name — copy this into the trigger’s name", name),
            once,
            "<p><strong>Condition.</strong> Set the condition type to PawScript. A PawScript condition is a check the game runs before the trigger is allowed to fire. Paste this check. It means “run only when the Update notebook has a row with a name.”</p>",
            boxes.box("PawScript condition — paste this as the check", cond["data"]),
            "<p><strong>Effect.</strong> Set the effect to Run a script. Paste this script as that effect. The script finds the matching person on the real list, replaces that whole row, and then clears the row from the Update notebook.</p>",
            boxes.box("Run a script — paste this as the effect", effect["data"]),
        ]
    )


SCRIPTS = [
    {
        "file": "pd.html",
        "hub": "Photos of people",
        "hub_line": "Choose this when you want the pictures to look like photographs of real people, the way a movie still or a camera photo looks.",
        "title": "Photos of people",
        "block": "Positional Director",
        "frame": "photo",
        "when": (
            "Choose this when you want the pictures to look like photographs: movie stills, "
            "camera language, and realistic people. Every turn still draws a brand new picture. "
            "This script throws away last turn’s written description of the face and the clothes, "
            "so you keep a notebook the new picture can copy from."
        ),
        "avoid": (
            "Turn on this picture script and no other. SFW Director, Lean Director, and the "
            "Unified directors are all trying to do the same photograph job. If two of them "
            "are on, they both write the picture fields and they will disagree."
        ),
        "family": "pd",
        "after": "photo-budget",
    },
    {
        "file": "sfw.html",
        "hub": "Photos, no sex posing",
        "hub_line": "Choose this when you want photographs, and you want the sex-posing instructions left out of the picture rules.",
        "title": "Photos, no sex posing",
        "block": "SFW Director (WF?)",
        "frame": "photo",
        "when": (
            "Choose this when you want photographs, and you do not want the picture script "
            "to include sex-posing instructions. Every turn still draws a new picture, and "
            "this script still needs appearance notebooks, because it does not reuse last "
            "turn’s written description of the face and the clothes."
        ),
        "avoid": (
            "Turn on this picture script and no other. It is the photograph script with the "
            "sex posing left out. Positional Director is the same job with that posing included, "
            "so leave Positional Director off."
        ),
        "family": "pd",
        "after": "photo-budget-sfw",
    },
    {
        "file": "explicit.html",
        "hub": "Photos with size tiers",
        "hub_line": "Choose this when the pictures are photographs and the game needs named body-size steps, such as cup sizes written out on purpose.",
        "title": "Photos with size tiers",
        "block": "Unified Explicit Director",
        "frame": "mixed",
        "when": (
            "Choose this when the pictures are photographs and your game needs the body "
            "sizes named in steps, for example a specific cup size written into the picture. "
            "You still keep appearance notebooks, because a new picture is drawn every turn "
            "and this script does not reuse last turn’s written description."
        ),
        "avoid": (
            "Turn on this picture script and no other. Positional Director, Principled, and "
            "Lean are the same picture job with different amounts of body-size language. "
            "Two of them will argue about the same picture."
        ),
        "family": "pd",
        "after": "artist-fill",
    },
    {
        "file": "principled.html",
        "hub": "Richer photos, no size tiers",
        "hub_line": "Choose this when you want a fuller photograph, with more detail, and you do not want the script to assign body-size steps.",
        "title": "Richer photos, no size tiers",
        "block": "Unified Principled Director (WF)",
        "frame": "mixed",
        "when": (
            "Choose this when you want a fuller set of photograph rules, and you do not "
            "want the script to assign body-size steps. You still keep appearance notebooks. "
            "The script can be filled as a film look or as a painting look. You pick one side "
            "when you fill the blanks."
        ),
        "avoid": (
            "Turn on this picture script and no other. Unified Explicit is the version that "
            "names body-size steps. Positional Director is the full photograph script. "
            "Leave both of those off."
        ),
        "family": "pd",
        "after": "film-or-art",
    },
    {
        "file": "unified-lean.html",
        "hub": "Shorter unified photos",
        "hub_line": "Choose this when you want the same unified photograph rules, but in a shorter sheet that costs less to send every turn.",
        "title": "Shorter unified photos",
        "block": "Unified Lean Director (WF)",
        "frame": "mixed",
        "when": (
            "Choose this when you want the unified photograph rules, but you want the "
            "shorter sheet. A shorter sheet is sent every turn, so it costs less, and it "
            "leaves out some of the longer description instructions. You still keep "
            "appearance notebooks, because the picture is drawn new every turn."
        ),
        "avoid": (
            "Turn on this picture script and no other. Lean Director is a different short "
            "photograph sheet. Unified Explicit is the long version with body-size steps. "
            "Leave both of those off."
        ),
        "family": "pd",
        "after": "film-or-art",
    },
    {
        "file": "lean.html",
        "hub": "Cheap photos",
        "hub_line": "Choose this when you still want photographs, and you want the shortest rule sheet in the library.",
        "title": "Cheap photos",
        "block": "Lean Director (WF)",
        "frame": "photo",
        "when": (
            "Choose this when you still want photographs, but you want the shortest rule "
            "sheet. It is the same kind of job as Positional Director, with less camera "
            "language and fewer body rules. You still keep appearance notebooks, because "
            "a new picture is drawn every turn and the written description is not reused."
        ),
        "avoid": (
            "Turn on this picture script and no other. Positional Director is the long "
            "photograph sheet. Unified Lean is the other short sheet. Leave both of those off."
        ),
        "family": "pd",
        "after": "photo-budget",
    },
    {
        "file": "artist.html",
        "hub": "A painting",
        "hub_line": "Choose this when you want one still picture that looks painted or drawn, such as oil, watercolor, or illustration, rather than a camera photo.",
        "title": "A painting",
        "block": "Artist",
        "frame": "paint",
        "when": (
            "Choose this when you want the pictures to look painted or drawn: oil, "
            "watercolor, print, or illustration. It is one still picture, not a comic page. "
            "You keep appearance notebooks, because a new picture is drawn every turn and "
            "this script copies the face from those notebooks."
        ),
        "avoid": (
            "Turn on this picture script and no other. If you want comic pages with panels "
            "and speech bubbles, that is the manga script, not this one."
        ),
        "family": "pd",
        "after": "artist-fill",
    },
    {
        "file": "manga.html",
        "hub": "Manga pages",
        "hub_line": "Choose this when you want the picture to be a comic page, with panels and speech bubbles, instead of one still image.",
        "title": "Manga pages",
        "block": "Manga/Storyboard",
        "frame": "manga",
        "when": (
            "Choose this when you want comic pages: several panels, and speech bubbles. "
            "You keep appearance notebooks. The painting script is one still picture. "
            "This one is a page of panels."
        ),
        "avoid": (
            "Turn on this picture script and no other. The painting script draws one still "
            "picture. It will fight these panel rules if you leave it on."
        ),
        "family": "pd",
        "after": "manga-fill",
    },
    {
        "file": "bob-ross.html",
        "hub": "A crowded scene",
        "hub_line": "Choose this when the picture is a crowd arranged in a space, rather than a close-up of one or two people.",
        "title": "A crowded scene",
        "block": "Bob Ross script (WF)",
        "frame": "mixed",
        "when": (
            "Choose this when the shot is a crowd arranged in a space, not a close-up of "
            "one or two people talking. You use the same Player Appearance and NPC Appearance "
            "notebooks as the photograph scripts. There is no separate Bob Ross notebook."
        ),
        "avoid": (
            "Turn on this picture script and no other. Use Player Appearance and one NPC "
            "Appearance notebook. An old library used different notebooks whose names said "
            "“for Bob Ross.” Those notebooks are not in this version."
        ),
        "family": "pd",
        "after": "artist-fill",
    },
    {
        "file": "single.html",
        "hub": "One person the game remembers",
        "hub_line": "Choose this when there is one named person, and you want their face to stay steady from picture to picture.",
        "title": "One person the game remembers",
        "block": "Wrangler (WF)",
        "frame": "mixed",
        "rename": (
            "This block used to be called Vanilla IW Wrangler (Single subject). "
            "The name to paste now is Wrangler (WF). If you still have the old name "
            "in your game, replace that block with this one. Do not leave both turned on."
        ),
        "when": (
            "Choose this when there is one named person and you want the face to stay "
            "steady. A new picture is still drawn every turn. What stays steady is the "
            "written description, as long as you spell the name the same way. Create no "
            "appearance notebooks. A notebook would throw that saved description away."
        ),
        "avoid": (
            "Turn on this picture script and no other. Bareback Wrangler is the same "
            "one-person job with a shorter sheet. Leave it off. Also leave Player Appearance "
            "and NPC Appearance off. Those notebooks are for the scripts that rewrite the "
            "description every turn. On this script they stop the face from staying put."
        ),
        "family": "none",
        "after": "remembered-face",
    },
    {
        "file": "bareback.html",
        "hub": "One person, lean language",
        "hub_line": "Choose this when there is one named person, you want the face to stay steady, and you want a shorter rule sheet than Wrangler.",
        "title": "One person, lean language",
        "block": "Bareback Wrangler (WF)",
        "frame": "mixed",
        "when": (
            "Choose this when there is one named person, you want the face to stay steady, "
            "and you want shorter picture rules than Wrangler. Create no appearance notebooks. "
            "The saved description is what keeps the face steady, and a notebook fights that."
        ),
        "avoid": (
            "Turn on this picture script and no other. Wrangler (WF) is the longer version "
            "of this same one-person job. Leave it off, and do not create appearance notebooks."
        ),
        "family": "none",
        "after": "remembered-face",
    },
]

SCRIPT_BY_FILE = {s["file"]: s for s in SCRIPTS}

LIB_GROUPS = [
    (
        "Photographs — pick one",
        ["pd.html", "sfw.html", "explicit.html", "principled.html", "unified-lean.html", "lean.html"],
    ),
    ("Painted or comic — pick one", ["artist.html", "manga.html"]),
    ("A crowded scene", ["bob-ross.html"]),
    ("One remembered face — pick one", ["single.html", "bareback.html"]),
]

AFTER = {
    "photo-budget": (
        "<ul>"
        "<li>Search the text you pasted for notes wrapped in <code>&lt;# … #&gt;</code>. The game skips everything inside those wraps. That is how optional instructions stay off until you want them.</li>"
        "<li>Find the line with square brackets for budget, Hollywood or indie, and genre. Write your choices inside the brackets. Then delete the <code>&lt;#</code> and <code>#&gt;</code> around that line so the game can read it.</li>"
        "<li>Find the mood line. Write three to five mood words. Then delete the wrap around that line too.</li>"
        "<li>Sex pose packs and fight pose packs are also wrapped. Delete the wrap only if your game actually shows that kind of scene. If you open a pack you do not use, those instructions are sent every turn and they cost extra.</li>"
        "</ul>"
    ),
    "photo-budget-sfw": (
        "<ul>"
        "<li>Search the text you pasted for notes wrapped in <code>&lt;# … #&gt;</code>. The game skips everything inside those wraps until you delete the wrap.</li>"
        "<li>Find the line with square brackets for budget, Hollywood or indie, and genre. Write your choices inside the brackets. Then delete the wrap so the game can read that line.</li>"
        "<li>Find the mood line. Write three to five mood words. Then delete the wrap around that line too.</li>"
        "<li>There is a fight pose pack. Delete its wrap only if your game shows fights. This look has no sex-posing pack, because the sex posing was left out on purpose.</li>"
        "</ul>"
    ),
    "artist-fill": (
        "<ul>"
        "<li>Search the text you pasted for notes wrapped in <code>&lt;# … #&gt;</code>. The game skips those notes until you delete the wrap.</li>"
        "<li>Find the line with square brackets for period, region, and the kind of artist. Write your choices. Then delete the wrap so the game can read that line.</li>"
        "<li>Find the mood line. Write three to five mood words. Then delete the wrap around that line too.</li>"
        "<li>Sex pose packs and fight pose packs stay wrapped unless your game actually shows those scenes. Opening one sends it every turn.</li>"
        "</ul>"
    ),
    "film-or-art": (
        "<ul>"
        "<li>Search the text you pasted for notes wrapped in <code>&lt;# … #&gt;</code>. The game skips those notes until you delete the wrap.</li>"
        "<li>There is a slot that says film or painting. Keep the side you want, delete the other side, and then delete the wrap so the game can read your choice.</li>"
        "<li>Find the line with square brackets for period, region, and the kind of artist. Write your choices, then delete the wrap.</li>"
        "<li>Find the mood line. Write three to five mood words, then delete the wrap.</li>"
        "<li>Sex pose packs and fight pose packs stay wrapped unless your game actually shows those scenes.</li>"
        "</ul>"
    ),
    "manga-fill": (
        "<ul>"
        "<li>Search the text you pasted for notes wrapped in <code>&lt;# … #&gt;</code>. The game skips those notes until you delete the wrap.</li>"
        "<li>Find the tradition line. Fill in the time, the region, and the comic tradition, such as Shonen or Seinen. Then delete the wrap so the game can read it.</li>"
        "<li>Find the mood line. Write three to five mood words, then delete the wrap.</li>"
        "<li>Sex pose packs and fight pose packs stay wrapped unless your game actually shows those scenes.</li>"
        "</ul>"
    ),
    "remembered-face": (
        "<ul>"
        "<li>Spell the person’s name the same way every turn. The saved description is tied to that exact spelling. A new spelling looks like a new person, so the face changes.</li>"
        "<li>Leave the hidden note that starts “If using appearance tracked items” wrapped. That note is what would throw away the saved description. Do not delete its wrap, and do not create appearance notebooks.</li>"
        "<li>There is a slot that says film or painting. Keep the side you want, delete the other side, and then delete the wrap.</li>"
        "<li>Find the line with square brackets for period, region, and the kind of artist. Write your choices, then delete the wrap.</li>"
        "<li>Find the mood line. Write three to five mood words, then delete the wrap.</li>"
        "<li>The first time this person is drawn, name the face, the hair, and the colors of the clothes. Later turns reuse those words. A vague first description gets redrawn as a different person even when the name matches.</li>"
        "<li>Sex pose packs and fight pose packs stay wrapped unless your game actually shows those scenes.</li>"
        "</ul>"
    ),
}


def exact_name(script: dict, blocks: dict) -> str:
    return blocks[script["block"]]["name"]


def look_card(script: dict, blocks: dict) -> str:
    exact = exact_name(script, blocks)
    face = (
        "Every turn draws a new picture. This look reuses last turn’s written description when you spell the name the same way, so you do not create an appearance notebook."
        if script["family"] == "none"
        else "Every turn draws a new picture. This look throws away last turn’s written description, so you keep notebooks the new picture can copy."
    )
    return (
        f'<a class="card" href="{script["file"]}">'
        f"<strong>{esc(script['hub'])}</strong>"
        f'<p class="chip">{esc(exact)}</p>'
        f"<p>{esc(script['hub_line'])}</p>"
        f'<p class="face">{esc(face)}</p>'
        f'<span class="btn">OPEN THIS</span></a>'
    )


def frame_keep(kind: str) -> str:
    extra = (
        "<li>If your game does not show sex in the pictures, delete the phrases about sexually stylized art, erotic styling, and genitalia. Those words are instructions to the picture model. Leaving them in will push the pictures that way.</li>"
        "<li>A label such as <code>&lt;#TONE#&gt;</code> is a comment. The game ignores the label. The paragraph after the label is live until you delete that paragraph.</li>"
    )
    if kind == "photo":
        body = (
            "<li>Keep the lines that sound like photographs or computer graphics. Those are the look you picked.</li>"
            "<li>Delete the paragraph that is only for manga or comics. That paragraph would pull the photograph toward a comic page.</li>"
        )
    elif kind == "paint":
        body = (
            "<li>Keep the words about paint, brushes, and illustration.</li>"
            "<li>Delete camera and film words, and delete Unreal Engine lines, unless you truly want the painting to look like a game screenshot.</li>"
            "<li>Delete the paragraph that is only for manga or comics.</li>"
        )
    elif kind == "manga":
        body = (
            "<li>Keep the manga and comic paragraph. That is the page layout you picked.</li>"
            "<li>Delete Unreal Engine lines. Those push the comic toward a game screenshot.</li>"
        )
    else:
        body = (
            "<li>This look can be photographs or a painting. Keep the paragraphs that match the side you filled in the picture rules. Delete the other side, or both looks will be sent at once.</li>"
            "<li>Delete the manga or comic paragraph unless you actually want comic pages. If you want comic pages, the manga look is the better script.</li>"
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
            '<div class="ok"><p><strong>Create no appearance notebooks.</strong></p>'
            "<p>Every turn, Infinite Worlds draws a brand new picture. It does not reuse the last picture. "
            "What this look can reuse is the written description of the person’s face and clothes, "
            "and only when you spell their name the same way every time. That saved description is "
            "what people mean by the picture cache.</p>"
            "<p>Leave the hidden note that starts “If using appearance tracked items” wrapped. "
            "Opening it tells the game to throw the saved description away. The first description "
            "has to name the face, the hair, and the colors of the clothes. If that first line is "
            "vague, the new picture invents a new person even though the name matches. "
            "If someone else is in the scene, put them in the setting. This script is built for one named person.</p></div>"
        )
    player = trackers["Player Appearance"]
    small = trackers["NPC Appearance small cast"]
    large = trackers["NPC Appearance (large cast)"]
    return (
        '<div class="panel"><p><strong>Why these notebooks</strong></p>'
        "<p>Every turn, Infinite Worlds draws a brand new picture. It does not keep the last picture. "
        "This look also throws away last turn’s written description of the face and the clothes. "
        "It does that by putting the turn number on the subject line and by marking the clothes as changed. "
        "The notebooks are the written description the new picture copies. A notebook here means an "
        "Items to track entry. Without it, the face drifts, because there is nothing stable to copy.</p>"
        "<p>If your cast is small, add a row when someone speaks or is physically in the scene. "
        "If your cast is large, add a row only when the Relationship Tracker marks that person "
        "<code>significant: true</code>. That word is a yes-or-no flag on their relationship row. "
        "A large cast therefore also needs the Relationship set on the "
        '<a href="notebooks.html">Notebooks</a> page. If that set is missing, the flag never gets set, '
        "and the appearance list stays empty.</p></div>"
        "<p>Always copy the player notebook. Then copy either the few-people list or the many-people list. "
        "Copy one of those NPC lists, not both. Two lists for the same people will disagree about how they look.</p>"
        "<p>Relationship, intimacy, and the NPC appearance update are a separate set. "
        "Open the <a href=\"notebooks.html\">Notebooks</a> page after the pictures are working, and copy that set there.</p>"
        f"<h3>Always — player</h3>\n{tracker_boxes(boxes, player)}\n"
        '<div class="or-split">'
        "<section><h3>A few people — copy this notebook, and skip the large list</h3>\n"
        f"{tracker_boxes(boxes, small)}</section>"
        "<section><h3>Many people — copy this notebook, and skip the small list</h3>\n"
        f"{tracker_boxes(boxes, large)}</section>"
        "</div>"
    )


def done_box() -> str:
    return """
<div class="ok">
<p><strong>Pictures are done</strong> when those four steps are in your game. You can stop here and play. If you want more, these pages are optional:</p>
<p><a class="btn" href="writing.html">STORY VOICE</a>
<a class="btn" href="extras.html">ADD-ONS</a>
<a class="btn" href="bodies.html">BODIES</a>
<a class="btn" href="creatures.html">CREATURES</a>
<a class="btn" href="notebooks.html">NOTEBOOKS</a>
<a class="btn" href="styles.html">STYLES</a></p>
</div>
"""


def write_script_page(script: dict, blocks: dict, trackers: dict, game: dict) -> None:
    boxes = Boxes()
    block = blocks[script["block"]]
    exact = block["name"]
    space = (
        "<p><strong>The name ends with a space.</strong> When you paste the name, include that last space. "
        "If you trim it off, Infinite Worlds treats it as a different block, and the rules you copied will not be the ones the page is talking about.</p>"
        if exact.endswith(" ")
        else ""
    )
    rename = f"<p>{esc(script['rename'])}</p>" if script.get("rename") else ""
    body = f"""
<p class="bubble">STAY ON THIS PAGE</p>
<h1>{esc(script["title"])}</h1>
<p class="chip">{esc(exact)}</p>
{rename}
<p class="lede">{esc(script["when"])}</p>
<nav class="toc">
<a href="#step1">1. Picture rules</a>
<a href="#step2">2. Notebooks</a>
<a href="#step3">3. Fill blanks</a>
<a href="#step4">4. Image style</a>
</nav>
<section class="step" id="step1">
<h2>Step 1 — Extra Instruction Blocks</h2>
<p>In your world, open Extra Instruction Blocks. That is the list of extra rule sheets the game sends every turn. Create one block, paste the box below into it, and name the block exactly as the box says.</p>
<div class="warn"><p>{esc(script["avoid"])}</p></div>
{space}
{block_box(boxes, block)}
</section>
<section class="step" id="step2">
<h2>Step 2 — Items to track</h2>
<p>Items to track are the notebooks the game keeps between turns. This step tells you which notebooks this look needs.</p>
{notebook_step(script, trackers, boxes)}
</section>
<section class="step" id="step3">
<h2>Step 3 — Fill blanks on what you pasted</h2>
<div class="panel">
<p>Some notes in the script are wrapped in <code>&lt;# … #&gt;</code>. The game skips everything between those marks. The author hid optional packs there — sex scenes, fights, and long clothing rules — so you do not pay for them every turn until you want them. When you want a pack, fill any square brackets inside it, then delete the <code>&lt;#</code> and the <code>#&gt;</code>. When this page tells you to leave a wrap closed, leave it closed.</p>
{AFTER[script["after"]]}
</div>
</section>
<section class="step" id="step4">
<h2>Step 4 — Image style</h2>
<p>These four boxes are a blank template for the words that wrap the picture. Paste them into the Image style prefix and suffix fields, then keep or delete paragraphs so they match this look.</p>
<p>Those fields go to the picture model only. They do not go to the story writer. That is why you should not paste them into the story Description field. Description is how the story talks. Image style is how the picture looks.</p>
<p>A named style from the Styles page and this blank template are two different wrappers. Use one of them. If you paste both, the picture model receives two looks at once and they fight.</p>
<p>If you would rather start from a finished look, open <a href="styles.html">Styles</a>, pick one, and copy its prefix and its suffix instead of these four boxes.</p>
{frame_keep(script["frame"])}
{frame_boxes(boxes, game)}
</section>
{done_box()}
"""
    (DOCS / script["file"]).write_text(
        page_shell(
            f"{script['title']} — The Script Library",
            script["hub_line"],
            body,
        ),
        encoding="utf-8",
    )


def later_links() -> str:
    return """
<p class="quiet">Once the pictures are in your game, you can add:
<a href="writing.html">Story voice</a> ·
<a href="extras.html">Add-ons</a> ·
<a href="bodies.html">Bodies</a> ·
<a href="creatures.html">Creatures</a> ·
<a href="notebooks.html">Notebooks</a> ·
<a href="styles.html">Styles</a> ·
<a href="video.html">Video</a> ·
<a href="dont.html">Never mix these</a></p>
"""


def picker_body(blocks: dict, intro: str) -> str:
    groups = []
    for heading, files in LIB_GROUPS:
        cards = "".join(look_card(SCRIPT_BY_FILE[f], blocks) for f in files)
        groups.append(f'<div class="group"><h2>{esc(heading)}</h2><div class="grid">{cards}</div></div>')
    return f"""
<p class="bubble">THE SCRIPT LIBRARY 3.29</p>
<h1>Pick one look.</h1>
<p class="lede">{esc(intro)}</p>
<div class="panel">
<p><strong>Why you pick one look</strong></p>
<p>Every turn, Infinite Worlds draws a brand new picture. It does not reuse the last picture. What it can reuse is the written description of a person’s face and clothes, and only when you spell their name the same way every time. If that description is vague, the new picture invents a new face even though the name matches. That saved description is the picture cache.</p>
<p>Wrangler and Bareback keep that saved description. That is why their cards say you do not create an appearance notebook. Every other look throws the saved description away on purpose, so you keep notebooks the new picture can copy.</p>
<p>Turn on one picture script. Every block you leave enabled is sent on every turn, which costs more, and these scripts all write the same picture fields. If two of them are on, they contradict each other and the picture comes out muddled.</p>
</div>
<p class="ok">Stay on that look’s page until the pictures are in your game and they look right. You can come back later for story voice, notebooks, or a named picture style.</p>
{"".join(groups)}
{later_links()}
"""


def write_index() -> None:
    body = f"""
<p class="bubble">IW-SLICK</p>
<h1>Copy-paste kit.</h1>
<p class="lede">This is a public kit for people who build worlds in Infinite Worlds. Sabre built the site. The community writes the pieces. More pieces will land here later.</p>
<h2>Contributions</h2>
<div class="grid">
<a class="card" href="library.html">
<strong>The Script Library 3.29</strong>
<p>Open a page, copy the box, and paste it into your Infinite Worlds world. The pages cover picture scripts, how the story talks, notebooks the game keeps between turns, and named picture styles.</p>
<p>The scripts were written by {esc(CREDITS)}. Sabre built this copy-paste site.</p>
<span class="btn">OPEN THIS</span>
</a>
<div class="card soon">
<strong>More later</strong>
<p>Other contributions will show up on this board. This home is for the whole kit, not only the Script Library.</p>
<p>To submit something, find Sabre in the Infinite Worlds Discord.</p>
</div>
</div>
"""
    (DOCS / "index.html").write_text(
        page_shell(
            "IW-SLICK — Infinite Worlds copy-paste kit",
            "IW-SLICK is a public copy-paste kit for Infinite Worlds. The Script Library 3.29 is the first contribution.",
            body,
            mode="home",
        ),
        encoding="utf-8",
    )


def write_library(blocks: dict) -> None:
    intro = (
        "Open one picture look and stay on that page until the pictures in your game look right. "
        "The chip on the card is the exact name of the Extra Instruction Block, which is the extra rule sheet you paste. "
        "Copy the whole page. Turn on one look only."
    )
    (DOCS / "library.html").write_text(
        page_shell(
            "The Script Library 3.29 — pick a look",
            "Pick one picture script by its exact name, and finish the pictures on that page before you open another.",
            picker_body(blocks, intro),
        ),
        encoding="utf-8",
    )


def write_start(blocks: dict) -> None:
    intro = (
        "You are in The Script Library 3.29. Open one look below and stay on that page until the pictures in your game look right. "
        "The chip on the card is the exact name of the Extra Instruction Block you will paste."
    )
    (DOCS / "start.html").write_text(
        page_shell(
            "The Script Library 3.29 — pick a look",
            "Open one picture look and finish the pictures on that page.",
            picker_body(blocks, intro),
        ),
        encoding="utf-8",
    )


def write_dual() -> None:
    body = """
<p class="bubble">MOVED</p>
<h1>Two people moved.</h1>
<p class="lede">This library does not have a two-person Wrangler. Wrangler and Bareback are built for one named person. When two named people need to appear in a photograph, use a photograph script. When the shot is a crowd, use Bob Ross.</p>
<div class="grid">
<a class="card" href="pd.html">
<strong>Photos of people</strong>
<p class="chip">Positional Director</p>
<p>Use this when two named people should appear together in a photograph.</p>
<span class="btn">OPEN THIS</span>
</a>
<a class="card" href="lean.html">
<strong>Cheap photos</strong>
<p class="chip">Lean Director (WF)</p>
<p>Use this when you want the same photograph job on a shorter rule sheet.</p>
<span class="btn">OPEN THIS</span>
</a>
<a class="card" href="bob-ross.html">
<strong>A crowded scene</strong>
<p class="chip">Bob Ross script (WF)</p>
<p>Use this when the picture is a crowd arranged in a space, rather than a close-up of two people.</p>
<span class="btn">OPEN THIS</span>
</a>
</div>
<p><a class="btn" href="library.html">ALL LOOKS</a></p>
"""
    (DOCS / "dual.html").write_text(
        page_shell(
            "Two people moved — The Script Library",
            "There is no two-person Wrangler. Use Positional Director, Lean Director, or Bob Ross.",
            body,
        ),
        encoding="utf-8",
    )


def write_writing(game: dict, blocks: dict, trackers: dict) -> None:
    boxes = Boxes()
    story = blocks["SecretInfo + Storymaster"]
    reader = trackers["Reader Profile"]
    meta = trackers["Story Metadata"]
    body = f"""
<p class="bubble">STORY VOICE</p>
<h1>How the story talks.</h1>
<p class="lede">Do this once for your whole game. You do not paste it again for each picture look. Paste the boxes in the same order as the fields on the Infinite Worlds screen, so each box lands in the field it belongs to.</p>
<div class="panel">
<p><strong>Why these fields are separate</strong></p>
<p>Infinite Worlds splits the story into two jobs. The Simulation Engine is the hidden plan: what happens next, and what the characters know. The Narrative Author is the prose the player reads. If those jobs share one box, the hidden plan leaks into the story the player sees.</p>
<p>Storymaster is the block that decides what happens next. Description is the field that decides how that prose sounds. Reader Profile is a notebook about the human at the keyboard, so pacing can follow how they play. It is not the player character’s character sheet. Story Metadata is a notebook of the story’s genre and appeal. Change it only when the story itself changes for good. One wild turn should not rewrite the genre.</p>
</div>
<nav class="toc">
<a href="#w1">1. Main Instructions</a>
<a href="#w2">2. Storymaster</a>
<a href="#w3">3. Author style</a>
<a href="#w4">4. Evaluation</a>
<a href="#w5">5. Description</a>
<a href="#w6">6. Summarization</a>
<a href="#w7">7. Reader Profile</a>
<a href="#w8">8. Story Metadata</a>
</nav>
<section class="step" id="w1">
<h2>Step 1 — Main Instructions</h2>
<p>Paste this into Main Instructions, the big instruction box at the top of the world. It tells the story to read the Reader Profile and Story Metadata notebooks. Those notebooks are steps 7 and 8 on this page. Copy them too. If you skip them, those lines in Main Instructions have nothing to read.</p>
{boxes.box("Main Instructions — Split Game Master", split_gm(game))}
</section>
<section class="step" id="w2">
<h2>Step 2 — Extra Instruction Blocks (Storymaster)</h2>
<p>Create an Extra Instruction Block and name it exactly <strong>{esc(story["name"])}</strong>. An Extra Instruction Block is an extra rule sheet the game sends every turn. Inside the paste, a section is wrapped in <code>&lt;# … #&gt;</code>. The game skips everything between those marks until you delete the wrap. Fill the square brackets first: the genres, what those genres owe the reader, this story’s appeal, what is new about it, the tone, the themes, the conflicts, and the turn counts. Then delete the <code>&lt;#</code> and <code>#&gt;</code> so the game can read that section.</p>
{block_box(boxes, story)}
</section>
<section class="step" id="w3">
<h2>Step 3 — Author style</h2>
<p>Paste this into the Author style field. Replace <code>[Author Style]</code> with a short description of how the sentences should sound, such as spare, warm, or formal. Leave the words “Written by Storymaster.” in place. Those words tell the story which voice is speaking.</p>
{boxes.box("Author style", game["authorStyle"])}
</section>
<section class="step" id="w4">
<h2>Step 4 — Evaluation</h2>
<p>Paste this into the Evaluation field. Evaluation is the private check the game runs on the turn before the player reads it. It is not a paragraph the player sees.</p>
{boxes.box("Evaluation", game["evaluationRequest"])}
</section>
<section class="step" id="w5">
<h2>Step 5 — Description</h2>
<p>Paste this into the Description field only if that field is still about how the story sounds. Description is the voice of the prose the player reads. Picture style belongs in Image style, which only the picture model reads. If you already wrote picture instructions in Description, leave them. Pasting this box would replace those instructions.</p>
{boxes.box("Description", game["descriptionRequest"])}
</section>
<section class="step" id="w6">
<h2>Step 6 — Summarization</h2>
<p>Paste this into the Summarization field. That field tells the game how to shrink older turns so the story can remember them without rereading the whole chat.</p>
{boxes.box("Summarization", game["summaryRequest"])}
</section>
<section class="step" id="w7">
<h2>Step 7 — Reader Profile notebook</h2>
<p>Create this notebook under Items to track. A notebook is a saved note the game keeps between turns. This one describes the human at the keyboard, so the story can match its pace to how you actually play. It is not the player character’s sheet. The story fills it in over many turns. You do not have to write the profile yourself before you start.</p>
{tracker_boxes(boxes, reader)}
</section>
<section class="step" id="w8">
<h2>Step 8 — Story Metadata notebook</h2>
<p>Create this notebook under Items to track. It stores the story’s genre and what the story is trying to deliver. Leave it alone during ordinary play. Change it only when the story itself changes for good, such as a new act with a different promise to the reader. One strange turn should not rewrite it.</p>
{tracker_boxes(boxes, meta)}
</section>
{later_links()}
"""
    (DOCS / "writing.html").write_text(
        page_shell(
            "Story voice — The Script Library",
            "Split Game Master, Storymaster, Author style, Evaluation, Description, Summarization, Reader Profile, Story Metadata.",
            body,
        ),
        encoding="utf-8",
    )


EXTRAS = [
    (
        "Characterization",
        "Paste this when you want people to keep acting like themselves from turn to turn. It is a writing rule, not a picture rule.",
    ),
    (
        "Pacing",
        "Paste this when scenes rush to the ending, or stall with nothing happening. It tells the story how fast a scene should move.",
    ),
    (
        "Sexual Content",
        "Paste this when your game includes sex scenes and you want rules for how those scenes are written. Skip it if your game does not have those scenes, because every block you leave on is sent every turn.",
    ),
    (
        "Period Knowledge",
        "Paste this when the story is set in a specific time and people should know only what that time would know. After you paste, find [time period] and write the period there.",
    ),
    (
        "Narrative Craft",
        "Paste this when you want extra rules for how the prose is built: scene shape, what to show, and what to leave implied.",
    ),
    (
        "Lion Bugfixes",
        "Paste this when you play on a Lion-family model. Those models invent secret plots the scene never earned, and they pile on jargon. This block keeps secrets out of the hidden notes and asks for ordinary language.",
    ),
    (
        "Leopard Bugfixes",
        "Paste this when you play on a Leopard model. Those models go melodramatic and raise the stakes even when you might already win. This block leaves a middle road and lets you win.",
    ),
    (
        "Caracal Bugfixes",
        "Paste this when you play on Caracal. Caracal writes too short, and it offers the same choice three ways. This block asks for a long scene and three choices that are actually different.",
    ),
    (
        "Dolphin Bugfixes",
        "Paste this when you play on Dolphin. Dolphin rushes relationships and ends a scene before you get to act. This block keeps the slow burn and offers the choices first.",
    ),
    (
        "Wyvern Word Caps",
        "Paste this only when the picture model is Wyvern. Wyvern corrupts a long picture prompt that was written for Manticore, so this block is the shorter word cap. Leave it off when the picture model is Manticore, or you will cut a prompt that Manticore can still read.",
    ),
    (
        "Cover Image script",
        "This is for the store cover, not the picture the game draws every turn. Copy the block, give it to an AI along with your game title and blurb, then paste the result into the cover appearance field. Leave art-style words out of that result. Style belongs in Image style, which is the field the picture model reads.",
    ),
]


def write_extras(blocks: dict) -> None:
    boxes = Boxes()
    bits = [
        """
<p class="bubble">ADD-ONS</p>
<h1>Optional extras.</h1>
<p class="lede">Use these after the pictures in your game look right. Each extra is its own Extra Instruction Block, which is an extra rule sheet the game sends every turn. Copy only the ones your game needs. Every block you leave turned on is sent every turn, so unused blocks cost extra for no benefit.</p>
<p class="quiet"><a href="extras.html">Extra writing</a> · <a href="bodies.html">Bodies</a> · <a href="creatures.html">Creatures</a> · <a href="notebooks.html">Notebooks</a> · <a href="video.html">Video</a></p>
<div class="warn"><p><strong>Lion, Leopard, Caracal, and Dolphin.</strong> After you paste one of those bugfix blocks, open the block and set it to “Applies to certain models.” Then tick only the models named under that block on this page. In Infinite Worlds settings, turn on “AI-specific extra instructions.” If that switch is off, the block is sent to every model, including ones it was not written for.</p></div>
"""
    ]
    for name, blurb in EXTRAS:
        block = blocks[name]
        exact = block["name"]
        bits.append(f"<h2>{esc(exact.strip())}</h2>")
        bits.append(f"<p>{esc(blurb)}{esc(space_note(exact))}</p>")
        bits.append(
            f"<p>Create an Extra Instruction Block and name it exactly <strong>{esc(exact)}</strong>. "
            "Then paste the box below into that block.</p>"
        )
        ticks = MODEL_TICKS.get(exact.strip())
        if ticks:
            bits.append(
                '<div class="panel"><p><strong>Tick these models</strong></p>'
                "<p>On this block, choose “Applies to certain models” and turn on only these names. "
                f"Leave the other models off. {esc(ticks)}</p></div>"
            )
        bits.append(block_box(boxes, block))
    (DOCS / "extras.html").write_text(
        page_shell(
            "Add-ons — The Script Library",
            "Story extras, model bugfixes, Wyvern word caps, and the cover-image helper.",
            "".join(bits),
        ),
        encoding="utf-8",
    )


BODIES = [
    (
        "Male Description (alternate for baseline female description in PD/Manga)",
        "Paste this when you want male body language in the appearance section of the picture script you already copied. It can sit beside the female lines if you weave the shared parts together so they do not repeat. It is a patch inside the picture script, not a second picture script.",
    ),
    (
        "Futanari description block",
        "Paste this when you want those body lines instead of the female body lines. It replaces that section of the picture script. Do not leave the old female lines in the same section, or the picture model receives two body plans.",
    ),
    (
        "Agender/Genderless description block",
        "Paste this when you want a body described without gendered lines, as a columnar figure. It replaces the gendered body lines in the picture script. Remove the gendered lines it is standing in for.",
    ),
    (
        "Hypermasc/Hypertrophy module",
        "Paste this when you want huge muscle that can grow over the story. It reads a growth log before it describes the body, so the log has to exist or the description has nothing to follow. Paste this one module, not several body modules at once.",
    ),
]


def write_bodies(blocks: dict) -> None:
    boxes = Boxes()
    bits = [
        """
<p class="bubble">BODY ADD-ONS</p>
<h1>Bodies.</h1>
<p class="lede">These are patches you drop into the picture script you already pasted. They are not a second picture script. Paste one of them. If you paste two, they both describe the same body and the picture comes out muddled.</p>
<div class="panel"><p>Each box tells you which section of the picture script it belongs in. Read that opening, then paste the body lines into that section. Male description can sit beside female lines if you weave the shared parts together so they are not repeated. Futanari replaces the female body lines, so you remove the lines it replaces. Agender replaces gendered body lines the same way. Hypertrophy adds huge muscle, and it reads a growth log first, so that log has to be in the game before the description can follow it.</p></div>
<p class="quiet"><a href="extras.html">Extra writing</a> · <a href="bodies.html">Bodies</a> · <a href="creatures.html">Creatures</a></p>
"""
    ]
    for name, blurb in BODIES:
        block = blocks[name]
        bits.append(f"<h2>{esc(block['name'])}</h2>")
        bits.append(f"<p>{esc(blurb)}{esc(space_note(block['name']))}</p>")
        bits.append(block_box(boxes, block))
    (DOCS / "bodies.html").write_text(
        page_shell(
            "Body add-ons — The Script Library",
            "Male, futa, agender, and hypertrophy body blocks. Paste one.",
            "".join(bits),
        ),
        encoding="utf-8",
    )


def emit_blocks(boxes: Boxes, blocks: dict, names: list[str], blurbs: dict[str, str]) -> str:
    bits = []
    for name in names:
        block = blocks[name]
        bits.append(f"<h3>{esc(block['name'])}</h3>")
        blurb = blurbs.get(name, "")
        if blurb:
            bits.append(f"<p>{esc(blurb)}</p>")
        bits.append(
            f"<p>Create an Extra Instruction Block and name it exactly <strong>{esc(block['name'])}</strong>. "
            "Copy the capital letters as they are. Then paste the box below into that block.</p>"
        )
        bits.append(block_box(boxes, block))
    return "\n".join(bits)


def write_creatures(blocks: dict) -> None:
    boxes = Boxes()
    nonhuman = [f"Non-human plug-in 1/7"] + [f"non-human plug-in {i}/7" for i in range(2, 8)]
    blurbs = {
        "Non-human plug-in 1/7": "This is part 1 of the seven-part catalog. Paste all seven parts if you use this catalog. The name starts with a capital N.",
        "non-human plug-in 2/7": "This is part 2 of 7. The name starts with a lowercase n. Copy that lowercase letter, or the game treats it as a different block.",
        "non-human plug-in 3/7": "This is part 3 of 7. The name starts with a lowercase n. Copy that lowercase letter.",
        "non-human plug-in 4/7": "This is part 4 of 7. The name starts with a lowercase n. Copy that lowercase letter.",
        "non-human plug-in 5/7": "This is part 5 of 7. The name starts with a lowercase n. Copy that lowercase letter.",
        "non-human plug-in 6/7": "This is part 6 of 7. The name starts with a lowercase n. Copy that lowercase letter.",
        "non-human plug-in 7/7": "This is part 7 of 7. The name starts with a lowercase n. Copy that lowercase letter. After this part, the catalog is complete.",
        "Non-human plug-in - Core Only": "This is the short install. Paste this one block and stop, if you do not need the full catalog of body plans. Do not also paste the seven parts. Together they repeat the shared rules every turn.",
        "Robot plug-in 1/2": "This is robot part 1 of 2. Paste both robot parts. One part alone does not state the whole body plan.",
        "robot plug-in 2/2": "This is robot part 2 of 2. The name starts with a lowercase r. Copy that lowercase letter, and paste this together with part 1.",
        "Pokegirl plug in 1/2": "This is Pokégirl part 1 of 2. Paste both parts. The name has a space in “plug in,” not a hyphen.",
        "Pokegirl plug in 2/2": "This is Pokégirl part 2 of 2. Paste it together with part 1. The name has a space in “plug in,” not a hyphen.",
    }
    bits = [
        """
<p class="bubble">CREATURE ADD-ONS</p>
<h1>Not-human people.</h1>
<p class="lede">Pick one set and copy every part in that set. Copy the name exactly, including capital letters and lowercase letters. A different capital letter is a different block, and the set will be incomplete.</p>
<div class="panel"><p>The picture model draws a human body unless the prompt states the body plan in a formula it already knows how to draw. These blocks are those formulas. They look at the picture fields and the notebooks, then add the formula to the picture prompt.</p><p>Core Only is the shared rules in one block. The seven parts are the full catalog of body plans. If you paste both, the shared rules are sent twice every turn. Robot needs both of its parts. Pokégirl needs both of its parts.</p></div>
<div class="warn"><p><strong>Non-human.</strong> The cheap install is Core Only by itself. The full catalog is all seven parts, and nothing else from this set. Do not paste Core Only and the seven parts together.</p></div>
<p class="quiet"><a href="extras.html">Extra writing</a> · <a href="bodies.html">Bodies</a> · <a href="creatures.html">Creatures</a></p>
<h2>Cheap install — Core Only</h2>
""",
        emit_blocks(boxes, blocks, ["Non-human plug-in - Core Only"], blurbs),
        "<h2>Full catalog — seven parts</h2>",
        "<p>Paste all seven parts. Do not also paste Core Only. If both are on, the shared rules are sent twice every turn.</p>",
        emit_blocks(boxes, blocks, nonhuman, blurbs),
        "<h2>Robot — paste both</h2>",
        "<p>Paste both robot parts. One part does not state the whole body plan, so the picture model falls back toward a human body.</p>",
        emit_blocks(boxes, blocks, ["Robot plug-in 1/2", "robot plug-in 2/2"], blurbs),
        "<h2>Pokégirl — paste both</h2>",
        "<p>Paste both Pokégirl parts. The names say “plug in” with a space, not a hyphen. Copy that spacing.</p>",
        emit_blocks(boxes, blocks, ["Pokegirl plug in 1/2", "Pokegirl plug in 2/2"], blurbs),
    ]
    (DOCS / "creatures.html").write_text(
        page_shell(
            "Creature add-ons — The Script Library",
            "Non-human, Robot, and Pokégirl Extra Instruction Blocks. Pick one set.",
            "".join(bits),
        ),
        encoding="utf-8",
    )


def write_notebooks(trackers: dict, triggers: dict) -> None:
    boxes = Boxes()
    small = trackers["NPC Appearance small cast"]
    large = trackers["NPC Appearance (large cast)"]
    body = f"""
<p class="bubble">NOTEBOOKS</p>
<h1>Notebooks that update themselves.</h1>
<p class="lede">Your look page already told you to create Player Appearance and one NPC Appearance list. This page is the other notebooks. A notebook is an Items to track entry the game keeps between turns. Copy a set together: the real notebook, the Update notebook, and the trigger. A trigger is a small automatic job that runs when its check is true. If you copy only one piece, the set cannot finish the update.</p>
<div class="panel"><p><strong>Why an Update notebook</strong></p>
<p>If the story edits the real list and only fills in one field, that partial row can replace the whole person and wipe the other fields. The Update notebook is a staging inbox, so the story writes the new row there instead of on the real list. The trigger then copies that whole row onto the real list, matching the person by name or by alias, and clears the inbox. Leave Auto-update off on the real Relationship and Intimacy notebooks. If you turn it on, the story also writes those notebooks directly, and the staging step is skipped.</p></div>
<nav class="toc">
<a href="#rel">Relationship</a>
<a href="#intimacy">Intimacy</a>
<a href="#npc">NPC appearance</a>
</nav>
<section class="step" id="rel">
<h2>Relationship</h2>
<p>Copy all three pieces below. On the real notebook, turn Auto-update off. On the Update notebook, turn Auto-update on. That is how this set is meant to run. Auto-update is the switch that lets the story rewrite a notebook after each turn.</p>
<h3>1. The real notebook</h3>
{tracker_boxes(boxes, trackers["Relationship Tracker"])}
<h3>2. The Update notebook</h3>
{tracker_boxes(boxes, trackers["Relationship Update"])}
{trigger_section(boxes, triggers["Relationship Updater"])}
</section>
<section class="step" id="intimacy">
<h2>Intimacy</h2>
<p>Use the same three-piece pattern. Copy the log, which is the real notebook. Then copy the Update notebook. Then copy the trigger that moves a finished row from the Update notebook onto the log.</p>
<h3>1. The real notebook</h3>
{tracker_boxes(boxes, trackers["Intimacy Log"])}
<h3>2. The Update notebook</h3>
{tracker_boxes(boxes, trackers["Intimacy Update"])}
{trigger_section(boxes, triggers["Intimacy Updater"])}
</section>
<section class="step" id="npc">
<h2>NPC appearance update</h2>
<p>This set is optional. Use it when you want appearance edits to land through a staging list, the same way relationship edits do. You already pasted either the small-cast or the large-cast NPC Appearance notebook on your look page. This page does not replace that notebook. It adds the inbox and the trigger.</p>
<p>The Update notebook’s rules, as they ship, are only a reminder. After you paste, replace those rules with the update rules from the NPC notebook you already copied. Then set that real NPC Appearance notebook to <strong>Auto-update: off</strong>, so the story stops writing it directly. Leave this Update notebook on <strong>Auto-update: on</strong>, so the story writes the inbox and the trigger copies the row.</p>
<h3>1. The Update notebook</h3>
{tracker_boxes(boxes, trackers["NPC Appearance Update"])}
<h3>Paste one of these over the reminder</h3>
<p>A small cast uses the first box. A large cast uses the second. Paste that text into the Update notebook’s update rules, replacing the reminder that shipped with it. The small-cast rules add a person when they speak or are physically in the scene. The large-cast rules add a person only when the Relationship Tracker marks them <code>significant: true</code>.</p>
{boxes.box("Small-cast update rules — paste over the reminder", small.get("updateInstructions") or "")}
{boxes.box("Large-cast update rules — paste over the reminder", large.get("updateInstructions") or "")}
{trigger_section(boxes, triggers["NPC Appearance Updater"])}
</section>
{later_links()}
"""
    (DOCS / "notebooks.html").write_text(
        page_shell(
            "Notebooks — The Script Library",
            "Relationship, intimacy, and NPC appearance staging notebooks, with their triggers.",
            body,
        ),
        encoding="utf-8",
    )


def write_styles(game: dict) -> None:
    boxes = Boxes()
    by_strip = {entry["name"].strip(): entry for entry in game["loreBookEntries"]}
    grouped: list[tuple[str, list[str]]] = []
    used: set[str] = set()
    for heading, names in STYLE_GROUPS:
        found = []
        for name in names:
            if name not in by_strip:
                raise SystemExit(f"missing picture style: {name}")
            found.append(name)
            used.add(name)
        grouped.append((heading, found))
    extra = [entry["name"].strip() for entry in game["loreBookEntries"] if entry["name"].strip() not in used]
    if extra:
        grouped.append(("More looks", extra))

    toc = []
    sections = []
    for heading, names in grouped:
        anchor = slug(heading)
        toc.append(f'<a href="#{anchor}">{esc(heading)}</a>')
        bits = [f'<section class="step" id="{anchor}"><h2>{esc(heading)}</h2>']
        for name in names:
            entry = by_strip[name]
            COV.lore.add(entry["name"])
            try:
                prefix, suffix = split_style(entry["content"])
            except ValueError as exc:
                raise SystemExit(f"{entry['name']}: {exc}") from exc
            exact = entry["name"]
            bits.append(f"<h3>{esc(exact.strip())}</h3>")
            if exact.endswith(" "):
                bits.append(
                    "<p>The look’s name in the library ends with a space. You do not paste that name into Image style. "
                    "You paste the two boxes below. The name is only a label on this page.</p>"
                )
            bits.append(
                "<p>Paste the prefix into Image style, on the people prefix. Paste the suffix into Image style, on the people suffix. "
                "The prefix is the words that go in front of the picture prompt. The suffix is the words that go after it. "
                "Those fields are read by the picture model only, not by the story. "
                "If places and objects should share the same look, paste the same prefix and suffix into the not-people fields too.</p>"
            )
            bits.append(boxes.box(f"{exact.strip()} — prefix", prefix))
            bits.append(boxes.box(f"{exact.strip()} — suffix", suffix))
        bits.append("</section>")
        sections.append("\n".join(bits))

    body = f"""
<p class="bubble">PICTURE STYLES</p>
<h1>Pick one named look.</h1>
<p class="lede">Each look below is a finished pair: a prefix and a suffix. Copy one pair into Image style. These looks were stored with no keywords, so they never fire by themselves. You have to paste them. Image style is read by the picture model, not by the story writer.</p>
<div class="warn"><p>This replaces step 4 on a look page. A named style and the blank template are two different wrappers around the picture. Use one of them. If you paste both, the picture model receives two looks at once. If the look you picked includes sex-styling words and your game does not show sex in the pictures, delete those words before you save.</p></div>
<p>If you would rather fill the wrapper yourself, the blank template is on each look page and on <a href="frame.html">Picture frame words</a>.</p>
<nav class="toc">{"".join(toc)}</nav>
{"".join(sections)}
"""
    (DOCS / "styles.html").write_text(
        page_shell(
            "Picture styles — The Script Library",
            "Forty-three named picture looks. Pick one prefix and one suffix.",
            body,
        ),
        encoding="utf-8",
    )


VIDEO_LABELS = {
    "videoPlan": "Video plan — what the clip is about",
    "videoImagePosition": "Whether the still is the first frame or the last frame",
    "videoPrompt": "Video prompt",
}


def write_video(game: dict) -> None:
    boxes = Boxes()
    video = game["videoPromptInstructions"]
    bits = [
        """
<p class="bubble">VIDEO</p>
<h1>Picture to video.</h1>
<p class="lede">Use this page only if your game makes a video from the picture. These are three world fields. They are not Extra Instruction Blocks, and they are not notebooks you create under Items to track.</p>
<div class="panel"><p>The still picture is one frame of the clip. The position field tells the video step whether that still is the first frame or the last frame. Video duration and video style are filled in by the video step itself, so you do not create notebooks named <code>$videoDuration</code> or <code>$videoStyle</code>.</p></div>
"""
    ]
    for key, label in VIDEO_LABELS.items():
        COV.video.add(key)
        bits.append(f"<h2>{esc(label)}</h2>")
        bits.append(
            f"<p>Paste the box below into the <strong>{esc(key)}</strong> field on the video settings. "
            "Copy the whole box, including the instructions inside it.</p>"
        )
        bits.append(boxes.box(label, video[key]))
    (DOCS / "video.html").write_text(
        page_shell(
            "Video — The Script Library",
            "Video plan, still position, and video prompt. Paste into the video fields.",
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
<p class="lede">You do not need this page to finish a look. Each look page already includes these four boxes as step 4. A finished named look lives on <a href="styles.html">Styles</a>. Use that named look or this blank template. Do not paste both, or the picture model receives two looks at once.</p>
<div class="panel">
<p><strong>What to keep and what to delete</strong></p>
<ul>
<li><strong>Photographs.</strong> Keep the tone and the lines that sound like photos or computer graphics. Delete the paragraph that is only for manga or comics. That paragraph would pull a photograph toward a comic page.</li>
<li><strong>A painting.</strong> Keep the words about paint, brushes, and illustration. Delete camera and film words. Delete Unreal Engine lines unless you truly want the painting to look like a game screenshot.</li>
<li><strong>Manga pages.</strong> Keep the manga and comic paragraph. That is the page layout you picked. Delete Unreal Engine lines, which push the comic toward a game screenshot.</li>
<li><strong>A game that does not show sex in the pictures.</strong> Delete the phrases about sexually stylized art, erotic styling, and genitalia. Those words are instructions to the picture model. Leaving them in will push the pictures that way.</li>
</ul>
</div>
"""
    ]
    for key, label in FRAME_FIELDS:
        bits.append(f"<h2>{esc(label)}</h2>")
        bits.append(boxes.box(label, game[key]))
    (DOCS / "frame.html").write_text(
        page_shell(
            "Picture frame words — The Script Library",
            "The blank image style prefix and suffix template.",
            "".join(bits),
        ),
        encoding="utf-8",
    )


def write_dont() -> None:
    body = """
<p class="bubble">BACKUP</p>
<h1>Never mix these.</h1>
<p class="lede">Each look page already says what to leave turned off. This page is the full list, in case you come back later and forget which pieces fight.</p>
<div class="warn">
<ul>
<li>Every turn draws a new picture. Wrangler and Bareback reuse last turn’s written description of the face and clothes when you spell the name the same way. The other picture scripts throw that description away and copy notebooks instead. That is why those two looks get no appearance notebooks, and why the others do.</li>
<li>Turn on one picture script in a game. Positional Director, SFW Director, the Unified directors, and Lean Director are all the photograph job. If two of them are on, they write the same picture fields and they contradict each other.</li>
<li>Wrangler and Bareback are the same one-person job, the one that reuses the written description. Pick one of them. Leave the other off.</li>
<li>Photo, painting, manga, cheap photos, and Bob Ross use Player Appearance and one NPC Appearance list. Wrangler and Bareback use no appearance notebooks. Creating those notebooks on Wrangler or Bareback throws away the saved description that was keeping the face steady.</li>
<li>For non-human people, paste Core Only, or paste all seven Non-human parts. Do not paste both. Both together send the shared rules twice every turn.</li>
<li>Paste one body add-on. Male, futa, agender, and hypertrophy all describe the same body. If you paste them all, the picture model receives several body plans at once.</li>
<li>Use a named picture style, or use the blank image-style template. Do not use both. Both are wrappers around the same picture prompt.</li>
<li>Turn on Wyvern Word Caps only when the picture model is Wyvern. It replaces the longer Manticore word limits. On Manticore, leave it off.</li>
<li>Do not copy Foolproofing, Terminate, or Safeguard (Library only). Those stay in the library file. They are not meant for a live game, so this site does not give you a paste box for them.</li>
<li>The library file lists five sample skills: Empathy, Persuasion, Resilience, Perception, and Resourcefulness. Add those names on the Skills screen only if you want them in your game. They are not picture modules and they are not story modules.</li>
<li>Example people in the library file — Blank, Esmé Strandloper, the Hogwarts student, Jeanette Doe clothed, Jeanette Doe naked, and the Harpy test — are samples. Do not paste them into your cast unless you actually want those examples in your game.</li>
<li>Do not overwrite Description instructions you already wrote for pictures with the story-voice Description paste. Description is how the story talks. If that field already holds picture instructions, leave it alone.</li>
</ul>
</div>
<p><a class="btn" href="library.html">BACK TO LOOKS</a></p>
"""
    (DOCS / "dont.html").write_text(
        page_shell(
            "Never mix these — The Script Library",
            "One picture script, one body add-on, one picture style, and what to leave in the dump.",
            body,
        ),
        encoding="utf-8",
    )


def assert_coverage(game: dict) -> None:
    blocks = {b["name"] for b in game["instructionBlocks"]}
    missing_blocks = blocks - COV.blocks
    if missing_blocks:
        raise SystemExit("blocks not on a page: " + ", ".join(sorted(missing_blocks)))
    extra_blocks = COV.blocks - blocks
    if extra_blocks:
        raise SystemExit("unknown blocks recorded: " + ", ".join(sorted(extra_blocks)))

    trackers = {t["name"] for t in game["trackedItems"]}
    missing_trackers = trackers - COV.trackers - SKIP_TRACKERS
    if missing_trackers:
        raise SystemExit("trackers not on a page: " + ", ".join(sorted(missing_trackers)))

    triggers = {t["name"] for t in game["triggerEvents"]}
    missing_triggers = triggers - COV.triggers - SKIP_TRIGGERS
    if missing_triggers:
        raise SystemExit("triggers not on a page: " + ", ".join(sorted(repr(n) for n in missing_triggers)))

    lore = {e["name"] for e in game["loreBookEntries"]}
    missing_lore = lore - COV.lore
    if missing_lore:
        raise SystemExit("styles not on a page: " + ", ".join(sorted(missing_lore)))

    video = set(game["videoPromptInstructions"])
    missing_video = video - COV.video
    if missing_video:
        raise SystemExit("video fields not on a page: " + ", ".join(sorted(missing_video)))


def main() -> None:
    game = load_game()
    blocks = block_map(game)
    trackers = tracker_map(game)
    triggers = trigger_map(game)
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "assets").mkdir(parents=True, exist_ok=True)
    write_index()
    write_library(blocks)
    write_start(blocks)
    for script in SCRIPTS:
        write_script_page(script, blocks, trackers, game)
    write_dual()
    write_writing(game, blocks, trackers)
    write_extras(blocks)
    write_bodies(blocks)
    write_creatures(blocks)
    write_notebooks(trackers, triggers)
    write_styles(game)
    write_video(game)
    write_frame(game)
    write_dont()
    assert_coverage(game)
    pages = sorted(p.name for p in DOCS.glob("*.html"))
    print(f"Wrote {len(pages)} HTML pages from {JSON_PATH.name}")
    for name in pages:
        print(" ", name)


if __name__ == "__main__":
    main()
