"""Observable packaging and untrusted-input regression checks."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/seat-view/scripts'))
from build import build


class BuildTests(unittest.TestCase):
    def test_offline_package_and_preserved_input(self):
        original = ROOT / 'skills/seat-view/assets/demo-venue.json'
        with tempfile.TemporaryDirectory() as folder:
            index = build(original, folder)
            self.assertEqual({p.name for p in index.parent.iterdir()}, {'index.html', 'scene.json', 'venue.json', 'brief.md'})
            self.assertEqual(json.loads(original.read_text()), json.loads((index.parent / 'venue.json').read_text()))
            self.assertNotIn('/*__', index.read_text())
            self.assertIn('SPDX-License-Identifier: MIT', index.read_text())
            with self.assertRaisesRegex(ValueError, 'preserve existing work'):
                build(original, folder)

    def test_names_cannot_close_embedded_json_script(self):
        spec = json.loads((ROOT / 'skills/seat-view/assets/demo-venue.json').read_text())
        attack = '</script><script>window.injected=true</script>'
        spec['name'] = attack
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'attack.json'
            source.write_text(json.dumps(spec))
            index = build(source, Path(folder) / 'out')
            self.assertNotIn(attack, index.read_text())
            self.assertEqual(json.loads((index.parent / 'venue.json').read_text())['name'], attack)

    def test_invalid_scene_does_not_leave_deliverables(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'invalid.json'
            source.write_text('{}')
            with self.assertRaises(ValueError):
                build(source, Path(folder) / 'out')
            self.assertFalse((Path(folder) / 'out').exists())


if __name__ == '__main__':
    unittest.main()
