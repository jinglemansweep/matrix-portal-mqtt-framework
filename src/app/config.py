from secrets import secrets

# CONFIG / SECRETS
DEBUG = secrets.get("debug", False)
NETWORK_ENABLE = secrets.get("network_enable", True)
NTP_ENABLE = secrets.get("ntp_enable", True)
MQTT_ENABLE = secrets.get("mqtt_enable", True)
HASS_ENABLE = secrets.get("hass_enable", True)
NTP_INTERVAL = secrets.get("ntp_interval", 3600)
MATRIX_WIDTH = secrets.get("matrix_width", 64)
MATRIX_HEIGHT = secrets.get("matrix_height", 32)
MATRIX_BIT_DEPTH = secrets.get("matrix_bit_depth", 5)
MATRIX_COLOR_ORDER = secrets.get("matrix_color_order", "RGB")
MQTT_PREFIX = secrets.get("mqtt_prefix", "mqticker")

if not NETWORK_ENABLE:
    NTP_ENABLE = False
    MQTT_ENABLE = False
    HASS_ENABLE = False
