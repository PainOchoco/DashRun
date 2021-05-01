import pygame
import sys
import random
from pygame.locals import *

clock = pygame.time.Clock()
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

debug_mode = False

pygame.display.set_caption("Dash Run")

WINDOW_SIZE = (600, 400)

# ? Initialise la fenêtre
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)

display = pygame.Surface((300, 200))

# ? Charge les textures
grass_image = pygame.image.load('./assets/textures/grass.png')
dirt_image = pygame.image.load('./assets/textures/dirt.png')
plant_image = pygame.image.load("./assets/textures/plant.png")

tile_index = {1: grass_image, 2: dirt_image, 3: plant_image}

# ? Charge les sons et la musique
# ? https://opengameart.org/content/8-bit-jump-1
jump_sound = pygame.mixer.Sound("./assets/sounds/jump.wav")

grass_sounds = [pygame.mixer.Sound(
    "./assets/sounds/grass/grass_0.wav"), pygame.mixer.Sound("./assets/sounds/grass/grass_1.wav")]

# ? Ajustement du volume
jump_sound.set_volume(0.5)
grass_sounds[0].set_volume(0.2)
grass_sounds[1].set_volume(0.2)


# ? https://www.youtube.com/watch?v=gJNzwOwPlLE
pygame.mixer.music.load("./assets/sounds/music.wav")
pygame.mixer.music.play(-1)  # ? Joue la musique en boucle

TILE_SIZE = grass_image.get_width()
CHUNK_SIZE = 8


def generate_chunk(x, y):
    chunk_data = []
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos  # ? position exacte x de la tile
            target_y = y * CHUNK_SIZE + y_pos  # ? position exacte y de la tile

            tile_type = 0  # ? rien (air)

            if target_y > 10:
                tile_type = 2  # ? Terre
            elif target_y == 10:
                tile_type = 1  # ? Herbe
            elif target_y == 9:
                if random.randint(1, 5) == 1:
                    tile_type = 3  # ? 1/5 chance qu'il y ai une plante au dessus de l'herbe

            if tile_type != 0:  # ? On ajoute pas l'air
                # ? Position et type de la tile
                chunk_data.append([[target_x, target_y], tile_type])

    return chunk_data


global animation_frames
animation_frames = {}


def load_animation(path, frame_duration):
    global animation_frames
    # ? Nom de l'animation (dernier dossier)
    animation_name = path.split("/")[-1]
    animation_frame_data = []

    n = 0
    for frame in frame_duration:
        animation_frame_id = animation_name + "_" + str(n)
        img_path = path + "/" + animation_frame_id + ".png"
        animation_image = pygame.image.load(img_path)
        animation_frames[animation_frame_id] = animation_image.copy()

        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1

    return animation_frame_data


def change_action(action, frame, new_action):
    if action != new_action:
        action = new_action
        frame = 0
    return action, frame


animation_data = {}

animation_data["idle"] = load_animation(
    "./assets/textures/player/idle", [10, 10, 10, 10])
animation_data["run"] = load_animation(
    "./assets/textures/player/run", [5, 5, 5, 5, 5, 5, 5])
animation_data["jump"] = load_animation("./assets/textures/player/jump", [1])

player_action = "idle"
player_frame = 0
player_flip = False

grass_sound_timer = 0

game_map = {}


