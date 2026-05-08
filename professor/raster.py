# Bresenham (segmento), circunferência e elipse eixo-alinhada (ponto médio).

from __future__ import annotations

from professor.pixel_surface import PixelSurface


def draw_line_bresenham(ps: PixelSurface, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        ps.set_pixel(x, y, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def draw_circle_midpoint(ps: PixelSurface, xc: int, yc: int, r: int, color: tuple[int, int, int]) -> None:
    if r <= 0:
        ps.set_pixel(xc, yc, color)
        return
    x = 0
    y = r
    d = 1 - r

    def plot8(cx: int, cy: int, xp: int, yp: int) -> None:
        for px, py in (
            (cx + xp, cy + yp),
            (cx - xp, cy + yp),
            (cx + xp, cy - yp),
            (cx - xp, cy - yp),
            (cx + yp, cy + xp),
            (cx - yp, cy + xp),
            (cx + yp, cy - xp),
            (cx - yp, cy - xp),
        ):
            ps.set_pixel(px, py, color)

    plot8(xc, yc, x, y)
    while x < y:
        x += 1
        if d < 0:
            d += 2 * x + 1
        else:
            y -= 1
            d += 2 * (x - y) + 1
        plot8(xc, yc, x, y)


def draw_ellipse_midpoint(
    ps: PixelSurface, xc: int, yc: int, rx: int, ry: int, color: tuple[int, int, int]
) -> None:
    if rx <= 0 or ry <= 0:
        return

    def plot4(xp: int, yp: int) -> None:
        for px, py in (
            (xc + xp, yc + yp),
            (xc - xp, yc + yp),
            (xc + xp, yc - yp),
            (xc - xp, yc - yp),
        ):
            ps.set_pixel(px, py, color)

    rx2 = rx * rx
    ry2 = ry * ry
    x = 0
    y = ry
    d = ry2 - rx2 * ry + rx2 // 4
    while 2 * ry2 * x < 2 * rx2 * y:
        plot4(x, y)
        x += 1
        if d < 0:
            d += 2 * ry2 * x + ry2
        else:
            y -= 1
            d += 2 * ry2 * x - 2 * rx2 * y + ry2

    d = ry2 * (x + 1) * (x + 1) + rx2 * (y - 1) * (y - 1) - rx2 * ry2
    while y >= 0:
        plot4(x, y)
        y -= 1
        if d > 0:
            d -= 2 * rx2 * y + rx2
        else:
            x += 1
            d += 2 * ry2 * x - 2 * rx2 * y + rx2
