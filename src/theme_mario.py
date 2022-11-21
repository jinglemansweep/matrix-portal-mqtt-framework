import asyncio
import random
from displayio import Group

from app.display import BaseSprite, ClockLabel, load_bitmap
from app.utils import logger


spritesheet, pixel_shader = load_bitmap("/mario.bmp", transparent_index=31)


class Sprite(BaseSprite):
    pass


def tick(frame, width, height, actors):
    # logger(f"theme: frame={frame}")
    for actor in actors:
        if frame % 80 == 0:
            actor.set_velocity(random.randint(-1, 2), random.randint(-1, 2))
        if actor.x < 0:
            actor.set_velocity(x=1)
        elif actor.x > width - 16:
            actor.set_velocity(x=-1)
        if actor.y < 0:
            actor.set_velocity(y=1)
        elif actor.y > height - 16:
            actor.set_velocity(y=-1)


def setup(width, height, font):
    logger(f"theme setup: width={width} height={height} font={font}")
    # SETUP ROOT DISPLAYIO GROUP
    group = Group()
    actors = []
    # Add random sprites
    for i in range(4):
        sprite = Sprite(
            spritesheet,
            pixel_shader,
            1,
            1,
            16,
            16,
            random.choice([0, 15, 12]),
            random.randint(0, width - 16),
            random.randint(0, height - 16),
            async_delay=0.0001,
        )
        sprite.set_velocity(random.randint(-1, 1), random.randint(-1, 1))
        asyncio.create_task(sprite.start())
        actors.append(sprite)
        group.append(sprite.get_tilegrid())
    # ADD CLOCK
    clock = ClockLabel(x=1, y=3, font=font, async_delay=0.5)
    asyncio.create_task(clock.start())
    group.append(clock)
    # DEFINE TICK CALLBACK
    def tick_fn(frame):
        tick(frame, width, height, actors)

    return (group, tick_fn)
