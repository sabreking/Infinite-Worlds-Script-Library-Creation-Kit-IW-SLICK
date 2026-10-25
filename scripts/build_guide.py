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
            '<a href="https://infiniteworlds.app">Infinite Worlds</a> world creators. '
            "Contributions from the community. More will land here.</p>"
            "<p>License: GPL-3.0</p>"
        )
    else:
        nav = "\n".join(f'<a href="{href}">{esc(label)}</a>' for href, label in LIB_NAV)
        footer = (
            f"<p>The Script Library 3.29 — copy from these pages into Infinite Worlds. "
            f"A contribution from <strong>{esc(CREDITS)}</strong>.</p>"
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
        return "Visible to: AI only (the player does not see this notebook)"
    if vis == "ai_only_boring":
        return (
            "Visible to: AI only, boring "
            "(the AI still gets this every turn; it is marked boring so it is not treated as story prose)"
        )
    if vis in ("hidden", "hidden_boring"):
        return "Visible to: hidden"
    return "Visible to: everyone"


def auto_line(item: dict) -> str:
    return "Auto-update: on" if item.get("autoUpdate") else "Auto-update: off"


def space_note(name: str) -> str:
    if name.endswith(" "):
        return " The name ends with a space. Copy it exactly."
    return ""


def tracker_boxes(boxes: Boxes, item: dict) -> str:
    COV.trackers.add(item["name"])
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
        if str(val).strip():
            bits.append(boxes.box(label, str(val)))
    return "\n".join(bits)


def block_box(boxes: Boxes, block: dict, title: str | None = None) -> str:
    COV.blocks.add(block["name"])
    name = block["name"]
    heading = title or f"Paste into Extra Instruction Blocks — name it exactly: {name}"
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
        once = "<p>Turn on “can trigger more than once.”</p>"
    return "\n".join(
        [
            f"<h3>The trigger</h3>",
            space,
            f"<p>Name the trigger exactly: <strong>{esc(name)}</strong></p>",
            boxes.box("Trigger name", name),
            once,
            "<p><strong>Condition.</strong> Type: PawScript. Paste this check.</p>",
            boxes.box("PawScript condition", cond["data"]),
            "<p><strong>Effect.</strong> Type: Run a script. Paste this script.</p>",
            boxes.box("Run a script", effect["data"]),
        ]
    )


SCRIPTS = [
    {
        "file": "pd.html",
        "hub": "Photos of people",
        "hub_line": "Photographs, movie stills, realistic people.",
        "title": "Photos of people",
        "block": "Positional Director",
        "frame": "photo",
        "when": (
            "Use this when you want the pictures to look like photographs — "
            "movie stills, camera language, realistic people. A new picture is "
            "drawn every time, so you keep a notebook of how people look."
        ),
        "avoid": (
            "Do not turn on any other picture script. SFW Director, Lean Director, "
            "and the Unified directors are the same photo job. Pick this one only."
        ),
        "family": "pd",
        "after": "photo-budget",
    },
    {
        "file": "sfw.html",
        "hub": "Photos, no sex posing",
        "hub_line": "The same photograph job, without sex posing.",
        "title": "Photos, no sex posing",
        "block": "SFW Director (WF?)",
        "frame": "photo",
        "when": (
            "Use this when you want photographs, and you do not want sex-posing rules "
            "in the picture script. A new picture is drawn every time, so you keep "
            "appearance notebooks."
        ),
        "avoid": (
            "Do not turn on any other picture script. This is the photograph script "
            "with sex posing left out. Do not also use Positional Director."
        ),
        "family": "pd",
        "after": "photo-budget-sfw",
    },
    {
        "file": "explicit.html",
        "hub": "Photos with size tiers",
        "hub_line": "Photographs that name specific body-size tiers.",
        "title": "Photos with size tiers",
        "block": "Unified Explicit Director",
        "frame": "mixed",
        "when": (
            "Use this when the pictures are photographs and the game needs named "
            "body-size tiers. A new picture is drawn every time, so you keep "
            "appearance notebooks."
        ),
        "avoid": (
            "Do not turn on any other picture script. Do not also use Positional Director, "
            "Principled, or Lean. They are the same picture job."
        ),
        "family": "pd",
        "after": "artist-fill",
    },
    {
        "file": "principled.html",
        "hub": "Richer photos, no size tiers",
        "hub_line": "More detail in the photograph, without size-tier language.",
        "title": "Richer photos, no size tiers",
        "block": "Unified Principled Director (WF)",
        "frame": "mixed",
        "when": (
            "Use this when you want a fuller photograph script, and you do not want "
            "body-size tiers. A new picture is drawn every time, so you keep "
            "appearance notebooks."
        ),
        "avoid": (
            "Do not turn on any other picture script. Do not also use Unified Explicit "
            "or Positional Director."
        ),
        "family": "pd",
        "after": "film-or-art",
    },
    {
        "file": "unified-lean.html",
        "hub": "Shorter unified photos",
        "hub_line": "The unified photograph rules, cut down.",
        "title": "Shorter unified photos",
        "block": "Unified Lean Director (WF)",
        "frame": "mixed",
        "when": (
            "Use this when you want the unified photograph rules in a shorter sheet. "
            "A new picture is drawn every time, so you keep appearance notebooks."
        ),
        "avoid": (
            "Do not turn on any other picture script. Do not also use Lean Director "
            "or Unified Explicit."
        ),
        "family": "pd",
        "after": "film-or-art",
    },
    {
        "file": "lean.html",
        "hub": "Cheap photos",
        "hub_line": "The shortest photograph rules. Still a new picture every time.",
        "title": "Cheap photos",
        "block": "Lean Director (WF)",
        "frame": "photo",
        "when": (
            "Use this when you still want photographs, but the shortest rule sheet. "
            "A new picture is drawn every time, so you still keep appearance notebooks."
        ),
        "avoid": (
            "Do not turn on any other picture script. Do not also use Positional Director "
            "or Unified Lean."
        ),
        "family": "pd",
        "after": "photo-budget",
    },
    {
        "file": "artist.html",
        "hub": "A painting",
        "hub_line": "Oil, watercolor, illustration — drawn art, not a camera.",
        "title": "A painting",
        "block": "Artist",
        "frame": "paint",
        "when": (
            "Use this when you want the pictures to look painted or drawn — "
            "oil, watercolor, print, illustration. A new picture is drawn every time, "
            "so you keep appearance notebooks."
        ),
        "avoid": (
            "Do not turn on any other picture script. Comic pages are the manga script, "
            "not this one."
        ),
        "family": "pd",
        "after": "artist-fill",
    },
    {
        "file": "manga.html",
        "hub": "Manga pages",
        "hub_line": "Comic pages with talk bubbles.",
        "title": "Manga pages",
        "block": "Manga/Storyboard",
        "frame": "manga",
        "when": (
            "Use this when you want comic pages — panels and talk bubbles. "
            "A new picture is drawn every time, so you keep appearance notebooks."
        ),
        "avoid": (
            "Do not turn on any other picture script. The painting script is one still "
            "picture, not comic pages."
        ),
        "family": "pd",
        "after": "manga-fill",
    },
    {
        "file": "bob-ross.html",
        "hub": "A crowded scene",
        "hub_line": "Lots of people arranged in one picture.",
        "title": "A crowded scene",
        "block": "Bob Ross script (WF)",
        "frame": "mixed",
        "when": (
            "Use this when the shot is a crowd arranged in space, not a close-up of "
            "one or two people. A new picture is drawn every time. Use the same "
            "Player Appearance and NPC Appearance notebooks as the photo scripts."
        ),
        "avoid": (
            "Do not turn on any other picture script. There is no separate Bob Ross "
            "notebook. Use Player Appearance and NPC Appearance."
        ),
        "family": "pd",
        "after": "artist-fill",
    },
    {
        "file": "single.html",
        "hub": "One person the game remembers",
        "hub_line": "One face that stays the same from picture to picture.",
        "title": "One person the game remembers",
        "block": "Wrangler (WF)",
        "frame": "mixed",
        "rename": (
            "This block used to be called Vanilla IW Wrangler (Single subject). "
            "The name is now Wrangler (WF)."
        ),
        "when": (
            "Use this when there is one named person and you want the game to remember "
            "the face. Create no appearance notebooks."
        ),
        "avoid": (
            "Do not turn on any other picture script. Do not also use Bareback Wrangler. "
            "Do not create Player Appearance or NPC Appearance notebooks — those stop "
            "the game from remembering the face."
        ),
        "family": "none",
        "after": "remembered-face",
    },
    {
        "file": "bareback.html",
        "hub": "One person, lean language",
        "hub_line": "One remembered face, with shorter picture rules.",
        "title": "One person, lean language",
        "block": "Bareback Wrangler (WF)",
        "frame": "mixed",
        "when": (
            "Use this when there is one named person, you want the game to remember "
            "the face, and you want shorter picture rules. Create no appearance notebooks."
        ),
        "avoid": (
            "Do not turn on any other picture script. Do not also use Wrangler (WF). "
            "Do not create appearance notebooks."
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
        "<li>Find hidden notes wrapped in <code>&lt;# … #&gt;</code>. The game ignores those until you delete the wrap.</li>"
        "<li>Fill the budget / Hollywood-or-indie / genre line in square brackets, then unwrap it.</li>"
        "<li>Write 3 to 5 mood words, then unwrap that line too.</li>"
        "<li>Unwrap sex or fight pose packs only if the game actually shows those scenes.</li>"
        "</ul>"
    ),
    "photo-budget-sfw": (
        "<ul>"
        "<li>Find hidden notes wrapped in <code>&lt;# … #&gt;</code>. The game ignores those until you delete the wrap.</li>"
        "<li>Fill the budget / Hollywood-or-indie / genre line in square brackets, then unwrap it.</li>"
        "<li>Write 3 to 5 mood words, then unwrap that line too.</li>"
        "<li>Unwrap the fight pose pack only if the game shows fights. This look has no sex-posing pack.</li>"
        "</ul>"
    ),
    "artist-fill": (
        "<ul>"
        "<li>Find hidden notes wrapped in <code>&lt;# … #&gt;</code>. The game ignores those until you delete the wrap.</li>"
        "<li>Fill the period / region / artist line in square brackets, then unwrap it.</li>"
        "<li>Write 3 to 5 mood words, then unwrap that line too.</li>"
        "<li>Unwrap sex or fight pose packs only if the game actually shows those scenes.</li>"
        "</ul>"
    ),
    "film-or-art": (
        "<ul>"
        "<li>Find hidden notes wrapped in <code>&lt;# … #&gt;</code>. The game ignores those until you delete the wrap.</li>"
        "<li>There is a film-or-painting slot. Fill one side, delete the other, then unwrap it.</li>"
        "<li>Fill the period / region / artist line in square brackets, then unwrap it.</li>"
        "<li>Write 3 to 5 mood words, then unwrap that line too.</li>"
        "<li>Unwrap sex or fight pose packs only if the game actually shows those scenes.</li>"
        "</ul>"
    ),
    "manga-fill": (
        "<ul>"
        "<li>Find hidden notes wrapped in <code>&lt;# … #&gt;</code>. The game ignores those until you delete the wrap.</li>"
        "<li>Fill the tradition line (time, region, Shonen / Seinen, and so on) in square brackets, then unwrap it.</li>"
        "<li>Write 3 to 5 mood words, then unwrap that line too.</li>"
        "<li>Unwrap sex or fight pose packs only if the game actually shows those scenes.</li>"
        "</ul>"
    ),
    "remembered-face": (
        "<ul>"
        "<li>Keep spelling the person’s name the same way every turn.</li>"
        "<li>Leave the hidden “If using appearance tracked items” note wrapped. Do not unwrap it. Create no appearance notebooks.</li>"
        "<li>There is a film-or-painting slot. Fill one side, delete the other, then unwrap it.</li>"
        "<li>Fill the period / region / artist line in square brackets, then unwrap it.</li>"
        "<li>Write 3 to 5 mood words, then unwrap that line too.</li>"
        "<li>Unwrap sex or fight pose packs only if the game actually shows those scenes.</li>"
        "</ul>"
    ),
}


def exact_name(script: dict, blocks: dict) -> str:
    return blocks[script["block"]]["name"]


def look_card(script: dict, blocks: dict) -> str:
    exact = exact_name(script, blocks)
    face = (
        "The game remembers the face. Create no appearance notebooks"
        if script["family"] == "none"
        else "A new picture every time. You keep appearance notebooks"
    )
    return (
        f'<a class="card" href="{script["file"]}">'
        f"<strong>{esc(script['hub'])}</strong>"
        f'<p class="chip">{esc(exact)}</p>'
        f"<p>{esc(script['hub_line'])}</p>"
        f'<p class="face">{esc(face)}.</p>'
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
    player = trackers["Player Appearance"]
    small = trackers["NPC Appearance small cast"]
    large = trackers["NPC Appearance (large cast)"]
    return (
        "<p>Always copy the player notebook. Then copy <strong>either</strong> the few-people list "
        "<strong>or</strong> the many-people list.</p>"
        "<p>Relationship, intimacy, and the NPC appearance update live on the "
        '<a href="notebooks.html">Notebooks</a> page. Copy those after pictures work.</p>'
        f"<h3>Always — player</h3>\n{tracker_boxes(boxes, player)}\n"
        '<div class="or-split">'
        "<section><h3>A few people — copy this one, skip the large list</h3>\n"
        f"{tracker_boxes(boxes, small)}</section>"
        "<section><h3>Many people — copy this one, skip the small list</h3>\n"
        f"{tracker_boxes(boxes, large)}</section>"
        "</div>"
    )


def done_box() -> str:
    return """
<div class="ok">
<p><strong>Pictures are done</strong> when those four steps are in your game. Optional next:</p>
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
        "<p><strong>The name ends with a space.</strong> Copy it exactly from the box.</p>"
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
<div class="panel">{AFTER[script["after"]]}</div>
</section>
<section class="step" id="step4">
<h2>Step 4 — Image style</h2>
<p>These four boxes are the blank template. Paste them, then keep or delete paragraphs for <em>this</em> look.</p>
<p>If you want a finished named look instead, open <a href="styles.html">Styles</a> and copy one prefix and one suffix. Do not paste both the blank template and a named style.</p>
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
<p class="quiet">After pictures work:
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
<p class="ok">Stay on that look’s page until pictures work. Come back later for story voice, notebooks, or a named picture style.</p>
{"".join(groups)}
{later_links()}
"""


def write_index() -> None:
    body = f"""
<p class="bubble">IW-SLICK</p>
<h1>Copy-paste kit.</h1>
<p class="lede">A public kit for Infinite Worlds world creators. Contributions from the community. More will land here.</p>
<h2>Contributions</h2>
<div class="grid">
<a class="card" href="library.html">
<strong>The Script Library 3.29</strong>
<p>Picture scripts, story voice, notebooks, and picture styles — copy from the page into Infinite Worlds.</p>
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
            "IW-SLICK is a public copy-paste kit for Infinite Worlds. The Script Library 3.29 is the first contribution.",
            body,
            mode="home",
        ),
        encoding="utf-8",
    )


def write_library(blocks: dict) -> None:
    intro = (
        "Open one picture look. The card shows the exact Extra Instruction Block name. "
        "Copy everything on that page. Pick one look only."
    )
    (DOCS / "library.html").write_text(
        page_shell(
            "The Script Library 3.29 — pick a look",
            "Pick one picture script by name. Stay on that page until pictures work.",
            picker_body(blocks, intro),
        ),
        encoding="utf-8",
    )


def write_start(blocks: dict) -> None:
    intro = (
        "You are in The Script Library 3.29. Open a look below. Stay on that page until pictures work. "
        "The card shows the exact Extra Instruction Block name."
    )
    (DOCS / "start.html").write_text(
        page_shell(
            "The Script Library 3.29 — pick a look",
            "Open one picture look and finish pictures on that page.",
            picker_body(blocks, intro),
        ),
        encoding="utf-8",
    )


def write_dual() -> None:
    body = """
<p class="bubble">MOVED</p>
<h1>Two people moved.</h1>
<p class="lede">There is no dual Wrangler in this library. Two named people use a photograph script. A crowd uses Bob Ross.</p>
<div class="grid">
<a class="card" href="pd.html">
<strong>Photos of people</strong>
<p class="chip">Positional Director</p>
<p>Two named people in a photograph.</p>
<span class="btn">OPEN THIS</span>
</a>
<a class="card" href="lean.html">
<strong>Cheap photos</strong>
<p class="chip">Lean Director (WF)</p>
<p>The short photograph sheet.</p>
<span class="btn">OPEN THIS</span>
</a>
<a class="card" href="bob-ross.html">
<strong>A crowded scene</strong>
<p class="chip">Bob Ross script (WF)</p>
<p>Lots of people in one picture.</p>
<span class="btn">OPEN THIS</span>
</a>
</div>
<p><a class="btn" href="library.html">ALL LOOKS</a></p>
"""
    (DOCS / "dual.html").write_text(
        page_shell(
            "Two people moved — The Script Library",
            "The dual Wrangler is gone. Use Positional Director, Lean Director, or Bob Ross.",
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
<p class="lede">Do this <strong>once</strong>, not once per picture look. Paste in the order of the Infinite Worlds screen.</p>
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
<p>Paste this into Main Instructions. It reads the Reader Profile and Story Metadata notebooks. Those are steps 7 and 8 on this page. Copy them too, or those lines have nothing to read.</p>
{boxes.box("Main Instructions — Split Game Master", split_gm(game))}
</section>
<section class="step" id="w2">
<h2>Step 2 — Extra Instruction Blocks (Storymaster)</h2>
<p>Name it exactly <strong>{esc(story["name"])}</strong>. The variable block is hidden inside <code>&lt;# … #&gt;</code>. Fill the square brackets: genres, what those genres owe the reader, this story’s appeal, what is new, tone, themes, conflicts, and the turn counts. Then delete the wraps so the game can read that block.</p>
{block_box(boxes, story)}
</section>
<section class="step" id="w3">
<h2>Step 3 — Author style</h2>
<p>Replace <code>[Author Style]</code> with how the sentences should sound. Leave “Written by Storymaster.” in place.</p>
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
<section class="step" id="w7">
<h2>Step 7 — Reader Profile notebook</h2>
<p>This notebook is the real human reader, not the player character. The AI fills it over many turns.</p>
{tracker_boxes(boxes, reader)}
</section>
<section class="step" id="w8">
<h2>Step 8 — Story Metadata notebook</h2>
<p>Genre, appeal, and who the story is for. It should change only when the story itself changes for good.</p>
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
    ("Characterization", "People stay in character."),
    ("Pacing", "Scenes do not rush or stall for no reason."),
    ("Sexual Content", "Sex writing rules."),
    ("Period Knowledge", "Fill [time period] after you paste."),
    ("Narrative Craft", "Prose craft rules."),
    ("Lion Bugfixes", "Fixes for Lion-family models (Smilodon, Lynx, Massive Cat)."),
    ("Leopard Bugfixes", "Fixes for Leopard models."),
    ("Caracal Bugfixes", "Fixes for Caracal models."),
    ("Dolphin Bugfixes", "Fixes for Dolphin models. Slow burn stays slow."),
    (
        "Wyvern Word Caps",
        "Turn this on only if your picture model is Wyvern. It replaces the Manticore word limits. Do not run both word-limit sets.",
    ),
    (
        "Cover Image script",
        "This is for a store cover, not the picture every turn. Copy the block, give it to an AI with your game title and blurb, then paste the result into the cover appearance field. Do not put art-style words in that result. Style lives in Image style.",
    ),
]


def write_extras(blocks: dict) -> None:
    boxes = Boxes()
    bits = [
        """
<p class="bubble">ADD-ONS</p>
<h1>Optional extras.</h1>
<p class="lede">Use these after pictures work. Each one is its own Extra Instruction Block. Copy only what your game needs. More blocks cost more every turn.</p>
<p class="quiet"><a href="extras.html">Extra writing</a> · <a href="bodies.html">Bodies</a> · <a href="creatures.html">Creatures</a> · <a href="notebooks.html">Notebooks</a> · <a href="video.html">Video</a></p>
<div class="warn"><p><strong>Lion, Leopard, Caracal, and Dolphin:</strong> after you paste, set that block to “Applies to certain models” and tick only the models named under it. In Infinite Worlds settings, turn on “AI-specific extra instructions”. If that switch is off, the block hits every model.</p></div>
"""
    ]
    for name, blurb in EXTRAS:
        block = blocks[name]
        exact = block["name"]
        bits.append(f"<h2>{esc(exact.strip())}</h2>")
        bits.append(f"<p>{esc(blurb)}{esc(space_note(exact))}</p>")
        bits.append(f"<p>Name the Extra Instruction Block exactly: <strong>{esc(exact)}</strong></p>")
        ticks = MODEL_TICKS.get(exact.strip())
        if ticks:
            bits.append(
                f'<div class="panel"><p><strong>Tick these models</strong></p><p>{esc(ticks)}</p></div>'
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
        "Male body language. Paste this instead of stacking it on top of every other body block.",
    ),
    ("Futanari description block", "Futa body language."),
    ("Agender/Genderless description block", "Body language that is not gendered male or female."),
    ("Hypermasc/Hypertrophy module", "Very large male muscle and size language."),
]


def write_bodies(blocks: dict) -> None:
    boxes = Boxes()
    bits = [
        """
<p class="bubble">BODY ADD-ONS</p>
<h1>Bodies.</h1>
<p class="lede">These are extra Extra Instruction Blocks for the photo, painting, and manga scripts. Paste one. They fight if you stack them.</p>
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
        bits.append(f"<p>Name it exactly: <strong>{esc(block['name'])}</strong></p>")
        bits.append(block_box(boxes, block))
    return "\n".join(bits)


def write_creatures(blocks: dict) -> None:
    boxes = Boxes()
    nonhuman = [f"Non-human plug-in 1/7"] + [f"non-human plug-in {i}/7" for i in range(2, 8)]
    blurbs = {
        "Non-human plug-in 1/7": "Part 1 of 7.",
        "non-human plug-in 2/7": "Part 2 of 7. The name starts with a lowercase n.",
        "non-human plug-in 3/7": "Part 3 of 7. The name starts with a lowercase n.",
        "non-human plug-in 4/7": "Part 4 of 7. The name starts with a lowercase n.",
        "non-human plug-in 5/7": "Part 5 of 7. The name starts with a lowercase n.",
        "non-human plug-in 6/7": "Part 6 of 7. The name starts with a lowercase n.",
        "non-human plug-in 7/7": "Part 7 of 7. The name starts with a lowercase n.",
        "Non-human plug-in - Core Only": "The short install. Stop here if you do not need the full catalog.",
        "Robot plug-in 1/2": "Robot part 1 of 2.",
        "robot plug-in 2/2": "Robot part 2 of 2. The name starts with a lowercase r.",
        "Pokegirl plug in 1/2": "Pokégirl part 1 of 2.",
        "Pokegirl plug in 2/2": "Pokégirl part 2 of 2.",
    }
    bits = [
        """
<p class="bubble">CREATURE ADD-ONS</p>
<h1>Not-human people.</h1>
<p class="lede">Pick one set. Copy the name exactly, including capital letters.</p>
<div class="warn"><p><strong>Non-human:</strong> cheap install is Core Only alone. The full catalog is all seven parts. Do not paste Core Only and the seven parts together.</p></div>
<p class="quiet"><a href="extras.html">Extra writing</a> · <a href="bodies.html">Bodies</a> · <a href="creatures.html">Creatures</a></p>
<h2>Cheap install — Core Only</h2>
""",
        emit_blocks(boxes, blocks, ["Non-human plug-in - Core Only"], blurbs),
        "<h2>Full catalog — seven parts</h2>",
        "<p>Paste all seven. Do not also paste Core Only.</p>",
        emit_blocks(boxes, blocks, nonhuman, blurbs),
        "<h2>Robot — paste both</h2>",
        emit_blocks(boxes, blocks, ["Robot plug-in 1/2", "robot plug-in 2/2"], blurbs),
        "<h2>Pokégirl — paste both</h2>",
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
<p class="lede">Your look page already has Player Appearance and one NPC Appearance list. This page is the other notebooks. Copy a set together: the real notebook, the Update notebook, and the trigger.</p>
<p>The AI writes the Update notebook. The trigger copies that row onto the real notebook and clears the update row. A row is the whole record, so the Update notebook should hold the full row, not one changed field by itself.</p>
<nav class="toc">
<a href="#rel">Relationship</a>
<a href="#intimacy">Intimacy</a>
<a href="#npc">NPC appearance</a>
</nav>
<section class="step" id="rel">
<h2>Relationship</h2>
<p>Copy all three. Auto-update stays off on the real notebook and on on the Update notebook. That is how this set ships.</p>
<h3>1. The real notebook</h3>
{tracker_boxes(boxes, trackers["Relationship Tracker"])}
<h3>2. The Update notebook</h3>
{tracker_boxes(boxes, trackers["Relationship Update"])}
{trigger_section(boxes, triggers["Relationship Updater"])}
</section>
<section class="step" id="intimacy">
<h2>Intimacy</h2>
<p>Same pattern. Copy the log, the Update notebook, and the trigger.</p>
<h3>1. The real notebook</h3>
{tracker_boxes(boxes, trackers["Intimacy Log"])}
<h3>2. The Update notebook</h3>
{tracker_boxes(boxes, trackers["Intimacy Update"])}
{trigger_section(boxes, triggers["Intimacy Updater"])}
</section>
<section class="step" id="npc">
<h2>NPC appearance update</h2>
<p>Optional. Use this when appearance edits should land through a staging list. You already pasted either the small-cast or the large-cast NPC Appearance notebook on your look page.</p>
<p>This Update notebook’s rules are only a reminder. After you paste, replace those rules with the update rules from the notebook you already copied. Then set that NPC Appearance notebook to <strong>Auto-update: off</strong>. Leave this Update notebook on Auto-update: on.</p>
<h3>1. The Update notebook</h3>
{tracker_boxes(boxes, trackers["NPC Appearance Update"])}
<h3>Paste one of these over the reminder</h3>
<p>Small-cast games use the first box. Many-people games use the second. Paste it into the Update notebook’s update rules, replacing the reminder.</p>
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
                bits.append("<p>The look name ends with a space. You do not paste the name into Image style. You paste the two boxes below.</p>")
            bits.append("<p>Prefix goes in Image style — people — prefix. Suffix goes in Image style — people — suffix. Repeat both on the not-people fields if places should match.</p>")
            bits.append(boxes.box(f"{exact.strip()} — prefix", prefix))
            bits.append(boxes.box(f"{exact.strip()} — suffix", suffix))
        bits.append("</section>")
        sections.append("\n".join(bits))

    body = f"""
<p class="bubble">PICTURE STYLES</p>
<h1>Pick one named look.</h1>
<p class="lede">Each look is a finished prefix and suffix. Copy one. Do not paste all of them.</p>
<div class="warn"><p>This replaces step 4 on a look page. Do not also paste that blank template. If the look includes sex-styling words and your game does not show sex in pictures, delete those words.</p></div>
<p>The blank template, if you would rather fill it yourself, is on each look page and on <a href="frame.html">Picture frame words</a>.</p>
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
<p class="lede">Only if your game makes a video from the picture. These are three world fields, not Extra Instruction Blocks and not notebooks.</p>
<div class="ok"><p>Do not add notebooks for video duration or video style. The game already supplies those.</p></div>
"""
    ]
    for key, label in VIDEO_LABELS.items():
        COV.video.add(key)
        bits.append(f"<h2>{esc(label)}</h2>")
        bits.append(f"<p>Paste into the <strong>{esc(key)}</strong> field.</p>")
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
<p class="lede">You do not need this page to finish a look. Each look already has these four boxes. A finished named look lives on <a href="styles.html">Styles</a>. Use that or this template, not both.</p>
<div class="panel">
<p><strong>Keep or delete, in plain English</strong></p>
<ul>
<li><strong>Photographs:</strong> keep tone and lines that sound like photos or CGI. Delete the manga/comic-only paragraph.</li>
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
<p class="lede">Each look page already says what not to turn on. This is the full list.</p>
<div class="warn">
<ul>
<li>One picture script in a game. Positional Director, SFW Director, the Unified directors, and Lean Director are all the photograph job. Pick one.</li>
<li>Wrangler and Bareback are the same remembered-face job. Pick one.</li>
<li>Photo, painting, manga, cheap photos, and Bob Ross use Player Appearance and one NPC Appearance list. Wrangler and Bareback use no appearance notebooks.</li>
<li>Non-human Core Only, or all seven Non-human parts. Not both.</li>
<li>One body add-on. Male, futa, agender, and hypertrophy fight if you paste them all.</li>
<li>A named picture style, or the blank image-style template. Not both.</li>
<li>Wyvern Word Caps only when the picture model is Wyvern. It replaces the Manticore word limits.</li>
<li>Do not copy Foolproofing, Terminate, or Safeguard (Library only). Those stay in the library dump. They are not for a live game.</li>
<li>The JSON lists five sample skills: Empathy, Persuasion, Resilience, Perception, Resourcefulness. Add those names on the Skills screen only if you want them. They are not picture or story modules.</li>
<li>Example cast rows in the JSON (Blank, Esmé Strandloper, Hogwarts student, Jeanette Doe clothed, Jeanette Doe naked, Harpy test) are samples. Do not paste them into your cast unless you want those examples.</li>
<li>Do not overwrite Description instructions you already wrote for pictures with the story-voice Description paste.</li>
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
