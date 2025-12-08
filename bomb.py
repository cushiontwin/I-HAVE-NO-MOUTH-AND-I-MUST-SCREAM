from bomb_module_1 import Module as Module1
from bomb_module2 import Module2 as Module2
import pygame 
import sys

import pygame

class ClockModule(pygame.sprite.Group):
    WIDTH, HEIGHT = 200, 225
    MAX_RESETS = 1  # maximum number of resets
    REDUCE_PER_RESET = 20  # seconds reduced per reset

    def __init__(self, offset, total_time=30):
        super().__init__()
        self.offset = offset
        self.initial_total_time = total_time
        self.total_time = total_time
        self.remaining = total_time
        self.running = True
        self.reset_count = 0
        self.hooray_path = r"C:\Users\codyc\Code\.venv\game\hooray.mp3"
        self.explosion_sound = pygame.mixer.Sound(r"C:\Users\codyc\Code\.venv\game\boom.wav")
        self.font = pygame.font.Font(r"C:\Users\codyc\Code\.venv\game\Pixellari.ttf", 72)
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)

    def update(self, dt):
        if not self.running:
            return

        self.remaining -= dt
        
        if self.remaining <= 0:
            self.remaining = 0
            if self.running:
                pygame.mixer.Sound(r"C:\Users\codyc\Code\.venv\game\boom.wav").play()
            self.running = False

    def reset(self):
        """Reset the clock, reducing total time by 20s each reset. Max 2 resets."""
        # Solved the bomb
        if self.reset_count == self.MAX_RESETS:
            hooray = pygame.mixer.Sound(self.hooray_path)
            hooray.play()
            return

        self.reset_count += 1
        self.total_time = max(0, self.initial_total_time - self.REDUCE_PER_RESET * self.reset_count)
        self.remaining = self.total_time
        self.running = True
        print(f"[ClockModule] Reset {self.reset_count}: total_time={self.total_time}")

    def draw(self, screen, offset_override=None):
        self.surface.fill((30, 30, 30, 200))  # semi-transparent background
        seconds = int(self.remaining)
        mins = seconds // 60
        secs = seconds % 60
        text = f"{mins:02}:{secs:02}"

        img = self.font.render(text, True, (255, 255, 255))
        rect = img.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        self.surface.blit(img, rect)

        pos = offset_override if offset_override else self.offset
        screen.blit(self.surface, pos)


class ModuleManager:
    def __init__(self, modules):
        self.modules = modules
        # self.clock = next((m for m in modules if isinstance(m, ClockModule)), None)

    def handle_events(self, events):
        for module in self.modules:
            if not isinstance(module, ClockModule):
                module.handle_events(events)

    def update(self, dt):
        all_done = self.all_complete()

        # Only act when the round just completed
        if all_done:
            # Check if clock can still reset
            for m in self.modules:
                if isinstance(m, ClockModule):
                    if m.running:
                        if m.reset_count < m.MAX_RESETS:
                            for module in self.modules:
                                module.reset()
            # if self.clock and self.clock.reset_count < self.clock.MAX_RESETS:
            #     # Reset clock and all other modules
            #     self.clock.reset()
            #     for module in self.modules:
            #         module.reset()

                # Play hooray sound for the round


        # Update all modules
        for module in self.modules:
            # if isinstance(module, ClockModule):
            #     module.running = not all_done
            module.update(dt)

    def all_complete(self):
        """Return True if all non-clock modules are complete."""
        return all(
            getattr(module, "complete", True)
            for module in self.modules
            if not isinstance(module, ClockModule)
        )

    def draw(self, screen):
        for module in self.modules:
            module.draw(screen)
