"""Check config preservation, role restrictions, backups, and installation flow."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import setup_opencode as setup


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / 'config'
        self.directory.mkdir()

    def write(self, name, data):
        path = self.directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data)
        return path

    def test_jsonc_strings_comments_and_trailing_commas(self):
        path = self.write('settings.jsonc', '''{
            // keep URLs and escaped quotes
            "url": "https://example.com/*path*/", /* comment */
            "escaped": "a\\\"b", "list": ["comma,}",],
        }''')
        result = setup.read_jsonc(path)
        self.assertEqual(result['url'], 'https://example.com/*path*/')
        self.assertEqual(result['escaped'], 'a"b')
        self.assertEqual(result['list'], ['comma,}'])

    def test_preserve_models_and_unrelated_settings(self):
        original = {'preset': 'mine', 'companion': {'enabled': True},
                    'disabled_agents': ['oracle', 'designer'],
                    'presets': {'mine': {'oracle': {'model': 'provider/choice', 'variant': 'custom'},
                                        'helper': {'model': 'provider/helper'}}},
                    'council': {'presets': {'panel': {'alpha': {'model': 'provider/alpha'}}}}}
        before = copy.deepcopy(original)
        config = setup.configure(original, 'preserve')
        self.assertEqual(original, before)
        oracle = config['presets']['mine']['oracle']
        self.assertEqual(oracle['model'], 'provider/choice')
        self.assertEqual(oracle['variant'], 'custom')
        self.assertEqual(config['companion'], original['companion'])
        self.assertNotIn('oracle', config['disabled_agents'])
        self.assertTrue({'helper', 'designer', 'observer', 'council', 'councillor-alpha'}
                        <= set(config['disabled_agents']))
        for block in [config['agents'], config['presets']['mine']]:
            for role in ('explorer', 'librarian', 'fixer', 'oracle'):
                self.assertEqual(block[role]['permission']['task'], 'deny')
            for role in ('explorer', 'librarian', 'oracle'):
                self.assertEqual(block[role]['permission']['edit'], 'deny')
        self.assertEqual(oracle['permission']['bash'], 'allow')

    def test_profiles_match_catalog_and_remove_stale_effort(self):
        catalog = {m['id']: m for m in json.loads((setup.SETUP / 'go-catalog.json').read_text())['models']}
        for profile in ('recommended', 'alternative'):
            config = setup.configure({}, profile)
            agents = config['presets'][config['preset']]
            self.assertEqual(set(agents), set(setup.ROLES))
            for agent in agents.values():
                model = catalog[agent['model']]
                if 'variant' in agent:
                    self.assertIn(agent['variant'], model['variants'])
            self.assertTrue(catalog[agents['orchestrator']['model']]['image_input'])
        config = {'presets': {'skills-go-recommended': {'oracle': {'variant': 'bogus', 'options': {'old': True}}}}}
        result = setup.configure(config, 'recommended')['presets']['skills-go-recommended']['oracle']
        self.assertNotIn('variant', result)
        self.assertNotIn('options', result)

    def test_managed_prompts_keep_user_text(self):
        first = setup.managed_prompt('User instruction\n', 'Version one')
        second = setup.managed_prompt(first, 'Version two')
        self.assertIn('User instruction', second)
        self.assertNotIn('Version one', second)
        self.assertEqual(second.count(setup.START), 1)
        self.assertEqual(setup.managed_prompt(second, 'Version two'), second)
        with self.assertRaises(ValueError):
            setup.managed_prompt(setup.START, 'new')

    def test_legacy_root_models_are_preserved(self):
        config = setup.configure({'agents': {'orchestrator': {'model': 'my/provider', 'variant': 'chosen'}}}, 'preserve')
        root = config['presets'][config['preset']]['orchestrator']
        self.assertEqual(root['model'], 'my/provider')
        self.assertEqual(root['variant'], 'chosen')

    def test_apply_plan_backups_and_idempotence(self):
        old = self.write('skills/orchestrate/SKILL.md', 'local old skill\n')
        old.chmod(0o640)
        prompt = self.write('oh-my-opencode-slim/opencode-go/oracle_append.md', 'User advice\n')
        self.write('oh-my-opencode-slim.jsonc', '{"preset":"opencode-go","presets":{"opencode-go":{}}}')
        self.write('oh-my-opencode-slim.json', '{"unused_lower_priority":true}')
        updates, _ = setup.plan(self.directory, 'preserve')
        writer = setup.Writer(self.directory)
        for path, data in updates.items():
            writer.write(path, data)
        self.assertEqual((writer.backup / 'skills/orchestrate/SKILL.md').read_text(), 'local old skill\n')
        self.assertEqual(old.stat().st_mode & 0o777, 0o640)
        self.assertIn('User advice', prompt.read_text())
        self.assertIn(str(self.directory / 'skills/orchestrate'), prompt.read_text())
        self.assertEqual(json.loads((self.directory / 'oh-my-opencode-slim.json').read_text()),
                         {'unused_lower_priority': True})
        repeated, _ = setup.plan(self.directory, 'preserve')
        self.assertEqual(repeated, {})

    def test_plugin_pin_preserves_order_and_other_plugins(self):
        self.write('opencode.json', json.dumps({'plugin': ['before', 'oh-my-opencode-slim', 'after'],
                                               'provider': {'custom': {'setting': True}}}))
        updates = setup.pin_plugin(self.directory)
        value = json.loads(next(iter(updates.values())))
        self.assertEqual(value['plugin'], ['before', 'oh-my-opencode-slim@3.0.3', 'after'])
        self.assertEqual(value['provider'], {'custom': {'setting': True}})

    def test_dry_run_creates_no_files_or_process(self):
        self.directory.rmdir()
        command = [sys.executable, str(setup.REPO / 'scripts/setup_opencode.py'),
                   '--config-dir', str(self.directory), '--install-plugin']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('No files changed', result.stdout)
        self.assertFalse(self.directory.exists())

    def test_native_install_flow_and_failed_install_backup(self):
        core = self.write('opencode.json', '{"plugin":["unrelated"]}')
        argv = ['setup_opencode.py', '--config-dir', str(self.directory), '--install-plugin', '--apply']
        def install(command, env, check):
            self.assertIn('--background-subagents=no', command)
            self.assertEqual(env['OPENCODE_CONFIG_DIR'], str(self.directory))
            self.write('oh-my-opencode-slim.json', '{"preset":"opencode-go","presets":{"opencode-go":{}}}')
        with patch.object(sys, 'argv', argv), patch.object(setup.shutil, 'which', return_value='/fake/tool'), \
             patch.object(setup.subprocess, 'run', side_effect=install):
            setup.main()
        self.assertIn('oh-my-opencode-slim@3.0.3', json.loads(core.read_text())['plugin'])
        self.assertEqual((self.directory / 'run-opencode').stat().st_mode & 0o777, 0o755)
        self.assertTrue(list((self.directory / '.backups/skills-setup').glob('*/opencode.json')))
        with patch.object(sys, 'argv', argv), patch.object(setup.shutil, 'which', return_value='/fake/tool'), \
             patch.object(setup.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, ['installer'])):
            with self.assertRaises(SystemExit):
                setup.main()

    def test_rejects_invalid_presets_and_symlinks(self):
        with self.assertRaises(ValueError):
            setup.configure({'preset': '../escape', 'presets': {'../escape': {}}}, 'preserve')
        target = self.write('target', 'original')
        link = self.directory / 'linked'
        link.symlink_to(target)
        with self.assertRaises(ValueError):
            setup.Writer(self.directory).write(link, b'replacement')
        self.assertEqual(target.read_text(), 'original')


if __name__ == '__main__':
    unittest.main()
