"""Exercise the production install template with synthetic runtime payloads only."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CMAKE, TEMPLATE = sys.argv[1:3]
del sys.argv[1:3]


class InstallContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='mefpp-install-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source'
        self.build = self.root / 'build'
        self.prefix = self.root / 'prefix'
        self.build.mkdir()
        # Fixture: deliberately synthetic bytes test installer policy, not BPM science.
        payload = {
            'ins/mef/config/mefpp.paf': b'template 1',
            'ins/mef/config/omegacam.paf': b'template 2',
            'ins/mef/config/wfi.paf': b'template 3',
            'LICENSE': b'mefpp license fixture',
            'qfits5/LICENSE': b'qfits license fixture',
        }
        for name, value in payload.items():
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value)
        for name in ('resources/OCAM_BPM_1x1.fits', 'resources/WFI_BPM_1x1.fits',
                     'source-sha256.txt', 'mefpp'):
            path = self.build / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'synthetic install payload ' + name.encode())
        (self.build / 'build-info.json').write_text(json.dumps({'schema_version': 1}))
        (self.build / 'mefpp-path-.cmake').write_text(
            'set(MEFPP_EXECUTABLE [==[' + str(self.build / 'mefpp') + ']==])\n')
        # Configuration: generate the actual production install script for fixtures.
        configure = self.root / 'configure.cmake'
        configure.write_text('\n'.join([
            'set(MEFPP_BUILD_RESOURCES ON)',
            f'set(MEFPP_BINARY_DIR [==[{self.build}]==])',
            f'set(MEFPP_SOURCE_DIR [==[{self.source}]==])',
            f'configure_file([==[{TEMPLATE}]==] [==[{self.root / "install.cmake"}]==] @ONLY)',
        ]))
        subprocess.run([CMAKE, '-P', str(configure)], check=True, capture_output=True)

    def install(self, destdir=None):
        env = os.environ.copy()
        env.pop('DESTDIR', None)
        if destdir:
            env['DESTDIR'] = str(destdir)
        return subprocess.run([CMAKE, f'-DCMAKE_INSTALL_PREFIX={self.prefix}',
                               '-DCMAKE_INSTALL_CONFIG_NAME=Release', '-P',
                               str(self.root / 'install.cmake')], env=env,
                              capture_output=True, text=True)

    def snapshot(self, root):
        return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in root.rglob('*') if p.is_file()}

    def test_complete_repeat_and_destdir(self):
        # Install/repeat: all ten payload/manifest files and identical repeated bytes.
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        before = self.snapshot(self.prefix)
        self.assertEqual(len(before), 10)
        manifest = json.loads((self.prefix / 'share/mefpp/build-manifest.json').read_text())
        self.assertEqual(len(manifest['installed_files']), 9)
        self.assertTrue(os.access(self.prefix / 'bin/mefpp', os.X_OK))
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual(before, self.snapshot(self.prefix))
        # Staging: apply DESTDIR once and retain the runtime prefix in provenance.
        stage = self.root / 'stage'
        result = self.install(stage)
        self.assertEqual(result.returncode, 0, result.stderr)
        staged = stage / str(self.prefix).lstrip('/')
        self.assertEqual(before, self.snapshot(staged))
        self.assertEqual(json.loads((staged / 'share/mefpp/build-manifest.json').read_text())
                         ['install_prefix'], str(self.prefix))

    def test_modified_file_is_preserved_before_any_copy(self):
        # Conflict: preserve a user edit and reject installation before copying.
        target = self.prefix / 'config/mefpp.paf'
        target.parent.mkdir(parents=True)
        target.write_text('user edit')
        before = self.snapshot(self.prefix)
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Preserving existing different file', result.stderr)
        self.assertEqual(before, self.snapshot(self.prefix))

    def test_symlink_is_preserved(self):
        # Symlink: reject an ancestor link without writing through it.
        elsewhere = self.root / 'elsewhere'
        elsewhere.mkdir()
        self.prefix.mkdir()
        (self.prefix / 'config').symlink_to(elsewhere, target_is_directory=True)
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Refusing symlink', result.stderr)
        self.assertEqual(list(elsewhere.iterdir()), [])
        self.assertFalse((self.prefix / 'bin').exists())

    def test_external_ancestor_alias_is_supported(self):
        # Platform alias: allow a symlink above the prefix, like macOS /var.
        physical = self.root / 'physical'
        physical.mkdir()
        alias = self.root / 'alias'
        alias.symlink_to(physical, target_is_directory=True)
        self.prefix = alias / 'new-parent/prefix'
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.snapshot(physical / 'new-parent/prefix')), 10)
        manifest = json.loads((self.prefix / 'share/mefpp/build-manifest.json').read_text())
        self.assertEqual(manifest['install_prefix'], str(self.prefix))

    def test_prefix_symlink_is_rejected(self):
        # Prefix link: resolving external ancestors must not allow a linked prefix.
        elsewhere = self.root / 'elsewhere'
        elsewhere.mkdir()
        self.prefix.symlink_to(elsewhere, target_is_directory=True)
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Refusing symlink', result.stderr)
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_missing_resource_rejects_before_copy(self):
        # Incomplete payload: require both BPM products before any installation.
        (self.build / 'resources/WFI_BPM_1x1.fits').unlink()
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Required build product missing', result.stderr)
        self.assertFalse(self.prefix.exists())

    def test_nondirectory_parent_rejects_before_copy(self):
        # Path conflict: reject a regular file where a parent directory is needed.
        self.prefix.mkdir()
        (self.prefix / 'static_cal').write_text('preserve')
        before = self.snapshot(self.prefix)
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('parent is not a directory', result.stderr)
        self.assertEqual(before, self.snapshot(self.prefix))


if __name__ == '__main__':
    unittest.main(verbosity=2)
