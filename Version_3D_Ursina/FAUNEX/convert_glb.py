#!/usr/bin/env python3
"""
Convertisseur GLB → OBJ + MTL (lot entier d'un dossier)
--------------------------------------------------------
Deux modes disponibles :
  1. API Convert3D  (par défaut, nécessite une clé API)
  2. Local via trimesh (--local, aucune clé requise, pip install trimesh)

Usage :
    python convert_glb_to_obj.py <dossier_input> [options]

Exemples :
    # Mode API (clé dans la variable d'env CONVERT3D_API_KEY)
    python convert_glb_to_obj.py ./mes_modeles

    # Mode API avec clé en argument
    python convert_glb_to_obj.py ./mes_modeles --api-key VOTRE_CLE

    # Mode local (sans API)
    python convert_glb_to_obj.py ./mes_modeles --local

    # Spécifier un dossier de sortie
    python convert_glb_to_obj.py ./mes_modeles --output ./obj_output
"""

import argparse
import os
import sys
import time
import zipfile
import io
from pathlib import Path


# ─────────────────────────────────────────────────────────────
# Conversion via l'API Convert3D
# ─────────────────────────────────────────────────────────────

def convert_via_api(glb_path: Path, output_dir: Path, api_key: str) -> bool:
    """Envoie le fichier GLB à l'API Convert3D et récupère OBJ+MTL."""
    try:
        import requests
    except ImportError:
        print("  ✗ Le module 'requests' est manquant. Installez-le : pip install requests")
        return False

    url = "https://convert3d.org/api/convert"
    headers = {"Authorization": f"Token {api_key}"}

    print(f"  → Envoi vers l'API : {glb_path.name}")
    try:
        with open(glb_path, "rb") as f:
            response = requests.post(
                url,
                headers=headers,
                files={"file": (glb_path.name, f, "model/gltf-binary")},
                data={"from_format": "glb", "to_format": "obj"},
                timeout=120,
            )
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Erreur réseau : {e}")
        return False

    if response.status_code != 200:
        print(f"  ✗ Erreur API ({response.status_code}) : {response.text[:200]}")
        return False

    # L'API renvoie soit un ZIP (OBJ + MTL + textures), soit un OBJ seul
    content_type = response.headers.get("Content-Type", "")
    stem = glb_path.stem

    if "zip" in content_type or response.content[:2] == b"PK":
        # Extraire le ZIP dans le dossier de sortie
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            for member in z.namelist():
                # Renommer les fichiers avec le nom du GLB source
                ext = Path(member).suffix
                dest_name = f"{stem}{ext}"
                dest_path = output_dir / dest_name
                with z.open(member) as src, open(dest_path, "wb") as dst:
                    dst.write(src.read())
                print(f"  ✓ Extrait : {dest_name}")
    else:
        # Réponse directe OBJ
        obj_path = output_dir / f"{stem}.obj"
        obj_path.write_bytes(response.content)
        print(f"  ✓ Sauvegardé : {obj_path.name}")

    return True


# ─────────────────────────────────────────────────────────────
# Conversion locale via trimesh
# ─────────────────────────────────────────────────────────────

def convert_local(glb_path: Path, output_dir: Path) -> bool:
    """Convertit un GLB en OBJ+MTL localement avec trimesh."""
    try:
        import trimesh
    except ImportError:
        print("  ✗ Le module 'trimesh' est manquant. Installez-le : pip install trimesh")
        return False

    stem = glb_path.stem
    obj_path = output_dir / f"{stem}.obj"
    mtl_path = output_dir / f"{stem}.mtl"

    try:
        scene = trimesh.load(str(glb_path), force="scene")

        # Si c'est un simple mesh et non une scène
        if isinstance(scene, trimesh.Trimesh):
            scene = trimesh.scene.scene.Scene(geometry={stem: scene})

        # Export OBJ (trimesh génère automatiquement le .mtl associé)
        result = scene.export(str(obj_path))

        if obj_path.exists():
            size_kb = obj_path.stat().st_size / 1024
            print(f"  ✓ OBJ créé : {obj_path.name} ({size_kb:.1f} Ko)")
        if mtl_path.exists():
            print(f"  ✓ MTL créé : {mtl_path.name}")

        return True

    except Exception as e:
        print(f"  ✗ Erreur de conversion : {e}")
        return False


# ─────────────────────────────────────────────────────────────
# Point d'entrée principal
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Convertit tous les fichiers GLB d'un dossier en OBJ + MTL"
    )
    parser.add_argument(
        "input_dir",
        type=str,
        help="Dossier contenant les fichiers .glb à convertir",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Dossier de sortie (défaut : <input_dir>/obj_output)",
    )
    parser.add_argument(
        "--api-key", "-k",
        type=str,
        default=None,
        help="Clé API Convert3D (ou variable d'env CONVERT3D_API_KEY)",
    )
    parser.add_argument(
        "--local", "-l",
        action="store_true",
        help="Utiliser la conversion locale via trimesh (sans API)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Délai en secondes entre les appels API (défaut : 1.0)",
    )
    args = parser.parse_args()

    # ── Résolution des chemins ──────────────────────────────
    input_dir = Path(args.input_dir).resolve()
    if not input_dir.is_dir():
        print(f"✗ Dossier introuvable : {input_dir}")
        sys.exit(1)

    output_dir = Path(args.output).resolve() if args.output else input_dir / "obj_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Recherche des fichiers GLB ──────────────────────────
    glb_files = sorted(input_dir.glob("*.glb"))
    if not glb_files:
        print(f"✗ Aucun fichier .glb trouvé dans : {input_dir}")
        sys.exit(0)

    print(f"\n📁 Dossier source  : {input_dir}")
    print(f"📂 Dossier de sortie : {output_dir}")
    print(f"🔢 Fichiers GLB trouvés : {len(glb_files)}\n")
    print("─" * 50)

    # ── Sélection du mode ───────────────────────────────────
    use_local = args.local
    api_key = args.api_key or os.environ.get("CONVERT3D_API_KEY")

    if not use_local and not api_key:
        print("⚠️  Aucune clé API trouvée. Basculement en mode local (trimesh).")
        print("   Conseil : définissez la variable CONVERT3D_API_KEY ou passez --api-key\n")
        use_local = True

    mode_label = "local (trimesh)" if use_local else "API Convert3D"
    print(f"⚙️  Mode : {mode_label}\n")

    # ── Boucle de conversion ────────────────────────────────
    success, failed = 0, 0

    for i, glb_path in enumerate(glb_files, start=1):
        print(f"[{i}/{len(glb_files)}] {glb_path.name}")

        if use_local:
            ok = convert_local(glb_path, output_dir)
        else:
            ok = convert_via_api(glb_path, output_dir, api_key)
            if i < len(glb_files):
                time.sleep(args.delay)  # respecter le rate-limit de l'API

        if ok:
            success += 1
        else:
            failed += 1

        print()

    # ── Résumé ──────────────────────────────────────────────
    print("─" * 50)
    print(f"✅ Convertis avec succès : {success}")
    if failed:
        print(f"❌ Échecs : {failed}")
    print(f"📂 Fichiers disponibles dans : {output_dir}")


if __name__ == "__main__":
    main()