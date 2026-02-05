import pygame
import random
import sys
import math

# --- INITIALISATION ---
pygame.init()

# --- CONSTANTES & CONFIGURATION ---
LARGEUR, HAUTEUR = 800, 600
TITRE = "Eco-Explorer: Prototype Alpha"
FPS = 60

# Couleurs (R, G, B)
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
VERT_FORET = (34, 139, 34)
BLEU_NUIT = (10, 10, 50)
ROUGE_INTERFACE = (200, 50, 50)
GRIS = (100, 100, 100)
OR = (255, 215, 0)

# Paramètres Jeu
MAX_PHOTOS = 5
CYCLE_JOUR_NUIT = 2000 # Durée du cycle en frames

# --- CLASSES ---

class Animal(pygame.sprite.Sprite):
    def __init__(self, nom, x, y, couleur, rareté, est_nocturne=False):
        super().__init__()
        self.nom = nom
        self.image = pygame.Surface((30, 30))
        self.image.fill(couleur) # Remplacé par un sprite plus tard
        self.rect = self.image.get_rect(center=(x, y))
        self.couleur = couleur
        self.rareté = rareté
        self.est_nocturne = est_nocturne
        self.vitesse = 1 if rareté < 3 else 2
        self.direction = pygame.math.Vector2(random.choice([-1, 1]), random.choice([-1, 1]))
        self.timer_mouvement = 0

    def update(self, est_nuit):
        # Gestion Apparition (Jour/Nuit)
        visible = True
        if self.est_nocturne and not est_nuit:
            visible = False
        elif not self.est_nocturne and est_nuit:
            visible = False
        
        if not visible:
            self.image.set_alpha(0) # Invisible
            return
        else:
            self.image.set_alpha(255)

        # IA Simple : Déplacement aléatoire
        self.timer_mouvement += 1
        if self.timer_mouvement > 100:
            self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
            self.timer_mouvement = 0
        
        # Déplacement et rebond sur les bords
        self.rect.x += self.direction.x * self.vitesse
        self.rect.y += self.direction.y * self.vitesse

        if self.rect.left < 0 or self.rect.right > LARGEUR: self.direction.x *= -1
        if self.rect.top < 0 or self.rect.bottom > HAUTEUR: self.direction.y *= -1

