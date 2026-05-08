"""Menu inicial e tela de créditos."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pygame

import config


@dataclass
class MenuRects:
    play: pygame.Rect
    credits: pygame.Rect
    back: pygame.Rect


_ASSET_DIR = Path(__file__).resolve().parent.parent / "assets"
MENU_BG_FILE = _ASSET_DIR / "menu_bg.png"
VICTORY_BG_FILE = _ASSET_DIR / "victory.png"
# Lado maior da janela do menu (mantém proporção do fundo).
MENU_WINDOW_MAX_SIDE = 820


def load_menu_background() -> pygame.Surface | None:
    if not MENU_BG_FILE.is_file():
        return None
    try:
        img = pygame.image.load(str(MENU_BG_FILE))
        try:
            return img.convert()
        except pygame.error:
            return img
    except pygame.error:
        return None


def load_victory_background() -> pygame.Surface | None:
    if not VICTORY_BG_FILE.is_file():
        return None
    try:
        img = pygame.image.load(str(VICTORY_BG_FILE))
        try:
            return img.convert()
        except pygame.error:
            return img
    except pygame.error:
        return None


def menu_window_size(bg: pygame.Surface) -> tuple[int, int]:
    bw, bh = bg.get_size()
    m = max(bw, bh)
    if m <= 0:
        return 640, 480
    scale = MENU_WINDOW_MAX_SIDE / m
    return max(1, int(bw * scale)), max(1, int(bh * scale))


def scale_menu_background(bg: pygame.Surface, win_w: int, win_h: int) -> pygame.Surface:
    return pygame.transform.scale(bg, (win_w, win_h))


def layout_menu_rects(win_w: int, win_h: int) -> MenuRects:
    bw, bh = 220, 52
    cx = win_w // 2 - bw // 2
    play = pygame.Rect(cx, int(win_h * 0.68), bw, bh)
    credits = pygame.Rect(cx, int(win_h * 0.68) + bh + 14, bw, bh)
    back = pygame.Rect(cx, int(win_h * 0.82), bw, bh)
    return MenuRects(play=play, credits=credits, back=back)


def draw_main_menu(
    screen: pygame.Surface,
    bg_scaled: pygame.Surface,
    rects: MenuRects,
    font_btn: pygame.font.Font,
) -> None:
    screen.blit(bg_scaled, (0, 0))
    for rect, label in (
        (rects.play, "Jogar"),
        (rects.credits, "Créditos"),
    ):
        pygame.draw.rect(screen, config.UI_MID, rect)
        pygame.draw.rect(screen, config.UI_SHADOW, rect, 3)
        txt = font_btn.render(label, True, config.UI_GLOW)
        trect = txt.get_rect(center=rect.center)
        screen.blit(txt, trect)


def draw_credits_screen(
    screen: pygame.Surface,
    bg_scaled: pygame.Surface,
    back_rect: pygame.Rect,
    font_title: pygame.font.Font,
    font_btn: pygame.font.Font,
    font_name: pygame.font.Font,
) -> None:
    screen.blit(bg_scaled, (0, 0))
    veil = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    veil.fill((*config.UI_SHADOW, 210))
    screen.blit(veil, (0, 0))
    title = font_title.render("Créditos", True, config.UI_LIGHT)
    tr = title.get_rect(center=(screen.get_width() // 2, int(screen.get_height() * 0.28)))
    screen.blit(title, tr)
    name = font_name.render("Victor Araújo Silva", True, config.UI_GLOW)
    nr = name.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(name, nr)
    pygame.draw.rect(screen, config.UI_MID, back_rect)
    pygame.draw.rect(screen, config.UI_SHADOW, back_rect, 3)
    bt = font_btn.render("Voltar", True, config.UI_GLOW)
    br = bt.get_rect(center=back_rect.center)
    screen.blit(bt, br)
