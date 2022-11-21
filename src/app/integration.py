import asyncio
import board
import json
from keypad import Keys
from rtc import RTC

from app.constants import (
    NTP_INTERVAL,
    ASYNCIO_POLL_MQTT_DELAY,
    ASYNCIO_POLL_GPIO_DELAY,
    MQTT_PREFIX,
)
from app.storage import store
from app.utils import logger, parse_timestamp

mqtt_messages = []

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
    logger(f"mqtt received: topic={topic} message={message}")
    mqtt_messages.append((topic, message))
    # process_message(client, topic, message)


def on_mqtt_connect(client, userdata, flags, rc):
    logger("mqtt connected: flags={} rc={}".format(flags, rc))


def on_mqtt_disconnect(client, userdata, rc):
    logger("mqtt disconnected")


async def mqtt_poll(client, hass, timeout=ASYNCIO_POLL_MQTT_DELAY):
    while True:
        client.loop(timeout=timeout)
        if len(mqtt_messages):
            topic, message = mqtt_messages.pop(0)
            logger(f"mqtt queue: enqueued={len(mqtt_messages)} processing={topic}")
            hass.process_message(topic, message)
            del topic, message
        await asyncio.sleep(timeout)


# HOME ASSISTANT


import json

HASS_DISCOVERY_TOPIC_PREFIX = "homeassistant"
OPTS_LIGHT_RGB = dict(color_mode=True, supported_color_modes=["rgb"], brightness=False)


class HASSEntity:
    def __init__(
        self,
        client,
        store,
        host_id,
        entity_prefix,
        name,
        device_class,
        discovery_topic_prefix,
        options=None,
    ):
        if options is None:
            options = dict()
        self.client = client
        self.store = store
        self.host_id = host_id
        self.entity_prefix = entity_prefix
        self.name = name
        self.device_class = device_class
        self.options = options
        self.discovery_topic_prefix = discovery_topic_prefix
        topic_prefix = self._build_entity_topic_prefix()
        self.topic_config = f"{topic_prefix}/config"
        self.topic_command = f"{topic_prefix}/set"
        self.topic_state = f"{topic_prefix}/state"
        self.state = dict()

    def configure(self):
        auto_config = dict(
            name=self._build_full_name(),
            unique_id=self._build_full_name(),
            device_class=self.device_class,
            schema="json",
            command_topic=self.topic_command,
            state_topic=self.topic_state,
        )
        config = auto_config.copy()
        config.update(self.options)
        logger(f"hass entity configure: name={self.name} config={config}")
        self.client.publish(self.topic_config, json.dumps(config), retain=True, qos=1)
        self.client.subscribe(self.topic_command, 1)
        del auto_config, config

    def update(self, new_state=None):
        if new_state is None:
            new_state = dict()
        self.state.update(new_state)
        logger(f"hass entity update: name={self.name} state={self.state}")
        self.client.publish(
            self.topic_state, self._get_hass_state(), retain=True, qos=1
        )

    def _build_full_name(self):
        return f"{self.entity_prefix}_{self.host_id}_{self.name}"

    def _build_entity_topic_prefix(self):
        return f"{self.discovery_topic_prefix}/{self.device_class}/{self._build_full_name()}"

    def _get_hass_state(self):
        return (
            self.state["state"]
            if self.device_class == "switch"
            else json.dumps(self.get_state())
        )


class HASSManager:
    def __init__(
        self,
        client,
        store,
        host_id,
        entity_prefix=MQTT_PREFIX,
        discovery_topic_prefix=HASS_DISCOVERY_TOPIC_PREFIX,
    ):
        self.client = client
        self.store = store
        self.host_id = host_id
        self.entity_prefix = entity_prefix
        self.discovery_topic_prefix = discovery_topic_prefix
        self.store["entities"] = dict()
        logger(
            f"hass manager: host_id={host_id} discovery_topic_prefix={discovery_topic_prefix}"
        )
        pass

    def add_entity(self, name, device_class, options=None, initial_state=None):
        entity = HASSEntity(
            self.client,
            self.store,
            self.host_id,
            self.entity_prefix,
            name,
            device_class,
            self.discovery_topic_prefix,
            options,
        )
        entity.configure()
        entity.update(initial_state)
        self.store["entities"][name] = entity
        logger(
            f"hass entity created: name={name} device_class={device_class} options={options} initial_state={initial_state}"
        )
        return entity

    def process_message(self, topic, message):
        logger(f"hass process message: topic={topic} message={message}")
        for name, entity in self.store["entities"].items():
            if topic == entity.topic_command:
                logger(f"hass topic match entity={entity.name}")
                entity.update(_message_to_hass(message, entity))
                break


def _message_to_hass(message, entity):
    return (
        dict(state="ON" if message == "ON" else "OFF")
        if entity.device_class == "switch"
        else json.loads(message)
    )


# GPIO BUTTONS


async def gpio_poll(timeout=ASYNCIO_POLL_GPIO_DELAY):
    with Keys(
        (board.BUTTON_UP, board.BUTTON_DOWN), value_when_pressed=False, pull=True
    ) as keys:
        while True:
            key_event = keys.events.get()
            if key_event and key_event.pressed:
                key_number = key_event.key_number
                logger(f"button: key={key_number}")
                store["button"] = key_number
            await asyncio.sleep(timeout)
