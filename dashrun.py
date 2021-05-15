import pygame
import sys
import random
import engine
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

FONT_SIZE = 16

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


engine.load_animations("./assets/textures/")

grass_sound_timer = 0

game_map = {}

player_y_momentum = 0
air_timer = 0

true_scroll = (0, 0)

player = engine.entity(50, 50, 11, 40, "player")


moving_right = False
moving_left = False

background_objects = [[0.25, [120, 10, 70, 400]], [0.25, [280, 30, 40, 400]], [
    0.5, [30, 40, 40, 400]], [0.5, [130, 90, 100, 400]], [0.5, [300, 80, 120, 400]]]

# ? Boucle du jeu
while True:
    # ? Efface l'écran
    display.fill((4, 44, 54))
    # debug_menu.fill((0, 0, 0, 0))

    if grass_sound_timer > 0:
        grass_sound_timer -= 1

    # * just testing
    # if (true_scroll[0] + (player.x - true_scroll[0] - 150) / 20) >= true_scroll[0] + 1:
    #     true_scroll[0] += (player.x - true_scroll[0] - 150) / 20
    # else:
    #     true_scroll[0] += 1

    true_scroll[0] += (player.x - true_scroll[0] - 150) / 20
    true_scroll[1] += (player.y - true_scroll[1] - 100) / 20

    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])  # ? Arrondie le scroll à l'entier pour que
    scroll[1] = int(scroll[1])  # ? les tiles soient placées au pixel près

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

    # ? animation immobile
    if player_movement[0] == 0:
        player.set_action("idle")

    # ? animation mouvement vers la droite
    if player_movement[0] > 0:
        player.set_action("run")
        player.set_flip(False)

    # ? animation mouvement vers la gauche
    if player_movement[0] < 0:
        player.set_action("run")
        player.set_flip(True)

    # ? saut
    if player_movement[1] < 0:
        player.set_action("jump")

    collision_types = player.move(player_movement, tile_rects)

    if collision_types["bottom"]:
        player_y_momentum = 0
        air_timer = 0

        if player_movement[0] != 0 and grass_sound_timer == 0:
            grass_sound_timer = 30
            random.choice(grass_sounds).play()
    else:
        air_timer += 1

    player.change_frame(1)
    player.display(display, scroll)

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
                player.x = 50
                player.y = 50
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

    if (debug_mode):
        # ? https://www.dafont.com/upheaval.font
        debug_data = [
            "X:{}".format(player.x),
            "Y:{}".format(player.y),
            "FPS:{}".format(int(round(clock.get_fps())))]

        for line in range(len(debug_data)):
            # ! un peu laggy
            # debug_img = font.render(debug_data[line], True, (255, 255, 255))
            # debug_menu.blit(debug_img, (0, line * FONT_SIZE + 3))
            print(debug_data[line])

    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
    # screen.blit(pygame.transform.scale(debug_menu, WINDOW_SIZE), (0, 0))
    pygame.display.update()
    clock.tick(60)  # ? 60FPS
