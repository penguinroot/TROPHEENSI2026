from perlin_noise import PerlinNoise
import numpy as np
from PIL import Image

width, height = 512, 512
scale = 100.0

noise = PerlinNoise(octaves=6, seed=1)

img = np.zeros((height, width), dtype=np.uint8)

for y in range(height):
    for x in range(width):
        value = noise([x / scale, y / scale])
        value = int((value + 1) * 127.5)  # [-1,1] → [0,255]
        img[y, x] = value

Image.fromarray(img, mode="L").save("perlin.png")