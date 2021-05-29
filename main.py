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
        pg.event.set_allowed([QUIT, KEYDOWN, KEYUP])
        pg.display.set_caption(TITLE)

        self.screen = pg.display.set_mode(WINDOW_SIZE, pg.RESIZABLE | pg.DOUBLEBUF, TILE_SIZE)
        self.display = pg.Surface(DISPLAY_SIZE)

        self.clock = pg.time.Clock()
        self.score = 0
        
        self.running = True
        self.true_scroll = [0, 0]
        self.scroll = [0, 0]
        self.render_offset = [0, 0]
        self.tile_rects = []

        self.speed = SPEED
        self.dash_speed = DASH_SPEED

        self.particles = Particle()

        self.FULLSCREEN_MODE = FULLSCREEN_MODE
        self.DEBUG_MODE = DEBUG_MODE

        self.tileset = Tileset("./assets/textures/tileset.png")
        load_animations("./assets/textures/")
        
        self.sounds = load_sounds("./assets/sounds/")
        self.sounds["jump"].set_volume(0.2)
        self.sounds["dash"].set_volume(0.2)
        self.sounds["death"].set_volume(0.2)

        # ? Load fonts
        self.fonts = {}
        self.fonts["main"] = pg.font.Font("./assets/fonts/font.ttf", FONT_SIZE)
        self.fonts["title"] = pg.font.Font("./assets/fonts/title_font.ttf", FONT_SIZE * 2)



    def new(self):
        self.player = Player(X_START, Y_START, 11, 40)
        self.world = World("./assets/maps/", BIG_CHUNK_SIZE, self.tileset)
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
            self.true_scroll, self.scroll = get_scroll(self.true_scroll, self.player, self.score)
            self.speed, self.dash_speed = get_speed(self.score)

            if self.player.entity.obj.rect.centery >= Y_LIMIT or (self.player.entity.obj.rect.centerx - self.scroll[0]) <= 0:
                self.restart()

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
                    if self.player.air_timer < 10:  # ? Le joueur peut sauter s'il est dans les airs moins de 10 frames
                        # ? Pour pouvoir sauter au bord des plateformes
                        self.sounds["jump"].play()  # ? bioup
                        self.player.momentum = -5

                # ? V
                elif event.key in DOWN_KEYS:
                    self.player.momentum += 15

                # ? -->> Dash
                elif event.key in DASH_KEYS and not self.player.dashing and self.player.dash_cooldown <= 0 and (self.player.moving_right or self.player.moving_left):
                    self.sounds["dash"].play()
                    self.player.dashing = True
                    self.player.dash_timer = DASH_TIMER

                # ? Fullscreen mode
                elif event.key in FULLSCREEN_KEYS:
                    self.FULLSCREEN_MODE = not self.FULLSCREEN_MODE
                    if self.FULLSCREEN_MODE:
                        self.screen = pg.display.set_mode(WINDOW_SIZE, pg.FULLSCREEN | pg.SCALED | pg.DOUBLEBUF, TILE_SIZE)
                    else:
                        self.screen = pg.display.set_mode(WINDOW_SIZE, pg.RESIZABLE | pg.DOUBLEBUF, TILE_SIZE)

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
        
        for i in range(10):
            self.particles.add([0, 0 + i * (HEIGHT / 20)])
        self.particles.emit(self.display)

        self.player.update(self.tile_rects, self.speed, self.dash_speed)
        self.player.entity.display(self.display, self.scroll)


        if self.player.dashing:
            self.render_offset = dash_effect(self)
        dash_bar(self, (DASH_COOLDOWN - self.player.dash_cooldown) / DASH_COOLDOWN)

        if round(self.player.entity.x - X_START) / 16 >= self.score:
            self.score = round((self.player.entity.x - X_START) / 16)

        score(self, self.score, self.get_pb())

        self.screen.blit(pg.transform.scale(self.display, WINDOW_SIZE), self.render_offset)
        self.render_offset = [0, 0]

        pg.display.flip()

        if (self.DEBUG_MODE):
            debug_data = [
                "X\t{}".format(self.player.entity.x),
                "Y\t{}".format(self.player.entity.y),
                "FPS\t{}".format(int(round(self.clock.get_fps())))
            ]
            print("\n[DEBUG]")
            print("\n".join(debug_data))

    def save_score(self):
        if self.get_pb() < self.score:
            with open("score.txt", "w") as file:
                file.write(str(self.score))


    def get_pb(self):
        with open("score.txt", "r") as file:
            return int(file.read())

    def home_screen(self):
        self.display.fill(BG_COLOR)
        draw_text(self, TITLE, "title", YELLOW, (WIDTH / 4, HEIGHT / 8))
        draw_text(self, PRESS_KEY.format(pg.key.name(START_KEY)), "main", LIGHT, (WIDTH / 4, HEIGHT / 4))
        self.screen.blit(pg.transform.scale(self.display, WINDOW_SIZE), [0, 0])
        pg.display.flip()
        
        wait_for_key(self, START_KEY)

    def death_screen(self):
        self.display.fill(BG_COLOR)
        draw_text(self, random.choice(DEATH_MSG), "title", YELLOW, (WIDTH / 4, HEIGHT / 8))
        draw_text(self, SCORE.format(self.score), "main", LIGHT, (WIDTH / 4, HEIGHT / 4))
        draw_text(self, PB.format(self.get_pb()), "main", ORANGE if self.score == self.get_pb() else LIGHT, (WIDTH / 4, (HEIGHT / 4) + FONT_SIZE * 2))
        draw_text(self, PRESS_KEY.format(pg.key.name(START_KEY)), "main", LIGHT, (WIDTH / 4, (HEIGHT / 4) + FONT_SIZE * 4))
        self.screen.blit(pg.transform.scale(self.display, WINDOW_SIZE), [0, 0])
        pg.display.flip()

        wait_for_key(self, START_KEY)


    def restart(self):
        pg.mixer.music.stop()
        self.sounds["death"].play()
        self.save_score()
        self.death_screen()
        # ? Reset player stuff
        self.player.moving_right = False
        self.player.moving_left = False
        self.player.dashing = False
        self.player.dash_timer = 0
        self.player.dash_cooldown = 0
        self.player.air_timer = 0
        self.player.momentum = 0
        self.player.movement = [0, 0]
        self.player.entity.set_pos(X_START, Y_START)

        self.world = World("./assets/maps/", BIG_CHUNK_SIZE, self.tileset)
        self.world.generate()
        
        # ? Reset game stuff
        self.score = 0
        self.true_scroll = [0, 0]
        self.scroll = [0, 0]
        pg.mixer.music.play(-1)



game = Game()
game.home_screen()
while game.running:
    game.new()
