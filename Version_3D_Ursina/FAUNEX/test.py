from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import time
from math import sin
from pathlib import Path
from ursina import PointLight, DirectionalLight, AmbientLight

# Configuration des chemins pour les assets
ASSETS_DIR = Path(__file__).parent / "assets_add"
ANIMALS_DIR = ASSETS_DIR / "3d" / "animals"

application.asset_folder = ASSETS_DIR

app = Ursina(title='FAUNEX', borderless=False)
# app.wireframe_on()
window.exit_button.enabled = False
window.fps_counter.enabled = True

class ParametresJeu:
    VITESSE_ANIMAL = 2
    DIST_ATTRACTION_APPAT = 20
    DIST_CONSOMMATION_APPAT = 1.5

TAILLES_ANIMAUX = {
    "Renard Roux": 1.3,
    "Ours Brun": 2.0,
    "Cerf": 0.25,
    "Fennec": 0.005,
    "Loup Gris": 1.8,
    "Sanglier": 1.0,
    "Lynx": 0.5,
    "Panthère": 1.9,
    "Aigle Royal": 0.5,
    "Faucon": 1.2,
    "Corbeau": 0.7,
    "Hibou": 0.1,
    "Pigeon": 0.6,
    "Crocodile": 0.05,
    "Vipère": 0.05,
    "Caméléon": 0.05,
    "Iguane": 0.5,
    "Scorpion": 0.05,
    "Scarabée": 0.05,
    "Mante": 0.05,
    "Papillon": 0.35,
}

MODELES_ANIMAUX = {
    "Renard Roux": "01_red_fox.glb",
    "Ours Brun": "02_brown_bear.glb",
    "Cerf": "03_deer.glb",
    "Fennec": "04_fennec.glb",
    "Loup Gris": "05_gray_wolf.glb",
    "Sanglier": "06_wild_boar.glb",
    "Lynx": "07_lynx.glb",
    "Panthère": "08_panther.glb",
    "Aigle Royal": "09_golden_eagle.glb",
    "Faucon": "10_falcon.glb",
    "Corbeau": "11_crow.glb",
    "Hibou": "12_owl.glb",
    "Pigeon": "13_pigeon.glb",
    "Crocodile": "14_crocodile.glb",
    "Vipère": "15_viper.glb",
    "Caméléon": "16_chameleon.glb",
    "Iguane": "17_iguana.glb",
    "Scorpion": "18_scorpio.glb",
    "Scarabée": "19_beetle.glb",
    "Mante": "20_mantis.glb",
    "Papillon": "21_butterfly.glb",
}

