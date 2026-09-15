# Prose

The time, written as a sentence. Large Cormorant Garamond letters name the hour, with smaller italic words connecting the phrases.

[![Get Prose](https://img.shields.io/badge/Pebble-Get_Prose-2563eb?style=flat-square)](https://apps.repebble.com/0aaaa16fba454f08bc4abb09) [![MIT code license](https://img.shields.io/badge/Code-MIT-181717?style=flat-square)](LICENSE) [![Ambient Time collection](https://img.shields.io/badge/Ambient_Time-Collection-181717?style=flat-square)](https://ambient-time.com/watch/pebble/)

The English setting uses familiar five-minute phrases: “ten past six,” “a quarter till three,” and “twelve o’clock.” The words round down to the current five-minute interval. The face updates once a minute and works offline.

Prose supports rectangular Pebble watches: Basalt, Diorite, Emery and Flint. Each display size has its own spacing and type sizes. Monochrome watches use solid white lettering; color watches have softer gray connecting words. Choose among 13 languages in the Pebble phone app’s face settings: English, German, French, Italian, Spanish, Portuguese, Dutch, Swedish, Ukrainian, Japanese, Chinese, Korean and Arabic. The watch remembers your selection offline.

## Build

Use Pebble SDK 4.33.1 and its command-line tool. The source archive includes the fonts and generated lettering required to build the face.

```sh
npm ci --ignore-scripts
pebble build --sdk 4.33.1
```

The checks need Node.js, a C compiler, Python 3 and the packages in `test/requirements.txt`. Packaging and emulator checks use the Python environment supplied with `pebble-tool`.

```sh
python3 -m pip install -r test/requirements.txt
make test
make assets
python test/package.py
python test/emulator-language.py basalt --fresh
python test/package.py --evidence build/evidence
python test/independent.py
```

Run the emulator check for each declared target before staging a release. `test/package.py --evidence build/evidence` freezes the reviewed package and source archive. `test/independent.py` builds that archive outside the checkout and compares native code, resources and phone JavaScript. The source check compares all 1,440 daily phrases with the supplied English grammar. Rendering checks cover every minute on each display layout, at each supported rectangular size. Emulator reports identify the exact build they tested. Physical-watch daylight readability and battery measurements remain open.

## Source and fonts

Luke Steuber created Prose and its original [Spoken Prose clock](https://datapoems.io/clocks/dial-prose/). The supplied web source is preserved in `reference/source.html`; this native edition preserves its five-minute timing. The saved multilingual grammar and source hashes are under `reference/multilingual/`. Each language uses its own source grammar. Palette controls remain specific to the web version.

CJK and Arabic lettering uses bundled Noto font subsets, with OFL licenses and source fingerprints in `resources/fonts/multilingual/`. See `tools/languages/README.md` for reproducible language resources and settings checks.

Luke Steuber’s original code is copyright 2026 Luke Steuber, under the MIT License. [Cormorant Garamond](https://github.com/google/fonts/tree/main/ofl/cormorantgaramond) is by Christian Thalmann and the Cormorant Project Authors. The font uses the SIL Open Font License; its license and source fingerprints accompany the font files in `resources/fonts/`.

The bundled tinf decoder is copyright Joergen Ibsen and uses the zlib license. Its notice and local modifications are recorded in [tinf-LICENSE](src/c/tinf-LICENSE) and [tinf-provenance.json](src/c/tinf-provenance.json). Phone settings use `@rebble/clay`, which retains its own MIT notice.

## Around here

[Luke Steuber](https://github.com/lukeslp) · [Data Poems](https://github.com/data-poems) · [Ambient Time](https://github.com/ambient-time) · [Actually Useful AI](https://github.com/actually-useful-ai) · [One Impossible Thing](https://github.com/one-impossible-thing)

Made by [Luke Steuber](https://lukesteuber.com). Questions or collaboration:
[luke@lukesteuber.com](mailto:luke@lukesteuber.com).
