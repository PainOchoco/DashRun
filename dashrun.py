import pygame
import sys
from pygame.locals import *

pygame.init()
clock = pygame.time.Clock()

pygame.display.set_caption("Dash Run")

WINDOW_SIZE = (400, 400)

# ? Initialise la fenêtre
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)

display = pygame.Surface((300, 300))

# ? Initialise le joueur
player_image = pygame.image.load("./assets/player/no_animation.png")

grass_image = pygame.image.load('./assets/grass.png')
TILE_SIZE = grass_image.get_width()

dirt_image = pygame.image.load('./assets/dirt.png')

game_map = [['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
            ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
                '0', '0', '0', '0', '0', '0', '0', '0', '0'],
            ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
                '0', '0', '0', '0', '0', '0', '0', '0', '0'],
            ['0', '0', '0', '0', '0', '0', '0', '2', '2', '2',
                '2', '2', '0', '0', '0', '0', '0', '0', '0'],
            ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
                '0', '0', '0', '0', '0', '0', '0', '0', '0'],
            ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
                '0', '0', '0', '0', '0', '0', '0', '0', '0'],
            ['2', '2', '0', '0', '0', '0', '0', '0', '0', '0',
                '0', '0', '0', '0', '0', '0', '0', '2', '2'],
            ['1', '1', '2', '2', '2', '2', '2', '2', '2', '2',
                '2', '2', '2', '2', '2', '2', '2', '1', '1'],
            ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1',
                '1', '1', '1', '1', '1', '1', '1', '1', '1'],
            ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1',
                '1', '1', '1', '1', '1', '1', '1', '1', '1'],
            ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1',
                '1', '1', '1', '1', '1', '1', '1', '1', '1'],
            ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1',
                '1', '1', '1', '1', '1', '1', '1', '1', '1'],
            ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1']]


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
player_entity = pygame.Rect(
    50, 50, player_image.get_width(), player_image.get_height())

moving_right = False
moving_left = False

test_rectangle = pygame.Rect(100, 100, 100, 50)

# ? Boucle du jeu
while True:
    # ? Efface l'écran
    display.fill((4, 44, 54))

    tile_rects = []

    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == "1":
                display.blit(dirt_image, (x * TILE_SIZE, y * TILE_SIZE))
            if tile == "2":
                display.blit(grass_image, (x * TILE_SIZE, y * TILE_SIZE))
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

    player_entity, collisions = move(
        player_entity, player_movement, tile_rects)

    if collisions["bottom"]:
        player_y_momentum = 0
        air_timer = 0
    else:
        air_timer += 1

    display.blit(
        player_image, (int(player_entity.x), int(player_entity.y)))

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
                    player_y_momentum = -5

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
