import pygame
import random
import math

# --- Initialisation ---
pygame.init()
LARGEUR = 800
HAUTEUR = 600
screen = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Écosystème vivant")
VERT = (34, 139, 34)
clock = pygame.time.Clock()
FPS = 60

class Animal() :
    def __init__(self,speed,x,y,color):
        self.speed=speed
        self.x=x
        self.y=y
        self.color=color
    def dessiner(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 5)
        
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(VERT)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
