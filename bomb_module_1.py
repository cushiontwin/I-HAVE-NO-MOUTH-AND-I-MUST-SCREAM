import pygame
import sys
import random
from utilities import BaseSprite, Button

WIDTH, HEIGHT = 800, 600
FPS = 60
MOVE_STEP = 28

selector_image_path = r"C:\Users\codyc\Code\.venv\game\square.png"
arrow_unpressed_image_path = r"C:\Users\codyc\Code\.venv\game\arrow.png"
arrow_pressed_image_path = r"C:\Users\codyc\Code\.venv\game\arrow_pressed.png"
confirm_image_path = r"C:\Users\codyc\Code\.venv\game\confirm_button.png"
grid_image_path = r"C:\Users\codyc\Code\.venv\game\grid.png"
lightbulb_on_image_path = r"C:\Users\codyc\Code\.venv\game\lightbulb_on.png"
lightbulb_off_image_path = r"C:\Users\codyc\Code\.venv\game\lightbulb_off.png"
blip_sound_path = r"C:\Users\codyc\Code\.venv\game\blip_sine.wav"
error_sound_path = r"C:\Users\codyc\Code\.venv\game\error.wav"
boop_sound_path = r"C:\Users\codyc\Code\.venv\game\boop.wav"

# pygame.mixer.init()
# pygame.mixer.init()

# CHANNEL_CONFIRM = pygame.mixer.Channel(1)
# CHANNEL_BLIP    = pygame.mixer.Channel(2)
# CHANNEL_ERROR   = pygame.mixer.Channel(3)




class Lightbulb(BaseSprite):

    def __init__(self, on_path, off_path, pos=(0,0), scale=4):
        super().__init__(off_path, pos, scale)
        self.image_on = pygame.transform.scale_by(pygame.image.load(on_path).convert_alpha(), scale)
        self.image_off = self.image
        self.on = False
        self.success_sound = pygame.mixer.Sound(r"C:\Users\codyc\Code\.venv\game\success.wav")

    def turn_on(self):
        self.image = self.image_on
        self.success_sound.play()
        self.on = True

    def turn_off(self):
        self.image = self.image_off
        self.on = False


class ArrowButton(Button):
    def __init__(self, pos, module, direction, unpressed_path, pressed_path,
                 step=MOVE_STEP, scale=4):
        super().__init__(unpressed_path, pos, scale)
        self.module = module
        self.direction = direction
        self.step = step
        # Load pressed/unpressed images
        self.unpressed_image = pygame.transform.scale_by(pygame.image.load(unpressed_path).convert_alpha(), scale)
        self.pressed_image = pygame.transform.scale_by(pygame.image.load(pressed_path).convert_alpha(), scale)
        self.image = self.unpressed_image
        self.error_sound = pygame.mixer.Sound(error_sound_path)
        self.blip_sound = pygame.mixer.Sound(blip_sound_path)

    def on_release(self):
        self.image = self.unpressed_image

    def try_move(self, dx, dy):
        x, y = self.module.grid_pos
        new_x = x + dx
        new_y = y + dy

        if not (0 <= new_x <= 5 and 0 <= new_y <= 5):
            return False

        rect = self.module.selector.rect
        rect.x += dx * self.step
        rect.y += -dy * self.step
        self.module.grid_pos = (new_x, new_y)
        return True
        
    def on_click(self):
        self.image = self.pressed_image
        
        dirs = {"up": (0, 1), "down": (0,-1), "left": (-1,0), "right": (1,0)}
        dx, dy = dirs[self.direction]

        if self.try_move(dx, dy):
            self.blip_sound.play()
        else:
            self.error_sound.play()


class ConfirmButton(Button):
    def __init__(self, pos, module, image_path=confirm_image_path, scale=2, name=None, sound_path=boop_sound_path):
        super().__init__(image_path, pos, scale)
        self.module = module
        self.sound = pygame.mixer.Sound(sound_path)

    def on_click(self):
        """Check if the selector is on the correct grid position."""
        self.sound.play()
        self.module.check_result()


class Module(pygame.sprite.Group):
    WIDTH, HEIGHT = 300, 225

    def __init__(self, offset):
        super().__init__()
        self.offset = offset
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.grid_pos = (0, 0)
        self.correct_pos = (random.randint(0, 5), random.randint(0, 5))
        self.complete = False

        # Sprites
        self.grid = BaseSprite(grid_image_path, (24, 24), scale=4)
        self.lightbulb = Lightbulb(lightbulb_on_image_path, lightbulb_off_image_path, (240, 20), scale=4)
        self.selector = BaseSprite(selector_image_path, (20, 156), scale=4)
        self.add(self.grid, self.selector, self.lightbulb)

        # Buttons
        self.buttons = []
        self._create_buttons()

    def _create_buttons(self):
        # Confirm
        confirm_btn = ConfirmButton((232, 132), self)
        self.buttons.append(confirm_btn)
        self.add(confirm_btn)
        # Arrows
        positions = [(232, 100), (232, 164), (200, 132), (264, 132)]
        directions = ["up", "down", "left", "right"]
        for pos, dir in zip(positions, directions):
            arrow = ArrowButton(pos, self, dir, arrow_unpressed_image_path, arrow_pressed_image_path)
            self.buttons.append(arrow)
            self.add(arrow)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        mx, my = pygame.mouse.get_pos()
        local_mouse = (mx - self.offset[0], my - self.offset[1])
        for event in events:
            for btn in self.buttons:
                btn.handle_event(event, local_mouse)

    def update(self, dt):
        super().update(dt)

    def draw(self, screen: pygame.Surface):
        self.surface.fill((40, 40, 40))
        super().draw(self.surface)
        screen.blit(self.surface, self.offset)

    def check_result(self) -> bool:
        # Turn the lightbulb on
        if self.grid_pos == self.correct_pos:
            if not self.complete:
                self.lightbulb.turn_on()
            self.complete = True

        print(f"Selected: {self.grid_pos} | {self.correct_pos} => {self.complete}")
        return self.complete

    def reset(self):
        """Reset the module to start a new round."""
        self.complete = False
        self.grid_pos = (0, 0)
        self.selector.rect.topleft = (20, 156)
        self.correct_pos = (random.randint(0, 5), random.randint(0, 5))
        self.lightbulb.turn_off()
        print(f"[Module] Reset: new correct_pos={self.correct_pos}")