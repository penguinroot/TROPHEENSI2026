from math import pi, sin, cos
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import Vec3, WindowProperties
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()

        # --- ENVIRONNEMENT ---
        self.scene = self.loader.loadModel("models/environment")
        self.scene.reparentTo(self.render)
        self.scene.setScale(0.25)
        self.scene.setPos(-8, 42, 0)

        # --- CAMERA POV PLAYER ---
        self.camera.setPos(0, -10, 2)
        self.camera.setHpr(0, 0, 0)

        # --- MOUVEMENT SMOOTH ---
        self.currentVelocity = Vec3(0, 0, 0)

        # --- GRAVITÉ & SAUT ---
        self.groundZ = 2          # hauteur du sol
        self.velocityZ = 0        # vitesse verticale actuelle
        self.jumpForce = 7        # puissance du saut
        self.gravity = -20        # gravité

        # --- MOUVEMENT CAMÉRA ---
        self.mouseSensitivity = 0.1
        self.lastMouseX = 0
        self.lastMouseY = 0
        self.camPitch = 0  # Rotation verticale
        self.camYaw = 0    # Rotation horizontale

        # Verrouiller la souris au centre
        properties = WindowProperties()
        properties.setCursorHidden(True)
        self.win.requestProperties(properties)

        # --- CONTROLES CLAVIER ---
        self.accept("z", self.setKey, ["forward", True])
        self.accept("z-up", self.setKey, ["forward", False])
        self.accept("s", self.setKey, ["backward", True])
        self.accept("s-up", self.setKey, ["backward", False])
        self.accept("q", self.setKey, ["left", True])
        self.accept("q-up", self.setKey, ["left", False])
        self.accept("d", self.setKey, ["right", True])
        self.accept("d-up", self.setKey, ["right", False])

        # SAUT
        self.accept("space", self.jump)
        
        # Échap pour quitter
        self.accept("escape", self.quitApp)

        self.keyMap = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False
        }

        self.speed = 10
        self.strafeSpeed = 8

        # Tâches
        self.taskMgr.add(self.updateCamera, "UpdateCameraTask")
        self.taskMgr.add(self.updateMouseLook, "UpdateMouseLookTask")

        # Centrer la souris
        self.centerMouse()

    def setKey(self, key, value):
        self.keyMap[key] = value

    def quitApp(self):
        self.userExit()

    def centerMouse(self):
        """Centre la souris dans la fenêtre"""
        if self.mouseWatcherNode.hasMouse():
            x = self.win.getXSize() // 2
            y = self.win.getYSize() // 2
            self.win.movePointer(0, x, y)
            self.lastMouseX = x
            self.lastMouseY = y

    def updateMouseLook(self, task):
        """Gère le mouvement de la caméra avec la souris"""
        if self.mouseWatcherNode.hasMouse():
            # Obtenir la position actuelle de la souris
            x = self.win.getPointer(0).getX()
            y = self.win.getPointer(0).getY()
            
            # Calculer le déplacement depuis la dernière frame
            dx = x - self.lastMouseX
            dy = y - self.lastMouseY
            
            # Mettre à jour les rotations
            self.camYaw -= dx * self.mouseSensitivity
            self.camPitch -= dy * self.mouseSensitivity
            
            # Limiter la rotation verticale (éviter le retournement)
            self.camPitch = max(-90, min(90, self.camPitch))
            
            # Appliquer la rotation à la caméra
            self.camera.setHpr(self.camYaw, self.camPitch, 0)
            
            # Recentrer la souris
            self.centerMouse()
            
        return Task.cont

    def jump(self):
        # Autoriser le saut seulement si on est au sol
        if self.camera.getZ() <= self.groundZ + 0.01:
            self.velocityZ = self.jumpForce

    def updateCamera(self, task):
        dt = globalClock.getDt()

        # --- CALCUL DU MOUVEMENT ---
        targetVel = Vec3(0, 0, 0)
        
        # Avant/arrière (Z/S) - dans la direction de la caméra
        if self.keyMap["forward"]:
            targetVel.y += self.speed
        if self.keyMap["backward"]:
            targetVel.y -= self.speed
            
        # Gauche/droite (Q/D) - latéral par rapport à la caméra
        if self.keyMap["left"]:
            targetVel.x -= self.strafeSpeed
        if self.keyMap["right"]:
            targetVel.x += self.strafeSpeed

        # Lissage du mouvement
        smoothMoveFactor = min(dt * 8, 1)
        self.currentVelocity = self.currentVelocity + (targetVel - self.currentVelocity) * smoothMoveFactor

        # Appliquer le mouvement relatif à l'orientation de la caméra
        movement = self.currentVelocity * dt
        self.camera.setPos(
            self.camera, 
            movement.x,  # Déplacement latéral
            movement.y,  # Déplacement avant/arrière
            0
        )

        # --- GRAVITÉ + SAUT ---
        self.velocityZ += self.gravity * dt
        newZ = self.camera.getZ() + self.velocityZ * dt

        if newZ < self.groundZ:
            newZ = self.groundZ
            self.velocityZ = 0

        self.camera.setZ(newZ)

        return Task.cont

app = MyApp()
app.run()