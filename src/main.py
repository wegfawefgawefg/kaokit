import math
import pygame
import glm

pygame.init()

render_resolution = glm.vec2(240, 160)
window_size = render_resolution * 4


def mouse_pos():
    return glm.vec2(pygame.mouse.get_pos()) / window_size * render_resolution


def draw(surface):
    angle = pygame.time.get_ticks() / 1000

    rect_size = glm.vec2(16, 16)
    center = render_resolution / 2
    rect_pos = center - rect_size / 2 + glm.vec2(32, 32)

    for i in range(3):
        rot = glm.rotate(glm.vec2(0.0, 1.0), angle + i * 90)
        rect_pos_rotated = rot @ (rect_pos - center) + rect_pos
        pygame.draw.rect(
            surface, (255, 0, 0), (rect_pos_rotated.to_tuple(), rect_size.to_tuple())
        )

    pygame.draw.circle(surface, (0, 255, 0), mouse_pos(), 10)


def main():
    window = pygame.display.set_mode(window_size.to_tuple())
    render_surface = pygame.Surface(render_resolution.to_tuple())

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN
                and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)
            ):
                running = False

        render_surface.fill((0, 0, 0))

        draw(render_surface)

        stretched_surface = pygame.transform.scale(render_surface, window_size)
        window.blit(stretched_surface, (0, 0))
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
