import pygame as pg
import random
import engine
from settings import *
from pygame.locals import *

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.pre_init(44100, -16, 2, 512)
        pg.display.set_caption(TITLE)

        self.screen = pg.display.set_mode(WINDOW_SIZE, pg.RESIZABLE, 32)
        self.display = pg.Surface(DISPLAY_SIZE)
        self.clock = pg.time.Clock()
        self.running = True
        self.true_scroll = [0, 0]
        self.scroll = [0, 0]
        self.tile_rects = []

        self.FULLSCREEN_MODE = FULLSCREEN_MODE
        self.DEBUG_MODE = DEBUG_MODE

        self.tileset = engine.Tileset("./assets/textures/tileset.png")
        engine.load_animations("./assets/textures/")
        
        self.sounds = engine.load_sounds("./assets/sounds/")
        self.sounds["jump"].set_volume(0.2)


    def new(self):
        self.player = engine.player(X_START, Y_START, 11, 40, "player")
        self.world = engine.world("./assets/maps/", 5, self.tileset)
        self.world.generate()
        self.run()

    def run(self):
        self.playing = True
        
        pg.mixer.music.load("./assets/music.wav")
        pg.mixer.music.play(-1)

        while self.playing:
            self.events()

            # ? Scroll
            self.true_scroll, self.scroll = engine.get_scroll(self.true_scroll, self.player)

            self.draw()
            self.clock.tick(FPS)

            if self.player.entity.y >= Y_LIMIT:
                self.player.entity.set_pos(X_START, Y_START)

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing: self.playing = False
                self.running = False

            # ? Touche pressée
            if event.type == KEYDOWN:
                # ? ->
                if event.key in RIGHT_KEYS:
                    self.player.moving_right = True
                # ? <-
                if event.key in LEFT_KEYS:
                    self.player.moving_left = True
                # ? ^
                if event.key in UP_KEYS:
                    if self.player.air_timer < 10:  # ? Le joueur peut sauter s'il est dans les airs moins de 6 frames
                        # ? Pour pouvoir sauter au bord des plateformes
                        self.player.momentum = -5
                        self.sounds["jump"].play()  # ? bioup

                # ? V
                if event.key in DOWN_KEYS:
                    self.player.momentum += 15

                # ? Fullscreen mode
                if event.key in FULLSCREEN_KEYS:
                    self.FULLSCREEN_MODE = not self.FULLSCREEN_MODE
                    if self.FULLSCREEN_MODE:
                        self.screen = pg.display.set_mode(WINDOW_SIZE, pg.FULLSCREEN | pg.SCALED, 32)
                    else:
                        self.screen = pg.display.set_mode(WINDOW_SIZE, pg.RESIZABLE, 32)

                # ? Debug mode
                if event.key in DEBUG_KEYS:
                    self.DEBUG_MODE = not self.DEBUG_MODE

            # ? Touche lâchée
            if event.type == KEYUP:
                # ? ->
                if event.key in RIGHT_KEYS:
                    self.player.moving_right = False
                # ? <-
                if event.key in LEFT_KEYS:
                    self.player.moving_left = False


    def draw(self):
        self.display.fill((4, 44, 54))
        self.tile_rects = self.world.load_terrain(self.display, self.scroll)
        
        self.player.update(self.tile_rects)
        self.player.entity.display(self.display, self.scroll)

        self.screen.blit(pg.transform.scale(self.display, WINDOW_SIZE), (0, 0))
        pg.display.flip()

        if (self.DEBUG_MODE):
            debug_data = [
                "X\t{}".format(self.player.entity.x),
                "Y\t{}".format(self.player.entity.y),
                "FPS\t{}".format(int(round(self.clock.get_fps())))
            ]
            print("\n[DEBUG]")
            print("\n".join(debug_data))


game = Game()

while game.running:
    game.new()
