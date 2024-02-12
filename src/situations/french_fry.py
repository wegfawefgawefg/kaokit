import copy
from enum import Enum, auto
import random
import pygame
import glm
from glm import vec2
from asset_groups import (
    BIG_SWEATS,
    BLUSHES,
    FACES,
    HEADS,
    UPPER_BODY_FOR_TABLE_LEFT,
    WOMAN_FACES,
    DrinkingBodies,
)

from assets import BodyParts, Props
from utils import mouse_pos

from ._situation import Situation

ANIMATION_UPDATE_INTERVAL = 30


class Blinker:
    def __init__(self, blink_duration=20, interval=360, variance=120):
        self.blink_duration = blink_duration
        self.interval = interval  # base interval amount
        self.variation = variance  # interval variance

        self.blink_timer = 0  #   counts down during blinking
        self.time_to_next_blink = 0

    def is_blinking(self):
        return self.blink_timer > 0

    def step(self):
        if self.blink_timer > 0:
            self.blink_timer -= 1
        else:
            if self.time_to_next_blink > 0:
                self.time_to_next_blink -= 1
            else:  # blink
                self.blink_timer = self.blink_duration
                self.time_to_next_blink = self.interval + random.randint(
                    0, self.variation
                )


class Part:
    def __init__(self, part, offset):
        self.part = part
        self.offset = offset


class PartsGroup:
    def __init__(self):
        self.pos = vec2(0, 0)
        self.parts = []

    def add_part(self, part):
        self.parts.append(part)

    def set_pos(self, pos):
        self.pos = pos
        for part in self.parts:
            part.set_pos()

    def step(self, frame_count):
        for part in self.parts:
            part.step(frame_count)

    def draw(self, graphics):
        for part in self.parts:
            part.draw(graphics)


class LeftOrRight(Enum):
    Left = auto()
    Right = auto()


class Head:
    def __init__(self):
        self.pos = vec2(0, 0)
        self.vel = vec2(0, 0)
        self.frame_index = random.randint(0, 2)
        self.facing = LeftOrRight.Right

    def set_pos(self, pos):
        self.pos = pos
        self.face.root_pos = pos

    def step(self, frame_count):
        self.pos += self.vel
        if self.vel < 0:
            self.facing = LeftOrRight.Left
        elif self.vel > 0:
            self.facing = LeftOrRight.Right

        if frame_count % ANIMATION_UPDATE_INTERVAL == 0:
            self.frame_index = (self.frame_index + 1) % 3

    def draw(self, graphics, frame_count):
        head = HEADS[self.frame_index]
        texture = graphics.assets.get(head)
        pos = copy.deepcopy(self.pos)

        if self.facing == LeftOrRight.Left:
            texture = pygame.transform.flip(texture, True, False)
        graphics.window.blit(texture, pos.to_tuple())


class Face:
    def __init__(self):
        self.root_pos = vec2(0, 0)
        self.offset = vec2(0, 0)
        self.frame_index = random.randint(0, 2)
        self.facing = LeftOrRight.Right

    def set_pos(self, pos):
        self.root_pos = pos

    def get_pos(self):
        return self.root_pos + self.offset

    def step(self, frame_count):
        if self.offset.x < 0:
            self.facing = LeftOrRight.Left
        elif self.offset.x > 0:
            self.facing = LeftOrRight.Right

        if frame_count % ANIMATION_UPDATE_INTERVAL == 0:
            self.frame_index = (self.frame_index + 1) % 3

        self.face.step(self, frame_count)

    def draw(self, graphics, frame_count):
        face = FACES[self.frame_index]
        texture = graphics.assets.get(face)
        pos = copy.deepcopy(self.pos)
        if offset:
            pos += offset

        if self.facing == LeftOrRight.Left:
            texture = pygame.transform.flip(texture, True, False)
        graphics.window.blit(texture, self.pos.to_tuple())


