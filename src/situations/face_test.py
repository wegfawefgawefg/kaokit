import copy
from enum import Enum, auto
import random
import pygame
from glm import vec2
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
from situations.animation_kit import (
    Blinker,
    Element,
    LeftOrRight,
    OffsetPart,
    change_facing_based_on_offset,
    offset_lookat,
    set_offset_with_arrow_keys,
    set_offset_with_dpad,
    set_offset_with_left_analog_stick,
)

from ._situation import Situation

ANIMATION_UPDATE_INTERVAL = 30


class Bird:
    def __init__(self, pos, speed) -> None:
        self.pos = pos
        self.speed = speed

        self.element = Element()
        self.element.asset_group = BIRD

    def step(self, frame_count) -> None:
        self.pos.x += self.speed
        self.element.set_abs_pos(self.pos)
        self.element.step(frame_count)

    def draw(self, graphics, frame_count) -> None:
        self.element.draw(graphics, frame_count)
        # this_bird = BIRD[self.bird_frame_index]
        # self.texture = graphics.assets.get(this_bird)
        # bird_size = vec2(self.texture.get_size())
        # bird_center = bird_size / 2

        # if frame_count % ANIMATION_UPDATE_INTERVAL == 0:
        #     self.bird_frame_index = (self.bird_frame_index + 1) % len(BIRD)

        # if self.speed < 0:
        #     self.texture = pygame.transform.flip(self.texture, True, False)
        # graphics.window.blit(self.texture, self.pos.to_tuple())


class HairType(Enum):
    NONE = auto()
    CURLS = auto()
    SPLIT = auto()
    CURLS_AND_SPLIT = auto()


