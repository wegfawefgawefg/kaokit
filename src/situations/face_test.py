import copy
from enum import Enum, auto
import random
import pygame
import glm
from asset_groups import (
    BIG_SWEATS,
    BIRD,
    BLUSHES,
    CURLS,
    FACES,
    HEADS,
    SPLIT_HAIR,
    DrinkingBodies,
)

from assets import BodyParts

from ._situation import Situation

ANIMATION_UPDATE_INTERVAL = 30


class Bird:
    def __init__(self, pos, speed) -> None:
        self.pos = pos
        self.speed = speed

        self.bird_frame_index = 0

    def step(self, frame_count) -> None:
        self.pos.x += self.speed

    def draw(self, graphics, frame_count) -> None:
        this_bird = BIRD[self.bird_frame_index]
        self.texture = graphics.assets.get(this_bird)
        bird_size = glm.vec2(self.texture.get_size())
        bird_center = bird_size / 2

        if frame_count % ANIMATION_UPDATE_INTERVAL == 0:
            self.bird_frame_index = (self.bird_frame_index + 1) % len(BIRD)

        if self.speed < 0:
            self.texture = pygame.transform.flip(self.texture, True, False)
        graphics.window.blit(self.texture, self.pos.to_tuple())


class HairType(Enum):
    NONE = auto()
    CURLS = auto()
    SPLIT = auto()
    CURLS_AND_SPLIT = auto()


