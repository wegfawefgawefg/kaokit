import glm
from small_ass_cache import AssetCache, loader


class Camera:
    def __init__(self, size):
        self.pos = glm.vec2(0, 0)
        self.size = size

    def set_center(self, pos):
        self.pos = pos - self.size / 2

    def get_center(self):
        return self.pos + self.size / 2
