import pygame
from random import *
from math import *

# --- Initialisation ---
pygame.init()
LARGEUR = 800
HAUTEUR = 600
screen = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Écosystème vivant")
VERT = (34, 139, 34)
clock = pygame.time.Clock()
FPS = 60
class Nouritture():
    def __init__(self,x,y,color,):
        self.x=x
        self.y=y
        self.color=color
    def dessiner(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, 10, 10))
class Plante(Nouritture):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)

class Animal() :
    def __init__(self,speed,x,y,color):
        self.speed=speed
        self.x=x
        self.y=y
        self.color=color
    def dessiner(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 5)


class Lapin(Animal):
    def __init__(self, speed, x, y, color):
        super().__init__(speed, x, y, color)
    def aller_manger(self,lst_nouritture):
        dist_min=max(LARGEUR,HAUTEUR)
        nourr_plus_proche=0
        for i in lst_nouritture :
            dist_act=sqrt((i.x-self.x)**2+(i.y-self.y)**2)
            if dist_act < dist_min :
                dist_min=dist_act
                nourr_plus_proche = i
        if nourr_plus_proche == 0 : 
            return None
        if nourr_plus_proche.x > self.x :
            self.x+=1
        elif nourr_plus_proche.x < self.x :
            self.x-=1
        if nourr_plus_proche.y > self.y :
            self.y+=1
        elif nourr_plus_proche.y < self.y :
            self.y-=1
        if nourr_plus_proche.y == self.y and nourr_plus_proche.x == self.x :
            lst_nouritture.remove(nourr_plus_proche)
            return lst_nouritture
running = True
lapin=Lapin(2,10,10,(255,255,255))
plante=[Plante(100,200,(0,200,0))]
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(VERT)
    plante[0].dessiner()
    lapin.aller_manger(plante)
    lapin.dessiner()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()