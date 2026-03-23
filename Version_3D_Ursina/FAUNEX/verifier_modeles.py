#!/usr/bin/env python3
"""
Script de vérification des modèles GLB pour FAUNEX
Vérifie que tous les fichiers sont présents et accessibles
"""

from pathlib import Path
import json

# Configuration des chemins
SCRIPT_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPT_DIR / "assets_add"
ANIMALS_DIR = ASSETS_DIR / "3d" / "animals"
GROUND_DIR = ASSETS_DIR / "3d" / "ground"
FARMER_DIR = ASSETS_DIR / "3d" / "farmer"

# Données des animaux
DONNEES_ANIMAUX = [
    ("Renard Roux", "Mammifère", "01_red_fox.glb"),
    ("Ours Brun", "Mammifère", "02_brown_bear.glb"),
    ("Cerf", "Mammifère", "03_deer.glb"),
    ("Fennec", "Mammifère", "04_fennec.glb"),
    ("Loup Gris", "Mammifère", "05_gray_wolf.glb"),
    ("Sanglier", "Mammifère", "06_wild_boar.glb"),
    ("Lynx", "Mammifère", "07_lynx.glb"),
    ("Panthère", "Mammifère", "08_panther.glb"),
    ("Aigle Royal", "Oiseau", "09_golden_eagle.glb"),
    ("Faucon", "Oiseau", "10_falcon.glb"),
    ("Corbeau", "Oiseau", "11_crow.glb"),
    ("Hibou", "Oiseau", "12_owl.glb"),
    ("Pigeon", "Oiseau", "13_pigeon.glb"),
    ("Crocodile", "Reptile", "14_crocodile.glb"),
    ("Vipère", "Reptile", "15_viper.glb"),
    ("Caméléon", "Reptile", "16_chameleon.glb"),
    ("Iguane", "Reptile", "17_iguana.glb"),
    ("Scorpion", "Insecte", "18_scorpio.glb"),
    ("Scarabée", "Insecte", "19_beetle.glb"),
    ("Mante", "Insecte", "20_mantis.glb"),
    ("Papillon", "Insecte", "21_butterfly.glb"),
]

DONNEES_ARBRES = [
    ("Arbre Grand", "00001_tree.glb"),
    ("Arbre Petit", "00002_tree.glb"),
    ("Rocher Petit", "00003_rocks.glb"),
    ("Rocher Grand", "00004_rocks.glb"),
    ("Buisson", "00005_bush.glb"),
]

DONNEES_FARMER = [
    ("Fermier Basique", "00_farmer.glb"),
    ("Fermier V2", "00_farmer_v2.glb"),
]


def verifier_fichier(chemin, nom_entite):
    """Vérifie qu'un fichier existe et retourne son statut"""
    if chemin.exists():
        taille_ko = chemin.stat().st_size / 1024
        print(f"  ✅ {nom_entite}: {chemin.name} ({taille_ko:.1f} KB)")
        return True
    else:
        print(f"  ❌ {nom_entite}: MANQUANT - {chemin.name}")
        return False


def afficher_separator(titre, char="="):
    """Affiche un séparateur avec titre"""
    longueur = 60
    titre_format = f" {titre} "
    padding_gauche = (longueur - len(titre_format)) // 2
    padding_droit = longueur - len(titre_format) - padding_gauche
    
    print("\n" + char * longueur)
    print(char * padding_gauche + titre_format + char * padding_droit)
    print(char * longueur)


