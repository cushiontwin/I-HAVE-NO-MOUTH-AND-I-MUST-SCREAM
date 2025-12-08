import pygame
import sys
from tickets import Ticket, TicketGroup, TextSelector
import time
import bomb

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 2300, 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Deck ↔ Hand Groups")
clock = pygame.time.Clock()

deck = TicketGroup()
hand = TicketGroup()


def setup_tickets():
    directions_x  = TextSelector(["LEFT", "RIGHT"], 1)
    directions_y  = TextSelector(["UP", "DOWN"], 1)
    numbers       = TextSelector(["0","1","2","3","4","5","6","7","8","9"], 5)
    commands      = TextSelector(["YES", "NO", "STOP"], 3)
    general       = TextSelector(["NOT", "MODULE", "BUT"], 3)
    communication = TextSelector(["GOOD JOB", "OOPS", "NICE", "THINK", "PLEASE"], 5)
    operations    = TextSelector(["+", "-"], 1)

    text_selectors = [directions_x, directions_y, numbers, commands, general, communication, operations]

    # get a random text to be used for initiating a ticket
    ticket_texts = []
    for selector in text_selectors:
        ticket_texts.extend(selector.get())
    
    for i, ticket_text in enumerate(ticket_texts):
        image_path = r"C:\Users\codyc\Code\.venv\game\ticket_bg.png"
        deck.add(Ticket(image_path, text=f"{ticket_text}"))
setup_tickets()


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = TicketGroup()

    def remove_from_hand(self):
        selected = self.hand.get_selected()
        for ticket in selected:
            ticket.selected = False
            self.hand.remove(ticket)
        return self.hand.tickets
    
    def add_to_hand(self, deck):
        """Queue selected tickets from deck to hand for animation."""
        selected = deck.get_selected()
        if not selected:
            return

        self.hand.clear()  # optional
        HAND_START_POS = (3*WIDTH // 4, HEIGHT - 200)
        HAND_GAP = 120
        PRINTED_TICKET_POS = (WIDTH//2 + 200, 200)

        for i, ticket in enumerate(selected):
            # create new ticket
            new_ticket = ticket.addToHand()
            self.hand.add(new_ticket)
            ticket.selected = False

            # set new ticket's starting position to current deck position
            new_ticket.rect.topleft = ticket.rect.topleft

            # compute target position in hand
            target = (HAND_START_POS[0] + i * HAND_GAP, HAND_START_POS[1])

            # Animate with a pause between each card
            new_ticket.animate_to(
                start_pos=(WIDTH//2 + 200,300),
                target_pos=PRINTED_TICKET_POS,
                duration=0.5,
                delay=i * 0.3  # stagger each card by 0.3s
            )
            new_ticket.animate_to(
                start_pos=(PRINTED_TICKET_POS[0],PRINTED_TICKET_POS[1]),
                target_pos=target,
                duration=0.5,
                delay=i * 0.3  # stagger each card by 0.3s
            )
  

class Diffuser(Player):
    def __init__(self, name):
        super().__init__(name)

class Communicator(Player):
    MAX_SELECTION = 5

    def __init__(self, name):
        super().__init__(name)
    
    def select_ticket(self, pos, groups):
        """Toggle selection on clicked tickets in given TicketGroups."""
        clicked_any = False

        # Count how many are already selected across all groups
        selected_count = sum(len(g.get_selected()) for g in groups)

        for group in groups:
            for ticket in reversed(list(group.tickets.values())):
                if ticket.rect.collidepoint(pos):
                    # ----- LIMIT SELECTION TO 5 -----
                    if not ticket.selected and selected_count >= self.MAX_SELECTION:
                        # Trying to select a 6th one → ignore
                        return

                    ticket.selected = not ticket.selected
                    clicked_any = True
                    break
            if clicked_any:
                break

        # Deselect all if clicked outside
        if not clicked_any:
            for group in groups:
                group.deselect_all()


        

cody = Communicator("Cody")
d = Diffuser("Ben")

def run():
    # Configuration
    start_x, start_y = (50, 50)       # top-left corner
    x_gap, y_gap = (100, 75)          # spacing between tickets
    columns = 5                       # max tickets per row
    rows = 4                          # number of rows
    dt = clock.tick(60) / 1000        # move inside the loop

    # Initialize modules at different positions
    modules = [
        bomb.Module1((3*WIDTH//4, 50)),
        bomb.Module1((3*WIDTH//4+225, 300)),
        bomb.Module2(((3*WIDTH)//4 +325, 50)),
        bomb.ClockModule((3*WIDTH//4, 300), total_time=181)
    ]
    manager = bomb.ModuleManager(modules)

    # Generate positions
    DECK_POSITIONS = [
        (start_x + col * x_gap, start_y + row * y_gap)
        for row in range(rows)
        for col in range(columns)
    ]
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                cody.select_ticket(event.pos, [deck, cody.hand])

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    cody.remove_from_hand()
                    cody.add_to_hand(deck)

        screen.fill((70, 70, 70))

        # Draw tickets
        for t in cody.hand:
            t.update(dt)
            t.draw(screen, t.rect.topleft)

        deck.update(dt)
        deck.draw(screen, positions=DECK_POSITIONS)

        # Draw modules normally
        manager.handle_events(events)
        manager.update(dt)
        manager.draw(screen)

        # Copy modules to the left
        modules_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        modules_surface.fill((0, 0, 0, 0))  # transparent

        # Draw modules onto that surface
        manager.draw(modules_surface)

        # Blit the surface 200 px to the right
        screen.blit(modules_surface, (-WIDTH//2, 0))


        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    run()
