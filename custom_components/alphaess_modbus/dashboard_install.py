"""Create the default AlphaESS dashboard using HA's Lovelace APIs.

Only migrate the three-view beta produced by this fork; never replace an
arbitrary dashboard, change the user's HA landing page, or call a service.
"""
import logging
from inspect import unwrap

from homeassistant.components.lovelace.dashboard import DashboardsCollection, LovelaceStorage
from homeassistant.helpers.storage import Store

_LOGGER = logging.getLogger(__name__)
URL_PATH = "dashboard-alphaess-native"
STRATEGY = {"strategy": {"type": "custom:alphaess-modbus"}}


def is_beta_dashboard(config):
    """Only recognise the exact three-view beta card structure we installed."""
    views = config.get("views", [])
    return (
        set(config) == {"views"}
        and len(views) == 3
        and [v.get("path") for v in views] == ["overview", "controls", "diagnostics"]
        and all(v.get("type") == "panel" and len(v.get("cards", [])) == 1
                and v["cards"][0].get("type") == "custom:alphaess-beta-live"
                for v in views)
    )


async def async_install_dashboard(hass):
    """Run once after Lovelace setup; persist registration through its collection."""
    data = hass.data.get("lovelace")
    dashboards = data.get("dashboards") if isinstance(data, dict) else getattr(data, "dashboards", None)
    if dashboards is None or hass.config.recovery_mode:
        return
    current = dashboards.get(URL_PATH)
    if current is not None:
        if not isinstance(current, LovelaceStorage):
            return  # YAML dashboards remain user-managed.
        config = await current.async_load(False)
        if is_beta_dashboard(config):
            # A targeted rollback record, saved before replacing the known beta.
            await Store(hass, 1, "alphaess_modbus.dashboard_migration").async_save(
                {"url_path": URL_PATH, "config": config}
            )
            await current.async_save(STRATEGY)
        return

    # Reuse HA's live collection. A second collection would have a stale copy
    # of dashboard metadata and could lose changes made later through the UI.
    collection = _dashboard_collection(hass)
    if collection is None:
        _LOGGER.warning("Automatic AlphaESS dashboard creation unavailable; add the AlphaESS strategy through dashboard settings")
        return
    await collection.async_create_item({
        "url_path": URL_PATH, "title": "AlphaESS (Beta)",
        "icon": "mdi:solar-panel", "show_in_sidebar": True, "require_admin": True,
    })
    # HA's own collection listener registers the panel and storage object.
    await dashboards[URL_PATH].async_save(STRATEGY)
    _LOGGER.info("Created default AlphaESS dashboard at /%s", URL_PATH)


def _dashboard_collection(hass):
    """Resolve HA's registered collection, guarded for supported HA versions.

    The list command wraps a bound DashboardsCollectionWebSocket method with
    functools.wraps on HA 2024.12 and 2026.10. Never create a competing Store.
    """
    command = hass.data.get("websocket_api", {}).get("lovelace/dashboards/list")
    if not command:
        return None
    owner = getattr(unwrap(command[0]), "__self__", None)
    collection = getattr(owner, "storage_collection", None)
    return collection if isinstance(collection, DashboardsCollection) else None
