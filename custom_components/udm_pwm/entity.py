"""Shared entity helpers for UDM Pro Fan Control."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import UdmProFanControlCoordinator


class UdmProFanControlEntity(CoordinatorEntity[UdmProFanControlCoordinator]):
    """Base UDM Pro Fan Control entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: UdmProFanControlCoordinator,
        entry_id: str,
        key: str,
    ) -> None:
        """Initialize the entity."""

        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            manufacturer="Ubiquiti",
            name="UDM Pro",
        )
