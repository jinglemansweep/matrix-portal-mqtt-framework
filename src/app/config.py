from secrets import secrets

# CONFIG / SECRETS
DEBUG = secrets.get("debug", False)
NTP_ENABLE = secrets.get("ntp_enable", True)
NTP_INTERVAL = secrets.get("ntp_interval", 3600)
MATRIX_WIDTH = secrets.get("matrix_width", 64)
MATRIX_HEIGHT = secrets.get("matrix_height", 32)
MATRIX_BIT_DEPTH = secrets.get("matrix_bit_depth", 5)
MATRIX_COLOR_ORDER = secrets.get("matrix_color_order", "RGB")
MQTT_PREFIX = secrets.get("mqtt_prefix", "mqticker")
