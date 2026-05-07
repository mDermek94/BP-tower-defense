
from game_logic import *
import os

BASE_PATH = os.path.dirname(__file__)
ASSETS_PATH = os.path.join(BASE_PATH, "assets", "Sprites")
DATA_PATH = os.path.join(BASE_PATH, "data")

CURRENT_BOARD_FILE = os.path.join(DATA_PATH, "board_test_random.txt")
CURRENT_WAVE_FILE = os.path.join(DATA_PATH, "wave_test_random.txt")

# Starting resources
STARTING_MONEY = 10
STARTING_RESOURCE_1 = 0
STARTING_RESOURCE_2 = 0

STARTING_HEALTH = 100

# Tower costs
TOWER0_COST_MONEY = 5

TOWER1_COST_MONEY = 5
TOWER1_COST_RESOURCE_1 = 5

TOWER2_COST_MONEY = 10
TOWER2_COST_RESOURCE_1 = 10
TOWER2_COST_RESOURCE_2 = 10

# Factory costs
FACTORY0_COST_MONEY = 5

FACTORY1_COST_MONEY = 10
FACTORY1_COST_RESOURCE_1 = 10

FACTORY_DEATH_PENALTY = 10

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

max_board_width = SCREEN_WIDTH - 300
max_board_height = SCREEN_HEIGHT - 40
board_size = min(max_board_width, max_board_height)

TILE_COUNT = 10
TILE_SIZE = board_size // TILE_COUNT
BOARD_SIZE = TILE_SIZE * TILE_COUNT

BOARD_X = (SCREEN_WIDTH - board_size) // 2
BOARD_Y = (SCREEN_HEIGHT - board_size) // 2

PLAY_BUTTON_X = BOARD_X - 135

with open(CURRENT_BOARD_FILE, "r") as f:
    BOARD = get_starting_board(f)
    
    HOME_BASE = f.readline().strip().split(",")
    ENEMY_SPAWN = f.readline().strip().split(",")
    
    for i in range(len(HOME_BASE)):
        HOME_BASE[i] = int(HOME_BASE[i])
        ENEMY_SPAWN[i] = int(ENEMY_SPAWN[i])

ENEMY_PATH = build_enemy_path(BOARD, ENEMY_SPAWN, HOME_BASE, BOARD_X, BOARD_Y, TILE_SIZE)
ENEMY_WAVES = build_enemy_waves(CURRENT_WAVE_FILE)

HOME_BASE_COORDS, ENEMY_SPAWN_COORDS = get_base_enemy_coords(HOME_BASE, ENEMY_SPAWN, BOARD_X, BOARD_Y, TILE_SIZE)

TOWER_SPRITES = []
try:
    BASE_PATH = os.path.dirname(__file__)
    ASSETS_PATH = os.path.join(BASE_PATH, "assets", "Sprites")
    
    tower_sprite_1 = pygame.image.load(os.path.join(ASSETS_PATH, "Towers", "Tower-#1.png"))
    # Scale sprite
    tower_sprite_1 = pygame.transform.scale(tower_sprite_1, (60, 60))
    TOWER_SPRITES.append(tower_sprite_1)
    
    tower_sprite_2 = pygame.image.load(os.path.join(ASSETS_PATH, "Towers", "Tower-#2.png"))
    # Scale sprite
    tower_sprite_2 = pygame.transform.scale(tower_sprite_2, (60, 60))
    TOWER_SPRITES.append(tower_sprite_2)
    
    tower_sprite_3 = pygame.image.load(os.path.join(ASSETS_PATH, "Towers", "Tower-#3.png"))
    # Scale sprite
    tower_sprite_3 = pygame.transform.scale(tower_sprite_3, (60, 60))
    TOWER_SPRITES.append(tower_sprite_3)
except pygame.error as e:
    print(f"Could not load tower sprite: {e}")
    TOWER_SPRITES.append(None)

FACTORY_SPRITES = []
try:
    BASE_PATH = os.path.dirname(__file__)
    ASSETS_PATH = os.path.join(BASE_PATH, "assets", "Sprites")
    
    factory_sprite_1 = pygame.image.load(os.path.join(ASSETS_PATH, "Factories", "Factory-#1.png"))
    # Scale sprite
    factory_sprite_1 = pygame.transform.scale(factory_sprite_1, (60, 60))
    FACTORY_SPRITES.append(factory_sprite_1)
    
    factory_sprite_2 = pygame.image.load(os.path.join(ASSETS_PATH, "Factories", "Factory-#2.png"))
    # Scale sprite
    factory_sprite_2 = pygame.transform.scale(factory_sprite_2, (60, 60))
    FACTORY_SPRITES.append(factory_sprite_2)
except pygame.error as e:
    print(f"Could not load factory sprite: {e}")
    FACTORY_SPRITES.append(None)

# Colors - suggested by ChatGPT
BG_COLOR = (40, 40, 40)             # Window background
BOARD_COLOR = (0, 0, 0)             # Board background
UI_PANEL_COLOR = (60, 60, 60)       # UI panel background
UI_BOX_COLOR = (80, 80, 80)         # Tower inventory box
UI_BOX_HOVER = (100, 100, 100)      # Hover color
UI_BOX_BORDER = (200, 200, 200)     # Border color
LINE_COLOR = (0, 0, 0)              # Grid lines
TOWER_TILE_COLOR_A = (72, 209, 56)  # Tower tile 1
TOWER_TILE_COLOR_B = (42, 115, 33)  # Tower tile 2
PATH_TILE_COLOR = (227, 189, 0)     # Path tile
