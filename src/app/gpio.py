import asyncio
import board
from keypad import Keys

from app.storage import store
from app.utils import logger


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
