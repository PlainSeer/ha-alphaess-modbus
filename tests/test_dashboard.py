"""Frontend publishing is optional and never sets up inverter controls."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch
from hashlib import sha256

from custom_components.alphaess_modbus import dashboard


def fake(frontend=True):
    async def execute(fn):
        return fn()
    return SimpleNamespace(config=SimpleNamespace(components={'frontend'} if frontend else set()),
                           http=SimpleNamespace(async_register_static_paths=AsyncMock()),
                           async_add_executor_job=AsyncMock(side_effect=execute))


def test_headless_setup_is_noop():
    h = fake(False)
    asyncio.run(dashboard.async_setup_dashboard(h))
    h.async_add_executor_job.assert_not_called()
    h.http.async_register_static_paths.assert_not_called()


def test_module_registration_and_content_hash():
    h = fake()
    with patch.object(dashboard, 'add_extra_js_url') as add:
        asyncio.run(dashboard.async_setup_dashboard(h))
    path = h.http.async_register_static_paths.call_args.args[0][0]
    assert path.url_path == dashboard.MODULE_URL
    assert not path.cache_headers
    digest = sha256(dashboard.MODULE_PATH.read_bytes()).hexdigest()[:16]
    add.assert_called_once_with(h, f'{dashboard.MODULE_URL}?v={digest}')


def test_frontend_failure_does_not_block_integration():
    h = fake()
    h.http.async_register_static_paths.side_effect = RuntimeError('frontend unavailable')
    with patch.object(dashboard, 'add_extra_js_url') as add:
        asyncio.run(dashboard.async_setup_dashboard(h))
    add.assert_not_called()


def test_setup_hook_delegates_only_to_frontend():
    from custom_components.alphaess_modbus import async_setup
    with patch.object(dashboard, 'async_setup_dashboard', new_callable=AsyncMock) as setup:
        h = fake()
        assert asyncio.run(async_setup(h, {}))
        setup.assert_awaited_once_with(h)
