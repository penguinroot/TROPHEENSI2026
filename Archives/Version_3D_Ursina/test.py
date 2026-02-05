from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader

app = Ursina()
Entity.default_shader = lit_with_shadows_shader
objets_trouves = []
# ===== TERRAIN =====
terrain = Entity(
    model='plane',
    texture='grass.png',
    collider='mesh',
    scale=1000
)
# ===== UI AVEC TEXTE =====
ui_fenetre = Panel(
    parent=camera.ui,
    scale=(0.5, 0.5),
    position=(0, 0),
    enabled=False
)

# Texte en blanc pour contraste
ui_titre = Text(
    "Objets trouvés",
    parent=ui_fenetre,
    position=(0, 0.15),
    origin=(0, 0),
    scale=2,
    color=color.white  # Texte blanc
)

ui_contenu = Text(
    "fvesve",
    parent=ui_fenetre,
    position=(0, 0),
    origin=(0, 0),
    scale=1.5,
    color=color.white  # Texte blanc
)
def mettre_a_jour_fenetre():
    if objets_trouves:
        liste_objets = "\n".join(f"- {obj.nom}" for obj in objets_trouves)
        ui_contenu.text = liste_objets
    else:
        ui_contenu.text = "Aucun objet trouvé pour l'instant."
    if len(objets_trouves)>=1 : 
        nombre_lignes = len(objets_trouves) 
    else : 
        nombre_lignes=1
    ui_contenu.y = -0.05 * nombre_lignes
# ===== OBJETS À TROUVER =====
arbre = Entity(
    nom='arbre',
    model='cube',
    collider='box',
    scale=10,
    position=(0, 5, 30),
)
arbre.tag = 'a_trouver'

fleur = Entity(
    nom='fleur',
    model='quad',
    color=color.red,
    collider='box',
    scale=10,
    position=(30, 5, 0)
)
fleur.tag = 'a_trouver'

# ===== JOUEUR =====
player = FirstPersonController(
    position=(0, 200, 0),
    speed=20
)

# ===== CIEL =====
Sky()

# ===== INPUT =====
def input(key):
    if key == 'left mouse down':
        hit = raycast(
            origin=camera.world_position,
            direction=camera.forward,
            distance=100,
            ignore=[player],
            debug=True
        )

        if hit.hit:
            if hasattr(hit.entity, 'tag') and hit.entity.tag == 'a_trouver':
                print("✅ Objet à trouver cliqué !")
                hit.entity.tag='trouve'
                objets_trouves.append(hit.entity)
    if key == 'g':
        ui_fenetre.enabled = not ui_fenetre.enabled
        if ui_fenetre.enabled:
            mettre_a_jour_fenetre()

app.run()
