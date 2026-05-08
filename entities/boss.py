from __future__ import annotations

import math
from enum import Enum, auto

import config
from entities.player import Player
from world.tilemap import Tile


def _overlap(ax: int, ay: int, aw: int, ah: int, bx: int, by: int, bw: int, bh: int) -> bool:
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


BOSS_TILE_W = 3
BOSS_TILE_H = 2


class BossState(Enum):
    PATROL = auto()
    CHARGE = auto()
    RECOVER = auto()


class Boss:
    __slots__ = (
        "x",
        "y",
        "patrol_dir",
        "state",
        "recover_timer",
        "charge_cooldown",
        "charge_dir",
        "hp",
        "hurt_flash_remaining",
        "dying",
        "death_timer",
        "_flash_phase",
        "_anim_elapsed",
    )

    def __init__(self, tile_x: float, tile_y: int) -> None:
        self.x = tile_x
        self.y = tile_y
        self.patrol_dir: float = 1.0
        self.state = BossState.PATROL
        self.recover_timer = 0.0
        self.charge_cooldown = 1.5
        self.charge_dir = 1.0
        self.hp = config.BOSS_MAX_HP
        self.hurt_flash_remaining = 0.0
        self.dying = False
        self.death_timer = 0.0
        self._flash_phase = 0.0
        self._anim_elapsed = 0.0

    def footprint_ix(self) -> int:
        return int(math.floor(self.x))

    def is_active_threat(self) -> bool:
        return not self.dying and self.hp > 0

    def take_hit_from_stone(self) -> None:
        if self.dying or self.hp <= 0:
            return
        self.hp -= 1
        self._flash_phase = 0.0
        self.hurt_flash_remaining = config.BOSS_HIT_FLASH_SEC
        if self.hp <= 0:
            self.dying = True
            self.death_timer = config.BOSS_DEATH_DURATION_SEC
            return
        self.state = BossState.PATROL
        self.recover_timer = 0.0

    def use_white_damage_flash(self) -> bool:
        if self.dying:
            return int(self._flash_phase / config.BOSS_DEATH_FLASH_INTERVAL_SEC) % 2 == 0
        if self.hurt_flash_remaining > 0:
            return int(self._flash_phase / config.BOSS_HIT_FLASH_INTERVAL_SEC) % 2 == 0
        return False

    def render_colors(self) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        base_outer = config.COLOR_BOSS_DARK
        base_inner = config.COLOR_BOSS
        if self.use_white_damage_flash():
            w = config.COLOR_BOSS_FLASH
            return (w, w)
        return (base_outer, base_inner)

    def sprite_frame_index(self) -> int:
        step = max(config.BOSS_ANIM_FRAME_SEC, 1e-4)
        return int(self._anim_elapsed / step) % 5

    def sprite_face_right(self) -> bool:
        if self.state == BossState.CHARGE:
            return self.charge_dir > 0.0
        return self.patrol_dir > 0.0

    def _tiles_block_boss(self, tilemap, ix: int) -> bool:
        for dy in range(BOSS_TILE_H):
            for dx in range(BOSS_TILE_W):
                tx, ty = ix + dx, self.y + dy
                if not tilemap.in_bounds(tx, ty):
                    return True
                t = tilemap.get_tile(tx, ty)
                if t in (Tile.FLOOR, Tile.CHECKPOINT, Tile.EXIT):
                    continue
                return True
        return False

    def _collides_at(self, tilemap, x_float: float) -> bool:
        return self._tiles_block_boss(tilemap, int(math.floor(x_float)))

    def try_move_x(self, tilemap, delta: float) -> bool:
        if abs(delta) < 1e-9:
            return False
        steps = max(1, min(12, int(math.ceil(abs(delta) * 12))))
        step = delta / steps
        hit_wall = False
        for _ in range(steps):
            nx = self.x + step
            if self._collides_at(tilemap, nx):
                hit_wall = True
                break
            self.x = nx
        return hit_wall

    def _facing_player(self, px: float) -> int:
        center = self.x + (BOSS_TILE_W - 1) / 2.0
        if px + 0.5 > center + 1e-3:
            return 1
        if px + 0.5 < center - 1e-3:
            return -1
        return 0

    def _vertically_aligned(self, py: float) -> bool:
        return float(self.y) <= py <= float(self.y + BOSS_TILE_H - 1) + 0.999

    def _player_in_front(self, px: float, facing: int) -> bool:
        ix = self.footprint_ix()
        if facing == 1:
            return px > float(ix + BOSS_TILE_W - 1) + 0.001
        if facing == -1:
            return px < float(ix) - 0.001
        return False

    def _maybe_begin_charge(self, player: Player) -> None:
        if self.state != BossState.PATROL or self.charge_cooldown > 0:
            return
        px, py = player.draw_x, player.draw_y
        if not self._vertically_aligned(py):
            return
        fc = self._facing_player(px)
        if fc == 0 or not self._player_in_front(px, fc):
            return
        self.state = BossState.CHARGE
        self.charge_dir = float(fc)

    def update(
        self,
        dt: float,
        tilemap,
        player: Player,
        on_charge_wall_impact,
    ) -> bool:
        if self.dying:
            self.death_timer -= dt
            self._flash_phase += dt
            self._anim_elapsed += dt
            return self.death_timer <= 0

        if self.hurt_flash_remaining > 0:
            self.hurt_flash_remaining = max(0.0, self.hurt_flash_remaining - dt)
            self._flash_phase += dt

        if self.state != BossState.CHARGE:
            self.charge_cooldown = max(0.0, self.charge_cooldown - dt)

        if self.state == BossState.RECOVER:
            self.recover_timer -= dt
            if self.recover_timer <= 0:
                self.state = BossState.PATROL
            self._anim_elapsed += dt
            return False

        if self.state == BossState.PATROL:
            self._maybe_begin_charge(player)
            spd = config.BOSS_PATROL_TILES_PER_SEC * dt
            hit = self.try_move_x(tilemap, self.patrol_dir * spd)
            if hit:
                self.patrol_dir *= -1.0
            self._maybe_begin_charge(player)
            self._anim_elapsed += dt * (1.7 if self.state == BossState.CHARGE else 1.0)
            return False

        if self.state == BossState.CHARGE:
            spd = config.BOSS_CHARGE_TILES_PER_SEC * dt
            hit = self.try_move_x(tilemap, self.charge_dir * spd)
            if hit:
                self.state = BossState.RECOVER
                self.recover_timer = config.BOSS_RECOVER_SEC
                self.charge_cooldown = config.BOSS_CHARGE_COOLDOWN_SEC
                on_charge_wall_impact()
            self._anim_elapsed += dt * 1.7
            return False

        return False

    def hurts_player_now(self, player: Player, ts: int = config.TILE_SIZE) -> bool:
        if not self.is_active_threat():
            return False
        pl = int(round(player.draw_x * ts))
        pt = int(round(player.draw_y * ts))
        bl = self.footprint_ix() * ts
        bt = self.y * ts
        return _overlap(pl, pt, ts, ts, bl, bt, BOSS_TILE_W * ts, BOSS_TILE_H * ts)
