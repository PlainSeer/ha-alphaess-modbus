"""Regression tests with real HA entity classes and no inverter connection."""
import asyncio
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from custom_components.alphaess_modbus.house_energy import AlphaESSHouseEnergySensor, COUNTERS, DAILY
from custom_components.alphaess_modbus.binary_sensor import AlphaESSBatteryFullSensor
from custom_components.alphaess_modbus.sensor import AlphaESSDailySensor
from custom_components.alphaess_modbus.const import DAILY_ENERGY_SENSORS


def make_total():
    c = SimpleNamespace(data={k: 1000.0 for k in COUNTERS},
                        _last_polled={k: 100.0 for k in COUNTERS}, last_update_success=True)
    c.data['active_power_pv_meter'] = 3600
    c._last_polled['active_power_pv_meter'] = 100.0
    s = AlphaESSHouseEnergySensor(c, SimpleNamespace(entry_id='test'))
    s.async_write_ha_state = Mock()
    s._sample()
    return c, s


def test_total_starts_at_zero_and_balances_counter_deltas():
    c, s = make_total()
    assert s.native_value == 0
    changes = [3, 1, 4, 2, 1]
    for k, change in zip(COUNTERS, changes):
        c.data[k] += change
        c._last_polled[k] = 160
    c._last_polled['active_power_pv_meter'] = 160
    s._sample()
    assert s.native_value == 5.06
    s._sample()
    assert s.native_value == 5.06  # Same cached sample must not integrate twice.
    assert s.state_class == 'total'


def test_partial_counter_refresh_waits_for_all_inputs():
    c, s = make_total()
    c.data['total_energy_consumption_from_grid_meter'] += 1
    c._last_polled['total_energy_consumption_from_grid_meter'] = 160
    s._sample()
    assert s.native_value == 0
    c._last_polled.update({k: 160 for k in COUNTERS})
    s._sample()
    assert s.native_value == 1


def test_counter_reset_rebases_without_large_false_delta():
    c, s = make_total()
    c.data['total_energy_charge_battery'] = 0
    c._last_polled.update({k: 160 for k in COUNTERS})
    s._sample()
    assert s.native_value == 0
    assert s.extra_state_attributes['counter_resets'] == 1
    c.data['total_energy_consumption_from_grid_meter'] += 1
    c._last_polled.update({k: 220 for k in COUNTERS})
    s._sample()
    assert s.native_value == 1


@pytest.mark.parametrize('bad', [None, float('nan'), float('inf'), 'bad', -1])
def test_invalid_counter_unavailable_and_recovery(bad):
    c, s = make_total()
    k = next(iter(COUNTERS))
    c.data[k] = bad
    s._sample()
    assert s.native_value is None
    c.data[k] = 1001
    c._last_polled.update({k: 160 for k in COUNTERS})
    s._sample()
    assert s.native_value == 1


def test_outage_skips_ac_gap_but_recovers_counter_energy():
    c, s = make_total()
    c.last_update_success = False
    s._sample()
    assert not s.available
    c.last_update_success = True
    c.data['total_energy_consumption_from_grid_meter'] += 2
    c._last_polled.update({k: 1000 for k in c._last_polled})
    s._sample()
    assert s.native_value == 2
    assert s.extra_state_attributes['ac_energy_gap']


def test_long_gap_and_negative_ac_are_not_counted_as_generation():
    c, s = make_total()
    c._last_polled['active_power_pv_meter'] = 200
    c.data['active_power_pv_meter'] = -100
    s._sample()
    assert s.native_value == 0
    c._last_polled['active_power_pv_meter'] = 220
    s._sample()
    assert s.native_value == 0


