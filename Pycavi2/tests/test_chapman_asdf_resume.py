"""Synthetic evidence-reuse guards; no Conda or target ASDF execution."""
import json
from pathlib import Path
import runpy
import tempfile
import unittest

reuse = runpy.run_path(str(Path(__file__).with_name('qualify_m5_asdf_chapman.py')))['reuse_completed_gates']


class ResumeTests(unittest.TestCase):
    def test_reuse_requires_original_preservation_and_identical_qc(self):
        root = Path(tempfile.mkdtemp(prefix='chapman-asdf-resume-'))
        print('RETAINED RESUME CASE:', root)
        old = root / 'old'; old.mkdir()
        run = root / 'new'; run.mkdir()
        source = run / 'source'; source.mkdir()
        prefix = old / 'libasdf-environment'
        for name in ('include/asdf.h', 'include/asdf/config.h', 'lib/pkgconfig/libasdf.pc', 'bin/pkgconf'):
            p = prefix / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text('fixture')
        (prefix / 'conda-meta').mkdir()
        (prefix / 'conda-meta/asdf.json').write_text(json.dumps(dict(name='libasdf', version='0.3.0', build='fixture0')))
        (old / 'libasdf-packages.log').write_text(json.dumps([dict(name='libasdf', version='0.3.0', build_string='fixture0')]))
        (old / 'libasdf-explicit.log').write_text('fixture package URL')
        names = ('Pycavi2/pycavi/pycavi/pycavi_qc.py', 'Pycavi2/pycavi/config/qc-schema-1.0.0.json',
                 'Pycavi2/tests/test_shared_qc.py')
        for name in names:
            for directory in (old / 'source', source):
                p = directory / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(name.encode())
        qc = dict(successful=True, tests=10, network_attempts=[])
        (old / 'qc').mkdir(); (old / 'qc/qc-contract-results.json').write_text(json.dumps(qc))
        previous = dict(revision='449220c3351a0e95649dfcbdb66873ed66422fc1', status='failed', actual_glibc='2.17',
            external_prefix=str(prefix), shared_qc=qc, preservation=dict(checkout=True, installed_files=True,
                production_packages=True, retained_python_environment=True, exported_source=True,
                external_prefix_after_install=True), commands=[dict(label=label, exit_status=0) for label in
                ('conda-platform', 'libasdf-plan', 'libasdf-create', 'libasdf-packages', 'libasdf-explicit',
                 'shared-qc', 'libasdf-link-flags')])
        report = old / 'chapman-qualification.json'; report.write_text(json.dumps(previous))
        def git(*parts):
            return parts[1].split(':', 1)[1].encode()
        result, controls, evidence = reuse(old, run, source, git)
        self.assertEqual(result, prefix); self.assertEqual(controls, qc)
        self.assertIn('qc_sha256', evidence)
        changed = source / names[0]; changed.write_text('changed')
        with self.assertRaisesRegex(RuntimeError, 'Changed QC source'):
            reuse(old, run, source, git)
        changed.write_bytes(names[0].encode())
        previous['preservation']['external_prefix_after_install'] = False
        report.write_text(json.dumps(previous))
        with self.assertRaisesRegex(RuntimeError, 'preservation mismatch'):
            reuse(old, run, source, git)


if __name__ == '__main__':
    unittest.main(verbosity=2)
