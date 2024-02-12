import glm
import pygame


def mouse_pos(window):
    mp = pygame.mouse.get_pos()
    print(mp)
    return glm.vec2(mp)
    # ws = window.get_size()
    # return glm.vec2(mp[0] / ws[0], mp[1] / ws[1])
