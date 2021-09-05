import pandas as pd
import pygame
from time import sleep

h, w = 64, 96

table = pd.read_csv("table.csv")
data = list(map(lambda a: int(a, 16), table['mosi'].dropna()[37:]))

pygame.init()
surface = pygame.display.set_mode((w * 10, h * 10))
rects = [[pygame.Rect(x * 10 , y * 10, 10, 10) for x in range(w)] for y in range(h)]

i = 0

while i < len(data):
    cmd1 = data[i]
    start_x, end_x = data[i + 1], data[i + 2]
    cmd2 = data[i + 3]
    start_y, end_y = data[i + 4], data[i + 5]

    width = end_x + 1 - start_x
    height = end_y + 1 - start_y

    i += 6

    for j in range(width * height):
        color_prim = (data[i + j * 2] << 8) | data[i + j * 2 + 1]

        red = (color_prim >> 11) & ((1 << 5) - 1)
        green = (color_prim >> 5) & ((1 << 6) - 1)
        blue = color_prim & ((1 << 5) - 1)

        color = (int(255 / ((1 << 5) - 1) * red),
                 int(255 / ((1 << 6) - 1) * green),
                 int(255 / ((1 << 5) - 1) * blue))

        pygame.draw.rect(surface, color, rects[start_y + (j % height)][start_x + (j // height)])
    
    
    i += width * height * 2

    if i == len(data):
        break

while True:
    pygame.display.flip()
    sleep(0.05)