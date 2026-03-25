from panda3d.core import loadPrcFileData
loadPrcFileData('', '\n'.join([
    'load-display pandagl',
    'aux-display pandadx9',
    'aux-display pandadx8',
    'aux-display tinydisplay',
]))
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import time
import json
import os
import random
from math import sin
from collections import deque
from pathlib import Path
from ursina import PointLight, DirectionalLight, AmbientLight
import sys
from direct.showbase.ShowBase import ShowBase
from panda3d.core import MovieTexture, AudioSound


# ─────────────────────────────────────────
#  Chemins
# ─────────────────────────────────────────
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent

ASSETS_DIR  = BASE_DIR / "assets_add"
ANIMALS_DIR = ASSETS_DIR / "3d" / "animals"
GROUND_DIR  = ASSETS_DIR / "3d" / "ground"
FARMER_DIR  = ASSETS_DIR / "3d" / "farmer"

application.asset_folder = ASSETS_DIR

app = Ursina(title='FAUNEX', borderless=False)
window.exit_button.enabled = False
window.fps_counter.enabled = True


# ─────────────────────────────────────────
#  Classe d'intro vidéo (version corrigée)
# ─────────────────────────────────────────
# import cv2
# import numpy as np
# from panda3d.core import Texture, PNMImage

# class IntroVideo:
#     def __init__(self, video_path, on_finish_callback):
#         self.on_finish    = on_finish_callback
#         self.playing      = True
#         self.cap          = None
#         self.video_entity = None
#         self.tex          = None

#         # Fond noir
#         self.fond = Entity(
#             model='quad', color=color.black,
#             scale=(2, 2), parent=camera.ui, z=0.1
#         )

#         video_path = Path(video_path)
#         if not video_path.exists():
#             print(f"❌ Vidéo non trouvée : {video_path}")
#             self.skip()
#             return

#         self.cap = cv2.VideoCapture(str(video_path.absolute()))
#         if not self.cap.isOpened():
#             print(f"❌ OpenCV ne peut pas ouvrir : {video_path}")
#             self.skip()
#             return

#         self.fps          = self.cap.get(cv2.CAP_PROP_FPS) or 30
#         self.frame_time   = 1.0 / self.fps
#         self.last_frame_t = time.time()

#         ret, frame = self.cap.read()
#         if not ret:
#             print(f"❌ Impossible de lire la première frame")
#             self.skip()
#             return

#         h, w  = frame.shape[:2]
#         ratio = w / h
#         print(f"📹 Vidéo ouverte : {w}x{h} @ {self.fps:.1f} fps")

#         # Texture Panda3D brute
#         from panda3d.core import Texture as PandaTexture
#         self.tex = PandaTexture()
#         self.tex.setup2dTexture(w, h, PandaTexture.T_unsigned_byte, PandaTexture.F_rgb)
#         self.tex.setKeepRamImage(True)

#         # Entité quad — on applique la texture Panda3D directement
#         # via setTexture() sur le NodePath (Entity hérite de NodePath)
#         self.video_entity = Entity(
#             model='quad',
#             scale=(1.2, 1.2 / ratio),
#             parent=camera.ui,
#             z=0.2
#         )
#         self.video_entity.setTexture(self.tex, 1)

#         # Première frame
#         self._push_frame(frame)

#         # Audio séparé
#         self.sound = None
#         for ext in ('.mp3', '.wav', '.ogg'):
#             audio_path = video_path.with_suffix(ext)
#             if audio_path.exists():
#                 print(f"🔊 Audio : {audio_path.name}")
#                 try:
#                     rel = audio_path.relative_to(ASSETS_DIR).as_posix()
#                     self.sound = Audio(rel, loop=False, autoplay=True)
#                 except Exception as e:
#                     print(f"⚠️ Impossible de charger l'audio : {e}")
#                 break
#         if not self.sound:
#             print("ℹ️ Aucun fichier audio trouvé")

#         self.skip_text = Text(
#             "Cliquez pour passer",
#             parent=camera.ui, position=(0, -0.43),
#             origin=(0, 0), scale=1.1,
#             color=color.rgba(255, 255, 255, 160),
#             z=0.3
#         )

#         self.alpha     = 160
#         self.alpha_dir = 50
#         print("🎬 Intro vidéo démarrée (OpenCV)")

#     # ------------------------------------------------------------------
#     def _push_frame(self, frame):
#         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         frame_rgb = np.flipud(frame_rgb)
#         self.tex.setRamImage(frame_rgb.tobytes())

#     # ------------------------------------------------------------------
#     def update(self):
#         if not self.playing or self.cap is None:
#             return

#         # Clignotement texte
#         if hasattr(self, 'skip_text') and self.skip_text:
#             self.alpha += self.alpha_dir * time.dt * 120
#             if self.alpha >= 220:
#                 self.alpha     = 220
#                 self.alpha_dir = -50
#             elif self.alpha <= 80:
#                 self.alpha     = 80
#                 self.alpha_dir = 50
#             self.skip_text.color = color.rgba(255, 255, 255, int(self.alpha))

#         # Cadence frames
#         maintenant = time.time()
#         if maintenant - self.last_frame_t < self.frame_time:
#             return

#         self.last_frame_t = maintenant
#         ret, frame = self.cap.read()

#         if not ret:
#             print("🎬 Vidéo terminée.")
#             self.skip()
#             return

#         self._push_frame(frame)

#     # ------------------------------------------------------------------
#     def on_click(self):
#         if self.playing:
#             self.skip()

#     # ------------------------------------------------------------------
#     def skip(self):
#         if not self.playing:
#             return

#         self.playing = False
#         print("🎮 Fin de l'intro, démarrage du jeu...")

#         if self.cap:
#             self.cap.release()
#             self.cap = None

#         for ent in [self.video_entity, self.fond,
#                     getattr(self, 'skip_text', None)]:
#             if ent:
#                 try:
#                     destroy(ent)
#                 except Exception:
#                     pass

#         if self.sound:
#             try:
#                 self.sound.stop()
#                 destroy(self.sound)
#             except Exception:
#                 pass

#         if self.on_finish:
#             self.on_finish()

# ─────────────────────────────────────────
#  Palette de couleurs UI
# ─────────────────────────────────────────
class Couleurs:
    FOND            = color.rgba(12/255,  14/255,  22/255,  245/255)
    PANNEAU         = color.rgba(22/255,  27/255,  42/255,  250/255)
    LIGNE           = color.rgba(40/255,  50/255,  70/255,  255/255)
    ACCENT          = color.rgb(70, 200, 110)
    ATTENTION       = color.rgb(220, 70, 50)
    TEXTE           = color.rgb(210, 215, 225)
    TITRE           = color.rgb(255, 205, 45)
    BOUTON          = color.rgba(45/255,  58/255,  82/255,  255/255)
    BOUTON_SURVOL   = color.rgba(65/255,  85/255,  120/255, 255/255)
    BOUTON_PRESSION = color.rgba(30/255,  40/255,  58/255,  255/255)
    HUD_FOND        = color.rgba(8/255,   10/255,  18/255,  200/255)
    NOTIF_FOND      = color.rgba(0, 0, 0, 200/255)


