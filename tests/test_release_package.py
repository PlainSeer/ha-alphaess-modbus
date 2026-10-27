"""Ensure the release artifact installs into the directory HACS supplies."""
import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def test_hacs_package_contains_complete_integration_and_extracts_at_root(tmp_path):
    package = tmp_path / "alphaess_modbus.zip"
    subprocess.run([sys.executable, str(ROOT / "tools/build_release.py"), str(package)],
                   cwd=ROOT, check=True)
    source = ROOT / "custom_components/alphaess_modbus"
    expected = {path.relative_to(source).as_posix(): path.read_bytes()
                for path in source.rglob("*") if path.is_file()
                and "__pycache__" not in path.parts and path.suffix != ".pyc"}
    expected["LICENSE"] = (ROOT / "LICENSE").read_bytes()
    with ZipFile(package) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == set(expected)
        for name, content in expected.items():
            assert archive.read(name) == content
        destination = tmp_path / "config/custom_components/alphaess_modbus"
        archive.extractall(destination)  # HACS extracts directly into this directory.
    manifest = json.loads((destination / "manifest.json").read_text())
    assert manifest["domain"] == "alphaess_modbus"
    assert manifest["codeowners"] == ["@PlainSeer"]
    hacs = json.loads((ROOT / "hacs.json").read_text())
    assert hacs["zip_release"] is True and hacs["filename"] == package.name
    assert (destination / "frontend/alphaess-power-flow.js").is_file()
    assert (destination / "brand/icon.png").is_file()
    assert not (destination / "custom_components").exists()
