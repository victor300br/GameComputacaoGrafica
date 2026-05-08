"""Constantes globais do jogo (resolução lógica, escala de janela)."""

# Cada célula do mapa é desenhada como um quadrado de TILE_SIZE x TILE_SIZE pixels.
TILE_SIZE = 16

# Escala para exibir na janela (1 = 1 pixel lógico = 1 pixel na tela).
WINDOW_SCALE = 3

# Duração (segundos) da transição entre dois tiles.
MOVE_DURATION = 0.10

# Queda da pedra (um tile); menor = mais rápido que o jogador, ainda fluido.
STONE_FALL_DURATION = 0.055
# Intervalo (segundos) para piscar a gema (ligada/desligada).
EMERALD_BLINK_INTERVAL = 0.45

# Paleta UI (título Lost Cave — tons verdes estilo handheld).
UI_SHADOW = (8, 26, 8)  # #081a08
UI_DARK = (27, 51, 27)  # #1b331b
UI_MID = (74, 112, 74)  # #4a704a
UI_LIGHT = (147, 180, 132)  # #93b484
UI_GLOW = (203, 217, 168)  # #cbd9a8

# Cores provisórias (depois vira paleta 4 cores).
COLOR_BACKGROUND = (157, 189, 147)  # #E8F5E0
COLOR_FLOOR = (157, 189, 147) # #E8F5E0
COLOR_WALL = (20, 20, 24)
COLOR_PLAYER = (235, 203, 139)
COLOR_CHECKPOINT = (46, 52, 102)
COLOR_BREAKABLE = (80, 160, 90)
COLOR_STONE = (120, 80, 55)
COLOR_EXIT = (60, 100, 110)
COLOR_EMERALD = (160, 70, 220)
COLOR_GEM_DOOR = (255, 120, 170)
COLOR_CHEST = (74, 112, 74)  # UI_MID — fallback se não houver sprite do baú

# Boss (level 3)
BOSS_PATROL_TILES_PER_SEC = 2.6
BOSS_CHARGE_TILES_PER_SEC = 16.0
BOSS_CHARGE_COOLDOWN_SEC = 2.0
BOSS_RECOVER_SEC = 0.55
COLOR_BOSS = (160, 40, 80)
COLOR_BOSS_DARK = (110, 25, 55)
COLOR_BOSS_FLASH = (255, 255, 255)

# Boss: vida / piscadas
BOSS_MAX_HP = 3
BOSS_HIT_FLASH_SEC = 0.42
BOSS_HIT_FLASH_INTERVAL_SEC = 0.07
BOSS_DEATH_DURATION_SEC = 1.15
BOSS_DEATH_FLASH_INTERVAL_SEC = 0.04
# Duração de cada frame da animação walk (1–5) em loop.
BOSS_ANIM_FRAME_SEC = 0.11
# Escala visual do sprite (hitbox de jogo continua 3×2 tiles). >1 = aranha maior na tela.
# A base do desenho fica fixa no chão (by + altura hitbox + BOSS_VISUAL_OFFSET_Y).
BOSS_VISUAL_SCALE = 1.38
# Ajuste fino do “chão” dos pés (pixels lógicos); a base do sprite encosta nesta linha.
BOSS_VISUAL_OFFSET_Y = 14

# Música na arena do boss (level3): início em 1:45 e loop retoma desse ponto.
BOSS_MUSIC_PATH = r"c:\Users\Victor\Downloads\Vordt of the Boreal Valley.mp3"
BOSS_MUSIC_START_SEC = 105.0
