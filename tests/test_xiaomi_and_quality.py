import ipaddress
import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
READMES = ('README.md', 'README.en.md', 'README.zh-CN.md', 'README.ko.md', 'README.ja.md')


def cases():
    return {c['id']: c for c in json.loads((ROOT / 'examples/observations.json').read_text())['cases']}


def anchors(text):
    # GitHub-style heading slugs for the headings used by this repository.
    text = re.sub(r'```.*?```', '', text, flags=re.S)
    found, counts = set(), {}
    for heading in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', text, re.M):
        heading = re.sub(r'\[([^]]+)\]\([^)]*\)', r'\1', heading)
        slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        found.add(slug if count == 0 else f'{slug}-{count}')
    found.update(re.findall(r'<a\s+(?:id|name)=["\']([^"\']+)', text))
    return found


class XiaomiAndQualityTests(unittest.TestCase):
    def test_locked_selfcheck_serving_boundary(self):
        c = cases()['xiaomi-locked-serving-self-check']
        self.assertEqual((c['android'], c['api_level'], c['version']), (16, 36, '0.1.44'))
        self.assertTrue(c['serving_helper_rpc_tested'])
        self.assertFalse(c['root_available'])
        self.assertFalse(c['app_ai_e2e_tested'])
        self.assertTrue(c['device_locked'] and c['device_secure'])
        self.assertFalse(c['global_interactive'])
        self.assertEqual(c['self_check'], {'pass': 12, 'partial': 0, 'fail': 0, 'skipped': 0,
                                         'seconds': 42, 'changing_frame_and_tree_seconds': 15})
        self.assertTrue(all(c['cleanup'].values()))
        self.assertIn('NoSuchMethodException', c['initial_failure'])

    def test_telegram_separate_path_and_one_send(self):
        c = cases()['xiaomi-locked-telegram-saved-message']
        self.assertFalse(c['serving_helper_rpc_tested'])
        self.assertFalse(c['app_ai_e2e_tested'])
        self.assertFalse(c['message_body_published'])
        self.assertEqual((c['send_invocations'], c['send_retries']), (1, 0))
        self.assertIn('own Saved Messages', c['destination'])
        self.assertIn('not another person', c['seen_interpretation'])
        self.assertTrue(c['cleanup']['composer_empty'])
        self.assertTrue(c['cleanup']['sent_message_retained'])
        self.assertIn('not recorded', c['target_app_version'])

    def test_xiaomi_cleanup_and_sampling_limits(self):
        for key in ('xiaomi-locked-serving-self-check', 'xiaomi-locked-telegram-saved-message'):
            c = cases()[key]
            self.assertEqual(c['observed_on'], '2026-11-17')
            self.assertTrue(c['main_task_unchanged_at_samples'])
            self.assertFalse(c['continuous_physical_state_trace'])
            self.assertTrue(c['cleanup']['task_restored_background_before_display_close'])
            self.assertTrue(c['cleanup']['only_physical_display_remaining'])
            for limit in ('overnight_idle', 'reboot_recovery', 'roaming', 'continuous_focus_trace'):
                self.assertIn(limit, c['not_tested'])

    def test_historical_failures_remain(self):
        c = cases()
        self.assertIn('samsung-root', c)
        self.assertIn('xiaomi-locked-native', c)
        self.assertIn('xiaomi-paired-helper-recovery', c)
        self.assertTrue(c['pixel17-locked-serving-semantic']['probe_coordinate_tap'].startswith('FAIL'))
        self.assertFalse(c['a32-root-bootstrap-system-screen-off']['secure_keyguard_tested'])

    def test_xiaomi_localized_entrypoints(self):
        for name in READMES:
            text = (ROOT / name).read_text()
            self.assertIn('(docs/xiaomi-pad-mini-android16.md)', text, name)
            self.assertIn('(docs/acceptance-matrix.md)', text, name)
            self.assertIn('12/12', text, name)
            self.assertIn('Saved Messages', text, name)
            self.assertIn('42', text, name)

    def test_device_guide_keeps_failures_and_boundaries(self):
        text = (ROOT / 'docs/xiaomi-pad-mini-android16.md').read_text()
        for marker in ('NoSuchMethodException', 'root=null', 'one accessibility connection',
                       'not a model-AI workflow', 'before display release',
                       'not proof that another person', 'Source-copy rollback'):
            self.assertIn(marker, text)
        self.assertNotIn('100% reliable', text)

    def test_acceptance_matrix_distinguishes_durations(self):
        text = (ROOT / 'docs/acceptance-matrix.md').read_text()
        for marker in ('42 seconds', '15 seconds', '90 seconds', '308.7 seconds',
                       'not a single boolean', 'before the first unlock', 'documentation tests are not device tests'):
            self.assertIn(marker, text)

    def test_all_local_markdown_links_and_fragments(self):
        for path in ROOT.rglob('*.md'):
            for link in re.findall(r'\]\(([^\s)]+)\)', path.read_text()):
                if '://' in link or link.startswith('mailto:'):
                    continue
                target, _, fragment = unquote(link).partition('#')
                resolved = (path.parent / target).resolve() if target else path
                self.assertTrue(resolved.is_relative_to(ROOT), (path, link))
                self.assertTrue(resolved.exists(), (path, link))
                if fragment and resolved.suffix == '.md':
                    self.assertIn(fragment, anchors(resolved.read_text()), (path, link))

    def test_public_fixtures_have_no_contact_message_or_private_network(self):
        paths = [*ROOT.glob('*.md'), *ROOT.glob('docs/*.md'), *ROOT.glob('examples/*.json')]
        forbidden = [r'https?://[^\s)]+\.ts\.net', r'/pair#code=',
                     r'(?i)"(?:message_body|message_text|recipient_phone|contact_name|serial|token|nonce)"\s*:',
                     r'(?i)-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
                     r'\b(?:RF|MZF)[A-Z0-9]{8,}\b']
        for path in paths:
            text = path.read_text()
            for pattern in forbidden:
                self.assertIsNone(re.search(pattern, text), (path, pattern))
            for value in re.findall(r'(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])', text):
                try:
                    address = ipaddress.ip_address(value)
                except ValueError:
                    continue
                self.assertTrue(address.is_loopback or str(address) == '0.0.0.0', (path, value))

    def test_no_private_runtime_artifacts(self):
        for path in ROOT.rglob('*'):
            if '.git' in path.parts or '__pycache__' in path.parts:
                continue
            if path.is_file():
                self.assertNotIn(path.suffix.lower(), {'.apk', '.dex', '.png', '.jpg', '.jpeg', '.pem', '.p12'}, path)
            self.assertNotEqual(path.name, 'private', path)

    def test_ci_actions_pinned_and_read_only(self):
        text = (ROOT / '.github/workflows/docs.yml').read_text()
        uses = re.findall(r'uses:\s*(\S+)', text)
        self.assertEqual(len(uses), 2)
        self.assertTrue(all(re.fullmatch(r'actions/(?:checkout|setup-python)@[0-9a-f]{40}', value) for value in uses))
        self.assertIn('contents: read', text)
        self.assertIn('persist-credentials: false', text)
        self.assertIn('python3 -m unittest discover -s tests -v', text)
        self.assertNotIn('secrets.', text)
        self.assertNotIn('pull_request_target', text)


if __name__ == '__main__':
    unittest.main()
