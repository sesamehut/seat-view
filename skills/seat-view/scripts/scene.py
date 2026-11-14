"""Original parameterized concert geometry. Python standard library only.

Meters; X right, Y up, +Z audience. Azimuth 0 = +Z, +90 = +X.
Tier and row numbers are one-based model coordinates, never ticket numbers.
"""
import argparse
import datetime
import json
import math
import re
from pathlib import Path
from urllib.parse import urlparse


class SpecError(ValueError):
    """A user-correctable scene specification error."""


def _object(value, fields, path):
    if not isinstance(value, dict):
        raise SpecError(f"{path}: expected an object")
    extra, missing = set(value) - set(fields), set(fields) - set(value)
    if extra or missing:
        raise SpecError(f"{path}: unknown keys {sorted(extra)}, missing keys {sorted(missing)}")


def _number(value, low, high, path, integer=False):
    try:
        finite = isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise SpecError(f"{path}: expected a finite number")
    if not low - 1e-9 <= value <= high + 1e-9 or (integer and int(value) != value):
        raise SpecError(f"{path}: expected {'integer ' if integer else ''}in [{low:g}, {high:g}]")
    return value


def _text(value, path, limit=500):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise SpecError(f"{path}: expected 1–{limit} characters")
    return value


def _list(value, low, high, path):
    if not isinstance(value, list) or not low <= len(value) <= high:
        raise SpecError(f"{path}: expected {low}–{high} items")


def _url(value, path):
    _text(value, path, 2000)
    try:
        u = urlparse(value)
        valid = u.scheme in ('http', 'https') and u.hostname and not u.username and not u.password
    except ValueError:
        valid = False
    if not valid:
        raise SpecError(f"{path}: expected an HTTP(S) URL without credentials")


