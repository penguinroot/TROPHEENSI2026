from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import (
    Vec3, WindowProperties,
    GeomVertexFormat, GeomVertexData,
    Geom, GeomNode, GeomTriangles,
    GeomVertexWriter,
    DirectionalLight, AmbientLight,
    Vec4, Texture, TextureStage, SamplerState,
    Shader
)
from perlin_noise import PerlinNoise
import numpy as np
import math


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
        # COLLISION
        # ======================
        self.playerHeight = 2  # Hauteur du joueur au-dessus du sol
        self.maxSlopeAngle = 45  # Angle maximum en degrés
        self.maxSlope = math.tan(math.radians(self.maxSlopeAngle))

        # ======================
        # CLAVIER
        # ======================
        self.keyMap = {"z": False, "s": False, "q": False, "d": False}
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

        # ======================
        # TEXTURES
        # ======================
        self.loadTextures()
        self.applyTerrainShader()

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
    # COLLISION AMÉLIORÉE
    # =====================================================
    def checkSlope(self, current_pos, target_pos):
        """Vérifie si la pente entre la position actuelle et la cible est franchissable"""
        current_height = self.getGroundHeight(current_pos.x, current_pos.y)
        target_height = self.getGroundHeight(target_pos.x, target_pos.y)
        
        dx = target_pos.x - current_pos.x
        dy = target_pos.y - current_pos.y
        horizontal_distance = math.sqrt(dx*dx + dy*dy)
        
        if horizontal_distance > 0.1:
            slope = (target_height - current_height) / horizontal_distance
            return abs(slope) <= self.maxSlope
        return True

    def checkLateralCollision(self, current_pos, target_pos):
        """Vérifie les collisions latérales avec les pentes raides"""
        # Vérifie plusieurs points entre la position actuelle et la cible
        steps = 3
        for i in range(1, steps + 1):
            t = i / steps
            check_x = current_pos.x + (target_pos.x - current_pos.x) * t
            check_y = current_pos.y + (target_pos.y - current_pos.y) * t
            
            # Vérifie la pente locale autour du point
            height_center = self.getGroundHeight(check_x, check_y)
            
            # Vérifie les points autour pour détecter les murs
            check_radius = 1.0
            for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
                rad = math.radians(angle)
                check_x2 = check_x + math.cos(rad) * check_radius
                check_y2 = check_y + math.sin(rad) * check_radius
                height_around = self.getGroundHeight(check_x2, check_y2)
                
                # Si la différence de hauteur est trop importante, c'est un mur
                if abs(height_around - height_center) > self.playerHeight * 1.5:
                    return False
        return True

    # =====================================================
    # TERRAIN
    # =====================================================
    def generateHeightmap(self):
        size = self.terrainSize
        hm = np.zeros((size, size))
        for y in range(size):
            for x in range(size):
                # Ajout de plusieurs octaves de bruit pour plus de détails
                value = 0
                freq = 1.0
                amp = 1.0
                for _ in range(4):
                    value += self.noise([x / (100 * freq), y / (100 * freq)]) * amp
                    freq *= 2.0
                    amp *= 0.5
                hm[y][x] = value * self.heightScale
        return hm

    def getGroundHeight(self, x, y):
        xi = int(x / self.terrainScale)
        yi = int(y / self.terrainScale)
        if 0 <= xi < self.terrainSize and 0 <= yi < self.terrainSize:
            return self.heightmap[yi][xi]
        return 0

    def generateTerrain(self):
        # Format avec position, normale et coordonnées de texture
        format = GeomVertexFormat.getV3n3t2()
        vdata = GeomVertexData("terrain", format, Geom.UHStatic)

        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        texcoord = GeomVertexWriter(vdata, "texcoord")
        tris = GeomTriangles(Geom.UHStatic)

        size = self.terrainSize

        def height(x, y):
            return self.heightmap[y][x]

        for y in range(size):
            for x in range(size):
                h = height(x, y)
                vertex.addData3(x * self.terrainScale, y * self.terrainScale, h)
                
                # Coordonnées de texture basées sur la position
                texcoord.addData2(x / 10.0, y / 10.0)

                # Calcul normal amélioré
                hl = height(max(x - 1, 0), y)
                hr = height(min(x + 1, size - 1), y)
                hd = height(x, max(y - 1, 0))
                hu = height(x, min(y + 1, size - 1))
                
                # Vecteurs pour le calcul de la normale
                dx = Vec3(2 * self.terrainScale, 0, hr - hl)
                dy = Vec3(0, 2 * self.terrainScale, hu - hd)
                
                n = dx.cross(dy).normalized()
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
    # TEXTURES PROCÉDURALES
    # =====================================================
    def loadTextures(self):
        # Création de textures procédurales simples (en l'absence de fichiers)
        # En pratique, vous chargeriez des fichiers PNG/JPG
        self.textures = {}
        
        # Pour cet exemple, nous créons des textures de base
        # Dans un projet réel, vous chargeriez :
        # self.textures['grass'] = self.loader.loadTexture("textures/grass.jpg")
        # self.textures['rock'] = self.loader.loadTexture("textures/rock.jpg")
        # self.textures['snow'] = self.loader.loadTexture("textures/snow.jpg")
        
        # Création de textures procédurales de base
        self.createProceduralTextures()

    def createProceduralTextures(self):
        """Crée des textures procédurales simples"""
        # Texture herbe (verte)
        grass_data = self.createColorTexture(0.2, 0.6, 0.25)
        self.textures['grass'] = Texture("grass")
        self.textures['grass'].setup2dTexture(64, 64, Texture.T_unsigned_byte, Texture.F_rgb)
        self.textures['grass'].setRamImage(grass_data)
        
        # Texture roche (gris)
        rock_data = self.createColorTexture(0.5, 0.5, 0.5)
        self.textures['rock'] = Texture("rock")
        self.textures['rock'].setup2dTexture(64, 64, Texture.T_unsigned_byte, Texture.F_rgb)
        self.textures['rock'].setRamImage(rock_data)
        
        # Texture neige (blanche)
        snow_data = self.createColorTexture(0.9, 0.9, 0.9)
        self.textures['snow'] = Texture("snow")
        self.textures['snow'].setup2dTexture(64, 64, Texture.T_unsigned_byte, Texture.F_rgb)
        self.textures['snow'].setRamImage(snow_data)
        
        # Configuration du filtrage
        for tex in self.textures.values():
            tex.setMagfilter(SamplerState.FT_linear_mipmap_linear)
            tex.setMinfilter(SamplerState.FT_linear_mipmap_linear)
            tex.setWrapU(SamplerState.WM_repeat)
            tex.setWrapV(SamplerState.WM_repeat)

    def createColorTexture(self, r, g, b):
        """Crée une texture unie avec une couleur donnée"""
        data = bytearray()
        for y in range(64):
            for x in range(64):
                # Ajouter un peu de variation pour éviter l'aspect plat
                var = (x ^ y) & 0x0F
                data.append(int((r * 255 + var) % 255))
                data.append(int((g * 255 + var) % 255))
                data.append(int((b * 255 + var) % 255))
        return bytes(data)

    def applyTerrainShader(self):
        """Applique un shader pour mélanger les textures selon l'altitude et la pente"""
        
        # Créer des TextureStages pour chaque texture
        grass_stage = TextureStage('grass')
        grass_stage.setSort(0)
        self.terrain.setTexture(grass_stage, self.textures['grass'])
        self.terrain.setTexScale(grass_stage, 20, 20)
        
        rock_stage = TextureStage('rock')
        rock_stage.setSort(1)
        self.terrain.setTexture(rock_stage, self.textures['rock'])
        self.terrain.setTexScale(rock_stage, 10, 10)
        
        snow_stage = TextureStage('snow')
        snow_stage.setSort(2)
        self.terrain.setTexture(snow_stage, self.textures['snow'])
        self.terrain.setTexScale(snow_stage, 5, 5)
        
        # Définir un shader simple qui mélange les textures
        # Ce shader mélange les textures en fonction de la hauteur (z)
        vertex_shader = """
        #version 130
        
        uniform mat4 p3d_ModelViewProjectionMatrix;
        in vec4 p3d_Vertex;
        in vec3 p3d_Normal;
        in vec2 p3d_MultiTexCoord0;
        
        out vec3 v_normal;
        out vec2 v_texcoord;
        out float v_height;
        
        void main() {
            gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
            v_normal = normalize(p3d_Normal);
            v_texcoord = p3d_MultiTexCoord0;
            v_height = p3d_Vertex.z;
        }
        """
        
        fragment_shader = """
        #version 130
        
        uniform sampler2D p3d_Texture0;  // grass
        uniform sampler2D p3d_Texture1;  // rock
        uniform sampler2D p3d_Texture2;  // snow
        
        in vec3 v_normal;
        in vec2 v_texcoord;
        in float v_height;
        
        out vec4 frag_color;
        
        void main() {
            // Échantillonner les trois textures
            vec4 grass_color = texture(p3d_Texture0, v_texcoord);
            vec4 rock_color = texture(p3d_Texture1, v_texcoord);
            vec4 snow_color = texture(p3d_Texture2, v_texcoord);
            
            // Calculer la pente (verticalité de la normale)
            float slope = 1.0 - abs(v_normal.y);
            
            // Facteurs de mélange
            float grass_factor = 0.0;
            float rock_factor = 0.0;
            float snow_factor = 0.0;
            
            // Déterminer les zones en fonction de la hauteur et de la pente
            float normalized_height = v_height / 30.0;  // 30 = heightScale * 2
            
            // Haute altitude : neige
            if (normalized_height > 0.7) {
                snow_factor = 1.0;
            }
            // Altitude moyenne : mélange herbe/roche selon la pente
            else if (normalized_height > 0.3) {
                snow_factor = smoothstep(0.7, 0.8, normalized_height);
                rock_factor = slope * (1.0 - snow_factor);
                grass_factor = (1.0 - slope) * (1.0 - snow_factor);
            }
            // Basse altitude : herbe
            else {
                grass_factor = 1.0 - smoothstep(0.2, 0.3, normalized_height);
                rock_factor = slope * (1.0 - grass_factor);
            }
            
            // Normaliser les facteurs
            float total = grass_factor + rock_factor + snow_factor;
            if (total > 0.0) {
                grass_factor /= total;
                rock_factor /= total;
                snow_factor /= total;
            }
            
            // Mélanger les couleurs
            frag_color = grass_color * grass_factor +
                        rock_color * rock_factor +
                        snow_color * snow_factor;
            
            // Ajouter un peu d'ombrage basé sur la normale
            float light = max(0.3, dot(v_normal, normalize(vec3(1, 1, 1))));
            frag_color.rgb *= light;
        }
        """
        
        # Créer et appliquer le shader
        shader = Shader.make(Shader.SL_GLSL, vertex_shader, fragment_shader)
        self.terrain.setShader(shader)

    # =====================================================
    # MOVE + GRAVITÉ + COLLISION
    # =====================================================
    def jump(self):
        if self.velocityZ == 0:
            self.velocityZ = self.jumpForce

    def updateCamera(self, task):
        dt = globalClock.getDt()

        target = Vec3(0, 0, 0)
        if self.keyMap["z"]:
            target.y += self.speed
        if self.keyMap["s"]:
            target.y -= self.speed
        if self.keyMap["q"]:
            target.x -= self.strafeSpeed
        if self.keyMap["d"]:
            target.x += self.strafeSpeed

        self.currentVelocity += (target - self.currentVelocity) * min(dt * 8, 1)
        move = self.currentVelocity * dt
        
        # Calcul de la nouvelle position potentielle
        new_pos = Vec3(
            self.camera.getX() + move.x,
            self.camera.getY() + move.y,
            self.camera.getZ()
        )
        
        # Vérification des collisions
        current_pos = Vec3(self.camera.getX(), self.camera.getY(), 0)
        target_pos = Vec3(new_pos.x, new_pos.y, 0)
        
        can_move = True
        
        # Vérifier la pente
        if not self.checkSlope(current_pos, target_pos):
            can_move = False
        
        # Vérifier les collisions latérales
        if not self.checkLateralCollision(current_pos, target_pos):
            can_move = False
        
        # Appliquer le mouvement si possible
        if can_move:
            self.camera.setX(new_pos.x)
            self.camera.setY(new_pos.y)
        else:
            # Glisser le long de l'obstacle
            # Essayer de se déplacer uniquement en X ou Y
            if self.checkSlope(current_pos, Vec3(new_pos.x, current_pos.y, 0)) and \
               self.checkLateralCollision(current_pos, Vec3(new_pos.x, current_pos.y, 0)):
                self.camera.setX(new_pos.x)
            
            if self.checkSlope(current_pos, Vec3(current_pos.x, new_pos.y, 0)) and \
               self.checkLateralCollision(current_pos, Vec3(current_pos.x, new_pos.y, 0)):
                self.camera.setY(new_pos.y)

        # Gestion de la gravité
        self.velocityZ += self.gravity * dt
        newZ = self.camera.getZ() + self.velocityZ * dt

        ground = self.getGroundHeight(self.camera.getX(), self.camera.getY()) + self.playerHeight
        if newZ < ground:
            newZ = ground
            self.velocityZ = 0

        self.camera.setZ(newZ)

        return Task.cont


app = MyApp()
app.run()