"""Select entities for UDM Pro Fan Control."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import UdmProFanControlSettings
from .const import CONF_CONTROL_MODE, CONTROL_MODES, DEFAULT_CONTROL_MODE, DOMAIN
from .coordinator import UdmProFanControlCoordinator
from .entity import UdmProFanControlEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities."""

    coordinator: UdmProFanControlCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([UdmProControlModeSelect(coordinator, entry)])


class UdmProControlModeSelect(UdmProFanControlEntity, SelectEntity):
    """Control mode selector."""

    _attr_translation_key = "control_mode"
    _attr_options = list(CONTROL_MODES)

    def __init__(
        self, coordinator: UdmProFanControlCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the select entity."""

        super().__init__(coordinator, entry.entry_id, "control_mode")
        self._entry = entry

    @property
    def current_option(self) -> str:
        """Return the selected control mode."""

        return self._entry.options.get(
            CONF_CONTROL_MODE,
            self._entry.data.get(CONF_CONTROL_MODE, DEFAULT_CONTROL_MODE),
        )

    async def async_select_option(self, option: str) -> None:
        """Update the selected control mode."""

        if option not in CONTROL_MODES:
            return

        new_options = dict(self._entry.options)
        new_options[CONF_CONTROL_MODE] = option
        self.hass.config_entries.async_update_entry(self._entry, options=new_options)
        self.coordinator.update_settings(
            UdmProFanControlSettings.from_entry_data(
                self._entry.data, self._entry.options
            )
        )
        await self.coordinator.async_request_refresh()
