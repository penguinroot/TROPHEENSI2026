from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import (
    Vec3, WindowProperties,
    GeomVertexFormat, GeomVertexData,
    Geom, GeomNode, GeomTriangles,
    GeomVertexWriter,
    DirectionalLight, AmbientLight,
    Vec4
)
from perlin_noise import PerlinNoise
import numpy as np


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()

        # ======================
        # LUMIÈRES
        # ======================
        ambient = AmbientLight("ambient")
        ambient.setColor(Vec4(0.4, 0.4, 0.4, 1))
        self.ambientNP = self.render.attachNewNode(ambient)
        self.render.setLight(self.ambientNP)

        sun = DirectionalLight("sun")
        sun.setColor(Vec4(0.9, 0.9, 0.85, 1))
        self.sunNP = self.render.attachNewNode(sun)
        self.sunNP.setHpr(-60, -60, 0)
        self.render.setLight(self.sunNP)

        self.setBackgroundColor(0.53, 0.8, 0.92, 1)

        # ======================
        # CAMERA
        # ======================
        self.camera.setPos(250, 250, 20)

        # ======================
        # SOURIS
        # ======================
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)

        self.mouseSensitivity = 0.15
        self.camYaw = 0
        self.camPitch = 0

        self.centerMouse()

        # ======================
        # MOUVEMENT
        # ======================
        self.speed = 15
        self.strafeSpeed = 12
        self.currentVelocity = Vec3(0, 0, 0)

        # ======================
        # GRAVITÉ
        # ======================
        self.gravity = -30
        self.velocityZ = 0
        self.jumpForce = 10

        # ======================
        # CLAVIER
        # ======================
        self.keyMap = {"forward": False, "backward": False, "left": False, "right": False}
        for k in self.keyMap:
            self.accept(k[0], self.setKey, [k, True])
            self.accept(f"{k[0]}-up", self.setKey, [k, False])

        self.accept("space", self.jump)
        self.accept("escape", self.userExit)

        # ======================
        # TERRAIN
        # ======================
        self.terrainSize = 300
        self.terrainScale = 3
        self.heightScale = 15

        self.noise = PerlinNoise(octaves=5, seed=3)
        self.heightmap = self.generateHeightmap()

        self.terrain = self.generateTerrain()
        self.terrain.reparentTo(self.render)
        self.terrain.setColor(0.2, 0.6, 0.25, 1)  # herbe

        # ======================
        # TASKS
        # ======================
        self.taskMgr.add(self.updateMouseLook, "MouseLook")
        self.taskMgr.add(self.updateCamera, "UpdateCamera")

    # =====================================================
    # INPUT
    # =====================================================
    def setKey(self, key, value):
        self.keyMap[key] = value

    def centerMouse(self):
        x = self.win.getXSize() // 2
        y = self.win.getYSize() // 2
        self.win.movePointer(0, x, y)

    # =====================================================
    # MOUSE LOOK
    # =====================================================
    def updateMouseLook(self, task):
        if self.mouseWatcherNode.hasMouse():
            mw = self.win.getPointer(0)
            dx = mw.getX() - self.win.getXSize() // 2
            dy = mw.getY() - self.win.getYSize() // 2

            self.camYaw -= dx * self.mouseSensitivity
            self.camPitch -= dy * self.mouseSensitivity
            self.camPitch = max(-85, min(85, self.camPitch))

            self.camera.setHpr(self.camYaw, self.camPitch, 0)
            self.centerMouse()

        return Task.cont

    # =====================================================
    # TERRAIN
    # =====================================================
    def generateHeightmap(self):
        size = self.terrainSize
        hm = np.zeros((size, size))
        for y in range(size):
            for x in range(size):
                hm[y][x] = self.noise([x / 100, y / 100]) * self.heightScale
        return hm

    def getGroundHeight(self, x, y):
        xi = int(x / self.terrainScale)
        yi = int(y / self.terrainScale)
        if 0 <= xi < self.terrainSize and 0 <= yi < self.terrainSize:
            return self.heightmap[yi][xi]
        return 0

    def generateTerrain(self):
        format = GeomVertexFormat.getV3n3()
        vdata = GeomVertexData("terrain", format, Geom.UHStatic)

        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        tris = GeomTriangles(Geom.UHStatic)

        size = self.terrainSize

        def height(x, y):
            return self.heightmap[y][x]

        for y in range(size):
            for x in range(size):
                h = height(x, y)
                vertex.addData3(x * self.terrainScale, y * self.terrainScale, h)

                # Calcul normal simple
                hl = height(max(x - 1, 0), y)
                hr = height(min(x + 1, size - 1), y)
                hd = height(x, max(y - 1, 0))
                hu = height(x, min(y + 1, size - 1))

                n = Vec3(hl - hr, hd - hu, 2).normalized()
                normal.addData3(n)

        def vid(x, y):
            return y * size + x

        for y in range(size - 1):
            for x in range(size - 1):
                tris.addVertices(vid(x, y), vid(x + 1, y), vid(x, y + 1))
                tris.addVertices(vid(x + 1, y), vid(x + 1, y + 1), vid(x, y + 1))

        geom = Geom(vdata)
        geom.addPrimitive(tris)
        node = GeomNode("terrain")
        node.addGeom(geom)

        return self.render.attachNewNode(node)

    # =====================================================
    # MOVE + GRAVITÉ
    # =====================================================
    def jump(self):
        if self.velocityZ == 0:
            self.velocityZ = self.jumpForce

    def updateCamera(self, task):
        dt = globalClock.getDt()

        target = Vec3(0, 0, 0)
        if self.keyMap["forward"]:
            target.y += self.speed
        if self.keyMap["backward"]:
            target.y -= self.speed
        if self.keyMap["left"]:
            target.x -= self.strafeSpeed
        if self.keyMap["right"]:
            target.x += self.strafeSpeed

        self.currentVelocity += (target - self.currentVelocity) * min(dt * 8, 1)
        move = self.currentVelocity * dt
        self.camera.setPos(self.camera, move.x, move.y, 0)

        self.velocityZ += self.gravity * dt
        newZ = self.camera.getZ() + self.velocityZ * dt

        ground = self.getGroundHeight(self.camera.getX(), self.camera.getY()) + 2
        if newZ < ground:
            newZ = ground
            self.velocityZ = 0

        self.camera.setZ(newZ)

        return Task.cont


app = MyApp()
app.run()
