"""Validate a native Dial Prose PBW; --evidence stages a verified local review kit.

Copyright 2026 Luke Steuber. MIT License. No upload or physical-watch connection.
Run with the Pebble-tool Python environment (libpebble2 and pypng).
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

import png
from libpebble2.util.stm32_crc import crc32

ROOT = Path(__file__).resolve().parent.parent
UUID = 'b824aad2-f29d-4081-a6f6-60a19f00262d'
SIZES = {'basalt': (144, 168), 'diorite': (144, 168), 'emery': (200, 228),
         'flint': (144, 168), 'chalk': (180, 180), 'gabbro': (260, 260)}
ROOT_FILES = ('package.json', 'package-lock.json', 'wscript', 'Makefile', 'README.md', 'LICENSE', '.gitignore', '.gitattributes')
SOURCE_DIRS = ('src', 'resources', 'reference', 'test', 'tools')
REQUIRED_FRAMES = {'hero', 'idle', 'quarter', 'twentyfive', 'eleven-till', 'seven-quarter', 'eight-oclock', 'eight-till', 'noon', 'midnight', 'before-five', 'five-rollover', 'before-noon', 'noon-rollover', 'before-midnight', 'midnight-rollover'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_png(path, expected):
    """Decode all rows, including PNG chunk CRC checks; an IHDR alone is not evidence."""
    width, height, rows, info = png.Reader(bytes=path.read_bytes()).read()
    require((width, height) == expected, f'{path.name}: expected {expected}, got {(width, height)}')
    count = 0
    pixels = hashlib.sha256()
    for row in rows:
        require(len(row) == width * info['planes'], f'{path.name}: truncated pixel row')
        pixels.update(row.tobytes() if hasattr(row, 'tobytes') else bytes(row))
        count += 1
    require(count == height, f'{path.name}: truncated PNG')
    return pixels.hexdigest()


def validate_build(root):
    source = json.loads((root / 'package.json').read_text())
    pebble = source['pebble']
    require(source['name'] == 'dial-prose', 'Unexpected source package name')
    require(source['author'] == pebble['companyName'] == 'Luke Steuber', 'Incorrect authorship')
    require(pebble['uuid'] == UUID, 'Dial Prose UUID must be preserved')
    targets = pebble['targetPlatforms']
    require(len(targets) == len(SIZES) and set(targets) == set(SIZES), 'Expected exactly six target platforms')
    require(pebble.get('capabilities') == ['configurable'] and pebble.get('messageKeys') == {'LANGUAGE': 0, 'THEME': 90, 'REQUEST_STATE': 91}, 'Expected language settings channel')
    # The SDK names its bundle after the checkout directory, including imported ZIPs.
    pbw = root / 'build' / f'{root.name}.pbw'
    with zipfile.ZipFile(pbw) as archive:
        require(archive.testzip() is None, 'Corrupt PBW ZIP')
        manifest = json.loads(archive.read('appinfo.json'))
        require(manifest['uuid'] == UUID, 'PBW UUID mismatch')
        require(manifest['versionLabel'] == source['version'], 'PBW version mismatch')
        require(manifest['companyName'] == 'Luke Steuber', 'PBW companyName mismatch')
        require(manifest['watchapp']['watchface'] is True, 'PBW is not a watchface')
        declared = manifest['targetPlatforms']
        require(len(declared) == len(SIZES) and set(declared) == set(SIZES), 'PBW target mismatch')
        require(manifest['capabilities'] == ['configurable'] and manifest['appKeys'] == {'LANGUAGE': 0, 'THEME': 90, 'REQUEST_STATE': 91}, 'PBW language settings mismatch')
        require('pebble-js-app.js' in archive.namelist(), 'Missing phone settings bundle')
        require(any(item.get('menuIcon') for item in manifest['resources']['media']), 'Missing menu icon')
        for platform in sorted(SIZES):
            contents = json.loads(archive.read(f'{platform}/manifest.json'))
            for kind in ('application', 'resources'):
                item = contents[kind]
                payload = archive.read(f'{platform}/{item["name"]}')
                if kind == 'resources':
                    require(len(payload) <= 262144, f'{platform}: store resource budget exceeded')
                require(len(payload) == item['size'] > 0, f'{platform}: incorrect {kind} size')
                require(crc32(payload) == item['crc'], f'{platform}: incorrect {kind} STM32 CRC')
    check_png(root / 'resources/images/menu-icon.png', (25, 25))
    return source, pbw, sha(pbw)


def validate_evidence(evidence, digest):
    reports = {}
    for platform, size in SIZES.items():
        report = json.loads((evidence / f'{platform}-report.json').read_text())
        require(report['platform'] == platform, f'{platform}: wrong report platform')
        require(report['pbwSHA256'] == digest, f'{platform}: stale evidence')
        for flag in ('nativePhrases', 'pixelParity', 'minuteCadence', 'naturalFiveRollover', 'naturalNoonRollover', 'naturalMidnightRollover'):
            require(report.get(flag) is True, f'{platform}: missing {flag}')
        logs = report['logs']
        require(not any(any(term in line.lower() for term in ('fault', 'crash', 'allocation failed'))
                        for line in logs), f'{platform}: native fault logged')
        for fixture in ('10:08:', '11:59:', '12:00:', '03:15:', '07:25:', '10:35:', '23:59:', '00:00:'):
            require(any('Prose' in line and 'time=' + fixture in line for line in logs),
                    f'{platform}: missing time fixture {fixture}')
        names, pixels = [], {}
        for relative in report['frames']:
            name = Path(relative).name
            require(name.startswith(platform + '-') and name.endswith('.png'), f'{platform}: unexpected frame {name}')
            require(name not in names, f'{platform}: duplicate frame {name}')
            names.append(name)
            pixels[name] = check_png(evidence / name, size)
        require({f'{platform}-{name}.png' for name in REQUIRED_FRAMES}.issubset(names),
                f'{platform}: incomplete native fixture frames')
        require(pixels[f'{platform}-hero.png'] == pixels[f'{platform}-idle.png'],
                f'{platform}: unexpected sub-minute changes')
        # Reports in the review kit refer to adjacent captures, not an absent build directory.
        report = dict(report, frames=[name for name in names if not name.endswith('-boot.png')])
        reports[platform] = report
    return reports


def source_files(root):
    files = [root / name for name in ROOT_FILES]
    excluded = {'__pycache__', '.git', 'build', 'release', 'evidence', 'node_modules', '.pytest_cache'}
    for directory in SOURCE_DIRS:
        folder = root / directory
        require(folder.is_dir(), f'Missing source directory: {directory}')
        files.extend(file for file in folder.rglob('*') if file.is_file()
                     and not excluded.intersection(file.relative_to(folder).parts)
                     and file.suffix not in ('.pyc', '.pyo') and file.name != '.DS_Store')
    for file in files:
        require(file.is_file() and not file.is_symlink(), f'Missing or linked source input: {file}')
    return sorted(files)


def stage(root, evidence, source, pbw, digest, reports):
    files = source_files(root)  # Validate portability inputs before writing any release artifact.
    out = root / 'release'
    out.mkdir(exist_ok=True)
    name = f'dial-prose-{source["version"]}'
    package = out / f'{name}.pbw'
    shutil.copy2(pbw, package)
    archive_path = out / f'{name}-source.zip'
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file in files:
            archive.write(file, file.relative_to(root))
        require(archive.testzip() is None, 'Corrupt source ZIP')
    captures = root / 'evidence'
    captures.mkdir(exist_ok=True)
    summary = {'version': source['version'], 'uuid': UUID, 'pbwSHA256': digest,
               'sourceZipSHA256': sha(archive_path), 'platforms': {}}
    for platform, report in reports.items():
        (captures / f'{platform}-report.json').write_text(json.dumps(report, indent=2) + '\n')
        for name in report['frames']:
            original, destination = evidence / name, captures / name
            if original.resolve() != destination.resolve():
                shutil.copy2(original, destination)
        samples = [tuple(map(int, match.groups())) for line in report['logs']
                   if (match := re.search(r'frame_ms=(\d+) free=(\d+)', line))]
        summary['platforms'][platform] = {
            'capturedAt': report['capturedAt'], 'dimensions': list(SIZES[platform]),
            'minuteCadence': True, 'pixelParity': True, 'naturalFiveRollover': True, 'naturalNoonRollover': True, 'naturalMidnightRollover': True,
            'nativeFrameCount': len(report['frames']),
            'loggedRenderMS': {'min': min(s[0] for s in samples), 'max': max(s[0] for s in samples)} if samples else None,
            'renderMeasurementClock': 'Watch wall time; fixture clock changes can affect these samples.',
            'minimumLoggedFreeHeapBytes': min(s[1] for s in samples) if samples else None}
    summary['limits'] = ('Local emulator-tested review candidate. Native PNGs require visual inspection. '
                         'Physical-watch power/readability, CloudPebble import and store publication remain unverified.')
    (captures / 'validation.json').write_text(json.dumps(summary, indent=2) + '\n')
    artifacts = sorted(path for path in out.iterdir() if path.suffix in ('.pbw', '.zip'))
    (out / 'SHA256SUMS').write_text(''.join(f'{sha(path)}  {path.name}\n' for path in artifacts))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path,
                        help='Validate six native capture reports and stage the local PBW/source review kit')
    args = parser.parse_args()
    source, pbw, digest = validate_build(ROOT)
    if args.evidence:
        reports = validate_evidence(args.evidence, digest)
        print(json.dumps(stage(ROOT, args.evidence, source, pbw, digest, reports), indent=2))
    else:
        print(f'Dial Prose {source["version"]}: six native targets, menu icon, offline watchface; SHA-256 {digest}')


if __name__ == '__main__':
    main()
