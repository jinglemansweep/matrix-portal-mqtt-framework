import asyncio
import board
import json
from keypad import Keys
from rtc import RTC

from app.config import MQTT_PREFIX, NTP_INTERVAL
from app.storage import store
from app.utils import logger, parse_timestamp

# NETWORK


def ntp_update(network):
    logger("setting date/time from network")
    timestamp = network.get_local_time()
    timetuple = parse_timestamp(timestamp)
    RTC().datetime = timetuple


async def ntp_poll(network):
    while True:
        ntp_update(network)
        await asyncio.sleep(NTP_INTERVAL)


# MQTT


def on_mqtt_message(client, topic, message):
    print(f"MQTT > Message: Topic={topic} | Message={message}")
    process_message(client, topic, message)


def on_mqtt_connect(client, userdata, flags, rc):
    print("MQTT > Connected: Flags={} | RC={}".format(flags, rc))


def on_mqtt_disconnect(client, userdata, rc):
    print("MQTT > Disconnected")


async def mqtt_poll(client, timeout=0.000001):
    while True:
        client.loop(timeout=timeout)
        await asyncio.sleep(timeout)


# HOME ASSISTANT

HASS_TOPIC_PREFIX = "homeassistant"
OPTS_LIGHT_RGB = dict(color_mode=True, supported_color_modes=["rgb"], brightness=False)


def advertise_entity(
    client, host_id, name, device_class="switch", options=None, initial_state=None
):
    if options is None:
        options = {}
    topic_prefix = build_entity_topic_prefix(name, device_class)
    name_full = f"{MQTT_PREFIX}_{host_id}_{name}"
    auto_config = dict(
        name=name_full,
        unique_id=name_full,
        device_class=device_class,
        schema="json",
        command_topic=f"{topic_prefix}/set",
        state_topic=f"{topic_prefix}/state",
    )
    config = auto_config.copy()
    config.update(options)
    logger(
        f"advertising hass entity: name={name} name_full={name_full} config={config}"
    )
    client.publish(f"{topic_prefix}/config", json.dumps(config), retain=True, qos=1)
    client.subscribe(f"{topic_prefix}/set", 1)
    if initial_state is not None:
        update_entity_state(client, device_class, name, initial_state)


def update_entity_state(client, device_class, name, new_state=None):
    logger(
        f"updating hass entity state: device_class={device_class} name={name} state={new_state}"
    )
    global store
    if new_state is None:
        new_state = {}
    store["entities"][name] = new_state
    payload = (
        store["entities"][name]["state"]
        if device_class == "switch"
        else json.dumps(new_state)
    )
    topic_prefix = build_entity_topic_prefix(name, device_class)
    client.publish(f"{topic_prefix}/state", payload, retain=True, qos=1)


def process_message(client, topic, message):
    if not topic.startswith(HASS_TOPIC_PREFIX):
        return
    bits = topic.split("/")
    device_class = bits[1]
    name = bits[2]
    payload = (
        dict(state="ON" if message == "ON" else "OFF")
        if device_class == "switch"
        else json.loads(message)
    )
    if topic == f"{HASS_TOPIC_PREFIX}/{device_class}/{name}/set":
        update_entity_state(client, device_class, name, payload)


def build_entity_topic_prefix(name, device_class):
    return f"{HASS_TOPIC_PREFIX}/{device_class}/{name}"


# GPIO BUTTONS


async def poll_buttons():
    with Keys(
        (board.BUTTON_UP, board.BUTTON_DOWN), value_when_pressed=False, pull=True
    ) as keys:
        while True:
            key_event = keys.events.get()
            if key_event and key_event.pressed:
                key_number = key_event.key_number
                logger(f"button: key={key_number}")
                store["button"] = key_number
            await asyncio.sleep(0.001)