class Joueur(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((50, 100, 200)) # Bleu pour le joueur
        self.rect = self.image.get_rect(center=(LARGEUR//2, HAUTEUR//2))
        self.vitesse = 4
        self.inventaire_photos = []
        self.xp = 0
        self.argent = 0

    def mouvement(self, touches):
        if touches[pygame.K_LEFT]: self.rect.x -= self.vitesse
        if touches[pygame.K_RIGHT]: self.rect.x += self.vitesse
        if touches[pygame.K_UP]: self.rect.y -= self.vitesse
        if touches[pygame.K_DOWN]: self.rect.y += self.vitesse
        
        # Limites écran
        self.rect.clamp_ip(pygame.Rect(0, 0, LARGEUR, HAUTEUR))

# --- MOTEUR DE JEU ---

def afficher_texte(surface, texte, taille, x, y, couleur=BLANC):
    font = pygame.font.SysFont("Arial", taille)
    img_texte = font.render(texte, True, couleur)
    surface.blit(img_texte, (x, y))

def simulation_quiz(ecran, animal_nom):
    """Mini-jeu de quiz simple quand une photo est prise"""
    questions = {
        "Renard": {"q": "Que mange le renard ?", "r": ["Des Pizza", "Omnivore", "Juste de l'herbe"], "bon": 1},
        "Hibou": {"q": "Quand chasse le hibou ?", "r": ["La nuit", "Le midi", "Au goûter"], "bon": 0},
        "Papillon": {"q": "Quelle est la larve du papillon ?", "r": ["L'asticot", "La chenille", "Le ver"], "bon": 1}
    }
    
    data = questions.get(animal_nom, {"q": "Est-ce un animal rare ?", "r": ["Oui", "Non"], "bon": 0})
    
    en_quiz = True
    while en_quiz:
        pygame.draw.rect(ecran, (30, 30, 30), (100, 100, 600, 400))
        pygame.draw.rect(ecran, BLANC, (100, 100, 600, 400), 2)
        
        afficher_texte(ecran, f"QUIZ : {animal_nom}", 40, 150, 120, OR)
        afficher_texte(ecran, data["q"], 30, 150, 180)
        
        # Afficher les options (1, 2, 3)
        y_pos = 250
        for i, rep in enumerate(data["r"]):
            afficher_texte(ecran, f"{i+1}. {rep}", 30, 150, y_pos)
            y_pos += 50
            
        afficher_texte(ecran, "Appuyez sur 1, 2 ou 3", 20, 150, 450, GRIS)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                touche = -1
                if event.key == pygame.K_1: touche = 0
                if event.key == pygame.K_2: touche = 1
                if event.key == pygame.K_3: touche = 2
                
                if touche != -1 and touche < len(data["r"]):
                    return touche == data["bon"] # Retourne Vrai si bonne réponse

def main():
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption(TITRE)
    clock = pygame.time.Clock()

    # Création des groupes
    groupe_animaux = pygame.sprite.Group()
    joueur = Joueur()
    
    # Peuplement du biome (Nom, X, Y, Couleur, Rareté, Nocturne?)
    groupe_animaux.add(Animal("Renard", 200, 200, (255, 140, 0), 2, False)) # Orange
    groupe_animaux.add(Animal("Hibou", 500, 100, (100, 50, 0), 3, True))    # Marron foncé (Nuit)
    groupe_animaux.add(Animal("Papillon", 400, 400, (255, 192, 203), 1, False)) # Rose
    
    # Variables d'état
    mode_photo = False
    zoom_level = 1.0
    timer_jour = 0
    est_nuit = False
    message_feedback = ""
    timer_feedback = 0

    running = True
    while running:
        dt = clock.tick(FPS)
        ecran.fill(VERT_FORET) # Fond biome

        # --- GESTION ÉVÉNEMENTS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Molette pour zoomer
            if event.type == pygame.MOUSEWHEEL:
                if mode_photo:
                    zoom_level += event.y * 0.1
                    zoom_level = max(1.0, min(3.0, zoom_level)) # Clamp zoom

            if event.type == pygame.KEYDOWN:
                # Espace pour activer/désactiver l'appareil photo
                if event.key == pygame.K_SPACE:
                    mode_photo = not mode_photo
                    zoom_level = 1.0 # Reset zoom
                
                # Entrée pour prendre la photo (si mode photo actif)
                if event.key == pygame.K_RETURN and mode_photo:
                    if len(joueur.inventaire_photos) >= MAX_PHOTOS:
                        message_feedback = "Carte SD pleine !"
                        timer_feedback = 60
                    else:
                        # Logique de prise de vue
                        sujet_trouve = None
                        viseur_rect = pygame.Rect(0, 0, 200/zoom_level, 200/zoom_level)
                        viseur_rect.center = joueur.rect.center
                        
                        for animal in groupe_animaux:
                            # Si l'animal est invisible (nuit/jour), on ne peut pas le prendre
                            if animal.image.get_alpha() == 0: continue

                            if viseur_rect.colliderect(animal.rect):
                                sujet_trouve = animal
                                break
                        
                        if sujet_trouve:
                            # Lancer le Quiz
                            reussite_quiz = simulation_quiz(ecran, sujet_trouve.nom)
                            bonus = 50 if reussite_quiz else 10
                            
                            joueur.xp += (100 * sujet_trouve.rareté) + bonus
                            joueur.inventaire_photos.append(sujet_trouve.nom)
                            joueur.argent += 10 if reussite_quiz else 0
                            
                            message_feedback = f"Photo : {sujet_trouve.nom} ! (+{bonus} Eco-Cred)"
                        else:
                            message_feedback = "Photo floue / Rien en vue..."
                        
                        timer_feedback = 120 # 2 secondes

        # --- MISE À JOUR ---
        
        # Cycle Jour / Nuit
        timer_jour += 1
        if timer_jour > CYCLE_JOUR_NUIT:
            timer_jour = 0
            est_nuit = not est_nuit
        
        # Mouvement Joueur (bloqué si en mode photo)
        touches = pygame.key.get_pressed()
        if not mode_photo:
            joueur.mouvement(touches)
        
        groupe_animaux.update(est_nuit)

        # --- DESSIN ---
        
        # 1. Dessiner les animaux
        groupe_animaux.draw(ecran)
        
        # 2. Dessiner le joueur
        ecran.blit(joueur.image, joueur.rect)
        
        # 3. Filtre Nuit (Overlay)
        if est_nuit:
            overlay = pygame.Surface((LARGEUR, HAUTEUR))
            overlay.set_alpha(150) # Transparence
            overlay.fill(BLEU_NUIT)
            ecran.blit(overlay, (0,0))
            afficher_texte(ecran, "NUIT", 20, LARGEUR-60, 10, BLANC)
        else:
            afficher_texte(ecran, "JOUR", 20, LARGEUR-60, 10, OR)

        # 4. Interface Appareil Photo
        if mode_photo:
            # Assombrir le tour pour simuler le focus
            overlay_photo = pygame.Surface((LARGEUR, HAUTEUR))
            overlay_photo.set_alpha(100)
            overlay_photo.fill(NOIR)
            
            # Créer le trou du viseur (calcul selon zoom)
            taille_viseur = 200 / zoom_level
            rect_viseur = pygame.Rect(0, 0, taille_viseur, taille_viseur)
            rect_viseur.center = joueur.rect.center
            
            # Dessiner l'overlay sauf le viseur (technique du masque simple ici simulée par 4 rectangles pour simplifier)
            # Pour faire simple dans ce proto : on dessine juste le cadre du viseur
            ecran.blit(overlay_photo, (0,0))
            pygame.draw.rect(ecran, BLANC, rect_viseur, 2)
            pygame.draw.circle(ecran, ROUGE_INTERFACE, rect_viseur.center, 2) # Point central
            
            afficher_texte(ecran, f"ZOOM: x{zoom_level:.1f}", 20, 10, 50, ROUGE_INTERFACE)
            afficher_texte(ecran, "[ENTRÉE] PRENDRE PHOTO", 20, 10, 80, BLANC)

        # 5. Interface UI (HUD)
        afficher_texte(ecran, f"XP: {joueur.xp} | Argent: {joueur.argent}E", 25, 10, 10)
        afficher_texte(ecran, f"SD: {len(joueur.inventaire_photos)}/{MAX_PHOTOS}", 25, 250, 10)
        
        if not mode_photo:
            afficher_texte(ecran, "[ESPACE] MODE PHOTO", 20, 10, HAUTEUR-30, BLANC)

        # Feedback textuel (ex: "Photo réussie")
        if timer_feedback > 0:
            afficher_texte(ecran, message_feedback, 30, LARGEUR//2 - 100, HAUTEUR - 100, OR)
            timer_feedback -= 1

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()