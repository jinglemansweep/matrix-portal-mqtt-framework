import asyncio
import gc
import random
from displayio import Group
from rtc import RTC

from app.display import (
    TileGrid,
    AnimatedTileGrid,
    ClockLabel,
    CalendarLabel,
    load_bitmap,
)
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
            x=x,
            y=y,
            x_range=x_range,
        )
        self.move_every_frames = random.randint(50, 200)
        self._animate_tile_start = SPRITE_MARIO_WALK_START
        self._animate_frames_per_tile = 3
        self._animate_tile_index = 0
        self._animate_tile_count = 3

    def tick(self, store):
        frame = store["frame"]
        if frame % self.move_every_frames == 0 and random.randint(1, 3) == 1:
            self.set_random_target()
        self._animate_tiles(frame)
        self._set_tile()
        super().tick(store)

    def set_random_target(self):
        if self._animate_x_range is None:
            return
        self.set_target(
            random.randint(self._animate_x_range[0], self._animate_x_range[1])
        )

    def _animate_tiles(self, frame):
        if frame % self._animate_frames_per_tile == 0:
            self._animate_tile_index += 1
            if self._animate_tile_index > self._animate_tile_count - 1:
                self._animate_tile_index = 0

    def _set_tile(self):
        self.flip_x = self._animate_x_dir_last < 0
        if self._animate_x_velocity == 0 and self._animate_y_velocity == 0:
            self[0] = SPRITE_MARIO_STILL
        else:
            self[0] = self._animate_tile_start + self._animate_tile_index


class GoombaSprite(AnimatedTileGrid):
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
            default_tile=SPRITE_GOOMBA_WALK,
            x=x,
            y=y,
            x_range=x_range,
        )
        self.move_every_frames = random.randint(50, 200)

    def tick(self, store):
        frame = store["frame"]
        if frame % self.move_every_frames == 0 and random.randint(1, 6) == 1:
            self.set_random_target()
        self._set_tile(frame)
        super().tick(store)

    def set_random_target(self):
        if self._animate_x_range is None:
            return
        self.set_target(
            random.randint(self._animate_x_range[0], self._animate_x_range[1])
        )

    def _set_tile(self, frame):
        self.flip_x = frame % 4 < 2
        if self._animate_x_velocity == 0 and self._animate_y_velocity == 0:
            self[0] = SPRITE_GOOMBA_STILL
        else:
            self[0] = SPRITE_GOOMBA_WALK


class BrickSprite(TileGrid):
    def __init__(self, x, y, width=1):
        super().__init__(
            bitmap=spritesheet,
            pixel_shader=pixel_shader,
            width=width,
            height=1,
            tile_width=16,
            tile_height=16,
            default_tile=SPRITE_BRICK,
            x=x,
            y=y,
        )


class RockSprite(TileGrid):
    def __init__(self, x, y, width=1):
        super().__init__(
            bitmap=spritesheet,
            pixel_shader=pixel_shader,
            width=width,
            height=1,
            tile_width=16,
            tile_height=16,
            default_tile=SPRITE_ROCK,
            x=x,
            y=y,
        )


class PipeSprite(AnimatedTileGrid):
    def __init__(self, x, y, width=1):
        super().__init__(
            bitmap=spritesheet,
            pixel_shader=pixel_shader,
            width=width,
            height=1,
            tile_width=16,
            tile_height=16,
            default_tile=SPRITE_PIPE,
            x=x,
            y=y,
        )
        self.y_base = y
        self.last_second = None

    def tick(self, store):
        now = RTC().datetime
        minute = now.tm_min
        second = now.tm_sec
        if self.last_second is not None or second != self.last_second:
            self.last_second = second
            self.set_target(x=None, y=self.y_base + 11 - (second // 5))
        super().tick(store)

    def set_random_target(self):
        if self._animate_x_range is None:
            return


class Theme:
    def __init__(self, width, height, font):
        logger(f"theme setup: width={width} height={height} font={font}")
        self.width = width
        self.height = height
        self.font = font
        # SETUP LOCAL VARS
        y_floor = height - 16 if height > 32 else height - 8
        y_actor = height - 32 if height > 32 else height - 24
        # SETUP STATE
        self.actors = []
        # SETUP ROOT DISPLAYIO GROUP
        self.group = Group()
        # Add Pipe sprite
        self.pipe = PipeSprite(
            random.randint(0, width - 16),
            y_actor,
        )
        self.group.append(self.pipe)
        # Add Mario sprite
        self.mario = MarioSprite(
            random.randint(0, width), y_actor, x_range=[-16, width + 16]
        )
        self.group.append(self.mario)
        # Add Goomba sprite
        self.goomba = GoombaSprite(
            random.randint(0, width), y_actor, x_range=[-16, width + 16]
        )
        self.group.append(self.goomba)
        # Add floor sprites
        floor_sprite = random.choice([RockSprite, BrickSprite])
        self.floor = floor_sprite(0, y_floor, width // 16)
        self.group.append(self.floor)
        # ADD CLOCK / DATE
        self.clock = ClockLabel(x=33, y=2, font=font)
        self.group.append(self.clock)
        self.calendar = CalendarLabel(x=0, y=2, font=font)
        self.group.append(self.calendar)

    def tick(
        self,
        store,
    ):
        # logger(f"theme: frame={frame}")
        self.clock.tick(store)
        self.calendar.tick(store)
        self.mario.tick(store)
        self.goomba.tick(store)
        self.pipe.tick(store)