def distance_2d(a, b):
    return ((a[0] - b[0]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5

def chemin_modele_ursina(chemin: Path):
    try:
        return chemin.relative_to(ASSETS_DIR).as_posix()
    except ValueError:
        return chemin.as_posix()

def charger_modele_glb(nom_animal, chemin_complet=None):
    """Charge un modèle GLB ou OBJ+MTL"""
    if chemin_complet is None:
        if nom_animal not in MODELES_ANIMAUX:
            return None
        chemin_complet = ANIMALS_DIR / MODELES_ANIMAUX[nom_animal]
    
    if not chemin_complet.exists():
        print(f"⚠️  Modèle non trouvé: {chemin_complet}")
        return None
    
    try:
        return chemin_modele_ursina(chemin_complet)
    except Exception as e:
        print(f"❌ Erreur lors du chargement de {nom_animal}: {e}")
        return None

def charger_modele(nom_animal, chemin_complet=None):
    """
    Charge un modèle en essayant OBJ+MTL d'abord, puis GLB.
    Stratégie: pour chaque animal, cherche d'abord un fichier .obj
    avec le même nom de base que le fichier .glb configuré.
    """
    if chemin_complet is None:
        if nom_animal not in MODELES_ANIMAUX:
            return None
        chemin_base = ANIMALS_DIR / MODELES_ANIMAUX[nom_animal]
        # Essayer d'abord la version OBJ (même nom de fichier, extension .obj)
        chemin_obj = chemin_base.with_suffix('.obj')
        if chemin_obj.exists():
            chemin_complet = chemin_obj
        else:
            # Sinon, utiliser le chemin GLB d'origine
            chemin_complet = chemin_base
    
    if not chemin_complet.exists():
        print(f"⚠️  Modèle non trouvé: {chemin_complet}")
        return None
    
    try:
        chemin_relatif = chemin_modele_ursina(chemin_complet)
        
        # Vérifier que le fichier OBJ et son MTL existent ensemble
        if chemin_complet.suffix.lower() == '.obj':
            chemin_mtl = chemin_complet.with_suffix('.mtl')
            if not chemin_mtl.exists():
                print(f"⚠️  Fichier MTL manquant pour {chemin_complet}")
                # Continuer quand même, le matériau par défaut sera utilisé
            else:
                print(f"✓ Chargement OBJ+MTL: {chemin_relatif}")
        else:
            print(f"✓ Chargement GLB: {chemin_relatif}")
        
        return chemin_relatif
    except Exception as e:
        print(f"❌ Erreur lors du chargement de {nom_animal}: {e}")
        return None

class Animal(Entity):
    def __init__(self, nom, espece, valeur_couleur, position, comportement, rarete):
        taille = TAILLES_ANIMAUX.get(nom, 1.5)
        model_path = charger_modele(nom)
        
        if model_path:
            try:
                super().__init__(
                    model=model_path,
                    position=position,
                    scale=taille,
                    collider='box'
                )
                self.shader = lit_with_shadows_shader
            except Exception as e:
                print(f"⚠️  Fallback cube pour {nom}: {e}")
                super().__init__(
                    model='cube',
                    color=valeur_couleur,
                    position=position,
                    scale=taille,
                    collider='box'
                )
        else:
            super().__init__(
                model='cube',
                color=valeur_couleur,
                position=position,
                scale=taille,
                collider='box'
            )
        
        print(f"Model: {self.model}, Texture: {self.texture}")
        self.nom = nom
        self.espece = espece
        self.comportement = comportement
        self.rarete = rarete
        self.base_y = position[1]

    def mettre_a_jour_ia(self, joueur, entites):
        # Animation de vol pour les créatures en hauteur
        if self.base_y > 1.5:
            self.y = self.base_y + sin(time.time() * 2 + self.x) * 1.5

        if self.comportement == 'sommeil':
            return

        dist_vers_joueur = distance_2d(self.position, joueur.position)
        portee_detection = 15

        if self.comportement == 'fuit' and dist_vers_joueur < portee_detection:
            fuite = Vec3(self.x - joueur.x, 0, self.z - joueur.z).normalized()
            self.position += fuite * time.dt * ParametresJeu.VITESSE_ANIMAL * 3
        elif self.comportement == 'curieux' and dist_vers_joueur < 25:
            self.look_at(Vec3(joueur.x, self.y, joueur.z))

class JeuFaunex:
    def __init__(self):
        self.entites = []
        self.joueur = FirstPersonController(position=(0, 2, 0), speed=10)

        # Terrain
        self.terrain = Entity(
            model='plane',
            texture='grass',
            texture_scale=(10, 10),
            scale=300,
            collider='box',
            shader=lit_with_shadows_shader
        )
        
        Sky()
        
        # Lumières
        self.lumiere_soleil = DirectionalLight(
            shadows=True,
            rotation=(45, -45, 45),
            color=color.rgb(255, 255, 255)
        )

        self.lumiere_ambiante = AmbientLight(
            color=color.rgba(120, 120, 120, 0.4)
        )

        self.lumiere_joueur = PointLight(
            parent=self.joueur,
            y=2,
            z=0,
            color=color.rgb(255, 255, 220),
            shadows=True
        )

        # Créer les animaux
        self._creer_animaux()

    def _creer_animaux(self):
        donnees_animaux = [
            # Mammifères
            ("Renard Roux", "Mammifère", color.orange, (0, 1, 0), "fuit", 2),
            ("Ours Brun", "Mammifère", color.brown, (10, 1.5, 0), "curieux", 4),
            ("Cerf", "Mammifère", color.rgb(160, 100, 40), (20, 1.5, 0), "fuit", 2),
            ("Fennec", "Mammifère", color.yellow, (30, 1, 0), "curieux", 3),
            ("Loup Gris", "Mammifère", color.gray, (40, 1, 0), "curieux", 4),
            ("Sanglier", "Mammifère", color.rgb(100, 70, 50), (50, 1, 0), "fuit", 2),
            ("Lynx", "Mammifère", color.black, (60, 1, 0), "curieux", 5),
            ("Panthère", "Mammifère", color.white, (70, 1, 0), "fuit", 5),

            # Oiseaux
            ("Aigle Royal", "Oiseau", color.rgb(200, 150, 50), (0, 15, 0), "fuit", 4),
            ("Faucon", "Oiseau", color.dark_gray, (10, 20, 0), "fuit", 5),
            ("Corbeau", "Oiseau", color.black, (20, 12, 0), "curieux", 1),
            ("Hibou", "Oiseau", color.rgb(130, 100, 60), (30, 10, 0), "sommeil", 3),
            ("Pigeon", "Oiseau", color.light_gray, (40, 8, 0), "curieux", 1),

            # Reptiles
            ("Crocodile", "Reptile", color.rgb(50, 100, 50), (0, 0.5, 10), "sommeil", 4),
            ("Vipère", "Reptile", color.rgb(120, 150, 80), (10, 0.2, 10), "fuit", 3),
            ("Caméléon", "Reptile", color.green, (20, 0.5, 10), "sommeil", 4),
            ("Iguane", "Reptile", color.rgb(80, 180, 80), (30, 0.5, 10), "curieux", 3),

            # Insectes
            ("Scorpion", "Insecte", color.red, (0, 0.2, 20), "fuit", 3),
            ("Scarabée", "Insecte", color.rgb(20, 20, 80), (10, 0.1, 20), "fuit", 1),
            ("Mante", "Insecte", color.lime, (20, 0.5, 20), "sommeil", 3),
            ("Papillon", "Insecte", color.cyan, (30, 3, 20), "curieux", 2),
        ]
        
        for donnees in donnees_animaux:
            self.entites.append(Animal(*donnees))

    def update(self):
        for e in self.entites:
            if hasattr(e, 'mettre_a_jour_ia'):
                e.mettre_a_jour_ia(self.joueur, self.entites)

jeu = JeuFaunex()

def update():
    jeu.update()

app.run()