"""Generate the saved-view preview from anonymised, example entity metadata."""
import json
from pathlib import Path
from types import SimpleNamespace

from custom_components.alphaess_modbus.dashboard_config import build_dashboard

folder = Path(__file__).parent
entities = [SimpleNamespace(**e) for e in json.loads((folder / "registry.json").read_text())]
config = build_dashboard(entities, {"example": SimpleNamespace(name="AlphaESS", name_by_user=None)})
(folder / "saved-dashboard.json").write_text(json.dumps(config, indent=2) + "\n")
