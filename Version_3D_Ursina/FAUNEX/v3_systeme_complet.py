from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import time
import json
import os
from math import sin

app = Ursina(title='FAUNEX', borderless=True, fullscreen=True)
window.exit_button.enabled = False
window.fps_counter.enabled = False
window.entity_counter.enabled = False
window.collider_counter.enabled = False

FOND = color.rgba(12/255, 14/255, 22/255, 245/255)
PANNEAU = color.rgba(22/255, 27/255, 42/255, 250/255)
LIGNE = color.rgba(40/255, 50/255, 70/255, 255/255)
ACCENT = color.rgb(70, 200, 110)
ATTENTION = color.rgb(220, 70, 50)
TEXTE = color.rgb(210, 215, 225)
TITRE = color.rgb(255, 205, 45)
BOUTON = color.rgba(45/255, 58/255, 82/255, 255/255)
BOUTON_SURVOL = color.rgba(65/255, 85/255, 120/255, 255/255)
BOUTON_PRESSION = color.rgba(30/255, 40/255, 58/255, 255/255)
HUD_FOND = color.rgba(8/255, 10/255, 18/255, 200/255)
NOTIF_FOND = color.rgba(0, 0, 0, 200/255)

VITESSE_MISE_AU_POINT = 8
DIST_MAX_MISE_AU_POINT = 100
VITESSE_ANIMAL = 2
DIST_ATTRACTION_APPAT = 20
DIST_CONSOMMATION_APPAT = 1.5
DIST_SALUTATION_PNJ = 5
DUREE_NOTIFICATION = 3.0
ESPACEMENT_NOTIFICATION = 0.08

