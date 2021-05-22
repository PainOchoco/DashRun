import pygame
import math
import os
import random
import csv
from settings import *
from pygame.locals import *

def collision_test(rect, tiles):
    """
    ### Description
    Vérification de collision entre un rectangle et les rectangles de tiles

    ### Arguments
    - rect: `rect` Rectangle dont on veut tester la collision
    - tiles: `array<rect>` Liste de rectangle représentant les tiles

    ### Retourne
    - hit_list: `array<rect>` La liste des tiles que le rectangle touche
    """
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list


class physics_obj(object):
    """
    ### Description 
    Classe permettant de créer et de bouger un objet physique.
    """

    def __init__(self, x, y, size_x, size_y):
        """
        ### Description
        Création d'un objet physique

        ### Arguments
        - x: `int` Position sur l'axe X de l'objet
        - y: `int` Position sur l'axe Y de l'objet
        - size_x: `int` Largeur de l'objet 
        - size_y: `int` Longueur de l'objet

        ### Propriétés
        - x: `int` Position sur l'axe X de l'objet
        - y: `int` Position sur l'axe Y de l'objet
        - width: `int` Largeur de l'objet 
        - height: `int` Longueur de l'objet
        - rect: `rect` Rectangle représentant l'objet
        """
        self.x = x
        self.y = y
        self.width = size_x
        self.height = size_y
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def move(self, movement, tiles):
        """
        ### Description
        Assure le mouvement d'un objet physique en fonction des tiles

        ### Arguments
        - movement: `vector` Vecteur du mouvement de l'objet
        - tiles: `array<rect>` Liste des rectangles représentant les tiles

        ### Retourne
        collision_types: `dict` Types de collisions causées par le mouvement
        """

        collision_types = {
            'top': False,
            'bottom': False,
            'right': False,
            'left': False,
            'data': []  # ? Enregistre le rectangle représentant la tile que l'objet à touché
                        # ? Pas utilisé pour l'instant mais ça peut être utile pour différentes textures (glace...)
        }

        # ? Test l'axe X
        self.x += movement[0]
        self.rect.x = int(self.x)

        block_hit_list = collision_test(self.rect, tiles)

        for block in block_hit_list:
            # ? Mouvement X positif, vers la droite
            if movement[0] > 0:
                self.rect.right = block.left  # ? Replacement de l'objet
                collision_types['right'] = True

            # ? Mouvement X négatif, vers la gauche
            elif movement[0] < 0:
                self.rect.left = block.right  # ? Replacement de l'objet
                collision_types['left'] = True

            collision_types['data'].append(block)
            self.x = self.rect.x

        # ? Test l'axe Y
        self.y += movement[1]
        self.rect.y = int(self.y)

        block_hit_list = collision_test(self.rect, tiles)

        for block in block_hit_list:

            # ? Mouvement Y positif, vers le bas
            if movement[1] > 0:
                self.rect.bottom = block.top  # ? Replacement de l'objet
                collision_types['bottom'] = True

            # ? Mouvement Y négatif, vers le haut
            elif movement[1] < 0:
                self.rect.top = block.bottom  # ? Replacement de l'objet
                collision_types['top'] = True

            collision_types['data'].append(block)
            self.change_y = 0
            self.y = self.rect.y

        return collision_types

def flip(img, boolean=True):
    """
    ### Description
    Retourne l'image sur l'axe Y

    ### Arguments
    - img: `surface` Image a retourner
    - boolean: `bool` Sens
    """
    return pygame.transform.flip(img, boolean, False)


def blit_center(surf, surf2, pos):
    """
    ### Description
    Affiche une surface au centre d'une autre surface

    ### Arguments
    - surf: `surface` Surface sur laquelle centrer la seconde surface
    - surf2: `surface` Surface à centrer
    - pos: `tuple` Positions de la surface à centrer
    """
    x = int(surf2.get_width() / 2)
    y = int(surf2.get_height() / 2)
    surf.blit(surf2, (pos[0] - x, pos[1] - y))


