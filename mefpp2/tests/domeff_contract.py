"""Single-detector and mosaic WFI dome and sky flats through native stacking."""
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
id = "CCD-B"
amplifier = "L"
native_paf_chip = 2
reference_hdu = 2
enabled = true
raw_size = [6, 3]
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
[native.instrument.detectors.CHIP2]
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


def check(command, work, capture_writer, kind):
    operation = f"{kind}ff"
    classification = "FLAT,SCREEN" if kind == "dome" else "FLAT,SKY"
    raw, controls, reduced = (work / name for name in ("raw", "controls", "reduced"))
    raw.mkdir()
    subprocess.run([command, "project", "init", "--name", kind,
                    "--raw", str(raw), "--orchestration", str(controls),
                    "--reduced", str(reduced)], check=True)
    output = reduced / "cal" / operation
    output.mkdir()
    (controls / "wfi-1x1.toml").write_text(PROFILE)
    listing = controls / f"{kind}.list"
    paths = []
    for index, signal in enumerate((100, 200, 300, 10)):
        primary = fits.PrimaryHDU()
        primary.header["INSTRUME"] = "WFI"
        primary.header["HIERARCH ESO DPR TYPE"] = classification
        primary.header["FILTER"] = "B"
        image = np.full((3, 6), signal + 22, dtype=np.int16)
        image[:, -1] = 22
        path = raw / f"flat-{index}.fits"
        signal_b = 3 * signal // 2 if index < 3 else 150
        image_b = image.copy()
        image_b[:, :-1] = signal_b + 22
        detectors = [fits.ImageHDU(image, name="CCD-A"), fits.ImageHDU(image_b, name="CCD-B")]
        if index == 1:
            detectors.reverse()
        fits.HDUList([primary, *detectors]).writeto(path)
        paths.append(path)
    listing.write_text("".join(f"{path}\t{classification}\n" for path in paths))
    hashes = [digest(path) for path in paths]

    recipe = f"""{operation}_recipe_schema_version = 1
project = "project.toml"
detector_toml = "wfi-1x1.toml"
run = "cal/{operation}"
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
    config = controls / f"{operation}.toml"
    args = [command, "cal", operation, "--config", config.name]
    config.write_text(recipe.replace('filter = "B"', 'filter = "wrong"'))
    invalid = subprocess.run(args, cwd=controls, text=True, capture_output=True)
    assert invalid.returncode != 0 and not list(output.iterdir()), invalid.stderr

    config.write_text(recipe)
    result = subprocess.run(args, cwd=controls, text=True, capture_output=True)
    assert result.returncode == 0, (result.stdout, result.stderr)
    [product] = output.glob("*.fits")
    with fits.open(product) as hdus:
        assert hdus[0].header["PRODCATG"] == f"CALIB.MASTER_{kind.upper()}_FLAT"
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
            assert qc["provenance"]["operation"] == f"cal.{operation}"
            assert qc["provenance"]["configuration"]["snapshot"] == recipe
            assert qc["file"]["sha256"] == digest(product)
            inputs = qc["embedded_input_records"]
            assert [entry["file"]["sha256"] for entry in inputs] == hashes
            assert [entry["detectors"][0]["source_hdu"] for entry in inputs] == [1, 2, 1, 1]
            statuses = qc["inputs"]
            assert [row["participation_by_detector"][0]["status"] for row in statuses] == [
                "used", "used", "used", "rejected",
            ]
        check_mosaic(args, controls, reduced, config, recipe, hashes, asdf, operation)
    print(f"PASS: WFI {kind} admission, scan/trim, exact normalization, FITS and QC bindings")


def check_mosaic(args, controls, reduced, config, recipe, hashes, asdf, operation):
    output = reduced / "cal" / f"{operation}-mosaic"
    output.mkdir()
    # A mosaic must identify the sky or dome product independently of its filename.
    mosaic = recipe.replace('detector = "CCD-A"', 'detector = "all"')
    mosaic = mosaic.replace(f'run = "cal/{operation}"', f'run = "cal/{operation}-mosaic"')
    config.write_text(mosaic)
    result = subprocess.run(args, cwd=controls, text=True, capture_output=True)
    assert result.returncode == 0, (result.stdout, result.stderr)

    [product] = output.glob("*.fits")
    with fits.open(product) as hdus:
        kind = operation.removesuffix("ff")
        assert hdus[0].header["PRODCATG"] == f"CALIB.MASTER_{kind.upper()}_FLAT"
        assert hdus[0].header["NEXTEND"] == 2
        assert [hdu.name for hdu in hdus[1:]] == ["CCD-B", "CCD-A"]
        np.testing.assert_array_equal(hdus[1].data, np.full((3, 5), 1.3125))
        np.testing.assert_array_equal(hdus[2].data, np.ones((3, 5)))
        assert hdus[1].header["ESO MPP QC FRMEDIAN"] == 262.5
        assert hdus[2].header["ESO MPP QC FRMEDIAN"] == 200

    with asdf.open(product.with_suffix(".asdf")) as archive:
        qc = archive.tree["qc"]
        assert qc["provenance"]["configuration"]["snapshot"] == mosaic
        assert qc["file"]["sha256"] == digest(product)
        inputs = qc["embedded_input_records"]
        assert [entry["file"]["sha256"] for entry in inputs] == hashes
        for frame, source_hdus in zip(inputs, ((2, 1), (1, 2), (2, 1), (2, 1)), strict=True):
            assert [(d["detector_id"], d["source_hdu"]) for d in frame["detectors"]] == [
                ("CCD-B", source_hdus[0]), ("CCD-A", source_hdus[1]),
            ]
        assert [row["status"] for row in qc["inputs"][-1]["participation_by_detector"]] == [
            "used", "rejected",
        ]
    print("PASS: mosaic uses chip 1 illumination and writes catalogue order with per-detector QC")


def check_master_bias(command, work, kind):
    import asdf

    operation = f"{kind}ff"
    classification = "FLAT,SCREEN" if kind == "dome" else "FLAT,SKY"
    raw, controls, reduced = (work / name for name in ("raw", "controls", "reduced"))
    raw.mkdir()
    subprocess.run([command, "project", "init", "--name", operation,
                    "--raw", str(raw), "--orchestration", str(controls),
                    "--reduced", str(reduced)], check=True)
    (controls / "wfi-1x1.toml").write_text(PROFILE)
    output = reduced / "cal" / operation
    output.mkdir()
    bias_path = reduced / "cal/master-bias.fits"
    response = np.array([1, 2, 3, 2, 1], dtype=np.int16)
    biases = {"CCD-A": np.array([30, 4, 22, 12, 8], dtype=np.int16),
              "CCD-B": np.array([12, 30, 4, 22, 8], dtype=np.int16)}
    primary = fits.PrimaryHDU()
    primary.header["INSTRUME"] = "WFI"
    primary.header["PRODCATG"] = "CALIB.MASTER_BIAS"
    master = fits.HDUList([primary, *[
        fits.ImageHDU(np.tile(biases[name], (3, 1)), name=name)
        for name in ("CCD-A", "CCD-B")
    ]])
    for hdu in master[1:]:
        hdu.header["BUNIT"] = "ADU"
    master.writeto(bias_path)
    bias_hash = digest(bias_path)

    paths = []
    for index, level in enumerate((100, 200, 300, 20)):
        header = fits.PrimaryHDU()
        header.header["INSTRUME"] = "WFI"
        header.header["FILTER"] = "B"
        header.header["HIERARCH ESO DPR TYPE"] = classification
        planes = []
        for name in ("CCD-B", "CCD-A") if index % 2 else ("CCD-A", "CCD-B"):
            signal = level if name == "CCD-A" else (2 * level if index < 3 else 100)
            image = np.full((3, 6), 22, dtype=np.int16)
            image[:, :5] += biases[name] + signal * response
            planes.append(fits.ImageHDU(image, name=name))
        path = raw / f"flat-{index}.fits"
        fits.HDUList([header, *planes]).writeto(path)
        paths.append(path)
    hashes = [digest(path) for path in paths]
    listing = controls / f"{kind}.list"
    listing.write_text("".join(f"{path}\t{classification}\n" for path in paths))
    recipe = f"""{operation}_recipe_schema_version = 1
