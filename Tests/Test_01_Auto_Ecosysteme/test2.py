import pygame
import math
import random
import numpy as np
from collections import deque

# ======================
# CONFIG
# ======================
WIDTH = 800
HEIGHT = 600
FPS = 60
GENERATION_TIME = 5000  # Temps en ms pour chaque génération

# Couleurs
GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
ORANGE = (255, 120, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GRAY = (200, 200, 200)

# Paramètres de l'algorithme génétique
POPULATION_SIZE = 20
MUTATION_RATE = 0.2
MUTATION_STRENGTH = 0.3
ELITISM_RATE = 0.2  # Pourcentage des meilleurs à conserver

# ======================
# INIT PYGAME
# ======================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Renard vs Lapin - Algorithme Génétique")
clock = pygame.time.Clock()

# ======================
# FONCTIONS UTILES
# ======================
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def normalize(dx, dy):
    d = math.sqrt(dx*dx + dy*dy)
    if d == 0:
        return 0, 0
    return dx/d, dy/d

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def relu(x):
    return max(0, x)

def tanh(x):
    return math.tanh(x)

# ======================
# RÉSEAU DE NEURONES
# ======================
class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Initialisation des poids avec Xavier initialization
        self.weights1 = np.random.randn(input_size, hidden_size) / np.sqrt(input_size)
        self.bias1 = np.zeros((1, hidden_size))
        
        self.weights2 = np.random.randn(hidden_size, output_size) / np.sqrt(hidden_size)
        self.bias2 = np.zeros((1, output_size))
        
        self.fitness = 0
        
    def forward(self, inputs):
        # Transformation numpy
        inputs = np.array(inputs).reshape(1, -1)
        
        # Couche cachée
        hidden = np.dot(inputs, self.weights1) + self.bias1
        hidden = np.tanh(hidden)  # Activation tanh
        
        # Couche de sortie
        output = np.dot(hidden, self.weights2) + self.bias2
        output = np.tanh(output)  # Activation tanh pour sorties entre -1 et 1
        
        return output.flatten()
    
    def mutate(self, mutation_rate=MUTATION_RATE, strength=MUTATION_STRENGTH):
        # Mutation des poids
        mask1 = np.random.random(self.weights1.shape) < mutation_rate
        self.weights1 += mask1 * np.random.randn(*self.weights1.shape) * strength
        
        mask2 = np.random.random(self.weights2.shape) < mutation_rate
        self.weights2 += mask2 * np.random.randn(*self.weights2.shape) * strength
        
        # Mutation des biais
        mask_b1 = np.random.random(self.bias1.shape) < mutation_rate
        self.bias1 += mask_b1 * np.random.randn(*self.bias1.shape) * strength
        
        mask_b2 = np.random.random(self.bias2.shape) < mutation_rate
        self.bias2 += mask_b2 * np.random.randn(*self.bias2.shape) * strength
    
    def crossover(self, other):
        """Crossover avec un autre réseau"""
        child = NeuralNetwork(self.input_size, self.hidden_size, self.output_size)
        
        # Crossover uniforme
        mask1 = np.random.random(self.weights1.shape) > 0.5
        child.weights1 = self.weights1 * mask1 + other.weights1 * (1 - mask1)
        
        mask2 = np.random.random(self.weights2.shape) > 0.5
        child.weights2 = self.weights2 * mask2 + other.weights2 * (1 - mask2)
        
        # Biais
        mask_b1 = np.random.random(self.bias1.shape) > 0.5
        child.bias1 = self.bias1 * mask_b1 + other.bias1 * (1 - mask_b1)
        
        mask_b2 = np.random.random(self.bias2.shape) > 0.5
        child.bias2 = self.bias2 * mask_b2 + other.bias2 * (1 - mask_b2)
        
        return child
    
    def copy(self):
        """Copie le réseau"""
        new_nn = NeuralNetwork(self.input_size, self.hidden_size, self.output_size)
        new_nn.weights1 = self.weights1.copy()
        new_nn.weights2 = self.weights2.copy()
        new_nn.bias1 = self.bias1.copy()
        new_nn.bias2 = self.bias2.copy()
        return new_nn

# ======================
# CLASSES ANIMAUX
# ======================
class Animal:
    def __init__(self, x, y, color, speed, size):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.size = size
        self.alive = True
        self.fitness = 0
        self.time_survived = 0

    def draw(self, screen):
        if self.alive:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
            
            # Dessiner un petit indicateur de direction
            direction_length = self.size + 5
            end_x = self.x + math.cos(self.angle) * direction_length
            end_y = self.y + math.sin(self.angle) * direction_length
            pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 2)