def get_hit_tile(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list


def move(rect, movement, tiles):
    collision_types = {"top": False, "bottom": False,
                       "right": False, "left": False}
    rect.x += int(movement[0])

    hit_list = get_hit_tile(rect, tiles)

    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types["right"] = True

        if movement[0] < 0:
            rect.left = tile.right
            collision_types["left"] = True

    rect.y += int(movement[1])
    hit_list = get_hit_tile(rect, tiles)

    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types["bottom"] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types["top"] = True

    return rect, collision_types


player_y_momentum = 0
air_timer = 0

true_scroll = [0, 0]

player_rect = pygame.Rect(
    50, 50, 11, 33)

background_objects = [[0.25, [120, 10, 70, 400]], [0.25, [280, 30, 40, 400]], [
    0.5, [30, 40, 40, 400]], [0.5, [130, 90, 100, 400]], [0.5, [300, 80, 120, 400]]]

moving_right = False
moving_left = False

# ? Boucle du jeu
while True:
    # ? Efface l'écran
    display.fill((4, 44, 54))

    if grass_sound_timer > 0:
        grass_sound_timer -= 1

    true_scroll[0] += (player_rect.x - true_scroll[0] - 150) / 20
    true_scroll[1] += (player_rect.y - true_scroll[1] - 100) / 20

    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])  # ? Arrondie le scroll à l'entier pour que
    scroll[1] = int(scroll[1])  # ? les tiles soient placés au pixel près

    # ? Background
    pygame.draw.rect(display, (7, 80, 75), pygame.Rect(0, 120, 300, 80))

    for background_object in background_objects:
        rect_object = pygame.Rect(int(background_object[1][0] - scroll[0] * background_object[0]),
                                  int(background_object[1][1] -
                                      scroll[1] * background_object[0]),
                                  background_object[1][2], background_object[1][3])

        if background_object[0] == 0.5:  # ? 2ème plan
            pygame.draw.rect(display, (14, 222, 150), rect_object)
        else:  # ? 3ème plan
            pygame.draw.rect(display, (9, 91, 85), rect_object)

    tile_rects = []

    for y in range(3):
        for x in range(4):
            target_x = x - 1 + int(round(scroll[0] / (CHUNK_SIZE * TILE_SIZE)))
            target_y = y - 1 + int(round(scroll[1] / (CHUNK_SIZE * TILE_SIZE)))
            target_chunk = "{};{}".format(str(target_x), str(target_y))

            if target_chunk not in game_map:
                game_map[target_chunk] = generate_chunk(target_x, target_y)

            for tile in game_map[target_chunk]:
                tile_x = tile[0][0] * TILE_SIZE
                tile_y = tile[0][1] * TILE_SIZE

                display.blit(tile_index[tile[1]],
                             (tile_x - scroll[0], tile_y - scroll[1]))

                if tile[1] in [1, 2]:  # ? terre ou herbe -> collision
                    tile_rects.append(pygame.Rect(
                        tile_x, tile_y, TILE_SIZE, TILE_SIZE))

    # ? Affiche le joueur

    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += 2
    if moving_left:
        player_movement[0] -= 2

    player_movement[1] += player_y_momentum
    player_y_momentum += 0.2

    if player_y_momentum > 3:
        player_y_momentum = 3

    # ? animation mouvement vers la droite
    if player_movement[0] > 0:
        player_action, player_frame = change_action(
            player_action, player_frame, "run")
        player_flip = False

    # ? animation immobile
    if player_movement[0] == 0:
        player_action, player_frame = change_action(
            player_action, player_frame, "idle")

    # ? animation mouvement vers la gauche
    if player_movement[0] < 0:
        player_action, player_frame = change_action(
            player_action, player_frame, "run")
        player_flip = True

    # ? saut
    if player_movement[1] < 0:
        player_action, player_frame = change_action(
            player_action, player_frame, "jump")

    player_rect, collisions = move(
        player_rect, player_movement, tile_rects)

    if collisions["bottom"]:
        player_y_momentum = 0
        air_timer = 0

        if player_movement[0] != 0 and grass_sound_timer == 0:
            grass_sound_timer = 30
            random.choice(grass_sounds).play()
    else:
        air_timer += 1

    player_frame += 1

    if player_frame >= len(animation_data[player_action]):
        player_frame = 0

    player_image_id = animation_data[player_action][player_frame]
    player_image = animation_frames[player_image_id]

    if (debug_mode):
        pygame.draw.rect(display, (255, 255, 0), pygame.Rect(
            player_rect.x - scroll[0], player_rect.y - scroll[1], player_rect.width, player_rect.height))

    display.blit(pygame.transform.flip(
        player_image, player_flip, False), (int(player_rect.centerx - scroll[0] - 15), int(player_rect.centery - scroll[1] - 22)))

    for event in pygame.event.get():
        # ? Ferme le programme
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # ? Touche pressée
        if event.type == KEYDOWN:
            # ? ->
            if event.key == K_RIGHT:
                moving_right = True
            # ? <-
            if event.key == K_LEFT:
                moving_left = True
            # ? ^
            if event.key == K_UP:
                if air_timer < 6:  # ? Le joueur peut sauter s'il est dans les airs moins de 6 frames
                    # ? Pour pouvoir sauter au bord des plateformes
                    player_y_momentum = -5
                    jump_sound.play()  # ? bioup
            # ? Restart
            if event.key == K_r:
                player_rect.x = 50
                player_rect.y = 50
                player_y_momentum = 0

            if event.key == K_F3:
                if (debug_mode):
                    debug_mode = False
                else:
                    debug_mode = True

        # ? Touche lâchée
        if event.type == KEYUP:
            # ? ->
            if event.key == K_RIGHT:
                moving_right = False
            # ? <-
            if event.key == K_LEFT:
                moving_left = False

    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
    pygame.display.update()
    clock.tick(60)  # ? 60FPS
