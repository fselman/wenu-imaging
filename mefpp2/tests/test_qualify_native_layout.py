"""Executable dispatch regression for the private target runner (#193)."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from qualify_native_layout import selected_tool


class ToolInvocationTests(unittest.TestCase):
    def test_multicall_symlink_preserves_selected_entry_point(self):
        # Tiny executable: observe actual argv[0]-dependent dispatch, no native build.
        with tempfile.TemporaryDirectory(prefix="m4-tool-dispatch-") as root:
            root = Path(root)
            target = root / "multicall"
            target.write_text('#!/bin/sh\nprintf "%s\\n" "${0##*/}"\n')
            target.chmod(0o700)
            for name in ("ar", "ranlib"):
                with self.subTest(entry_point=name):
                    link = root / name
                    link.symlink_to(target.name)
                    output = subprocess.check_output([str(selected_tool(link))], text=True)
                    self.assertEqual(output.strip(), name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
