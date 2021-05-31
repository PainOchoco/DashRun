from components.entity import *
from components.settings import *

class Player(object):
    def __init__(self, x, y, size_x, size_y):
        """
        ### Description
        Classe du joueur

        ### Arguments:
        - x: `int` Position X
        - y: `int` Position Y
        - size_x: `int` Longueur
        - size_y: `int` Hauteur
        
        ### Propriétés
        - entity: `Entity` entité représentant le joueur
        - moving_right, moving_left, dashing: `bool` Inputs du joueur
        - dash_timer: `int` Temps du joueur en dash
        - dash_cooldown: `int` Temps de recharge du dash
        - air_timer: `int` Temps du joueur en l'air
        - momentum: `int` élan du joueur sur l'axe Y (utiliser pour le saut et l'atterissage)
        - movement: `tuple` Agit comme un vecteur pour le mouvement du joueur
        - collision_type: `dict` Collisions du joueur avec la map
        """

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

    def update(self, tile_rects, speed, dash_speed):
        """
        ### Description
        Mets à jour le joueur, le fait bouger, teste ses collisions avec la map et l'anime

        ### Arguments
        - tile_rects: `arr<Rect>` Liste de rectangles représentant les tiles de la map
        - speed: `int` Vitesse de course du joueur
        - dash_speed: `int` Vitesse de dash du joueur
        """
        self.move(speed, dash_speed)
        self.check_collisions(tile_rects)
        self.animate()

    def animate(self):
        """
        ### Description
        Anime le joueur en fonction de ses mouvements
        """

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
        
    def move(self, speed, dash_speed):
        """
        ### Description
        Fait bouger le joueur en fonction de sa vitesse

        ### Arguments
        - speed: `int` Vitesse de course du joueur
        - dash_speed: `int` Vitesse de dash du joueur
        """

        self.movement = [0, 0]

        if self.moving_right:
            self.movement[0] += SPEED
        elif self.moving_left:
            self.movement[0] -= SPEED
        
        self.dash_cooldown -= 1
        if self.dashing:
            self.dash(dash_speed)

        self.movement[1] += self.momentum
        self.momentum += 0.2

        if self.momentum > 3:
            self.momentum = 3

    def dash(self, dash_speed):
        self.dash_cooldown = DASH_COOLDOWN

        if self.moving_right:
            self.movement[0] += dash_speed
        if self.moving_left:
            self.movement[0] -= dash_speed
        
        self.dash_timer -= 1
        
        if self.dash_timer == 0:
            self.dashing = False

    def check_collisions(self, tile_rects):
        self.collision_types = self.entity.move(self.movement, tile_rects)

        if self.collision_types["bottom"]: # ? saut reset au sol
            self.momentum = 0
            self.air_timer = 0

        if self.collision_types["top"]: # ? bonk
            self.momentum = 3

        else:
            self.air_timer += 1