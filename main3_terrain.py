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

        # ==================================================
        # LUMIÈRES
        # ==================================================
        ambient = AmbientLight("ambient")
        ambient.setColor(Vec4(0.4, 0.4, 0.4, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        sun = DirectionalLight("sun")
        sun.setColor(Vec4(0.9, 0.9, 0.85, 1))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(-60, -45, 0)
        self.render.setLight(sun_np)

        self.setBackgroundColor(0.53, 0.8, 0.92, 1)

        # ==================================================
        # CAMERA
        # ==================================================
        self.camera.setPos(150, 150, 25)
        self.camYaw = 0
        self.camPitch = 0

        # ==================================================
        # SOURIS
        # ==================================================
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)
        self.mouseSensitivity = 0.15
        self.centerMouse()

        # ==================================================
        # MOUVEMENT
        # ==================================================
        self.speed = 55
        self.gravity = -35
        self.jumpForce = 12
        self.velocityZ = 0

        # ==================================================
        # CLAVIER (ZQSD)
        # ==================================================
        self.keyMap = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False
        }

        self.accept("z", self.setKey, ["forward", True])
        self.accept("z-up", self.setKey, ["forward", False])
        self.accept("s", self.setKey, ["backward", True])
        self.accept("s-up", self.setKey, ["backward", False])
        self.accept("q", self.setKey, ["left", True])
        self.accept("q-up", self.setKey, ["left", False])
        self.accept("d", self.setKey, ["right", True])
        self.accept("d-up", self.setKey, ["right", False])

        self.accept("space", self.jump)
        self.accept("escape", self.userExit)

        # ==================================================
        # TERRAIN
        # ==================================================
        self.terrainSize = 300
        self.terrainScale = 3
        self.heightScale = 20

        self.noise = PerlinNoise(octaves=2, seed=2)
        self.heightmap = self.generateHeightmap()
        self.terrain = self.generateTerrain()
        self.terrain.reparentTo(self.render)
        self.terrain.setColor(0.2, 0.6, 0.25, 1)

        # ==================================================
        # TASKS
        # ==================================================
        self.taskMgr.add(self.updateMouseLook, "MouseLook")
        self.taskMgr.add(self.updatePlayer, "UpdatePlayer")

    # ==================================================
    # INPUT
    # ==================================================
    def setKey(self, key, value):
        self.keyMap[key] = value

    def centerMouse(self):
        self.win.movePointer(
            0,
            self.win.getXSize() // 2,
            self.win.getYSize() // 2
        )

    # ==================================================
    # MOUSE LOOK
    # ==================================================
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

    # ==================================================
    # TERRAIN
    # ==================================================
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

        v = GeomVertexWriter(vdata, "vertex")
        n = GeomVertexWriter(vdata, "normal")
        tris = GeomTriangles(Geom.UHStatic)

        size = self.terrainSize

        def h(x, y):
            return self.heightmap[y][x]

        for y in range(size):
            for x in range(size):
                z = h(x, y)
                v.addData3(x * self.terrainScale, y * self.terrainScale, z)

                hl = h(max(x - 1, 0), y)
                hr = h(min(x + 1, size - 1), y)
                hd = h(x, max(y - 1, 0))
                hu = h(x, min(y + 1, size - 1))

                normal = Vec3(hl - hr, hd - hu, 2).normalized()
                n.addData3(normal)

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

    # ==================================================
    # PLAYER
    # ==================================================
    def jump(self):
        if self.velocityZ == 0:
            self.velocityZ = self.jumpForce

    def updatePlayer(self, task):
        dt = min(globalClock.getDt(), 0.05)

        # Direction
        direction = Vec3(0, 0, 0)
        if self.keyMap["forward"]:
            direction.y += 1
        if self.keyMap["backward"]:
            direction.y -= 1
        if self.keyMap["left"]:
            direction.x -= 1
        if self.keyMap["right"]:
            direction.x += 1

        if direction.length() > 0:
            direction.normalize()

        move = direction * self.speed * dt
        self.camera.setPos(self.camera, move.x, move.y, 0)

        # Gravité
        self.velocityZ += self.gravity * dt
        newZ = self.camera.getZ() + self.velocityZ * dt

        groundZ = self.getGroundHeight(
            self.camera.getX(),
            self.camera.getY()
        ) + 2.0

        if newZ < groundZ:
            newZ = groundZ
            self.velocityZ = 0

        self.camera.setZ(newZ)

        return Task.cont


app = MyApp()
app.run()