def validate_spec(spec):
    """Reject malformed/unbounded inputs; do not silently alter researched geometry."""
    _object(spec, ['schema_version', 'name', 'kind', 'units', 'bowl', 'stage', 'views',
                   'evidence', 'sources', 'assumptions'], 'spec')
    if type(spec['schema_version']) is not int or spec['schema_version'] != 1:
        raise SpecError('schema_version: expected 1')
    _text(spec['name'], 'name', 120)
    if spec['kind'] not in ('generic', 'researched') or spec['units'] != 'm':
        raise SpecError('kind must be generic/researched and units must be m')
    bowl = spec['bowl']
    _object(bowl, ['radius_x', 'radius_y', 'tiers'], 'bowl')
    for key in ('radius_x', 'radius_y'):
        _number(bowl[key], 20, 200, f'bowl.{key}')
    _list(bowl['tiers'], 1, 4, 'bowl.tiers')
    geometry = ['bowl.radius_x', 'bowl.radius_y']
    prior_top, offset = -1, 0
    for i, tier in enumerate(bowl['tiers']):
        path = f'bowl.tiers[{i}]'
        fields = ['rows', 'row_depth', 'row_rise', 'base_height', 'gap_before']
        _object(tier, fields, path)
        for key, low, high in [('rows', 1, 60), ('row_depth', .45, 1.5),
                               ('row_rise', .1, .85), ('base_height', 0, 75), ('gap_before', 0, 15)]:
            _number(tier[key], low, high, f'{path}.{key}', key == 'rows')
            geometry.append(f'{path}.{key}')
        top = tier['base_height'] + (tier['rows'] - 1) * tier['row_rise']
        if tier['base_height'] <= prior_top or top > 95:
            raise SpecError(f'{path}: tiers must rise without overlap; top must not exceed 95 m')
        prior_top = top
        offset += tier['gap_before'] + tier['rows'] * tier['row_depth']
    if offset > 120:
        raise SpecError('bowl.tiers: combined radial depth must not exceed 120 m')
    stage = spec['stage']
    _object(stage, ['layout', 'width', 'depth', 'height'], 'stage')
    if stage['layout'] not in ('end', 'thrust', 'center'):
        raise SpecError('stage.layout: expected end, thrust, or center')
    for key, low, high in [('width', 4, min(100, bowl['radius_x'] * 1.4)),
                           ('depth', 3, min(60, bowl['radius_y'] * .7)), ('height', .2, 5)]:
        _number(stage[key], low, high, f'stage.{key}')
    geometry += [f'stage.{key}' for key in ('layout', 'width', 'depth', 'height')]
    _list(spec['views'], 1, 12, 'views')
    ids = set()
    for i, view in enumerate(spec['views']):
        _object(view, ['id', 'label', 'tier', 'row', 'azimuth_deg'], f'views[{i}]')
        if not isinstance(view['id'], str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,39}', view['id']):
            raise SpecError(f'views[{i}].id: use 1–40 lowercase letters, numbers, or hyphens')
        if view['id'] in ids:
            raise SpecError(f'views[{i}].id: duplicate identifier')
        ids.add(view['id'])
        _text(view['label'], f'views[{i}].label', 120)
        _number(view['tier'], 1, len(bowl['tiers']), f'views[{i}].tier', True)
        tier = bowl['tiers'][int(view['tier']) - 1]
        _number(view['row'], 1, tier['rows'], f'views[{i}].row', True)
        _number(view['azimuth_deg'], -360, 360, f'views[{i}].azimuth_deg')
    _list(spec['sources'], 0, 40, 'sources')
    urls = set()
    for i, source in enumerate(spec['sources']):
        _object(source, ['title', 'url', 'accessed'], f'sources[{i}]')
        _text(source['title'], f'sources[{i}].title', 300)
        _url(source['url'], f'sources[{i}].url')
        if not isinstance(source['accessed'], str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', source['accessed']):
            raise SpecError(f'sources[{i}].accessed: expected YYYY-MM-DD')
        try:
            datetime.date.fromisoformat(source['accessed'])
        except ValueError as exc:
            raise SpecError(f'sources[{i}].accessed: invalid calendar date') from exc
        urls.add(source['url'])
    if spec['kind'] == 'researched' and not urls:
        raise SpecError('researched scenes require at least one source')
    _list(spec['assumptions'], 0, 40, 'assumptions')
    for i, assumption in enumerate(spec['assumptions']):
        _text(assumption, f'assumptions[{i}]', 1000)
    _list(spec['evidence'], 0, 150, 'evidence')
    covered = set()
    for i, item in enumerate(spec['evidence']):
        _object(item, ['field', 'status', 'source_url', 'note'], f'evidence[{i}]')
        field = _text(item['field'], f'evidence[{i}].field', 120)
        if field not in geometry and field not in ('bowl', 'stage', 'views'):
            raise SpecError(f'evidence[{i}].field: unknown geometry field')
        if item['status'] not in ('verified', 'estimated', 'unknown'):
            raise SpecError(f'evidence[{i}].status: expected verified/estimated/unknown')
        _text(item['note'], f'evidence[{i}].note', 1000)
        if item['source_url']:
            _url(item['source_url'], f'evidence[{i}].source_url')
            if item['source_url'] not in urls:
                raise SpecError(f'evidence[{i}].source_url: add this URL to sources')
        elif item['source_url'] != '':
            raise SpecError(f'evidence[{i}].source_url: use a URL or empty string')
        if item['status'] == 'verified' and not item['source_url']:
            raise SpecError(f'evidence[{i}]: verified facts need a source URL')
        covered.update(path for path in geometry if path == field or path.startswith(field + '.'))
    if not spec['assumptions'] and set(geometry) - covered:
        raise SpecError('Uncovered geometry requires explicit assumptions or evidence for every field')
    return spec


class Mesh:
    def __init__(self, name, color):
        self.data = dict(name=name, color=color, vertices=[], faces=[])

    def face(self, points):
        start = len(self.data['vertices'])
        self.data['vertices'].extend([[round(v, 6) for v in p] for p in points])
        self.data['faces'].append(list(range(start, start + len(points))))


def _ellipse(bowl, angle, offset, height):
    s, c = math.sin(angle), math.cos(angle)
    nx, nz = s / bowl['radius_x'], c / bowl['radius_y']
    length = math.hypot(nx, nz)
    return [bowl['radius_x'] * s + offset * nx / length, height,
            bowl['radius_y'] * c + offset * nz / length]


def _box(name, center, size, color):
    x, y, z = center
    a, b, c = [v / 2 for v in size]
    vertices = [[x + sx * a, y + sy * b, z + sz * c]
                for sx, sy, sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                                   (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    return dict(name=name, color=color, vertices=vertices,
                faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[3,7,6,2],[0,4,7,3],[1,2,6,5]])


def _person(x, floor, z):
    # Original geometric human, 1.75 m from soles to crown; not a specific artist.
    parts = [('left-leg',(-.12,.37,0),(.17,.74,.23)),
             ('right-leg',(.12,.37,0),(.17,.74,.23)),
             ('torso',(0,1.04,0),(.44,.6,.25)),
             ('left-arm',(-.31,1.04,0),(.15,.62,.19)),
             ('right-arm',(.31,1.04,0),(.15,.62,.19)),
             ('neck',(0,1.4,0),(.13,.16,.13)),
             ('head',(0,1.6,0),(.27,.3,.25))]
    return [_box('performer-' + name, [x + p[0], floor + p[1], z + p[2]], size, '#ffc788')
            for name, p, size in parts]


def build_scene(spec):
    """Build a deterministic scene; all returned values are JSON-serializable."""
    validate_spec(spec)
    bowl, stage = spec['bowl'], spec['stage']
    meshes, tier_offsets = [], []
    ground = Mesh('infield', '#314c4d')
    for i in range(96):
        ground.face([[0, 0, 0], _ellipse(bowl, i*math.tau/96, 0, 0),
                     _ellipse(bowl, (i+1)*math.tau/96, 0, 0)])
    meshes.append(ground.data)
    offset = 0
    for ti, tier in enumerate(bowl['tiers']):
        offset += tier['gap_before']
        tier_offsets.append(offset)
        tread = Mesh(f'tier-{ti+1}-terraces', ['#d5c9b2','#b4c9c5','#cfbca9','#b8bec9'][ti])
        riser = Mesh(f'tier-{ti+1}-risers', '#697e7d')
        aisle = Mesh(f'tier-{ti+1}-aisles', '#4c6566')
        # 24 sectors. A darker terrace strip marks each conceptual aisle.
        # Surfaces remain continuous: every allowed azimuth has a safe eye point.
        for sector in range(24):
            left = math.radians(sector * 15 - 7.5)
            stops = [left, left + math.radians(1), left + math.radians(8), left + math.radians(15)]
            for segment, (a, b) in enumerate(zip(stops, stops[1:])):
                for row in range(int(tier['rows'])):
                    d = offset + row * tier['row_depth']
                    end = d + tier['row_depth']
                    h = tier['base_height'] + row * tier['row_rise']
                    mat = aisle if segment == 0 else tread
                    mat.face([_ellipse(bowl,a,d,h), _ellipse(bowl,a,end,h),
                              _ellipse(bowl,b,end,h), _ellipse(bowl,b,d,h)])
                    below = (0 if ti == 0 else max(0, h-.8)) if row == 0 else h-tier['row_rise']
                    if h > below:
                        riser.face([_ellipse(bowl,a,d,below),_ellipse(bowl,a,d,h),
                                    _ellipse(bowl,b,d,h),_ellipse(bowl,b,d,below)])
                back = offset + tier['rows'] * tier['row_depth']
                top = tier['base_height'] + (tier['rows']-1) * tier['row_rise']
                if top > 0:
                    riser.face([_ellipse(bowl,a,back,top),_ellipse(bowl,a,back,0),
                                _ellipse(bowl,b,back,0),_ellipse(bowl,b,back,top)])
        meshes.extend([tread.data, riser.data, aisle.data])
        offset += tier['rows'] * tier['row_depth']
    w, d, h = stage['width'], stage['depth'], stage['height']
    back_limit = bowl['radius_y'] * math.sqrt(1 - (w / (2*bowl['radius_x']))**2)
    center_z = 0 if stage['layout'] == 'center' else -back_limit + 2 + d/2
    meshes.append(_box('stage-main', [0,h/2,center_z], [w,h,d], '#203e43'))
    performer_z = center_z + d/2 - min(2, d*.25)
    if stage['layout'] == 'thrust':
        length = min(bowl['radius_y']*.45, bowl['radius_y']*.5 - center_z - d/2)
        width = min(8, w*.22)
        meshes.append(_box('stage-runway', [0,h/2,center_z+d/2+length/2], [width,h,length], '#2f6065'))
        performer_z = center_z + d/2 + length - 1
    screen_h = min(12, max(4, w*.28))
    if stage['layout'] == 'center':
        screen_w = min(12, w*.55)
        for sign in (-1, 1):
            meshes.append(_box(f'screen-{sign}', [0,h+screen_h+5,sign*.5],
                               [screen_w,screen_h,.3], '#5fced4'))
    else:
        meshes.append(_box('screen-main', [0,h+screen_h/2+.4,center_z-d/2+.4],
                           [w*.86,screen_h,.35], '#5fced4'))
    meshes.extend(_person(0,h,performer_z))
    target = [0,h+1.3,performer_z]
    views = []
    for view in spec['views']:
        index = int(view['tier']) - 1
        tier = bowl['tiers'][index]
        radial = tier_offsets[index] + (view['row']-.5) * tier['row_depth']
        height = tier['base_height'] + (view['row']-1) * tier['row_rise'] + 1.2
        pos = _ellipse(bowl, math.radians(view['azimuth_deg']), radial, height)
        dx, dy, dz = [pos[i]-target[i] for i in range(3)]
        views.append({**view, 'position':pos, 'target':target[:], 'distance_m':math.sqrt(dx*dx+dy*dy+dz*dz),
                      'depression_deg':math.degrees(math.atan2(dy,math.hypot(dx,dz))),
                      'fov_vertical_deg':50, 'eye_height_m':1.2})
    vertices = [p for mesh in meshes for p in mesh['vertices']]
    if sum(len(m['faces']) for m in meshes) > 50000:
        raise SpecError('Scene exceeds the 50,000-face generation budget')
    return dict(schema_version=1, name=spec['name'], kind=spec['kind'], spec=spec, meshes=meshes,
                views=views, target=target, bounds=dict(radius=max(math.hypot(p[0],p[2]) for p in vertices),
                                                       height=max(p[1] for p in vertices)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('spec', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        scene = build_scene(json.loads(args.spec.read_text(encoding='utf-8')))
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(scene, ensure_ascii=False, separators=(',', ':'), allow_nan=False), encoding='utf-8')
    except (SpecError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f'seat-view: {exc}\n')
    print(f'Generated {args.out} ({len(scene["meshes"])} meshes)')


if __name__ == '__main__':
    main()
