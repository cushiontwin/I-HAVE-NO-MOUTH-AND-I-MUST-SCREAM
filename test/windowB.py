import pygame

def run(conn):
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Window B (Sends Mouse)")

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        mx, my = pygame.mouse.get_pos()
        # Send mouse pos to window A
        conn.send(("mouse", (mx, my)))     # Send mouse pos to window A

        screen.fill((50, 20, 20))
        pygame.draw.circle(screen, (255, 255, 0), (mx, my), 10)
        pygame.display.flip()

        clock.tick(60)
