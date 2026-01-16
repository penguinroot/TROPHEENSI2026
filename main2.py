from math import pi, sin, cos
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import Point3, Vec3
from direct.gui.DirectGui import DirectButton
from panda3d.core import WindowProperties

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()

        # --- ENVIRONNEMENT ---
        self.scene = self.loader.loadModel("models/environment")
        self.scene.reparentTo(self.render)
        self.scene.setScale(0.25)
        self.scene.setPos(-8, 42, 0)

        # --- PANDA ACTEUR ---
        self.pandaActor = Actor("models/panda-model",
                                {"walk": "models/panda-walk4"})
        self.pandaActor.setScale(0.005)
        self.pandaActor.reparentTo(self.render)
        self.pandaActor.loop("walk")

        # --- CAMERA FIXE ---
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        self.fixedCamera = True

        # --- CAMERA POV DU PANDA ---
        self.povPos = Point3(0, 0.5, 1000)
        self.povHpr = Point3(180, 0, 0)

        # --- BOUTON GUI POUR BASCULER LES VUES ---
        self.toggleButton = DirectButton(text="Changer Vue",
                                         scale=0.07,
                                         pos=(0.8, 0, 0.9),
                                         command=self.toggleCameraView)

        # --- CONTRÔLE DU PANDA ---
        self.accept("z", self.setKey, ["backward", True])
        self.accept("z-up", self.setKey, ["backward", False])
        self.accept("s", self.setKey, ["forward", True])
        self.accept("s-up", self.setKey, ["forward", False])
        self.accept("q", self.setKey, ["turnLeft", True])
        self.accept("q-up", self.setKey, ["turnLeft", False])
        self.accept("d", self.setKey, ["turnRight", True])
        self.accept("d-up", self.setKey, ["turnRight", False])

        self.keyMap = {
            "forward": False,
            "backward": False,
            "turnLeft": False,
            "turnRight": False
        }

        self.speed = 1000        # vitesse de déplacement (unités/seconde)
        self.turnSpeed = 60   # vitesse de rotation (degrés/seconde)

        self.taskMgr.add(self.updatePanda, "UpdatePandaTask")

    # --- GESTION DES TOUCHES ---
    def setKey(self, key, value):
        self.keyMap[key] = value

    # --- MOUVEMENT DU PANDA ---
    def updatePanda(self, task):
        dt = globalClock.getDt()  # temps depuis la dernière frame

        # Rotation
        if self.keyMap["turnLeft"]:
            self.pandaActor.setH(self.pandaActor.getH() + self.turnSpeed * dt)
        if self.keyMap["turnRight"]:
            self.pandaActor.setH(self.pandaActor.getH() - self.turnSpeed * dt)

        # Déplacement
        direction = Vec3(0, 0, 0)
        if self.keyMap["forward"]:
            direction.y += 1
        if self.keyMap["backward"]:
            direction.y -= 1

        if direction.length() > 0:
            direction.normalize()
            # Déplacer dans la direction locale du panda
            self.pandaActor.setPos(self.pandaActor, direction * self.speed * dt)

        return Task.cont

    # --- CAMERA FIXE AUTOUR DE LA SCÈNE ---
    def spinCameraTask(self, task):
        if self.fixedCamera:
            angleDegrees = task.time * 6.0
            angleRadians = angleDegrees * (pi / 180.0)
            self.camera.setPos(20 * sin(angleRadians), -20 * cos(angleRadians), 3)
            self.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont

    # --- BASCULER ENTRE LES VUES ---
    def toggleCameraView(self):
        if self.fixedCamera:
            self.fixedCamera = False
            self.camera.reparentTo(self.pandaActor)
            self.camera.setPos(self.povPos)
            self.camera.setHpr(self.povHpr)
        else:
            self.fixedCamera = True
            self.camera.reparentTo(self.render)

app = MyApp()
app.run()