def distance_2d(a, b):
    return ((a[0] - b[0]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5

def creer_bouton(texte, parent, pos, taille=(0.62, 0.09), au_clic=None, couleur_fond=BOUTON, survol=BOUTON_SURVOL, pression=BOUTON_PRESSION, enabled=True):
    btn = Button(text=texte, parent=parent, position=pos, scale=taille, color=couleur_fond, highlight_color=survol, pressed_color=pression, z=-0.1, enabled=enabled)
    btn.text_entity.color = color.white
    btn.text_entity.scale = (1.3 / taille[0], 1.3 / taille[1])
    if au_clic != None:
        btn.on_click = au_clic
    return btn

class Animal(Entity):
    def __init__(self, nom, espece, valeur_couleur, position, comportement, rarete):
        taille = 1.5
        if espece == "Insecte":
            taille = 0.4
        if espece == "Oiseau":
            taille = 0.8
        
        super().__init__(model='cube', color=valeur_couleur, position=position, scale=taille, collider='box')
        self.nom = nom
        self.espece = espece
        self.comportement = comportement
        self.rarete = rarete
        self.decouvert = False
        self.etiquette = 'animal'
        self.base_y = position[1]

    def mettre_a_jour_ia(self, joueur, entites):
        if self.base_y > 1.5:
            self.y = self.base_y + sin(time.time() * 2 + self.x) * 1.5

        if self.comportement == 'sommeil':
            return

        appats = []
        for e in entites:
            if hasattr(e, 'etiquette'):
                if e.etiquette == 'appat':
                    appats.append(e)

        if len(appats) > 0:
            le_plus_proche = appats[0]
            dist_min = distance_2d(self.position, le_plus_proche.position)
            for b in appats:
                d = distance_2d(self.position, b.position)
                if d < dist_min:
                    dist_min = d
                    le_plus_proche = b

            dist_vers_appat = dist_min
            if dist_vers_appat < DIST_ATTRACTION_APPAT:
                direction = Vec3(le_plus_proche.x - self.x, 0, le_plus_proche.z - self.z).normalized()
                self.position += direction * time.dt * VITESSE_ANIMAL
                if dist_vers_appat < DIST_CONSOMMATION_APPAT:
                    entites.remove(le_plus_proche)
                    destroy(le_plus_proche)
                return

        dist_vers_joueur = distance_2d(self.position, joueur.position)
        portee_detection = 15

        if self.comportement == 'fuit':
            if dist_vers_joueur < portee_detection:
                fuite = Vec3(self.x - joueur.x, 0, self.z - joueur.z).normalized()
                self.position += fuite * time.dt * VITESSE_ANIMAL * 3
        
        if self.comportement == 'curieux':
            if dist_vers_joueur < 25:
                self.look_at(Vec3(joueur.x, self.y, joueur.z))

class Dechet(Entity):
    def __init__(self, position):
        super().__init__(model='cube', color=color.dark_gray, scale=0.5, position=position, collider='box')
        self.etiquette = 'dechet'

class PNJ(Entity):
    def __init__(self, nom, position, valeur_couleur):
        super().__init__(model='cube', color=valeur_couleur, position=position, scale=(1, 2, 1), collider='box')
        self.nom = nom
        self.etiquette = 'pnj'
        self.a_salue = False

class Appat(Entity):
    def __init__(self, position):
        super().__init__(model='sphere', color=color.red, scale=0.35, position=position)
        self.etiquette = 'appat'

class Empreinte(Entity):
    def __init__(self, position):
        super().__init__(model='quad', color=color.rgba(120/255, 60/255, 0, 160/255), position=position, rotation_x=90, scale=2.5)
        self.etiquette = 'empreinte'

class AppareilPhoto:
    def __init__(self):
        self.champ_vision = 90
        self.capacite = 5
        self.photos_prises = 0
        self.en_mise_au_point = False
        self.valeur_mise_au_point = 0.0

    def zoomer(self, direction):
        nouveau_zoom = self.champ_vision - direction * 10
        if nouveau_zoom < 20:
            nouveau_zoom = 20
        if nouveau_zoom > 90:
            nouveau_zoom = 90
        self.champ_vision = nouveau_zoom
        camera.fov = self.champ_vision

    def demarrer_mise_au_point(self):
        self.en_mise_au_point = True

    def arreter_mise_au_point(self):
        self.en_mise_au_point = False

    def mettre_a_jour_mise_au_point(self):
        if self.en_mise_au_point:
            self.valeur_mise_au_point = (sin(time.time() * VITESSE_MISE_AU_POINT) + 1) / 2

    def prendre_photo(self, cible, etat_jeu):
        if self.photos_prises >= self.capacite:
            return False, False, 0

        score = 20 * cible.rarete

        if self.valeur_mise_au_point > 0.8:
            score += 50
        if self.valeur_mise_au_point < 0.4:
            score -= 20

        dist = distance_2d(etat_jeu.joueur.position, cible.position)
        if dist < 10:
            score += 30

        premiere_fois = True
        for nom in etat_jeu.encyclopedie:
            if nom == cible.nom:
                premiere_fois = False

        if premiere_fois:
            etat_jeu.encyclopedie.append(cible.nom)
            etat_jeu.verifier_badges()
        else:
            score = score // 5

        if score < 1:
            score = 1
        else:
            score = int(score)

        etat_jeu.credits += score
        self.photos_prises += 1
        cible.decouvert = True

        return True, premiere_fois, score

class EtatJeu:
    def __init__(self):
        self.credits = 50
        self.appats_restants = 2
        self.encyclopedie = []
        self.badges = []
        self.dechets_ramasses = 0
        self.joueur = None
        self.pnj_rencontre = False

    def verifier_badges(self):
        if len(self.encyclopedie) >= 3:
            if "Photographe Débutant" not in self.badges:
                self.badges.append("Photographe Débutant")
                return "Photographe Débutant"
        if self.dechets_ramasses >= 5:
            if "Ami de la Nature" not in self.badges:
                self.badges.append("Ami de la Nature")
                return "Ami de la Nature"
        return None

    def sauvegarder(self, appareil_photo):
        donnees = {
            "credits": self.credits,
            "appats_restants": self.appats_restants,
            "encyclopedie": self.encyclopedie,
            "badges": self.badges,
            "dechets_ramasses": self.dechets_ramasses,
            "capacite_sd": appareil_photo.capacite,
            "photos_sd": appareil_photo.photos_prises,
            "pnj_rencontre": self.pnj_rencontre
        }
        with open("sauvegarde_faunex.json", "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=4)

    def charger(self, appareil_photo):
        if os.path.exists("sauvegarde_faunex.json") == False:
            return
        with open("sauvegarde_faunex.json", "r", encoding="utf-8") as f:
            donnees = json.load(f)
            
        if "credits" in donnees:
            self.credits = donnees["credits"]
        else:
            self.credits = 50
            
        if "appats_restants" in donnees:
            self.appats_restants = donnees["appats_restants"]
        else:
            self.appats_restants = 2
            
        if "encyclopedie" in donnees:
            self.encyclopedie = donnees["encyclopedie"]
        else:
            self.encyclopedie = []
            
        if "badges" in donnees:
            self.badges = donnees["badges"]
        else:
            self.badges = []
            
        if "dechets_ramasses" in donnees:
            self.dechets_ramasses = donnees["dechets_ramasses"]
        else:
            self.dechets_ramasses = 0
            
        if "capacite_sd" in donnees:
            appareil_photo.capacite = donnees["capacite_sd"]
        else:
            appareil_photo.capacite = 5
            
        if "photos_sd" in donnees:
            appareil_photo.photos_prises = donnees["photos_sd"]
        else:
            appareil_photo.photos_prises = 0
            
        if "pnj_rencontre" in donnees:
            self.pnj_rencontre = donnees["pnj_rencontre"]
        else:
            self.pnj_rencontre = False

class GestionnaireMenu:
    def __init__(self, joueur):
        self.joueur = joueur
        self.menus_actifs = []
        self.menus = {}

    def enregistrer(self, nom, panneau, bloquant=True):
        self.menus[nom] = (panneau, bloquant)

    def ouvrir(self, nom):
        if nom not in self.menus:
            return
        
        panneau = self.menus[nom][0]
        bloquant = self.menus[nom][1]
        
        if bloquant:
            copie_actifs = list(self.menus_actifs)
            for autre in copie_actifs:
                if self.menus[autre][1] == True:
                    self.fermer(autre)
                    
        panneau.enabled = True
        if nom not in self.menus_actifs:
            self.menus_actifs.append(nom)
            
        if bloquant:
            self.joueur.enabled = False
            mouse.locked = False
            mouse.visible = True

    def fermer(self, nom):
        if nom not in self.menus_actifs:
            return
            
        panneau = self.menus[nom][0]
        panneau.enabled = False
        self.menus_actifs.remove(nom)
        
        if self.est_bloque() == False:
            self.joueur.enabled = True
            mouse.locked = True
            mouse.visible = False

    def basculer(self, nom):
        if nom in self.menus_actifs:
            self.fermer(nom)
        else:
            self.ouvrir(nom)

    def fermer_tout(self):
        copie_actifs = list(self.menus_actifs)
        for nom in copie_actifs:
            self.fermer(nom)

    def est_bloque(self):
        for m in self.menus_actifs:
            if self.menus[m][1] == True:
                return True
        return False

class GestionnaireNotification:
    def __init__(self):
        self.notifications = []
        self.etiquettes = []
        self.conteneur = Entity(parent=camera.ui, position=(-0.85, -0.45), z=-0.5)

    def ajouter(self, texte, couleur=color.white, duree=DUREE_NOTIFICATION):
        temps_fin = time.time() + duree
        self.notifications.append((texte, couleur, temps_fin))
        self._rafraichir()

    def mettre_a_jour(self):
        maintenant = time.time()
        change = False
        while len(self.notifications) > 0:
            if self.notifications[0][2] <= maintenant:
                self.notifications.pop(0)
                change = True
            else:
                break
        if change:
            self._rafraichir()

    def _rafraichir(self):
        for etiq in self.etiquettes:
            destroy(etiq)
        self.etiquettes.clear()

        decalage_y = 0.0
        index = len(self.notifications) - 1
        while index >= 0:
            texte = self.notifications[index][0]
            couleur = self.notifications[index][1]
            etiq = Text(texte, parent=self.conteneur, position=(0, decalage_y), origin=(-0.5, 0.5), scale=0.9, color=couleur, background=True, background_color=NOTIF_FOND)
            self.etiquettes.append(etiq)
            decalage_y += ESPACEMENT_NOTIFICATION
            index -= 1

class AffichageTeteHaute:
    def __init__(self, etat_jeu, appareil_photo):
        self.jeu = etat_jeu
        self.camera_equipement = appareil_photo
        self.fond = Entity(parent=camera.ui, model='quad', color=HUD_FOND, scale=(0.35, 0.15), position=(-0.7, 0.40), z=-0.5)
        self.texte = Text(parent=camera.ui, position=(-0.85, 0.46), scale=1.2, color=TEXTE, z=-0.6)

    def mettre_a_jour(self):
        self.texte.text = f"Crédits {self.jeu.credits} cr\nAppâts  {self.jeu.appats_restants}\nSD      {self.camera_equipement.photos_prises}/{self.camera_equipement.capacite}"

class Viseur:
    def __init__(self):
        z = -0.5
        self.h = Entity(parent=camera.ui, model='quad', scale=(0.028, 0.003), color=color.rgba(255/255,255/255,255/255,180/255), z=z)
        self.v = Entity(parent=camera.ui, model='quad', scale=(0.003, 0.028), color=color.rgba(255/255,255/255,255/255,180/255), z=z)
        self.point = Entity(parent=camera.ui, model='quad', scale=0.006, color=color.rgba(255/255,255/255,200/255,200/255), z=z)

class BarreMiseAuPoint:
    def __init__(self):
        self.fond = Entity(parent=camera.ui, model='quad', color=color.rgba(30/255,30/255,30/255,200/255), scale=(0.50, 0.028), position=(0, -0.32), z=-0.5, enabled=False)
        self.barre = Entity(parent=camera.ui, model='quad', color=color.green, scale=(0.001, 0.022), position=(-0.25, -0.32), z=-0.6, enabled=False)
        self.etiquette = Text('MISE AU POINT', parent=camera.ui, position=(0, -0.28), origin=(0,0), scale=1.4, color=color.yellow, z=-0.6, enabled=False)

    def mettre_a_jour(self, valeur_mise_au_point):
        if self.fond.enabled == False:
            return
        
        l = valeur_mise_au_point * 0.50
        if l < 0.001:
            l = 0.001
            
        self.barre.scale_x = l
        self.barre.x = -0.25 + l / 2
        
        if valeur_mise_au_point > 0.8:
            self.barre.color = color.green
        else:
            self.barre.color = color.orange

    def afficher(self):
        self.fond.enabled = True
        self.barre.enabled = True
        self.etiquette.enabled = True

    def cacher(self):
        self.fond.enabled = False
        self.barre.enabled = False
        self.etiquette.enabled = False

def creer_menu_pause(gest_menus, etat_jeu, appareil_photo, entites, gest_notifs):
    superposition = Entity(parent=camera.ui, model='quad', color=color.rgba(0,0,0,160/255), scale=(3,3), z=0.5, enabled=False)
    panneau = Entity(parent=camera.ui, model='quad', color=PANNEAU, scale=(0.42, 0.40), z=0.4, enabled=False)
    Text("PAUSE", parent=panneau, y=0.38, origin=(0,0), scale=4.0, color=TITRE, z=-0.1)

    def reprendre():
        annuler_reset()
        gest_menus.fermer('pause')
        superposition.enabled = False

    def sauvegarder_et_quitter():
        etat_jeu.sauvegarder(appareil_photo)
        application.quit()

    def demander_reset():
        btn_reprendre.enabled = False
        btn_reset.enabled = False
        btn_quitter.enabled = False
        texte_confirm.enabled = True
        btn_oui.enabled = True
        btn_non.enabled = True

    def annuler_reset():
        btn_reprendre.enabled = True
        btn_reset.enabled = True
        btn_quitter.enabled = True
        texte_confirm.enabled = False
        btn_oui.enabled = False
        btn_non.enabled = False

    def executer_reset():
        etat_jeu.credits = 50
        etat_jeu.appats_restants = 2
        etat_jeu.encyclopedie.clear()
        etat_jeu.badges.clear()
        etat_jeu.dechets_ramasses = 0
        etat_jeu.pnj_rencontre = False
        appareil_photo.capacite = 5
        appareil_photo.photos_prises = 0
        
        for e in entites:
            if hasattr(e, 'decouvert'):
                e.decouvert = False
        
        if os.path.exists("sauvegarde_faunex.json"):
            os.remove("sauvegarde_faunex.json")
        
        reprendre()
        gest_notifs.ajouter("Progression réinitialisée !", color.red)

    btn_reprendre = creer_bouton("Reprendre", panneau, (0, 0.12), (0.72, 0.15), au_clic=reprendre)
    btn_reset = creer_bouton("Réinitialiser", panneau, (0, -0.05), (0.72, 0.15), au_clic=demander_reset)
    btn_quitter = creer_bouton("Quitter", panneau, (0, -0.22), (0.72, 0.15), au_clic=sauvegarder_et_quitter, couleur_fond=color.rgba(110/255,30/255,30/255,1), survol=color.rgba(150/255,40/255,40/255,1))

    texte_confirm = Text("Tout effacer ?", parent=panneau, y=0.10, origin=(0,0), scale=2.5, color=ATTENTION, enabled=False, z=-0.1)
    btn_oui = creer_bouton("OUI", panneau, (-0.2, -0.10), (0.3, 0.15), au_clic=executer_reset, couleur_fond=color.rgba(180/255,40/255,40/255,1), enabled=False)
    btn_non = creer_bouton("NON", panneau, (0.2, -0.10), (0.3, 0.15), au_clic=annuler_reset, couleur_fond=BOUTON, enabled=False)

    gest_menus.enregistrer('pause', panneau, bloquant=True)
    return superposition

def creer_menu_commandes(gest_menus):
    panneau = Entity(parent=camera.ui, model='quad', color=PANNEAU, scale=(0.62, 0.78), z=0.4, enabled=False)
    Text("Commandes FAUNEX", parent=panneau, y=0.42, origin=(0,0), scale=2.5, color=TITRE, z=-0.1)

    touches = ["TAB", "ESC", "Clic G (maintenir)", "Clic G (relacher)", "Molette", "P", "E", "B"]
    descriptions = ["Ouvrir/Fermer ce menu", "Menu Pause", "Cadrer une photo", "Prendre la photo", "Zoom optique", "Poser un appat", "Encyclopedie", "Boutique"]
    
    for i in range(len(touches)):
        y = 0.26 - i * 0.08
        Text(touches[i], parent=panneau, position=(-0.44, y), scale=1.5, color=ACCENT, z=-0.1)
        Text(descriptions[i], parent=panneau, position=(-0.08, y), scale=1.5, color=color.white, z=-0.1)

    def fermer_commandes():
        gest_menus.fermer('commandes')

    creer_bouton("Fermer (TAB)", panneau, (0, -0.40), (0.45, 0.085), au_clic=fermer_commandes)
    gest_menus.enregistrer('commandes', panneau, bloquant=True)
    return panneau

def creer_menu_encyclopedie(gest_menus, etat_jeu, entites):
    panneau = Entity(parent=camera.ui, model='quad', color=PANNEAU, scale=(0.90, 0.88), z=0.4, enabled=False)
    Text("Wiki-Dex", parent=panneau, y=0.44, origin=(0,0), scale=2.5, color=TITRE, z=-0.1)

    texte_info = Text("", parent=panneau, position=(-0.42, 0.35), scale=1.5, color=color.white, z=-0.1)
    panneau.cartes_photos = []

    def rafraichir():
        for e in panneau.cartes_photos:
            destroy(e)
        panneau.cartes_photos.clear()

        chaine_badges = ""
        if len(etat_jeu.badges) > 0:
            for b in etat_jeu.badges:
                chaine_badges += b + ", "
        else:
            chaine_badges = "Aucun"
            
        nb_decouvertes = len(etat_jeu.encyclopedie)
        mot_animal = "animal"
        if nb_decouvertes > 1:
            mot_animal = "animaux"
        
        texte_info.text = f"Badges : {chaine_badges}\nDécouvertes : {nb_decouvertes} {mot_animal}"

        for idx in range(len(etat_jeu.encyclopedie)):
            nom = etat_jeu.encyclopedie[idx]
            col = color.white
            for a in entites:
                if hasattr(a, 'nom'):
                    if a.nom == nom:
                        col = a.color
                        break
                        
            col_x = -0.34 + (idx % 4) * 0.225
            col_y = 0.10 - (idx // 4) * 0.24

            carte = Entity(parent=panneau, model='quad', color=color.rgba(200/255,200/255,200/255,1), scale=(0.19, 0.20), position=(col_x, col_y), z=-0.1)
            interieur = Entity(parent=carte, model='quad', color=col, scale=(0.85, 0.62), position=(0, 0.10), z=-0.2)
            etiquette = Text(nom, parent=carte, scale=4.0, color=color.black, position=(-0.46, -0.38), z=-0.3)
            
            panneau.cartes_photos.append(carte)
            panneau.cartes_photos.append(interieur)
            panneau.cartes_photos.append(etiquette)

    def fermer_encyclo():
        gest_menus.fermer('encyclo')

    creer_bouton("Fermer (E)", panneau, (0, -0.42), (0.38, 0.075), au_clic=fermer_encyclo)
    gest_menus.enregistrer('encyclo', panneau, bloquant=True)
    panneau.rafraichir = rafraichir
    return panneau

def creer_menu_boutique(gest_menus, etat_jeu, appareil_photo, gest_notifs):
    panneau = Entity(parent=camera.ui, model='quad', color=PANNEAU, scale=(0.55, 0.52), z=0.4, enabled=False)
    Text("Boutique", parent=panneau, y=0.40, origin=(0,0), scale=2.5, color=TITRE, z=-0.1)
    affichage_credits = Text("", parent=panneau, y=0.25, origin=(0,0), scale=1.8, color=ACCENT, z=-0.1)

    def mettre_a_jour_credits():
        affichage_credits.text = f"Crédits : {etat_jeu.credits} cr"

    def acheter_carte_sd():
        cout = 50
        if etat_jeu.credits >= cout:
            etat_jeu.credits -= cout
            appareil_photo.capacite += 5
            mettre_a_jour_credits()
            gest_notifs.ajouter("Achat : Carte SD (+5 photos) !", ACCENT)
        else:
            gest_notifs.ajouter(f"Pas assez de crédits ! (manque {cout - etat_jeu.credits} cr)", ATTENTION)

    def acheter_appat():
        cout = 20
        if etat_jeu.credits >= cout:
            etat_jeu.credits -= cout
            etat_jeu.appats_restants += 1
            mettre_a_jour_credits()
            gest_notifs.ajouter("Achat : Appat x1 !", ACCENT)
        else:
            gest_notifs.ajouter(f"Pas assez de crédits ! (manque {cout - etat_jeu.credits} cr)", ATTENTION)

    creer_bouton("Carte SD (+5 photos) - 50 cr", panneau, (0, 0.05), (0.85, 0.15), au_clic=acheter_carte_sd)
    creer_bouton("Appat x1 - 20 cr", panneau, (0, -0.13), (0.85, 0.15), au_clic=acheter_appat)

    def fermer_boutique():
        gest_menus.fermer('shop')

    creer_bouton("Fermer (B)", panneau, (0, -0.38), (0.38, 0.09), au_clic=fermer_boutique)
    gest_menus.enregistrer('shop', panneau, bloquant=True)
    panneau.mettre_a_jour_credits = mettre_a_jour_credits
    return panneau

def creer_menu_quiz(gest_menus, gest_notifs, etat_jeu):
    panneau = Entity(parent=camera.ui, model='quad', color=PANNEAU, scale=(0.52, 0.55), z=0.4, enabled=False)
    Text("Quiz Naturel", parent=panneau, y=0.40, origin=(0,0), scale=2.5, color=TITRE, z=-0.1)
    question = Text("", parent=panneau, y=0.25, origin=(0,0), scale=1.5, color=color.white, z=-0.1)

    panneau.reponse_attendue = ""

    def verifier_reponse(rep):
        if rep == panneau.reponse_attendue:
            etat_jeu.credits += 15
            gest_notifs.ajouter("Bonne réponse ! +15 cr", ACCENT)
        else:
            gest_notifs.ajouter(f"Erreur ! C'était un(e) {panneau.reponse_attendue}.", ATTENTION)
        gest_menus.fermer('quiz')

    def rep_mammifere(): verifier_reponse("Mammifère")
    def rep_reptile(): verifier_reponse("Reptile")
    def rep_insecte(): verifier_reponse("Insecte")
    def rep_oiseau(): verifier_reponse("Oiseau")

    creer_bouton("Mammifère", panneau, (0, 0.05), (0.65, 0.11), au_clic=rep_mammifere)
    creer_bouton("Reptile", panneau, (0, -0.08), (0.65, 0.11), au_clic=rep_reptile)
    creer_bouton("Insecte", panneau, (0, -0.21), (0.65, 0.11), au_clic=rep_insecte)
    creer_bouton("Oiseau", panneau, (0, -0.34), (0.65, 0.11), au_clic=rep_oiseau)

    gest_menus.enregistrer('quiz', panneau, bloquant=True)
    panneau.question = question
    return panneau

class JeuFaunex:
    def __init__(self):
        self.etat_jeu = EtatJeu()
        self.appareil_photo = AppareilPhoto()
        self.entites = []
        
        self.temps_derniere_sauvegarde = time.time()

        self.joueur = FirstPersonController(position=(0,2,0), speed=10)
        self.etat_jeu.joueur = self.joueur

        self.terrain = Entity(model='plane', texture='grass', collider='mesh', scale=300, color=color.rgb(85,140,65))
        Sky()

        self.etat_jeu.charger(self.appareil_photo)

        self._creer_entites_monde()

        self.gest_notifs = GestionnaireNotification()
        self.gest_menus = GestionnaireMenu(self.joueur)
        self.ath = AffichageTeteHaute(self.etat_jeu, self.appareil_photo)
        self.viseur = Viseur()
        self.barre_focus = BarreMiseAuPoint()

        self.pause_overlay = creer_menu_pause(self.gest_menus, self.etat_jeu, self.appareil_photo, self.entites, self.gest_notifs)
        creer_menu_commandes(self.gest_menus)
        self.encyclo_menu = creer_menu_encyclopedie(self.gest_menus, self.etat_jeu, self.entites)
        self.shop_menu = creer_menu_boutique(self.gest_menus, self.etat_jeu, self.appareil_photo, self.gest_notifs)
        self.quiz_menu = creer_menu_quiz(self.gest_menus, self.gest_notifs, self.etat_jeu)

        self.gest_menus.ouvrir('commandes')

    def _creer_entites_monde(self):
        self.entites.append(Animal("Renard Roux", "Mammifère", color.orange, (10, 1, 15), "fuit", 2))
        self.entites.append(Animal("Ours Brun", "Mammifère", color.brown, (-20, 1.5, -10), "curieux", 4))
        self.entites.append(Animal("Cerf", "Mammifère", color.rgb(160,100,40), (30, 1.5, 25), "fuit", 2))
        self.entites.append(Animal("Fennec", "Mammifère", color.yellow, (70, 1, 30), "curieux", 3))
        self.entites.append(Animal("Loup Gris", "Mammifère", color.gray, (-40, 1, 50), "curieux", 4))
        self.entites.append(Animal("Sanglier", "Mammifère", color.rgb(100, 70, 50), (15, 1, -30), "fuit", 2))
        self.entites.append(Animal("Lynx", "Mammifère", color.black, (-60, 1, -60), "curieux", 5))
        self.entites.append(Animal("Panthère", "Mammifère", color.white, (80, 1, -80), "fuit", 5))
        
        self.entites.append(Animal("Aigle Royal", "Oiseau", color.rgb(200, 150, 50), (0, 15, 40), "fuit", 4))
        self.entites.append(Animal("Faucon", "Oiseau", color.dark_gray, (50, 20, -20), "fuit", 5))
        self.entites.append(Animal("Corbeau", "Oiseau", color.black, (-30, 12, 10), "curieux", 1))
        self.entites.append(Animal("Hibou", "Oiseau", color.rgb(130, 100, 60), (40, 10, 60), "sommeil", 3))
        self.entites.append(Animal("Pigeon", "Oiseau", color.light_gray, (5, 8, -5), "curieux", 1))

        self.entites.append(Animal("Crocodile", "Reptile", color.rgb(50, 100, 50), (-70, 0.5, 20), "sommeil", 4))
        self.entites.append(Animal("Vipère", "Reptile", color.rgb(120, 150, 80), (20, 0.2, -40), "fuit", 3))
        self.entites.append(Animal("Caméléon", "Reptile", color.green, (-15, 0.5, 35), "sommeil", 4))
        self.entites.append(Animal("Iguane", "Reptile", color.rgb(80, 180, 80), (60, 0.5, 10), "curieux", 3))

        self.entites.append(Animal("Scorpion", "Insecte", color.red, (80, 0.2, 10), "fuit", 3))
        self.entites.append(Animal("Scarabée", "Insecte", color.rgb(20, 20, 80), (-25, 0.1, -25), "fuit", 1))
        self.entites.append(Animal("Mante", "Insecte", color.lime, (-50, 0.5, -10), "sommeil", 3))
        self.entites.append(Animal("Papillon", "Insecte", color.cyan, (35, 3, -15), "curieux", 2))

        self.entites.append(Dechet((5,0.5,5)))
        self.entites.append(Dechet((-15,0.5,20)))
        self.entites.append(Dechet((60,0.5,5)))

        self.pnj = PNJ("Garde Forestier", (0,1,10), color.green)
        self.entites.append(self.pnj)

        self.entites.append(Empreinte((5,0.1,10)))

    def verifier_salutation_pnj(self):
        if self.etat_jeu.pnj_rencontre:
            return
        dist = distance_2d(self.joueur.position, self.pnj.position)
        if dist < DIST_SALUTATION_PNJ:
            self.etat_jeu.pnj_rencontre = True
            self.gest_notifs.ajouter("Garde Forestier : Bienvenue dans FAUNEX !", TITRE, 5.0)

    def update(self):
        self.gest_notifs.mettre_a_jour()

        if time.time() - self.temps_derniere_sauvegarde >= 10:
            self.etat_jeu.sauvegarder(self.appareil_photo)
            self.temps_derniere_sauvegarde = time.time()
            self.gest_notifs.ajouter("Autosauvegarde...", color.gray, 1.5)

        menu_ouvert = self.gest_menus.est_bloque()
        if menu_ouvert:
            self.viseur.h.enabled = False
            self.viseur.v.enabled = False
            self.viseur.point.enabled = False
        else:
            self.viseur.h.enabled = True
            self.viseur.v.enabled = True
            self.viseur.point.enabled = True

        self.ath.mettre_a_jour()

        self.appareil_photo.mettre_a_jour_mise_au_point()
        if self.appareil_photo.en_mise_au_point:
            self.barre_focus.mettre_a_jour(self.appareil_photo.valeur_mise_au_point)

        if menu_ouvert == False:
            for e in self.entites:
                if hasattr(e, 'mettre_a_jour_ia'):
                    e.mettre_a_jour_ia(self.joueur, self.entites)

        self.verifier_salutation_pnj()

    def input(self, key):
        if key == 'escape':
            if len(self.gest_menus.menus_actifs) > 0:
                self.gest_menus.fermer_tout()
                self.pause_overlay.enabled = False
            else:
                self.pause_overlay.enabled = True
                self.gest_menus.ouvrir('pause')
            return

        if key == 'tab':
            self.gest_menus.basculer('commandes')
            return
            
        if key == 'e':
            self.gest_menus.basculer('encyclo')
            if self.encyclo_menu.enabled:
                self.encyclo_menu.rafraichir()
            return
            
        if key == 'b':
            self.gest_menus.basculer('shop')
            if self.shop_menu.enabled:
                self.shop_menu.mettre_a_jour_credits()
            return

        if self.gest_menus.est_bloque():
            return

        if key == 'scroll up':
            self.appareil_photo.zoomer(1)
        elif key == 'scroll down':
            self.appareil_photo.zoomer(-1)
        elif key == 'p':
            if self.etat_jeu.appats_restants > 0:
                self.etat_jeu.appats_restants -= 1
                pos = self.joueur.position + self.joueur.forward * 2
                self.entites.append(Appat(pos))
                self.gest_notifs.ajouter(f"Appât posé ! ({self.etat_jeu.appats_restants} restant(s))")
            else:
                self.gest_notifs.ajouter("Plus d'appâts !", ATTENTION)

        elif key == 'left mouse down':
            touche_ray = raycast(camera.world_position, camera.forward, distance=DIST_MAX_MISE_AU_POINT, ignore=[self.joueur])
            
            if touche_ray.hit:
                if hasattr(touche_ray.entity, 'etiquette'):
                    if touche_ray.entity.etiquette == 'animal':
                        self.appareil_photo.demarrer_mise_au_point()
                        self.barre_focus.afficher()
                    elif touche_ray.entity.etiquette == 'dechet':
                        if touche_ray.entity in self.entites:
                            self.entites.remove(touche_ray.entity)
                        destroy(touche_ray.entity)
                        self.etat_jeu.credits += 10
                        self.etat_jeu.dechets_ramasses += 1
                        badge = self.etat_jeu.verifier_badges()
                        if badge != None:
                            self.gest_notifs.ajouter(f"Badge débloqué : {badge} !", TITRE)
                        self.gest_notifs.ajouter("Déchet ramassé ! +10 cr", ACCENT)

        elif key == 'left mouse up':
            if self.appareil_photo.en_mise_au_point:
                self.appareil_photo.arreter_mise_au_point()
                self.barre_focus.cacher()
                touche_ray = raycast(camera.world_position, camera.forward, distance=DIST_MAX_MISE_AU_POINT, ignore=[self.joueur])
                
                if touche_ray.hit:
                    if hasattr(touche_ray.entity, 'etiquette'):
                        if touche_ray.entity.etiquette == 'animal':
                            succes, premiere_fois, score = self.appareil_photo.prendre_photo(touche_ray.entity, self.etat_jeu)
                            
                            if succes == False:
                                self.gest_notifs.ajouter("Carte SD pleine ! Achète une extension.", ATTENTION)
                            else:
                                if premiere_fois:
                                    self.gest_notifs.ajouter(f"NOUVEAU ! {touche_ray.entity.nom} +{score} cr", ACCENT)
                                    self.quiz_menu.question.text = f"Type de {touche_ray.entity.nom} ?"
                                    self.quiz_menu.reponse_attendue = touche_ray.entity.espece
                                    self.gest_menus.ouvrir('quiz')
                                else:
                                    self.gest_notifs.ajouter(f"{touche_ray.entity.nom} déjà vu ! +{score} cr", TEXTE)

jeu = JeuFaunex()

def update():
    jeu.update()

def input(key):
    jeu.input(key)

app.run()