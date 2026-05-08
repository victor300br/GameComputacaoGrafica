# Flood fill (região de mesma cor) e boundary fill (para na cor do contorno).

from __future__ import annotations

from collections import deque

from professor.pixel_surface import PixelSurface


def flood_fill(ps: PixelSurface, sx: int, sy: int, fill: tuple[int, int, int]) -> None:
    start = ps.get_pixel(sx, sy)
    if start is None or start == fill:
        return
    q: deque[tuple[int, int]] = deque()
    q.append((sx, sy))
    visited = set()
    while q:
        x, y = q.popleft()
        if (x, y) in visited:
            continue
        if not (0 <= x < ps.width and 0 <= y < ps.height):
            continue
        c = ps.get_pixel(x, y)
        if c is None or c != start:
            continue
        visited.add((x, y))
        ps.set_pixel(x, y, fill)
        q.append((x + 1, y))
        q.append((x - 1, y))
        q.append((x, y + 1))
        q.append((x, y - 1))


def boundary_fill(
    ps: PixelSurface, sx: int, sy: int, boundary: tuple[int, int, int], fill: tuple[int, int, int]
) -> None:
    start = ps.get_pixel(sx, sy)
    if start is None or start == boundary or start == fill:
        return
    q: deque[tuple[int, int]] = deque()
    q.append((sx, sy))
    seen: set[tuple[int, int]] = set()
    while q:
        x, y = q.popleft()
        if (x, y) in seen:
            continue
        if not (0 <= x < ps.width and 0 <= y < ps.height):
            continue
        c = ps.get_pixel(x, y)
        if c is None or c == boundary:
            continue
        if c == fill:
            seen.add((x, y))
            continue
        seen.add((x, y))
        ps.set_pixel(x, y, fill)
        q.append((x + 1, y))
        q.append((x - 1, y))
        q.append((x, y + 1))
        q.append((x, y - 1))
