# Language resources

The face settings use append-only integer language IDs from `test/multilingual-source.json`. English is always 0. Never reorder existing IDs. The pinned web source supplies grammar, including inflection and five-minute rounding. No network is needed to display a saved language.

`make test` verifies all source minutes and exercises the production resource decoder under AddressSanitizer and UndefinedBehaviorSanitizer. `make settings-test`, after building, executes the bundled phone code and its actual Clay dependency. `test/emulator-language.py` checks each language and restart persistence on a declared native target.

To regenerate lettering, install `tools/languages/requirements.txt` and run `make languages`. Included OFL font subsets are sufficient. To deliberately rebuild missing subsets, download the original files listed in `resources/fonts/multilingual/provenance.json` and their accompanying OFL licenses, then set `PEBBLE_LANGUAGE_FONTS` to that directory. Expected filenames are listed in `generate.py`; license files are `OFL-CJK.txt` and `OFL-Arabic.txt`. Keep source and subset fingerprints with the result.

Arabic runs are shaped and reordered before rasterization. CJK uses the corresponding language font. The resource renderer reads bounded spans from flash instead of loading a complete language into RAM. Native screenshots and physical-watch readability are separate evidence.

Copyright 2026 Luke Steuber. MIT; fonts retain their included OFL terms.

Prose resources use independent 8 KiB deflate blocks. The cache and input buffer consume about 16 KiB; no complete language is allocated. The included tinf decoder is by Joergen Ibsen under its accompanying zlib license. Source fingerprints and local compatibility changes are recorded in `src/c/tinf-provenance.json`.