class entity(object):
    """
    ### Description
    Classe permettant de créer une entité et d'intéragir avec celle-ci.
    Une entité est composée de plusieurs propriétés et hérite de la classe `physics_obj`
    """

    global animation_database, animation_higher_database

    def __init__(self, x, y, size_x, size_y, e_type):
        """
        ### Description
        Création d'une entité

        ### Arguments
        - x: `int` Position sur l'axe X de l'objet
        - y: `int` Position sur l'axe Y de l'objet
        - x_size: `int` Largeur de l'objet 
        - y_size: `int` Longueur de l'objet
        - e_type: `str` Type d'entité

        ### Propriétés
        - x: `int` Position sur l'axe X de l'objet
        - y: `int` Position sur l'axe Y de l'objet
        - width: `int` Largeur de l'objet 
        - height: `int` Longueur de l'objet
        - obj: `physics_obj` L'objet physique de l'entité
        - animation: `array<str>` Animations récupérées de animation_higher_database
        - image: `surface` L'image de l'entité
        - animation_frame: `int` Indice des animations dans animation_higher_database 
        - animation_tags: `array<str>` Instructions pour gérer les animation (ex: loop)
        - flip: `bool` Si l'image de l'entité est retournée sur l'axe Y
        - offset: `tuple` Décalage de l'image par rapport à l'objet physique
        - rotation: `int` Angle de rotation de l'image de l'entité
        - e_type: `str` Type d'entité (utilisé pour les animations)
        - action_timer: `int` Timer pour une action spécifique
        - action: `str` Identifiant de l'action actuelle de l'entité
        - entity_data: `obj` Données de l'entités, on peut yeet plein de choses en plus là-dedans 
        """

        self.x = x
        self.y = y
        self.width = size_x
        self.height = size_y
        self.obj = physics_obj(x, y, size_x, size_y)
        self.animation = None
        self.image = None
        self.animation_frame = 0
        self.animation_tags = []
        self.flip = False
        self.offset = (0, 0)
        self.rotation = 0
        # ? Pour l'instant l'entity type est utilisé seulement pour les animations
        self.type = e_type
        self.action_timer = 0
        self.action = ''
        self.set_action('idle')  # ? Animation par défaut
        self.entity_data = {}

    def set_pos(self, x, y):
        """
        ### Description
        Change la position de l'entité, son objet physique et le rectangle de l'objet physique

        ### Arguments
        - x: `int` Position sur l'axe X
        - y: `int` Position sur l'axe Y
        """

        self.x = x
        self.y = y
        self.obj.x = x
        self.obj.y = y
        self.obj.rect.x = x
        self.obj.rect.y = y

    def move(self, movement, tiles):
        """
        ### Description
        Assure le mouvement de l'entité en fonction des tiles

        ### Arguments
        - movement: `vector` Vecteur du mouvement de l'objet
        - tiles: `array<rect>` Liste des rectangles représentant les tiles

        ### Retourne
        collision_types: `dict` Types de collisions causées par le mouvement
        """

        collision_types = self.obj.move(movement, tiles)
        self.x = self.obj.x
        self.y = self.obj.y
        return collision_types

    def rect(self):
        """
        ### Description
        Création du rectangle représentant l'entité avec sa positions et ses dimensions

        ### Retourne
        Le rectangle de l'entité
        """

        return pygame.Rect(self.x, self.y, self.width, self.height)

    def set_flip(self, boolean):
        self.flip = boolean

    def set_animation_tags(self, tags):
        self.animation_tags = tags

    def set_animation(self, sequence):
        self.animation = sequence
        self.animation_frame = 0

    def set_action(self, action_id, force=False):
        """
        ### Description
        Défini l'action de l'entité

        ### Arguments
        - action_id: `str` L'identifiant de l'action
        - force: `bool` Si l'action est reset (retour à la première frame de l'animation)
        """

        # ? Si c'est la même action on skip
        if (self.action == action_id) and (force == False):
            pass
        else:
            self.action = action_id
            anim = animation_higher_database[self.type][action_id]
            self.animation = anim[0]
            self.set_animation_tags(anim[1])
            self.animation_frame = 0

    def get_entity_angle(self, entity_2):
        """
        ### Description
        Calcule l'angle entre deux entités

        ### Arguments
        - entity_2: `entity` La deuxième entité nécessaire pour calculer l'angle
        """

        x1 = self.x + int(self.width / 2)
        y1 = self.y + int(self.height / 2)
        x2 = entity_2.x + int(entity_2.width / 2)
        y2 = entity_2.y + int(entity_2.height / 2)
        angle = math.atan((y2-y1)/(x2-x1))
        if x2 < x1:
            angle += math.pi # ? Simple trigo
        return angle

    def get_center(self):
        """
        ### Description
        Calcule la position du centre de l'entité
        """
        x = self.x + int(self.width / 2)
        y = self.y + int(self.height / 2)
        return [x, y]

    def clear_animation(self):
        """
        ### Description
        Efface l'ensemble d'animations de l'entité
        """
        self.animation = None

    def set_image(self, image):
        """
        ### Description
        Définie l'image de l'entité

        ### Arguments
        - image: `surface` Image de l'entité
        """

        self.image = image

    def set_offset(self, offset):
        """
        ### Description
        Définie le décalage entre l'image et l'objet physique de l'entité

        ### Arguments
        - offset: `tuple` Décalage X et Y
        """

        self.offset = offset

    def set_frame(self, index):
        """
        ### Description
        Définie l'indice spécifique de l'ensemble d'animation actuel

        ### Arguments
        - index: `int` Indice de l'ensemble d'animation actuel
        """

        self.animation_frame = index

    def handle(self):
        self.action_timer += 1
        self.change_frame(1)

    def change_frame(self, amount):
        """
        ### Description
        Avance le fil d'animation de l'entité d'un montant spécifique
        
        ### Arguments
        - amount: `int` Montant
        """

        self.animation_frame += amount
        if self.animation != None:
            while self.animation_frame < 0:
                if 'loop' in self.animation_tags:
                    self.animation_frame += len(self.animation)
                else:
                    self.animation = 0
            while self.animation_frame >= len(self.animation):
                if 'loop' in self.animation_tags:
                    self.animation_frame -= len(self.animation)
                else:
                    self.animation_frame = len(self.animation)-1

    def get_current_img(self):
        """
        ### Description
        Donne l'image actuelle de l'entité
        """

        if self.animation == None:
            if self.image != None:
                return flip(self.image, self.flip)
            else:
                return None
        else:
            return flip(animation_database[self.animation[self.animation_frame]], self.flip)

    def get_drawn_img(self):
        """
        ### Description
        Donne l'image actuelle de l'entité avec la rotation
        """

        image_to_render = None
        if self.animation == None:
            if self.image != None:
                image_to_render = flip(self.image, self.flip).copy()
        else:
            image_to_render = flip(
                animation_database[self.animation[self.animation_frame]], self.flip).copy()
        if image_to_render != None:
            image_to_render = pygame.transform.rotate(
                image_to_render, self.rotation)
            return image_to_render

    def display(self, surface, scroll):
        """
        ### Description
        Affiche l'image de l'entité en fonction du décalage et du scroll

        ### Arguments
        - surface: `surface` Surface sur laquelle afficher l'image
        - scroll: `tuple` Scroll actuel du jeu
        """
        
        image_to_render = self.get_drawn_img()
        center_x = image_to_render.get_width()/2
        center_y = image_to_render.get_height()/2

        blit_center(surface, image_to_render, (int(
            self.x)-scroll[0]+self.offset[0]+center_x, int(self.y)-scroll[1]+self.offset[1]+center_y))


