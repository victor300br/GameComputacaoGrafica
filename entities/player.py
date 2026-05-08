"""Jogador em coordenadas de tile (grade), com interpolação visual entre células."""

from __future__ import annotations

import config


class Player:
    def __init__(self, tile_x: int, tile_y: int) -> None:
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.draw_x = float(tile_x)
        self.draw_y = float(tile_y)
        self._start_x = float(tile_x)
        self._start_y = float(tile_y)
        self._target_x = float(tile_x)
        self._target_y = float(tile_y)
        self._move_t = 0.0
        self.is_moving = False
        self.facing_dx = 0
        self.facing_dy = 1

    def begin_move_to(self, tx: int, ty: int) -> None:
        if self.is_moving:
            return
        dx = tx - self.tile_x
        dy = ty - self.tile_y
        if dx != 0 or dy != 0:
            self.facing_dx = dx
            self.facing_dy = dy
        self._start_x = self.draw_x
        self._start_y = self.draw_y
        self._target_x = float(tx)
        self._target_y = float(ty)
        self._move_t = 0.0
        self.is_moving = True

    def update(self, dt: float) -> None:
        if not self.is_moving:
            return

        self._move_t += dt / config.MOVE_DURATION
        if self._move_t >= 1.0:
            self._move_t = 1.0
            self.is_moving = False

        t = self._move_t
        self.draw_x = self._start_x + (self._target_x - self._start_x) * t
        self.draw_y = self._start_y + (self._target_y - self._start_y) * t

        if not self.is_moving:
            self.tile_x = int(self._target_x)
            self.tile_y = int(self._target_y)
            self.draw_x = self._target_x
            self.draw_y = self._target_y

    def sync_draw_to_tile(self) -> None:
        """Usado ao restaurar checkpoint."""
        self.draw_x = float(self.tile_x)
        self.draw_y = float(self.tile_y)
        self._start_x = self.draw_x
        self._start_y = self.draw_y
        self._target_x = self.draw_x
        self._target_y = self.draw_y
        self._move_t = 0.0
        self.is_moving = False
