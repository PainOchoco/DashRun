import pygame
import math
import os
import random
import csv
from components.settings import *

class Particle():
    def __init__(self, startx, starty, col, pause):
        self.x = startx
        self.y = starty + random.randint(-7, 7)
        self.col = col
        self.sx = startx
        self.sy = starty + random.randint(-7, 7)
        self.pause = pause

    def move(self):
        if self.pause==0:
            if self.x < self.sx - 50:
                self.x = self.sx
                self.y = self.sy + random.randint(-7, 7)

            else:
                self.x-=1
        else:
            self.pause-=1

# other useful functions

def swap_color(img, old_c, new_c):
    img.set_colorkey(old_c)
    surf = img.copy()
    surf.fill(new_c)
    surf.blit(img, (0, 0))
    return surf

def get_scroll(true_scroll, player):
        true_scroll[0] += (player.entity.x + player.entity.width / 2 - true_scroll[0] - WIDTH / 4) / 20
        true_scroll[1] += (player.entity.y + player.entity.height / 2- true_scroll[1] - HEIGHT / 4) / 20

        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])  # ? Arrondie le scroll à l'entier pour que
        scroll[1] = int(scroll[1])  # ? les tiles soient placées au pixel près

        return true_scroll, scroll


def load_sounds(path):
    sounds = {}
    files = os.listdir(path)
    for file in files:
        sounds[file.replace(".wav", "")] = pygame.mixer.Sound(path + file)

    return sounds