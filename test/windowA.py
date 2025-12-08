import pygame

def run(conn):
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Window A (Shows B's Mouse)")

    clock = pygame.time.Clock()

    mouse_from_B = (0, 0)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        # Check if window B sent new mouse data
        if conn.poll():
            msg_type, pos = conn.recv()
            if msg_type == "mouse":
                mouse_from_B = pos

        screen.fill((20, 20, 60))

        # Draw B's mouse inside window A
        pygame.draw.circle(screen, (0, 255, 0), mouse_from_B, 10)

        pygame.display.flip()
        clock.tick(60)
