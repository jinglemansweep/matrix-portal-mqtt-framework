from secrets import secrets

# CONFIG / SECRETS
DEBUG = secrets.get("debug", False)
BRIGHTNESS = secrets.get("brightness", 0.2)
NTP_TIMEZONE = secrets.get("timezone", "Europe/London")
NTP_INTERVAL = secrets.get("ntp_interval", 60 * 60 * 3)
MATRIX_WIDTH = secrets.get("matrix_width", 64)
MATRIX_HEIGHT = secrets.get("matrix_height", 32)
MATRIX_BIT_DEPTH = secrets.get("matrix_bit_depth", 4)
MATRIX_COLOR_ORDER = secrets.get("matrix_color_order", "RGB")
MQTT_PREFIX = secrets.get("mqtt_prefix", "ledclock")

# CONSTANTS
_ASYNCIO_DELAY = 0.01
ASYNCIO_LOOP_DELAY = _ASYNCIO_DELAY
ASYNCIO_GPIO_POLL_DELAY = _ASYNCIO_DELAY
ASYNCIO_MQTT_POLL_DELAY = _ASYNCIO_DELAY
ASYNCIO_MQTT_PING_INTERVAL = 30

# GPIO
BUTTON_UP = 0
BUTTON_DOWN = 1