class Lapin(Animal):
    def __init__(self, x, y, brain=None):
        super().__init__(x, y, WHITE, speed=3, size=8)
        # Inputs: distance au renard (2), position normalisée (2), angle actuel (1)
        # Outputs: angle de mouvement (1), vitesse (1)
        self.brain = brain if brain else NeuralNetwork(5, 8, 2)
        self.angle = random.uniform(0, 2 * math.pi)
        self.max_speed = 3.5
        
    def get_inputs(self, renard):
        # Normaliser les distances et positions
        dx = renard.x - self.x
        dy = renard.y - self.y
        dist = distance(self.x, self.y, renard.x, renard.y)
        
        # Inputs normalisés
        inputs = [
            dx / WIDTH,  # Distance X normalisée
            dy / HEIGHT, # Distance Y normalisée
            self.x / WIDTH,  # Position X normalisée
            self.y / HEIGHT, # Position Y normalisée
            self.angle / (2 * math.pi)  # Angle normalisé
        ]
        
        return inputs
    
    def update(self, renard):
        if not self.alive:
            return
            
        self.time_survived += 1
        
        # Calculer les entrées pour le réseau de neurones
        inputs = self.get_inputs(renard)
        outputs = self.brain.forward(inputs)
        
        # Interpréter les sorties
        # output[0]: nouvel angle (-1 à 1 -> -π à π)
        # output[1]: vitesse (-1 à 1 -> 0 à max_speed)
        
        angle_change = outputs[0] * math.pi
        self.angle = (self.angle + angle_change) % (2 * math.pi)
        
        speed_factor = (outputs[1] + 1) / 2  # Convertir de [-1,1] à [0,1]
        current_speed = speed_factor * self.max_speed
        
        # Déplacement
        self.x += math.cos(self.angle) * current_speed
        self.y += math.sin(self.angle) * current_speed
        
        # Limites écran avec rebond
        if self.x < 0:
            self.x = 0
            self.angle = math.pi - self.angle
        elif self.x > WIDTH:
            self.x = WIDTH
            self.angle = math.pi - self.angle
            
        if self.y < 0:
            self.y = 0
            self.angle = -self.angle
        elif self.y > HEIGHT:
            self.y = HEIGHT
            self.angle = -self.angle
            
        # Fitness: plus il survit longtemps, mieux c'est
        self.fitness = self.time_survived
        
        # Bonus pour rester loin du renard
        dist = distance(self.x, self.y, renard.x, renard.y)
        self.fitness += dist / 10
        
        # Pénalité s'il est trop proche du bord
        border_dist = min(self.x, WIDTH - self.x, self.y, HEIGHT - self.y)
        if border_dist < 50:
            self.fitness -= 10

class Renard(Animal):
    def __init__(self, x, y, brain=None):
        super().__init__(x, y, ORANGE, speed=2.5, size=10)
        # Inputs: distance au lapin (2), position normalisée (2), angle actuel (1)
        # Outputs: angle de mouvement (1), vitesse (1)
        self.brain = brain if brain else NeuralNetwork(5, 8, 2)
        self.angle = random.uniform(0, 2 * math.pi)
        self.max_speed = 3.0
        self.caught = 0  # Nombre de lapins attrapés
        
    def get_inputs(self, lapin):
        # Normaliser les distances et positions
        dx = lapin.x - self.x
        dy = lapin.y - self.y
        
        inputs = [
            dx / WIDTH,
            dy / HEIGHT,
            self.x / WIDTH,
            self.y / HEIGHT,
            self.angle / (2 * math.pi)
        ]
        
        return inputs
    
    def update(self, lapin):
        if not self.alive:
            return
            
        self.time_survived += 1
        
        # Calculer les entrées pour le réseau de neurones
        inputs = self.get_inputs(lapin)
        outputs = self.brain.forward(inputs)
        
        # Interpréter les sorties
        angle_change = outputs[0] * math.pi
        self.angle = (self.angle + angle_change) % (2 * math.pi)
        
        speed_factor = (outputs[1] + 1) / 2
        current_speed = speed_factor * self.max_speed
        
        # Déplacement
        self.x += math.cos(self.angle) * current_speed
        self.y += math.sin(self.angle) * current_speed
        
        # Limites écran avec rebond
        if self.x < 0:
            self.x = 0
            self.angle = math.pi - self.angle
        elif self.x > WIDTH:
            self.x = WIDTH
            self.angle = math.pi - self.angle
            
        if self.y < 0:
            self.y = 0
            self.angle = -self.angle
        elif self.y > HEIGHT:
            self.y = HEIGHT
            self.angle = -self.angle
            
        # Vérifier capture
        if lapin.alive and distance(self.x, self.y, lapin.x, lapin.y) < 15:
            lapin.alive = False
            self.caught += 1
            self.fitness += 1000  # Gros bonus pour attraper un lapin
            
        # Fitness: attrape rapidement et suit bien
        dist = distance(self.x, self.y, lapin.x, lapin.y)
        self.fitness += (HEIGHT - dist) / 10  # Plus il est proche, mieux c'est
        self.fitness += self.time_survived / 100  # Bonus pour la survie

