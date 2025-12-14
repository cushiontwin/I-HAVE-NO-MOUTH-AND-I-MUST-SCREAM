import pygame
from tickets import TicketGroup, setup_tickets
from utilities import *
from spline_test import *
import bomb

pygame.init()


WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
animations = AnimationManager()

DECK_POS = (50, 50)
HAND_POS = (WIDTH//2, 600)
GAP = 40

b1 = bomb.Module1((WIDTH//2-150, 50))
modules = [
    b1
]
bomb_manager = bomb.ModuleManager(modules)


class Deck:
    HOVER_SCALE = 1.2  # how much to enlarge on hover
    def __init__(self):
        super().__init__()
        self.deck = setup_tickets()
        self.gap_x = 6
        self.gap_y = 10
        self.col = 10
        self.mid_offset = ((self.col-1) * (self.gap_x + self.deck.sprites()[0].rect.width))//2
        
        self.button_position = (WIDTH//2,HEIGHT-100)
        self.visibilty_button = Button(
            image_path=r"C:\Users\codyc\Code\.venv\game\confirm_button.png",   # Path to your button image
            pos=self.button_position,            # Top-left position
            scale=2,                   # Scale factor
            name="show_hide",
            on_click_func=self.toggle_visibilty,
        )
        self.visibilty_button.pos = (self.visibilty_button.pos[0] - self.visibilty_button.rect.width//2, self.visibilty_button.rect.    height)
        self.visible = False

        self.visibile_positions = self.setup_visible((WIDTH//2-self.mid_offset,100), 2, 10, 10, 10)

    def show(self):
        for i, ticket in enumerate(self.deck.sprites()):
            animations.add(
                ticket,
                [(100,500), (100,400), self.visibile_positions[i]],
                duration=1,
                delay=0.05*i,
                easing=ease_in_out_quint,
                degree=2,
                lean=True,
            )

    def hide(self):
        for i, ticket in enumerate(self.deck.sprites()):
            animations.add(
                ticket,
                [self.visibile_positions[i], (100,400), (100,500)],
                duration=1,
                delay=0.05*i,
                easing=ease_in_out_quint,
                degree=2,
                lean=True,
            )
        
    def toggle_visibilty(self):
        if self.visible:
            self.show()
        else:
            self.hide()
        self.visible = not self.visible
    
    def setup_visible(self, start_pos=(0,0), rows=1, cols=1, gap_x=6, gap_y=10):
        positions = []
        for idx, sprite in enumerate(self.deck):
            row = idx // cols
            col = idx % cols
            positions.append((start_pos[0] + col * (gap_x + sprite.rect.width),
                              start_pos[1] + row * (gap_y + sprite.rect.height)))
        return positions
    
    def draw_ticket_with_hover(self, screen, ticket, mouse_pos):
        """
        Draw a ticket with hover/selected scaling.
        Selected tickets stay enlarged even when not hovered.
        """
        HOVER_SCALE = 1.2

        hovered = ticket.rect.collidepoint(mouse_pos)
        enlarged = hovered or getattr(ticket, "selected", False)

        if enlarged:
            orig_center = ticket.rect.center
            scaled_image = pygame.transform.smoothscale(
                ticket.image,
                (
                    int(ticket.rect.width * HOVER_SCALE),
                    int(ticket.rect.height * HOVER_SCALE)
                )
            )
            scaled_rect = scaled_image.get_rect(center=orig_center)
            screen.blit(scaled_image, scaled_rect)
        else:
            screen.blit(ticket.image, ticket.rect)

    def draw(self, screen: pygame.Surface):
        mx, my = pygame.mouse.get_pos()

        for ticket in self.deck.sprites():
            self.draw_ticket_with_hover(screen, ticket, (mx, my))

        screen.blit(self.visibilty_button.image, self.visibilty_button.rect)

    # def draw(self, screen: pygame.Surface):
    #     """Draw all tickets and the button to the screen."""
    #     # Draw tickets
    #     for i, ticket in enumerate(self.deck.sprites()):
    #         # if self.visible:
    #         screen.blit(ticket.image, ticket.rect.topleft)
    #         # else:
    #         #     screen.blit(ticket.image, ticket.rect)
    #             # pass
    #     screen.blit(self.visibilty_button.image, self.visibilty_button.rect)
            

class Player:
    # TODO:
    # - When deleting from discard, theres a tiny flash before it does so.

    def __init__(self):
        self.hand = TicketGroup()
        self.discard = TicketGroup()
        self.discard_pile_pos = (WIDTH-100, 500)
        
    def add_tickets(self, tickets, start_pos, hand_pos):
        tickets = TicketGroup([ticket.copy() for ticket in tickets.sprites()])

        self.animate_to_discard(self.hand)
        tickets = tickets.sprites()  # list of actual Ticket objects
        stacking_offset = 10
        gap = 12 + tickets[0].rect.width
        dur = .5
        delay_ticket = 0.25

        gap = 12 + tickets[0].rect.width
        num_cards = len(tickets)
        card_width = tickets[0].rect.width
        total_width = (num_cards - 1) * (gap) + card_width
        start_x = HAND_POS[0] - total_width // 2

        for i, ticket in enumerate(tickets):
            # Create a temporary visual copy for animation
            lift_pos = (start_pos[0], start_pos[1] - 250 + i * stacking_offset)
            # hand_target = (hand_pos[0] + i * gap, hand_pos[1] - ticket.rect.height)
            hand_target = (start_x + i * gap, HAND_POS[1] - ticket.rect.height)

            # Step 1: move up
            animations.add(
                ticket,
                [start_pos, lift_pos],
                duration=dur,
                delay=delay_ticket * i,
                easing=ease_out_quart,
                degree=1,
            )
            self.hand.add(ticket)   

            animations.add(
                ticket,
                [lift_pos, (start_pos[0]+200, start_pos[1]-300), hand_target],
                duration=dur*2,
                delay=(delay_ticket*i)+dur,
                easing=ease_in_out_quint,
                degree=2,
                lean=True,
            )

    def animate_to_discard(self, tickets, discard_pos=(200, 200)):
        """Animate tickets from hand to discard without removing originals immediately."""

        tickets = tickets.sprites()
        # tickets = TicketGroup([ticket.copy() for ticket in tickets.sprites()])
        dur = 1
        delay_ticket = 0.25



        for i, ticket in enumerate(tickets):
            player.discard.add(ticket)
            player.hand.remove(ticket)
            animations.add(
                ticket,
                [ticket.rect.center, self.discard_pile_pos],
                duration=dur,
                delay=delay_ticket * i,
                easing=ease_out_quart,
                degree=1,
                lean=True
            )
        print(self.hand, self.discard)

       

class RectSprite(pygame.sprite.Sprite):
    def __init__(self, width, height, color, pos=(0,0)):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)

rect_sprite = RectSprite(50, 70, (255, 0, 0), pos=(80, 480))
clip = pygame.sprite.Group(rect_sprite)


# ─────────────────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────────────────
player = Player()
d = Deck()





running = True
while running:
    dt = clock.tick(60) / 1000
    screen.fill((35, 35, 35))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # LEFT CLICK → select/deselect tickets
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            clicked_any = False

            if d.visibilty_button.rect.collidepoint(mouse_pos):
                d.toggle_visibilty()
            for ticket in d.deck:
                if ticket.rect.collidepoint(mouse_pos):
                    ticket.on_click()
                    clicked_any = True

            if not clicked_any:
                d.deck.deselect_all()
                # player.hand.deselect_all()
        bomb_manager.handle_events(event)

        # ENTER → move selected deck tickets to player's hand
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                selected = TicketGroup(d.deck.get_selected())
                # selected = TicketGroup([ticket.copy() for ticket in selected])

                # Animate selected tickets to hand
                player.add_tickets(selected, start_pos=(100,540), hand_pos=HAND_POS)
                d.deck.deselect_all()


    animations.update(dt)
    bomb_manager.update(dt)

    bomb_manager.draw(screen)
    player.hand.draw(screen)
    player.discard.draw(screen)
    d.draw(screen)

    clip.draw(screen)
    pygame.display.flip()

pygame.quit()
