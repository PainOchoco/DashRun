# coding: utf8

import math
import os
import random
import csv
import pygame as pg
from components.settings import *

def get_scroll(true_scroll, player, score):
    """
    ### Description
    Renvoie le nouveau scroll par rapport à la position du joueur et son score

    ### Arguments
    - true_scroll: `tuple` Scroll avec des nombres flottants
    - player: `Player`
    - score: `int`

    ### Renvoie
    - true_scroll: `tuple` Nouveau scroll avec des nombres flottants
    - scroll: `tuple` Nouveau scroll avec des nombres entiers
    """
    if player.entity.obj.rect.centerx - true_scroll[0] - 10 >= WIDTH / 4 or player.entity.x == X_START:
        true_scroll[0] += (player.entity.obj.rect.centerx - true_scroll[0] - WIDTH / 4) / 20
    else:
        true_scroll[0] += 1 + score / 100
        
    
    true_scroll[1] += (player.entity.obj.rect.centery - true_scroll[1] - HEIGHT / 4) / 20
    scroll = true_scroll.copy()
    scroll[0] = round(scroll[0])  # ? Arrondie le scroll à l'entier pour que
    scroll[1] = round(scroll[1])  # ? Tout soient placées au pixel près
    return true_scroll, scroll

# ! Finalement non utilisé, incontrôlable
def get_speed(score):
    """
    ### Description
    Change la vitesse du joueur en fonction du score

    ### Arguments
    - score: `int` Le score actuel du joueur

    ### Renvoie
    - speed: `int` Vitesse de course
    - dash_speed: `int` Vitesse de dash
    """
    speed = SPEED + score / 100
    dash_speed = DASH_SPEED + score / 100

    return speed, dash_speed

def load_sounds(path):
    """
    ### Description
    Charge les sons dans pygame depuis un dossier défini

    ### Arguments
    - path: `str` Chemin d'accès du dossier contenant des sons
    
    ### Renvoie
    - sounds: `dict<Sound>` Dictionnaire de sons chargés avec pygame
    """

    sounds = {}
    files = os.listdir(path)
    for file in files:
        sounds[file.replace(".wav", "")] = pg.mixer.Sound(path + file)

    return sounds

def draw_text(game, text, font, color, pos, is_centered = True, opacity = 255):
    """
    ### Description
    Dessine du texte

    ### Arguments
    - game: `Game` Instance du jeu pour pouvoir accéder à l'écran et aux fonts
    - text: `str` Texte à dessiner
    - font: `str` Nom de la font
    - color: `RGB` Couleur du texte
    - (optionel) is_centered: `bool` Si le texte est dessiné par rapport à son centre ou à son angle en haut à droite
    - (optionel) opacity: `int` L'opacité du texte
    """
    text_surf = game.fonts[font].render(text, True, color)
    text_surf.set_alpha(opacity)
    text_rect = text_surf.get_rect()
    if is_centered:
        text_rect.center = pos
    else:
        text_rect.topleft = pos

    game.display.blit(text_surf, text_rect)

# ! Pas eu le temps de faire une classe pour les menus, c'est pas très bien de faire comme ça
def death_screen(self, key):
    death_msg = random.choice(DEATH_MSG)
    waiting = True
    while waiting:
        self.display.fill(BG_COLOR)
        draw_text(self, death_msg, "title", YELLOW, (WIDTH / 4, HEIGHT / 8))
        draw_text(self, SCORE_MSG.format(self.score), "main", LIGHT, (WIDTH / 4, HEIGHT / 4))
        draw_text(self, PB_MSG.format(self.get_pb()), "main", ORANGE if self.score == self.get_pb() else LIGHT, (WIDTH / 4, (HEIGHT / 4) + FONT_SIZE * 2))
        draw_text(self, PRESS_KEY_MSG.format(pg.key.name(START_KEY)), "main", LIGHT, (WIDTH / 4, (HEIGHT / 4) + FONT_SIZE * 4))
        self.screen.blit(pg.transform.scale(self.display, WINDOW_SIZE), [0, 0])
        pg.display.flip()
        self.clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                waiting = False
                self.running = False
            elif event.type == pg.KEYUP:
                if event.key == key:
                    waiting = False

                elif event.key in FULLSCREEN_KEYS:
                    self.FULLSCREEN_MODE = not self.FULLSCREEN_MODE
                    if self.FULLSCREEN_MODE:
                        self.screen = pg.display.set_mode(WINDOW_SIZE, pg.FULLSCREEN | pg.SCALED | pg.DOUBLEBUF, TILE_SIZE)
                    else:
                        self.screen = pg.display.set_mode(WINDOW_SIZE, pg.RESIZABLE | pg.DOUBLEBUF, TILE_SIZE)


