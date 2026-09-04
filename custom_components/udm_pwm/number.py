"""Number entities for UDM Pro Fan Control."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import UdmProFanControlSettings
from .const import (
    CONF_CURVE_MAX_PWM,
    CONF_CURVE_MAX_TEMP,
    CONF_CURVE_HYSTERESIS,
    CONF_CURVE_MIN_PWM,
    CONF_CURVE_MIN_TEMP,
    CONF_CURVE_PWM2_MAX_PWM,
    CONF_CURVE_PWM2_MIN_PWM,
    CONF_INTERVAL,
    CONF_PWM1,
    CONF_PWM2,
    CONF_SMART_INTERVAL,
    DEFAULT_CURVE_MAX_PWM,
    DEFAULT_CURVE_MAX_TEMP,
    DEFAULT_CURVE_HYSTERESIS,
    DEFAULT_CURVE_MIN_PWM,
    DEFAULT_CURVE_MIN_TEMP,
    DEFAULT_CURVE_PWM2_MAX_PWM,
    DEFAULT_CURVE_PWM2_MIN_PWM,
    DEFAULT_INTERVAL,
    DEFAULT_PWM1,
    DEFAULT_PWM2,
    DEFAULT_SMART_INTERVAL,
    DOMAIN,
    MAX_CURVE_TEMP,
    MAX_CURVE_HYSTERESIS,
    MAX_INTERVAL,
    MAX_PWM,
    MAX_SMART_INTERVAL,
    MIN_CURVE_TEMP,
    MIN_CURVE_HYSTERESIS,
    MIN_INTERVAL,
    MIN_PWM,
    MIN_SMART_INTERVAL,
)
from .coordinator import UdmProFanControlCoordinator
from .entity import UdmProFanControlEntity


@dataclass(frozen=True, kw_only=True)
class UdmProNumberEntityDescription(NumberEntityDescription):
    """Describes a writable UDM Pro setting."""

    option_key: str


NUMBERS: tuple[UdmProNumberEntityDescription, ...] = (
    UdmProNumberEntityDescription(
        key="target_pwm1",
        translation_key="target_pwm1",
        option_key=CONF_PWM1,
        native_min_value=MIN_PWM,
        native_max_value=MAX_PWM,
        native_step=1,
    ),
    UdmProNumberEntityDescription(
        key="target_pwm2",
        translation_key="target_pwm2",
        option_key=CONF_PWM2,
        native_min_value=MIN_PWM,
        native_max_value=MAX_PWM,
        native_step=1,
    ),
    UdmProNumberEntityDescription(
        key="poll_interval",
        translation_key="poll_interval",
        option_key=CONF_INTERVAL,
        native_min_value=MIN_INTERVAL,
        native_max_value=MAX_INTERVAL,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.SECONDS,
    ),
    UdmProNumberEntityDescription(
        key="smart_interval",
        translation_key="smart_interval",
        option_key=CONF_SMART_INTERVAL,
        native_min_value=MIN_SMART_INTERVAL,
        native_max_value=MAX_SMART_INTERVAL,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.SECONDS,
    ),
    UdmProNumberEntityDescription(
        key="curve_min_temp",
        translation_key="curve_min_temp",
        option_key=CONF_CURVE_MIN_TEMP,
        native_min_value=MIN_CURVE_TEMP,
        native_max_value=MAX_CURVE_TEMP,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    UdmProNumberEntityDescription(
        key="curve_max_temp",
        translation_key="curve_max_temp",
        option_key=CONF_CURVE_MAX_TEMP,
        native_min_value=MIN_CURVE_TEMP,
        native_max_value=MAX_CURVE_TEMP,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    UdmProNumberEntityDescription(
        key="curve_hysteresis",
        translation_key="curve_hysteresis",
        option_key=CONF_CURVE_HYSTERESIS,
        native_min_value=MIN_CURVE_HYSTERESIS,
        native_max_value=MAX_CURVE_HYSTERESIS,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    UdmProNumberEntityDescription(
        key="curve_min_pwm",
        translation_key="curve_min_pwm",
        option_key=CONF_CURVE_MIN_PWM,
        native_min_value=MIN_PWM,
        native_max_value=MAX_PWM,
        native_step=1,
    ),
    UdmProNumberEntityDescription(
        key="curve_max_pwm",
        translation_key="curve_max_pwm",
        option_key=CONF_CURVE_MAX_PWM,
        native_min_value=MIN_PWM,
        native_max_value=MAX_PWM,
        native_step=1,
    ),
    UdmProNumberEntityDescription(
        key="curve_pwm2_min_pwm",
        translation_key="curve_pwm2_min_pwm",
        option_key=CONF_CURVE_PWM2_MIN_PWM,
        native_min_value=MIN_PWM,
        native_max_value=MAX_PWM,
        native_step=1,
    ),
    UdmProNumberEntityDescription(
        key="curve_pwm2_max_pwm",
        translation_key="curve_pwm2_max_pwm",
        option_key=CONF_CURVE_PWM2_MAX_PWM,
        native_min_value=MIN_PWM,
        native_max_value=MAX_PWM,
        native_step=1,
    ),
)

DEFAULT_NUMBER_VALUES = {
    CONF_PWM1: DEFAULT_PWM1,
    CONF_PWM2: DEFAULT_PWM2,
    CONF_INTERVAL: DEFAULT_INTERVAL,
    CONF_SMART_INTERVAL: DEFAULT_SMART_INTERVAL,
    CONF_CURVE_MIN_TEMP: DEFAULT_CURVE_MIN_TEMP,
    CONF_CURVE_MAX_TEMP: DEFAULT_CURVE_MAX_TEMP,
    CONF_CURVE_HYSTERESIS: DEFAULT_CURVE_HYSTERESIS,
    CONF_CURVE_MIN_PWM: DEFAULT_CURVE_MIN_PWM,
    CONF_CURVE_MAX_PWM: DEFAULT_CURVE_MAX_PWM,
    CONF_CURVE_PWM2_MIN_PWM: DEFAULT_CURVE_PWM2_MIN_PWM,
    CONF_CURVE_PWM2_MAX_PWM: DEFAULT_CURVE_PWM2_MAX_PWM,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities."""

    coordinator: UdmProFanControlCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        UdmProNumber(coordinator, entry, description) for description in NUMBERS
    )


class UdmProNumber(UdmProFanControlEntity, NumberEntity):
    """Writable UDM Pro setting."""

    entity_description: UdmProNumberEntityDescription

    def __init__(
        self,
        coordinator: UdmProFanControlCoordinator,
        entry: ConfigEntry,
        description: UdmProNumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""

        super().__init__(coordinator, entry.entry_id, description.key)
        self._entry = entry
        self.entity_description = description

    @property
    def native_value(self) -> int:
        """Return the configured value."""

        return int(
            self._entry.options.get(
                self.entity_description.option_key,
                self._entry.data.get(
                    self.entity_description.option_key,
                    DEFAULT_NUMBER_VALUES[self.entity_description.option_key],
                ),
            )
        )

    async def async_set_native_value(self, value: float) -> None:
        """Update the config entry option and refresh the device."""

        new_options = dict(self._entry.options)
        new_options[self.entity_description.option_key] = int(value)
        self.hass.config_entries.async_update_entry(self._entry, options=new_options)
        self.coordinator.update_settings(
            UdmProFanControlSettings.from_entry_data(
                self._entry.data, self._entry.options
            )
        )
        await self.coordinator.async_request_refresh()
