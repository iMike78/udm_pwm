"""Sensor entities for UDM Pro Fan Control."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import UdmProFanControlCoordinator
from .entity import UdmProFanControlEntity


@dataclass(frozen=True, kw_only=True)
class UdmProSensorEntityDescription(SensorEntityDescription):
    """Describes a UDM Pro sensor."""

    value_fn: Callable[..., int | None]


SENSORS: tuple[UdmProSensorEntityDescription, ...] = (
    UdmProSensorEntityDescription(
        key="hdd_temperature",
        translation_key="hdd_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data.hdd_temperature,
    ),
    UdmProSensorEntityDescription(
        key="temp1",
        translation_key="temp1",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data.temp1,
    ),
    UdmProSensorEntityDescription(
        key="temp2",
        translation_key="temp2",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data.temp2,
    ),
    UdmProSensorEntityDescription(
        key="temp3",
        translation_key="temp3",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data.temp3,
    ),
    UdmProSensorEntityDescription(
        key="fan1_rpm",
        translation_key="fan1_rpm",
        native_unit_of_measurement="rpm",
        value_fn=lambda data: data.fan1_rpm,
    ),
    UdmProSensorEntityDescription(
        key="fan2_rpm",
        translation_key="fan2_rpm",
        native_unit_of_measurement="rpm",
        value_fn=lambda data: data.fan2_rpm,
    ),
    UdmProSensorEntityDescription(
        key="pwm1",
        translation_key="pwm1",
        value_fn=lambda data: data.pwm1,
    ),
    UdmProSensorEntityDescription(
        key="pwm2",
        translation_key="pwm2",
        value_fn=lambda data: data.pwm2,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities."""

    coordinator: UdmProFanControlCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        UdmProSensor(coordinator, entry.entry_id, description)
        for description in SENSORS
    )


class UdmProSensor(UdmProFanControlEntity, SensorEntity):
    """UDM Pro sensor entity."""

    entity_description: UdmProSensorEntityDescription

    def __init__(
        self,
        coordinator: UdmProFanControlCoordinator,
        entry_id: str,
        description: UdmProSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""

        super().__init__(coordinator, entry_id, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> int | None:
        """Return the native sensor value."""

        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
