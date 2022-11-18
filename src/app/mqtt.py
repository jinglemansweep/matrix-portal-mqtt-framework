import asyncio
from app.config import MQTT_PREFIX
from app.hass import process_message
from app.storage import store


def on_mqtt_message(client, topic, message):
    print(f"MQTT > Message: Topic={topic} | Message={message}")
    process_message(client, topic, message)
    host_id = store["host_id"]
    if topic == f"{MQTT_PREFIX}_{host_id}_message":
        store["message"] = message


def on_mqtt_connect(client, userdata, flags, rc):
    print("MQTT > Connected: Flags={} | RC={}".format(flags, rc))
    host_id = store["host_id"]
    client.subscribe(f"{MQTT_PREFIX}_{host_id}_message")


def on_mqtt_disconnect(client, userdata, rc):
    print("MQTT > Disconnected")


async def mqtt_poll(client, timeout=0.000001):
    while True:
        client.loop(timeout=timeout)
        await asyncio.sleep(timeout)
