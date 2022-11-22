import asyncio
import gc
import random
from displayio import Group

from app.display import AnimatedTileGrid, ClockLabel, load_bitmap
from app.utils import logger


spritesheet, pixel_shader = load_bitmap("/mario.bmp", transparent_index=15)
gc.collect()

SPRITE_MARIO_STILL = 0
SPRITE_MARIO_JUMP = 1
SPRITE_MARIO_WALK_START = 2  # 2,3,4
SPRITE_GOOMBA_STILL = 5
SPRITE_GOOMBA_WALK = 6
SPRITE_BRICK = 7
SPRITE_ROCK = 8
SPRITE_PIPE = 9


class MarioSprite(AnimatedTileGrid):
    def __init__(
        self,
        x,
        y,
        x_range=None,
    ):
        super().__init__(
            bitmap=spritesheet,
            pixel_shader=pixel_shader,
            width=1,
            height=1,
            tile_width=16,
            tile_height=16,
            default_tile=SPRITE_MARIO_WALK_START,
            tile_count=3,
            frames_per_tile=3,
            x=x,
            y=y,
            x_range=x_range,
        )

    def set_random_target(self):
        if self._animate_x_range is None:
            return
        self.set_target(
            random.randint(self._animate_x_range[0], self._animate_x_range[1])
        )

    def tick(self, store):
        frame = store["frame"]
        if frame % 100 == 0:
            self.set_random_target()
        self._set_tile()
        super().tick(store)

    def _set_tile(self):
        self.flip_x = self._animate_x_dir_last < 0
        if self._animate_x_velocity == 0 and self._animate_y_velocity == 0:
            self[0] = SPRITE_MARIO_STILL
        else:
            self[0] = self._animate_tile_default + self._animate_tile_idx


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
        self.mario1 = MarioSprite(8, 16, x_range=[-16, width + 16])
        self.mario2 = MarioSprite(
            40,
            height - 24,
            x_range=[-16, width + 16],
        )
        self.group.append(self.mario1)
        self.group.append(self.mario2)
        # ADD CLOCK
        clock = ClockLabel(x=1, y=3, font=font, async_delay=0.1)
        asyncio.create_task(clock.start())
        self.group.append(clock)

    def tick(
        self,
        store,
    ):
        # logger(f"theme: frame={frame}")
        self.mario1.tick(store)
        self.mario2.tick(store)
