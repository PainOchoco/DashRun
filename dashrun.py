import pygame
import sys
from pygame.locals import *

pygame.init()
display = pygame.display
clock = pygame.time.Clock()

display.set_caption("Dash Run")

size = (400, 400)

# ? Initialise la fenêtre
screen = pygame.display.set_mode(size, 0, 32)

# ? Initialise le joueur
player_image = pygame.image.load("./assets/player/no_animation.png")

player_location = [50, 50]

moving_right = False
moving_left = False

player_y_momentum = 0

# ? Boucle du jeu
while True:
    # ? Efface l'écran
    screen.fill((4, 44, 54))

    # ? Affiche le joueur
    screen.blit(
        player_image, (int(player_location[0]), int(player_location[1])))

    # ? Mouvements
    if moving_right:
        player_location[0] += 4

    if moving_left:
        player_location[0] -= 4

    # ? Collision bordure
    if player_location[1] > size[1] - player_image.get_height():
        player_y_momentum = -player_y_momentum
    else:
        player_y_momentum += 0.2

    player_location[1] += player_y_momentum

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

        # ? Touche lâchée
        if event.type == KEYUP:
            # ? ->
            if event.key == K_RIGHT:
                moving_right = False
            # ? <-
            if event.key == K_LEFT:
                moving_left = False

    display.update()
    clock.tick(60)  # ? 60FPS
