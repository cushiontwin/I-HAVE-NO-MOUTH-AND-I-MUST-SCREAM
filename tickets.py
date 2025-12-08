import pygame
from typing import Optional, Dict, List, Tuple, Iterable
import random


class TextSelector:
    def __init__(self, words: list, count: int):
        """
        words: list of possible words
        count: how many to select
        """
        count = min(count, len(words))  # safety
        self.selected = random.sample(words, count)

    def get(self):
        """Return the selected words."""
        return self.selected

    def __repr__(self):
        return f"{self.selected}"
    

class Ticket:
    """Represents a single ticket with an image and selectable state."""

    def __init__(self, image_path: Optional[str] = None, text: Optional[str] = None, font_size: int = 18) -> None:
        if image_path is None:
            raise ValueError("image_path must be provided for a Ticket")

        self.image: pygame.Surface = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 3)
        self.original_image = self.image.copy()  # keep original for redrawing text

        self.rect: pygame.Rect = self.image.get_rect()
        self.selected: bool = False
        self.image_path: str = image_path

        # Animation queue
        self._animations = []  # queue of (start_pos, target_pos, duration, delay)

        # Animation properties
        self._move_start = pygame.Vector2(self.rect.topleft)
        self._move_end = pygame.Vector2(self.rect.topleft)
        self._move_duration = 0
        self._move_elapsed = 0
        self._moving = False

        # --- Text ---
        self.text = text
        self.font_size = font_size
        # self.font = pygame.font.SysFont(None, font_size)
        self.font = pygame.font.Font(r"C:\Users\codyc\Code\.venv\game\Pixellari.ttf", font_size)

        if text:
            self.set_text(text)

    def set_text(self, text, color=(0,0,0)):
        self.text = text
        self.image = self.original_image.copy()
        text_surf = self.font.render(text, True, color)
        img_rect = self.image.get_rect()
        text_rect = text_surf.get_rect(center=img_rect.center)
        self.image.blit(text_surf, text_rect)

    def animate_to(self, target_pos, duration=0.5, start_pos=None, delay=0.0):
        """Queue an animation."""
        if start_pos is None:
            # if there is a queued animation, start from its end
            if self._animations:
                start_pos = self._animations[-1][1]
            else:
                start_pos = self.rect.topleft
        else:
            start_pos = start_pos
        self._animations.append((start_pos, target_pos, duration, delay))
        print(self._animations)
        if not self._moving:
            self._start_next_animation()

    def _start_next_animation(self):
        if not self._animations:
            self._moving = False
            return

        start, end, duration, delay = self._animations.pop(0)
        if start == None:
            start = self.rect.topleft
        self._move_start = pygame.Vector2(start)
        self._move_end = pygame.Vector2(end)
        self._move_duration = max(duration, 0.0001)
        self._delay = delay
        self._move_elapsed = 0
        self._moving = True

    def update(self, dt):
        if not self._moving:
            return

        # handle delay
        if self._delay > 0:
            self._delay -= dt
            if self._delay <= 0:
                self._moving = True
            else:
                return

        # animate
        self._move_elapsed += dt
        t = min(self._move_elapsed / self._move_duration, 1)
        eased_t = t * t * (3 - 2 * t)  # smoothstep
        new_pos = self._move_start.lerp(self._move_end, eased_t)
        self.rect.topleft = (new_pos.x, new_pos.y)

        if t >= 1:
            self._moving = False
            self._start_next_animation()

    def draw(self, surface: pygame.Surface, pos: Tuple[int, int]) -> None:
        
        if not self._moving:
            self.rect.topleft = pos
        surface.blit(self.image, self.rect)
        if self.selected:
            pygame.draw.rect(surface, (255, 255, 0), self.rect.inflate(8, 8), 2)

    def addToHand(self) -> "Ticket":
        new_ticket = Ticket(self.image_path, text=self.text, font_size=self.font_size)
        return new_ticket
    
    def copy(self) -> "Ticket":
        return Ticket(self.image_path, text=self.text, font_size=self.font_size)


# --- TicketGroup Class ---
class TicketGroup:
    """Manages a collection of Ticket instances."""

    def __init__(self) -> None:
        """
        Initialize an empty TicketGroup.
        """
        self.tickets: Dict[int, Ticket] = {}  # key: int, value: Ticket

    def add(self, ticket: Ticket) -> Dict[int, Ticket]:
        """
        Add a ticket to the group.

        Parameters
        ----------
        ticket : Ticket
            Ticket to add.

        Returns
        -------
        dict of int to Ticket
            The current dictionary of tickets.
        """
        self.tickets[len(self.tickets)] = ticket
        return self.tickets

    def clear(self) -> None:
        """Remove all tickets from the group."""
        self.tickets.clear()

    def remove(self, ticket: Ticket) -> Dict[int, Ticket]:
        """
        Remove a specific ticket from the group.

        Parameters
        ----------
        ticket : Ticket
            Ticket to remove.

        Returns
        -------
        dict of int to Ticket
            Updated dictionary of tickets.
        """
        keys_to_remove = [key for key, val in self.tickets.items() if val == ticket]
        for key in keys_to_remove:
            del self.tickets[key]
        return self.tickets
    
    def update(self, dt):
        for ticket in self.tickets.values():
            ticket.update(dt)

    def __iter__(self) -> Iterable[Ticket]:
        """
        Iterate over all tickets in the group.

        Returns
        -------
        iterable of Ticket
            Iterator of tickets.
        """
        return iter(self.tickets.values())

    def get_selected(self) -> List[Ticket]:
        """
        Get all currently selected tickets.

        Returns
        -------
        list of Ticket
            List of selected tickets.
        """
        return [ticket for ticket in self.tickets.values() if ticket.selected]

    def deselect_all(self) -> Dict[int, Ticket]:
        """
        Deselect all tickets in the group.

        Returns
        -------
        dict of int to Ticket
            Updated dictionary of tickets.
        """
        for ticket in self.tickets.values():
            ticket.selected = False
        return self.tickets

    def draw(
        self,
        surface: pygame.Surface,
        start_pos: Tuple[int, int] = (0, 0),
        gap: int = 0,
        positions: Optional[List[Tuple[int, int]]] = None
    ) -> None:
        """
        Draw all tickets in the group on a surface.

        Parameters
        ----------
        surface : pygame.Surface
            Surface to draw tickets on.
        start_pos : tuple of int, optional
            Starting position for linear layout. Default is (0, 0).
        gap : int, optional
            Gap between tickets in linear layout. Default is 0.
        positions : list of tuple of int, optional
            Predefined positions for tickets. Default is None.
        """
        if positions:
            # Use predefined positions (like deck)
            for i, ticket in enumerate(self.tickets.values()):
                pos = positions[i % len(positions)]
                ticket.draw(surface, pos)
        else:
            # Use offset (like hand)
            for i, ticket in enumerate(self.tickets.values()):
                pos = (start_pos[0] + i * gap, start_pos[1])
                ticket.draw(surface, pos)
