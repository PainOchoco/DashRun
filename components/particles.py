import pygame as pg
import random
from components.settings import *

class Particle():
    def __init__(self):
        self.particles = []

    def emit(self, screen):
        """
        ### Description
        Affiche les particules

        ### Arguments
        - screen: `Surface` L'écran sur lequel émettre les particules
        """

        if self.particles:
            for particle in self.particles:
                particle[0][0] += particle[1][0]
                particle[0][1] += particle[1][1]
                particle[2] -= 0.2
                pg.draw.circle(screen, ORANGE, particle[0], int(particle[2]))

                if particle[2] <= 0:
                    self.particles.remove(particle)


    def add(self, pos, amount = 1):
        """
        ### Description
        Ajoute une particule à la liste, avec un rayon et une direction aléatoire

        ### Arguments
        - pos: `tuple` Position de la particule
        - (optionel) amout: `int` Montant de particules ajoutée (elles auront les mêmes propriétés)
        """        
        radius = random.randint(1, 3)
        direction = [random.randint(-2, 2), random.randint(-2, 2)]
        particle = [pos, direction, radius]
        self.particles.append(particle)
