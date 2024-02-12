from enum import Enum, auto
import random
from glm import vec2
import pygame
from asset_groups import FACES, HEADS


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


class OffsetPart:
    def __init__(self, part, offset):
        self.part = part
        self.offset = offset


class PartGroup:
    def __init__(self):
        self.root_pos = vec2(0, 0)
        self.offset = vec2(0, 0)
        self.offset_parts = []

    def add_offset_part(self, offset_part):
        self.offset_parts.append(offset_part)

    def set_pos(self, pos):
        self.root_pos = pos
        for part_offset in self.parts:
            new_pos = self.root_pos + self.part_offset
            part_offset.part.set_pos(new_pos)

    def step(self, frame_count):
        for offset_part in self.offset_parts:
            offset_part.part.step(frame_count)

    def draw(self, graphics):
        for offset_part in self.offset_parts:
            offset_part.draw(graphics)


class LeftOrRight(Enum):
    Left = auto()
    Right = auto()


"""
seems like theres an element abstraction in here for frame_index, and facing
but also for having a settable offset, left right up down, and analog offset.

"""


def change_facing_based_on_offset(element):
    if element.offset.x < 0:
        element.facing = LeftOrRight.Left
    elif element.offset.x > 0:
        element.facing = LeftOrRight.Right


def change_facing_based_on_velocity(thing):
    if thing.vel.x < 0:
        thing.facing = LeftOrRight.Left
    elif thing.vel.x > 0:
        thing.facing = LeftOrRight.Right


class Element:
    """optional settings:
    - set an asset_group
    - set change_facing_based_on_offset

    MAYBE TODO:
        consider ripping out the change facing based on offset
        let that be a "system" that applies to a list of elements
    """

    def __init__(self):
        self.root_pos = vec2(0, 0)
        self.offset = vec2(0, 0)
        self.frame_index = random.randint(0, 2)
        self.facing = LeftOrRight.Right

        self.change_facing_based_on_offset = False

        self.asset_group = None

    def set_pos(self, pos):
        self.root_pos = pos

    def get_pos(self):
        return self.root_pos + self.offset

    def step(self, frame_count):
        if self.change_facing_based_on_offset:
            if self.offset.x < 0:
                self.facing = LeftOrRight.Left
            elif self.offset.x > 0:
                self.facing = LeftOrRight.Right

        if frame_count % ANIMATION_UPDATE_INTERVAL == 0:
            self.frame_index = (self.frame_index + 1) % 3

    def draw(self, graphics, frame_count):
        asset = self.asset_group[self.frame_index]
        texture = graphics.assets.get(asset)

        if self.facing == LeftOrRight.Left:
            texture = pygame.transform.flip(texture, True, False)
        graphics.window.blit(texture, self.get_pos().to_tuple())


# its some sort of control scheme thing
class DPADOffsetShifter:
    def __init__(self, element, offset_mag) -> None:
        self.element = element
        self.offset_mag = offset_mag

    def left_pressed(self, element) -> None:
        self.element.offset.x = -self.offset_mag
        self.element.offset.y = 0

    def right_pressed(self, element) -> None:
        self.element.offset.x = self.offset_mag
        self.element.offset.y = 0

    def up_pressed(self, element) -> None:
        self.element.offset.y = -self.offset_mag
        self.element.offset.x = 0

    def down_pressed(self, element) -> None:
        self.element.offset.y = self.offset_mag
        self.element.offset.x = 0

    def step(self, gamepads):
        for gamepad in gamepads:
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


# also a control scheme
class AnalogOffsetShifter:
    def __init__(self, element, offset_mag) -> None:
        self.element = element
        self.offset_mag = offset_mag

    def step(self, gamepads):
        for gamepad in gamepads:
            for i in range(gamepad.get_numaxes()):
                axis = gamepad.get_axis(i)
                if i == 0:
                    self.element.x = axis * self.offset_mag
                elif i == 1:
                    self.element.y = axis * self.offset_mag


class Head(Element):
    def __init__(self):
        super().__init__()
        self.asset_group = HEADS


class Face(Element):
    def __init__(self):
        super().__init__()
        self.asset_group = FACES
