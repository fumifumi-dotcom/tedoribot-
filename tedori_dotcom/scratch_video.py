import imageio
from PIL import Image, ImageDraw
import numpy as np
import os

frames = []
for i in range(30):
    img = Image.new('RGB', (400, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 50 + i*10, 50 + i*10], fill=(255, 0, 0))
    # Convert PIL to numpy
    frames.append(np.array(img))

imageio.mimwrite('test_video.mp4', frames, fps=15, codec='libx264')
print("Successfully wrote test_video.mp4")
