# Scanline (paridade de interseções). Triângulos: Gouraud e textura por baricêntricas.

from __future__ import annotations

import pygame

from professor.pixel_surface import PixelSurface


def draw_polygon_scanline(ps: PixelSurface, vertices: list[tuple[int, int]], color: tuple[int, int, int]) -> None:
    n = len(vertices)
    if n < 3:
        return
    ys = [v[1] for v in vertices]
    y_min = max(0, min(ys))
    y_max = min(ps.height - 1, max(ys))
    for y in range(y_min, y_max + 1):
        xs: list[float] = []
        for i in range(n):
            x0, y0 = vertices[i]
            x1, y1 = vertices[(i + 1) % n]
            if y0 == y1:
                continue
            if y < min(y0, y1) or y >= max(y0, y1):
                continue
            t = (y - y0) / (y1 - y0)
            xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            x_start = int(max(0, round(xs[k])))
            x_end = int(min(ps.width - 1, round(xs[k + 1])))
            for x in range(x_start, x_end + 1):
                ps.set_pixel(x, y, color)


def _barycentric(
    px: float, py: float, ax: float, ay: float, bx: float, by: float, cx: float, cy: float
) -> tuple[float, float, float] | None:
    den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(den) < 1e-9:
        return None
    w_a = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / den
    w_b = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / den
    w_c = 1.0 - w_a - w_b
    if w_a >= -1e-4 and w_b >= -1e-4 and w_c >= -1e-4:
        return (max(0.0, w_a), max(0.0, w_b), max(0.0, w_c))
    return None


def draw_triangle_gouraud(
    ps: PixelSurface,
    p0: tuple[int, int, tuple[int, int, int]],
    p1: tuple[int, int, tuple[int, int, int]],
    p2: tuple[int, int, tuple[int, int, int]],
) -> None:
    x0, y0, c0 = p0
    x1, y1, c1 = p1
    x2, y2, c2 = p2
    xmin = int(max(0, min(x0, x1, x2)))
    xmax = int(min(ps.width - 1, max(x0, x1, x2)))
    ymin = int(max(0, min(y0, y1, y2)))
    ymax = int(min(ps.height - 1, max(y0, y1, y2)))
    for y in range(ymin, ymax + 1):
        for x in range(xmin, xmax + 1):
            b = _barycentric(
                float(x) + 0.5, float(y) + 0.5, float(x0), float(y0), float(x1), float(y1), float(x2), float(y2)
            )
            if b is None:
                continue
            wa, wb, wc = b
            cr = int(wa * c0[0] + wb * c1[0] + wc * c2[0])
            cg = int(wa * c0[1] + wb * c1[1] + wc * c2[1])
            cb = int(wa * c0[2] + wb * c1[2] + wc * c2[2])
            ps.set_pixel(x, y, (cr, cg, cb))


def draw_triangle_textured(
    ps: PixelSurface,
    p0: tuple[int, int, float, float],
    p1: tuple[int, int, float, float],
    p2: tuple[int, int, float, float],
    tex: pygame.Surface,
) -> None:
    def sample(u: float, v: float) -> tuple[int, int, int]:
        tw, th = tex.get_width(), tex.get_height()
        tx = int(max(0, min(tw - 1, u * (tw - 1))))
        ty = int(max(0, min(th - 1, v * (th - 1))))
        c = tex.get_at((tx, ty))
        return (int(c[0]), int(c[1]), int(c[2]))

    x0, y0, u0, v0 = p0
    x1, y1, u1, v1 = p1
    x2, y2, u2, v2 = p2
    xmin = int(max(0, min(x0, x1, x2)))
    xmax = int(min(ps.width - 1, max(x0, x1, x2)))
    ymin = int(max(0, min(y0, y1, y2)))
    ymax = int(min(ps.height - 1, max(y0, y1, y2)))
    for y in range(ymin, ymax + 1):
        for x in range(xmin, xmax + 1):
            b = _barycentric(
                float(x) + 0.5, float(y) + 0.5, float(x0), float(y0), float(x1), float(y1), float(x2), float(y2)
            )
            if b is None:
                continue
            wa, wb, wc = b
            uu = wa * u0 + wb * u1 + wc * u2
            vv = wa * v0 + wb * v1 + wc * v2
            ps.set_pixel(x, y, sample(uu, vv))