# ======================
# ALGORITHME GÉNÉTIQUE
# ======================
class GeneticAlgorithm:
    def __init__(self, population_size, animal_type, hidden_size=8):
        self.population_size = population_size
        self.animal_type = animal_type
        self.hidden_size = hidden_size
        self.generation = 0
        self.best_fitness = 0
        self.best_individual = None
        self.fitness_history = []
        
        # Créer la population initiale
        self.population = self.create_initial_population()
        
    def create_initial_population(self):
        population = []
        for _ in range(self.population_size):
            if self.animal_type == "lapin":
                brain = NeuralNetwork(5, self.hidden_size, 2)
                animal = Lapin(random.randint(50, WIDTH-50), 
                              random.randint(50, HEIGHT-50), brain)
            else:  # renard
                brain = NeuralNetwork(5, self.hidden_size, 2)
                animal = Renard(random.randint(50, WIDTH-50), 
                               random.randint(50, HEIGHT-50), brain)
            population.append(animal)
        return population
    
    def select_parents(self):
        """Sélection par tournoi"""
        tournament_size = 3
        parents = []
        
        for _ in range(2):  # Sélectionner 2 parents
            tournament = random.sample(self.population, tournament_size)
            winner = max(tournament, key=lambda x: x.fitness)
            parents.append(winner)
            
        return parents
    
    def create_next_generation(self):
        # Trier par fitness
        sorted_pop = sorted(self.population, key=lambda x: x.fitness, reverse=True)
        
        # Élitisme: garder les meilleurs
        elite_count = int(self.population_size * ELITISM_RATE)
        new_population = []
        
        # Garder les meilleurs (élites)
        for i in range(elite_count):
            elite = sorted_pop[i]
            if self.animal_type == "lapin":
                new_animal = Lapin(random.randint(50, WIDTH-50),
                                  random.randint(50, HEIGHT-50),
                                  elite.brain.copy())
            else:
                new_animal = Renard(random.randint(50, WIDTH-50),
                                   random.randint(50, HEIGHT-50),
                                   elite.brain.copy())
            new_population.append(new_animal)
        
        # Remplir le reste de la population avec croisement et mutation
        while len(new_population) < self.population_size:
            # Sélection des parents
            parents = self.select_parents()
            
            # Croisement
            child_brain = parents[0].brain.crossover(parents[1].brain)
            
            # Mutation
            child_brain.mutate()
            
            # Créer le nouvel animal
            if self.animal_type == "lapin":
                child = Lapin(random.randint(50, WIDTH-50),
                             random.randint(50, HEIGHT-50),
                             child_brain)
            else:
                child = Renard(random.randint(50, WIDTH-50),
                              random.randint(50, HEIGHT-50),
                              child_brain)
                
            new_population.append(child)
        
        # Mettre à jour la population
        self.population = new_population
        self.generation += 1
        
        # Mettre à jour le meilleur individu
        best = max(sorted_pop, key=lambda x: x.fitness)
        if best.fitness > self.best_fitness:
            self.best_fitness = best.fitness
            self.best_individual = best.brain.copy()
        
        self.fitness_history.append(best.fitness)
        
        # Limiter l'historique de fitness
        if len(self.fitness_history) > 100:
            self.fitness_history.pop(0)
            
        return self.population
    
    def reset_fitness(self):
        """Réinitialiser les fitness pour une nouvelle génération"""
        for animal in self.population:
            animal.fitness = 0
            animal.time_survived = 0
            animal.alive = True
            animal.caught = 0
            # Réinitialiser la position
            animal.x = random.randint(50, WIDTH-50)
            animal.y = random.randint(50, HEIGHT-50)
            animal.angle = random.uniform(0, 2 * math.pi)

