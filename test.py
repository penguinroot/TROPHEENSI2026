from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Charger le terrain depuis un modèle 3D
terrain = Entity(
    model='terrain.obj',  # Remplace 'terrain.obj' par le chemin de ton modèle 3D
    texture='terrain_texture.png',  # Optionnel, tu peux mettre une texture
    collider='mesh',  # Important pour que le joueur ne traverse pas le terrain
    scale=10
)

# Créer le joueur
player = FirstPersonController(
    position=(0, 200, 0),  # Position de départ au-dessus du terrain
    speed=5
)

# Lumière pour voir le terrain correctement
DirectionalLight(y=2, z=3, shadows=True)
Sky()  # Ajoute un ciel simple

def update():
    # Ici tu peux ajouter des interactions ou des contrôles supplémentaires
    pass

app.run()
