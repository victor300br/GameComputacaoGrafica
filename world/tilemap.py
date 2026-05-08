# Grade de tiles; desenho em config.TILE_SIZE px.

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path


class Tile(IntEnum):
    FLOOR = 0
    WALL = 1
    INVIS_WALL = 2
    CHECKPOINT = 3
    BREAKABLE = 4
    STONE = 5
    EXIT = 6
    EMERALD = 7
    GEM_DOOR = 8
    CHEST = 9


@dataclass(frozen=True)
class ParsedLevel:
    tilemap: "TileMap"
    spawn: tuple[int, int]
    boss_origin: tuple[float, int] | None = None
    rock_drop_columns: tuple[int, int, int] | None = None


class TileMap:
    def __init__(self, width: int, height: int, tiles: list[list[Tile]]) -> None:
        self.width = width
        self.height = height
        self._tiles = tiles

    def clone(self) -> TileMap:
        return TileMap(self.width, self.height, [row[:] for row in self._tiles])

    @staticmethod
    def _char_to_tile(ch: str) -> Tile | None:
        if ch == "#":
            return Tile.WALL
        if ch in ". ":
            return Tile.FLOOR
        if ch == "I":
            return Tile.INVIS_WALL
        if ch == "@":
            return None  # spawn, vira chão
        if ch in ("F", "P"):
            return Tile.GEM_DOOR
        if ch == "C":
            return Tile.CHECKPOINT
        if ch == "g":
            return Tile.BREAKABLE
        if ch == "o":
            return Tile.STONE
        if ch == ",":
            return Tile.EXIT
        if ch == "e":
            return Tile.EMERALD
        return Tile.WALL

    @classmethod
    def from_strings(cls, lines: list[str]) -> ParsedLevel:
        # @/p spawn; b/B boss; 1/2/3 marcam colunas de queda de pedra.
        boss_cells: list[tuple[int, int]] = []
        rock_marker_x: dict[str, int] = {}
        h = len(lines)
        w = max(len(row) for row in lines) if lines else 0
        grid: list[list[Tile]] = []
        spawn: tuple[int, int] = (1, 1)

        for y, row in enumerate(lines):
            row_tiles: list[Tile] = []
            for x in range(w):
                ch = row[x] if x < len(row) else "#"
                if ch in ("@", "p"):
                    spawn = (x, y)
                    row_tiles.append(Tile.FLOOR)
                    continue
                if ch in ("K", "k"):
                    row_tiles.append(Tile.CHEST)
                    continue
                if ch in ("b", "B"):
                    boss_cells.append((x, y))
                    row_tiles.append(Tile.FLOOR)
                    continue
                if ch in "123":
                    rock_marker_x[ch] = x
                    row_tiles.append(Tile.FLOOR)
                    continue
                t = cls._char_to_tile(ch)
                if t is None:
                    row_tiles.append(Tile.FLOOR)
                else:
                    row_tiles.append(t)
            grid.append(row_tiles)

        tilemap = cls(w, h, grid)
        boss_origin: tuple[float, int] | None = None
        if boss_cells:
            min_x = min(c[0] for c in boss_cells)
            min_y = min(c[1] for c in boss_cells)
            boss_origin = (float(min_x), min_y)

        rock_drop_columns: tuple[int, int, int] | None = None
        if rock_marker_x:
            mid = w // 2
            rock_drop_columns = (
                rock_marker_x.get("1", mid),
                rock_marker_x.get("2", mid),
                rock_marker_x.get("3", mid),
            )

        return ParsedLevel(
            tilemap=tilemap,
            spawn=spawn,
            boss_origin=boss_origin,
            rock_drop_columns=rock_drop_columns,
        )

    @classmethod
    def from_file(cls, path: str | Path) -> ParsedLevel:
        text = Path(path).read_text(encoding="utf-8")
        lines = [ln.rstrip("\n\r") for ln in text.splitlines() if ln.strip()]
        return cls.from_strings(lines)

    def in_bounds(self, tx: int, ty: int) -> bool:
        return 0 <= tx < self.width and 0 <= ty < self.height

    def get_tile(self, tx: int, ty: int) -> Tile:
        return self._tiles[ty][tx]

    def set_tile(self, tx: int, ty: int, tile: Tile) -> None:
        self._tiles[ty][tx] = tile


def default_level() -> tuple[TileMap, tuple[int, int]]:
    root = Path(__file__).resolve().parent.parent
    tutorial = root / "levels" / "tutorial.txt"
    pl = TileMap.from_file(tutorial)
    return pl.tilemap, pl.spawn
