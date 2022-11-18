import asyncio
import board
from busio import I2C
import gc
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix
from adafruit_bitmap_font import bitmap_font
from adafruit_lis3dh import LIS3DH_I2C
from displayio import Group
from adafruit_display_text.label import Label
from rtc import RTC
from secrets import secrets

from app.config import (
    DEBUG,
    NTP_ENABLE,
    NTP_INTERVAL,
    MATRIX_WIDTH,
    MATRIX_HEIGHT,
    MATRIX_BIT_DEPTH,
    MATRIX_COLOR_ORDER,
    MQTT_PREFIX,
)
from app.storage import store
from app.gpio import poll_buttons
from app.hass import advertise_entity, OPTS_LIGHT_RGB
from app.mqtt import mqtt_poll, on_mqtt_connect, on_mqtt_disconnect, on_mqtt_message
from app.utils import logger, debug, matrix_rotation, parse_timestamp, rgb2hex

logger(
    f"debug={DEBUG} ntp_enable={NTP_ENABLE} ntp_interval={NTP_INTERVAL} mqtt_prefix={MQTT_PREFIX}"
)
logger(
    f"matrix_width={MATRIX_WIDTH} matrix_height={MATRIX_HEIGHT} matrix_bit_depth={MATRIX_BIT_DEPTH} matrix_color_order={MATRIX_COLOR_ORDER}"
)

# CONSTANTS
BUTTON_UP = 0
BUTTON_DOWN = 1

# STATIC RESOURCES
logger("loading static resources")
font_bitocra = bitmap_font.load_font("/bitocra7.bdf")

# RGB MATRIX
logger("configuring rgb matrix")
matrix = Matrix(
    width=MATRIX_WIDTH,
    height=MATRIX_HEIGHT,
    bit_depth=MATRIX_BIT_DEPTH,
    color_order=MATRIX_COLOR_ORDER,
)
accelerometer = LIS3DH_I2C(I2C(board.SCL, board.SDA), address=0x19)
_ = accelerometer.acceleration  # drain startup readings

# DISPLAY / FRAMEBUFFER
logger("configuring display/framebuffer")
display = matrix.display
display.rotation = matrix_rotation(accelerometer)
display.show(Group())
gc.collect()

# NETWORKING
logger("configuring networking")
network = Network(status_neopixel=board.NEOPIXEL, debug=DEBUG)
network.connect()
mac = network._wifi.esp.MAC_address
store["host_id"] = host_id = "{:02x}{:02x}{:02x}{:02x}".format(
    mac[0], mac[1], mac[2], mac[3]
)
gc.collect()
# NETWORK TIME
if NTP_ENABLE:
    logger("setting date/time from network")
    timestamp = network.get_local_time()
    timetuple = parse_timestamp(timestamp)
    RTC().datetime = timetuple


# MQTT
logger("configuring mqtt client")
MQTT.set_socket(socket, network._wifi.esp)
client = MQTT.MQTT(
    broker=secrets.get("mqtt_broker"),
    username=secrets.get("mqtt_user"),
    password=secrets.get("mqtt_password"),
    port=secrets.get("mqtt_port", 1883),
)
client.on_connect = on_mqtt_connect
client.on_disconnect = on_mqtt_disconnect
client.on_message = on_mqtt_message
client.connect()
gc.collect()

# HOME ASSISTANT
light_rgb_options = dict(
    color_mode=True, supported_color_modes=["rgb"], brightness=False
)
advertise_entity(client, host_id, "power", "switch")
advertise_entity(
    client,
    host_id,
    "date_rgb",
    "light",
    OPTS_LIGHT_RGB,
    dict(state="ON", color=0x00FF00, brightness=255, color_mode="rgb"),
)

# DISPLAYIO
group = Group()
display.show(group)

# LOCAL STATE
message_count = 0
prev_message = []

# EVENT LOOP
def run():
    logger("start asyncio event loop")
    gc.collect()
    while True:
        try:
            asyncio.run(main())
        finally:
            logger(f"asyncio crash, restarting")
            asyncio.new_event_loop()


async def main():
    logger("event loop started")
    asyncio.create_task(poll_buttons())
    asyncio.create_task(mqtt_poll(client))
    gc.collect()

    while True:
        await tick()
        await asyncio.sleep(0.0001)


async def tick():
    global store, message_count
    frame = store["frame"]
    logger(f"tick: frame={frame}")
    if store["message"] is not None:
        message_count += 1
        for p in range(7):
            for l in group:
                l.y -= 1
            await asyncio.sleep(0.001)
        label = Label(
            x=1,
            y=60,
            font=font_bitocra,
            color=0x111111,
            text=store["message"],
        )
        group.append(label)
        store["message"] = None

        if len(group) > 8:
            group.pop(0)
    store["frame"] += 1
    gc.collect()


# STARTUP

run()
