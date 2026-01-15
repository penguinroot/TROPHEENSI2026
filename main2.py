from math import pi, sin, cos
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import (
    Point3, Vec4, AmbientLight, DirectionalLight,
    Spotlight, PerspectiveLens, Fog, WindowProperties
)
from direct.filter.CommonFilters import CommonFilters


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.render.setAntialias(True)

        # --------------------
        # Fenêtre
        # --------------------
        props = WindowProperties()
        props.setTitle("Panda3D - Cinematic RTX-like Demo")
        self.win.requestProperties(props)

        # --------------------
        # Décor
        # --------------------
        self.scene = self.loader.loadModel("models/environment")
        self.scene.reparentTo(self.render)
        self.scene.setScale(0.25)
        self.scene.setPos(-8, 42, 0)
        self.scene.setShaderAuto()

        # --------------------
        # Panda
        # --------------------
        self.pandaActor = Actor(
            "models/panda-model",
            {"walk": "models/panda-walk4"}
        )
        self.pandaActor.setScale(0.005)
        self.pandaActor.setPos(0, 10, 0)
        self.pandaActor.reparentTo(self.render)
        self.pandaActor.setShaderAuto()
        self.pandaActor.loop("walk")

        # --------------------
        # Lumières
        # --------------------
        # Lumière ambiante faible
        ambient = AmbientLight("ambient")
        ambient.setColor(Vec4(0.08, 0.08, 0.1, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        # Soleil principal avec ombres HD
        self.sun = DirectionalLight("sun")
        self.sun.setColor(Vec4(1.4, 1.35, 1.2, 1))
        self.sun.setShadowCaster(True, 4096, 4096)
        self.sunNP = self.render.attachNewNode(self.sun)
        self.sunNP.setHpr(-45, -60, 0)
        self.render.setLight(self.sunNP)

        # Projecteur cinéma sur le panda
        lens = PerspectiveLens()
        lens.setFov(40)
        self.spot = Spotlight("spot")
        self.spot.setLens(lens)
        self.spot.setColor(Vec4(1.8, 1.6, 1.4, 1))
        self.spot.setShadowCaster(True, 2048, 2048)
        self.spotNP = self.render.attachNewNode(self.spot)
        self.spotNP.setPos(0, -5, 8)
        self.spotNP.lookAt(self.pandaActor)
        self.render.setLight(self.spotNP)

        # Activation globale des shaders (obligatoire pour ombres)
        self.render.setShaderAuto()

        # --------------------
        # Brouillard atmosphérique
        # --------------------
        fog = Fog("fog")
        fog.setColor(0.2, 0.25, 0.3)
        fog.setExpDensity(0.015)
        self.render.setFog(fog)

        # --------------------
        # Effet Bloom (compatible toutes versions)
        # --------------------
        self.filters = CommonFilters(self.win, self.cam)
        self.filters.setBloom(
            blend=(0.3, 0.3, 0.3, 0.0),
            desat=0.2,
            intensity=3.0,
            size="medium"
        )

        # --------------------
        # Animation du panda
        # --------------------
        move1 = self.pandaActor.posInterval(
            6, Point3(4, -10, 0), startPos=Point3(-4, 10, 0)
        )
        rot1 = self.pandaActor.hprInterval(
            2, Point3(180, 0, 0)
        )
        move2 = self.pandaActor.posInterval(
            6, Point3(-4, 10, 0)
        )
        rot2 = self.pandaActor.hprInterval(
            2, Point3(0, 0, 0)
        )

        self.pandaSeq = Sequence(
            move1, rot1, move2, rot2,
            name="pandaSeq"
        )
        self.pandaSeq.loop()

        # --------------------
        # Caméra cinématique
        # --------------------
        self.taskMgr.add(self.cinematicCameraTask, "CinematicCamera")

    def cinematicCameraTask(self, task):
        t = task.time

        # Trajectoire dynamique type drone
        radius = 30 + 5 * sin(t * 0.7)
        angle = t * 0.6

        x = radius * sin(angle)
        y = -radius * cos(angle)
        z = 6 + 2 * sin(t * 1.5)

        self.camera.setPos(x, y, z)
        self.camera.lookAt(self.pandaActor)

        # Léger roulis pour effet cinéma
        roll = 5 * sin(t)
        self.camera.setR(roll)

        # Le projecteur suit le panda
        self.spotNP.setPos(
            self.pandaActor.getX(),
            self.pandaActor.getY() - 6,
            10
        )
        self.spotNP.lookAt(self.pandaActor)

        return Task.cont


app = MyApp()
app.run()
