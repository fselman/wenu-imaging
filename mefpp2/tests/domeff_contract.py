"""Single-detector WFI screen flats through native admission and stacking."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import tempfile

from astropy.io import fits
import numpy as np


PROFILE = """
footprint_schema_version = 1
instrument = "wfi"
readout_id = "WFI:synthetic"
binning = [1, 1]
[[detector]]
id = "CCD-A"
amplifier = "L"
native_paf_chip = 1
reference_hdu = 1
enabled = true
raw_size = [6, 3]
[native.instrument.detectors.CHIP1]
prescan_x_min = {value = 6}
prescan_x_max = {value = 6}
overscan_x_min = {value = 6}
overscan_x_max = {value = 6}
trimreg_x_min = {value = 1}
trimreg_x_max = {value = 5}
trimreg_y_min = {value = 1}
trimreg_y_max = {value = 3}
gain = {value = 2.0}
ron = {value = 5.1}
"""


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(command, work, capture_writer):
    raw, controls, reduced = (work / name for name in ("raw", "controls", "reduced"))
    raw.mkdir()
    subprocess.run([command, "project", "init", "--name", "dome",
                    "--raw", str(raw), "--orchestration", str(controls),
                    "--reduced", str(reduced)], check=True)
    output = reduced / "cal/domeff"
    output.mkdir()
    (controls / "wfi-1x1.toml").write_text(PROFILE)
    listing = controls / "dome.list"
    paths = []
    for index, signal in enumerate((100, 200, 300, 10)):
        primary = fits.PrimaryHDU()
        primary.header["INSTRUME"] = "WFI"
        primary.header["HIERARCH ESO DPR TYPE"] = "FLAT,SCREEN"
        primary.header["FILTER"] = "B"
        image = np.full((3, 6), signal + 22, dtype=np.int16)
        image[:, -1] = 22
        path = raw / f"flat-{index}.fits"
        detectors = [fits.ImageHDU(image, name="CCD-A"), fits.ImageHDU(image, name="CCD-B")]
        if index == 1:
            detectors.reverse()
        fits.HDUList([primary, *detectors]).writeto(path)
        paths.append(path)
    listing.write_text("".join(f"{path}\tFLAT,SCREEN\n" for path in paths))
    hashes = [digest(path) for path in paths]

    recipe = f"""domeff_recipe_schema_version = 1
project = "project.toml"
detector_toml = "wfi-1x1.toml"
run = "cal/domeff"
[inputs]
list = "{listing}"
[flat]
detector = "CCD-A"
filter = "B"
filter_keyword = "FILTER"
use_prescan = false
use_overscan = true
reject_scan_low = 0
reject_scan_high = 0
minimum_frames = 3
frame_mean_low_adu = 50
frame_mean_high_adu = 500
clip_low_sigma = 3.0
clip_high_sigma = 3.0
normalization_region = [1, 5, 1, 3]
"""
    config = controls / "domeff.toml"
    args = [command, "cal", "domeff", "--config", config.name]
    config.write_text(recipe.replace('filter = "B"', 'filter = "wrong"'))
    invalid = subprocess.run(args, cwd=controls, text=True, capture_output=True)
    assert invalid.returncode != 0 and not list(output.iterdir()), invalid.stderr

    config.write_text(recipe)
    result = subprocess.run(args, cwd=controls, text=True, capture_output=True)
    assert result.returncode == 0, (result.stdout, result.stderr)
    [product] = output.glob("*.fits")
    with fits.open(product) as hdus:
        assert hdus[0].header["PRODCATG"] == "CALIB.MASTER_DOME_FLAT"
        assert len(hdus) == 2 and hdus[1].name == "CCD-A"
        assert hdus[1].header["ESO MPP QC FRMEDIAN"] == 200
        np.testing.assert_array_equal(hdus[1].data, np.ones((3, 5)))
    assert [digest(path) for path in paths] == hashes
    assert product.with_suffix(".log").is_file()
    if capture_writer:
        assert product.with_suffix(".asdf").read_text().splitlines() == ["1 1", "2 1", "1 1", "1 0"]
    else:
        import asdf
        with asdf.open(product.with_suffix(".asdf")) as archive:
            qc = archive.tree["qc"]
            assert qc["provenance"]["operation"] == "cal.domeff"
            assert qc["provenance"]["configuration"]["snapshot"] == recipe
            assert qc["file"]["sha256"] == digest(product)
            inputs = qc["embedded_input_records"]
            assert [entry["file"]["sha256"] for entry in inputs] == hashes
            assert [entry["detectors"][0]["source_hdu"] for entry in inputs] == [1, 2, 1, 1]
            statuses = qc["inputs"]
            assert [row["participation_by_detector"][0]["status"] for row in statuses] == [
                "used", "used", "used", "rejected",
            ]
    print("PASS: WFI dome admission, scan/trim, exact normalization, FITS and QC bindings")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--command", type=Path, required=True)
    parser.add_argument("--capture-writer", action="store_true")
    arguments = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="native-dome-") as directory:
        check(str(arguments.command.resolve()), Path(directory).resolve(), arguments.capture_writer)


if __name__ == "__main__":
    main()