def home_screen(self, key):
    waiting = True
    while waiting:
        self.display.fill(BG_COLOR)
        draw_text(self, TITLE, "title", YELLOW, ((WIDTH / 4), HEIGHT / 8))

        draw_text(self, PRESS_KEY_MSG.format(pg.key.name(START_KEY)), "main", LIGHT, (WIDTH / 4, HEIGHT / 4))
        self.screen.blit(pg.transform.scale(self.display, WINDOW_SIZE), self.render_offset)
        pg.display.flip()
        
        self.clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                waiting = False
                self.running = False
            elif event.type == pg.KEYUP:
                if event.key == key:
                    waiting = False

                elif event.key in FULLSCREEN_KEYS:
                    self.FULLSCREEN_MODE = not self.FULLSCREEN_MODE
                    if self.FULLSCREEN_MODE:
                        self.screen = pg.display.set_mode(WINDOW_SIZE, pg.FULLSCREEN | pg.SCALED | pg.DOUBLEBUF, TILE_SIZE)
                    else:
                        self.screen = pg.display.set_mode(WINDOW_SIZE, pg.RESIZABLE | pg.DOUBLEBUF, TILE_SIZE)


def dash_bar(game, progress):
    """
    ### Description
    Affiche la barre de dash

    ### Arguments
    - game: `Game` Instance du jeu pour pouvoir accéder à l'écran sur lequel afficher la barre
    - progress: `int` Temps de recharge du dash
    """
    # ? Si la barre est pleine, afficher en orange
    color = YELLOW
    if progress >= 1: 
        progress = 1
        color = ORANGE

    # ? Bordure de la barre
    dash_border_rect = pg.Rect(DASH_BAR_POS, DASH_BAR_SIZE)
    pg.draw.rect(game.display, GRAY, dash_border_rect, 1)

    # ? Intérieur de la barre, ce qui va se remplir et se vider
    inner_bar_pos  = (DASH_BAR_POS[0] + 2, DASH_BAR_POS[1] + 2)
    inner_bar_size = ((DASH_BAR_SIZE[0] - 4) * progress, DASH_BAR_SIZE[1] - 4)
    pg.draw.rect(game.display, color, (inner_bar_pos, inner_bar_size))

    # ? Texte "dash" au-dessus de la barre
    draw_text(game, "dash", "main", LIGHT, (dash_border_rect.centerx, dash_border_rect.centery - dash_border_rect.h - 3))

def dash_effect(game):

    for i in range(DASH_TIMER - game.player.dash_timer):
        if game.player.moving_right:
            game.player.entity.display(game.display, (game.scroll[0] + 7*i, game.scroll[1]), 255 - 35 * i)
        elif game.player.moving_left:
            game.player.entity.display(game.display, (game.scroll[0] - 7*i, game.scroll[1]), 255 - 35 * i)
    return screen_shake()

def screen_shake():
    """
    ### Description
    Bouge l'écran de manière aléatoire pour donner un effet tremblement

    ### Renvoie
    - render_offset: `tuple` Décalage aléatoire en X et Y à appliquer au rendu du jeu
    """
    random_shake = random.randint(0, SCREEN_SHAKE_FORCE) - SCREEN_SHAKE_FORCE / 2
    render_offset = [random_shake, random_shake]
    return render_offset

def score(game, score, pb):
    """
    ### Description
    Affiche le score

    ### Arguments
    - game: `Game` Instance du jeu
    - score: `int` Score actuel du joueur à afficher
    - pb: `int` Meilleur score du joueur
    """

    # ? Si le joueur est en train d'avoir un meilleur score, le score s'affichera en orange
    draw_text(game, str(score), "main", ORANGE if score > pb else LIGHT, SCORE_POS, False)