class FrenchFry(Situation):
    face_offset_mag = 40

    def __init__(self) -> None:
        self.man_tl = vec2(-18, 82)
        self.woman_tl = vec2(548, 112)

        self.current_head_index = 0
        self.head_horizontal_flip = False

        self.current_face_index = 0
        self.face_offset = vec2(0, 0)
        self.face_horizontal_flip = False

        self.current_body_group = None
        self.current_body_index = 0
        self.glass_level = 0  # 0 to 100

        self.blush_index = 0
        self.sweat_index = 0

        self.man_blinker = Blinker()
        self.woman_blinker = Blinker()

        self.blushing = False
        self.sweating = False

    def left_pressed(self) -> None:
        self.face_offset.x = -FrenchFry.face_offset_mag
        self.face_offset.y = 0

    def right_pressed(self) -> None:
        self.face_offset.x = FrenchFry.face_offset_mag
        self.face_offset.y = 0

    def up_pressed(self) -> None:
        self.face_offset.y = -FrenchFry.face_offset_mag
        self.face_offset.x = 0

    def down_pressed(self) -> None:
        self.face_offset.y = FrenchFry.face_offset_mag
        self.face_offset.x = 0

    def space_pressed(self) -> None:
        self.face_offset = vec2(0, 0)

    def step(
        self,
        frame_count,
        graphics,
        gamepads,
    ) -> None:
        # arrow keys to move face offset
        keys = pygame.key.get_pressed()
        # move self.man_tl
        moved = False
        if keys[pygame.K_LEFT]:
            self.man_tl.x -= 1
            moved = True
        if keys[pygame.K_RIGHT]:
            self.man_tl.x += 1
            moved = True
        if keys[pygame.K_UP]:
            self.man_tl.y -= 1
            moved = True
        if keys[pygame.K_DOWN]:
            self.man_tl.y += 1
            moved = True
        if moved:
            print(self.man_tl)

        # 4568 on numpad for woman_tl
        moved = False
        if keys[pygame.K_KP4]:
            self.woman_tl.x -= 1
            moved = True
        if keys[pygame.K_KP6]:
            self.woman_tl.x += 1
            moved = True
        if keys[pygame.K_KP8]:
            self.woman_tl.y -= 1
            moved = True
        if keys[pygame.K_KP5]:
            self.woman_tl.y += 1
            moved = True
        if moved:
            print(self.woman_tl)

        for gamepad in gamepads:
            for i in range(gamepad.get_numaxes()):
                axis = gamepad.get_axis(i)
                if i == 0:
                    self.face_offset.x = axis * FrenchFry.face_offset_mag
                elif i == 1:
                    self.face_offset.y = axis * FrenchFry.face_offset_mag

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

        if self.face_offset.x < 0:
            self.face_horizontal_flip = False
            self.head_horizontal_flip = False
        elif self.face_offset.x > 0:
            self.face_horizontal_flip = True
            self.head_horizontal_flip = True

        self.man_blinker.step()
        self.woman_blinker.step()

        if self.glass_level < 30:
            self.current_body_group = DrinkingBodies.GLASS_LOWERED
        elif self.glass_level < 70:
            self.current_body_group = DrinkingBodies.GLASS_MIDDLE
        else:
            self.current_body_group = DrinkingBodies.GLASS_RAISED

    def draw(self, graphics, frame_count) -> None:
        graphics.window.fill((255, 255, 255))

        screen_center = graphics.render_resolution / 2

        # food table
        food_table_texture = graphics.assets.get(Props.FOOD_TABLE)
        food_table_size = vec2(food_table_texture.get_size())
        food_table_center = food_table_size / 2
        food_table_pos = screen_center - food_table_center

        graphics.window.blit(food_table_texture, food_table_pos.to_tuple())

        # food
        fries_and_ketchup_texture = graphics.assets.get(Props.FRIES_AND_KETCHUP)
        fries_and_ketchup_size = vec2(fries_and_ketchup_texture.get_size())
        fries_and_ketchup_center = fries_and_ketchup_size / 2
        fries_and_ketchup_pos = screen_center - fries_and_ketchup_center

        graphics.window.blit(
            fries_and_ketchup_texture, fries_and_ketchup_pos.to_tuple()
        )

        # man on left

        # head
        current_head = HEADS[self.current_head_index]
        head_texture = graphics.assets.get(current_head)
        head_size = vec2(head_texture.get_size())

        head_pos = copy.deepcopy(self.man_tl)

        # if head_horizontal_flip:
        #     head_texture = pygame.transform.flip(head_texture, True, False)
        graphics.window.blit(head_texture, head_pos.to_tuple())
        if frame_count % ANIMATION_UPDATE_INTERVAL == 0:
            self.current_head_index = (self.current_head_index + 1) % len(HEADS)

        # face
        current_face = FACES[self.current_face_index]
        if self.man_blinker.is_blinking():
            current_face = BodyParts.FACE_CENTER_NEUTRAL_BLINK
        face_texture = graphics.assets.get(current_face)
        face_size = vec2(face_texture.get_size())
        face_center = face_size / 2

        face_pos = head_pos + head_size / 2 - face_size / 2
        face_pos += self.face_offset

        if self.face_horizontal_flip:
            face_texture = pygame.transform.flip(face_texture, True, False)
        graphics.window.blit(face_texture, face_pos.to_tuple())
        if frame_count % ANIMATION_UPDATE_INTERVAL == 0:
            self.current_face_index = (self.current_face_index + 1) % len(FACES)

        # blush
        current_blush = BLUSHES[self.blush_index]
        blush_texture = graphics.assets.get(current_blush)
        blush_size = vec2(blush_texture.get_size())
        blush_pos = face_pos
        if self.blushing:
            graphics.window.blit(blush_texture, blush_pos.to_tuple())
            if frame_count % ANIMATION_UPDATE_INTERVAL == 0:
                self.blush_index = (self.blush_index + 1) % len(BLUSHES)

        # sweat
        current_sweat = BIG_SWEATS[self.sweat_index]
        sweat_texture = graphics.assets.get(current_sweat)
        sweat_size = vec2(sweat_texture.get_size())
        sweat_pos = face_pos
        if self.sweating:
            graphics.window.blit(sweat_texture, sweat_pos.to_tuple())
            if frame_count % ANIMATION_UPDATE_INTERVAL == 0:
                self.sweat_index = (self.sweat_index + 1) % len(BLUSHES)

        # body
        current_body = UPPER_BODY_FOR_TABLE_LEFT[self.current_body_index]
        body_texture = graphics.assets.get(current_body)
        body_size = vec2(body_texture.get_size())
        body_center = body_size / 2

        body_pos = head_pos
        body_pos += vec2(141, 154)
        # body_pos += mouse_pos(graphics.window)
        body_pos.y += head_size.y / 2

        graphics.window.blit(body_texture, body_pos.to_tuple())
        if frame_count % ANIMATION_UPDATE_INTERVAL == 0:
            self.current_body_index = (self.current_body_index + 1) % len(
                self.current_body_group
            )

        # woman on right
        # head
        current_head = HEADS[self.current_head_index]
        head_texture = graphics.assets.get(current_head)
        head_size = vec2(head_texture.get_size())

        head_pos = copy.deepcopy(self.woman_tl)
        # head_pos += mouse_pos(graphics.window)

        head_texture = pygame.transform.flip(head_texture, True, False)
        graphics.window.blit(head_texture, head_pos.to_tuple())
        if frame_count % ANIMATION_UPDATE_INTERVAL == 0:
            self.current_head_index = (self.current_head_index + 1) % len(HEADS)

        # body
        current_body = UPPER_BODY_FOR_TABLE_LEFT[self.current_body_index]
        body_texture = graphics.assets.get(current_body)
        body_size = vec2(body_texture.get_size())
        body_center = body_size / 2

        body_pos = head_pos + vec2(176, 390)
        # body_pos += mouse_pos(graphics.window)

        body_texture = pygame.transform.flip(body_texture, True, False)
        graphics.window.blit(body_texture, body_pos.to_tuple())

        # face
        current_face = WOMAN_FACES[self.current_face_index]
        if self.woman_blinker.is_blinking():
            current_face = BodyParts.WOMAN_FACE_NEUTRAL_BLINK
        face_texture = graphics.assets.get(current_face)
        face_size = vec2(face_texture.get_size())

        face_pos = head_pos + head_size / 2 - face_size / 2
        face_pos += self.face_offset

        if self.face_horizontal_flip:
            face_texture = pygame.transform.flip(face_texture, True, False)
        graphics.window.blit(face_texture, face_pos.to_tuple())