def main():
    print("\n🐾 FAUNEX - Vérification des modèles 3D\n")
    
    # Vérifier la structure des répertoires
    afficher_separator("Vérification des répertoires")
    
    repertoires = [
        (ASSETS_DIR, "assets_add"),
        (ANIMALS_DIR, "animals"),
        (GROUND_DIR, "ground"),
        (FARMER_DIR, "farmer"),
    ]
    
    tous_ok = True
    for chemin, nom in repertoires:
        if chemin.exists():
            print(f"✅ {nom}: {chemin}")
        else:
            print(f"❌ {nom}: MANQUANT - {chemin}")
            tous_ok = False
    
    if not tous_ok:
        print("\n⚠️  ERREUR: Répertoires manquants !")
        print(f"   Le dossier 'assets_add' doit être à côté de ce script")
        return False
    
    # Vérifier les modèles d'animaux
    afficher_separator("Modèles d'animaux (21 total)")
    
    animaux_ok = 0
    animaux_manquants = 0
    
    for nom, espece, fichier in DONNEES_ANIMAUX:
        chemin = ANIMALS_DIR / fichier
        if verifier_fichier(chemin, f"{nom} ({espece})"):
            animaux_ok += 1
        else:
            animaux_manquants += 1
    
    print(f"\n📊 Animaux: {animaux_ok}/21 présents", end="")
    if animaux_manquants > 0:
        print(f", {animaux_manquants} manquants ❌")
    else:
        print(" ✅")
    
    # Vérifier les modèles de terrain
    afficher_separator("Modèles de terrain (5 total)")
    
    arbres_ok = 0
    arbres_manquants = 0
    
    for nom, fichier in DONNEES_ARBRES:
        chemin = GROUND_DIR / fichier
        if verifier_fichier(chemin, nom):
            arbres_ok += 1
        else:
            arbres_manquants += 1
    
    print(f"\n📊 Terrain: {arbres_ok}/5 présents", end="")
    if arbres_manquants > 0:
        print(f", {arbres_manquants} manquants ❌")
    else:
        print(" ✅")
    
    # Vérifier les modèles Farmer
    afficher_separator("Modèles Farmer (2 total)")
    
    farmer_ok = 0
    farmer_manquants = 0
    
    for nom, fichier in DONNEES_FARMER:
        chemin = FARMER_DIR / fichier
        if verifier_fichier(chemin, nom):
            farmer_ok += 1
        else:
            farmer_manquants += 1
    
    print(f"\n📊 Farmer: {farmer_ok}/2 présents", end="")
    if farmer_manquants > 0:
        print(f", {farmer_manquants} manquants ❌")
    else:
        print(" ✅")
    
    # Résumé final
    afficher_separator("Résumé", "=")
    
    total_presents = animaux_ok + arbres_ok + farmer_ok
    total_manquants = animaux_manquants + arbres_manquants + farmer_manquants
    total = total_presents + total_manquants
    
    print(f"\nTotal: {total_presents}/{total} modèles présents")
    
    if total_manquants == 0:
        print("\n🎉 Tous les modèles sont présents ! Prêt à lancer FAUNEX !")
        print("\nPour lancer le jeu:")
        print("  python version_dev_corrigee.py")
        return True
    else:
        print(f"\n⚠️  {total_manquants} modèle(s) manquant(s)")
        print("\nModèles manquants:")
        
        for nom, espece, fichier in DONNEES_ANIMAUX:
            chemin = ANIMALS_DIR / fichier
            if not chemin.exists():
                print(f"  - {nom} ({espece}): {fichier}")
        
        for nom, fichier in DONNEES_ARBRES:
            chemin = GROUND_DIR / fichier
            if not chemin.exists():
                print(f"  - {nom}: {fichier}")
        
        for nom, fichier in DONNEES_FARMER:
            chemin = FARMER_DIR / fichier
            if not chemin.exists():
                print(f"  - {nom}: {fichier}")
        
        print("\nAssurez-vous que le dossier assets_add contient tous les fichiers GLB")
        return False


def generer_rapport(fichier_sortie="rapport_modeles.json"):
    """Génère un rapport JSON des modèles disponibles"""
    rapport = {
        "animaux": [],
        "terrain": [],
        "farmer": [],
        "total_presents": 0,
        "total_manquants": 0
    }
    
    for nom, espece, fichier in DONNEES_ANIMAUX:
        chemin = ANIMALS_DIR / fichier
        rapport["animaux"].append({
            "nom": nom,
            "espece": espece,
            "fichier": fichier,
            "present": chemin.exists(),
            "taille_kb": chemin.stat().st_size / 1024 if chemin.exists() else 0
        })
        if chemin.exists():
            rapport["total_presents"] += 1
        else:
            rapport["total_manquants"] += 1
    
    for nom, fichier in DONNEES_ARBRES:
        chemin = GROUND_DIR / fichier
        rapport["terrain"].append({
            "nom": nom,
            "fichier": fichier,
            "present": chemin.exists(),
            "taille_kb": chemin.stat().st_size / 1024 if chemin.exists() else 0
        })
        if chemin.exists():
            rapport["total_presents"] += 1
        else:
            rapport["total_manquants"] += 1
    
    for nom, fichier in DONNEES_FARMER:
        chemin = FARMER_DIR / fichier
        rapport["farmer"].append({
            "nom": nom,
            "fichier": fichier,
            "present": chemin.exists(),
            "taille_kb": chemin.stat().st_size / 1024 if chemin.exists() else 0
        })
        if chemin.exists():
            rapport["total_presents"] += 1
        else:
            rapport["total_manquants"] += 1
    
    # Sauvegarder le rapport
    with open(fichier_sortie, 'w', encoding='utf-8') as f:
        json.dump(rapport, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Rapport généré: {fichier_sortie}")
    return rapport


if __name__ == "__main__":
    resultat = main()
    
    # Générer un rapport JSON
    generer_rapport()
    
    # Code de sortie
    exit(0 if resultat else 1)
