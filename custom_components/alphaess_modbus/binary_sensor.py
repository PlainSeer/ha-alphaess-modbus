from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .house_energy import finite
from .const import DOMAIN
from .coordinator import AlphaESSCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: AlphaESSCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        AlphaESSExcessExportPauseSensor(coordinator, entry),
        AlphaESSForceImportPauseSensor(coordinator, entry),
        AlphaESSBatteryFullSensor(coordinator, entry),
        AlphaESSPeakShavingPauseSensor(coordinator, entry),
    ])


class AlphaESSExcessExportPauseSensor(BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Excess Export Pause"
    _attr_icon = "mdi:pause-circle"
    _attr_translation_key = "excess_export_pause"

    def __init__(self, coordinator: AlphaESSCoordinator, entry: ConfigEntry) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_excess_export_pause"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)})

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success

    @property
    def is_on(self) -> bool:
        return self._coordinator.ee_paused


class AlphaESSForceImportPauseSensor(BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Force Import Pause"
    _attr_icon = "mdi:pause-circle"
    _attr_translation_key = "force_import_pause"

    def __init__(self, coordinator: AlphaESSCoordinator, entry: ConfigEntry) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_force_import_pause"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)})

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success

    @property
    def is_on(self) -> bool:
        return self._coordinator.fi_paused


class AlphaESSBatteryFullSensor(CoordinatorEntity, BinarySensorEntity):
    """Hillview full indication: charging not permitted, discharging permitted."""

    _attr_has_entity_name = True
    _attr_name = "Battery Full"
    _attr_icon = "mdi:battery-check"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        # Preserve the v1.16.0 registry identity and existing entity IDs.
        self._attr_unique_id = f"{entry.entry_id}_battery_full_soc"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)})

    @property
    def available(self):
        value = finite((self.coordinator.data or {}).get("battery_status"))
        return super().available and value in (0, 1, 256, 257, 512, 513)

    @property
    def is_on(self):
        if not self.available:
            return None
        return float(self.coordinator.data["battery_status"]) == 1


class AlphaESSPeakShavingPauseSensor(CoordinatorEntity, BinarySensorEntity):
    """Passive view of the optional peak-shaving controller."""

    _attr_has_entity_name = True
    _attr_name = "Peak Shaving Paused"
    _attr_icon = "mdi:pause-circle"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry_id = entry.entry_id
        self._attr_unique_id = f"{entry.entry_id}_peak_shaving_paused"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)})

    @property
    def is_on(self):
        switches = self.hass.data[DOMAIN].get(f"{self._entry_id}_switches", {})
        peak = switches.get("peak_shaving")
        return bool(peak and peak.is_on and peak.paused)
