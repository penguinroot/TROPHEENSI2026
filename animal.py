# animal.py
import pygame
import random

class Animal:
    def __init__(self, x, y, color, speed=2):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
    
    def move(self, width, height):
        """Déplacement aléatoire et rester dans les limites de la fenêtre"""
        self.x += random.randint(-self.speed, self.speed)
        self.y += random.randint(-self.speed, self.speed)
        self.x = max(0, min(width, self.x))
        self.y = max(0, min(height, self.y))
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 5)

# Sous-classes pour les espèces
class Lapin(Animal):
    def __init__(self, x, y):
        super().__init__(x, y, color=(255, 255, 255), speed=3)  # blanc, rapide

class Renard(Animal):
    def __init__(self, x, y):
        super().__init__(x, y, color=(255, 0, 0), speed=2)  # rouge, plus lent
    
    def peut_manger(self, lapin, distance=15):
        """Vérifie si le renard peut manger le lapin"""
        dx = self.x - lapin.x
        dy = self.y - lapin.y
        dist = (dx**2 + dy**2)**0.5
        return dist < distance
