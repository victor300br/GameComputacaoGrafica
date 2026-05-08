# Cohen–Sutherland em [x_min,x_max]×[y_min,y_max]; world_to_viewport = afim 2D para retângulo de tela.

from __future__ import annotations

INSIDE = 0
LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8


def _region_code(x: float, y: float, x_min: float, y_min: float, x_max: float, y_max: float) -> int:
    code = INSIDE
    if x < x_min:
        code |= LEFT
    elif x > x_max:
        code |= RIGHT
    if y < y_min:
        code |= TOP
    elif y > y_max:
        code |= BOTTOM
    return code


def cohen_sutherland_clip(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    x_min: float,
    y_min: float,
    x_max: float,
    y_max: float,
) -> tuple[float, float, float, float] | None:
    code0 = _region_code(x0, y0, x_min, y_min, x_max, y_max)
    code1 = _region_code(x1, y1, x_min, y_min, x_max, y_max)
    while True:
        if code0 == 0 and code1 == 0:
            return (x0, y0, x1, y1)
        if code0 & code1 != 0:
            return None
        code_out = code0 if code0 != 0 else code1
        if code_out & TOP:
            x = x0 + (x1 - x0) * (y_min - y0) / (y1 - y0)
            y = y_min
        elif code_out & BOTTOM:
            x = x0 + (x1 - x0) * (y_max - y0) / (y1 - y0)
            y = y_max
        elif code_out & RIGHT:
            y = y0 + (y1 - y0) * (x_max - x0) / (x1 - x0)
            x = x_max
        elif code_out & LEFT:
            y = y0 + (y1 - y0) * (x_min - x0) / (x1 - x0)
            x = x_min
        else:
            return None
        if code_out == code0:
            x0, y0 = x, y
            code0 = _region_code(x0, y0, x_min, y_min, x_max, y_max)
        else:
            x1, y1 = x, y
            code1 = _region_code(x1, y1, x_min, y_min, x_max, y_max)


def world_to_viewport(
    wx: float,
    wy: float,
    wx0: float,
    wy0: float,
    wx1: float,
    wy1: float,
    vx0: int,
    vy0: int,
    vx1: int,
    vy1: int,
) -> tuple[int, int]:
    if wx1 == wx0 or wy1 == wy0:
        return (vx0, vy0)
    sx = (wx - wx0) / (wx1 - wx0)
    sy = (wy - wy0) / (wy1 - wy0)
    dsx = vx1 - vx0
    dsy = vy1 - vy0
    sx_px = int(round(vx0 + sx * dsx))
    sy_px = int(round(vy0 + sy * dsy))
    return (sx_px, sy_px)
