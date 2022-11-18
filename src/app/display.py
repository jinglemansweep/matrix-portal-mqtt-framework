from adafruit_display_text.label import Label
from displayio import Group, TileGrid


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
        self.tilegrid = TileGrid(
            bitmap,
            pixel_shader,
            width,
            height,
            tile_width,
            tile_height,
            default_tile,
            self.x,
            self.y,
        )

    def set_position(self, x=None, y=None):
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y

    def set_target(self, x=None, y=None):
        if x is not None:
            self.x_target = x
        if y is not None:
            self.y_target = y

    def tick(self):
        self._move_to_target()
        self._perform_move()

    def _move_to_target(self):
        self.x_velocity = 0
        self.y_velocity = 0
        if self.x < self.x_target:
            self.x_velocity = 1
        if self.x > self.x_target:
            self.x_velocity = -1
        if self.y < self.y_target:
            self.y_velocity = 1
        if self.y > self.y_target:
            self.y_velocity = -1

    def _perform_move(self):
        self.x += self.x_velocity
        self.y += self.y_velocity
        self.tilegrid.x = int(self.x)
        self.tilegrid.y = int(self.y)


class MyLabel(Label):
    pass