class FaceTest(Situation):
    hair_change_delay = 15

    def __init__(self, graphics) -> None:
        screen_center = vec2(graphics.window.get_size()) / 2.0

        ## body configuration
        # head
        self.head = Element()
        self.head.asset_group = HEADS
        head_size = vec2(self.head.get_current_texture(graphics).get_size())
        head_center = head_size / 2
        head_pos = screen_center - head_center
        self.head.set_abs_pos(head_pos)

        # face
        self.face = Element()
        self.face.asset_group = FACES
        self.head.add_child(self.face)
        self.face.parent_offset = vec2(128, 128)

        self.blinker = Blinker()

        # face decorations
        self.sweating = False
        self.sweat = None

        self.blushing = False
        self.blush = None
        # self.blush = Element()
        # self.blush.asset_group = BLUSHES
        # self.face.add_offset_part(OffsetPart(self.blush, vec2(0, 0)))

        self.body = Element()
        self.body.asset_group = DrinkingBodies.GLASS_LOWERED
        self.head.add_child(self.body)
        self.body.parent_offset = vec2(0, head_size.y / 2)

        self.glass_level = 0  # 0 to 100

        self.hair_change_delay = 0
        self.hair_mode = HairType.NONE

        self.upper_hair = Element()
        self.upper_hair.asset_group = CURLS

        self.lower_hair = Element()
        self.lower_hair.asset_group = SPLIT_HAIR

        self.bird = None

    def step(
        self,
        frame_count,
        graphics,
        gamepads,
    ) -> None:
        self.head.step(frame_count)

        for gamepad in gamepads:
            for i in range(gamepad.get_numaxes()):
                # if B is pressed, blush
                if gamepad.get_button(1):
                    if not self.blushing:
                        self.blushing = True
                        blush = Element()
                        blush.asset_group = BLUSHES
                        blush.inherit_facing = False
                        self.face.add_child(blush)
                        self.blush = blush

                # X to sweat
                if gamepad.get_button(2):
                    if not self.sweating:
                        self.sweating = True
                        sweat = Element()
                        sweat.asset_group = BIG_SWEATS
                        sweat.inherit_facing = False
                        self.face.add_child(sweat)
                        self.sweat = sweat

                # select clears blush
                if gamepad.get_button(6):
                    if self.sweating:
                        self.sweating = False
                        self.face.remove_child(self.sweat)
                        self.sweat = None

                    if self.blushing:
                        self.blushing = False
                        self.face.remove_child(self.blush)
                        self.blush = None

                # if y press, spawn a bird
                if gamepad.get_button(3):
                    if self.bird is None:
                        self.bird = Bird(
                            vec2(-256, 0),
                            1,
                        )

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

        self.face.offset = vec2(0, 0)
        set_offset_with_left_analog_stick(self.face, 40, gamepads)
        set_offset_with_arrow_keys(self.face, 40)
        set_offset_with_dpad(self.face, 40, gamepads)

        if self.bird:
            offset_lookat(self.face, 40, self.bird)

        if self.hair_change_delay > 0:
            self.hair_change_delay -= 1

        change_facing_based_on_offset(self.face)

        if self.glass_level < 30:
            self.body.asset_group = DrinkingBodies.GLASS_LOWERED
        elif self.glass_level < 70:
            self.body.asset_group = DrinkingBodies.GLASS_MIDDLE
        else:
            self.body.asset_group = DrinkingBodies.GLASS_RAISED

        if self.bird:
            self.bird.step(frame_count)
            # if bird is off screen, remove it
            bird_size = vec2(self.bird.element.get_current_texture(graphics).get_size())
            if self.bird.pos.x > graphics.render_resolution.x + bird_size.x:
                self.bird = None

    def draw(self, graphics, frame_count) -> None:

        graphics.window.fill((255, 255, 255))

        screen_center = graphics.render_resolution / 2

        self.head.draw(graphics, frame_count)

        # face
        # current_face = FACES[self.current_face_index]
        # if self.blink_timer > 0:
        #     current_face = BodyParts.FACE_CENTER_NEUTRAL_BLINK
        # face_texture = graphics.assets.get(current_face)
        # face_size = vec2(face_texture.get_size())
        # face_center = face_size / 2

        # face_pos = screen_center - face_center
        # face_pos += self.face_offset

        # if self.face_horizontal_flip:
        #     face_texture = pygame.transform.flip(face_texture, True, False)
        # graphics.window.blit(face_texture, face_pos.to_tuple())
        # if self.frame_count % FaceTest.face_update_interval == 0:
        #     self.current_face_index = (self.current_face_index + 1) % len(FACES)

        # hair
        # if self.hair_mode == HairType.CURLS:
        #     current_hair = CURLS[self.current_head_index]
        #     hair_texture = graphics.assets.get(current_hair)
        #     hair_pos = head_pos
        #     graphics.window.blit(hair_texture, hair_pos.to_tuple())
        # elif self.hair_mode == HairType.SPLIT:
        #     current_hair = SPLIT_HAIR[self.current_head_index]
        #     hair_texture = graphics.assets.get(current_hair)
        #     hair_pos = head_pos
        #     graphics.window.blit(hair_texture, hair_pos.to_tuple())
        # elif self.hair_mode == HairType.CURLS_AND_SPLIT:
        #     current_hair = CURLS[self.current_head_index]
        #     hair_texture = graphics.assets.get(current_hair)
        #     hair_pos = head_pos
        #     graphics.window.blit(hair_texture, hair_pos.to_tuple())

        #     current_hair = SPLIT_HAIR[self.current_head_index]
        #     hair_texture = graphics.assets.get(current_hair)
        #     hair_pos = head_pos
        #     graphics.window.blit(hair_texture, hair_pos.to_tuple())

        # # blush
        # current_blush = BLUSHES[self.blush_index]
        # blush_texture = graphics.assets.get(current_blush)
        # blush_size = vec2(blush_texture.get_size())
        # blush_pos = face_pos
        # if self.blushing:
        #     graphics.window.blit(blush_texture, blush_pos.to_tuple())
        #     if self.frame_count % FaceTest.face_update_interval == 0:
        #         self.blush_index = (self.blush_index + 1) % len(BLUSHES)

        # # sweat
        # current_sweat = BIG_SWEATS[self.sweat_index]
        # sweat_texture = graphics.assets.get(current_sweat)
        # sweat_size = vec2(sweat_texture.get_size())
        # sweat_pos = face_pos
        # if self.sweating:
        #     graphics.window.blit(sweat_texture, sweat_pos.to_tuple())
        #     if self.frame_count % FaceTest.face_update_interval == 0:
        #         self.sweat_index = (self.sweat_index + 1) % len(BLUSHES)

        # # body
        # current_body = self.current_body_group[self.current_body_index]
        # body_texture = graphics.assets.get(current_body)
        # body_size = vec2(body_texture.get_size())
        # body_center = body_size / 2

        # body_pos = screen_center - body_center
        # body_pos.y += head_size.y / 2

        # graphics.window.blit(body_texture, body_pos.to_tuple())
        # if self.frame_count % ANIMATION_UPDATE_INTERVAL == 0:
        #     self.current_body_index = (self.current_body_index + 1) % len(
        #         self.current_body_group
        #     )

        if self.bird:
            self.bird.draw(graphics, frame_count)
