# IW-SLICK

**Infinite Worlds Script Library Creation Kit**

IW-SLICK is an open-source community library for [Infinite Worlds](https://infiniteworlds.app) creators. The project gathers, maintains, organizes, and makes discoverable modular scripts, systems, and other reusable game components. Browse how other creators are building their games, reuse what is useful, and contribute your own work.

The project is currently in its early organization phase. Contributions, suggestions, and help improving the library are welcome.

**Hosted site (same index as this README):** [https://mellow-truffle-5x34.here.now/](https://mellow-truffle-5x34.here.now/)

---

## Contributing

Pull requests are welcome. You can contribute a new module, script, system, documentation improvement, or organizational change. If you would rather not open a pull request, reach out directly to the repository maintainer with what you would like added.

The goal is to keep useful modular material together in one place so creators can add it to their own games and discover interesting systems from the community.

## First contribution: The Script Library

The Script Library is the first contribution to IW-SLICK. It was added with permission from **@KaapstadMK**, with pieces from Xyphrax, Thyr, TWNT, Tori, Funky Munky, MrDrunkinDragon, WolfishGrimm, and SpacemanSpiff.

It contains picture scripts, story voice, and extras for Infinite Worlds. The hosted pages provide a convenient way to browse and copy these contributions into a game, but the project is intended to grow beyond this first collection.

**How to copy:** [https://mellow-truffle-5x34.here.now/library.html](https://mellow-truffle-5x34.here.now/library.html)

Pick **one** picture look. The card shows the exact Extra Instruction Block name. Stay on that look’s page until pictures work (picture rules, notebooks, fill blanks, Image style). Then add story voice or extras if you want them.

The JSON is the source for rebuilding the Library pages and is available to contributors who prefer working directly with files.

| Resource | Where |
|----------|--------|
| Hosted look picker | [mellow-truffle-5x34.here.now/library.html](https://mellow-truffle-5x34.here.now/library.html) |
| Rebuild Library pages | `python scripts/build_guide.py` (reads the JSON, writes `docs/`) |
| Library JSON (v2.38 source) | [`library/The Script Library 2.38.json`](library/The%20Script%20Library%202.38.json) |
| Shared Infinite Worlds world | [infiniteworlds.app/shared/7zDKHR](https://infiniteworlds.app/shared/7zDKHR) |

Old picture scripts and library-only Foolproofing / Terminate / Safeguard are not on the copy pages.

## Planned tooling

A small Windows tool is in development and will be added to this repository when it is ready. The goal is one-click module installation:

`JSON in -> Install Module -> JSON out`

This will make it easier to add library modules to an existing game without manually editing the game JSON.

## Official platform docs

- [PawScript expressions](https://infiniteworlds.app/pawscript-expressions-guide)
- [PawScript scripts](https://infiniteworlds.app/pawscript-script-guide)
- [YAML guide](https://infiniteworlds.app/yaml-guide)

---

## License

[GPL-3.0](LICENSE)
