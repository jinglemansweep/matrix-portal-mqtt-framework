import gc
import time
from adafruit_display_text.label import Label
from displayio import OnDiskBitmap, TileGrid
from cedargrove_palettefader.palettefader import PaletteFader
from rtc import RTC

PALETTE_GAMMA = 1.0
PALETTE_BRIGHTNESS = 0.1
PALETTE_NORMALIZE = True


class BaseSprite:
    def __init__(
        self,
        bitmap,
        pixel_shader,
        width=1,
        height=1,
        tile_width=None,
        tile_height=None,
        default_tile=0,
        x=0,
        y=0,
    ):
        self.x = float(x)
        self.y = float(y)
        self.x_target = None
        self.y_target = None
        self.x_velocity = 0
        self.y_velocity = 0
        self.x_dir_last = None
        self.y_dir_last = None
        self.is_moving = False
        self.tilegrid = TileGrid(
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

    def get_tilegrid(self):
        return self.tilegrid

    def set_position(self, x=None, y=None):
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y

    def set_velocity(self, x=0, y=0):
        if x is not None:
            self.x_velocity = x
        if y is not None:
            self.y_velocity = y

    def set_target(self, x=None, y=None):
        if x is not None:
            self.x_target = x
        if y is not None:
            self.y_target = y

    def stop(self):
        self.set_velocity(0, 0)
        self.x_target = None
        self.y_target = None

    async def tick(self):
        self._set_target_velocities()
        self._apply_velocities()
        self._update_tilegrid()

    def _set_target_velocities(self):
        if self.x_target is not None:
            if self.x_target != self.x:
                self.x_velocity = self.x_dir_last = 1 if self.x_target > self.x else -1
            else:
                self.v_velocity = 0
                self.x_target = None
        if self.y_target is not None:
            if self.y_target != self.y:
                self.y_velolicty = self.y_dir_last = 1 if self.y_target > self.y else -1
            else:
                self.y_velocity = 0
                self.y_target = None

    def _apply_velocities(self):
        self.x += self.x_velocity
        self.y += self.y_velocity

    def _update_tilegrid(self):
        self.tilegrid.x = int(self.x)
        self.tilegrid.y = int(self.y)


class ClockLabel(Label):
    def __init__(self, x, y, font, color=0x111111):
        super().__init__(text="", font=font, color=color)
        self.x = x
        self.y = y
        self.new_second = None

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


class MyLabel(Label):
    pass


def load_bitmap(
    filename,
    brightness=PALETTE_BRIGHTNESS,
    gamma=PALETTE_GAMMA,
    normalize=PALETTE_NORMALIZE,
    transparent_index=None,
):
    bitmap = OnDiskBitmap(filename)
    palette = bitmap.pixel_shader
    if transparent_index is not None:
        palette.make_transparent(transparent_index)
    palette_adj = PaletteFader(
        palette, PALETTE_BRIGHTNESS, PALETTE_GAMMA, PALETTE_NORMALIZE
    )
    gc.collect()
    return bitmap, palette_adj.palette
