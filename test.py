from __future__ import annotations
from dataclasses import dataclass
import time

from abc import ABC, abstractmethod

class Player(ABC):
    """
    Base class for all players in the game.
    Defines the interface that all player roles must implement.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def take_turn(self, game_state: dict) -> None:
        """
        Perform the player's turn.
        Must be implemented by subclasses.
        """
        pass

    def __str__(self):
        return f"Player: {self.name}"


class  Ticket:
    def __init__(self, name: str, image_path: str = None,):
        self.name = name
        self.image_path = image_path

    def __str__(self):
        return f"Ticket(name={self.name}, image={self.image_path})"
    
    @classmethod
    def from_dict(cls, ticket_dict: dict):
        """
        Factory method: create a Ticket from a dictionary.
        Expected keys: 'name', optional 'image_path'
        """
        name = ticket_dict.get("name")
        image_path = ticket_dict.get("image_path")
        return cls(name, image_path)

    @classmethod
    def create_tickets(cls, tickets_data: list):
        """
        Create multiple Ticket instances from a list of dictionaries.
        Returns a list of Ticket objects.
        """
        return [cls.from_dict(data) for data in tickets_data]

ticket_data = [
    {"name": "Move Up", "image_path": "up.png"},
    {"name": "Move Down", "image_path": "down.png"},
    {"name": "Cut Red Wire"},
    {"name": "Cut Blue Wire"},
    {"name": "Press Button"},
    {"name": "Rotate Dial"}
]


class Hand:
    def __init__(self):
        self.tickets = []

    def add(self, ticket):
        self.tickets.append(ticket)

    def add_many(self, tickets):
        self.tickets.extend(tickets)

    def clear(self):
        self.tickets = []

    def __len__(self):
        return len(self.tickets)
    
    def __str__(self):
        return ", ".join(str(ticket) for ticket in self.tickets)

    def __iter__(self):
        return iter(self.tickets)


class TicketPool:
    def __init__(self, tickets):
        self.tickets = tickets  # list of all 20 tickets

    def list_available(self):
        return self.tickets


class Communicator(Player):

    def __init__(self, name, ticket_pool):
        super().__init__(name)
        self.ticket_pool = ticket_pool  # TicketPool object
        self.selected_hand = Hand()     # max 5 tickets per turn

    def take_turn(self, game_state: dict):
        print(f"\n[Communicator] {self.name}'s turn")
        print("Available tickets:")
        for i, ticket in enumerate(self.ticket_pool.list_available()):
            print(f"{i}: {ticket}")

        print("Choose up to 5 tickets (comma separated indices):")
        choice_str = input("> ").strip()
        choices = [x for x in choice_str.split(",") if x.isdigit()]
        choices = [int(x) for x in choices if 0 <= int(x) < len(self.ticket_pool.tickets)]

        if len(choices) > 5:
            print("You can only pick up to 5 tickets!")
            return

        # assign selected tickets
        selected = [self.ticket_pool.tickets[i] for i in choices]
        self.selected_hand.clear()
        self.selected_hand.add_many(selected)
        # # send to diffuser via game state
        game_state["tickets_to_send"] = selected
        print(f"Sent {len(selected)} tickets: {self.selected_hand}")
    
    # def select_

    def send_tickets(self):
        return self.selected_hand


class Diffuser(Player):
    def __init__(self, name):
        super().__init__(name)
        self.hand = Hand()

    def update_hand(self, new_cards):
        self.hand.clear()
        self.hand.add_many(new_cards)
        # print(self.hand.add_many(new_cards))
        # print([i for i in self.hand])

    def take_turn(self, game_state: dict):
        print(f"\n[Diffuser] {self.name}'s turn")
        print("Your current tickets:")
        for ticket in self.hand:
            print("-", ticket)


class Game:
    def __init__(self, comm_name, diff_name, tickets_data):
        tickets = Ticket.create_tickets(tickets_data)
        self.communicator = Communicator(comm_name, TicketPool(tickets))
        self.diffuser = Diffuser(diff_name)
        self.players = [self.communicator, self.diffuser]
        self.current_player_index = 0
        self.state = {
            "tickets_to_send": None,
            "last_action": None,
            "running": True,
        }

    def switch_turns(self):
        self.current_player_index = (self.current_player_index + 1) % 2
        # print(c3urrent_player_index)
        # after communicator ends turn, pass tickets to diffuser
        if self.current_player_index == 1:
            if self.state["tickets_to_send"]:
                self.diffuser.update_hand(self.state["tickets_to_send"])
                # self.state["tickets_to_send"] = None

    def run(self):
        print("=== Bomb Defusal Game Starting ===")
        while self.state["running"]:
            # time.sleep(1)  # just to slow down the loop for readability
            
            current_player = self.players[self.current_player_index]
            current_player.take_turn(self.state)
            self.switch_turns()
            # Example ending condition
            if self.state["last_action"] == "CUT RED WIRE":
                print("Boom! Wrong wire! Game over!")
                self.state["running"] = False


game = Game("Alice", "Bob", ticket_data)
game.run()


# class Game:
#     """
#     Base game engine for a 2-player terminal game.
#     Manages initialization, main loop, turn order, and exit conditions.
#     """

#     def __init__(self, player1_name: str, player2_name: str) -> None:
#         self.players = [
#             Player(player1_name),
#             Player(player2_name)
#         ]
#         self.current_player_index = 0

#         # Flexible container for game-specific state
#         self.state: dict = {
#             "turn_count": 0,
#             "last_move": None,
#             "running": True
#         }

#     def run(self) -> None:
#         """Start the main game loop."""
#         self.on_start()

#         while self.state["running"]:
#             self.update()
#             self.render()
#             self.switch_turns()

#         self.on_end()

#     def on_start(self) -> None:
#         """Hook for anything that needs to run before the game loop starts."""
#         print("Game starting...\n")

#     def update(self) -> None:
#         """
#         Update the game logic for the current player.
#         Turn order, inputs, and rule checks live here.
#         """
#         current_player = self.players[self.current_player_index]
#         current_player.take_turn(self.state)
#         self.state["turn_count"] += 1

#         # Example condition — your real game will replace this:
#         if self.state["turn_count"] >= 10:
#             self.state["running"] = False

#     def render(self) -> None:
#         """Display game state each loop iteration."""
#         print("\n--- GAME STATE ---")
#         print(f"Turn: {self.state['turn_count']}")
#         print(f"Last Move: {self.state['last_move']}")
#         print("------------------\n")

#     def switch_turns(self) -> None:
#         """Move to the next player's turn."""
#         self.current_player_index = (self.current_player_index + 1) % len(self.players)

#     def on_end(self) -> None:
#         """Hook for anything that needs to run after the loop exits."""
#         print("Game over. Thanks for playing!")


# if __name__ == "__main__":
#     game = Game("Player 1", "Player 2")
#     game.run()