# ─────────────────────────────────────────
#  Paramètres globaux
# ─────────────────────────────────────────
class ParametresJeu:
    VITESSE_MISE_AU_POINT   = 8
    DIST_MAX_MISE_AU_POINT  = 100
    VITESSE_ANIMAL          = 2
    DIST_ATTRACTION_APPAT   = 20
    DIST_CONSOMMATION_APPAT = 1.5
    DIST_SALUTATION_PNJ     = 5
    DUREE_NOTIFICATION      = 3.0
    ESPACEMENT_NOTIFICATION = 0.08

    # Génération aléatoire des arbres/éléments
    NB_ARBRES_GRANDS  = 60
    NB_ARBRES_PETITS  = 60
    NB_ROCHERS_GRANDS = 8
    NB_ROCHERS_PETITS = 10
    NB_BUISSONS       = 12
    RAYON_MONDE       = 120   # demi-côté de la zone de spawn (en unités)
    DIST_MIN_SPAWN    = 6     # distance minimale au joueur (origine) pour éviter les chevauchements


# ─────────────────────────────────────────
#  Tailles
# ─────────────────────────────────────────
TAILLES_ANIMAUX = {
    "Ours Brun":   2.0,
    "Loup Gris":   1.8,
    "Panthere":    1.9,
    "Lynx":        0.5,
    "Sanglier":    1.0,
    "Cerf":        0.25,
    "Renard Roux": 1.3,
    "Fennec":      0.005,
    "Aigle Royal": 0.5,
    "Faucon":      1.2,
    "Hibou":       0.1,
    "Corbeau":     0.7,
    "Pigeon":      0.6,
    "Crocodile":   0.05,
    "Iguane":      0.5,
    "Vipere":      0.05,
    "Cameleon":    0.05,
    "Scorpion":    0.05,
    "Scarabee":    0.05,
    "Mante":       0.05,
    "Papillon":    0.35,
}

TAILLES_ELEMENTS = {
    "arbre_grand":  0.05,
    "arbre_petit":  0.05,
    "rocher_grand": 0.05,
    "rocher_petit": 0.05,
    "buisson":      0.05,
}


# ─────────────────────────────────────────
#  Mappings de modèles
# ─────────────────────────────────────────
MODELES_ANIMAUX = {
    "Renard Roux": "01_red_fox.glb",
    "Ours Brun":   "02_brown_bear.glb",
    "Cerf":        "03_deer.glb",
    "Fennec":      "04_fennec.glb",
    "Loup Gris":   "05_gray_wolf.glb",
    "Sanglier":    "06_wild_boar.glb",
    "Lynx":        "07_lynx.glb",
    "Panthere":    "08_panther.glb",
    "Aigle Royal": "09_golden_eagle.glb",
    "Faucon":      "10_falcon.glb",
    "Corbeau":     "11_crow.glb",
    "Hibou":       "12_owl.glb",
    "Pigeon":      "13_pigeon.glb",
    "Crocodile":   "14_crocodile.glb",
    "Vipere":      "15_viper.glb",
    "Cameleon":    "16_chameleon.glb",
    "Iguane":      "17_iguana.glb",
    "Scorpion":    "18_scorpio.glb",
    "Scarabee":    "19_beetle.glb",
    "Mante":       "20_mantis.glb",
    "Papillon":    "21_butterfly.glb",
}

MODELES_ARBRES = {
    "arbre_grand":  "00002_tree.glb",
    "arbre_petit":  "00002_tree.glb",
    "rocher_petit": "00003_rocks.glb",
    "rocher_grand": "00004_rocks.glb",
    "buisson":      "00005_bush.glb",
}