class FaceTest(Situation):
    face_offset_mag = 40
    head_update_interval = 30
    face_update_interval = 30

    base_blink_interval = 360
    blink_interval_variation = 120

    blink_duration = 20
    hair_change_delay = 15

    def __init__(self) -> None:
        self.current_head_index = 0
        self.head_horizontal_flip = False

        self.current_face_index = 0
        self.face_offset = glm.vec2(0, 0)
        self.face_horizontal_flip = False

        self.current_body_group = None
        self.current_body_index = 0
        self.glass_level = 0  # 0 to 100

        self.blush_index = 0
        self.sweat_index = 0

        self.time_to_next_blink = copy.copy(FaceTest.base_blink_interval)
        self.blink_timer = 0

        self.blushing = False
        self.sweating = False

        self.frame_count = 0

        self.hair_mode = HairType.NONE
        self.hair_change_delay = 0

        self.bird = None

    def left_pressed(self) -> None:
        self.face_offset.x = -FaceTest.face_offset_mag
        self.face_offset.y = 0

    def right_pressed(self) -> None:
        self.face_offset.x = FaceTest.face_offset_mag
        self.face_offset.y = 0

    def up_pressed(self) -> None:
        self.face_offset.y = -FaceTest.face_offset_mag
        self.face_offset.x = 0

    def down_pressed(self) -> None:
        self.face_offset.y = FaceTest.face_offset_mag
        self.face_offset.x = 0

    def space_pressed(self) -> None:
        self.face_offset = glm.vec2(0, 0)

    def step(
        self,
        graphics,
        gamepads,
    ) -> None:
        # arrow keys to move face offset
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.left_pressed()
        elif keys[pygame.K_RIGHT]:
            self.right_pressed()
        elif keys[pygame.K_UP]:
            self.up_pressed()
        elif keys[pygame.K_DOWN]:
            self.down_pressed()
        elif keys[pygame.K_SPACE]:
            self.space_pressed()

        for gamepad in gamepads:
            for i in range(gamepad.get_numaxes()):
                axis = gamepad.get_axis(i)
                if i == 0:
                    self.face_offset.x = axis * FaceTest.face_offset_mag
                elif i == 1:
                    self.face_offset.y = axis * FaceTest.face_offset_mag

                # if B is pressed, blush
                if gamepad.get_button(1):
                    if not self.blushing:
                        self.blushing = True

                # X to sweat
                if gamepad.get_button(2):
                    if not self.sweating:
                        self.sweating = True

                # select clears blush
                if gamepad.get_button(6):
                    self.blushing = False
                    self.sweating = False

                # if y press, spawn a bird
                if gamepad.get_button(3):
                    if self.bird is None:
                        self.bird = Bird(
                            glm.vec2(-256, 0),
                            1,
                        )

            # dpad
            for i in range(gamepad.get_numhats()):
                hat = gamepad.get_hat(i)
                if hat[0] == 1:
                    self.right_pressed()
                elif hat[0] == -1:
                    self.left_pressed()
                elif hat[1] == 1:
                    self.up_pressed()
                elif hat[1] == -1:
                    self.down_pressed()

            # glass level is set by right trigger
            self.glass_level = int((gamepad.get_axis(5) + 1) * 50)

            # right bumper to change hair
            if gamepad.get_button(5) and self.hair_change_delay == 0:
                # if none is selected, go to curls
                if self.hair_mode == HairType.NONE:
                    self.hair_mode = HairType.CURLS
                elif self.hair_mode == HairType.CURLS:
                    self.hair_mode = HairType.SPLIT
                elif self.hair_mode == HairType.SPLIT:
                    self.hair_mode = HairType.CURLS_AND_SPLIT
                elif self.hair_mode == HairType.CURLS_AND_SPLIT:
                    self.hair_mode = HairType.NONE

                self.hair_change_delay = FaceTest.hair_change_delay

        if self.hair_change_delay > 0:
            self.hair_change_delay -= 1

        if self.face_offset.x < 0:
            self.face_horizontal_flip = False
            self.head_horizontal_flip = False
        elif self.face_offset.x > 0:
            self.face_horizontal_flip = True
            self.head_horizontal_flip = True

        if self.blink_timer > 0:
            self.blink_timer -= 1
        else:
            if self.time_to_next_blink > 0:
                self.time_to_next_blink -= 1
            else:  # blink
                self.blink_timer = FaceTest.blink_duration
                self.time_to_next_blink = FaceTest.base_blink_interval + random.randint(
                    0, FaceTest.blink_interval_variation
                )

        if self.glass_level < 30:
            self.current_body_group = DrinkingBodies.GLASS_LOWERED
        elif self.glass_level < 70:
            self.current_body_group = DrinkingBodies.GLASS_MIDDLE
        else:
            self.current_body_group = DrinkingBodies.GLASS_RAISED

        if self.bird:
            self.bird.step(self.frame_count)
            # if bird is off screen, remove it
            if self.bird.pos.x > graphics.render_resolution.x + 256:
                self.bird = None

    def draw(self, graphics) -> None:

        graphics.window.fill((255, 255, 255))

        screen_center = graphics.render_resolution / 2

        # head
        current_head = HEADS[self.current_head_index]
        head_texture = graphics.assets.get(current_head)
        head_size = glm.vec2(head_texture.get_size())
        head_center = head_size / 2

        head_pos = screen_center - head_center

        # if head_horizontal_flip:
        #     head_texture = pygame.transform.flip(head_texture, True, False)
        graphics.window.blit(head_texture, head_pos.to_tuple())
        if self.frame_count % ANIMATION_UPDATE_INTERVAL == 0:
            self.current_head_index = (self.current_head_index + 1) % len(HEADS)

        # face
        current_face = FACES[self.current_face_index]
        if self.blink_timer > 0:
            current_face = BodyParts.FACE_CENTER_NEUTRAL_BLINK
        face_texture = graphics.assets.get(current_face)
        face_size = glm.vec2(face_texture.get_size())
        face_center = face_size / 2

        face_pos = screen_center - face_center
        face_pos += self.face_offset

        if self.face_horizontal_flip:
            face_texture = pygame.transform.flip(face_texture, True, False)
        graphics.window.blit(face_texture, face_pos.to_tuple())
        if self.frame_count % FaceTest.face_update_interval == 0:
            self.current_face_index = (self.current_face_index + 1) % len(FACES)

        # hair
        if self.hair_mode == HairType.CURLS:
            current_hair = CURLS[self.current_head_index]
            hair_texture = graphics.assets.get(current_hair)
            hair_pos = head_pos
            graphics.window.blit(hair_texture, hair_pos.to_tuple())
        elif self.hair_mode == HairType.SPLIT:
            current_hair = SPLIT_HAIR[self.current_head_index]
            hair_texture = graphics.assets.get(current_hair)
            hair_pos = head_pos
            graphics.window.blit(hair_texture, hair_pos.to_tuple())
        elif self.hair_mode == HairType.CURLS_AND_SPLIT:
            current_hair = CURLS[self.current_head_index]
            hair_texture = graphics.assets.get(current_hair)
            hair_pos = head_pos
            graphics.window.blit(hair_texture, hair_pos.to_tuple())

            current_hair = SPLIT_HAIR[self.current_head_index]
            hair_texture = graphics.assets.get(current_hair)
            hair_pos = head_pos
            graphics.window.blit(hair_texture, hair_pos.to_tuple())

        # blush
        current_blush = BLUSHES[self.blush_index]
        blush_texture = graphics.assets.get(current_blush)
        blush_size = glm.vec2(blush_texture.get_size())
        blush_pos = face_pos
        if self.blushing:
            graphics.window.blit(blush_texture, blush_pos.to_tuple())
            if self.frame_count % FaceTest.face_update_interval == 0:
                self.blush_index = (self.blush_index + 1) % len(BLUSHES)

        # sweat
        current_sweat = BIG_SWEATS[self.sweat_index]
        sweat_texture = graphics.assets.get(current_sweat)
        sweat_size = glm.vec2(sweat_texture.get_size())
        sweat_pos = face_pos
        if self.sweating:
            graphics.window.blit(sweat_texture, sweat_pos.to_tuple())
            if self.frame_count % FaceTest.face_update_interval == 0:
                self.sweat_index = (self.sweat_index + 1) % len(BLUSHES)

        # body
        current_body = self.current_body_group[self.current_body_index]
        body_texture = graphics.assets.get(current_body)
        body_size = glm.vec2(body_texture.get_size())
        body_center = body_size / 2

        body_pos = screen_center - body_center
        body_pos.y += head_size.y / 2

        graphics.window.blit(body_texture, body_pos.to_tuple())
        if self.frame_count % ANIMATION_UPDATE_INTERVAL == 0:
            self.current_body_index = (self.current_body_index + 1) % len(
                self.current_body_group
            )

        if self.bird:
            self.bird.draw(graphics, self.frame_count)

        self.frame_count += 1
