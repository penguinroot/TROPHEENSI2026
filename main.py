from ursina import *

# Initialisation de l'application
app = Ursina()

# Fenêtre
window.title = "Mon jeu Ursina"
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = True

# Sol
ground = Entity(
    model='plane',
    scale=(20, 1, 20),
    texture='white_cube',
    texture_scale=(20, 20),
    collider='box',
    color=color.light_gray
)

# Cube de test
cube = Entity(
    model='cube',
    scale=1,
    position=(0, 0.5, 0),
    texture='white_cube',
    color=color.azure,
    collider='box'
)

# Caméra
camera.position = (0, 8, -15)
camera.rotation_x = 30

# Fonction update (appelée à chaque frame)
def update():
    # Rotation du cube
    cube.rotation_y += 40 * time.dt

# Entrées clavier / souris
def input(key):
    if key == 'escape':
        quit()

# Lancement du jeu
app.run()
