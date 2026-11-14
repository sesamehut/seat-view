#!/usr/bin/env python3
"""Build a portable concert-view preview. Python standard library only."""
import argparse
import functools
import http.server
import json
from pathlib import Path
import sys

from scene import build_scene

SKILL = Path(__file__).resolve().parents[1]


def inline_json(value):
    # Prevent untrusted names and source notes from terminating an HTML script.
    return json.dumps(value, ensure_ascii=False, allow_nan=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


def build(spec_path, output):
    spec = json.loads(Path(spec_path).read_text(encoding='utf-8'))
    scene = build_scene(spec)
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    paths = [output / n for n in ('index.html', 'scene.json', 'venue.json', 'brief.md')]
    if any(p.exists() for p in paths):
        raise ValueError('Output contains generated files. Choose a new directory to preserve existing work.')
    template = (SKILL / 'assets/viewer.html').read_text(encoding='utf-8')
    library = (SKILL / 'assets/vendor/three.module.min.js').read_text(encoding='utf-8')
    licenses = (SKILL / 'LICENSE').read_text(encoding='utf-8') + '\nThree.js:\n' + (SKILL / 'assets/vendor/LICENSE.three').read_text(encoding='utf-8')
    html = template.replace('<!--__LICENSES__-->', '<!--\n' + licenses + '\n-->').replace('/*__THREE__*/', library).replace('/*__SCENE__*/', inline_json(scene))
    paths[0].write_text(html, encoding='utf-8')
    paths[1].write_text(json.dumps(scene, ensure_ascii=False, allow_nan=False), encoding='utf-8')
    paths[2].write_text(json.dumps(spec, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    lines = [f"# {spec['name']}", '', 'Approximate view study, not a verified ticket-seat reconstruction.', '',
             'All views use a 50° vertical field of view; distance is to the modeled performer.', '', '## Viewpoints', '']
    for view in scene['views']:
        lines.append(f"- {view['label']}: {view['distance_m']:.1f} m; depression {view['depression_deg']:.1f}°.")
    lines += ['', '## Assumptions', ''] + ['- ' + a for a in spec['assumptions']]
    lines += ['', '## Evidence', '']
    for e in spec['evidence']:
        lines.append(f"- {e['field']} — {e['status']}: {e['note']} ({e.get('source_url', '')})")
    lines += ['', '## Sources', '']
    for s in spec['sources']:
        lines.append(f"- {s['title']}: {s['url']} (accessed {s['accessed']})")
    lines += ['', '## Limits', '', 'Roof, railings, crowd, FOH towers and show-specific obstructions are not modeled. No visibility guarantee or seat recommendation score.', '']
    paths[3].write_text('\n'.join(lines), encoding='utf-8')
    return paths[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--demo', action='store_true', help='Use the fictional demo venue, offline')
    group.add_argument('--spec', type=Path, help='Evidence-backed venue specification')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--serve', type=int, metavar='PORT', help='Serve the output on localhost until Ctrl-C')
    args = parser.parse_args()
    if args.serve is not None and not 1024 <= args.serve <= 65535:
        parser.error('--serve must be between 1024 and 65535')
    try:
        index = build(SKILL / 'assets/demo-venue.json' if args.demo else args.spec, args.output)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f'seat-view: {exc}\n')
    print(f'Preview: {index.as_uri()}')
    if args.serve:
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(index.parent))
        with http.server.ThreadingHTTPServer(('127.0.0.1', args.serve), handler) as server:
            print(f'Local preview: http://127.0.0.1:{args.serve}', flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass


if __name__ == '__main__':
    main()
