import pygame
import sys
import random
from utilities import BaseSprite, Button

FPS = 60

selector_image_path = r"C:\Users\codyc\Code\.venv\game\square.png"
lightbulb_on_image_path = r"C:\Users\codyc\Code\.venv\game\lightbulb_on.png"
lightbulb_off_image_path = r"C:\Users\codyc\Code\.venv\game\lightbulb_off.png"

blip_sound_path = r"C:\Users\codyc\Code\.venv\game\blip_sine.wav"
error_sound_path = r"C:\Users\codyc\Code\.venv\game\error.wav"
boop_sound_path = r"C:\Users\codyc\Code\.venv\game\boop.wav"

# pygame.mixer.init()


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

class Module2(pygame.sprite.Group):
    WIDTH, HEIGHT = 200, 225

    def __init__(self, offset):
        super().__init__()
        self.offset = offset
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.complete = False

        self.lightbulb = Lightbulb(lightbulb_on_image_path, lightbulb_off_image_path, (150, 20), scale=4)

        x_center = 50
        y_center = 100
        self.gap = 20
        # Buttons
        self.buttons = [
            Button(selector_image_path, (x_center - self.gap, y_center - self.gap), name="1", on_click_func=self.clicked),
            Button(selector_image_path, (x_center + self.gap, y_center - self.gap), name="2", on_click_func=self.clicked),
            Button(selector_image_path, (x_center - self.gap, y_center + self.gap), name="3", on_click_func=self.clicked),
            Button(selector_image_path, (x_center + self.gap, y_center + self.gap), name="4", on_click_func=self.clicked),
        ]

        self.add(self.lightbulb)
        for btn in self.buttons:
            self.add(btn)

        self.correct_sequence = random.sample(self.buttons, 4)
        self.sequence_index = 0
        
        self.boop = pygame.mixer.Sound(boop_sound_path)
        self.blip = pygame.mixer.Sound(blip_sound_path)
        self.error = pygame.mixer.Sound(error_sound_path)
        print("Module2 Correct Sequence:", [btn.name for btn in self.correct_sequence])

    def clicked(self, btn):
        print("Clicked:", btn.name)
        if btn == self.correct_sequence[self.sequence_index]:
            self.sequence_index += 1
            print("Correct button!")
            self.boop.play()

            if self.sequence_index == len(self.correct_sequence):
                if not self.complete:
                    self.lightbulb.turn_on()
                self.complete = True
                print("Module Complete!")
        else:
            print("Wrong button! Resetting sequence.")
            self.error.play()
            self.sequence_index = 0

    def handle_events(self, events):
        mx, my = pygame.mouse.get_pos()
        local_mouse = (mx - self.offset[0], my - self.offset[1])

        for event in events:
            for btn in self.buttons:
                btn.handle_event(event, local_mouse)

    def update(self, dt):
        super().update(dt)

    def draw(self, screen):
        self.surface.fill((40, 40, 40))
        super().draw(self.surface)
        screen.blit(self.surface, self.offset)

    def reset(self):
        """Reset the module to start a new round."""
        self.complete = False
        self.sequence_index = 0
        self.correct_sequence = random.sample(self.buttons, 4)
        self.lightbulb.turn_off()
        print("Module2 reset! New sequence:", [btn.name for btn in self.correct_sequence])
