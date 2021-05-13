import pygame
import math
import os
from pygame.locals import *


def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list


class physics_obj(object):

    def __init__(self, x, y, x_size, y_size):
        self.width = x_size
        self.height = y_size
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.x = x
        self.y = y

    def move(self, movement, tiles):

        collision_types = {'top': False, 'bottom': False, 'right': False,
                           'left': False, 'data': []}

        # ? Test l'axe X
        self.x += movement[0]
        self.rect.x = int(self.x)

        block_hit_list = collision_test(self.rect, tiles)

        for block in block_hit_list:
            markers = [False, False, False, False]

            # ? Mouvement X positif, vers la droite
            if movement[0] > 0:
                self.rect.right = block.left
                collision_types['right'] = True
                markers[0] = True

            # ? Mouvement X négatif, vers la gauche
            elif movement[0] < 0:
                self.rect.left = block.right
                collision_types['left'] = True
                markers[1] = True

            collision_types['data'].append([block, markers])
            self.x = self.rect.x

        # ? Test l'axe Y
        self.y += movement[1]
        self.rect.y = int(self.y)

        block_hit_list = collision_test(self.rect, tiles)

        for block in block_hit_list:
            markers = [False, False, False, False]

            # ? Mouvement Y positif, vers le bas
            if movement[1] > 0:
                self.rect.bottom = block.top
                collision_types['bottom'] = True
                markers[2] = True

            # ? Mouvement Y négatif, vers le haut
            elif movement[1] < 0:
                self.rect.top = block.bottom
                collision_types['top'] = True
                markers[3] = True

            collision_types['data'].append([block, markers])
            self.change_y = 0
            self.y = self.rect.y

        return collision_types


def flip(img, boolean=True):
    return pygame.transform.flip(img, boolean, False)


def blit_center(surf, surf2, pos):
    x = int(surf2.get_width()/2)
    y = int(surf2.get_height()/2)
    surf.blit(surf2, (pos[0]-x, pos[1]-y))