# ─────────────────────────────────────────
#  Utilitaires
# ─────────────────────────────────────────
def distance_2d(a, b):
    return ((a[0] - b[0]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def chemin_modele_ursina(chemin: Path):
    try:
        return chemin.relative_to(ASSETS_DIR).as_posix()
    except ValueError:
        return chemin.as_posix()


def charger_modele(nom, base_dir, mapping):
    if nom not in mapping:
        return None
    chemin_base = base_dir / mapping[nom]
    chemin_obj  = chemin_base.with_suffix('.obj')
    chemin_fbx  = chemin_base.with_suffix('.fbx')

    if chemin_obj.exists():
        chemin_complet = chemin_obj
    elif chemin_fbx.exists():
        chemin_complet = chemin_fbx
    else:
        chemin_complet = chemin_base

    if not chemin_complet.exists():
        print(f"⚠️  Modèle non trouvé : {chemin_complet}")
        return None

    try:
        chemin_relatif = chemin_modele_ursina(chemin_complet)
        if chemin_complet.suffix.lower() == '.obj':
            mtl = chemin_complet.with_suffix('.mtl')
            print(f"✓ OBJ+MTL : {chemin_relatif}" if mtl.exists() else f"⚠️  MTL manquant : {chemin_complet}")
        else:
            print(f"✓ GLB : {chemin_relatif}")
        return chemin_relatif
    except Exception as e:
        print(f"❌ Erreur chargement {nom} : {e}")
        return None


def creer_bouton(texte, parent, pos, taille=(0.62, 0.09), au_clic=None,
                 couleur_fond=Couleurs.BOUTON,
                 survol=Couleurs.BOUTON_SURVOL,
                 pression=Couleurs.BOUTON_PRESSION,
                 enabled=True):
    btn = Button(
        text=texte, parent=parent, position=pos, scale=taille,
        color=couleur_fond, highlight_color=survol, pressed_color=pression,
        z=-0.1, enabled=enabled
    )
    btn.text_entity.color = color.white
    btn.text_entity.scale = (1.3 / taille[0], 1.3 / taille[1])
    if au_clic:
        btn.on_click = au_clic
    return btn


def positions_aleatoires(nb, rayon, dist_min, positions_existantes=None, seed=None):
    """
    Génère `nb` positions (x, z) aléatoires dans [-rayon, rayon]²
    en évitant l'origine (spawn joueur) et les positions déjà occupées.

    - `dist_min`          : distance minimale à l'origine
    - `positions_existantes` : liste de (x, _, z) déjà utilisées — évite les chevauchements grossiers
    - `seed`              : graine optionnelle pour reproduire la même carte
    """
    rng = random.Random(seed)
    positions = []
    tentatives_max = nb * 20  # évite une boucle infinie sur de grandes densités

    for _ in range(tentatives_max):
        if len(positions) >= nb:
            break
        x = rng.uniform(-rayon, rayon)
        z = rng.uniform(-rayon, rayon)

        # Trop proche du joueur ?
        if (x ** 2 + z ** 2) ** 0.5 < dist_min:
            continue

        # Trop proche d'une position existante ?
        trop_proche = False
        toutes = (positions_existantes or []) + [(p[0], 0, p[1]) for p in positions]
        for px, _, pz in toutes:
            if ((x - px) ** 2 + (z - pz) ** 2) ** 0.5 < 4.0:
                trop_proche = True
                break
        if trop_proche:
            continue

        positions.append((x, z))

    if len(positions) < nb:
        print(f"⚠️  Seulement {len(positions)}/{nb} positions générées (zone trop dense ?)")

    return positions


# ─────────────────────────────────────────
#  Entités du monde
# ─────────────────────────────────────────
class Animal(Entity):
    def __init__(self, nom, espece, valeur_couleur, position, comportement, rarete):
        taille     = TAILLES_ANIMAUX.get(nom, 1.5)
        model_path = charger_modele(nom, ANIMALS_DIR, MODELES_ANIMAUX)

        OFFSETS_ROTATION = {
            "Renard Roux": 0,
            "Loup Gris":   180,
            "Cerf":        0,
            "Papillon":    0,
            "Panthere":    90,
        }
        self.rotation_offset = OFFSETS_ROTATION.get(nom, 0)

        if model_path:
            try:
                super().__init__(model=model_path, position=position, scale=taille, collider='mesh')
                self.shader = lit_with_shadows_shader
            except Exception as e:
                print(f"⚠️  Fallback cube {nom} : {e}")
                super().__init__(model='cube', color=valeur_couleur, position=position,
                                 scale=taille, collider='mesh')
        else:
            super().__init__(model='cube', color=valeur_couleur, position=position,
                             scale=taille, collider='mesh')

        print(f"[Animal] {nom} — model: {self.model}, texture: {self.texture}")

        self.nom          = nom
        self.espece       = espece
        self.comportement = comportement
        self.rarete       = rarete
        self.decouvert    = False
        self.etiquette    = 'animal'
        self.base_y       = position[1]

    # appats est passé directement — plus de filtrage coûteux à chaque frame
    def mettre_a_jour_ia(self, joueur, entites, appats):
        # Animation de vol
        if self.base_y > 1.5:
            self.y = self.base_y + sin(time.time() * 2 + self.x) * 1.5

        if self.comportement == 'sommeil':
            return

        move_dir = None
        speed    = ParametresJeu.VITESSE_ANIMAL

        # Attraction vers les appâts (liste pré-filtrée)
        if appats:
            le_plus_proche  = min(appats, key=lambda b: distance_2d(self.position, b.position))
            dist_vers_appat = distance_2d(self.position, le_plus_proche.position)

            if dist_vers_appat < ParametresJeu.DIST_ATTRACTION_APPAT:
                move_dir = Vec3(
                    le_plus_proche.x - self.x, 0,
                    le_plus_proche.z - self.z
                ).normalized()

                if dist_vers_appat < ParametresJeu.DIST_CONSOMMATION_APPAT:
                    entites.remove(le_plus_proche)
                    appats.remove(le_plus_proche)  # retirer des deux listes
                    destroy(le_plus_proche)

        # Interaction joueur
        dist_vers_joueur = distance_2d(self.position, joueur.position)

        if self.comportement == 'fuit' and dist_vers_joueur < 15:
            move_dir = Vec3(self.x - joueur.x, 0, self.z - joueur.z).normalized()
            speed   *= 3
        elif self.comportement == 'curieux' and dist_vers_joueur < 25:
            self.look_at(Vec3(joueur.x, self.y, joueur.z))

        # Déplacement + orientation
        if move_dir:
            self.look_at(self.position + move_dir)
            self.rotation_y = (self.rotation_y + self.rotation_offset) % 360
            self.position  += move_dir * time.dt * speed


class Arbre(Entity):
    def __init__(self, position, type_arbre="arbre_grand"):
        taille     = TAILLES_ELEMENTS.get(type_arbre, 1.0)
        model_path = charger_modele(type_arbre, GROUND_DIR, MODELES_ARBRES) if type_arbre in MODELES_ARBRES else None

        if model_path:
            try:
                super().__init__(model=model_path, position=position, scale=taille, collider='mesh')
                self.shader = lit_with_shadows_shader
            except Exception as e:
                print(f"⚠️  Fallback arbre : {e}")
                super().__init__(model='cube', color=color.green, position=position,
                                 scale=taille, collider='mesh')
        else:
            super().__init__(model='cube', color=color.green, position=position,
                             scale=taille, collider='mesh')

        self.etiquette = 'arbre'


class Dechet(Entity):
    def __init__(self, position):
        super().__init__(model='cube', color=color.dark_gray, scale=0.5,
                         position=position, collider='mesh')
        self.etiquette = 'dechet'


class PNJ(Entity):
    def __init__(self, nom, position, valeur_couleur):
        model_path = charger_modele(nom, FARMER_DIR, {"Garde Forestier": "00_farmer.fbx"})
        if model_path:
            try:
                super().__init__(model=model_path, position=position, scale=1.5, collider='box')
                self.shader = lit_with_shadows_shader
            except Exception as e:
                print(f"⚠️  Fallback cube PNJ : {e}")
                super().__init__(model='cube', color=valeur_couleur,
                                 position=position, scale=(1, 2, 1), collider='box')
        else:
            super().__init__(model='cube', color=valeur_couleur,
                             position=position, scale=(1, 2, 1), collider='box')

        self.nom       = nom
        self.etiquette = 'pnj'
        self.a_salue   = False


class Appat(Entity):
    def __init__(self, position):
        super().__init__(model='sphere', color=color.red, scale=0.35, position=position)
        self.etiquette = 'appat'


class Empreinte(Entity):
    def __init__(self, position):
        super().__init__(
            model='quad',
            color=color.rgba(120/255, 60/255, 0, 160/255),
            position=position,
            rotation_x=90,
            scale=2.5
        )
        self.etiquette = 'empreinte'


# ─────────────────────────────────────────
#  Appareil photo
# ─────────────────────────────────────────
class AppareilPhoto:
    def __init__(self):
        self.champ_vision         = 90
        self.capacite             = 5
        self.photos_prises        = 0
        self.en_mise_au_point     = False
        self.valeur_mise_au_point = 0.0

    def zoomer(self, direction):
        self.champ_vision = max(20, min(90, self.champ_vision - direction * 10))
        camera.fov = self.champ_vision

    def demarrer_mise_au_point(self):
        self.en_mise_au_point = True

    def arreter_mise_au_point(self):
        self.en_mise_au_point = False

    def mettre_a_jour_mise_au_point(self):
        if self.en_mise_au_point:
            self.valeur_mise_au_point = (sin(time.time() * ParametresJeu.VITESSE_MISE_AU_POINT) + 1) / 2

    def prendre_photo(self, cible, etat_jeu):
        if self.photos_prises >= self.capacite:
            return False, False, 0

        score = 20 * cible.rarete
        if self.valeur_mise_au_point > 0.8:
            score += 50
        elif self.valeur_mise_au_point < 0.4:
            score -= 20
        if distance_2d(etat_jeu.joueur.position, cible.position) < 10:
            score += 30

        premiere_fois = cible.nom not in etat_jeu.encyclopedie
        if premiere_fois:
            etat_jeu.encyclopedie.append(cible.nom)
            etat_jeu.verifier_badges()
        else:
            score //= 5

        score = max(1, int(score))
        etat_jeu.credits   += score
        self.photos_prises += 1
        cible.decouvert     = True
        return True, premiere_fois, score


# ─────────────────────────────────────────
#  État du jeu & sauvegarde
# ─────────────────────────────────────────
class EtatJeu:
    def __init__(self):
        self.credits          = 50
        self.appats_restants  = 2
        self.encyclopedie     = []
        self.badges           = []
        self.dechets_ramasses = 0
        self.joueur           = None
        self.pnj_rencontre    = False
        self.appat_pnj_donne  = False   # anti-exploit : appât offert une seule fois

    def verifier_badges(self):
        if len(self.encyclopedie) >= 3 and "Photographe Debutant" not in self.badges:
            self.badges.append("Photographe Debutant")
            return "Photographe Debutant"
        if self.dechets_ramasses >= 5 and "Ami de la Nature" not in self.badges:
            self.badges.append("Ami de la Nature")
            return "Ami de la Nature"
        return None

    def sauvegarder(self, appareil_photo):
        donnees = {
            "credits":          self.credits,
            "appats_restants":  self.appats_restants,
            "encyclopedie":     self.encyclopedie,
            "badges":           self.badges,
            "dechets_ramasses": self.dechets_ramasses,
            "capacite_sd":      appareil_photo.capacite,
            "photos_sd":        appareil_photo.photos_prises,
            "pnj_rencontre":    self.pnj_rencontre,
            "appat_pnj_donne":  self.appat_pnj_donne,
        }
        with open("sauvegarde_faunex.json", "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=4)

    def charger(self, appareil_photo):
        if not os.path.exists("sauvegarde_faunex.json"):
            return
        with open("sauvegarde_faunex.json", "r", encoding="utf-8") as f:
            donnees = json.load(f)
        self.credits          = donnees.get("credits",          50)
        self.appats_restants  = donnees.get("appats_restants",  2)
        self.encyclopedie     = donnees.get("encyclopedie",     [])
        self.badges           = donnees.get("badges",           [])
        self.dechets_ramasses = donnees.get("dechets_ramasses", 0)
        self.pnj_rencontre    = donnees.get("pnj_rencontre",    False)
        self.appat_pnj_donne  = donnees.get("appat_pnj_donne",  False)
        appareil_photo.capacite      = donnees.get("capacite_sd", 5)
        appareil_photo.photos_prises = donnees.get("photos_sd",   0)


# ─────────────────────────────────────────
#  Gestionnaire de menus
# ─────────────────────────────────────────
class GestionnaireMenu:
    def __init__(self, joueur):
        self.joueur       = joueur
        self.menus_actifs = set()
        self.menus        = {}

    def enregistrer(self, nom, panneau, bloquant=True):
        self.menus[nom] = (panneau, bloquant)

    def ouvrir(self, nom):
        if nom not in self.menus:
            return
        panneau, bloquant = self.menus[nom]
        if bloquant:
            for autre in list(self.menus_actifs):
                if self.menus[autre][1]:
                    self.fermer(autre)
        panneau.enabled = True
        self.menus_actifs.add(nom)
        if bloquant:
            self.joueur.enabled = False
            mouse.locked  = False
            mouse.visible = True

    def fermer(self, nom):
        if nom not in self.menus_actifs:
            return
        panneau, bloquant = self.menus[nom]
        panneau.enabled = False
        self.menus_actifs.remove(nom)
        if not any(self.menus[m][1] for m in self.menus_actifs):
            self.joueur.enabled = True
            mouse.locked  = True
            mouse.visible = False

    def basculer(self, nom):
        if nom in self.menus_actifs:
            self.fermer(nom)
        else:
            self.ouvrir(nom)

    def fermer_tout(self):
        for nom in list(self.menus_actifs):
            self.fermer(nom)

    def est_bloque(self):
        return any(self.menus[m][1] for m in self.menus_actifs)


# ─────────────────────────────────────────
#  Notifications — dirty flag
#  Reconstruit l'UI seulement si nécessaire
# ─────────────────────────────────────────
class GestionnaireNotification:
    def __init__(self):
        self.notifications = deque()
        self.etiquettes    = []
        self.conteneur     = Entity(parent=camera.ui, position=(-0.85, -0.45), z=-0.5)
        self._dirty        = False

    def ajouter(self, texte, couleur=color.white, duree=ParametresJeu.DUREE_NOTIFICATION):
        self.notifications.append((texte, couleur, time.time() + duree))
        self._dirty = True  # marquer, ne pas reconstruire immédiatement

    def mettre_a_jour(self):
        maintenant = time.time()
        avant      = len(self.notifications)
        while self.notifications and self.notifications[0][2] <= maintenant:
            self.notifications.popleft()
        if len(self.notifications) != avant:
            self._dirty = True
        if self._dirty:
            self._rafraichir()
            self._dirty = False  # une seule reconstruction par changement

    def _rafraichir(self):
        for etiq in self.etiquettes:
            destroy(etiq)
        self.etiquettes.clear()
        decalage_y = 0.0
        for texte, couleur, _ in reversed(self.notifications):
            etiq = Text(
                texte,
                parent=self.conteneur,
                position=(0, decalage_y),
                origin=(-0.5, 0.5),
                scale=0.9,
                color=couleur,
                background=True,
                background_color=Couleurs.NOTIF_FOND
            )
            self.etiquettes.append(etiq)
            decalage_y += ParametresJeu.ESPACEMENT_NOTIFICATION


# ─────────────────────────────────────────
#  HUD
# ─────────────────────────────────────────
class AffichageTeteHaute:
    def __init__(self, etat_jeu, appareil_photo):
        self.jeu               = etat_jeu
        self.camera_equipement = appareil_photo
        self.fond = Entity(
            parent=camera.ui, model='quad', color=Couleurs.HUD_FOND,
            scale=(0.35, 0.15), position=(-0.7, 0.40), z=-0.5
        )
        self.texte = Text(
            parent=camera.ui, position=(-0.85, 0.46),
            scale=1.2, color=Couleurs.TEXTE, z=-0.6
        )

    def mettre_a_jour(self):
        self.texte.text = (
            f"Credits {self.jeu.credits} cr\n"
            f"Appats  {self.jeu.appats_restants}\n"
            f"SD      {self.camera_equipement.photos_prises}/{self.camera_equipement.capacite}"
        )


class Viseur:
    def __init__(self):
        z = -0.5
        c = color.rgba(255/255, 255/255, 255/255, 180/255)
        self.h     = Entity(parent=camera.ui, model='quad', scale=(0.028, 0.003), color=c, z=z)
        self.v     = Entity(parent=camera.ui, model='quad', scale=(0.003, 0.028), color=c, z=z)
        self.point = Entity(parent=camera.ui, model='quad', scale=0.006,
                            color=color.rgba(255/255, 255/255, 200/255, 200/255), z=z)


class BarreMiseAuPoint:
    def __init__(self):
        self.fond      = Entity(parent=camera.ui, model='quad',
                                color=color.rgba(30/255, 30/255, 30/255, 200/255),
                                scale=(0.50, 0.028), position=(0, -0.32), z=-0.5, enabled=False)
        self.barre     = Entity(parent=camera.ui, model='quad', color=color.green,
                                scale=(0.001, 0.022), position=(-0.25, -0.32), z=-0.6, enabled=False)
        self.etiquette = Text('MISE AU POINT', parent=camera.ui, position=(0, -0.28),
                              origin=(0, 0), scale=1.4, color=color.yellow, z=-0.6, enabled=False)

    def mettre_a_jour(self, valeur):
        if not self.fond.enabled:
            return
        l = max(0.001, valeur * 0.50)
        self.barre.scale_x = l
        self.barre.x       = -0.25 + l / 2
        self.barre.color   = color.green if valeur > 0.8 else color.orange

    def afficher(self):
        self.fond.enabled      = True
        self.barre.enabled     = True
        self.etiquette.enabled = True

    def cacher(self):
        self.fond.enabled      = False
        self.barre.enabled     = False
        self.etiquette.enabled = False


# ─────────────────────────────────────────
#  Menus
# ─────────────────────────────────────────
def creer_menu_pause(gest_menus, etat_jeu, appareil_photo, entites, gest_notifs):
    superposition = Entity(parent=camera.ui, model='quad',
                           color=color.rgba(0, 0, 0, 160/255),
                           scale=(3, 3), z=0.5, enabled=False)
    panneau = Entity(parent=camera.ui, model='quad', color=Couleurs.PANNEAU,
                     scale=(0.42, 0.40), z=0.4, enabled=False)
    Text("PAUSE", parent=panneau, y=0.38, origin=(0, 0), scale=4.0, color=Couleurs.TITRE, z=-0.1)

    def reprendre():
        annuler_reset()
        gest_menus.fermer('pause')
        superposition.enabled = False

    def sauvegarder_et_quitter():
        etat_jeu.sauvegarder(appareil_photo)
        application.quit()

    def demander_reset():
        btn_reprendre.enabled = False
        btn_reset.enabled     = False
        btn_quitter.enabled   = False
        texte_confirm.enabled = True
        btn_oui.enabled       = True
        btn_non.enabled       = True

    def annuler_reset():
        btn_reprendre.enabled = True
        btn_reset.enabled     = True
        btn_quitter.enabled   = True
        texte_confirm.enabled = False
        btn_oui.enabled       = False
        btn_non.enabled       = False

    def executer_reset():
        etat_jeu.credits          = 50
        etat_jeu.appats_restants  = 2
        etat_jeu.encyclopedie.clear()
        etat_jeu.badges.clear()
        etat_jeu.dechets_ramasses = 0
        etat_jeu.pnj_rencontre    = False
        etat_jeu.appat_pnj_donne  = False
        appareil_photo.capacite      = 5
        appareil_photo.photos_prises = 0
        for e in entites:
            if hasattr(e, 'decouvert'):
                e.decouvert = False
        if os.path.exists("sauvegarde_faunex.json"):
            os.remove("sauvegarde_faunex.json")
        reprendre()
        gest_notifs.ajouter("Progression reinitialisee !", color.red)

    btn_reprendre = creer_bouton("Reprendre",     panneau, (0,  0.12), (0.72, 0.15), au_clic=reprendre)
    btn_reset     = creer_bouton("Reinitialiser", panneau, (0, -0.05), (0.72, 0.15), au_clic=demander_reset)
    btn_quitter   = creer_bouton(
        "Quitter", panneau, (0, -0.22), (0.72, 0.15),
        au_clic=sauvegarder_et_quitter,
        couleur_fond=color.rgba(110/255, 30/255, 30/255, 1),
        survol=color.rgba(150/255, 40/255, 40/255, 1)
    )
    texte_confirm = Text("Tout effacer ?", parent=panneau, y=0.10, origin=(0, 0),
                         scale=2.5, color=Couleurs.ATTENTION, enabled=False, z=-0.1)
    btn_oui = creer_bouton("OUI", panneau, (-0.2, -0.10), (0.3, 0.15),
                           au_clic=executer_reset,
                           couleur_fond=color.rgba(180/255, 40/255, 40/255, 1), enabled=False)
    btn_non = creer_bouton("NON", panneau, (0.2, -0.10), (0.3, 0.15),
                           au_clic=annuler_reset, couleur_fond=Couleurs.BOUTON, enabled=False)

    gest_menus.enregistrer('pause', panneau, bloquant=True)
    return superposition


def creer_menu_dialogue(gest_menus, gest_notifs, etat_jeu, appareil_photo):
    panneau = Entity(
        parent=camera.ui, model='quad', color=Couleurs.PANNEAU,
        scale=(0.80, 0.48), position=(0, -0.28), z=0.4, enabled=False
    )
    Text("Garde Forestier", parent=panneau, position=(-0.36, 0.17),
         scale=1.8, color=Couleurs.TITRE, z=-0.1)

    # wordwrap retiré (bug Ursina) — retours à la ligne explicites dans les textes
    texte_dialogue = Text(
        "", parent=panneau,
        position=(-0.36, 0.05),
        scale=1.4, color=Couleurs.TEXTE,
        z=-0.1
    )

    def donner_appat():
        if not etat_jeu.appat_pnj_donne:
            etat_jeu.appats_restants += 1
            etat_jeu.appat_pnj_donne  = True
            gest_notifs.ajouter("Garde Forestier : +1 appat offert !", Couleurs.ACCENT)
        else:
            gest_notifs.ajouter("Je n'ai plus rien a te donner.", Couleurs.TEXTE)

    DIALOGUES = [
        {
            "texte": "Bienvenue, jeune photographe !\nLa faune ici est riche.\nQue puis-je faire pour toi ?",
            "choix": [
                ("Donne-moi un appat gratuit",   "appat"),
                ("Parle-moi de la faune locale", "info"),
                ("Au revoir",                    "quitter"),
            ]
        },
        {
            "appat": {
                "texte": "Tiens, prends ca.\nUtilise-le bien, les animaux\nmeritent le respect !",
                "effet": donner_appat,
                "suite": "fin"
            },
            "info": {
                "texte": "On recense 21 especes dans cette zone.\nLes oiseaux volent haut, leve les yeux !\nLes insectes se cachent au sud.",
                "suite": "fin"
            },
            "fin": {
                "texte": "Bonne chance !\nEt ramasse les dechets que tu croises,\nla nature te remerciera.",
                "suite": None
            }
        }
    ]

    boutons_choix  = []
    panneau._etape = "accueil"

    def afficher_etape(etape_id):
        panneau._etape = etape_id
        for btn in boutons_choix:
            destroy(btn)
        boutons_choix.clear()

        if etape_id == "accueil":
            data = DIALOGUES[0]
            texte_dialogue.text = data["texte"]
            for i, (label, cle) in enumerate(data["choix"]):
                b = creer_bouton(
                    label, panneau,
                    pos=(0.05, 0.00 - i * 0.12),
                    taille=(0.56, 0.10),
                    au_clic=lambda c=cle: reagir(c)
                )
                boutons_choix.append(b)
        else:
            reponse = DIALOGUES[1].get(etape_id)
            if not reponse:
                gest_menus.fermer('dialogue')
                return
            texte_dialogue.text = reponse["texte"]
            if "effet" in reponse:
                reponse["effet"]()
            suite     = reponse.get("suite")
            label_btn = "Continuer" if suite else "Au revoir"
            b = creer_bouton(
                label_btn, panneau,
                pos=(0.05, -0.18),
                taille=(0.38, 0.10),
                au_clic=lambda s=suite: afficher_etape(s) if s else gest_menus.fermer('dialogue')
            )
            boutons_choix.append(b)

    def reagir(cle):
        if cle == "quitter":
            gest_menus.fermer('dialogue')
        else:
            afficher_etape(cle)

    panneau.demarrer = lambda: afficher_etape("accueil")
    gest_menus.enregistrer('dialogue', panneau, bloquant=True)
    return panneau


def creer_menu_commandes(gest_menus):
    panneau = Entity(parent=camera.ui, model='quad', color=Couleurs.PANNEAU,
                     scale=(0.62, 0.85), z=0.4, enabled=False)
    Text("Commandes FAUNEX", parent=panneau, y=0.44, origin=(0, 0),
         scale=2.5, color=Couleurs.TITRE, z=-0.1)

    commandes = [
        ("TAB",                "Ouvrir/Fermer ce menu"),
        ("ESC",                "Menu Pause"),
        ("F",                  "Parler au Garde Forestier"),
        ("Clic G (maintenir)", "Cadrer une photo"),
        ("Clic G (relacher)",  "Prendre la photo"),
        ("Molette",            "Zoom optique"),
        ("P",                  "Poser un appat"),
        ("E",                  "Encyclopedie"),
        ("B",                  "Boutique"),
    ]
    for i, (touche, desc) in enumerate(commandes):
        y = 0.28 - i * 0.08
        Text(touche, parent=panneau, position=(-0.44, y), scale=1.5, color=Couleurs.ACCENT, z=-0.1)
        Text(desc,   parent=panneau, position=(-0.08, y), scale=1.5, color=color.white,    z=-0.1)

    creer_bouton("Fermer (TAB)", panneau, (0, -0.42), (0.45, 0.085),
                 au_clic=lambda: gest_menus.fermer('commandes'))
    gest_menus.enregistrer('commandes', panneau, bloquant=True)
    return panneau


def creer_menu_encyclopedie(gest_menus, etat_jeu, entites):
    panneau = Entity(parent=camera.ui, model='quad', color=Couleurs.PANNEAU,
                     scale=(0.90, 0.88), z=0.4, enabled=False)
    Text("Wiki-Dex", parent=panneau, y=0.44, origin=(0, 0),
         scale=2.5, color=Couleurs.TITRE, z=-0.1)

    texte_info    = Text("", parent=panneau, position=(-0.42, 0.35),
                         scale=1.5, color=color.white, z=-0.1)
    cartes_photos = []

    def rafraichir():
        nonlocal cartes_photos
        for e in cartes_photos:
            destroy(e)
        cartes_photos.clear()

        chaine_badges   = ", ".join(etat_jeu.badges) if etat_jeu.badges else "Aucun"
        nb_dec          = len(etat_jeu.encyclopedie)
        mot             = "animal" if nb_dec <= 1 else "animaux"
        texte_info.text = f"Badges : {chaine_badges}\nDecouvertes : {nb_dec} {mot}"

        for idx, nom in enumerate(etat_jeu.encyclopedie):
            col = color.white
            for a in entites:
                if hasattr(a, 'nom') and a.nom == nom:
                    col = a.color if hasattr(a, 'color') else color.white
                    break
            col_x = -0.34 + (idx % 4) * 0.225
            col_y =  0.10 - (idx // 4) * 0.24

            carte     = Entity(parent=panneau, model='quad',
                               color=color.rgba(200/255, 200/255, 200/255, 1),
                               scale=(0.19, 0.20), position=(col_x, col_y), z=-0.1)
            interieur = Entity(parent=carte, model='quad', color=col,
                               scale=(0.85, 0.62), position=(0, 0.10), z=-0.2)
            etiquette = Text(nom, parent=carte, scale=4.0, color=color.black,
                             position=(-0.46, -0.38), z=-0.3)
            cartes_photos.extend([carte, interieur, etiquette])

    creer_bouton("Fermer (E)", panneau, (0, -0.42), (0.38, 0.075),
                 au_clic=lambda: gest_menus.fermer('encyclo'))
    gest_menus.enregistrer('encyclo', panneau, bloquant=True)
    panneau.rafraichir = rafraichir
    return panneau


def creer_menu_boutique(gest_menus, etat_jeu, appareil_photo, gest_notifs):
    panneau = Entity(parent=camera.ui, model='quad', color=Couleurs.PANNEAU,
                     scale=(0.55, 0.52), z=0.4, enabled=False)
    Text("Boutique", parent=panneau, y=0.40, origin=(0, 0),
         scale=2.5, color=Couleurs.TITRE, z=-0.1)
    affichage_credits = Text("", parent=panneau, y=0.25, origin=(0, 0),
                             scale=1.8, color=Couleurs.ACCENT, z=-0.1)

    def mettre_a_jour_credits():
        affichage_credits.text = f"Credits : {etat_jeu.credits} cr"

    def acheter(objet, cout, action):
        if etat_jeu.credits >= cout:
            etat_jeu.credits -= cout
            action()
            mettre_a_jour_credits()
            gest_notifs.ajouter(f"Achat : {objet} !", Couleurs.ACCENT)
        else:
            gest_notifs.ajouter(
                f"Pas assez de credits ! (manque {cout - etat_jeu.credits} cr)",
                Couleurs.ATTENTION
            )

    objets = [
        ("Carte SD (+5 photos)", 50,
         lambda: setattr(appareil_photo, 'capacite', appareil_photo.capacite + 5)),
        ("Appat x1", 20,
         lambda: setattr(etat_jeu, 'appats_restants', etat_jeu.appats_restants + 1)),
    ]
    for i, (etiq, cout, action) in enumerate(objets):
        y = 0.05 - i * 0.18
        creer_bouton(f"{etiq} - {cout} cr", panneau, (0, y), (0.85, 0.15),
                     au_clic=lambda l=etiq, c=cout, a=action: acheter(l, c, a))

    creer_bouton("Fermer (B)", panneau, (0, -0.38), (0.38, 0.09),
                 au_clic=lambda: gest_menus.fermer('shop'))
    gest_menus.enregistrer('shop', panneau, bloquant=True)
    panneau.mettre_a_jour_credits = mettre_a_jour_credits
    return panneau


def creer_menu_quiz(gest_menus, gest_notifs, etat_jeu):
    panneau = Entity(parent=camera.ui, model='quad', color=Couleurs.PANNEAU,
                     scale=(0.52, 0.55), z=0.4, enabled=False)
    Text("Quiz Naturel", parent=panneau, y=0.40, origin=(0, 0),
         scale=2.5, color=Couleurs.TITRE, z=-0.1)
    question = Text("", parent=panneau, y=0.25, origin=(0, 0),
                    scale=1.5, color=color.white, z=-0.1)
    panneau.reponse_attendue = ""

    def repondre(rep):
        if rep == panneau.reponse_attendue:
            etat_jeu.credits += 15
            gest_notifs.ajouter("Bonne reponse ! +15 cr", Couleurs.ACCENT)
        else:
            gest_notifs.ajouter(
                f"Erreur ! C'etait un(e) {panneau.reponse_attendue}.",
                Couleurs.ATTENTION
            )
        gest_menus.fermer('quiz')

    for i, rep in enumerate(["Mammifere", "Reptile", "Insecte", "Oiseau"]):
        creer_bouton(rep, panneau, (0, 0.05 - i * 0.13), (0.65, 0.11),
                     au_clic=lambda r=rep: repondre(r))

    gest_menus.enregistrer('quiz', panneau, bloquant=True)
    panneau.question = question
    return panneau


# ─────────────────────────────────────────
#  Jeu principal
# ─────────────────────────────────────────
class JeuFaunex:
    def __init__(self):
        # Variable pour l'intro
        self.intro = None
        self.jeu_initialise = False
        
        # Charger et démarrer l'intro
        self.demarrer_jeu()
    
    # def demarrer_intro(self):
    #     """Démarre l'intro vidéo"""
    #     # Chemin vers la vidéo d'intro (à placer dans assets_add/video/)
    #     video_path = ASSETS_DIR / "logo" / "intro.avi"
        
    #     # Vérifier si la vidéo existe
    #     if video_path.exists():
    #         print(f"🎬 Chargement de l'intro : {video_path}")
    #         self.intro = IntroVideo(video_path, self.demarrer_jeu)
    #     else:
    #         print(f"⚠️ Vidéo d'intro non trouvée : {video_path}")
    #         print("   Placez votre fichier intro.mp4 dans assets_add/video/")
    #         self.demarrer_jeu()
    
    def demarrer_jeu(self):
        """Initialise le jeu après l'intro"""
        if self.jeu_initialise:
            return
        
        self.jeu_initialise = True
        print("🎮 Démarrage du jeu...")
        
        self.etat_jeu        = EtatJeu()
        self.appareil_photo  = AppareilPhoto()
        self.entites         = []
        self.appats          = []   # liste dédiée appâts — évite le filtrage à chaque frame
        self.temps_derniere_sauvegarde = time.time()
        self._temps_derniere_notif_pnj = 0.0

        self.joueur          = FirstPersonController(position=(0, 2, 0), speed=10)
        self.etat_jeu.joueur = self.joueur

        # Terrain
        self.terrain = Entity(
            model='plane',
            texture='grass',
            texture_scale=(100, 100),
            scale=300,
            collider='box',
            shader=lit_with_shadows_shader
        )
        Sky()

        # Éclairage — shadows=False sur le PointLight pour économiser du GPU
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
            y=2, z=0,
            color=color.rgb(255, 255, 220),
            shadows=False   # ← désactivé pour les performances
        )

        self.etat_jeu.charger(self.appareil_photo)
        self._creer_entites_monde()

        self.gest_notifs = GestionnaireNotification()
        self.gest_menus  = GestionnaireMenu(self.joueur)
        self.ath         = AffichageTeteHaute(self.etat_jeu, self.appareil_photo)
        self.viseur      = Viseur()
        self.barre_focus = BarreMiseAuPoint()

        self.pause_overlay = creer_menu_pause(
            self.gest_menus, self.etat_jeu, self.appareil_photo, self.entites, self.gest_notifs
        )
        creer_menu_commandes(self.gest_menus)
        self.dialogue_menu = creer_menu_dialogue(
            self.gest_menus, self.gest_notifs, self.etat_jeu, self.appareil_photo
        )
        self.encyclo_menu = creer_menu_encyclopedie(self.gest_menus, self.etat_jeu, self.entites)
        self.shop_menu    = creer_menu_boutique(
            self.gest_menus, self.etat_jeu, self.appareil_photo, self.gest_notifs
        )
        self.quiz_menu = creer_menu_quiz(self.gest_menus, self.gest_notifs, self.etat_jeu)

        self.gest_menus.ouvrir('commandes')
    
    # ------------------------------------------------------------------
    def _creer_entites_monde(self):
        donnees_animaux = [
            # Mammifères
            ("Renard Roux", "Mammifere", color.orange,            ( 0, 1.0,  0), "fuit",    2),
            ("Ours Brun",   "Mammifere", color.brown,             (10, 1.5,  0), "fuit", 4),
            ("Cerf",        "Mammifere", color.rgb(160, 100, 40), (20, 1.5,  0), "fuit",    2),
            ("Fennec",      "Mammifere", color.yellow,            (30, 1.0,  0), "fuit", 3),
            ("Loup Gris",   "Mammifere", color.gray,              (40, 1.0,  0), "fuit", 4),
            ("Sanglier",    "Mammifere", color.rgb(100, 70,  50), (50, 1.0,  0), "fuit",    2),
            ("Lynx",        "Mammifere", color.black,             (60, 1.0,  0), "fuit", 5),
            ("Panthere",    "Mammifere", color.white,             (70, 1.0,  0), "fuit",    5),
            # Oiseaux
            ("Aigle Royal", "Oiseau",    color.rgb(200, 150, 50), ( 0,15.0,  0), "fuit",    4),
            ("Faucon",      "Oiseau",    color.dark_gray,         (10,20.0,  0), "fuit",    5),
            ("Corbeau",     "Oiseau",    color.black,             (20,12.0,  0), "fuit", 1),
            ("Hibou",       "Oiseau",    color.rgb(130, 100, 60), (30,10.0,  0), "sommeil", 3),
            ("Pigeon",      "Oiseau",    color.light_gray,        (40, 8.0,  0), "fuit", 1),
            # Reptiles
            ("Crocodile",   "Reptile",   color.rgb( 50, 100, 50), ( 0, 0.5, 10), "sommeil", 4),
            ("Vipere",      "Reptile",   color.rgb(120, 150, 80), (10, 0.2, 10), "fuit",    3),
            ("Cameleon",    "Reptile",   color.green,             (20, 0.5, 10), "sommeil", 4),
            ("Iguane",      "Reptile",   color.rgb( 80, 180, 80), (30, 0.5, 10), "fuit", 3),
            # Insectes
            ("Scorpion",    "Insecte",   color.red,               ( 0, 0.2, 20), "fuit",    3),
            ("Scarabee",    "Insecte",   color.rgb( 20,  20, 80), (10, 0.1, 20), "fuit",    1),
            ("Mante",       "Insecte",   color.lime,              (20, 0.5, 20), "sommeil", 3),
            ("Papillon",    "Insecte",   color.cyan,              (30, 3.0, 20), "fuit", 2),
        ]
        for d in donnees_animaux:
            self.entites.append(Animal(*d))

        for pos in [(5, 0.5, 5), (-15, 0.5, 20), (60, 0.5, 5)]:
            self.entites.append(Dechet(pos))

        # ── Génération aléatoire des éléments du monde ──────────────────
        # On récupère les positions des entités déjà placées pour éviter
        # les chevauchements grossiers avec les animaux et les déchets.
        positions_occupees = [
            (e.x, e.y, e.z) for e in self.entites if hasattr(e, 'x')
        ]

        # Catalogue : (type_arbre, nb_instances, graine_rng)
        catalogue_elements = [
            ("arbre_grand",  ParametresJeu.NB_ARBRES_GRANDS,  0),
            ("arbre_petit",  ParametresJeu.NB_ARBRES_PETITS,  1),
        ]

        for type_elem, nb, seed_offset in catalogue_elements:
            positions = positions_aleatoires(
                nb=nb,
                rayon=ParametresJeu.RAYON_MONDE,
                dist_min=ParametresJeu.DIST_MIN_SPAWN,
                positions_existantes=positions_occupees,
                seed=42 + seed_offset,  # graine fixe → carte reproductible ;
                                        # retirez `seed=` pour une carte différente à chaque lancement
            )
            for x, z in positions:
                arbre = Arbre((x, 0, z), type_elem)
                self.entites.append(arbre)
                positions_occupees.append((x, 0, z))

        self.pnj = PNJ("Garde Forestier", (0, 1, 10), color.green)
        self.entites.append(self.pnj)
        self.entites.append(Empreinte((5, 0.1, 10)))

    # ------------------------------------------------------------------
    def verifier_salutation_pnj(self):
        # Court-circuit immédiat si un menu est ouvert
        if self.gest_menus.est_bloque():
            return
        dist = distance_2d(self.joueur.position, self.pnj.position)
        if dist >= 8:
            return
        maintenant = time.time()
        # Afficher le hint au maximum toutes les 2 secondes
        if maintenant - self._temps_derniere_notif_pnj > 2.0:
            self._temps_derniere_notif_pnj = maintenant
            self.gest_notifs.ajouter("[F] Parler au Garde Forestier", Couleurs.TEXTE, 1.8)

    # ------------------------------------------------------------------
    def update(self):
        # Si le jeu n'est pas initialisé, on met juste à jour l'intro
        if not self.jeu_initialise:
            if self.intro:
                self.intro.update()
            return
        
        self.gest_notifs.mettre_a_jour()

        # Autosauvegarde toutes les 10 s
        if time.time() - self.temps_derniere_sauvegarde >= 10:
            self.etat_jeu.sauvegarder(self.appareil_photo)
            self.temps_derniere_sauvegarde = time.time()
            self.gest_notifs.ajouter("Autosauvegarde...", color.gray, 1.5)

        menu_ouvert = self.gest_menus.est_bloque()
        self.viseur.h.enabled     = not menu_ouvert
        self.viseur.v.enabled     = not menu_ouvert
        self.viseur.point.enabled = not menu_ouvert

        self.ath.mettre_a_jour()
        self.appareil_photo.mettre_a_jour_mise_au_point()
        if self.appareil_photo.en_mise_au_point:
            self.barre_focus.mettre_a_jour(self.appareil_photo.valeur_mise_au_point)

        if not menu_ouvert:
            # self.appats passé directement — plus de list comprehension × 21 animaux
            for e in self.entites:
                if hasattr(e, 'mettre_a_jour_ia'):
                    e.mettre_a_jour_ia(self.joueur, self.entites, self.appats)

        self.verifier_salutation_pnj()

    # ------------------------------------------------------------------
    def input(self, key):
        # Si le jeu n'est pas initialisé, on gère les entrées pour l'intro
        if not self.jeu_initialise:
            if self.intro:
                self.intro.on_click()
            return
        
        if key == 'escape':
            if self.gest_menus.menus_actifs:
                self.gest_menus.fermer_tout()
                self.pause_overlay.enabled = False
            else:
                self.pause_overlay.enabled = True
                self.gest_menus.ouvrir('pause')
            return

        touches_menus = {'tab': 'commandes', 'e': 'encyclo', 'b': 'shop'}
        if key in touches_menus:
            self.gest_menus.basculer(touches_menus[key])
            if touches_menus[key] == 'encyclo' and self.encyclo_menu.enabled:
                self.encyclo_menu.rafraichir()
            if touches_menus[key] == 'shop' and self.shop_menu.enabled:
                self.shop_menu.mettre_a_jour_credits()
            return

        if self.gest_menus.est_bloque():
            return

        # ── Zoom ──
        if key == 'scroll up':
            self.appareil_photo.zoomer(1)
        elif key == 'scroll down':
            self.appareil_photo.zoomer(-1)

        # ── Appât ──
        elif key == 'p':
            if self.etat_jeu.appats_restants > 0:
                self.etat_jeu.appats_restants -= 1
                pos          = self.joueur.position + self.joueur.forward * 2
                nouvel_appat = Appat(pos)
                self.entites.append(nouvel_appat)
                self.appats.append(nouvel_appat)   # ← maintenu dans les deux listes
                self.gest_notifs.ajouter(
                    f"Appat pose ! ({self.etat_jeu.appats_restants} restant(s))"
                )
            else:
                self.gest_notifs.ajouter("Plus d'appats !", Couleurs.ATTENTION)

        # ── Dialogue PNJ ──
        elif key == 'f':
            dist = distance_2d(self.joueur.position, self.pnj.position)
            if dist < ParametresJeu.DIST_SALUTATION_PNJ:
                self.etat_jeu.pnj_rencontre = True
                self.dialogue_menu.demarrer()
                self.gest_menus.ouvrir('dialogue')
            else:
                self.gest_notifs.ajouter(
                    "Approche-toi du Garde Forestier pour lui parler.",
                    Couleurs.TEXTE
                )

        # ── Photo — début cadrage ──
        elif key == 'left mouse down':
            touche_ray = raycast(
                camera.world_position, camera.forward,
                distance=ParametresJeu.DIST_MAX_MISE_AU_POINT,
                ignore=[self.joueur]
            )
            if touche_ray.hit and hasattr(touche_ray.entity, 'etiquette'):
                if touche_ray.entity.etiquette == 'animal':
                    self.appareil_photo.demarrer_mise_au_point()
                    self.barre_focus.afficher()
                elif touche_ray.entity.etiquette == 'dechet':
                    entite = touche_ray.entity
                    if entite in self.entites:
                        self.entites.remove(entite)
                    destroy(entite)
                    self.etat_jeu.credits         += 10
                    self.etat_jeu.dechets_ramasses += 1
                    badge = self.etat_jeu.verifier_badges()
                    if badge:
                        self.gest_notifs.ajouter(f"Badge debloque : {badge} !", Couleurs.TITRE)
                    self.gest_notifs.ajouter("Dechet ramasse ! +10 cr", Couleurs.ACCENT)

        # ── Photo — prise ──
        elif key == 'left mouse up':
            if self.appareil_photo.en_mise_au_point:
                self.appareil_photo.arreter_mise_au_point()
                self.barre_focus.cacher()
                touche_ray = raycast(
                    camera.world_position, camera.forward,
                    distance=ParametresJeu.DIST_MAX_MISE_AU_POINT,
                    ignore=[self.joueur]
                )
                if (touche_ray.hit
                        and hasattr(touche_ray.entity, 'etiquette')
                        and touche_ray.entity.etiquette == 'animal'):
                    succes, premiere_fois, score = self.appareil_photo.prendre_photo(
                        touche_ray.entity, self.etat_jeu
                    )
                    if not succes:
                        self.gest_notifs.ajouter(
                            "Carte SD pleine ! Achete une extension.", Couleurs.ATTENTION
                        )
                    elif premiere_fois:
                        self.gest_notifs.ajouter(
                            f"NOUVEAU ! {touche_ray.entity.nom} +{score} cr", Couleurs.ACCENT
                        )
                        self.quiz_menu.question.text    = f"Type de {touche_ray.entity.nom} ?"
                        self.quiz_menu.reponse_attendue = touche_ray.entity.espece
                        self.gest_menus.ouvrir('quiz')
                    else:
                        self.gest_notifs.ajouter(
                            f"{touche_ray.entity.nom} deja vu ! +{score} cr", Couleurs.TEXTE
                        )


# ─────────────────────────────────────────
#  Lancement
# ─────────────────────────────────────────
jeu = JeuFaunex()

def update():
    jeu.update()

def input(key):
    jeu.input(key)

app.run()