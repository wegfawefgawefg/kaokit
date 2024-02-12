from enum import Enum
import time

import glm
import pygame
from small_ass_cache import AssetCache, loader

from camera import Camera


class Graphics:
    def __init__(self):
        self.render_resolution = glm.vec2(1000, 1000) * 1
        self.window_size = self.render_resolution * 1
        self.camera = Camera(glm.vec2(1000, 1000))
        self.camera.set_center(glm.vec2(500, 500))

        self.window = pygame.display.set_mode(
            self.window_size.to_tuple(), flags=pygame.HWSURFACE
        )

        pygame.display.set_caption("kaokit")

        self.assets = AssetCache()
