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

# ? Boucle du jeu
while True:
    for event in pygame.event.get():

        # ? Ferme le programme
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    display.update()
    clock.tick(60)  # ? 60FPS