project = "project.toml"
detector_toml = "wfi-1x1.toml"
run = "cal/{operation}"
[inputs]
list = "{listing}"
master_bias = "master-bias.fits"
[flat]
detector = "all"
filter = "B"
filter_keyword = "FILTER"
use_prescan = false
use_overscan = true
reject_scan_low = 0
reject_scan_high = 0
minimum_frames = 3
frame_mean_low_adu = 50
frame_mean_high_adu = 2000
clip_low_sigma = 100.0
clip_high_sigma = 100.0
normalization_region = [1, 5, 1, 3]
"""
    config = controls / f"{operation}.toml"
    args = [command, "cal", operation, "--config", config.name]

    # Each rejected calibration uses a fresh path and must leave output empty.
    incompatible = []
    for key, value in (("PRODCATG", "CALIB.BPM"), ("INSTRUME", "OTHER")):
        copy = fits.HDUList([hdu.copy() for hdu in master])
        copy[0].header[key] = value
        incompatible.append(copy)
    copy = fits.HDUList([hdu.copy() for hdu in master])
    copy[1].header["EXTNAME"] = "CCD-B"
    incompatible.append(copy)
    copy = fits.HDUList([hdu.copy() for hdu in master])
    copy[1].data = np.zeros((3, 4), dtype=np.int16)
    incompatible.append(copy)
    for key, value in (("BUNIT", "electron"), ("HIERARCH ESO DET WIN1 BINX", 2)):
        copy = fits.HDUList([hdu.copy() for hdu in master])
        copy[1].header[key] = value
        incompatible.append(copy)
    copy = fits.HDUList([hdu.copy() for hdu in master])
    copy[1].data = copy[1].data.astype(np.float32)
    copy[1].data[0, 0] = np.nan
    nonfinite = reduced / "cal/nonfinite-bias.fits"
    copy.writeto(nonfinite)
    for index, bad in enumerate(incompatible):
        path = reduced / "cal" / f"bad-{index}.fits"
        bad.writeto(path)
        config.write_text(recipe.replace('"master-bias.fits"', f'"{path.name}"'))
        result = subprocess.run(args, cwd=controls, text=True, capture_output=True)
        assert result.returncode != 0 and not list(output.iterdir()), result
    for replacement in ('"missing.fits"', "23"):
        config.write_text(recipe.replace('"master-bias.fits"', replacement))
        result = subprocess.run(args, cwd=controls, text=True, capture_output=True)
        assert result.returncode != 0 and not list(output.iterdir()), result

    config.write_text(recipe)
    result = subprocess.run(args, cwd=controls, text=True, capture_output=True)
    assert result.returncode == 0, (result.stdout, result.stderr)
    (product,) = output.glob("*.fits")
    log = product.with_suffix(".log").read_text()
    assert f"BIAS_SUBTRACTION CCD-A HDU 1 BEFORE_ADMISSION_AND_NORMALIZATION SHA256 {bias_hash}" in log
    assert f"BIAS_SUBTRACTION CCD-B HDU 2 BEFORE_ADMISSION_AND_NORMALIZATION SHA256 {bias_hash}" in log
    # Corrected medians are 2L. A uses 3 frames, mean 400. B uses 4,
    # mean 650. The mosaic ratio is therefore exactly 650/400 = 1.625.
    expected = np.tile(response.astype(np.float32) / 2, (3, 1))
    with fits.open(product) as hdus:
        assert hdus[0].header["PRODCATG"] == f"CALIB.MASTER_{kind.upper()}_FLAT"
        assert [h.name for h in hdus[1:]] == ["CCD-B", "CCD-A"]
        np.testing.assert_array_equal(hdus[1].data, expected * 1.625)
        np.testing.assert_array_equal(hdus[2].data, expected)
        assert [h.header["ESO MPP QC FRMEDIAN"] for h in hdus[1:]] == [650, 400]
    with asdf.open(product.with_suffix(".asdf")) as archive:
        qc = archive.tree["qc"]
        assert qc["file"]["sha256"] == digest(product)
        assert qc["provenance"]["configuration"]["snapshot"] == recipe
        (calibration,) = qc["calibrations"]
        assert calibration["record_id"] == calibration["role"] == "master_bias"
        assert calibration["file"]["location"] == str(bias_path)
        assert calibration["file"]["sha256"] == bias_hash
        assert [(row["detector_id"], row["source_hdu"])
                for row in calibration["detector_bindings"]] == [("CCD-B", 2), ("CCD-A", 1)]
        evidence = {row["name"]: row["text"] for row in qc["extensions"]["native_evidence"]}
        assert evidence["bias_subtraction"] == "per_exposure_before_admission_and_normalization"
        for index, frame in enumerate(qc["embedded_input_records"]):
            assert frame["file"]["location"] == str(paths[index])
            assert frame["file"]["sha256"] == hashes[index]
            expected_hdus = [("CCD-B", 1), ("CCD-A", 2)] if index % 2 else [
                ("CCD-B", 2), ("CCD-A", 1)]
            assert [(row["detector_id"], row["source_hdu"]) for row in frame["detectors"]] == expected_hdus
            for row in frame["detectors"]:
                measurement = row["measurements"][0]
                name = row["detector_id"]
                if index == 3 and name == "CCD-A":
                    assert measurement["status"] == "unavailable"
                else:
                    medians = (200, 400, 600) if name == "CCD-A" else (400, 800, 1200, 200)
                    assert measurement["value"] == medians[index]
    assert digest(bias_path) == bias_hash
    assert [digest(path) for path in paths] == hashes
    rejected_output = reduced / "cal/nonfinite"
    rejected_output.mkdir()
    config.write_text(recipe.replace('"master-bias.fits"', '"nonfinite-bias.fits"')
                      .replace(f'run = "cal/{operation}"', 'run = "cal/nonfinite"'))
    result = subprocess.run(args, cwd=controls, text=True, capture_output=True)
    assert result.returncode != 0, result
    assert not list(rejected_output.glob("*.fits")) and not list(rejected_output.glob("*.asdf"))
    print(f"PASS: {operation} bias before normalization, exact mosaic, calibration admission and provenance")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--command", type=Path, required=True)
    parser.add_argument("--capture-writer", action="store_true")
    arguments = parser.parse_args()
    kinds = ("dome",) if arguments.capture_writer else ("dome", "sky")
    for kind in kinds:
        with tempfile.TemporaryDirectory(prefix=f"native-{kind}-") as directory:
            check(str(arguments.command.resolve()), Path(directory).resolve(), arguments.capture_writer, kind)
        if not arguments.capture_writer:
            with tempfile.TemporaryDirectory(prefix=f"native-{kind}-bias-") as directory:
                check_master_bias(str(arguments.command.resolve()), Path(directory).resolve(), kind)


if __name__ == "__main__":
    main()
