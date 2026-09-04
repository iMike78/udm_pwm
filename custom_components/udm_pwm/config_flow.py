"""Config flow for UDM Pro Fan Control."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .client import UdmProFanControlClient, UdmProFanControlSettings
from .const import (
    CONF_FAN1_RPM_PATH,
    CONF_FAN2_RPM_PATH,
    CONF_HDD_DEVICE,
    CONF_HOST,
    CONF_INTERVAL,
    CONF_PASSWORD,
    CONF_CONTROL_MODE,
    CONF_CURVE_MAX_PWM,
    CONF_CURVE_MAX_TEMP,
    CONF_CURVE_HYSTERESIS,
    CONF_CURVE_MIN_PWM,
    CONF_CURVE_MIN_TEMP,
    CONF_CURVE_PWM2_MAX_PWM,
    CONF_CURVE_PWM2_MIN_PWM,
    CONF_PWM1,
    CONF_PWM1_PATH,
    CONF_PWM2,
    CONF_PWM2_PATH,
    CONF_TEMP1_PATH,
    CONF_TEMP2_PATH,
    CONF_TEMP3_PATH,
    CONF_USERNAME,
    CONTROL_MODES,
    DEFAULT_CONTROL_MODE,
    DEFAULT_CURVE_MAX_PWM,
    DEFAULT_CURVE_MAX_TEMP,
    DEFAULT_CURVE_HYSTERESIS,
    DEFAULT_CURVE_MIN_PWM,
    DEFAULT_CURVE_MIN_TEMP,
    DEFAULT_CURVE_PWM2_MAX_PWM,
    DEFAULT_CURVE_PWM2_MIN_PWM,
    DEFAULT_FAN1_RPM_PATH,
    DEFAULT_FAN2_RPM_PATH,
    DEFAULT_HDD_DEVICE,
    DEFAULT_INTERVAL,
    DEFAULT_PWM1,
    DEFAULT_PWM1_PATH,
    DEFAULT_PWM2,
    DEFAULT_PWM2_PATH,
    DEFAULT_SMART_INTERVAL,
    DEFAULT_TEMP1_PATH,
    DEFAULT_TEMP2_PATH,
    DEFAULT_TEMP3_PATH,
    DEFAULT_USERNAME,
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
    CONF_SMART_INTERVAL,
)


class UdmProFanControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for UDM Pro Fan Control."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial setup step."""

        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()

            settings = UdmProFanControlSettings.from_entry_data(user_input)
            client = UdmProFanControlClient(settings)
            try:
                await self.hass.async_add_executor_job(client.read_status, False)
            except Exception:  # noqa: BLE001 - config flow maps details to UI strings.
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"UDM Pro ({user_input[CONF_HOST]})",
                    data=user_input,
                    options={
                        CONF_CONTROL_MODE: user_input[CONF_CONTROL_MODE],
                        CONF_PWM1: user_input[CONF_PWM1],
                        CONF_PWM2: user_input[CONF_PWM2],
                        CONF_INTERVAL: user_input[CONF_INTERVAL],
                        CONF_SMART_INTERVAL: user_input[CONF_SMART_INTERVAL],
                        CONF_CURVE_MIN_TEMP: user_input[CONF_CURVE_MIN_TEMP],
                        CONF_CURVE_MAX_TEMP: user_input[CONF_CURVE_MAX_TEMP],
                        CONF_CURVE_HYSTERESIS: user_input[CONF_CURVE_HYSTERESIS],
                        CONF_CURVE_MIN_PWM: user_input[CONF_CURVE_MIN_PWM],
                        CONF_CURVE_MAX_PWM: user_input[CONF_CURVE_MAX_PWM],
                        CONF_CURVE_PWM2_MIN_PWM: user_input[
                            CONF_CURVE_PWM2_MIN_PWM
                        ],
                        CONF_CURVE_PWM2_MAX_PWM: user_input[
                            CONF_CURVE_PWM2_MAX_PWM
                        ],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> UdmProFanControlOptionsFlow:
        """Create the options flow."""

        return UdmProFanControlOptionsFlow(config_entry)


class UdmProFanControlOptionsFlow(config_entries.OptionsFlow):
    """Handle options for UDM Pro Fan Control."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""

        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage integration options."""

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        merged = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(merged),
        )


def _user_schema(values: dict[str, Any] | None) -> vol.Schema:
    values = values or {}
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=values.get(CONF_HOST, "192.168.1.1")): str,
            vol.Required(
                CONF_USERNAME, default=values.get(CONF_USERNAME, DEFAULT_USERNAME)
            ): str,
            vol.Required(CONF_PASSWORD): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
            ),
            **_shared_fields(values),
            vol.Optional(
                CONF_PWM1_PATH, default=values.get(CONF_PWM1_PATH, DEFAULT_PWM1_PATH)
            ): str,
            vol.Optional(
                CONF_PWM2_PATH, default=values.get(CONF_PWM2_PATH, DEFAULT_PWM2_PATH)
            ): str,
            vol.Optional(
                CONF_FAN1_RPM_PATH,
                default=values.get(CONF_FAN1_RPM_PATH, DEFAULT_FAN1_RPM_PATH),
            ): str,
            vol.Optional(
                CONF_FAN2_RPM_PATH,
                default=values.get(CONF_FAN2_RPM_PATH, DEFAULT_FAN2_RPM_PATH),
            ): str,
            vol.Optional(
                CONF_TEMP1_PATH, default=values.get(CONF_TEMP1_PATH, DEFAULT_TEMP1_PATH)
            ): str,
            vol.Optional(
                CONF_TEMP2_PATH, default=values.get(CONF_TEMP2_PATH, DEFAULT_TEMP2_PATH)
            ): str,
            vol.Optional(
                CONF_TEMP3_PATH, default=values.get(CONF_TEMP3_PATH, DEFAULT_TEMP3_PATH)
            ): str,
            vol.Optional(
                CONF_HDD_DEVICE, default=values.get(CONF_HDD_DEVICE, DEFAULT_HDD_DEVICE)
            ): str,
        }
    )


