import math
import pygame
import glm
from audio import Audio, Music, PlaySong, handle_audio_events
from graphics import Graphics

from situations.face_test import FaceTest
from situations.french_fry import FrenchFry

pygame.init()

render_resolution = glm.vec2(240, 160)
window_size = render_resolution * 4


GAMEPADS = []

situations = [FaceTest, FrenchFry]


def main():
    pygame.joystick.init()
    graphics = Graphics()
    audio = Audio()

    situation_constructor = situations[1]
    situation = situation_constructor()
    frame_count = 0

    audio.events.append(PlaySong(Music.FRENCH_JAZZ))

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN
                and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)
            ):
                running = False
            elif event.type == pygame.JOYDEVICEADDED:
                gamepad = pygame.joystick.Joystick(event.device_index)
                print("Gamepad connected:", gamepad.get_name())
                GAMEPADS.append(gamepad)
            elif event.type == pygame.JOYDEVICEREMOVED:
                gamepad = pygame.joystick.Joystick(event.device_index)
                print("Gamepad disconnected:", gamepad.get_name())

                GAMEPADS.remove(gamepad)

        situation.step(frame_count, graphics, GAMEPADS)

        handle_audio_events(audio)
        graphics.window.fill((255, 255, 255))
        situation.draw(graphics, frame_count)

        # fps in top left

        # draw a circle at the mouse_position

        pygame.display.update()

        clock.tick(60)

        frame_count += 1

    pygame.quit()


if __name__ == "__main__":
    main()
