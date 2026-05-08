"""Estado principal: mapa + jogador + física de pedras + checkpoint + troca de fase."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import config
import pygame
from entities.boss import BOSS_TILE_H, BOSS_TILE_W, Boss
from entities.player import Player
from game.boss_music_event import BOSS_MUSIC_TRACK_ENDED
from render.framebuffer import Framebuffer
from world.tilemap import Tile, TileMap

_LEVEL_DIR = Path(__file__).resolve().parent.parent / "levels"
_ASSET_DIR = Path(__file__).resolve().parent.parent / "assets"
LEVEL_FILES: list[str] = ["tutorial.txt", "level2.txt", "level3.txt", "ending.txt"]


def _aabb_overlap(
    ax: int,
    ay: int,
    aw: int,
    ah: int,
    bx: int,
    by: int,
    bw: int,
    bh: int,
) -> bool:
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


@dataclass
class StoneFallAnim:
    x: int
    y0: int
    y1: int
    t: float = 0.0


class Game:
    def __init__(self) -> None:
        self._level_index = 0
        self._stone_anims: list[StoneFallAnim] = []
        self.tilemap: TileMap
        self.player: Player
        self.buffer: Framebuffer
        self._respawn_map: TileMap
        self._respawn_player: tuple[int, int]
        self._was_moving = False
        self._breakable_sprite_raw: pygame.Surface | None = self._load_breakable_sprite()
        self._breakable_sprite_scaled: pygame.Surface | None = None
        self._breakable_sprite_scaled_ts: int = -1
        self._stone_sprite_raw: pygame.Surface | None = self._load_stone_sprite()
        self._stone_sprite_scaled: pygame.Surface | None = None
        self._stone_sprite_scaled_ts: int = -1
        self._checkpoint_sprite_raw: pygame.Surface | None = self._load_checkpoint_sprite()
        self._checkpoint_sprite_scaled: pygame.Surface | None = None
        self._checkpoint_sprite_scaled_ts: int = -1
        self._door_sprite_raw: pygame.Surface | None = self._load_door_sprite()
        self._door_sprite_scaled: pygame.Surface | None = None
        self._door_sprite_scaled_ts: int = -1
        self._exit_stairs_sprite_raw: pygame.Surface | None = self._load_exit_stairs_sprite()
        self._exit_stairs_sprite_scaled: pygame.Surface | None = None
        self._exit_stairs_sprite_scaled_ts: int = -1
        self._chest_sprite_raw: pygame.Surface | None = self._load_chest_sprite()
        self._chest_sprite_scaled: pygame.Surface | None = None
        self._chest_sprite_scaled_ts: int = -1
        self._player_up_raw: pygame.Surface | None = self._load_player_up_sprite()
        self._player_down_raw: pygame.Surface | None = self._load_player_down_sprite()
        self._player_side_raw: pygame.Surface | None = self._load_player_side_sprite()
        self._player_up_scaled: pygame.Surface | None = None
        self._player_down_scaled: pygame.Surface | None = None
        self._player_side_scaled: pygame.Surface | None = None
        self._player_sprite_scaled_ts: int = -1
        self._wall_sprite_raw: pygame.Surface | None = self._load_wall_sprite()
        self._wall_sprite_scaled: pygame.Surface | None = None
        self._wall_sprite_scaled_ts: int = -1
        self._emerald_on_sprite_raw: pygame.Surface | None = self._load_emerald_on_sprite()
        self._emerald_off_sprite_raw: pygame.Surface | None = self._load_emerald_off_sprite()
        self._emerald_on_sprite_scaled: pygame.Surface | None = None
        self._emerald_off_sprite_scaled: pygame.Surface | None = None
        self._emerald_sprite_scaled_ts: int = -1
        self._emerald_blink_elapsed = 0.0
        self._game_over = False
        self._boss: Boss | None = None
        self._boss_reset: tuple[float, int] | None = None
        self._rock_drop_cols: tuple[int, int, int] | None = None
        self._boss_drop_index = 0
        self._game_over_retry_screen_rect: pygame.Rect | None = None
        self._game_over_menu_screen_rect: pygame.Rect | None = None
        self._go_font_title: pygame.font.Font | None = None
        self._go_font_ui: pygame.font.Font | None = None
        self._boss_frames_raw: list[pygame.Surface] | None = self._load_boss_sprite_frames()
        self._boss_frames_scaled: list[pygame.Surface] | None = None
        self._boss_frames_cache_key: tuple[int, float] | None = None
        self._load_level(self._level_index)

    def _load_breakable_sprite(self) -> pygame.Surface | None:
        sprite_candidates = [_ASSET_DIR / "grass.png", _ASSET_DIR / "grama.png"]
        return self._load_first_existing_sprite(sprite_candidates)

    def _load_stone_sprite(self) -> pygame.Surface | None:
        sprite_candidates = [_ASSET_DIR / "stone.png", _ASSET_DIR / "pedra.png"]
        return self._load_first_existing_sprite(sprite_candidates)

    def _load_checkpoint_sprite(self) -> pygame.Surface | None:
        sprite_candidates = [_ASSET_DIR / "checkpoint.png", _ASSET_DIR / "salvamento.png"]
        return self._load_first_existing_sprite(sprite_candidates)

    def _load_door_sprite(self) -> pygame.Surface | None:
        sprite_candidates = [_ASSET_DIR / "door.png", _ASSET_DIR / "porta.png"]
        return self._load_first_existing_sprite(sprite_candidates)

    def _load_exit_stairs_sprite(self) -> pygame.Surface | None:
        sprite_candidates = [_ASSET_DIR / "exit_stairs.png", _ASSET_DIR / "saida.png"]
        return self._load_first_existing_sprite(sprite_candidates)

    def _load_chest_sprite(self) -> pygame.Surface | None:
        sprite_candidates = [_ASSET_DIR / "chest.png", _ASSET_DIR / "bau.png"]
        return self._load_first_existing_sprite(sprite_candidates)

    def _load_player_up_sprite(self) -> pygame.Surface | None:
        return self._load_first_existing_sprite(
            [_ASSET_DIR / "player_up.png", _ASSET_DIR / "olhar_cima.png"]
        )

    def _load_player_down_sprite(self) -> pygame.Surface | None:
        return self._load_first_existing_sprite(
            [_ASSET_DIR / "player_down.png", _ASSET_DIR / "olhar_baixo.png"]
        )

    def _load_player_side_sprite(self) -> pygame.Surface | None:
        return self._load_first_existing_sprite(
            [_ASSET_DIR / "player_side.png", _ASSET_DIR / "olhar_lados.png"]
        )

    def _load_wall_sprite(self) -> pygame.Surface | None:
        sprite_candidates = [_ASSET_DIR / "wall.png", _ASSET_DIR / "parede.png"]
        return self._load_first_existing_sprite(sprite_candidates)

    def _load_emerald_on_sprite(self) -> pygame.Surface | None:
        sprite_candidates = [_ASSET_DIR / "emerald_on.png", _ASSET_DIR / "gema_ligada.png"]
        return self._load_first_existing_sprite(sprite_candidates)

    def _load_emerald_off_sprite(self) -> pygame.Surface | None:
        sprite_candidates = [_ASSET_DIR / "emerald_off.png", _ASSET_DIR / "gema_desligada.png"]
        return self._load_first_existing_sprite(sprite_candidates)

    def _load_boss_sprite_frames(self) -> list[pygame.Surface] | None:
        boss_dir = _ASSET_DIR / "boss"
        frames: list[pygame.Surface] = []
        for i in range(1, 6):
            path = boss_dir / f"boss_{i}.png"
            if not path.exists():
                return None
            try:
                surf = pygame.image.load(str(path))
                try:
                    surf = surf.convert_alpha()
                except pygame.error:
                    pass
                frames.append(surf)
            except pygame.error:
                return None
        return frames

    def _get_boss_frames_scaled(self, tile_size: int) -> list[pygame.Surface] | None:
        if not self._boss_frames_raw or len(self._boss_frames_raw) != 5:
            return None
        scale = config.BOSS_VISUAL_SCALE
        cache_key: tuple[int, float] = (tile_size, scale)
        if self._boss_frames_scaled is not None and self._boss_frames_cache_key == cache_key:
            return self._boss_frames_scaled
        fw = max(1, int(BOSS_TILE_W * tile_size * scale))
        fh = max(1, int(BOSS_TILE_H * tile_size * scale))
        scaled: list[pygame.Surface] = []
        for src in self._boss_frames_raw:
            if src.get_width() == fw and src.get_height() == fh:
                scaled.append(src)
            else:
                scaled.append(pygame.transform.scale(src, (fw, fh)))
        self._boss_frames_scaled = scaled
        self._boss_frames_cache_key = cache_key
        return scaled

    def _blit_boss_sprite_with_flash(
        self, target: pygame.Surface, sprite: pygame.Surface, pos: tuple[int, int], white_flash: bool
    ) -> None:
        if white_flash:
            fx = sprite.copy()
            fx.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_MAX)
            target.blit(fx, pos)
        else:
            target.blit(sprite, pos)

    def _load_first_existing_sprite(self, candidates: list[Path]) -> pygame.Surface | None:
        for path in candidates:
            if not path.exists():
                continue
            try:
                loaded = pygame.image.load(str(path))
                try:
                    return loaded.convert_alpha()
                except pygame.error:
                    return loaded
            except pygame.error:
                continue
        return None

    def _crop_visible_sprite_area(self, src: pygame.Surface) -> pygame.Surface:
        """Remove bordas transparentes para o conteúdo preencher melhor o tile."""
        bounds = src.get_bounding_rect()
        if bounds.width <= 0 or bounds.height <= 0:
            return src
        if bounds.size == src.get_size():
            return src
        return src.subsurface(bounds).copy()

    def _get_breakable_sprite(self, tile_size: int) -> pygame.Surface | None:
        src = self._breakable_sprite_raw
        if src is None:
            return None
        if self._breakable_sprite_scaled is not None and self._breakable_sprite_scaled_ts == tile_size:
            return self._breakable_sprite_scaled
        trimmed = self._crop_visible_sprite_area(src)
        if trimmed.get_width() == tile_size and trimmed.get_height() == tile_size:
            self._breakable_sprite_scaled = trimmed
        else:
            self._breakable_sprite_scaled = pygame.transform.scale(trimmed, (tile_size, tile_size))
        self._breakable_sprite_scaled_ts = tile_size
        return self._breakable_sprite_scaled

    def _get_stone_sprite(self, tile_size: int) -> pygame.Surface | None:
        src = self._stone_sprite_raw
        if src is None:
            return None
        if self._stone_sprite_scaled is not None and self._stone_sprite_scaled_ts == tile_size:
            return self._stone_sprite_scaled
        trimmed = self._crop_visible_sprite_area(src)
        if trimmed.get_width() == tile_size and trimmed.get_height() == tile_size:
            self._stone_sprite_scaled = trimmed
        else:
            self._stone_sprite_scaled = pygame.transform.scale(trimmed, (tile_size, tile_size))
        self._stone_sprite_scaled_ts = tile_size
        return self._stone_sprite_scaled

    def _get_checkpoint_sprite(self, tile_size: int) -> pygame.Surface | None:
        src = self._checkpoint_sprite_raw
        if src is None:
            return None
        if self._checkpoint_sprite_scaled is not None and self._checkpoint_sprite_scaled_ts == tile_size:
            return self._checkpoint_sprite_scaled
        trimmed = self._crop_visible_sprite_area(src)
        if trimmed.get_width() == tile_size and trimmed.get_height() == tile_size:
            self._checkpoint_sprite_scaled = trimmed
        else:
            self._checkpoint_sprite_scaled = pygame.transform.scale(trimmed, (tile_size, tile_size))
        self._checkpoint_sprite_scaled_ts = tile_size
        return self._checkpoint_sprite_scaled

    def _get_door_sprite(self, tile_size: int) -> pygame.Surface | None:
        src = self._door_sprite_raw
        if src is None:
            return None
        if self._door_sprite_scaled is not None and self._door_sprite_scaled_ts == tile_size:
            return self._door_sprite_scaled
        trimmed = self._crop_visible_sprite_area(src)
        if trimmed.get_width() == tile_size and trimmed.get_height() == tile_size:
            self._door_sprite_scaled = trimmed
        else:
            self._door_sprite_scaled = pygame.transform.scale(trimmed, (tile_size, tile_size))
        self._door_sprite_scaled_ts = tile_size
        return self._door_sprite_scaled

    def _get_exit_stairs_sprite(self, tile_size: int) -> pygame.Surface | None:
        src = self._exit_stairs_sprite_raw
        if src is None:
            return None
        if (
            self._exit_stairs_sprite_scaled is not None
            and self._exit_stairs_sprite_scaled_ts == tile_size
        ):
            return self._exit_stairs_sprite_scaled
        trimmed = self._crop_visible_sprite_area(src)
        if trimmed.get_width() == tile_size and trimmed.get_height() == tile_size:
            self._exit_stairs_sprite_scaled = trimmed
        else:
            self._exit_stairs_sprite_scaled = pygame.transform.scale(trimmed, (tile_size, tile_size))
        self._exit_stairs_sprite_scaled_ts = tile_size
        return self._exit_stairs_sprite_scaled

    def _get_chest_sprite(self, tile_size: int) -> pygame.Surface | None:
        src = self._chest_sprite_raw
        if src is None:
            return None
        if self._chest_sprite_scaled is not None and self._chest_sprite_scaled_ts == tile_size:
            return self._chest_sprite_scaled
        trimmed = self._crop_visible_sprite_area(src)
        if trimmed.get_width() == tile_size and trimmed.get_height() == tile_size:
            self._chest_sprite_scaled = trimmed
        else:
            self._chest_sprite_scaled = pygame.transform.scale(trimmed, (tile_size, tile_size))
        self._chest_sprite_scaled_ts = tile_size
        return self._chest_sprite_scaled

    def _get_wall_sprite(self, tile_size: int) -> pygame.Surface | None:
        src = self._wall_sprite_raw
        if src is None:
            return None
        if self._wall_sprite_scaled is not None and self._wall_sprite_scaled_ts == tile_size:
            return self._wall_sprite_scaled
        trimmed = self._crop_visible_sprite_area(src)
        if trimmed.get_width() == tile_size and trimmed.get_height() == tile_size:
            self._wall_sprite_scaled = trimmed
        else:
            self._wall_sprite_scaled = pygame.transform.scale(trimmed, (tile_size, tile_size))
        self._wall_sprite_scaled_ts = tile_size
        return self._wall_sprite_scaled

    def _ensure_player_sprites_scaled(self, tile_size: int) -> None:
        if self._player_sprite_scaled_ts == tile_size:
            return

        def one(raw: pygame.Surface | None) -> pygame.Surface | None:
            if raw is None:
                return None
            trimmed = self._crop_visible_sprite_area(raw)
            if trimmed.get_width() == tile_size and trimmed.get_height() == tile_size:
                return trimmed
            return pygame.transform.scale(trimmed, (tile_size, tile_size))

        self._player_up_scaled = one(self._player_up_raw)
        self._player_down_scaled = one(self._player_down_raw)
        self._player_side_scaled = one(self._player_side_raw)
        self._player_sprite_scaled_ts = tile_size

    def _get_emerald_sprites(self, tile_size: int) -> tuple[pygame.Surface | None, pygame.Surface | None]:
        on_src = self._emerald_on_sprite_raw
        off_src = self._emerald_off_sprite_raw
        if on_src is None and off_src is None:
            return None, None
        if self._emerald_sprite_scaled_ts != tile_size:
            self._emerald_on_sprite_scaled = None
            self._emerald_off_sprite_scaled = None
        if on_src is not None and self._emerald_on_sprite_scaled is None:
            trimmed_on = self._crop_visible_sprite_area(on_src)
            if trimmed_on.get_width() == tile_size and trimmed_on.get_height() == tile_size:
                self._emerald_on_sprite_scaled = trimmed_on
            else:
                self._emerald_on_sprite_scaled = pygame.transform.scale(trimmed_on, (tile_size, tile_size))
        if off_src is not None and self._emerald_off_sprite_scaled is None:
            trimmed_off = self._crop_visible_sprite_area(off_src)
            if trimmed_off.get_width() == tile_size and trimmed_off.get_height() == tile_size:
                self._emerald_off_sprite_scaled = trimmed_off
            else:
                self._emerald_off_sprite_scaled = pygame.transform.scale(trimmed_off, (tile_size, tile_size))
        self._emerald_sprite_scaled_ts = tile_size
        return self._emerald_on_sprite_scaled, self._emerald_off_sprite_scaled

    def _level_path(self, index: int) -> Path:
        return _LEVEL_DIR / LEVEL_FILES[index]

    def _load_level(self, index: int) -> None:
        self._level_index = index
        self._stone_anims.clear()
        parsed = TileMap.from_file(self._level_path(index))
        self.tilemap = parsed.tilemap
        spawn = parsed.spawn
        self.player = Player(spawn[0], spawn[1])
        self.buffer = Framebuffer(
            self.tilemap.width * config.TILE_SIZE,
            self.tilemap.height * config.TILE_SIZE,
        )
        self._respawn_map = self.tilemap.clone()
        self._respawn_player = (self.player.tile_x, self.player.tile_y)
        self._maybe_open_gem_doors()

        self._game_over = False
        self._boss_drop_index = 0
        if parsed.boss_origin is not None and parsed.rock_drop_columns is not None:
            bx, by = parsed.boss_origin
            self._boss = Boss(bx, by)
            self._boss_reset = (bx, by)
            self._rock_drop_cols = parsed.rock_drop_columns
        else:
            self._boss = None
            self._boss_reset = None
            self._rock_drop_cols = None

        self._sync_boss_arena_music()

    @property
    def is_boss_arena(self) -> bool:
        if self._level_index < 0 or self._level_index >= len(LEVEL_FILES):
            return False
        return LEVEL_FILES[self._level_index] == "level3.txt"

    def _start_boss_arena_music(self) -> None:
        path = Path(config.BOSS_MUSIC_PATH)
        if not path.is_file():
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.play(0, start=config.BOSS_MUSIC_START_SEC)
            pygame.mixer.music.set_endevent(BOSS_MUSIC_TRACK_ENDED)
        except pygame.error:
            pass

    def _stop_boss_arena_music(self) -> None:
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.set_endevent()
        except pygame.error:
            pass

    def _sync_boss_arena_music(self) -> None:
        if self.is_boss_arena:
            self._start_boss_arena_music()
        else:
            self._stop_boss_arena_music()

    def on_boss_music_track_ended(self) -> None:
        if self.is_boss_arena:
            self._start_boss_arena_music()

    def _emerald_count(self) -> int:
        return sum(
            1
            for ty in range(self.tilemap.height)
            for tx in range(self.tilemap.width)
            if self.tilemap.get_tile(tx, ty) == Tile.EMERALD
        )

    def _maybe_open_gem_doors(self) -> None:
        if self._emerald_count() > 0:
            return
        for ty in range(self.tilemap.height):
            for tx in range(self.tilemap.width):
                if self.tilemap.get_tile(tx, ty) == Tile.GEM_DOOR:
                    self.tilemap.set_tile(tx, ty, Tile.FLOOR)

    def _go_to_next_level(self) -> None:
        nxt = self._level_index + 1
        if nxt < len(LEVEL_FILES):
            self._load_level(nxt)

    def handle_input(self, dx: int, dy: int) -> None:
        if self._game_over:
            return
        if dx == 0 and dy == 0:
            return
        self._try_player_move(dx, dy)

    @property
    def is_game_over(self) -> bool:
        return self._game_over

    def try_again_from_game_over(self) -> None:
        if not self._game_over:
            return
        self._load_level(self._level_index)

    def restore_checkpoint(self) -> None:
        if self._game_over:
            return
        self.tilemap = self._respawn_map.clone()
        self._stone_anims.clear()
        px, py = self._respawn_player
        self.player.tile_x = px
        self.player.tile_y = py
        self.player.sync_draw_to_tile()
        if self._boss_reset is not None:
            self._boss = Boss(self._boss_reset[0], self._boss_reset[1])
            self._boss_drop_index = 0

    def _save_checkpoint(self) -> None:
        self._respawn_map = self.tilemap.clone()
        self._respawn_player = (self.player.tile_x, self.player.tile_y)

    def _player_aabb_pixels(self) -> tuple[int, int, int, int]:
        ts = config.TILE_SIZE
        left = int(round(self.player.draw_x * ts))
        top = int(round(self.player.draw_y * ts))
        return (left, top, ts, ts)

    def _player_aabb_at_tile(self, gx: float, gy: float) -> tuple[int, int, int, int]:
        ts = config.TILE_SIZE
        left = int(round(gx * ts))
        top = int(round(gy * ts))
        return (left, top, ts, ts)

    def _stone_fall_aabb_pixels(self, anim: StoneFallAnim, t: float) -> tuple[int, int, int, int]:
        ts = config.TILE_SIZE
        dy = anim.y1 - anim.y0
        top = int(round(anim.y0 * ts + t * dy * ts))
        left = anim.x * ts
        return (left, top, ts, ts)

    def _stone_fall_overlaps_player(self, anim: StoneFallAnim, t: float) -> bool:
        sl, st, sw, sh = self._stone_fall_aabb_pixels(anim, t)
        pl, pt, pw, ph = self._player_aabb_pixels()
        return _aabb_overlap(sl, st, sw, sh, pl, pt, pw, ph)

    def _fall_sweep_overlaps_player(self, tx: int, y0: int, y1: int) -> bool:
        """União vertical dos tiles y0..y1 na coluna tx (pedra + célula de aterrissagem)."""
        ts = config.TILE_SIZE
        pl, pt, pw, ph = self._player_aabb_pixels()
        left = tx * ts
        top = y0 * ts
        w = ts
        h = (y1 - y0 + 1) * ts
        return _aabb_overlap(pl, pt, pw, ph, left, top, w, h)

    def _player_target_overlaps_any_stone_anim(self, nx: int, ny: int) -> bool:
        pl, pt, pw, ph = self._player_aabb_at_tile(float(nx), float(ny))
        for anim in self._stone_anims:
            sl, st, sw, sh = self._stone_fall_aabb_pixels(anim, anim.t)
            if _aabb_overlap(pl, pt, pw, ph, sl, st, sw, sh):
                return True
        return False

    def _boss_blocks_tile(self, tx: int, ty: int) -> bool:
        if self._boss is None or not self._boss.is_active_threat():
            return False
        ix = self._boss.footprint_ix()
        if ty < self._boss.y or ty >= self._boss.y + BOSS_TILE_H:
            return False
        return ix <= tx < ix + BOSS_TILE_W

    def _boss_landing_hits_active_boss(self, anim: StoneFallAnim) -> bool:
        if self._boss is None or not self._boss.is_active_threat():
            return False
        ix = self._boss.footprint_ix()
        if anim.x < ix or anim.x >= ix + BOSS_TILE_W:
            return False
        return self._boss.y <= anim.y1 < self._boss.y + BOSS_TILE_H

    def _on_boss_charge_wall_hit(self) -> None:
        if self._rock_drop_cols is None:
            return
        if self._boss is None or not self._boss.is_active_threat():
            return
        cx = self._rock_drop_cols[self._boss_drop_index % 3]
        self._boss_drop_index += 1
        self._spawn_ceiling_stone(cx)

    def _spawn_ceiling_stone(self, cx: int) -> None:
        if not self.tilemap.in_bounds(cx, 1):
            return
        h = self.tilemap.height
        for y in range(1, h - 1):
            if not self.tilemap.in_bounds(cx, y):
                break
            t = self.tilemap.get_tile(cx, y)
            if t == Tile.STONE:
                continue
            if t in (Tile.WALL, Tile.INVIS_WALL, Tile.GEM_DOOR):
                break
            if t in (Tile.FLOOR, Tile.CHECKPOINT, Tile.EXIT, Tile.BREAKABLE, Tile.CHEST):
                self.tilemap.set_tile(cx, y, Tile.STONE)
                return

    def _enter_game_over(self) -> None:
        self._game_over = True
        self.player.is_moving = False
        self.player.tile_x = int(round(self.player.draw_x))
        self.player.tile_y = int(round(self.player.draw_y))
        self.player.draw_x = float(self.player.tile_x)
        self.player.draw_y = float(self.player.tile_y)

    def _try_player_move(self, dx: int, dy: int) -> None:
        if self._game_over:
            return
        if self.player.is_moving:
            return
        px, py = self.player.tile_x, self.player.tile_y
        nx, ny = px + dx, py + dy
        if not self.tilemap.in_bounds(nx, ny):
            return

        if self._boss_blocks_tile(nx, ny):
            return

        if self._player_target_overlaps_any_stone_anim(nx, ny):
            return

        t = self.tilemap.get_tile(nx, ny)

        if t in (Tile.WALL, Tile.INVIS_WALL, Tile.GEM_DOOR):
            return

        if t in (Tile.FLOOR, Tile.CHECKPOINT, Tile.EXIT, Tile.CHEST):
            self.player.begin_move_to(nx, ny)
            return

        if t == Tile.BREAKABLE:
            self.tilemap.set_tile(nx, ny, Tile.FLOOR)
            self.player.begin_move_to(nx, ny)
            return

        if t == Tile.EMERALD:
            self.tilemap.set_tile(nx, ny, Tile.FLOOR)
            self.player.begin_move_to(nx, ny)
            self._maybe_open_gem_doors()
            return

        if t == Tile.STONE:
            if dy != 0:
                return
            nx2, ny2 = nx + dx, ny + dy
            if not self.tilemap.in_bounds(nx2, ny2):
                return
            if self._player_target_overlaps_any_stone_anim(nx2, ny2):
                return
            if self._boss is not None and self._boss_blocks_tile(nx2, ny2):
                self.tilemap.set_tile(nx, ny, Tile.FLOOR)
                self._boss.take_hit_from_stone()
                self.player.begin_move_to(nx, ny)
                return
            t2 = self.tilemap.get_tile(nx2, ny2)
            if t2 not in (Tile.FLOOR, Tile.CHECKPOINT, Tile.EXIT, Tile.CHEST):
                return
            self.tilemap.set_tile(nx2, ny2, Tile.STONE)
            self.tilemap.set_tile(nx, ny, Tile.FLOOR)
            self.player.begin_move_to(nx, ny)

    def _tile_supports_falling_stone(self, tx: int, ty: int) -> bool:
        if not self.tilemap.in_bounds(tx, ty):
            return False
        t = self.tilemap.get_tile(tx, ty)
        return t in (Tile.FLOOR, Tile.CHECKPOINT, Tile.EXIT, Tile.CHEST)

    def _can_stone_fall_from_to(self, tx: int, y0: int, y1: int) -> bool:
        if not self._tile_supports_falling_stone(tx, y1):
            return False
        if self._fall_sweep_overlaps_player(tx, y0, y1):
            return False
        return True

    def _clamp_stone_fall_t(self, anim: StoneFallAnim, want: float) -> float:
        want = min(1.0, max(anim.t, want))
        if not self._stone_fall_overlaps_player(anim, want):
            return want
        lo, hi = anim.t, want
        if self._stone_fall_overlaps_player(anim, lo):
            return anim.t
        for _ in range(24):
            mid = (lo + hi) / 2
            if self._stone_fall_overlaps_player(anim, mid):
                hi = mid
            else:
                lo = mid
        return lo

    def _update_stone_fall_anims(self, dt: float) -> None:
        dur = config.STONE_FALL_DURATION
        remaining: list[StoneFallAnim] = []
        for anim in self._stone_anims:
            target_t = min(1.0, anim.t + dt / dur)
            anim.t = self._clamp_stone_fall_t(anim, target_t)
            if anim.t >= 1.0 - 1e-5:
                anim.t = 1.0
                self.tilemap.set_tile(anim.x, anim.y0, Tile.FLOOR)
                if self._boss_landing_hits_active_boss(anim):
                    self._boss.take_hit_from_stone()
                else:
                    self.tilemap.set_tile(anim.x, anim.y1, Tile.STONE)
                self._maybe_open_gem_doors()
            else:
                remaining.append(anim)
        self._stone_anims = remaining

    def _try_start_stone_falls(self) -> None:
        busy_cols = {a.x for a in self._stone_anims}
        busy_src = {(a.x, a.y0) for a in self._stone_anims}
        busy_dst = {(a.x, a.y1) for a in self._stone_anims}
        w, h = self.tilemap.width, self.tilemap.height
        for tx in range(w):
            if tx in busy_cols:
                continue
            for ty in range(h - 2, -1, -1):
                if self.tilemap.get_tile(tx, ty) != Tile.STONE:
                    continue
                if (tx, ty) in busy_src:
                    continue
                by = ty + 1
                if (tx, by) in busy_src or (tx, by) in busy_dst:
                    continue
                if not self._can_stone_fall_from_to(tx, ty, by):
                    continue
                self._stone_anims.append(StoneFallAnim(tx, ty, by, 0.0))
                break

    def _apply_stone_physics(self, dt: float) -> None:
        self._update_stone_fall_anims(dt)
        self._try_start_stone_falls()

    def _on_player_landed(self) -> None:
        tx, ty = self.player.tile_x, self.player.tile_y
        if self.tilemap.get_tile(tx, ty) == Tile.EXIT:
            self._go_to_next_level()
            return
        if self.tilemap.get_tile(tx, ty) == Tile.CHECKPOINT:
            self._save_checkpoint()

    def update(self, dt: float) -> None:
        if self._game_over:
            return
        self._emerald_blink_elapsed += dt
        self._was_moving = self.player.is_moving
        self.player.update(dt)
        if self._boss is not None:
            remove_boss = self._boss.update(
                dt, self.tilemap, self.player, self._on_boss_charge_wall_hit
            )
            if remove_boss:
                self._boss = None
            elif self._boss is not None and self._boss.hurts_player_now(self.player):
                self._enter_game_over()
                return
        if self._was_moving and not self.player.is_moving:
            self._on_player_landed()
        self._apply_stone_physics(dt)

    def _tile_color(self, tile: Tile) -> tuple[int, int, int]:
        if tile == Tile.WALL:
            return config.COLOR_WALL
        if tile == Tile.INVIS_WALL:
            return config.COLOR_FLOOR
        if tile == Tile.CHECKPOINT:
            return config.COLOR_CHECKPOINT
        if tile == Tile.BREAKABLE:
            return config.COLOR_BREAKABLE
        if tile == Tile.STONE:
            return config.COLOR_STONE
        if tile == Tile.EXIT:
            return config.COLOR_EXIT
        if tile == Tile.EMERALD:
            return config.COLOR_EMERALD
        if tile == Tile.GEM_DOOR:
            return config.COLOR_GEM_DOOR
        if tile == Tile.CHEST:
            return config.COLOR_CHEST
        return config.COLOR_FLOOR

    def render(self) -> None:
        self.buffer.clear(config.COLOR_BACKGROUND)
        ts = config.TILE_SIZE
        anim_sources = {(a.x, a.y0) for a in self._stone_anims}
        breakable_sprite = self._get_breakable_sprite(ts)
        stone_sprite = self._get_stone_sprite(ts)
        checkpoint_sprite = self._get_checkpoint_sprite(ts)
        door_sprite = self._get_door_sprite(ts)
        exit_stairs_sprite = self._get_exit_stairs_sprite(ts)
        chest_sprite = self._get_chest_sprite(ts)
        wall_sprite = self._get_wall_sprite(ts)
        emerald_on_sprite, emerald_off_sprite = self._get_emerald_sprites(ts)
        emerald_blink_on = (
            int(self._emerald_blink_elapsed / config.EMERALD_BLINK_INTERVAL) % 2 == 0
            if config.EMERALD_BLINK_INTERVAL > 0
            else True
        )
        emerald_sprite = emerald_on_sprite if emerald_blink_on else emerald_off_sprite
        if emerald_sprite is None:
            emerald_sprite = emerald_on_sprite or emerald_off_sprite

        for ty in range(self.tilemap.height):
            for tx in range(self.tilemap.width):
                tile = self.tilemap.get_tile(tx, ty)
                x, y = tx * ts, ty * ts
                if (tx, ty) in anim_sources:
                    self.buffer.fill_rect(x, y, ts, ts, config.COLOR_FLOOR)
                elif tile == Tile.WALL and wall_sprite is not None:
                    self.buffer.fill_rect(x, y, ts, ts, config.COLOR_FLOOR)
                    self.buffer.surface.blit(wall_sprite, (x, y))
                elif tile == Tile.STONE and stone_sprite is not None:
                    self.buffer.fill_rect(x, y, ts, ts, config.COLOR_FLOOR)
                    self.buffer.surface.blit(stone_sprite, (x, y))
                elif tile == Tile.STONE:
                    self.buffer.fill_rect(x, y, ts, ts, config.COLOR_STONE)
                elif tile == Tile.BREAKABLE and breakable_sprite is not None:
                    # Base de chão para que áreas transparentes do sprite não fiquem pretas.
                    self.buffer.fill_rect(x, y, ts, ts, config.COLOR_FLOOR)
                    self.buffer.surface.blit(breakable_sprite, (x, y))
                elif tile == Tile.CHECKPOINT and checkpoint_sprite is not None:
                    self.buffer.fill_rect(x, y, ts, ts, config.COLOR_FLOOR)
                    self.buffer.surface.blit(checkpoint_sprite, (x, y))
                elif tile == Tile.EXIT and exit_stairs_sprite is not None:
                    self.buffer.fill_rect(x, y, ts, ts, config.COLOR_FLOOR)
                    self.buffer.surface.blit(exit_stairs_sprite, (x, y))
                elif tile == Tile.GEM_DOOR and door_sprite is not None:
                    self.buffer.fill_rect(x, y, ts, ts, config.COLOR_FLOOR)
                    self.buffer.surface.blit(door_sprite, (x, y))
                elif tile == Tile.CHEST and chest_sprite is not None:
                    self.buffer.fill_rect(x, y, ts, ts, config.COLOR_FLOOR)
                    self.buffer.surface.blit(chest_sprite, (x, y))
                elif tile == Tile.EMERALD and emerald_sprite is not None:
                    self.buffer.fill_rect(x, y, ts, ts, config.COLOR_FLOOR)
                    self.buffer.surface.blit(emerald_sprite, (x, y))
                else:
                    self.buffer.fill_rect(x, y, ts, ts, self._tile_color(tile))

        if self._boss is not None:
            bx_px = int(round(self._boss.x * ts))
            by_px = self._boss.y * ts
            bw, bh = BOSS_TILE_W * ts, BOSS_TILE_H * ts
            boss_frames = self._get_boss_frames_scaled(ts)
            if boss_frames is not None:
                fi = self._boss.sprite_frame_index()
                surf = boss_frames[fi]
                if self._boss.sprite_face_right():
                    surf = pygame.transform.flip(surf, True, False)
                dw, dh = surf.get_width(), surf.get_height()
                draw_x = bx_px + (bw - dw) // 2
                floor_y = by_px + bh + config.BOSS_VISUAL_OFFSET_Y
                draw_y = floor_y - dh
                ux0 = min(bx_px, draw_x)
                uy0 = min(by_px, draw_y)
                ux1 = max(bx_px + bw, draw_x + dw)
                uy1 = max(by_px + bh, floor_y)
                self.buffer.fill_rect(ux0, uy0, ux1 - ux0, uy1 - uy0, config.COLOR_FLOOR)
                self._blit_boss_sprite_with_flash(
                    self.buffer.surface, surf, (draw_x, draw_y), self._boss.use_white_damage_flash()
                )
            else:
                outer_c, inner_c = self._boss.render_colors()
                dw = int(bw * config.BOSS_VISUAL_SCALE)
                dh = int(bh * config.BOSS_VISUAL_SCALE)
                draw_x = bx_px + (bw - dw) // 2
                floor_y = by_px + bh + config.BOSS_VISUAL_OFFSET_Y
                draw_y = floor_y - dh
                ux0 = min(bx_px, draw_x)
                uy0 = min(by_px, draw_y)
                ux1 = max(bx_px + bw, draw_x + dw)
                uy1 = max(by_px + bh, floor_y)
                self.buffer.fill_rect(ux0, uy0, ux1 - ux0, uy1 - uy0, config.COLOR_FLOOR)
                self.buffer.fill_rect(draw_x, draw_y, dw, dh, outer_c)
                pad = max(2, ts // 8)
                self.buffer.fill_rect(
                    draw_x + pad,
                    draw_y + pad,
                    dw - 2 * pad,
                    dh - 2 * pad,
                    inner_c,
                )

        for anim in self._stone_anims:
            px = anim.x * ts
            py = int(round(anim.y0 * ts + anim.t * (anim.y1 - anim.y0) * ts))
            if stone_sprite is not None:
                self.buffer.fill_rect(px, py, ts, ts, config.COLOR_FLOOR)
                self.buffer.surface.blit(stone_sprite, (px, py))
            else:
                self.buffer.fill_rect(px, py, ts, ts, config.COLOR_STONE)

        pxp = int(round(self.player.draw_x * ts))
        pyp = int(round(self.player.draw_y * ts))
        self._ensure_player_sprites_scaled(ts)
        fdx, fdy = self.player.facing_dx, self.player.facing_dy
        psurf: pygame.Surface | None = None
        if fdy < 0:
            psurf = self._player_up_scaled
        elif fdy > 0:
            psurf = self._player_down_scaled
        elif fdx != 0:
            base = self._player_side_scaled
            if base is not None:
                # Arte base = personagem olhando para a direita; espelha ao ir para a esquerda.
                psurf = pygame.transform.flip(base, True, False) if fdx < 0 else base
        if psurf is None:
            psurf = self._player_down_scaled or self._player_up_scaled or self._player_side_scaled
        if psurf is not None:
            self.buffer.fill_rect(pxp, pyp, ts, ts, config.COLOR_FLOOR)
            self.buffer.surface.blit(psurf, (pxp, pyp))
        else:
            self.buffer.fill_rect(pxp, pyp, ts, ts, config.COLOR_PLAYER)

    def try_click_chest(self, screen_x: int, screen_y: int) -> bool:
        if self._game_over:
            return False
        tile = self._screen_xy_to_tile(screen_x, screen_y)
        if tile is None:
            return False
        tx, ty = tile
        return self.tilemap.get_tile(tx, ty) == Tile.CHEST

    def player_can_finish_game_from_chest(self) -> bool:
        """Em cima do baú ou num tile vizinho (para abrir com Enter)."""
        if self._game_over:
            return False
        px, py = self.player.tile_x, self.player.tile_y
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            tx, ty = px + dx, py + dy
            if self.tilemap.in_bounds(tx, ty) and self.tilemap.get_tile(tx, ty) == Tile.CHEST:
                return True
        return False

    def _screen_xy_to_tile(self, screen_x: int, screen_y: int) -> tuple[int, int] | None:
        ts = config.TILE_SIZE
        scale = max(1, config.WINDOW_SCALE)
        buf_w = self.tilemap.width * ts
        buf_h = self.tilemap.height * ts
        surf_w = buf_w * scale
        surf_h = buf_h * scale
        if surf_w <= 0 or surf_h <= 0:
            return None
        lx = screen_x * buf_w // surf_w
        ly = screen_y * buf_h // surf_h
        lx = min(buf_w - 1, max(0, lx))
        ly = min(buf_h - 1, max(0, ly))
        return lx // ts, ly // ts

    def draw_game_over_layer(self, screen: pygame.Surface) -> None:
        pygame.font.init()
        if self._go_font_title is None:
            self._go_font_title = pygame.font.Font(None, 56)
            self._go_font_ui = pygame.font.Font(None, 26)
        assert self._go_font_title is not None and self._go_font_ui is not None
        if not self._game_over:
            self._game_over_retry_screen_rect = None
            self._game_over_menu_screen_rect = None
            return
        w, h = screen.get_size()
        veil = pygame.Surface((w, h), pygame.SRCALPHA)
        veil.fill((*config.UI_SHADOW, 210))
        screen.blit(veil, (0, 0))
        cx = w // 2
        title = self._go_font_title.render("GAME OVER", True, config.UI_GLOW)
        tr = title.get_rect(center=(cx, int(h * 0.34)))
        screen.blit(title, tr)
        lbl_retry = self._go_font_ui.render("Tentar novamente [Enter / clique]", True, config.UI_GLOW)
        retry_bt = pygame.Rect(0, 0, max(340, lbl_retry.get_width() + 36), 48)
        retry_bt.center = (cx, int(h * 0.55))
        self._game_over_retry_screen_rect = retry_bt.copy()
        pygame.draw.rect(screen, config.UI_MID, retry_bt)
        pygame.draw.rect(screen, config.UI_SHADOW, retry_bt, 3)
        lr = lbl_retry.get_rect(center=retry_bt.center)
        screen.blit(lbl_retry, lr)
        lbl_menu = self._go_font_ui.render("Menu principal [M / clique]", True, config.UI_LIGHT)
        menu_bt = pygame.Rect(0, 0, max(340, lbl_menu.get_width() + 36), 48)
        menu_bt.center = (cx, int(h * 0.66))
        self._game_over_menu_screen_rect = menu_bt.copy()
        pygame.draw.rect(screen, config.UI_DARK, menu_bt)
        pygame.draw.rect(screen, config.UI_SHADOW, menu_bt, 3)
        mr = lbl_menu.get_rect(center=menu_bt.center)
        screen.blit(lbl_menu, mr)

    def game_over_retry_contains(self, screen_x: int, screen_y: int) -> bool:
        r = self._game_over_retry_screen_rect
        return bool(r is not None and r.collidepoint(screen_x, screen_y))

    def game_over_menu_contains(self, screen_x: int, screen_y: int) -> bool:
        r = self._game_over_menu_screen_rect
        return bool(r is not None and r.collidepoint(screen_x, screen_y))
