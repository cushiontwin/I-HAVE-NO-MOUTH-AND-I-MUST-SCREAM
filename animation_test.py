import pygame
import time

# --- Animation (data only) ---
class Animation:
    """Stores a single animation step for one sprite."""
    def __init__(self, sprite, start_pos=None, end_pos=None, duration=0, delay=0, pause=False):
        self.sprite = sprite
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.duration = duration
        self.delay = delay
        self.pause = pause

    def __repr__(self):
        if self.pause:
            return f"<Pause {self.duration}s for {self.sprite}>"
        else:
            return f"<Move {self.sprite} {self.start_pos}->{self.end_pos} duration={self.duration}s>"


# --- AnimationQueue ---
class AnimationQueue:
    """Sequential queue that executes animations one by one for multiple sprites."""
    def __init__(self):
        self.queue = []
        self.current = None
        self.current_start_time = None
        self.started = False
        self.start_delay = 0

    def add_animation(self, anim: Animation):
        self.queue.append(anim)

    def add_pause(self, sprite, duration, delay=0):
        self.queue.append(Animation(sprite, (self.queue[-1].start_pos), (self.queue[-1].end_pos), duration=duration, delay=delay, pause=True))

    def start(self, delay=0):
        self.start_delay = delay
        self.start_time = time.time()
        self.started = True

    # def update(self):
    #     if not self.started or (self.current is None and not self.queue):
    #         return

    #     now = time.time()

    #     # Wait for initial queue delay
    #     if now - self.start_time < self.start_delay:
    #         return

    #     # Start next animation
    #     if self.current is None and self.queue:
    #         self.current = self.queue.pop(0)
    #         self.current_start_time = now

    #         # Dynamic start_pos
    #         if self.current.start_pos is None:
    #             self.current.start_pos = (self.current.sprite.x, self.current.sprite.y)

    #     if self.current is None:
    #         return

    #     # Compute elapsed for current animation
    #     elapsed = now - self.current_start_time

    #     # Wait for step-specific delay
    #     if elapsed < self.current.delay:
    #         return

    #     # Compute progress (0..1)
    #     t = min((elapsed - self.current.delay) / self.current.duration, 1.0)

    #     # Interpolate position
    #     sx, sy = self.current.start_pos
    #     ex, ey = self.current.end_pos
    #     self.current.sprite.x = sx + (ex - sx) * t
    #     self.current.sprite.y = sy + (ey - sy) * t

    #     # Finish animation
    #     if t >= 1.0:
    #         self.current = None

    #     return 
    def update(self):
        if not self.started: return
        now = time.time()
        if now - self.start_time < self.start_delay: return

        if self.current is None and self.queue:
            self.current = self.queue.pop(0)
            self.current_start_time = now
            if self.current.start_pos is None:
                self.current.start_pos = (self.current.sprite.x, self.current.sprite.y)

        c = self.current
        if c is None or now - self.current_start_time < c.delay: return

        t = min((now - self.current_start_time - c.delay)/c.duration, 1.0)
        sx, sy = c.start_pos; ex, ey = c.end_pos
        c.sprite.x, c.sprite.y = sx + (ex-sx)*t, sy + (ey-sy)*t
        if t >= 1.0: self.current = None



    def __repr__(self):
        cur_repr = repr(self.current) if self.current else "None"
        queue_repr = ", ".join(repr(anim) for anim in self.queue)
        return f"AnimationQueue(current={cur_repr}, queue=[{queue_repr}])"


# --- Pygame Sprite ---
class MySprite(pygame.sprite.Sprite):
    def __init__(self, pos, color, name):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.x, self.y = pos
        self.name = name

    def __repr__(self):
        return f"<Sprite {self.name}>"

    def update(self):
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)


# --- Pygame setup ---
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Create sprites
sprites = pygame.sprite.Group()
sprite_list = [
    MySprite((100, 300), (255,0,0), "A"),
    MySprite((150, 300), (0,255,0), "B"),
    MySprite((200, 300), (0,0,255), "C")
]
sprites.add(sprite_list)

# --- Single animation queue ---
queue = AnimationQueue()

# Define per-sprite animations in a loop
for i, sprite in enumerate(sprite_list):
    queue.add_animation(Animation(sprite, start_pos=(100, 300), end_pos=(100,200), duration=1, delay=0.2*i))
    # queue.add_pause(sprite, duration=0.3)
    queue.add_animation(Animation(sprite, start_pos=None, end_pos=(sprite.x + 150, sprite.y), duration=1, delay=0.2*i))

queue.start()


# --- Main loop ---
running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    queue.update()
    sprites.update()

    screen.fill((30, 30, 30))
    sprites.draw(screen)
    pygame.display.flip()

pygame.quit()







# def update(self):
#         if not self.started:
#             return

#         elapsed_since_start = time.time() - self.start_time
#         if elapsed_since_start < self.start_delay:
#             return

#         if self.current is None and self.queue:
#             self.current = self.queue.pop(0)
#             self.current_start_time = time.time()

#             if not self.current.pause:
#                 self.current.sprite.x, self.current.sprite.y = self.current.start_pos

#         if self.current:
#             step = self.current
#             elapsed = time.time() - self.current_start_time
#             if elapsed < step.delay:
#                 return

#             if step.pause:
#                 if elapsed >= step.delay + step.duration:
#                     self.current = None
#             else:
#                 t = min((elapsed - step.delay) / step.duration, 1.0)
#                 sx, sy = step.start_pos
#                 ex, ey = step.end_pos
#                 step.sprite.x = sx + (ex - sx) * t
#                 step.sprite.y = sy + (ey - sy) * t

#                 if t >= 1.0:
#                     step.sprite.x, step.sprite.y = ex, ey

#                     if len(self.queue) > 1:
#                         next_animation = self.queue[1]
#                         if next_animation.start_pos == None:
#                             next_animation.start_pos = (step.sprite.x, step.sprite.y)
#                     self.current = None
