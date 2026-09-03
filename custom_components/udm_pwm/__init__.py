"""UDM Pro Fan Control integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .client import UdmProFanControlClient, UdmProFanControlSettings
from .const import DOMAIN
from .coordinator import UdmProFanControlCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
]
type UdmProFanControlConfigEntry = ConfigEntry[UdmProFanControlCoordinator]


async def async_setup_entry(
    hass: HomeAssistant, entry: UdmProFanControlConfigEntry
) -> bool:
    """Set up UDM Pro Fan Control from a config entry."""

    settings = UdmProFanControlSettings.from_entry_data(entry.data, entry.options)
    client = UdmProFanControlClient(settings)
    coordinator = UdmProFanControlCoordinator(hass, client)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: UdmProFanControlConfigEntry
) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def _async_update_listener(
    hass: HomeAssistant, entry: UdmProFanControlConfigEntry
) -> None:
    """Handle options updates without losing existing entities."""

    coordinator: UdmProFanControlCoordinator = hass.data[DOMAIN][entry.entry_id]
    coordinator.update_settings(
        UdmProFanControlSettings.from_entry_data(entry.data, entry.options)
    )
    await coordinator.async_request_refresh()
