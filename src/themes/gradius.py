import gc
import random
from displayio import Group, Palette
from vectorio import Circle, Rectangle
from rtc import RTC

from app.display import (
    AnimatedTileGrid,
    ClockLabel,
    CalendarLabel,
    load_bitmap,
)
from app.utils import logger


spritesheet, pixel_shader = load_bitmap("/theme.bmp", transparent_index=7)
gc.collect()

SPRITE_GRADIUS_RIGHT_HARD = 0
SPRITE_GRADIUS_RIGHT = 1
SPRITE_GRADIUS_CENTER = 2
SPRITE_GRADIUS_LEFT = 3
SPRITE_GRADIUS_LEFT_HARD = 4


class GradiusSprite(AnimatedTileGrid):
    def __init__(self, x, y, x_range=None, y_range=None):
        super().__init__(
            bitmap=spritesheet,
            pixel_shader=pixel_shader,
            width=1,
            height=1,
            tile_width=32,
            tile_height=16,
            default_tile=SPRITE_GRADIUS_CENTER,
            x=x,
            y=y,
            x_range=x_range,
            y_range=y_range,
        )

    def tick(self, store):
        frame = store["frame"]
        if frame % 30 == 0 and random.randint(1, 10) == 1:
            self.set_random_target()
        self._set_tile(frame)
        super().tick(store)

    def set_random_target(self):
        x_target = random.randint(self._animate_x_range[0], self._animate_x_range[1])
        y_target = random.randint(self._animate_y_range[0], self._animate_y_range[1])
        self.set_target(
            x=x_target,
            y=y_target,
        )

    def _set_tile(self, frame):
        current = self.y
        target = self._animate_y_target
        if target is None:
            self[0] = SPRITE_GRADIUS_CENTER
        else:
            diff = target - current
            if diff <= -4:
                self[0] = SPRITE_GRADIUS_LEFT_HARD
            elif diff >= -3 and diff <= -1:
                self[0] = SPRITE_GRADIUS_LEFT
            elif diff <= 3 and diff >= 1:
                self[0] = SPRITE_GRADIUS_RIGHT
            elif diff >= 4:
                self[0] = SPRITE_GRADIUS_RIGHT_HARD


class BackgroundStarsGroup(Group):
    def __init__(self, x, y, display_width, display_height, count=5):
        super().__init__(x=x, y=y)
        self.display_width = display_width
        self.display_height = display_height
        self.count = count
        palette = Palette(1)
        palette[0] = 0x101010
        for i in range(count):
            star = Rectangle(
                pixel_shader=palette,
                width=1,
                height=1,
                x=random.randrange(0, self.display_width),
                y=random.randrange(0, self.display_height),
            )
            self.append(star)

    def tick(self, store):
        self.x -= 1
        if self.x < 0 - self.display_width:
            self.x = self.display_width


class ForegroundStarsGroup(Group):
    def __init__(self, x, y, display_width, display_height, count=3):
        super().__init__(x=x, y=y)
        self.display_width = display_width
        self.display_height = display_height
        self.count = count
        palette = Palette(1)
        palette[0] = 0x111166
        for i in range(count):
            star = Circle(
                pixel_shader=palette,
                radius=1,
                x=random.randrange(0, self.display_width),
                y=random.randrange(0, self.display_height),
            )
            self.append(star)

    def tick(self, store):
        self.x -= 2
        if self.x < 0 - self.display_width:
            self.x = self.display_width


class Theme:
    def __init__(self, width, height, font):
        logger(f"theme setup: width={width} height={height} font={font}")
        self.width = width
        self.height = height
        # SETUP STATE
        self.actors = []
        # SETUP ROOT DISPLAYIO GROUP
        self.group = Group()
        # Add background
        self.bg1 = BackgroundStarsGroup(0, 0, width, height)
        self.group.append(self.bg1)
        self.bg2 = BackgroundStarsGroup(width, 0, width, height)
        self.group.append(self.bg2)
        self.fg1 = ForegroundStarsGroup(0, 0, width, height)
        self.group.append(self.fg1)
        self.fg2 = ForegroundStarsGroup(width, 0, width, height)
        self.group.append(self.fg2)
        # Add Pipe sprite
        ship_x = (width // 2) - 16
        ship_y = (height // 2) - 8
        self.ship = GradiusSprite(
            ship_x, ship_y, x_range=[ship_x - 8, ship_x + 8], y_range=[10, height - 16]
        )
        self.group.append(self.ship)
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
        self.ship.tick(store)
        self.bg1.tick(store)
        self.bg2.tick(store)
        self.fg1.tick(store)
        self.fg2.tick(store)
