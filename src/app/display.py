import asyncio
import gc
import time
from adafruit_display_text.label import Label as BaseLabel
from displayio import OnDiskBitmap, TileGrid as BaseTileGrid, Group
from cedargrove_palettefader.palettefader import PaletteFader
from rtc import RTC

from app.constants import BRIGHTNESS

PALETTE_GAMMA = 1.0
PALETTE_NORMALIZE = True


class BlankGroup(Group):
    pass


class Label(BaseLabel):
    pass


class TileGrid(BaseTileGrid):
    def set_tile(self, tile=0):
        self[0] = tile


class AnimatedTileGrid(TileGrid):
    def __init__(
        self,
        bitmap,
        pixel_shader,
        width,
        height,
        tile_width,
        tile_height,
        default_tile,
        x,
        y,
        x_range=None,
        y_range=None,
        async_delay=None,
    ):
        super().__init__(
            bitmap=bitmap,
            pixel_shader=pixel_shader,
            width=width,
            height=height,
            tile_width=tile_width,
            tile_height=tile_height,
            default_tile=default_tile,
            x=x,
            y=y,
        )
        self._animate_x_range = x_range
        self._animate_y_range = y_range
        self._animate_async_delay = async_delay
        self._animate_x = float(x)
        self._animate_y = float(y)
        self._animate_x_target = None
        self._animate_y_target = None
        self._animate_x_velocity = 0
        self._animate_y_velocity = 0
        self._animate_x_dir_last = 1
        self._animate_y_dir_last = 1
        self._animate_is_moving = False

    def set_position(self, x=None, y=None):
        if x is not None:
            self._animate_x = x
        if y is not None:
            self._animate_y = y

    def set_velocity(self, x=0, y=0):
        if x is not None:
            self._animate_x_velocity = x
        if y is not None:
            self._animate_y_velocity = y

    def set_target(self, x=None, y=None):
        if x is not None:
            self._animate_x_target = x
        if y is not None:
            self._animate_y_target = y

    def stop(self):
        self.set_velocity(0, 0)
        self._animate_x_target = None
        self._animate_y_target = None

    async def start(self):
        if isinstance(self._animate_async_delay, float):
            while True:
                self.tick()
                await asyncio.sleep(self._animate_async_delay)

    def tick(self, state):
        self._set_target_velocities()
        self._apply_velocities()
        self._update_tilegrid()

    def _set_target_velocities(self):
        if self._animate_x_target is not None:
            if self._animate_x_target != self.x:
                self._animate_x_velocity = self._animate_x_dir_last = (
                    1 if self._animate_x_target > self.x else -1
                )
            else:
                self._animate_x_velocity = 0
                self._animate_x_target = None
        if self._animate_y_target is not None:
            if self._animate_y_target != self.y:
                self._animate_y_velocity = self._animate_y_dir_last = (
                    1 if self._animate_y_target > self.y else -1
                )
            else:
                self._animate_y_velocity = 0
                self._animate_y_target = None

    def _apply_velocities(self):
        self._animate_x += self._animate_x_velocity
        self._animate_x += self._animate_y_velocity

    def _update_tilegrid(self):
        self.x = int(self._animate_x)
        self.y = int(self._animate_y)


class ClockLabel(Label):
    def __init__(self, x, y, font, color=0x111111, async_delay=None):
        super().__init__(text="", font=font, color=color)
        self.x = x
        self.y = y
        self.new_second = None
        self.async_delay = async_delay

    async def start(self):
        if isinstance(self.async_delay, float):
            while True:
                self.tick()
                await asyncio.sleep(self.async_delay)

    def tick(self):
        # frame = state["frame"]
        # self.hidden = entities.get("time_rgb").get_state().get("state") == "OFF"
        now = RTC().datetime
        ts = time.monotonic()
        if self.new_second is None or ts > self.new_second + 1:
            self.new_second = ts
            hhmmss = "{:0>2d}:{:0>2d}:{:0>2d}".format(
                now.tm_hour, now.tm_min, now.tm_sec
            )
            self.text = hhmmss


def build_splash_group(font, text="loading..."):
    group = Group()
    group.append(Label(x=1, y=3, font=font, text=text, color=0x220022))
    return group


def load_bitmap(
    filename,
    brightness=BRIGHTNESS,
    gamma=PALETTE_GAMMA,
    normalize=PALETTE_NORMALIZE,
    transparent_index=None,
):
    bitmap = OnDiskBitmap(filename)
    palette = bitmap.pixel_shader
    if transparent_index is not None:
        palette.make_transparent(transparent_index)
    palette_adj = PaletteFader(palette, brightness, gamma, normalize)
    gc.collect()
    return bitmap, palette_adj.palette
