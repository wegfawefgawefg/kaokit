from enum import Enum
import time

import glm
import pygame
from small_ass_cache import AssetCache, loader


class Camera:
    def __init__(self, size):
        self.pos = glm.vec2(0, 0)
        self.size = size

    def set_center(self, pos):
        self.pos = pos - self.size / 2

    def get_center(self):
        return self.pos + self.size / 2


class Graphics:
    def __init__(self):
        self.render_resolution = glm.vec2(1000, 1000) * 1
        self.window_size = self.render_resolution * 1
        self.camera = Camera(glm.vec2(1000, 1000))
        self.camera.set_center(glm.vec2(500, 500))

        self.window = pygame.display.set_mode(self.window_size.to_tuple())
        self.render_surface = pygame.Surface(self.render_resolution.to_tuple())

        pygame.display.set_caption("kaokit")

        self.assets = AssetCache()

    def blit_render_surface_to_window(self):
        self.window.fill((255, 255, 255))
        stretched_surface = pygame.transform.scale(
            self.render_surface, self.window_size
        )
        self.window.blit(stretched_surface, (0, 0))


@loader(pygame.image.load, path="assets/graphics/body_parts")
class BodyParts(Enum):
    FACE_CENTER_NEUTRAL_1 = "face_center_neutral_1.png"
    FACE_CENTER_NEUTRAL_2 = "face_center_neutral_2.png"
    FACE_CENTER_NEUTRAL_3 = "face_center_neutral_3.png"
    OBLONG_HEAD_1 = "oblong_head_1.png"
    OBLONG_HEAD_2 = "oblong_head_2.png"
    OBLONG_HEAD_3 = "oblong_head_3.png"


if __name__ == "__main__":
    graphics = Graphics()

    # face textures
    faces = [
        BodyParts.FACE_CENTER_NEUTRAL_1,
        BodyParts.FACE_CENTER_NEUTRAL_2,
        BodyParts.FACE_CENTER_NEUTRAL_3,
    ]

    # head textures
    heads = [
        BodyParts.OBLONG_HEAD_1,
        BodyParts.OBLONG_HEAD_2,
        BodyParts.OBLONG_HEAD_3,
    ]

    current_head_index = 0
    head_update_interval = 30
    head_horizontal_flip = False

    current_face_index = 0
    face_update_interval = 30
    face_offset = glm.vec2(0, 0)
    face_offset_mag = 40
    face_horizontal_flip = False

    frame_count = 0
    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    exit()

        # arrow keys to move face offset
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            face_offset.x = -face_offset_mag
            face_offset.y = 0
            face_horizontal_flip = False
            head_horizontal_flip = False

        elif keys[pygame.K_RIGHT]:
            face_offset.x = face_offset_mag
            face_offset.y = 0
            face_horizontal_flip = True
            head_horizontal_flip = True
        elif keys[pygame.K_UP]:
            face_offset.y = -face_offset_mag
            face_offset.x = 0
        elif keys[pygame.K_DOWN]:
            face_offset.y = face_offset_mag
            face_offset.x = 0
        elif keys[pygame.K_SPACE]:
            face_offset = glm.vec2(0, 0)

        graphics.render_surface.fill((255, 255, 255))

        screen_center = graphics.render_resolution / 2

        current_head = heads[current_head_index]
        head_texture = graphics.assets.get(current_head)
        head_size = glm.vec2(head_texture.get_size())
        head_center = head_size / 2

        head_pos = screen_center - head_center

        # if head_horizontal_flip:
        #     head_texture = pygame.transform.flip(head_texture, True, False)
        graphics.render_surface.blit(head_texture, head_pos.to_tuple())
        if frame_count % head_update_interval == 0:
            current_head_index = (current_head_index + 1) % len(heads)

        current_face = faces[current_face_index]
        face_texture = graphics.assets.get(current_face)
        face_size = glm.vec2(face_texture.get_size())
        face_center = face_size / 2

        face_pos = screen_center - face_center
        face_pos += face_offset

        if face_horizontal_flip:
            face_texture = pygame.transform.flip(face_texture, True, False)
        graphics.render_surface.blit(face_texture, face_pos.to_tuple())
        if frame_count % face_update_interval == 0:
            current_face_index = (current_face_index + 1) % len(faces)

        graphics.blit_render_surface_to_window()
        pygame.display.update()

        frame_count += 1
