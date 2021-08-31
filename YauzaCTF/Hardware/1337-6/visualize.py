import pandas as pd
import pygame
from time import sleep
from collections import Counter
from PIL import Image

h, w = 64, 96

table = pd.read_csv("table_v2.csv")
data = list(map(lambda a: int(a, 16), table['mosi'].dropna()[37:]))

pygame.init()
surface = pygame.display.set_mode((w * 10, h * 10))
rects = [[pygame.Rect(x * 10 , y * 10, 10, 10) for x in range(w)] for y in range(h)]
colors = [[(0, 0, 0) for _ in range(w)] for __ in range(h)]

i = 0
sleep(3)

while i < len(data):
    cmd1 = data[i]
    start_x, end_x = data[i + 1], data[i + 2]
    cmd2 = data[i + 3]
    start_y, end_y = data[i + 4], data[i + 5]
    print(i, cmd1, start_x, end_x, cmd2, start_y, end_y)

    width = end_x + 1 - start_x
    height = end_y + 1 - start_y

    i += 6

    for j in range(width * height):
        color_prim = (data[i + j * 2] << 8) | data[i + j * 2 + 1]

        red = (color_prim >> 11) & ((1 << 5) - 1)
        green = (color_prim >> 5) & ((1 << 6) - 1)
        blue = color_prim & ((1 << 5) - 1)

        color = (int(255 / ((1 << 5) - 1) * red), int(255 / ((1 << 6) - 1) * green), int(255 / ((1 << 5) - 1) * blue))
        colors[start_y + (j % height)][start_x + (j // height)] = color

        # print(start_x, start_y, j, start_y, end_y)
        pygame.draw.rect(surface, color, rects[start_y + (j % height)][start_x + (j // height)])
        # pygame.display.flip()
    # sleep(0.01)
    
    
    i += width * height * 2

    if i == len(data):
        break

pygame.display.flip()

colors_flatten = []

for row in colors:
    colors_flatten += row

img = Image.new("RGB", (96, 64))
img.putdata(colors_flatten)
img.save("image.png")

while True:
    pass