class player(object):
    def __init__(self, x, y, size_x, size_y, e_type):
        self.entity = entity(x, y, size_x, size_y, e_type)
        self.moving_right = False
        self.moving_left = False
        self.dashing = False
        self.air_timer = 0
        self.momentum = 0
        self.movement = [0, 0]
        self.collision_types = {}

    def update(self, tile_rects):
        self.movement = [0, 0]

        if self.moving_right:
            self.movement[0] += SPEED
        if self.moving_left:
            self.movement[0] -= SPEED

        self.movement[1] += self.momentum
        self.momentum += 0.2

        if self.momentum > 3:
            self.momentum = 3
        
        self.animate()
        self.move(tile_rects)
        self.entity.change_frame(1)

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
        
    def move(self, tile_rects):
        self.collision_types = self.entity.move(self.movement, tile_rects)

        if self.collision_types["bottom"]:
            self.momentum = 0
            self.air_timer = 0
        else:
            self.air_timer += 1


# ? Animations !

# ? La base de données d'animations s'occupe de répertorier les images des animations,
# * Format : {'path': Surface}
# * Exemple : {'./assets/textures/player/idle/idle_0': <Surface(32x40x32 SW)>}
global animation_database
animation_database = {}

# ? La base de données supérieure s'occupe de répertorier les séquences d'un type d'animation, qui peut être composé de plusieurs ensembles d'animations
# ? Pour l'animation "idle" du joueur, la base de données stocke les surfaces de animation_database
# ? Et les répète le nombre de fois qu'une frame dans un type d'animation doit être affichée
# ? (Renseigné dans assets/textures/animations.txt)
# * Format : {'entity': {'animation_type': [[set1_animations1, ...], [set1_tag1] ...]}}
# * Exemple : {'player': {'idle': [['./assets/textures/player/idle/idle_0', ...], ['loop'] ...]}}
global animation_higher_database
animation_higher_database = {}


def animation_sequence(sequence, base_path):
    global animation_database
    result = []
    for frame in sequence:
        image_id = "{}/{}_{}".format(base_path,
                                     base_path.split("/")[-1], frame[0])
        # * Exemple : ./assets/textures/player/idle/idle_0
        image = pygame.image.load(image_id + '.png')

        animation_database[image_id] = image.copy()
        for i in range(frame[1]):
            result.append(image_id)
    return result


