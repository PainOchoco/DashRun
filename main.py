import pygame as pg
import random
from components.animation import *
from components.settings import *
from components.player import *
from components.utils import *
from components.world import *
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

        self.tileset = Tileset("./assets/textures/tileset.png")
        load_animations("./assets/textures/")
        
        self.sounds = load_sounds("./assets/sounds/")
        self.sounds["jump"].set_volume(0.2)


    def new(self):
        self.player = Player(X_START, Y_START, 11, 40)
        self.world = World("./assets/maps/", 5, self.tileset)
        self.world.generate()
        self.run()

    def run(self):
        self.playing = True
        
        pg.mixer.music.load("./assets/music.wav")
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1)

        while self.playing:
            self.events()

            # ? Scroll
            self.true_scroll, self.scroll = get_scroll(self.true_scroll, self.player)
            if self.player.entity.y >= Y_LIMIT:
                self.player.entity.set_pos(X_START, Y_START)

            self.draw()
            self.clock.tick(FPS)


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
                elif event.key in LEFT_KEYS:
                    self.player.moving_left = True
                # ? ^
                elif event.key in UP_KEYS:
                    if self.player.air_timer < 10:  # ? Le joueur peut sauter s'il est dans les airs moins de 6 frames
                        # ? Pour pouvoir sauter au bord des plateformes
                        self.player.momentum = -5
                        self.sounds["jump"].play()  # ? bioup

                # ? V
                elif event.key in DOWN_KEYS:
                    self.player.momentum += 15

                # ? -->> Dash
                elif event.key in DASH_KEYS and not self.player.dashing and self.player.dash_cooldown <= 0:
                    self.player.dashing = True
                    self.player.dash_timer = DASH_TIMER
                    self.player.dash_cooldown = DASH_COOLDOWN


                # ? Fullscreen mode
                elif event.key in FULLSCREEN_KEYS:
                    self.FULLSCREEN_MODE = not self.FULLSCREEN_MODE
                    if self.FULLSCREEN_MODE:
                        self.screen = pg.display.set_mode(WINDOW_SIZE, pg.FULLSCREEN | pg.SCALED, 32)
                    else:
                        self.screen = pg.display.set_mode(WINDOW_SIZE, pg.RESIZABLE, 32)

                # ? Debug mode
                elif event.key in DEBUG_KEYS:
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
        self.display.fill(BG_COLOR)
        self.tile_rects = self.world.load_terrain(self.display, self.scroll)
        
        self.player.update(self.tile_rects)
        self.player.entity.display(self.display, self.scroll)

        if self.player.dashing:
            for i in range(DASH_TIMER - self.player.dash_timer):
                if self.player.moving_right:
                    self.player.entity.display(self.display, (self.scroll[0] + 5*i, self.scroll[1]), 255 - 35 * i)
                elif self.player.moving_left:
                    self.player.entity.display(self.display, (self.scroll[0] - 5*i, self.scroll[1]), 255 - 35 * i)



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
