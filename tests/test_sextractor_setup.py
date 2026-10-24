"""Executable discovery regressions for the notebook 05 PAPI wrapper."""
import sys
import os
import tempfile
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Pycavi2"))
from pycavi.papi import papi_sextractor as wrapper


class SExtractorSetupTests(unittest.TestCase):
    def process(self, banner):
        process = Mock()
        process.communicate.return_value = (banner, None)
        return process

    def test_chapman_banner_is_found_through_sex_fallback(self):
        banners = [b"source-extractor: command not found",
                   b"sextractor: command not found",
                   b"\n         SExtractor  version 2.19.5 (2014-03-19)\n"]
        with patch.object(wrapper.subprocess, "Popen",
                          side_effect=[self.process(b) for b in banners]) as launch:
            self.assertEqual(wrapper.SExtractor().setup(), ("sex", b"2.19.5"))
        self.assertEqual([call.args[0] for call in launch.call_args_list],
                         ["source-extractor", "sextractor", "sex"])

    def test_explicit_path_accepts_both_banner_spellings(self):
        for banner in (b"SExtractor version 2.19.5 (2014-03-19)",
                       b"Source Extractor version 2.25.0"):
            with self.subTest(banner=banner), patch.object(
                    wrapper.subprocess, "Popen", return_value=self.process(banner)) as launch:
                program, version = wrapper.SExtractor().setup("/opt/tools/sex")
                self.assertEqual(program, "/opt/tools/sex")
                self.assertIn(version, (b"2.19.5", b"2.25.0"))
                self.assertEqual(launch.call_count, 1)

    def test_existing_source_extractor_banner_retains_first_candidate(self):
        with patch.object(wrapper.subprocess, "Popen", return_value=self.process(
                b"Source Extractor version 2.25.0")) as launch:
            self.assertEqual(wrapper.SExtractor().setup(),
                             ("source-extractor", b"2.25.0"))
            self.assertEqual(launch.call_count, 1)

    def test_unrelated_version_banner_is_rejected(self):
        with patch.object(wrapper.subprocess, "Popen", return_value=self.process(
                b"Other software version 2.19.5")):
            with self.assertRaisesRegex(wrapper.SExtractorException, "Cannot find"):
                wrapper.SExtractor().setup("/opt/tools/other")

    def test_recognized_banner_without_version_is_rejected(self):
        with patch.object(wrapper.subprocess, "Popen", return_value=self.process(
                b"SExtractor help")):
            with self.assertRaisesRegex(wrapper.SExtractorException, "Cannot determine"):
                wrapper.SExtractor().setup("/opt/tools/sex")

    def test_notebook_helper_passes_thread_limit_to_native_command(self):
        from pycavi.pycavi import pycavi_astromatic_tools as tools

        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)

            def native_command(command):
                self.assertIn(" -NTHREADS 1 ", command)
                self.assertIn("DETECT_THRESH", (work / "py-sextractor.sex").read_text())
                (work / "py-sextractor.cat").write_bytes(b"test catalogue")
                return 1  # Existing PAPI runCmd success convention.

            try:
                with patch.object(wrapper.SExtractor, "setup", return_value=("sex", b"2.19.5")), \
                     patch.object(wrapper.papi_misc_utils, "runCmd", side_effect=native_command):
                    result = tools.run_sextractor_on_target(
                        str(work / "input.fits"), str(work),
                        {"DETECT_THRESH": 10, "NTHREADS": 1})
                self.assertNotIn("NTHREADS", result.config)
                self.assertEqual(result.ext_config["NTHREADS"], 1)
                self.assertEqual((work / "input.cat").read_bytes(), b"test catalogue")
                self.assertEqual(Path.cwd(), original_cwd)
                self.assertEqual(wrapper.SExtractor().ext_config, {})
            finally:
                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
