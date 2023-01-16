import os


FPS = 60

QUALITIES = {"High": (1920, 1080), "HD": (1280, 720), "960H": (960, 576), "D1": (720, 576), "Low": (360, 240)}
size = WIDTH, HEIGHT = QUALITIES["HD"]
tile_width = tile_height = 50

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

GRAVITY = 0.35
JMP_POWER = 10
MOVE_SPEED = 7

ANIMATION_LEFT= ["pauk1.png", "pauk2.png", "pauk3.png"]
ANIMATION_RIGHT = ["pauk3.png", "pauk2.png", "pauk1.png"]
ANIMATION_JUMP = ["pauk1.png"]
ANIMATION_JUMP_LEFT = ["pauk1.png"]
ANIMATION_JUMP_RIGHT = ["pauk1.png"]
ANIMATION_STAY = ["pauk1.png"]