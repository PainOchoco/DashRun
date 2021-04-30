import pygame
import sys
from pygame.locals import *

pygame.init()
clock = pygame.time.Clock()

pygame.display.set_caption("Dash Run")

WINDOW_SIZE = (600, 400)

# ? Initialise la fenêtre
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)

display = pygame.Surface((300, 200))

# ? Initialise le joueur
player_image = pygame.image.load("./assets/player/no_animation.png")

grass_image = pygame.image.load('./assets/grass.png')
TILE_SIZE = grass_image.get_width()

dirt_image = pygame.image.load('./assets/dirt.png')


def load_map(path):
    file = open(path+".txt", "r")  # ? Ouverture du fichier en read mode
    data = file.read()
    file.close()

    rows = data.split("\n")  # ? Divise la map en colonnes
    game_map = []

    for row in rows:
        game_map.append(list(row))

    return game_map


game_map = load_map("map")


def get_hit_tile(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list


def move(rect, movement, tiles):
    collision_types = {"top": False, "bottom": False,
                       "right": False, "left": False}
    rect.x += movement[0]

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
    50, 50, player_image.get_width(), player_image.get_height())

background_objects = [[0.25, [120, 10, 70, 400]], [0.25, [280, 30, 40, 400]], [
    0.5, [30, 40, 40, 400]], [0.5, [130, 90, 100, 400]], [0.5, [300, 80, 120, 400]]]

moving_right = False
moving_left = False

# ? Boucle du jeu
while True:
    # ? Efface l'écran
    display.fill((4, 44, 54))

    true_scroll[0] += (player_rect.x - true_scroll[0] - 150) / 20
    true_scroll[1] += (player_rect.y - true_scroll[1] - 100) / 20

    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])  # ? Arrondie le scroll à l'entier pour que
    scroll[1] = int(scroll[1])  # ? les tiles soient placés au pixel près

    pygame.draw.rect(display, (7, 80, 75), pygame.Rect(0, 120, 300, 80))

    for background_object in background_objects:
        rect_object = pygame.Rect(int(background_object[1][0] - scroll[0] * background_object[0]),
                                  int(background_object[1][1] - scroll[1] * background_object[0]),
                                  background_object[1][2], background_object[1][3])

        if background_object[0] == 0.5:
            pygame.draw.rect(display, (14, 222, 150), rect_object)
        else:
            pygame.draw.rect(display, (9, 91, 85), rect_object)

    tile_rects = []

    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == "1":
                display.blit(dirt_image, (x * TILE_SIZE -
                                          scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == "2":
                display.blit(grass_image, (x * TILE_SIZE -
                                           scroll[0], y * TILE_SIZE - scroll[1]))
            if tile != "0":
                tile_rects.append(pygame.Rect(
                    x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            x += 1
        y += 1

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

    player_rect, collisions = move(
        player_rect, player_movement, tile_rects)

    if collisions["bottom"]:
        player_y_momentum = 0
        air_timer = 0
    else:
        air_timer += 1

    display.blit(
        player_image, (int(player_rect.x - scroll[0]), int(player_rect.y - scroll[1])))

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

            if event.key == K_r:
                player_rect.x = 50
                player_rect.y = 50
                player_y_momentum = 0

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
