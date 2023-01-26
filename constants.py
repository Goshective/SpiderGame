import os


FPS = 60

QUALITIES = {"High": (1920, 1080), "HD": (1280, 720), "960H": (960, 576), "D1": (720, 576), "Low": (360, 240)}
LEVEL_SIZES = 25, 64
size = WIDTH, HEIGHT = QUALITIES["HD"]
tile_width = tile_height = 50

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_BASE_PATH = ROOT_PATH + "\\players_database.db"

GRAVITY = 0.35
JMP_POWER = 10
MOVE_SPEED = 7
DIST_COEFF = 0.06
TIME_COEFF = 10000
SPAWN_COEFF = 150
ENEMY_RADIUS = 15

ANIMATION_LEFT= ["pauk1.png", "pauk2.png", "pauk3.png"]
ANIMATION_RIGHT = ["pauk3.png", "pauk2.png", "pauk1.png"]
ANIMATION_JUMP = ["pauk1.png"]
ANIMATION_JUMP_LEFT = ["pauk1.png"]
ANIMATION_JUMP_RIGHT = ["pauk1.png"]
ANIMATION_STAY = ["pauk1.png"]