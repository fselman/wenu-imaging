"""Synthetic regression for external-prefix selection; no Conda or ASDF execution."""
import json
from pathlib import Path
import runpy
import tempfile
import unittest

runner = runpy.run_path(str(Path(__file__).with_name('qualify_libasdf_mac.py')))


class PrefixTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix='asdf-prefix-case-'))
        print('RETAINED PREFIX CASE:', self.root)
        self.old = self.root / 'old'; self.old.mkdir()
        self.work = self.root / 'new'; self.work.mkdir()
        self.prefix = self.old / 'libasdf-environment'
        for name in ('include/asdf.h', 'lib/pkgconfig/libasdf.pc', 'bin/pkgconf'):
            path = self.prefix / name
            path.parent.mkdir(parents=True, exist_ok=True); path.write_text('fixture')
        (self.prefix / 'conda-meta').mkdir()
        self.write(self.prefix / 'conda-meta/libasdf.json', dict(name='libasdf', version='0.3.0', build='test_0'))
        self.write(self.old / 'libasdf-packages.log', [dict(name='libasdf', version='0.3.0', build_string='test_0')])
        self.write(self.old / 'qc-qualification.json', dict(revision='ad42ef7a2795f1420b131e4c0df4feae53b5ed6c',
            preservation=dict(checkout=True, installed_files=True, exported_source=True)))
        self.native = dict(prefix=str(self.prefix), libasdf='0.3.0', commands=[dict(label=label, exit_status=0)
            for label in ('conda-platform', 'libasdf-plan', 'libasdf-create', 'libasdf-packages',
                          'libasdf-explicit', 'libasdf-link-flags')])
        self.write(self.old / 'libasdf-qualification.json', self.native)

    def write(self, path, value):
        path.write_text(json.dumps(value))

    def test_compiler_gets_paths_when_pkgconf_omits_them(self):
        # Reproduce the actual Mac flags; paths with spaces stay single argv entries.
        prefix = self.root / 'prefix with spaces'
        flags = ['-D_THREAD_SAFE', '-pthread', '-lasdf', '-lpthread', '-lfyaml']
        argv = runner['compiler_command']('clang', '/sdk', 'fixture.c', 'probe', prefix, flags)
        self.assertIn('-I' + str(prefix / 'include'), argv)
        self.assertIn('-L' + str(prefix / 'lib'), argv)
        self.assertLess(argv.index('-L' + str(prefix / 'lib')), argv.index('-lasdf'))
        self.assertIn('-Wl,-rpath,' + str(prefix / 'lib'), argv)
        self.assertEqual(argv[argv.index('-lasdf'):argv.index('-lasdf') + 3], flags[-3:])

    def test_reuse_accepts_complete_and_rejects_incomplete_or_mismatched(self):
        # Verify the previous failed compilation can be reused only after provisioning passed.
        self.assertEqual(runner['retained_prefix'](self.old, self.work), self.prefix)
        self.native['commands'][2]['exit_status'] = 1
        self.write(self.old / 'libasdf-qualification.json', self.native)
        with self.assertRaisesRegex(RuntimeError, 'incomplete'):
            runner['retained_prefix'](self.old, self.work)
        self.native['commands'][2]['exit_status'] = 0
        self.write(self.old / 'libasdf-qualification.json', self.native)
        self.write(self.prefix / 'conda-meta/libasdf.json', dict(name='libasdf', version='0.4.0', build='test_0'))
        with self.assertRaisesRegex(RuntimeError, 'metadata differs'):
            runner['retained_prefix'](self.old, self.work)

    def test_preservation_detects_content_and_symlink_changes(self):
        # Prefix fingerprints must detect writes without following external directory links.
        link = self.prefix / 'external'; link.symlink_to(self.work, target_is_directory=True)
        before = runner['prefix_identity'](self.prefix)
        (self.work / 'outside').write_text('not part of prefix')
        self.assertEqual(before, runner['prefix_identity'](self.prefix))
        (self.prefix / 'include/asdf.h').write_text('changed')
        self.assertNotEqual(before, runner['prefix_identity'](self.prefix))


if __name__ == '__main__':
    unittest.main(verbosity=2)
