"""Passive house-energy estimates. Never requests data or controls the inverter."""
from __future__ import annotations

import math

from homeassistant.components.sensor import RestoreSensor, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN

# Existing coordinator keys only. Keep signs explicit to avoid double-counting PV.
COUNTERS = {
    "total_energy_consumption_from_grid_meter": 1,
    "total_energy_feed_to_grid_meter": -1,
    "total_energy_from_pv": 1,
    "total_energy_charge_battery": -1,
    "total_energy_discharge_battery": 1,
}
DAILY = {
    "today_energy_from_grid": 1,
    "today_energy_feed_to_grid": -1,
    "today_pv_generation": 1,  # Already includes integrated AC PV.
    "today_battery_charged": -1,
    "today_battery_discharged": 1,
}


def finite(value):
    """Reject missing/malformed input instead of fabricating zero energy."""
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


class AlphaESSHouseEnergySensor(CoordinatorEntity, RestoreSensor):
    """Independent entities; disabling one never disables the other's calculation."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "kWh"
    _attr_device_class = SensorDeviceClass.ENERGY
    # Counter quantisation can cause small decreases: never total_increasing.
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator, entry, daily_sources=None):
        super().__init__(coordinator)
        self._daily = daily_sources
        key = "house_energy_today" if daily_sources is not None else "house_energy_since_tracking"
        self._attr_name = "Today's House Energy" if daily_sources is not None else "House Energy Since Tracking"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)})
        self._value = 0.0
        self._previous = None
        self._poll_times = {}
        self._ac_sample = None
        self._tracking_since = None
        self._counter_resets = 0
        self._ac_gap = False
        self._ready = False

    async def async_added_to_hass(self):
        if self._daily is None:
            last = await self.async_get_last_state()
            if last:
                attrs = last.attributes
                value = finite(attrs.get("tracked_kwh"))
                previous = attrs.get("counter_snapshot", {})
                if (value is not None and isinstance(previous, dict)
                        and all(finite(previous.get(k)) is not None for k in COUNTERS)):
                    self._value = value
                    self._previous = {k: float(previous[k]) for k in COUNTERS}
                    self._tracking_since = attrs.get("tracking_since")
                    resets = finite(attrs.get("counter_resets", 0))
                    self._counter_resets = max(0, int(resets or 0))
                    # AC power cannot reconstruct energy during HA downtime.
                    self._ac_gap = True
        await super().async_added_to_hass()
        self._sample()

    def _sample(self):
        if self._daily is not None:
            return
        data = self.coordinator.data or {}
        values = {k: finite(data.get(k)) for k in COUNTERS}
        power = finite(data.get("active_power_pv_meter"))
        self._ready = (self.coordinator.last_update_success
                       and all(v is not None and v >= 0 for v in values.values())
                       and power is not None)
        if not self._ready:
            self._ac_sample = None
            self._ac_gap = True
            return
        polled = self.coordinator._last_polled
        # Integrate AC only when an existing successful power read advances.
        stamp = polled.get("active_power_pv_meter")
        if stamp is not None and (self._ac_sample is None or stamp > self._ac_sample[0]):
            if self._ac_sample is not None:
                elapsed = stamp - self._ac_sample[0]
                if 0 < elapsed <= 60:
                    self._value += self._ac_sample[1] * elapsed / 3_600_000
                else:
                    self._ac_gap = True
            self._ac_sample = (stamp, max(0.0, power))
        # Wait until all five counters have a fresh read; no mixed old/new totals.
        stamps = {k: polled.get(k, 0) for k in COUNTERS}
        if not all(stamps[k] > self._poll_times.get(k, 0) for k in COUNTERS):
            return
        if self._previous is not None:
            if any(values[k] < self._previous[k] for k in COUNTERS):
                # Preserve the accumulated total and rebase the entire balance.
                # Energy in the reset interval is unknowable; expose the event.
                self._counter_resets += 1
            else:
                self._value += sum((values[k] - self._previous[k]) * sign
                                   for k, sign in COUNTERS.items())
        self._previous = values
        self._poll_times = stamps
        if self._tracking_since is None:
            self._tracking_since = dt_util.now().isoformat()

    def _handle_coordinator_update(self):
        self._sample()
        super()._handle_coordinator_update()

    def _daily_value(self):
        today = dt_util.now().date()
        values = []
        for key, sign in DAILY.items():
            source = self._daily[key]
            if source._start_date != today:
                return None
            current = finite((self.coordinator.data or {}).get(source._source_key))
            baseline = finite(source._day_start_value)
            # Existing daily sensors clamp reset counters to zero. Do not mistake
            # that for a valid input to the house balance.
            if current is None or baseline is None or current < baseline:
                return None
            value = finite(source.native_value)
            if value is None:
                return None
            values.append(value * sign)
        return round(sum(values), 4)

    @property
    def available(self):
        if not super().available:
            return False
        if self._daily is not None:
            return self._daily_value() is not None
        return self._ready and self._previous is not None

    @property
    def native_value(self):
        if not self.available:
            return None
        if self._daily is not None:
            return self._daily_value()
        return round(self._value, 4)

    @property
    def last_reset(self):
        return dt_util.start_of_local_day() if self._daily is not None else None

    @property
    def extra_state_attributes(self):
        if self._daily is not None:
            return {"calculation": "import - export + PV - battery charged + battery discharged",
                    "comparison_only": True}
        return {"tracked_kwh": self._value, "counter_snapshot": self._previous,
                "tracking_since": self._tracking_since, "counter_resets": self._counter_resets,
                "ac_energy_gap": self._ac_gap, "comparison_only": True}
