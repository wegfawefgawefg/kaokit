from enum import Enum, auto
import random
from glm import vec2
import glm
import pygame
from asset_groups import BIG_SWEATS, BLUSHES, FACES, HEADS


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


class LeftOrRight(Enum):
    Left = auto()
    Right = auto()


"""
seems like theres an element abstraction in here for frame_index, and facing
but also for having a settable offset, left right up down, and analog offset.

"""


def change_facing_based_on_offset(element):
    if element.offset.x < 0:
        element.set_facing(LeftOrRight.Left)
    elif element.offset.x > 0:
        element.set_facing(LeftOrRight.Right)


def change_facing_based_on_velocity(thing):
    if thing.vel.x < 0:
        thing.facing = LeftOrRight.Left
    elif thing.vel.x > 0:
        thing.facing = LeftOrRight.Right


class OffsetPart:
    def __init__(self, part, offset):
        self.part = part
        self.offset = offset


class PositionType(Enum):
    Absolute = auto()
    Relative = auto()


class Element:
    next_id = 0

    def __init__(self):
        self.id = Element.next_id
        Element.next_id += 1

        self.active = True
        self.hidden = False

        self.root_abs_pos = vec2(0, 0)
        self.parent_offset = vec2(0, 0)
        self.offset = vec2(0, 0)
        self.frame_index = random.randint(0, 2)
        self.facing = LeftOrRight.Right
        self.inherit_facing = True

        self.change_facing_based_on_offset = False

        self.asset_group = None
        self.override_texture = None

        self.parent = None
        self.children = []

    def set_abs_pos(self, pos):
        self.root_abs_pos = pos

    def set_offset(self, offset):
        self.offset = offset

    def set_facing(self, facing):
        self.facing = facing
        for child in self.children:
            if child.inherit_facing:
                child.facing = facing

    def get_pos(self):
        if self.parent is None:
            return self.root_abs_pos + self.offset
        else:
            return self.parent.get_pos() + self.parent_offset + self.offset

    def add_child(self, element):
        self.children.append(element)
        element.parent = self

    def remove_child(self, element):
        id = element.id
        for i, child in enumerate(self.children):
            if child.id == id:
                self.children.pop(i)
                return

    def step(self, frame_count):
        if not self.active:
            return

        if frame_count % ANIMATION_UPDATE_INTERVAL == 0:
            self.frame_index = (self.frame_index + 1) % 3

        for child in self.children:
            child.step(frame_count)

    def get_current_texture(self, graphics):
        asset = self.asset_group[self.frame_index]
        texture = graphics.assets.get(asset)
        return texture

    def draw(self, graphics, frame_count):
        if self.hidden:
            return

        texture = self.get_current_texture(graphics)

        if self.facing == LeftOrRight.Left:
            texture = pygame.transform.flip(texture, True, False)
        graphics.window.blit(texture, self.get_pos().to_tuple())

        for child in self.children:
            child.draw(graphics, frame_count)


def set_offset_with_dpad(element: Element, offset_mag: float, gamepads):
    for gamepad in gamepads:
        for i in range(gamepad.get_numhats()):
            hat = gamepad.get_hat(i)
            if hat[0] == 1:
                element.set_offset(vec2(offset_mag, 0))
            elif hat[0] == -1:
                element.set_offset(vec2(-offset_mag, 0))
            elif hat[1] == 1:
                element.set_offset(vec2(0, -offset_mag))
            elif hat[1] == -1:
                element.set_offset(vec2(0, offset_mag))


def set_offset_with_arrow_keys(element: Element, offset_mag: float):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        element.offset.x = -offset_mag
        element.offset.y = 0
    elif keys[pygame.K_RIGHT]:
        element.offset.x = offset_mag
        element.offset.y = 0
    elif keys[pygame.K_UP]:
        element.offset.y = -offset_mag
        element.offset.x = 0
    elif keys[pygame.K_DOWN]:
        element.offset.y = offset_mag
        element.offset.x = 0
    elif keys[pygame.K_SPACE]:
        element.space_pressed()


def set_offset_with_left_analog_stick(element: Element, offset_mag: float, gamepads):
    for gamepad in gamepads:
        for i in range(gamepad.get_numaxes()):
            axis = gamepad.get_axis(i)
            if i == 0:
                element.offset.x = axis * offset_mag
            elif i == 1:
                element.offset.y = axis * offset_mag


def offset_lookat(element, offset_mag: float, target):
    if not target:
        return
    pos_without_offset = element.get_pos() - element.offset
    to_target = glm.normalize(target.pos - pos_without_offset)
    element.set_offset(to_target * offset_mag)
