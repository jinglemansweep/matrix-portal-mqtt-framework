import asyncio
import board
from busio import I2C
import gc
import time
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import adafruit_requests as requests
from adafruit_matrixportal.matrix import Matrix
from adafruit_matrixportal.network import Network
from adafruit_bitmap_font import bitmap_font
from adafruit_lis3dh import LIS3DH_I2C
from displayio import Group

from secrets import secrets

from app.constants import (
    DEBUG,
    BRIGHTNESS,
    NTP_INTERVAL,
    MATRIX_WIDTH,
    MATRIX_HEIGHT,
    MATRIX_BIT_DEPTH,
    MATRIX_COLOR_ORDER,
    MQTT_PREFIX,
    ASYNCIO_LOOP_DELAY,
)

from app.storage import store
from app.display import BlankGroup, build_splash_group
from app.integration import (
    mqtt_poll,
    on_mqtt_connect,
    on_mqtt_disconnect,
    on_mqtt_message,
    network_time_update,
    network_time_poll,
    gpio_poll,
    HASSManager,
)
from app.utils import logger, matrix_rotation
from theme import Theme

logger(
    f"debug={DEBUG} brightness={BRIGHTNESS} ntp_interval={NTP_INTERVAL} mqtt_prefix={MQTT_PREFIX}"
)
logger(
    f"matrix_width={MATRIX_WIDTH} matrix_height={MATRIX_HEIGHT} matrix_bit_depth={MATRIX_BIT_DEPTH} matrix_color_order={MATRIX_COLOR_ORDER}"
)


# LOCAL VARS
client = None

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
del accelerometer

# THEME
theme = Theme(width=MATRIX_WIDTH, height=MATRIX_HEIGHT, font=font_bitocra)
display.show(build_splash_group(font=font_bitocra))

# NETWORKING
logger("configuring networking")
network = Network(status_neopixel=board.NEOPIXEL, debug=DEBUG)
network.connect()
mac = network._wifi.esp.MAC_address
host_id = "{:02x}{:02x}{:02x}{:02x}".format(mac[0], mac[1], mac[2], mac[3])
requests.set_socket(socket, network._wifi.esp)
logger(f"network: host_id={host_id}")
gc.collect()

# NETWORK TIME
network_time_update(network)
gc.collect()

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
hass = HASSManager(client, store, host_id)
hass.add_entity("power", "switch", {}, {"state": "ON"})
hass.add_entity("time_seconds", "switch", {}, {"state": "OFF"})
hass.add_entity("date_show", "switch", {}, {"state": "ON"})

"""
light_rgb_options = dict(
    color_mode=True, supported_color_modes=["rgb"], brightness=False
)
"""
gc.collect()

# APP STARTUP
def run():
    logger("start asyncio event loop")
    gc.collect()
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print("EXCEPTION", e)
        finally:
            logger(f"asyncio restarting")
            time.sleep(1)
            asyncio.new_event_loop()


# START EVENT LOOP
async def main():
    logger("event loop started")
    asyncio.create_task(gpio_poll())
    asyncio.create_task(mqtt_poll(client, hass))
    asyncio.create_task(network_time_poll(network))
    while True:
        asyncio.create_task(tick())
        gc.collect()
        await asyncio.sleep(ASYNCIO_LOOP_DELAY)


# EVENT LOOP TICK HANDLER
async def tick():
    global store
    frame = store["frame"]
    entities = store["entities"]
    display.show(
        theme.group if entities["power"].state["state"] == "ON" else BlankGroup()
    )
    if frame % 100 == 0:
        logger(f"tick: frame={frame} entity_count={len(entities)}")
    theme.tick(store)
    store["frame"] += 1


# STARTUP

run()
