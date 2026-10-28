"""Synthetic completion/accounting checks for the focused #116 reader."""
import unittest
from descriptor_snapshots import PHASES
from repeat_bpm_bias_descriptor_case import observe


def balanced_log():
    rows = ["PASS: returned 9x9 mask good=79",
            "DESCRIPTOR LIMIT before soft=256 hard=10000 soft_unlimited=0",
            "DESCRIPTOR LIMIT after soft=10000 hard=10000 soft_unlimited=0",
            "BIAS RESULT supplied=1 pixels_unchanged=81 caller_released=1",
            "BPM RESULT native_exit=0 constructed=1 destroyed=1 builds=1 masks_released=1 mismatch=0 owner_live=0 mask_live=0"]
    for boundary in ("process-start", "after-context", "before-build", "after-build",
                     "after-mask-release", "after-context-release", "after-driver",
                     "after-purge", "after-second-purge"):
        rows += ["ACCOUNTING BEGIN " + boundary, "ACCOUNTING END " + boundary]
    # One stable descriptor: original signature calculation is independently explicit.
    cell = (((3 * 33 + 1) * 33 + 2) * 33 + 7) * 33 + 33188
    for phase in PHASES:
        rows += ["DESCRIPTOR DETAIL phase=%s fd=3 flags=1 dev=2 ino=7 mode=33188" % phase,
                 "DESCRIPTOR SET phase=%s count=1 identity=%d" % (phase, cell)]
    rows += ["DESCRIPTORS before=1 after=1 identity_equal=1",
             "CACHE DESCRIPTORS after-purge before=1 after=1 identity_equal=1",
             "CACHE DESCRIPTORS after-second-purge before=1 after=1 identity_equal=1"]
    return "\n".join(rows)


class FocusedObserverReader(unittest.TestCase):
    def test_balanced(self):
        self.assertEqual(observe(balanced_log(), 0)["findings"], [])

    def test_nonzero_exit_and_sanitizer_not_ignored(self):
        self.assertIn("Nonzero native exit", observe(balanced_log(), 86)["findings"])
        for diagnostic in ("ERROR: AddressSanitizer", "runtime error:"):
            self.assertIn("ASan/UBSan diagnostic", observe(balanced_log() + diagnostic, 0)["findings"])

    def test_missing_or_live_resource_observation_rejected(self):
        text = balanced_log()
        missing = text.replace("ACCOUNTING BEGIN after-purge", "OMITTED after-purge")
        self.assertTrue(observe(missing, 0)["findings"])
        live = text.replace("ACCOUNTING END after-purge",
                            "ALL_npointers 1\nALL_size 16\nRAM_alloc 16\nACCOUNTING END after-purge")
        self.assertTrue(observe(live, 0)["findings"])

    def test_missing_snapshot_or_owner_not_accepted(self):
        text = balanced_log()
        self.assertTrue(observe(text.replace("DESCRIPTOR SET phase=before", "OMITTED phase=before"), 0)["findings"])
        self.assertIn("Context/mask ownership contract failed",
                      observe(text.replace("destroyed=1", "destroyed=0"), 0)["findings"])

    def test_same_count_change_is_attributed(self):
        text = balanced_log()
        old = (((3 * 33 + 1) * 33 + 2) * 33 + 7) * 33 + 33188
        # Change inode at each post-call boundary, keeping the count unchanged.
        for phase in PHASES[1:]:
            text = text.replace("phase=%s fd=3 flags=1 dev=2 ino=7" % phase,
                                "phase=%s fd=3 flags=1 dev=2 ino=8" % phase)
            text = text.replace("phase=%s count=1 identity=%d" % (phase, old),
                                "phase=%s count=1 identity=%d" % (phase, old + 33))
        result = observe(text, 0)
        self.assertIn("Descriptor identity changed", result["findings"])
        self.assertEqual(result["descriptor_snapshots"]["changes"]["after-driver"][0]["after"]["ino"], 8)


if __name__ == "__main__":
    unittest.main()
