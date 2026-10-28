"""Synthetic observer-log checks for #116; no native application execution."""
import unittest
from descriptor_snapshots import PHASES, snapshots


def log(change=None):
    lines = []
    for phase in PHASES:
        entries = [dict(fd=fd, flags=0, dev=1, ino=100 + fd, mode=33188) for fd in range(4)]
        if change and phase != "before":
            change(entries)
        value = 0
        for e in entries:
            cell = e["fd"]
            for field in ("flags", "dev", "ino", "mode"):
                cell = cell * 33 + e[field]
            value += cell
            lines.append("DESCRIPTOR DETAIL phase=%s fd=%d flags=%d dev=%d ino=%d mode=%d" %
                         (phase, e["fd"], e["flags"], e["dev"], e["ino"], e["mode"]))
        lines.append("DESCRIPTOR SET phase=%s count=%d identity=%d" % (phase, len(entries), value))
    return "\n".join(lines)


class DescriptorSnapshots(unittest.TestCase):
    def test_balanced_and_unordered(self):
        # Balanced identities must survive arbitrary log-line ordering.
        text = log()
        expected = snapshots(text)
        self.assertFalse(any(expected["changes"].values()))
        self.assertEqual(snapshots("\n".join(reversed(text.splitlines()))), expected)

    def test_same_count_replacement_identifies_field(self):
        # This models the observed same-count mismatch, without claiming its cause.
        result = snapshots(log(lambda e: e[3].update(ino=999)))
        for phase in PHASES[1:]:
            self.assertEqual(len(result["changes"][phase]), 1)
            change = result["changes"][phase][0]
            self.assertEqual(change["fd"], 3)
            self.assertEqual(change["before"]["ino"], 103)
            self.assertEqual(change["after"]["ino"], 999)

    def test_added_and_removed_descriptors(self):
        # Additions and closures require explicit attribution too.
        for mutate, side in ((lambda e: e.pop(), "after"),
                             (lambda e: e.append(dict(fd=7, flags=1, dev=2, ino=9, mode=4480)), "before")):
            with self.subTest(side=side):
                result = snapshots(log(mutate))
                self.assertIsNone(result["changes"]["after-driver"][0][side])

    def test_missing_and_duplicate_boundaries_rejected(self):
        # Missing observations cannot become a pass.
        text = log()
        with self.assertRaises(RuntimeError):
            snapshots("\n".join(l for l in text.splitlines() if "phase=after-purge" not in l))
        with self.assertRaises(RuntimeError):
            snapshots(text + "\n" + text.splitlines()[-1])

    def test_missing_duplicate_and_corrupted_details_rejected(self):
        # Cross-check the detail count and original aggregate signature.
        text = log()
        first = text.splitlines()[0]
        for damaged in (text.replace(first + "\n", "", 1), text + "\n" + first,
                        text.replace("ino=100", "ino=999", 1)):
            with self.subTest(damaged=damaged[:80]), self.assertRaises(RuntimeError):
                snapshots(damaged)


if __name__ == "__main__":
    unittest.main()
