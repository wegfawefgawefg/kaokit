from enum import Enum
import time

import pygame
from small_ass_cache import AssetCache, loader


# args kwargs pygame.image.load wrapper
def load_image(args, **kwargs):
    return pygame.image.load(args, **kwargs).convert_alpha()


@loader(load_image, path="assets/graphics/body_parts")
class BodyParts(Enum):
    FACE_CENTER_NEUTRAL_1 = "face_center_neutral_1.png"
    FACE_CENTER_NEUTRAL_2 = "face_center_neutral_2.png"
    FACE_CENTER_NEUTRAL_3 = "face_center_neutral_3.png"
    FACE_CENTER_NEUTRAL_BLINK = "face_center_neutral_blink.png"
    OBLONG_HEAD_1 = "oblong_head_1.png"
    OBLONG_HEAD_2 = "oblong_head_2.png"
    OBLONG_HEAD_3 = "oblong_head_3.png"
    BODY_DRINKING_GLASS_LOWERED_1 = "body_drinking_glass_lowered_1.png"
    BODY_DRINKING_GLASS_LOWERED_2 = "body_drinking_glass_lowered_2.png"
    BODY_DRINKING_GLASS_LOWERED_3 = "body_drinking_glass_lowered_3.png"
    BODY_DRINKING_GLASS_MIDDLE_1 = "body_drinking_glass_middle_1.png"
    BODY_DRINKING_GLASS_MIDDLE_2 = "body_drinking_glass_middle_2.png"
    BODY_DRINKING_GLASS_MIDDLE_3 = "body_drinking_glass_middle_3.png"
    BODY_DRINKING_GLASS_RAISED_1 = "body_drinking_glass_raised_1.png"
    BODY_DRINKING_GLASS_RAISED_2 = "body_drinking_glass_raised_2.png"
    BODY_DRINKING_GLASS_RAISED_3 = "body_drinking_glass_raised_3.png"
    BLUSH_1 = "blush_1.png"
    BLUSH_2 = "blush_2.png"
    BLUSH_3 = "blush_3.png"
    BIG_SWEAT_1 = "big_sweat_1.png"
    BIG_SWEAT_2 = "big_sweat_2.png"
    BIG_SWEAT_3 = "big_sweat_3.png"
    WOMAN_FACE_NEUTRAL_1 = "woman_face_1.png"
    WOMAN_FACE_NEUTRAL_2 = "woman_face_2.png"
    WOMAN_FACE_NEUTRAL_3 = "woman_face_3.png"
    WOMAN_FACE_NEUTRAL_BLINK = "woman_face_blink.png"
    UPPER_BODY_FOR_TABLE_LEFT_1 = "upper_body_for_table_left_1.png"
    UPPER_BODY_FOR_TABLE_LEFT_2 = "upper_body_for_table_left_2.png"
    UPPER_BODY_FOR_TABLE_LEFT_3 = "upper_body_for_table_left_3.png"


@loader(load_image, path="assets/graphics/animals")
class Animals(Enum):
    BIRD_1 = "bird_1.png"
    BIRD_2 = "bird_2.png"
    BIRD_3 = "bird_3.png"


@loader(load_image, path="assets/graphics/hair")
class Hair(Enum):
    CURLS_1 = "curls_1.png"
    CURLS_2 = "curls_2.png"
    CURLS_3 = "curls_3.png"
    SPLIT_HAIR_1 = "split_hair_1.png"
    SPLIT_HAIR_2 = "split_hair_2.png"
    SPLIT_HAIR_3 = "split_hair_3.png"


@loader(load_image, path="assets/graphics/props")
class Props(Enum):
    FOOD_TABLE = "food_table.png"
    FRIES_AND_KETCHUP = "fries_and_ketchup.png"