def _options_schema(values: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            **_shared_fields(values),
            vol.Optional(
                CONF_PWM1_PATH, default=values.get(CONF_PWM1_PATH, DEFAULT_PWM1_PATH)
            ): str,
            vol.Optional(
                CONF_PWM2_PATH, default=values.get(CONF_PWM2_PATH, DEFAULT_PWM2_PATH)
            ): str,
            vol.Optional(
                CONF_FAN1_RPM_PATH,
                default=values.get(CONF_FAN1_RPM_PATH, DEFAULT_FAN1_RPM_PATH),
            ): str,
            vol.Optional(
                CONF_FAN2_RPM_PATH,
                default=values.get(CONF_FAN2_RPM_PATH, DEFAULT_FAN2_RPM_PATH),
            ): str,
            vol.Optional(
                CONF_TEMP1_PATH, default=values.get(CONF_TEMP1_PATH, DEFAULT_TEMP1_PATH)
            ): str,
            vol.Optional(
                CONF_TEMP2_PATH, default=values.get(CONF_TEMP2_PATH, DEFAULT_TEMP2_PATH)
            ): str,
            vol.Optional(
                CONF_TEMP3_PATH, default=values.get(CONF_TEMP3_PATH, DEFAULT_TEMP3_PATH)
            ): str,
            vol.Optional(
                CONF_HDD_DEVICE, default=values.get(CONF_HDD_DEVICE, DEFAULT_HDD_DEVICE)
            ): str,
        }
    )


def _shared_fields(values: dict[str, Any]) -> dict[Any, Any]:
    return {
        vol.Required(
            CONF_CONTROL_MODE,
            default=values.get(CONF_CONTROL_MODE, DEFAULT_CONTROL_MODE),
        ): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=list(CONTROL_MODES),
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Required(
            CONF_PWM1, default=values.get(CONF_PWM1, DEFAULT_PWM1)
        ): _pwm_selector(),
        vol.Required(
            CONF_PWM2, default=values.get(CONF_PWM2, DEFAULT_PWM2)
        ): _pwm_selector(),
        vol.Required(
            CONF_INTERVAL, default=values.get(CONF_INTERVAL, DEFAULT_INTERVAL)
        ): vol.All(vol.Coerce(int), vol.Range(min=MIN_INTERVAL, max=MAX_INTERVAL)),
        vol.Required(
            CONF_SMART_INTERVAL,
            default=values.get(CONF_SMART_INTERVAL, DEFAULT_SMART_INTERVAL),
        ): vol.All(
            vol.Coerce(int), vol.Range(min=MIN_SMART_INTERVAL, max=MAX_SMART_INTERVAL)
        ),
        vol.Required(
            CONF_CURVE_MIN_TEMP,
            default=values.get(CONF_CURVE_MIN_TEMP, DEFAULT_CURVE_MIN_TEMP),
        ): _curve_temperature_selector(),
        vol.Required(
            CONF_CURVE_MAX_TEMP,
            default=values.get(CONF_CURVE_MAX_TEMP, DEFAULT_CURVE_MAX_TEMP),
        ): _curve_temperature_selector(),
        vol.Required(
            CONF_CURVE_HYSTERESIS,
            default=values.get(CONF_CURVE_HYSTERESIS, DEFAULT_CURVE_HYSTERESIS),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=MIN_CURVE_HYSTERESIS,
                max=MAX_CURVE_HYSTERESIS,
                step=1,
                mode=selector.NumberSelectorMode.BOX,
            )
        ),
        vol.Required(
            CONF_CURVE_MIN_PWM,
            default=values.get(CONF_CURVE_MIN_PWM, DEFAULT_CURVE_MIN_PWM),
        ): _pwm_selector(),
        vol.Required(
            CONF_CURVE_MAX_PWM,
            default=values.get(CONF_CURVE_MAX_PWM, DEFAULT_CURVE_MAX_PWM),
        ): _pwm_selector(),
        vol.Required(
            CONF_CURVE_PWM2_MIN_PWM,
            default=values.get(
                CONF_CURVE_PWM2_MIN_PWM, DEFAULT_CURVE_PWM2_MIN_PWM
            ),
        ): _pwm_selector(),
        vol.Required(
            CONF_CURVE_PWM2_MAX_PWM,
            default=values.get(
                CONF_CURVE_PWM2_MAX_PWM, DEFAULT_CURVE_PWM2_MAX_PWM
            ),
        ): _pwm_selector(),
    }


def _pwm_selector() -> selector.NumberSelector:
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=MIN_PWM,
            max=MAX_PWM,
            step=1,
            mode=selector.NumberSelectorMode.BOX,
        )
    )


def _curve_temperature_selector() -> selector.NumberSelector:
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=MIN_CURVE_TEMP,
            max=MAX_CURVE_TEMP,
            step=1,
            mode=selector.NumberSelectorMode.BOX,
        )
    )
