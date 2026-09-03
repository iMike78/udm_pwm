"""Synchronous SSH client for UDM Pro fan control."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import re
import shlex
import time
from typing import Any

import paramiko
from paramiko.ssh_exception import AuthenticationException

from .const import (
    CONF_CONTROL_MODE,
    CONF_CURVE_MAX_PWM,
    CONF_CURVE_MAX_TEMP,
    CONF_CURVE_HYSTERESIS,
    CONF_CURVE_MIN_PWM,
    CONF_CURVE_MIN_TEMP,
    CONF_FAN1_RPM_PATH,
    CONF_FAN2_RPM_PATH,
    CONF_HDD_DEVICE,
    CONF_HOST,
    CONF_INTERVAL,
    CONF_PASSWORD,
    CONF_PWM1,
    CONF_PWM1_PATH,
    CONF_PWM2,
    CONF_PWM2_PATH,
    CONF_SMART_INTERVAL,
    CONF_TEMP1_PATH,
    CONF_TEMP2_PATH,
    CONF_TEMP3_PATH,
    CONF_USERNAME,
    DEFAULT_CONTROL_MODE,
    DEFAULT_CURVE_MAX_PWM,
    DEFAULT_CURVE_MAX_TEMP,
    DEFAULT_CURVE_HYSTERESIS,
    DEFAULT_CURVE_MIN_PWM,
    DEFAULT_CURVE_MIN_TEMP,
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
)

_LOGGER = logging.getLogger(__name__)


class UdmProFanControlError(Exception):
    """Base error for UDM Pro fan control."""


@dataclass(frozen=True)
class UdmProFanControlSettings:
    """Runtime settings for the UDM Pro SSH client."""

    host: str
    username: str
    password: str
    control_mode: str
    pwm1: int
    pwm2: int
    interval: int
    smart_interval: int
    curve_min_temp: int
    curve_max_temp: int
    curve_hysteresis: int
    curve_min_pwm: int
    curve_max_pwm: int
    pwm1_path: str
    pwm2_path: str
    fan1_rpm_path: str
    fan2_rpm_path: str
    temp1_path: str
    temp2_path: str
    temp3_path: str
    hdd_device: str

    @classmethod
    def from_entry_data(
        cls, data: dict[str, Any], options: dict[str, Any] | None = None
    ) -> "UdmProFanControlSettings":
        """Create settings from config entry data and options."""

        merged = {**data, **(options or {})}
        return cls(
            host=merged[CONF_HOST],
            username=merged.get(CONF_USERNAME, DEFAULT_USERNAME),
            password=merged[CONF_PASSWORD],
            control_mode=merged.get(CONF_CONTROL_MODE, DEFAULT_CONTROL_MODE),
            pwm1=int(merged.get(CONF_PWM1, DEFAULT_PWM1)),
            pwm2=int(merged.get(CONF_PWM2, DEFAULT_PWM2)),
            interval=int(merged.get(CONF_INTERVAL, DEFAULT_INTERVAL)),
            smart_interval=int(
                merged.get(CONF_SMART_INTERVAL, DEFAULT_SMART_INTERVAL)
            ),
            curve_min_temp=int(
                merged.get(CONF_CURVE_MIN_TEMP, DEFAULT_CURVE_MIN_TEMP)
            ),
            curve_max_temp=int(
                merged.get(CONF_CURVE_MAX_TEMP, DEFAULT_CURVE_MAX_TEMP)
            ),
            curve_hysteresis=int(
                merged.get(CONF_CURVE_HYSTERESIS, DEFAULT_CURVE_HYSTERESIS)
            ),
            curve_min_pwm=int(merged.get(CONF_CURVE_MIN_PWM, DEFAULT_CURVE_MIN_PWM)),
            curve_max_pwm=int(merged.get(CONF_CURVE_MAX_PWM, DEFAULT_CURVE_MAX_PWM)),
            pwm1_path=merged.get(CONF_PWM1_PATH, DEFAULT_PWM1_PATH),
            pwm2_path=merged.get(CONF_PWM2_PATH, DEFAULT_PWM2_PATH),
            fan1_rpm_path=merged.get(CONF_FAN1_RPM_PATH, DEFAULT_FAN1_RPM_PATH),
            fan2_rpm_path=merged.get(CONF_FAN2_RPM_PATH, DEFAULT_FAN2_RPM_PATH),
            temp1_path=merged.get(
                CONF_TEMP1_PATH,
                merged.get("phy_temperature_path", DEFAULT_TEMP1_PATH),
            ),
            temp2_path=merged.get(CONF_TEMP2_PATH, DEFAULT_TEMP2_PATH),
            temp3_path=merged.get(CONF_TEMP3_PATH, DEFAULT_TEMP3_PATH),
            hdd_device=merged.get(CONF_HDD_DEVICE, DEFAULT_HDD_DEVICE),
        )


@dataclass(frozen=True)
class UdmProStatus:
    """Current UDM Pro fan and storage status."""

    pwm1: int | None
    pwm2: int | None
    fan1_rpm: int | None
    fan2_rpm: int | None
    hdd_temperature: int | None
    temp1: int | None
    temp2: int | None
    temp3: int | None
    target_pwm1: int | None
    target_pwm2: int | None
    control_mode: str
    watchdog_ok: bool


class UdmProFanControlClient:
    """Read and write UDM Pro fan values over SSH."""

    def __init__(self, settings: UdmProFanControlSettings) -> None:
        """Initialize the SSH client wrapper."""

        self.settings = settings
        self._cached_hdd_temperature: int | None = None
        self._last_smart_read = 0.0
        self._last_curve_temperature: int | None = None
        self._last_curve_pwm: int | None = None

    def update_settings(self, settings: UdmProFanControlSettings) -> None:
        """Update settings used by the client."""

        self.settings = settings

    def read_status(self, enforce_targets: bool) -> UdmProStatus:
        """Read UDM status and optionally enforce configured PWM values."""

        client: paramiko.SSHClient | None = None
        try:
            client = self._connect()
            pwm1 = self._read_int(client, self.settings.pwm1_path)
            pwm2 = self._read_int(client, self.settings.pwm2_path)
            temp1 = self._read_optional_temperature(client, self.settings.temp1_path)
            temp2 = self._read_optional_temperature(client, self.settings.temp2_path)
            temp3 = self._read_optional_temperature(client, self.settings.temp3_path)
            hdd_temperature = self._read_cached_hdd_temperature(client)
            target_pwm1, target_pwm2 = self._target_pwm_values(
                hdd_temperature, temp1, temp2, temp3
            )

            watchdog_ok = True
            if enforce_targets and target_pwm1 is not None and target_pwm2 is not None:
                if pwm1 != target_pwm1:
                    _LOGGER.info("Updating PWM1 from %s to %s", pwm1, target_pwm1)
                    self._write_int(client, self.settings.pwm1_path, target_pwm1)
                    pwm1 = target_pwm1
                if pwm2 != target_pwm2:
                    _LOGGER.info("Updating PWM2 from %s to %s", pwm2, target_pwm2)
                    self._write_int(client, self.settings.pwm2_path, target_pwm2)
                    pwm2 = target_pwm2
                watchdog_ok = pwm1 == target_pwm1 and pwm2 == target_pwm2

            return UdmProStatus(
                pwm1=pwm1,
                pwm2=pwm2,
                fan1_rpm=self._read_optional_int(client, self.settings.fan1_rpm_path),
                fan2_rpm=self._read_optional_int(client, self.settings.fan2_rpm_path),
                hdd_temperature=hdd_temperature,
                temp1=temp1,
                temp2=temp2,
                temp3=temp3,
                target_pwm1=target_pwm1,
                target_pwm2=target_pwm2,
                control_mode=self.settings.control_mode,
                watchdog_ok=watchdog_ok,
            )
        finally:
            if client is not None:
                client.close()

    def _connect(self) -> paramiko.SSHClient:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                self.settings.host,
                username=self.settings.username,
                password=self.settings.password,
                timeout=10,
                auth_timeout=10,
                banner_timeout=10,
                look_for_keys=False,
                allow_agent=False,
            )
        except AuthenticationException:
            client.close()
            raise
        except Exception as err:  # noqa: BLE001 - preserve useful SSH error text.
            client.close()
            raise UdmProFanControlError(f"Could not connect to UDM Pro: {err}") from err
        return client

    def _exec(self, client: paramiko.SSHClient, command: str) -> str:
        stdin, stdout, stderr = client.exec_command(command)
        stdin.close()
        output = stdout.read().decode(errors="replace").strip()
        error = stderr.read().decode(errors="replace").strip()
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            raise UdmProFanControlError(error or f"Command failed: {command}")
        return output

    def _read_int(self, client: paramiko.SSHClient, path: str) -> int:
        value = self._exec(client, f"cat {shlex.quote(path)}")
        return int(value)

    def _read_optional_int(self, client: paramiko.SSHClient, path: str) -> int | None:
        try:
            return self._read_int(client, path)
        except Exception as err:  # noqa: BLE001 - optional telemetry may not exist.
            _LOGGER.debug("Could not read %s: %s", path, err)
            return None

    def _write_int(self, client: paramiko.SSHClient, path: str, value: int) -> None:
        self._exec(client, f"printf '%d' {int(value)} > {shlex.quote(path)}")

    def _read_optional_temperature(
        self, client: paramiko.SSHClient, path: str
    ) -> int | None:
        try:
            value = self._read_int(client, path)
        except Exception as err:  # noqa: BLE001 - optional telemetry may not exist.
            _LOGGER.debug("Could not read temperature from %s: %s", path, err)
            return None

        if abs(value) >= 1000:
            return round(value / 1000)
        return value

    def _read_hdd_temperature(self, client: paramiko.SSHClient) -> int | None:
        try:
            output = self._exec(
                client,
                f"smartctl -A {shlex.quote(self.settings.hdd_device)}",
            )
        except Exception as err:  # noqa: BLE001 - SMART may be unavailable.
            _LOGGER.debug("Could not read HDD temperature: %s", err)
            return None

        for line in output.splitlines():
            columns = line.split()
            if len(columns) >= 10 and columns[0] in {"190", "194"}:
                match = re.search(r"-?\d+", columns[9])
                if match:
                    return int(match.group(0))
            if "Current Drive Temperature" in line or line.strip().startswith("Temperature:"):
                match = re.search(r"(-?\d+)\s*(?:C|Celsius)", line)
                if match:
                    return int(match.group(1))
        return None

    def _read_cached_hdd_temperature(self, client: paramiko.SSHClient) -> int | None:
        now = time.monotonic()
        if (
            self._cached_hdd_temperature is not None
            and now - self._last_smart_read < self.settings.smart_interval
        ):
            return self._cached_hdd_temperature

        hdd_temperature = self._read_hdd_temperature(client)
        self._last_smart_read = now
        if hdd_temperature is not None:
            self._cached_hdd_temperature = hdd_temperature
        return self._cached_hdd_temperature

    def _target_pwm_values(
        self,
        hdd_temperature: int | None,
        temp1: int | None,
        temp2: int | None,
        temp3: int | None,
    ) -> tuple[int | None, int | None]:
        if self.settings.control_mode == "monitor":
            return None, None
        if self.settings.control_mode == "fixed":
            return self.settings.pwm1, self.settings.pwm2
        if self.settings.control_mode != "curve":
            return self.settings.pwm1, self.settings.pwm2

        temperatures = [
            value
            for value in (hdd_temperature, temp1, temp2, temp3)
            if value is not None
        ]
        if not temperatures:
            return self.settings.curve_max_pwm, self.settings.curve_max_pwm

        hottest = max(temperatures)
        target = self._curve_pwm(hottest)
        if (
            self._last_curve_pwm is not None
            and target < self._last_curve_pwm
            and hottest
            > self._temperature_for_pwm(self._last_curve_pwm)
            - self.settings.curve_hysteresis
        ):
            target = self._last_curve_pwm

        self._last_curve_temperature = hottest
        self._last_curve_pwm = target
        return target, target

    def _curve_pwm(self, temperature: int) -> int:
        min_temp = self.settings.curve_min_temp
        max_temp = max(self.settings.curve_max_temp, min_temp + 1)
        min_pwm = self.settings.curve_min_pwm
        max_pwm = max(self.settings.curve_max_pwm, min_pwm)

        if temperature <= min_temp:
            return min_pwm
        if temperature >= max_temp:
            return max_pwm

        ratio = (temperature - min_temp) / (max_temp - min_temp)
        return round(min_pwm + ratio * (max_pwm - min_pwm))

    def _temperature_for_pwm(self, pwm: int) -> float:
        min_temp = self.settings.curve_min_temp
        max_temp = max(self.settings.curve_max_temp, min_temp + 1)
        min_pwm = self.settings.curve_min_pwm
        max_pwm = max(self.settings.curve_max_pwm, min_pwm)

        if pwm <= min_pwm:
            return float(min_temp)
        if pwm >= max_pwm:
            return float(max_temp)

        ratio = (pwm - min_pwm) / (max_pwm - min_pwm)
        return min_temp + ratio * (max_temp - min_temp)