# ======================
# SIMULATION
# ======================
class Simulation:
    def __init__(self):
        self.ga_lapins = GeneticAlgorithm(POPULATION_SIZE // 2, "lapin")
        self.ga_renards = GeneticAlgorithm(POPULATION_SIZE // 2, "renard")
        self.current_lapin_index = 0
        self.current_renard_index = 0
        self.generation_start_time = pygame.time.get_ticks()
        self.match_start_time = pygame.time.get_ticks()
        self.match_duration = 5000  # 5 secondes par match
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 20)
        self.best_lapins_history = deque(maxlen=50)
        self.best_renards_history = deque(maxlen=50)
        
        # Initialiser le premier match
        self.current_lapin = self.ga_lapins.population[self.current_lapin_index]
        self.current_renard = self.ga_renards.population[self.current_renard_index]
        
    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Mettre à jour les animaux
        if self.current_lapin.alive:
            self.current_lapin.update(self.current_renard)
            self.current_renard.update(self.current_lapin)
        
        # Vérifier si le match est terminé (temps écoulé ou lapin mort)
        if (current_time - self.match_start_time > self.match_duration) or not self.current_lapin.alive:
            self.next_match()
            
        # Vérifier si la génération est terminée
        if self.current_lapin_index == 0 and self.current_renard_index == 0:
            if current_time - self.generation_start_time > GENERATION_TIME * len(self.ga_lapins.population):
                self.next_generation()
    
    def next_match(self):
        # Passer au prochain renard
        self.current_renard_index += 1
        
        # Si tous les renards ont été testés, passer au prochain lapin
        if self.current_renard_index >= len(self.ga_renards.population):
            self.current_renard_index = 0
            self.current_lapin_index += 1
            
            # Si tous les lapins ont été testés, revenir au début
            if self.current_lapin_index >= len(self.ga_lapins.population):
                self.current_lapin_index = 0
        
        # Sélectionner les nouveaux animaux
        self.current_lapin = self.ga_lapins.population[self.current_lapin_index]
        self.current_renard = self.ga_renards.population[self.current_renard_index]
        
        # Réinitialiser les positions
        self.current_lapin.x = random.randint(50, WIDTH-50)
        self.current_lapin.y = random.randint(50, HEIGHT-50)
        self.current_lapin.alive = True
        self.current_lapin.angle = random.uniform(0, 2 * math.pi)
        
        self.current_renard.x = random.randint(50, WIDTH-50)
        self.current_renard.y = random.randint(50, HEIGHT-50)
        self.current_renard.angle = random.uniform(0, 2 * math.pi)
        
        # Réinitialiser le temps du match
        self.match_start_time = pygame.time.get_ticks()
    
    def next_generation(self):
        print(f"Génération Lapins {self.ga_lapins.generation} - Meilleure fitness: {self.ga_lapins.best_fitness:.2f}")
        print(f"Génération Renards {self.ga_renards.generation} - Meilleure fitness: {self.ga_renards.best_fitness:.2f}")
        
        # Enregistrer les meilleurs fitness
        self.best_lapins_history.append(self.ga_lapins.best_fitness)
        self.best_renards_history.append(self.ga_renards.best_fitness)
        
        # Créer les nouvelles générations
        self.ga_lapins.create_next_generation()
        self.ga_renards.create_next_generation()
        
        # Réinitialiser les indices
        self.current_lapin_index = 0
        self.current_renard_index = 0
        
        # Réinitialiser les animaux actuels
        self.current_lapin = self.ga_lapins.population[0]
        self.current_renard = self.ga_renards.population[0]
        
        # Réinitialiser le temps de génération
        self.generation_start_time = pygame.time.get_ticks()
        self.match_start_time = pygame.time.get_ticks()
        
        # Réinitialiser les positions
        self.current_lapin.x = random.randint(50, WIDTH-50)
        self.current_lapin.y = random.randint(50, HEIGHT-50)
        self.current_lapin.alive = True
        
        self.current_renard.x = random.randint(50, WIDTH-50)
        self.current_renard.y = random.randint(50, HEIGHT-50)
    
    def draw(self, screen):
        # Fond
        screen.fill(GREEN)
        
        # Dessiner les animaux
        self.current_lapin.draw(screen)
        self.current_renard.draw(screen)
        
        # Dessiner la distance
        dist = distance(self.current_lapin.x, self.current_lapin.y, 
                       self.current_renard.x, self.current_renard.y)
        
        # Informations de débogage
        lapin_inputs = self.current_lapin.get_inputs(self.current_renard)
        renard_inputs = self.current_renard.get_inputs(self.current_lapin)
        
        # Interface utilisateur
        y_offset = 10
        
        # Générations
        gen_text = self.font.render(f"Génération Lapins: {self.ga_lapins.generation} | Renards: {self.ga_renards.generation}", 
                                   True, BLACK)
        screen.blit(gen_text, (10, y_offset))
        y_offset += 30
        
        # Match actuel
        match_text = self.font.render(f"Match: Lapin {self.current_lapin_index+1}/{len(self.ga_lapins.population)} | "
                                     f"Renard {self.current_renard_index+1}/{len(self.ga_renards.population)}", 
                                     True, BLACK)
        screen.blit(match_text, (10, y_offset))
        y_offset += 30
        
        # Fitness
        lapin_fitness = self.font.render(f"Fitness Lapin: {self.current_lapin.fitness:.1f}", True, BLUE)
        renard_fitness = self.font.render(f"Fitness Renard: {self.current_renard.fitness:.1f}", True, RED)
        screen.blit(lapin_fitness, (10, y_offset))
        screen.blit(renard_fitness, (WIDTH - 200, y_offset))
        y_offset += 30
        
        # Temps de survie
        time_text = self.font.render(f"Temps de survie: {self.current_lapin.time_survived} ticks", True, BLACK)
        screen.blit(time_text, (10, y_offset))
        y_offset += 30
        
        # Meilleures fitness
        best_lapin = self.font.render(f"Meilleur lapin: {self.ga_lapins.best_fitness:.1f}", True, BLUE)
        best_renard = self.font.render(f"Meilleur renard: {self.ga_renards.best_fitness:.1f}", True, RED)
        screen.blit(best_lapin, (10, y_offset))
        screen.blit(best_renard, (WIDTH - 200, y_offset))
        y_offset += 30
        
        # Distance
        dist_text = self.font.render(f"Distance: {dist:.1f}", True, BLACK)
        screen.blit(dist_text, (10, y_offset))
        y_offset += 30
        
        # État du lapin
        state_text = self.font.render(f"Lapin: {'VIVANT' if self.current_lapin.alive else 'MORT'}", 
                                     True, GREEN if self.current_lapin.alive else RED)
        screen.blit(state_text, (10, y_offset))
        y_offset += 40
        
        # Graphique des fitness (simplifié)
        self.draw_fitness_graph(screen, 10, HEIGHT - 150, 300, 120)
        
        # Instructions
        instructions = [
            "ALGORITHME GÉNÉTIQUE ACTIF",
            "Les lapins et renards apprennent à s'affronter",
            "Chaque génération améliore leurs stratégies"
        ]
        
        for i, text in enumerate(instructions):
            instr = self.small_font.render(text, True, BLACK)
            screen.blit(instr, (WIDTH - 350, 10 + i * 25))
    
    def draw_fitness_graph(self, screen, x, y, width, height):
        # Cadre
        pygame.draw.rect(screen, GRAY, (x, y, width, height))
        pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
        
        if len(self.best_lapins_history) < 2:
            return
            
        # Normaliser les données
        max_fitness = max(max(self.best_lapins_history), max(self.best_renards_history)) if self.best_renards_history else max(self.best_lapins_history)
        if max_fitness == 0:
            max_fitness = 1
            
        # Dessiner les courbes
        points_lapins = []
        points_renards = []
        
        for i, fitness in enumerate(self.best_lapins_history):
            x_pos = x + (i / len(self.best_lapins_history)) * width
            y_pos = y + height - (fitness / max_fitness) * height
            points_lapins.append((x_pos, y_pos))
            
        for i, fitness in enumerate(self.best_renards_history):
            x_pos = x + (i / len(self.best_renards_history)) * width
            y_pos = y + height - (fitness / max_fitness) * height
            points_renards.append((x_pos, y_pos))
        
        if len(points_lapins) > 1:
            pygame.draw.lines(screen, BLUE, False, points_lapins, 2)
        if len(points_renards) > 1:
            pygame.draw.lines(screen, RED, False, points_renards, 2)
        
        # Légende
        pygame.draw.rect(screen, BLUE, (x + 10, y + 10, 10, 10))
        pygame.draw.rect(screen, RED, (x + 10, y + 30, 10, 10))
        
        lapin_legend = self.small_font.render("Lapins", True, BLACK)
        renard_legend = self.small_font.render("Renards", True, BLACK)
        screen.blit(lapin_legend, (x + 25, y + 8))
        screen.blit(renard_legend, (x + 25, y + 28))

# ======================
# MAIN
# ======================
def main():
    simulation = Simulation()
    running = True
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Passer à la génération suivante manuellement
                    simulation.next_generation()
                elif event.key == pygame.K_r:
                    # Réinitialiser la simulation
                    simulation = Simulation()
        
        simulation.update()
        simulation.draw(screen)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()