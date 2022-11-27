import gc
import random
from displayio import Group

from app.display import (
    AnimatedTileGrid,
    ClockLabel,
    CalendarLabel,
    load_bitmap,
)
from app.utils import logger


spritesheet, pixel_shader = load_bitmap("/theme.bmp", transparent_index=0)
gc.collect()

SPRITE_WALK_START = 0 # 0-7
SPRITE_STAND_START = 8 # 8-11
SPRITE_DEATH = 12 # 12-15


class LemmingSprite(AnimatedTileGrid):
    def __init__(self, x, y, x_range=None, y_range=None):
        super().__init__(
            bitmap=spritesheet,
            pixel_shader=pixel_shader,
            width=1,
            height=1,
            tile_width=8,
            tile_height=8,
            default_tile=SPRITE_WALK_START,
            x=x,
            y=y,
            x_range=x_range,
            y_range=y_range,
        )
        self._animate_tile_start = SPRITE_WALK_START
        self._animate_frames_per_tile = 1
        self._animate_tile_index = 0
        self._animate_tile_count = 8   

    def tick(self, store):
        frame = store["frame"]
        if frame % 30 == 0 and random.randint(1, 10) == 1:
            self.set_random_target()
        self._animate_tiles(frame)
        self._set_tile(frame)
        super().tick(store)

    def set_random_target(self):
        x_target = random.randint(self._animate_x_range[0], self._animate_x_range[1])
        self.set_target(
            x=x_target
        )

    def _animate_tiles(self, frame):
        if frame % self._animate_frames_per_tile == 0:
            self._animate_tile_index += 1
            if self._animate_tile_index > self._animate_tile_count - 1:
                self._animate_tile_index = 0        

    def _set_tile(self, frame):
        self.flip_x = self._animate_x_dir_last < 0
        if self._animate_x_velocity == 0:
            self[0] = SPRITE_WALK_START
        else:
            self[0] = self._animate_tile_start + self._animate_tile_index            


class Theme:
    def __init__(self, width, height, font):
        logger(f"theme setup: width={width} height={height} font={font}")
        self.width = width
        self.height = height
        # SETUP STATE
        self.actors = []
        # SETUP ROOT DISPLAYIO GROUP
        self.group = Group()
        # Add Lemming sprites
        self.group_actors = Group()
        rows = 6 if height == 64 else 2
        for row in range(rows):
            for rand in range(random.randint(1, 3)):
                self.group_actors.append(
                    LemmingSprite(random.randint(-8, width), 8+(row*9), x_range=[-8, width])
                )
        self.group.append(self.group_actors)
        # ADD CLOCK / DATE
        self.clock = ClockLabel(x=33, y=2, font=font)
        self.group.append(self.clock)
        self.calendar = CalendarLabel(x=0, y=2, font=font)
        self.group.append(self.calendar)

    def tick(
        self,
        store,
        epochs
    ):
        # logger(f"theme tick: store={store} epochs={epochs}")
        self.clock.tick(store, epochs)
        self.calendar.tick(store, epochs)
        for actor in self.group_actors:
            actor.tick(store)
