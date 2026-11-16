import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class DocumentationTests(unittest.TestCase):
    def test_relative_links(self):
        for path in ROOT.rglob('*.md'):
            for link in re.findall(r'\]\(([^\s)]+)\)', path.read_text()):
                if '://' not in link and not link.startswith(('#', 'mailto:')):
                    self.assertTrue((path.parent / link.split('#')[0]).exists(), (path, link))

    def test_observation_ids_unique(self):
        data = json.loads((ROOT / 'examples/observations.json').read_text())
        ids = [case['id'] for case in data['cases']]
        self.assertEqual(len(ids), len(set(ids)))

    def test_public_hygiene(self):
        forbidden = [r'/Users/[^/]+/', r'\badb-[A-Za-z0-9]{8,}-', r'(?i)Bearer\s+[A-Za-z0-9_-]{16,}']
        for path in [*ROOT.glob('*.md'), *ROOT.glob('docs/*.md'), *ROOT.glob('examples/*.json')]:
            text = path.read_text()
            self.assertNotIn('\u2014', text, path)
            for pattern in forbidden:
                self.assertIsNone(re.search(pattern, text), (path, pattern))

    def test_pixel_localized_entrypoints(self):
        for name in ('README.md', 'README.en.md', 'README.zh-CN.md', 'README.ko.md', 'README.ja.md'):
            self.assertIn('(docs/pixel-android17.md)', (ROOT / name).read_text())

    def test_pixel_boundaries(self):
        cases = {c['id']: c for c in json.loads((ROOT / 'examples/observations.json').read_text())['cases']}
        locked = cases['pixel17-locked-serving-semantic']
        parallel = cases['pixel17-unlocked-parallel-whatsapp']
        self.assertTrue(locked['device_locked'])
        self.assertTrue(locked['serving_mcp_tested'])
        self.assertTrue(locked['probe_coordinate_tap'].startswith('FAIL'))
        self.assertIn('locked_third_party_apps', locked['not_tested'])
        self.assertFalse(parallel['device_locked'])
        self.assertFalse(parallel['continuous_focus_trace'])
        self.assertFalse(parallel['wireless_settings_changed'])
        self.assertFalse(parallel['app_restart_used'])
        self.assertIn('onTop=false', parallel['task_restore'])

if __name__ == '__main__':
    unittest.main()
