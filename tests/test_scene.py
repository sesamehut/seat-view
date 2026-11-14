"""Geometry, camera, evidence and hostile-input checks for the generator."""
import copy
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'skills'/'seat-view'/'scripts'))
from scene import SpecError, build_scene, validate_spec


class SceneTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads((ROOT/'skills'/'seat-view'/'assets'/'demo-venue.json').read_text())

    def test_demo_is_finite_and_has_safe_camera_positions(self):
        scene = build_scene(self.spec)
        self.assertLess(sum(len(m['faces']) for m in scene['meshes']), 50000)
        for mesh in scene['meshes']:
            self.assertTrue(all(math.isfinite(v) for p in mesh['vertices'] for v in p))
            for face in mesh['faces']:
                self.assertGreaterEqual(len(face), 3)
                self.assertTrue(all(0 <= index < len(mesh['vertices']) for index in face))
        offsets, offset = [], 0
        for tier in self.spec['bowl']['tiers']:
            offset += tier['gap_before']
            offsets.append(offset)
            offset += tier['rows']*tier['row_depth']
        for view in scene['views']:
            tier = self.spec['bowl']['tiers'][view['tier']-1]
            expected = tier['base_height']+(view['row']-1)*tier['row_rise']+1.2
            self.assertAlmostEqual(view['position'][1], expected)
            self.assertEqual(view['fov_vertical_deg'], 50)
            delta = [view['position'][i]-view['target'][i] for i in range(3)]
            self.assertAlmostEqual(view['distance_m'], math.hypot(*delta))
            self.assertGreater(view['distance_m'], 20)
        self.assertAlmostEqual(scene['views'][0]['position'][0], 0)
        self.assertGreater(scene['views'][0]['position'][2], 0)

    def test_stage_layouts_fit_inside_field_and_keep_human_scale(self):
        for layout in ('end', 'thrust', 'center'):
            for width in (4, 81.2):
                for depth in (3, 60):
                    with self.subTest(layout=layout, width=width, depth=depth):
                        self.spec['stage'].update(layout=layout, width=width, depth=depth)
                        scene = build_scene(self.spec)
                        for mesh in scene['meshes']:
                            if mesh['name'].startswith('stage-'):
                                for x, _, z in mesh['vertices']:
                                    self.assertLessEqual((x/58)**2+(z/86)**2, 1)
                        person = [p for m in scene['meshes'] if m['name'].startswith('performer-')
                                  for p in m['vertices']]
                        self.assertAlmostEqual(max(p[1] for p in person)-min(p[1] for p in person), 1.75)

    def test_radii_and_stage_extremes_fit(self):
        for rx, ry in ((20,20), (20,200), (200,20), (200,200)):
            for layout in ('end','thrust','center'):
                self.spec['bowl'].update(radius_x=rx,radius_y=ry)
                self.spec['stage'].update(width=min(100,rx*1.4),depth=min(60,ry*.7),layout=layout)
                scene = build_scene(self.spec)
                for mesh in scene['meshes']:
                    if mesh['name'].startswith('stage-'):
                        for x, _, z in mesh['vertices']:
                            self.assertLessEqual((x/rx)**2+(z/ry)**2, 1)

    def test_floor_and_terraces_face_up(self):
        scene = build_scene(self.spec)
        for mesh in scene['meshes']:
            if mesh['name']=='infield' or mesh['name'].endswith(('-terraces','-aisles')):
                for face in mesh['faces']:
                    a,b,c = [mesh['vertices'][index] for index in face[:3]]
                    normal_y = (b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2])
                    self.assertGreater(normal_y, 0)

    def test_invalid_numeric_and_unknown_fields_are_rejected(self):
        for bad in (None, True, '58', float('nan'), float('inf'), -10, 1e100, 10**400):
            with self.subTest(bad=bad):
                spec = copy.deepcopy(self.spec)
                spec['bowl']['radius_x'] = bad
                with self.assertRaises(SpecError):
                    build_scene(spec)
        for field, value in [('row',0),('tier',3),('azimuth_deg',900),('row',2.5)]:
            spec=copy.deepcopy(self.spec)
            spec['views'][0][field]=value
            with self.assertRaises(SpecError):
                build_scene(spec)
        self.spec['bowl']['roof']='something'
        with self.assertRaises(SpecError):
            build_scene(self.spec)

    def test_evidence_must_support_verified_claims(self):
        self.spec['kind']='researched'
        with self.assertRaises(SpecError):
            validate_spec(self.spec)
        self.spec['sources']=[dict(title='Example', url='https://example.org/venue', accessed='2026-11-14')]
        self.spec['evidence'][0]['status']='verified'
        with self.assertRaises(SpecError):
            validate_spec(self.spec)
        self.spec['evidence'][0]['source_url']='https://example.org/venue'
        validate_spec(self.spec)
        self.spec['evidence'][0]['source_url']='javascript:alert(1)'
        with self.assertRaises(SpecError):
            validate_spec(self.spec)

    def test_unexplained_geometry_and_duplicate_views_rejected(self):
        self.spec['assumptions']=[]
        self.spec['evidence']=[]
        with self.assertRaises(SpecError):
            validate_spec(self.spec)
        self.setUp()
        self.spec['views'][1]['id']=self.spec['views'][0]['id']
        with self.assertRaises(SpecError):
            validate_spec(self.spec)

    def test_tier_order_rejected(self):
        self.spec['bowl']['tiers'][1]['base_height']=5
        with self.assertRaises(SpecError):
            build_scene(self.spec)

    def test_maximum_row_count_stays_within_mesh_budget(self):
        self.spec['bowl']['tiers']=[dict(rows=60,row_depth=.45,row_rise=.1,base_height=i*8,gap_before=0)
                                    for i in range(4)]
        scene=build_scene(self.spec)
        self.assertLessEqual(sum(len(m['faces']) for m in scene['meshes']),50000)

    def test_model_is_deterministic(self):
        before=copy.deepcopy(self.spec)
        self.assertEqual(build_scene(self.spec), build_scene(self.spec))
        self.assertEqual(self.spec, before)


if __name__ == '__main__':
    unittest.main()
