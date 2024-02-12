# def draw(surface):
#     angle = pygame.time.get_ticks() / 1000

#     rect_size = glm.vec2(16, 16)
#     center = render_resolution / 2
#     rect_pos = center - rect_size / 2 + glm.vec2(32, 32)

#     for i in range(3):
#         rot = glm.rotate(glm.vec2(0.0, 1.0), angle + i * 90)
#         rect_pos_rotated = rot @ (rect_pos - center) + rect_pos
#         pygame.draw.rect(
#             surface, (255, 0, 0), (rect_pos_rotated.to_tuple(), rect_size.to_tuple())
#         )

#     pygame.draw.circle(surface, (0, 255, 0), mouse_pos(), 10)
