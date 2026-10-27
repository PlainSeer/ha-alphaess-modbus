"""Build the integration-only ZIP consumed by HACS, without local scratch files."""
import argparse
from pathlib import Path
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = Path("custom_components/alphaess_modbus")


def build_release(output: Path) -> None:
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z", "--", INTEGRATION.as_posix()], cwd=ROOT
    ).decode().split("\0")
    files = [(ROOT / path, Path(path).relative_to(INTEGRATION).as_posix())
             for path in tracked if path]
    if "manifest.json" not in {name for _, name in files}:
        raise ValueError("Integration manifest is missing from the tracked files")
    files.append((ROOT / "LICENSE", "LICENSE"))
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for source, name in sorted(files, key=lambda item: item[1]):
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    build_release(parser.parse_args().output)
