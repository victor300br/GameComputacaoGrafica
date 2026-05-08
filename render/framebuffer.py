"""Superfície lógica do jogo: desenho pixel a pixel ou por retângulos sobre buffer interno."""

from __future__ import annotations

import pygame


class Framebuffer:
    """Buffer com dimensões em pixels (largura x altura do mundo em resolução lógica)."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))

    def clear(self, color: tuple[int, int, int]) -> None:
        self.surface.fill(color)

    def set_pixel(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.surface.set_at((x, y), color)

    def fill_rect(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        color: tuple[int, int, int],
    ) -> None:
        """Retângulo alinhado aos eixos (útil até trocar por polígonos/scanline)."""
        pygame.draw.rect(self.surface, color, (x, y, w, h))
