from __future__ import annotations

from enum import Enum, auto

import pygame

import config
from game.boss_music_event import BOSS_MUSIC_TRACK_ENDED
from game.game import Game
from game.main_menu import (
    draw_credits_screen,
    draw_main_menu,
    layout_menu_rects,
    load_menu_background,
    load_victory_background,
    menu_window_size,
    scale_menu_background,
)
from professor.runner import LAB_H, LAB_W, ProfessorLab


class _AppPhase(Enum):
    MENU = auto()
    CREDITS = auto()
    PROFESSOR = auto()
    PLAYING = auto()
    VICTORY = auto()


def run() -> None:
    pygame.init()
    pygame.display.set_caption("Lost Cave")
    pygame.font.init()

    menu_bg_raw = load_menu_background()
    if menu_bg_raw is None:
        menu_w, menu_h = 720, 720
        menu_bg_scaled = pygame.Surface((menu_w, menu_h))
        menu_bg_scaled.fill(config.UI_SHADOW)
    else:
        menu_w, menu_h = menu_window_size(menu_bg_raw)
        menu_bg_scaled = scale_menu_background(menu_bg_raw, menu_w, menu_h)

    screen = pygame.display.set_mode((menu_w, menu_h))
    clock = pygame.time.Clock()

    font_btn = pygame.font.Font(None, 36)
    font_cred_title = pygame.font.Font(None, 52)
    font_name = pygame.font.Font(None, 40)

    phase = _AppPhase.MENU
    menu_rects = layout_menu_rects(menu_w, menu_h)
    game: Game | None = None
    prof_lab: ProfessorLab | None = None
    running = True

    def return_to_main_menu() -> None:
        nonlocal game, phase, screen, menu_bg_scaled, prof_lab
        pygame.mixer.music.stop()
        pygame.mixer.music.set_endevent()
        game = None
        prof_lab = None
        phase = _AppPhase.MENU
        screen = pygame.display.set_mode((menu_w, menu_h))
        pygame.display.set_caption("Lost Cave")
        if menu_bg_raw is not None:
            menu_bg_scaled = scale_menu_background(menu_bg_raw, menu_w, menu_h)

    victory_raw = load_victory_background()

    while running:
        dt = clock.tick(60) / 1000.0

        if phase in (_AppPhase.MENU, _AppPhase.CREDITS):
            menu_rects = layout_menu_rects(*screen.get_size())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif phase == _AppPhase.VICTORY:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    return_to_main_menu()
                elif event.type == pygame.KEYDOWN:
                    return_to_main_menu()

            elif phase == _AppPhase.PLAYING and game is not None:
                if event.type == BOSS_MUSIC_TRACK_ENDED:
                    game.on_boss_music_track_ended()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if game.is_game_over:
                        if game.game_over_retry_contains(mx, my):
                            game.try_again_from_game_over()
                        elif game.game_over_menu_contains(mx, my):
                            return_to_main_menu()
                    elif game.try_click_chest(mx, my):
                        pygame.mixer.music.stop()
                        pygame.mixer.music.set_endevent()
                        phase = _AppPhase.VICTORY
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return_to_main_menu()
                    elif event.key in (pygame.K_q,):
                        running = False
                    elif game.is_game_over:
                        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            game.try_again_from_game_over()
                        elif event.key == pygame.K_m:
                            return_to_main_menu()
                    elif game.player_can_finish_game_from_chest() and event.key in (
                        pygame.K_RETURN,
                        pygame.K_KP_ENTER,
                        pygame.K_e,
                    ):
                        pygame.mixer.music.stop()
                        pygame.mixer.music.set_endevent()
                        phase = _AppPhase.VICTORY
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        game.handle_input(-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        game.handle_input(1, 0)
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        game.handle_input(0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        game.handle_input(0, 1)
                    elif event.key == pygame.K_r:
                        game.restore_checkpoint()

            elif phase == _AppPhase.MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if menu_rects.play.collidepoint(mx, my):
                        game = Game()
                        gw = game.tilemap.width * config.TILE_SIZE * config.WINDOW_SCALE
                        gh = game.tilemap.height * config.TILE_SIZE * config.WINDOW_SCALE
                        screen = pygame.display.set_mode((gw, gh))
                        pygame.display.set_caption("Lost Cave — WASD | R checkpoint | Esc menu")
                        phase = _AppPhase.PLAYING
                    elif menu_rects.credits.collidepoint(mx, my):
                        phase = _AppPhase.CREDITS
                    elif menu_rects.professor.collidepoint(mx, my):
                        prof_lab = ProfessorLab()
                        screen = pygame.display.set_mode((LAB_W, LAB_H))
                        pygame.display.set_caption("Lost Cave — Laboratorio CG | Esc = menu")
                        phase = _AppPhase.PROFESSOR
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False
                    elif event.key == pygame.K_p:
                        prof_lab = ProfessorLab()
                        screen = pygame.display.set_mode((LAB_W, LAB_H))
                        pygame.display.set_caption("Lost Cave — Laboratorio CG | Esc = menu")
                        phase = _AppPhase.PROFESSOR
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        game = Game()
                        gw = game.tilemap.width * config.TILE_SIZE * config.WINDOW_SCALE
                        gh = game.tilemap.height * config.TILE_SIZE * config.WINDOW_SCALE
                        screen = pygame.display.set_mode((gw, gh))
                        pygame.display.set_caption("Lost Cave — WASD | R checkpoint | Esc menu")
                        phase = _AppPhase.PLAYING

            elif phase == _AppPhase.PROFESSOR and prof_lab is not None:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return_to_main_menu()
                    else:
                        prof_lab.handle_key(event.key)

            elif phase == _AppPhase.CREDITS:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if menu_rects.back.collidepoint(mx, my):
                        phase = _AppPhase.MENU
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        phase = _AppPhase.MENU
                    elif event.key in (pygame.K_q,):
                        running = False

        if phase == _AppPhase.MENU:
            draw_main_menu(screen, menu_bg_scaled, menu_rects, font_btn)
        elif phase == _AppPhase.CREDITS:
            draw_credits_screen(
                screen,
                menu_bg_scaled,
                menu_rects.back,
                font_cred_title,
                font_btn,
                font_name,
            )
        elif phase == _AppPhase.PROFESSOR and prof_lab is not None:
            prof_lab.update(dt)
            screen.blit(prof_lab.redraw(), (0, 0))
        elif phase == _AppPhase.VICTORY:
            sw, sh = screen.get_size()
            if victory_raw is not None:
                pic = pygame.transform.scale(victory_raw, (sw, sh))
                screen.blit(pic, (0, 0))
            else:
                screen.fill(config.UI_SHADOW)
        elif phase == _AppPhase.PLAYING and game is not None:
            game.update(dt)
            game.render()
            gw = game.tilemap.width * config.TILE_SIZE * config.WINDOW_SCALE
            gh = game.tilemap.height * config.TILE_SIZE * config.WINDOW_SCALE
            scaled = pygame.transform.scale(game.buffer.surface, (gw, gh))
            screen.blit(scaled, (0, 0))
            if game.is_game_over:
                game.draw_game_over_layer(screen)

        pygame.display.flip()

    pygame.quit()
