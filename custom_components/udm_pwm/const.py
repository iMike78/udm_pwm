"""Constants for the UDM Pro Fan Control integration."""

from __future__ import annotations

DOMAIN = "udm_pwm"

CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_CONTROL_MODE = "control_mode"
CONF_PWM1 = "pwm1"
CONF_PWM2 = "pwm2"
CONF_INTERVAL = "interval"
CONF_SMART_INTERVAL = "smart_interval"
CONF_CURVE_MIN_TEMP = "curve_min_temp"
CONF_CURVE_MAX_TEMP = "curve_max_temp"
CONF_CURVE_HYSTERESIS = "curve_hysteresis"
CONF_CURVE_MIN_PWM = "curve_min_pwm"
CONF_CURVE_MAX_PWM = "curve_max_pwm"
CONF_CURVE_PWM2_MIN_PWM = "curve_pwm2_min_pwm"
CONF_CURVE_PWM2_MAX_PWM = "curve_pwm2_max_pwm"
CONF_PWM1_PATH = "pwm1_path"
CONF_PWM2_PATH = "pwm2_path"
CONF_FAN1_RPM_PATH = "fan1_rpm_path"
CONF_FAN2_RPM_PATH = "fan2_rpm_path"
CONF_TEMP1_PATH = "temp1_path"
CONF_TEMP2_PATH = "temp2_path"
CONF_TEMP3_PATH = "temp3_path"
CONF_HDD_DEVICE = "hdd_device"

DEFAULT_USERNAME = "root"
DEFAULT_PWM1 = 160
DEFAULT_PWM2 = 140
DEFAULT_INTERVAL = 60
DEFAULT_SMART_INTERVAL = 300
DEFAULT_CONTROL_MODE = "fixed"
DEFAULT_CURVE_MIN_TEMP = 35
DEFAULT_CURVE_MAX_TEMP = 45
DEFAULT_CURVE_HYSTERESIS = 2
DEFAULT_CURVE_MIN_PWM = 120
DEFAULT_CURVE_MAX_PWM = 200
DEFAULT_CURVE_PWM2_MIN_PWM = 120
DEFAULT_CURVE_PWM2_MAX_PWM = 200
DEFAULT_PWM1_PATH = "/sys/class/hwmon/hwmon0/device/pwm1"
DEFAULT_PWM2_PATH = "/sys/class/hwmon/hwmon0/device/pwm2"
DEFAULT_FAN1_RPM_PATH = "/sys/class/hwmon/hwmon0/device/fan1_input"
DEFAULT_FAN2_RPM_PATH = "/sys/class/hwmon/hwmon0/device/fan2_input"
DEFAULT_TEMP1_PATH = "/sys/class/hwmon/hwmon0/device/temp1_input"
DEFAULT_TEMP2_PATH = "/sys/class/hwmon/hwmon0/device/temp2_input"
DEFAULT_TEMP3_PATH = "/sys/class/hwmon/hwmon0/device/temp3_input"
DEFAULT_HDD_DEVICE = "/dev/sda"

MIN_PWM = 0
MAX_PWM = 255
MIN_INTERVAL = 15
MAX_INTERVAL = 3600
MIN_SMART_INTERVAL = 60
MAX_SMART_INTERVAL = 3600
MIN_CURVE_TEMP = 20
MAX_CURVE_TEMP = 90
MIN_CURVE_HYSTERESIS = 0
MAX_CURVE_HYSTERESIS = 10
CONTROL_MODES = ("monitor", "fixed", "curve")

PLATFORMS = ["sensor", "binary_sensor", "number", "select"]
