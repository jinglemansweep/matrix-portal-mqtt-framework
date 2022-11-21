from secrets import secrets

# CONFIG / SECRETS
DEBUG = secrets.get("debug", False)
NTP_INTERVAL = secrets.get("ntp_interval", 60 * 60 * 12)
MATRIX_WIDTH = secrets.get("matrix_width", 64)
MATRIX_HEIGHT = secrets.get("matrix_height", 32)
MATRIX_BIT_DEPTH = secrets.get("matrix_bit_depth", 5)
MATRIX_COLOR_ORDER = secrets.get("matrix_color_order", "RGB")
MQTT_PREFIX = secrets.get("mqtt_prefix", "mpmqtt")

# CONSTANTS
_ASYNCIO_DELAY = 0.01
ASYNCIO_POLL_GPIO_DELAY = _ASYNCIO_DELAY
ASYNCIO_POLL_MQTT_DELAY = _ASYNCIO_DELAY
ASYNCIO_LOOP_DELAY = _ASYNCIO_DELAY

BUTTON_UP = 0
BUTTON_DOWN = 1
