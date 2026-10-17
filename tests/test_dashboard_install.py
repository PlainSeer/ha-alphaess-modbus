"""Default dashboard registration and narrow, reversible beta migration."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from custom_components.alphaess_modbus import dashboard_install as install


def beta_config():
    return {"views": [{"path": page, "type": "panel", "cards": [
        {"type": "custom:alphaess-beta-live"}]} for page in ("overview", "controls", "diagnostics")]}


def fake(current=None):
    dashboards = {} if current is None else {install.URL_PATH: current}
    return SimpleNamespace(data={"lovelace": SimpleNamespace(dashboards=dashboards)},
                           config=SimpleNamespace(recovery_mode=False))


def test_recognition_rejects_user_changes_and_extra_views():
    assert install.is_beta_dashboard(beta_config())
    config = beta_config()
    config["views"].append({"path": "custom"})
    assert not install.is_beta_dashboard(config)
    config = beta_config()
    config["views"][0]["cards"].append({"type": "markdown"})
    assert not install.is_beta_dashboard(config)


def test_migrate_known_beta_after_backup_only():
    current = Mock(spec=install.LovelaceStorage)
    current.async_load = AsyncMock(return_value=beta_config())
    current.async_save = AsyncMock()
    backup = AsyncMock()
    async def run():
        with patch.object(install, "Store", return_value=backup):
            await install.async_install_dashboard(fake(current))
        backup.async_save.assert_awaited_once()
        current.async_save.assert_awaited_once_with(install.STRATEGY)
        current.async_save.reset_mock()
        backup.async_save.side_effect = RuntimeError("disk full")
        with patch.object(install, "Store", return_value=backup):
            try:
                await install.async_install_dashboard(fake(current))
            except RuntimeError:
                pass
        current.async_save.assert_not_called()
    asyncio.run(run())


def test_unrelated_existing_dashboard_is_untouched():
    current = Mock(spec=install.LovelaceStorage)
    current.async_load = AsyncMock(return_value={"views": [{"cards": [{"type": "markdown"}]}]})
    current.async_save = AsyncMock()
    asyncio.run(install.async_install_dashboard(fake(current)))
    current.async_save.assert_not_called()


def test_real_ha_collection_persists_and_second_setup_is_noop():
    """Exercise HA's actual shared collection, validation, listeners and storage."""
    from homeassistant.core import HomeAssistant
    from homeassistant.components.lovelace.dashboard import DashboardsCollectionWebSocket
    from homeassistant.components.lovelace.const import STORAGE_DASHBOARD_CREATE_FIELDS, STORAGE_DASHBOARD_UPDATE_FIELDS
    import tempfile

    async def run():
        with tempfile.TemporaryDirectory() as directory:
            h = HomeAssistant(directory)
            dashboards = {}
            h.data["lovelace"] = SimpleNamespace(dashboards=dashboards)
            h.data["frontend_panels"] = {}
            collection = install.DashboardsCollection(h)
            await collection.async_load()
            async def listener(kind, item_id, item):
                dashboards[item["url_path"]] = install.LovelaceStorage(h, item)
            collection.async_add_listener(listener)
            DashboardsCollectionWebSocket(collection, "lovelace/dashboards", "dashboard",
                STORAGE_DASHBOARD_CREATE_FIELDS, STORAGE_DASHBOARD_UPDATE_FIELDS).async_setup(h)
            assert install._dashboard_collection(h) is collection
            await install.async_install_dashboard(h)
            current = dashboards[install.URL_PATH]
            assert await current.async_load(False) == install.STRATEGY
            await install.async_install_dashboard(h)
            assert len(collection.async_items()) == 1
            await collection.async_update_item(collection.async_items()[0]["id"], {"title": "User title"})
            assert collection.async_items()[0]["title"] == "User title"
            await h.async_block_till_done()
    asyncio.run(run())
