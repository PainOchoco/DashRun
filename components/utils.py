import math
import os
import random
import csv
import pygame as pg
from components.settings import *

class Particle():
    def __init__(self):
        self.particles = []

    def emit(self, screen):
        if self.particles:
            for particle in self.particles:
                particle[0][0] += particle[1][0]
                particle[0][1] += particle[1][1]
                particle[2] -= 0.2
                pg.draw.circle(screen, ORANGE, particle[0], int(particle[2]))

                if particle[2] <= 0:
                    self.particles.remove(particle)


    def add(self, pos):
        # for i in range(10):
        radius = random.randint(1, 3)
        direction = [random.randint(-2, 2), random.randint(-2, 2)]
        particle = [pos, direction, radius]
        self.particles.append(particle)

# other useful functions

def swap_color(img, old_c, new_c):
    img.set_colorkey(old_c)
    surf = img.copy()
    surf.fill(new_c)
    surf.blit(img, (0, 0))
    return surf

def get_scroll(true_scroll, player, score):
    if player.entity.obj.rect.centerx - true_scroll[0] - 10 >= WIDTH / 4 or player.entity.x == X_START:
        true_scroll[0] += (player.entity.obj.rect.centerx - true_scroll[0] - WIDTH / 4) / 20
    else:
        true_scroll[0] += 1 + score / 100
        
    
    true_scroll[1] += (player.entity.obj.rect.centery - true_scroll[1] - HEIGHT / 4) / 20
    scroll = true_scroll.copy()
    scroll[0] = round(scroll[0])  # ? Arrondie le scroll à l'entier pour que
    scroll[1] = round(scroll[1])  # ? les tiles soient placées au pixel près
    return true_scroll, scroll


def load_sounds(path):
    sounds = {}
    files = os.listdir(path)
    for file in files:
        sounds[file.replace(".wav", "")] = pg.mixer.Sound(path + file)

    return sounds

def draw_text(self, text, font, color, pos, is_centered = True, return_text = False):
    text_surf = self.fonts[font].render(text, True, color)
    text_rect = text_surf.get_rect()
    if is_centered:
        text_rect.center = pos
    else:
        text_rect.topleft = pos

    if return_text:
        return (text_surf, text_rect)

    self.display.blit(text_surf, text_rect)

def wait_for_key(self, key):
    waiting = True
    while waiting:
        self.clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                waiting = False
                self.running = False
            if event.type == pg.KEYUP and event.key == key:
                waiting = False

def dash_bar(self, progress):
    color = YELLOW
    if progress >= 1: 
        progress = 1
        color = ORANGE

    dash_border_rect = pg.Rect(DASH_BAR_POS, DASH_BAR_SIZE)
    pg.draw.rect(self.display, GRAY, dash_border_rect, 1)
    inner_bar_pos  = (DASH_BAR_POS[0] + 2, DASH_BAR_POS[1] + 2)
    inner_bar_size = ((DASH_BAR_SIZE[0] - 4) * progress, DASH_BAR_SIZE[1] - 4)
    pg.draw.rect(self.display, color, (inner_bar_pos, inner_bar_size))

    draw_text(self, "dash", "main", LIGHT, (dash_border_rect.centerx, dash_border_rect.centery - dash_border_rect.h - 3))

def dash_effect(self):
    for i in range(DASH_TIMER - self.player.dash_timer):
        if self.player.moving_right:
            self.player.entity.display(self.display, (self.scroll[0] + 7*i, self.scroll[1]), 255 - 35 * i)
        elif self.player.moving_left:
            self.player.entity.display(self.display, (self.scroll[0] - 7*i, self.scroll[1]), 255 - 35 * i)
    return screen_shake(self)

def screen_shake(self):
    random_shake = random.randint(0, SCREEN_SHAKE_FORCE) - SCREEN_SHAKE_FORCE / 2
    render_offset = [random_shake, random_shake]
    return render_offset

def score(self, score):
    draw_text(self, str(score), "main", LIGHT, (3, 3), False)