class entity(object):
    global animation_database, animation_higher_database

    def __init__(self, x, y, size_x, size_y, e_type):  # x, y, size_x, size_y, type
        self.x = x
        self.y = y
        self.size_x = size_x
        self.size_y = size_y
        self.obj = physics_obj(x, y, size_x, size_y)
        self.animation = None
        self.image = None
        self.animation_frame = 0
        self.animation_tags = []
        self.flip = False
        self.offset = [0, 0]
        self.rotation = 0
        self.type = e_type  # used to determine animation set among other things
        self.action_timer = 0
        self.action = ''
        self.set_action('idle')  # overall action for the entity
        self.entity_data = {}
        self.alpha = None

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.obj.x = x
        self.obj.y = y
        self.obj.rect.x = x
        self.obj.rect.y = y

    def move(self, momentum, tiles):
        collisions = self.obj.move(momentum, tiles)
        self.x = self.obj.x
        self.y = self.obj.y
        return collisions

    def rect(self):
        return pygame.Rect(self.x, self.y, self.size_x, self.size_y)

    def set_flip(self, boolean):
        self.flip = boolean

    def set_animation_tags(self, tags):
        self.animation_tags = tags

    def set_animation(self, sequence):
        self.animation = sequence
        self.animation_frame = 0

    def set_action(self, action_id, force=False):
        if (self.action == action_id) and (force == False):
            pass
        else:
            self.action = action_id
            anim = animation_higher_database[self.type][action_id]
            self.animation = anim[0]
            self.set_animation_tags(anim[1])
            self.animation_frame = 0

    def get_entity_angle(self, entity_2):
        x1 = self.x+int(self.size_x/2)
        y1 = self.y+int(self.size_y/2)
        x2 = entity_2.x+int(entity_2.size_x/2)
        y2 = entity_2.y+int(entity_2.size_y/2)
        angle = math.atan((y2-y1)/(x2-x1))
        if x2 < x1:
            angle += math.pi
        return angle

    def get_center(self):
        x = self.x+int(self.size_x/2)
        y = self.y+int(self.size_y/2)
        return [x, y]

    def clear_animation(self):
        self.animation = None

    def set_image(self, image):
        self.image = image

    def set_offset(self, offset):
        self.offset = offset

    def set_frame(self, amount):
        self.animation_frame = amount

    def handle(self):
        self.action_timer += 1
        self.change_frame(1)

    def change_frame(self, amount):
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
        if self.animation == None:
            if self.image != None:
                return flip(self.image, self.flip)
            else:
                return None
        else:
            return flip(animation_database[self.animation[self.animation_frame]], self.flip)

    def get_drawn_img(self):
        image_to_render = None
        if self.animation == None:
            if self.image != None:
                image_to_render = flip(self.image, self.flip).copy()
        else:
            image_to_render = flip(
                animation_database[self.animation[self.animation_frame]], self.flip).copy()
        if image_to_render != None:
            center_x = image_to_render.get_width()/2
            center_y = image_to_render.get_height()/2
            image_to_render = pygame.transform.rotate(
                image_to_render, self.rotation)
            if self.alpha != None:
                image_to_render.set_alpha(self.alpha)
            return image_to_render, center_x, center_y

    def display(self, surface, scroll):
        image_to_render = None
        if self.animation == None:
            if self.image != None:
                image_to_render = flip(self.image, self.flip).copy()
        else:
            image_to_render = flip(
                animation_database[self.animation[self.animation_frame]], self.flip).copy()
        if image_to_render != None:
            center_x = image_to_render.get_width()/2
            center_y = image_to_render.get_height()/2
            image_to_render = pygame.transform.rotate(
                image_to_render, self.rotation)
            if self.alpha != None:
                image_to_render.set_alpha(self.alpha)
            blit_center(surface, image_to_render, (int(
                self.x)-scroll[0]+self.offset[0]+center_x, int(self.y)-scroll[1]+self.offset[1]+center_y))


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
                                     base_path.split("/")[-1], frame[0])  # ? Exemple : ./assets/textures/player/idle/idle_0
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
    Charge les animations spécifiés dans le fichier animations.txt

    Aide pour le fichier animations.txt :

    `Format` : entity_type/animation_type sequence tags

    `Exemple` : player/idle 10,10,10,10 loop 

    ### Paramètres
    - path: Chemin d'accès au fichier animations.txt 
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


def particle_file_sort(l):
    l2 = []
    for obj in l:
        l2.append(int(obj[:-4]))
    l2.sort()
    l3 = []
    for obj in l2:
        l3.append(str(obj) + '.png')
    return l3


global particle_images
particle_images = {}


def load_particle_images(path):
    global particle_images
    file_list = os.listdir(path)
    for folder in file_list:
        try:
            img_list = os.listdir(path + '/' + folder)
            img_list = particle_file_sort(img_list)
            images = []
            for img in img_list:
                images.append(pygame.image.load(
                    path + '/' + folder + '/' + img).convert())
            particle_images[folder] = images.copy()
        except:
            pass


class particle(object):

    def __init__(self, x, y, particle_type, motion, decay_rate, start_frame, custom_color=None):
        self.x = x
        self.y = y
        self.type = particle_type
        self.motion = motion
        self.decay_rate = decay_rate
        self.color = custom_color
        self.frame = start_frame

    def draw(self, surface, scroll):
        global particle_images
        if self.frame > len(particle_images[self.type])-1:
            self.frame = len(particle_images[self.type])-1
        if self.color == None:
            blit_center(surface, particle_images[self.type][int(
                self.frame)], (self.x-scroll[0], self.y-scroll[1]))
        else:
            blit_center(surface, swap_color(particle_images[self.type][int(
                self.frame)], (255, 255, 255), self.color), (self.x-scroll[0], self.y-scroll[1]))

    def update(self):
        self.frame += self.decay_rate
        running = True
        if self.frame > len(particle_images[self.type])-1:
            running = False
        self.x += self.motion[0]
        self.y += self.motion[1]
        return running


# other useful functions

def swap_color(img, old_c, new_c):
    img.set_colorkey(old_c)
    surf = img.copy()
    surf.fill(new_c)
    surf.blit(img, (0, 0))
    return surf
