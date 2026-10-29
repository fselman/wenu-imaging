"""Read-only dependency metadata preflight; no installs or scientific imports."""
import importlib.metadata as md
import json
import os
import platform
import shutil
import sys
import tomllib

def collect():
    packages = {}
    names = ("pycavi", "numpy", "astropy", "asdf", "asdf-standard",
             "asdf-astropy", "PyYAML", "packaging", "attrs",
             "typing-extensions", "importlib-metadata", "zipp",
             "jmespath", "semantic-version", "pip", "setuptools")
    for name in names:
        try:
            dist = md.distribution(name)
            packages[name] = {"version": dist.version,
                              "location": str(dist.locate_file("")),
                              "requires_python": dist.metadata.get("Requires-Python")}
        except md.PackageNotFoundError:
            packages[name] = {"installed": False}
    try:
        libc = os.confstr("CS_GNU_LIBC_VERSION")
    except (ValueError, OSError, AttributeError):
        libc = "not available"
    parsed = tomllib.loads('[instrument]\nname = "WFI"\nexposure_s = 20.0\n')
    assert parsed["instrument"]["exposure_s"] == 20.0
    return {"host": platform.node(), "os": platform.platform(),
            "machine": platform.machine(), "libc": libc,
            "python": sys.executable, "version": sys.version,
            "prefix": sys.prefix, "base_prefix": sys.base_prefix,
            "tomllib": tomllib.__file__, "tomllib_smoke": "passed",
            "tools_on_path": {name: shutil.which(name) for name in
                              ("gcc", "g++", "clang", "cmake", "make", "conda")},
            "packages": packages,
            "scope": "metadata only; no scientific-package imports or installation"}

if __name__ == "__main__":
    print(json.dumps(collect(), indent=2))
