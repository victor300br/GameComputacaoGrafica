from __future__ import annotations

import pygame


class PixelSurface:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))

    def clear(self, color: tuple[int, int, int]) -> None:
        self.surface.fill(color)

    def set_pixel(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.surface.set_at((x, y), color)

    def get_pixel(self, x: int, y: int) -> tuple[int, int, int] | None:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
        c = self.surface.get_at((x, y))
        return (int(c[0]), int(c[1]), int(c[2]))
