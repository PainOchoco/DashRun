from components.entity import *
from components.settings import *

class Player(object):
    def __init__(self, x, y, size_x, size_y):
        self.entity = Entity(x, y, size_x, size_y, "player")
        self.moving_right = False
        self.moving_left = False
        self.dashing = False
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.air_timer = 0
        self.momentum = 0
        self.movement = [0, 0]
        self.collision_types = {}

    def update(self, tile_rects):
        self.move()
        self.check_collisions(tile_rects)
        self.animate()

    def animate(self):
        # ? animation immobile
        if self.movement[0] == 0:
            self.entity.set_action("idle")

        # ? animation mouvement vers la droite
        if self.movement[0] > 0:
            self.entity.set_action("run")
            self.entity.set_flip(False)

        # ? animation mouvement vers la gauche
        if self.movement[0] < 0:
            self.entity.set_action("run")
            self.entity.set_flip(True)

        # ? saut
        if self.movement[1] < 0:
            self.entity.set_action("jump")

        self.entity.change_frame(1)
        
    def move(self):
        self.movement = [0, 0]

        if self.moving_right:
            self.movement[0] += SPEED
        elif self.moving_left:
            self.movement[0] -= SPEED
        
        self.dash_cooldown -= 1
        if self.dashing:
            self.dash()

        self.movement[1] += self.momentum
        self.momentum += 0.2

        if self.momentum > 3:
            self.momentum = 3

    def dash(self):
        self.dash_cooldown = DASH_COOLDOWN

        if self.moving_right:
            self.movement[0] += DASH_SPEED
        if self.moving_left:
            self.movement[0] -= DASH_SPEED
        
        self.dash_timer -= 1
        
        if self.dash_timer == 0:
            self.dashing = False

    def check_collisions(self, tile_rects):
        self.collision_types = self.entity.move(self.movement, tile_rects)

        if self.collision_types["bottom"]:
            self.momentum = 0
            self.air_timer = 0

        if self.collision_types["top"]: # ? bonk
            self.momentum = 3

        else:
            self.air_timer += 1