def test_total_restores_full_precision_and_recovers_offline_counter_delta():
    c, s = make_total()
    s._value = 1.234567
    saved = SimpleNamespace(attributes=s.extra_state_attributes)
    new = AlphaESSHouseEnergySensor(c, SimpleNamespace(entry_id='test'))
    new.async_get_last_state = AsyncMock(return_value=saved)
    c.data['total_energy_from_pv'] += 2
    with patch.object(CoordinatorEntity, 'async_added_to_hass', new=AsyncMock()):
        asyncio.run(new.async_added_to_hass())
    assert new.native_value == 3.2346
    assert new.extra_state_attributes['tracking_since'] == s.extra_state_attributes['tracking_since']
    assert new.extra_state_attributes['ac_energy_gap']


def make_daily():
    c, _ = make_total()
    entry = SimpleNamespace(entry_id='test')
    sources = {key: AlphaESSDailySensor(c, entry, key, source, ac)
               for key, source, ac in DAILY_ENERGY_SENSORS}
    for source in sources.values():
        source._start_date = dt_util.now().date()
        source._day_start_value = 1000
    c.data.update(dict(zip(COUNTERS, [1010, 1003, 1020, 1005, 1002])))
    sources['today_pv_generation']._ac_accumulated_kwh = 1.5
    return c, sources, AlphaESSHouseEnergySensor(c, entry, sources)


def test_daily_includes_ac_exactly_once():
    _, _, s = make_daily()
    assert s.native_value == 25.5
    assert s.last_reset == dt_util.start_of_local_day()


def test_daily_midnight_waits_for_all_baselines():
    c, sources, s = make_daily()
    tomorrow = dt_util.now() + timedelta(days=1)
    with patch('custom_components.alphaess_modbus.house_energy.dt_util.now', return_value=tomorrow):
        assert not s.available
        for key in DAILY:
            source = sources[key]
            source._start_date = tomorrow.date()
            source._day_start_value = c.data[source._source_key]
            source._ac_accumulated_kwh = 0
        assert s.native_value == 0


def test_daily_missing_counter_and_counter_reset_do_not_fabricate_energy():
    c, _, s = make_daily()
    c.data['total_energy_charge_battery'] = 0
    assert s.native_value is None
    c.data['total_energy_charge_battery'] = None
    assert s.native_value is None


def test_quantisation_decrease_is_not_silently_clamped():
    c, s = make_total()
    c.data['total_energy_feed_to_grid_meter'] += 0.01
    c._last_polled.update({k: 160 for k in COUNTERS})
    s._sample()
    assert s.native_value == -0.01


@pytest.mark.parametrize('status, expected', [
    (1, True), (0, False), (256, False), (257, False), (512, False), (513, False),
    (None, None), (-1, None), (2, None), (1.5, None),
    (float('nan'), None), (float('inf'), None), ('bad', None),
])
def test_battery_full_status(status, expected):
    c = SimpleNamespace(data={'battery_status': status}, last_update_success=True)
    s = AlphaESSBatteryFullSensor(c, SimpleNamespace(entry_id='test'))
    assert s.is_on is expected
    assert s.available is (expected is not None)
    c.last_update_success = False
    assert not s.available
    assert s.is_on is None


def test_battery_full_uses_status_not_soc_and_preserves_identity():
    c = SimpleNamespace(data={'battery_status': 256, 'soc_battery': 100},
                        last_update_success=True)
    s = AlphaESSBatteryFullSensor(c, SimpleNamespace(entry_id='test'))
    assert s.is_on is False  # 100% alone no longer means full.
    c.data.update(battery_status=1, soc_battery=99)
    assert s.is_on is True
    assert s.name == 'Battery Full'
    assert s.unique_id == 'test_battery_full_soc'
    assert s.device_info['identifiers'] == {('alphaess_modbus', 'test')}
    c.data = {}
    assert s.is_on is None


@pytest.mark.parametrize("bad", ["bad", float("nan"), float("inf")])
def test_daily_malformed_counter_unavailable(bad):
    c, _, s = make_daily()
    c.data["total_energy_charge_battery"] = bad
    assert s.native_value is None
