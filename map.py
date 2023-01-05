import random as rnd
from PIL import Image, ImageDraw, ImageFilter


def generate_map(width=64, height=128):
    map = ''
    img = Image.new("L", (width, height))
    draw = ImageDraw.Draw(img)

    for x in range(width):
        for y in range(height):
            draw.point((x, y), rnd.randint(0, 255))

    pix = img.filter(ImageFilter.GaussianBlur(radius=3)).load()

    while True:
        player_pos = [rnd.randint(1, width), rnd.randint(1, height)]
        if pix[player_pos[0], player_pos[1]] < 127:
            break

    for x in range(width):
        for y in range(height):
            if player_pos == [x, y]:
                map += '@'
            elif 0 < x < width - 1 and 0 < y < height - 1:
                map += '#' if pix[x, y] > 127 else '.'
            else:
                map += '#'
        map += '\n'

    return [s for s in map.split('\n')]
