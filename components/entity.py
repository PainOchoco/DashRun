# coding: utf8

import pygame as pg
import math
from components.settings import *
from components.animation import *

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

class Physics_obj(object):
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
        self.rect = pg.Rect(x, y, self.width, self.height)

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
    return pg.transform.flip(img, boolean, False)


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


class Entity(object):
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
        self.obj = Physics_obj(x, y, size_x, size_y)
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

        return pg.Rect(self.x, self.y, self.width, self.height)

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
            image_to_render = pg.transform.rotate(
                image_to_render, self.rotation)
            return image_to_render

    def display(self, surface, scroll, opacity = 255):
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
        image_to_render.set_alpha(opacity)

        blit_center(surface, image_to_render, (int(
            self.x)-scroll[0]+self.offset[0]+center_x, int(self.y)-scroll[1]+self.offset[1]+center_y))

