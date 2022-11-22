import asyncio
import random
from displayio import Group

from app.display import AnimatedTileGrid, ClockLabel, load_bitmap
from app.utils import logger


spritesheet, pixel_shader = load_bitmap("/mario.bmp", transparent_index=31)

SPRITE_MARIO_R_STILL = 0
SPRITE_MARIO_R_JUMP = 1
SPRITE_MARIO_R_WALK_START = 2  # 2,3,4
SPRITE_MARIO_L_STILL = 5
SPRITE_MARIO_L_JUMP = 6
SPRITE_MARIO_L_WALK_START = 7  # 7,8,9

SPRITE_BRICK = 10
SPRITE_ROCK = 11
SPRITE_PIPE = 12
SPRITE_GOOMBA_STILL = 15
SPRITE_GOOMBA_WALK = 16


class Sprite(AnimatedTileGrid):
    # def tick(self):
    #    super().tick()
    #    self._set_target_velocities()
    #    self._apply_velocities()
    #    self._update_tilegrid()

    def set_random_tile(self):
        self.set_tile(
            random.choice(
                [
                    SPRITE_MARIO_L_STILL,
                    SPRITE_MARIO_R_WALK_START,
                    SPRITE_GOOMBA_STILL,
                    SPRITE_PIPE,
                    SPRITE_BRICK,
                    SPRITE_ROCK,
                ]
            )
        )

    pass


class Theme:
    def __init__(self, width, height, font):
        logger(f"theme setup: width={width} height={height} font={font}")
        self.width = width
        self.height = height
        self.font = font
        # SETUP STATE
        self.actors = []
        # SETUP ROOT DISPLAYIO GROUP
        self.group = Group()
        # Add random sprites
        for i in range(4):
            sprite = Sprite(
                spritesheet,
                pixel_shader,
                1,
                1,
                16,
                16,
                0,
                random.randint(0, width - 16),
                random.randint(0, height - 16),
            )
            sprite.set_random_tile()
            sprite.set_velocity(random.randint(-1, 1), random.randint(-1, 1))
            self.group.append(sprite)
            self.actors.append(sprite)
        # ADD CLOCK
        clock = ClockLabel(x=1, y=3, font=font, async_delay=0.1)
        asyncio.create_task(clock.start())
        self.group.append(clock)

    def tick(
        self,
        frame,
    ):
        # logger(f"theme: frame={frame}")
        for actor in self.actors:
            if frame % 80 == 1:
                actor.set_velocity(random.randint(-1, 2), random.randint(-1, 2))
                actor.set_random_tile()
            if actor.x < 0:
                actor.set_velocity(x=1)
            elif actor.x > self.width - 16:
                actor.set_velocity(x=-1)
            if actor.y < 0:
                actor.set_velocity(y=1)
            elif actor.y > self.height - 16:
                actor.set_velocity(y=-1)
            actor.tick()
