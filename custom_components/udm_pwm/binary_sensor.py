"""Binary sensor entities for UDM Pro Fan Control."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import UdmProFanControlCoordinator
from .entity import UdmProFanControlEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor entities."""

    coordinator: UdmProFanControlCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([UdmProWatchdogBinarySensor(coordinator, entry.entry_id)])


class UdmProWatchdogBinarySensor(UdmProFanControlEntity, BinarySensorEntity):
    """Watchdog status binary sensor."""

    _attr_translation_key = "watchdog"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self, coordinator: UdmProFanControlCoordinator, entry_id: str
    ) -> None:
        """Initialize the binary sensor."""

        super().__init__(coordinator, entry_id, "watchdog")

    @property
    def is_on(self) -> bool | None:
        """Return true when the watchdog currently has a problem."""

        if self.coordinator.data is None:
            return None
        return not self.coordinator.data.watchdog_ok
