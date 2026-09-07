# Dial Prose

The time, written as a sentence. Cormorant Garamond gives the hour a generous serif, with smaller italic words between the phrases. A quiet digital line keeps the exact local time in view.

This English edition uses familiar five-minute phrases: “ten past six,” “a quarter till three,” and “twelve o’clock.” The words round down to the current five-minute interval; the footer shows exact minutes in 24-hour format. The face updates once a minute and works offline.

Dial Prose supports Basalt, Chalk, Diorite, Emery, Flint and Gabbro. Each display shape has its own spacing and type sizes. Monochrome watches use solid white lettering; color watches have softer gray connecting words. There are no settings or button controls.

## Build

Use Pebble SDK 4.33.1 and its command-line tool. The source archive includes the fonts and generated lettering required to build the face.

```sh
pebble build --sdk 4.33.1
```

The checks need Node.js, a C compiler, Python 3 and the packages in `test/requirements.txt`. Packaging and emulator checks use the Python environment supplied with `pebble-tool`.

```sh
python3 -m pip install -r test/requirements.txt
make test
make assets
python test/package.py
python test/emulator.py gabbro --fresh
python test/package.py --evidence build/evidence
python test/independent.py
```

Run the emulator check for each declared target before staging a release. The source check compares all 1,440 daily phrases with the supplied English grammar. Rendering checks cover every minute on each display layout, including round-screen edges. Emulator reports identify the exact build they tested. Physical-watch daylight readability and battery measurements remain open.

## Source and fonts

Luke Steuber created Dial Prose and its original [Spoken Prose clock](https://datapoems.io/clocks/dial-prose/). The supplied web source is preserved in `reference/source.html`; this native edition uses its English grammar and five-minute timing. The web version also includes other languages and palette controls.

Code is copyright 2026 Luke Steuber, under the MIT License. [Cormorant Garamond](https://github.com/google/fonts/tree/main/ofl/cormorantgaramond) is by Christian Thalmann and the Cormorant Project Authors. [JetBrains Mono](https://github.com/google/fonts/tree/main/ofl/jetbrainsmono) supplies the exact-time line. Both fonts use the SIL Open Font License; their licenses and source fingerprints accompany the font files in `resources/fonts/`.
