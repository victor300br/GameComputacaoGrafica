from __future__ import annotations

import math
from pathlib import Path

import pygame

import config
from professor import clip as clip_mod
from professor import fills
from professor import polygon
from professor import raster
from professor import transforms
from professor.pixel_surface import PixelSurface

LAB_W = 640
LAB_H = 480


def _spider_local_segments() -> list[tuple[float, float, float, float]]:
    segs: list[tuple[float, float, float, float]] = []
    segs.extend(
        [
            (-14.0, -10.0, 14.0, -10.0),
            (14.0, -10.0, 18.0, 6.0),
            (18.0, 6.0, -18.0, 6.0),
            (-18.0, 6.0, -14.0, -10.0),
        ]
    )
    for i in range(4):
        y0 = -6.0 + i * 4.0
        ang = 0.55 + i * 0.12
        L = 38.0
        segs.append(
            (-14.0, y0, -14.0 - L * math.cos(ang), y0 - L * math.sin(ang))
        )
        segs.append((14.0, y0, 14.0 + L * math.cos(ang), y0 - L * math.sin(ang)))
    return segs


_SPIDER_SEGS = _spider_local_segments()


class ProfessorLab:
    def __init__(self) -> None:
        pygame.font.init()
        self.mode = 1
        self.t = 0.0
        self.buffer = PixelSurface(LAB_W, LAB_H)
        self.font = pygame.font.Font(None, 22)
        self.font_title = pygame.font.Font(None, 26)
        self._world_cx = 150.0
        self._world_cy = 100.0
        self._world_half = 120.0
        self._clip_margin = 40.0
        self._tex = self._load_or_make_texture()

    def _load_or_make_texture(self) -> pygame.Surface:
        path = Path(__file__).resolve().parent.parent / "assets" / "grass.png"
        if path.is_file():
            try:
                return pygame.image.load(str(path)).convert()
            except pygame.error:
                pass
        surf = pygame.Surface((64, 64))
        for y in range(64):
            for x in range(64):
                c = (40 + (x ^ y) * 3) % 80 + 40, (60 + x) % 120, (40 + y) % 90
                surf.set_at((x, y), c)
        return surf

    def handle_key(self, key: int) -> None:
        if key == pygame.K_1:
            self.mode = 1
        elif key == pygame.K_2:
            self.mode = 2
        elif key == pygame.K_3:
            self.mode = 3
        elif key == pygame.K_4:
            self.mode = 4
        elif self.mode == 4:
            step = 15.0
            if key == pygame.K_LEFT:
                self._world_cx -= step
            elif key == pygame.K_RIGHT:
                self._world_cx += step
            elif key == pygame.K_UP:
                self._world_cy -= step
            elif key == pygame.K_DOWN:
                self._world_cy += step
            elif key == pygame.K_PLUS or key == pygame.K_EQUALS:
                self._world_half = max(40.0, self._world_half * 0.85)
            elif key == pygame.K_MINUS:
                self._world_half = min(280.0, self._world_half * 1.15)

    def update(self, dt: float) -> None:
        self.t += dt

    def _draw_hud(self, target: pygame.Surface) -> None:
        lines = [
            "Laboratorio CG — Para o professor",
            "[1] Reta / circulo / elipse + Flood + Boundary Fill",
            "[2] Poligono scanline + gradiente (Gouraud) + textura",
            "[3] Aranha: translacao + escala + rotacao (animacao)",
            "[4] Janela/viewport + Cohen-Sutherland (+ setas +/- zoom)",
            "[Esc] Voltar ao menu",
        ]
        y = 6
        for i, line in enumerate(lines):
            col = config.UI_GLOW if i == 0 else config.UI_LIGHT
            surf = self.font_title.render(line, True, col) if i == 0 else self.font.render(line, True, col)
            target.blit(surf, (8, y))
            y += surf.get_height() + (4 if i == 0 else 2)

    def redraw(self) -> pygame.Surface:
        ps = self.buffer
        if self.mode == 1:
            self._draw_mode1(ps)
        elif self.mode == 2:
            self._draw_mode2(ps)
        elif self.mode == 3:
            self._draw_mode3(ps)
        else:
            self._draw_mode4(ps)
        out = ps.surface.copy()
        self._draw_hud(out)
        return out

    def _draw_mode1(self, ps: PixelSurface) -> None:
        ps.clear((10, 22, 12))
        raster.draw_line_bresenham(ps, 40, 400, 200, 280, config.UI_LIGHT)
        raster.draw_line_bresenham(ps, 200, 280, 40, 200, config.UI_MID)
        raster.draw_line_bresenham(ps, 40, 200, 40, 400, config.UI_GLOW)
        raster.draw_circle_midpoint(ps, 420, 160, 85, config.UI_LIGHT)
        raster.draw_ellipse_midpoint(ps, 420, 360, 110, 55, config.UI_GLOW)
        x0, y0, x1, y1 = 520, 80, 610, 200
        raster.draw_line_bresenham(ps, x0, y0, x1, y0, config.UI_SHADOW)
        raster.draw_line_bresenham(ps, x1, y0, x1, y1, config.UI_SHADOW)
        raster.draw_line_bresenham(ps, x1, y1, x0, y1, config.UI_SHADOW)
        raster.draw_line_bresenham(ps, x0, y1, x0, y0, config.UI_SHADOW)
        fx0, fy0, fx1, fy1 = 260, 370, 360, 450
        polygon.draw_polygon_scanline(
            ps, [(fx0, fy0), (fx1, fy0), (fx1, fy1), (fx0, fy1)], (32, 44, 36)
        )
        bcol = (6, 8, 6)
        raster.draw_line_bresenham(ps, fx0, fy0, fx1, fy0, bcol)
        raster.draw_line_bresenham(ps, fx1, fy0, fx1, fy1, bcol)
        raster.draw_line_bresenham(ps, fx1, fy1, fx0, fy1, bcol)
        raster.draw_line_bresenham(ps, fx0, fy1, fx0, fy0, bcol)
        fills.flood_fill(ps, (fx0 + fx1) // 2, (fy0 + fy1) // 2, (72, 125, 88))
        fills.boundary_fill(ps, 420, 160, config.UI_LIGHT, (60, 95, 65))

    def _draw_mode2(self, ps: PixelSurface) -> None:
        ps.clear((12, 18, 14))
        verts = [(80, 240), (200, 120), (300, 260), (240, 360), (100, 340)]
        polygon.draw_polygon_scanline(ps, verts, (50, 110, 70))
        polygon.draw_triangle_gouraud(
            ps,
            (380, 60, (200, 230, 120)),
            (560, 80, (40, 60, 100)),
            (480, 220, (180, 200, 90)),
        )
        polygon.draw_triangle_textured(
            ps,
            (360, 280, 0.0, 0.0),
            (520, 270, 1.0, 0.0),
            (440, 420, 0.5, 1.0),
            self._tex,
        )

    def _draw_mode3(self, ps: PixelSurface) -> None:
        ps.clear((14, 16, 12))
        cx = LAB_W // 2 + 110 * math.sin(self.t * 0.9)
        cy = LAB_H // 2 + 70 * math.cos(self.t * 0.7)
        theta = self.t * 1.1
        sc = 1.0 + 0.35 * math.sin(self.t * 2.4)
        M = transforms.compose_TRS(cx, cy, theta, sc, sc)
        leg_c = (40, 75, 45)
        body_c = (90, 140, 95)
        for x0, y0, x1, y1 in _SPIDER_SEGS:
            ax, ay = transforms.transform_point(M, x0, y0)
            bx, by = transforms.transform_point(M, x1, y1)
            raster.draw_line_bresenham(ps, int(round(ax)), int(round(ay)), int(round(bx)), int(round(by)), leg_c)
        for x0, y0, x1, y1 in _SPIDER_SEGS[:4]:
            ax, ay = transforms.transform_point(M, x0, y0)
            bx, by = transforms.transform_point(M, x1, y1)
            raster.draw_line_bresenham(ps, int(round(ax)), int(round(ay)), int(round(bx)), int(round(by)), body_c)

    def _draw_mode4(self, ps: PixelSurface) -> None:
        ps.clear((8, 14, 10))
        wx0 = self._world_cx - self._world_half
        wx1 = self._world_cx + self._world_half
        wy0 = self._world_cy - self._world_half * 0.72
        wy1 = self._world_cy + self._world_half * 0.72
        clip_x0 = wx0 + self._clip_margin
        clip_y0 = wy0 + self._clip_margin
        clip_x1 = wx1 - self._clip_margin
        clip_y1 = wy1 - self._clip_margin

        vx0, vy0 = 120, 100
        vx1, vy1 = LAB_W - 40, LAB_H - 40

        grid_lines = []
        for g in range(-200, 400, 40):
            grid_lines.append((float(g), -300.0, float(g), 300.0))
            grid_lines.append((-300.0, float(g), 400.0, float(g)))
        grid_lines.append((wx0 - 80, wy0 - 50, wx1 + 120, wy1 + 70))
        grid_lines.append((wx0 + 30, wy1 + 100, wx1 - 20, wy0 - 120))

        for x0, y0, x1, y1 in grid_lines:
            clipped = clip_mod.cohen_sutherland_clip(x0, y0, x1, y1, clip_x0, clip_y0, clip_x1, clip_y1)
            if clipped is None:
                continue
            xa, ya, xb, yb = clipped
            sa = clip_mod.world_to_viewport(xa, ya, wx0, wy0, wx1, wy1, vx0, vy0, vx1, vy1)
            sb = clip_mod.world_to_viewport(xb, yb, wx0, wy0, wx1, wy1, vx0, vy0, vx1, vy1)
            raster.draw_line_bresenham(ps, sa[0], sa[1], sb[0], sb[1], (100, 150, 110))

        raster.draw_line_bresenham(ps, vx0, vy0, vx1, vy0, config.UI_GLOW)
        raster.draw_line_bresenham(ps, vx1, vy0, vx1, vy1, config.UI_GLOW)
        raster.draw_line_bresenham(ps, vx1, vy1, vx0, vy1, config.UI_GLOW)
        raster.draw_line_bresenham(ps, vx0, vy1, vx0, vy0, config.UI_GLOW)

        corners = [
            (clip_x0, clip_y0),
            (clip_x1, clip_y0),
            (clip_x1, clip_y1),
            (clip_x0, clip_y1),
        ]
        scr_pts = [
            clip_mod.world_to_viewport(wx, wy, wx0, wy0, wx1, wy1, vx0, vy0, vx1, vy1) for wx, wy in corners
        ]
        c_col = config.UI_LIGHT
        for i in range(4):
            a, b = scr_pts[i], scr_pts[(i + 1) % 4]
            raster.draw_line_bresenham(ps, a[0], a[1], b[0], b[1], c_col)