def get_frame(ID):
    global animation_database
    return animation_database[ID]


def load_animations(path):
    """
    ### Description
    Charge les animations spécifiés par le fichier animations.txt

    ### Arguments
    - path: `str` Chemin d'accès au fichier animations.txt 

    ### Fichier `animations.txt`
    `Format` : entity_type/animation_type sequence tags

    `Exemple` : player/idle 10,10,10,10 loop 
    """
    global animation_higher_database
    f = open(path + 'animations.txt', 'r')
    data = f.read()
    f.close()

    for animation in data.split('\n'):
        sections = animation.split(' ')
        animation_path = sections[0]
        entity_info = animation_path.split('/')
        entity_type = entity_info[0]
        animation_id = entity_info[1]

        timings = sections[1].split(",")
        tags = sections[2].split(",")

        sequence = []
        n = 0
        for timing in timings:
            sequence.append([n, int(timing)])
            n += 1

        anim_sequence = animation_sequence(sequence, path + animation_path)

        if entity_type not in animation_higher_database:
            animation_higher_database[entity_type] = {}

        animation_higher_database[entity_type][animation_id] = [
            anim_sequence.copy(), tags]


class world():
    def __init__(self, path, length, tileset):
        self.length = length
        self.world_map = {}
        self.tile_rects = []
        self.path = path
        self.map_files = []
        self.maps = []
        self.tileset = tileset
        self.tile_list = tileset.get_tile_list(TILE_SIZE, TILE_SIZE)
        self.offset = 1

    def generate(self):
        start = self.load_map("start.csv")
        self.slice_map(start)

        self.map_files = os.listdir(self.path + "/parts/")

        for i in range(self.length):
            map = self.load_map("/parts/" + random.choice(self.map_files))
            self.maps.append(map)
            self.slice_map(map, self.offset)
            self.offset += (len(map[0]) / CHUNK_SIZE)

    def load_map(self, file_name):
        data = list(csv.reader(open(self.path + file_name, "r")))
        return data

    def load_terrain(self, display, scroll):
        self.tile_rects = []

        for y in range(3):
            for x in range(4):
                target_x = x - 1 + int(round(scroll[0] / (CHUNK_SIZE * TILE_SIZE)))
                target_y = y - 1 + int(round(scroll[1] / (CHUNK_SIZE * TILE_SIZE)))
                target_chunk = "{};{}".format(str(target_x), str(target_y))

                if target_chunk not in self.world_map:
                    self.world_map[target_chunk] = [[4 for x in range(8)] for y in range(8)] # ? empty chunk

                for y_pos in range(CHUNK_SIZE):
                    for x_pos in range(CHUNK_SIZE):
                        tile = int(self.world_map[target_chunk][x_pos][y_pos])
                        tile_x = (target_x * CHUNK_SIZE + x_pos) * TILE_SIZE
                        tile_y = (target_y * CHUNK_SIZE + y_pos) * TILE_SIZE

                        # if tile != 4:
                        display.blit(self.tile_list[tile], (tile_x - scroll[0] + 10, tile_y - scroll[1]))

                        if tile not in [4, 9, 14, 19, 23, 24, 28, 29]:
                            self.tile_rects.append(pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE))
        return self.tile_rects
    
    def slice_map(self, map, offset = 0):
        height = int(len(map) / CHUNK_SIZE)
        width = int(len(map[0]) / CHUNK_SIZE)
    
        for h in range(height):
            for w in range(width):
                columns = []
                for i in range(CHUNK_SIZE):
                    rows = []
                    for j in range(CHUNK_SIZE):
                        rows.append(map[j + h * CHUNK_SIZE][i + w * CHUNK_SIZE])
                    columns.append(rows)
    
                chunk_name = "{};{}".format(int(w + offset), h)
                self.world_map[chunk_name] = columns

class Tileset():
    def __init__(self, path):
        self.image = pygame.image.load(path)

    def get_tile(self, x, y, w, h):
        tile = pygame.Surface((w, h))
        tile.blit(self.image, (0, 0), (x, y, w, h))    
        return tile

    def get_tile_list(self, w, h):
        tiles = []
        for height in range(int(self.image.get_height() / h)):
            for width in range(int(self.image.get_width() / w)):
                tile = pygame.Surface((w, h))
                tile.set_colorkey((0, 0, 0))
                tile.blit(self.image, (0, 0), (width * w, height * h, w, h))
                tiles.append(tile)

        return tiles


class particle():
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