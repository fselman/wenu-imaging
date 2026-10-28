"""Parse per-descriptor observations for supplied-bias finding #116.

Compare the same fd/flags/device/inode/mode fields as the retained C gate.
Targets are explanatory only: no descriptor or runtime gets an exclusion.
"""
import ctypes
import re

PHASES = ("before", "after-driver", "after-purge", "after-second-purge")
FIELDS = ("fd", "flags", "dev", "ino", "mode")


def snapshots(output):
    # Completeness: one complete set per existing observation boundary.
    sets = re.findall(r"^DESCRIPTOR SET phase=(\S+) count=(\d+) identity=(\d+)$", output, re.M)
    rows = re.findall(r"^DESCRIPTOR DETAIL phase=(\S+) fd=(\d+) flags=(\d+) dev=(\d+) ino=(\d+) mode=(\d+)$", output, re.M)
    if len(sets) != 4 or {s[0] for s in sets} != set(PHASES):
        raise RuntimeError("Missing/duplicate descriptor set boundary")
    if any(row[0] not in PHASES for row in rows):
        raise RuntimeError("Unexpected descriptor detail boundary")
    result = {}
    mask = (1 << (8 * ctypes.sizeof(ctypes.c_ulong))) - 1
    for phase, count, identity in sets:
        entries = [dict(zip(FIELDS, map(int, row[1:]))) for row in rows if row[0] == phase]
        if len(entries) != int(count) or len({e["fd"] for e in entries}) != len(entries):
            raise RuntimeError("Incomplete/duplicate descriptor details: " + phase)
        # Independent readback: recompute the unchanged C aggregate signature.
        value = 0
        for entry in entries:
            cell = entry["fd"]
            for key in FIELDS[1:]:
                cell = (cell * 33 + entry[key]) & mask
            value = (value + cell) & mask
        if value != int(identity):
            raise RuntimeError("Descriptor details/signature disagree: " + phase)
        result[phase] = sorted(entries, key=lambda e: e["fd"])
    # Attribution: identify exact fields added, removed or changed at each boundary.
    baseline = {e["fd"]: e for e in result["before"]}
    changes = {}
    for phase in PHASES[1:]:
        current = {e["fd"]: e for e in result[phase]}
        changes[phase] = [dict(fd=fd, before=baseline.get(fd), after=current.get(fd))
                          for fd in sorted(set(baseline) | set(current))
                          if baseline.get(fd) != current.get(fd)]
    return dict(boundaries=result, changes=changes)
