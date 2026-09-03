"""Data update coordinator for UDM Pro Fan Control."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from paramiko.ssh_exception import AuthenticationException

from .client import (
    UdmProFanControlClient,
    UdmProFanControlError,
    UdmProFanControlSettings,
    UdmProStatus,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class UdmProFanControlCoordinator(DataUpdateCoordinator[UdmProStatus]):
    """Coordinate UDM Pro polling and watchdog writes."""

    def __init__(
        self, hass: HomeAssistant, client: UdmProFanControlClient
    ) -> None:
        """Initialize the coordinator."""

        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=client.settings.interval),
        )

    async def _async_update_data(self) -> UdmProStatus:
        """Fetch data from the UDM Pro."""

        try:
            return await self.hass.async_add_executor_job(self.client.read_status, True)
        except AuthenticationException as err:
            raise ConfigEntryAuthFailed("UDM Pro SSH authentication failed") from err
        except (OSError, UdmProFanControlError) as err:
            raise UpdateFailed(str(err)) from err
        except Exception as err:  # noqa: BLE001 - surface unexpected device errors.
            raise HomeAssistantError(str(err)) from err

    def update_settings(self, settings: UdmProFanControlSettings) -> None:
        """Update client settings and polling interval."""

        self.client.update_settings(settings)
        self.update_interval = timedelta(seconds=settings.interval)
