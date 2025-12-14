import pygame
from pygame.math import Vector2
import random

pygame.init()

# ---------------------------
# EASING FUNCTIONS
# ---------------------------
def ease_out_expo(t):
    t = min(max(t, 0), 1)
    if t == 1:
        return 1
    return 1 - 2 ** (-10 * t)

def ease_out_quint(t):
    t = min(max(t, 0), 1)
    return 1 - (1 - t) ** 5

def ease_in_out_quint(t):
    t = min(max(t, 0), 1)
    if t < 0.5:
        return 16 * t**5
    else:
        return 1 - (-2*t + 2)**5 / 2


# ---------------------------
# SIMPLE B-SPLINE
# ---------------------------
class BSpline:
    def __init__(self, points, degree=3):
        self.control_points = [Vector2(p) for p in points]
        self.degree = degree
        self.knots = self.generate_knots()

    def generate_knots(self):
        n = len(self.control_points)
        k = self.degree
        return [0]*k + list(range(n - k + 1)) + [n - k]*k

    def de_boor(self, t):
        k = self.degree
        knots = self.knots
        pts = self.control_points
        n = len(pts) - 1

        # find knot span
        for i in range(len(knots)-1):
            if knots[i] <= t <= knots[i+1]:
                break
        i = min(i, n)

        d = [pts[j] for j in range(i - k, i + 1)]
        for r in range(1, k+1):
            for j in range(k, r-1, -1):
                denom = knots[j + i - r + 1] - knots[i - k + j]
                alpha = 0.0 if denom == 0 else (t - knots[i - k + j]) / denom
                d[j] = (1 - alpha) * d[j-1] + alpha * d[j]
        return d[k]

# ---------------------------
# ANIMATION CLASS
# ---------------------------
class Animation:
    def __init__(self, sprite, points, duration=1.0, degree=1, easing=None, delay=0.0):
        if len(points) < degree + 1:
            raise ValueError(f"Need at least {degree+1} points for degree {degree} spline")
        self.sprite = sprite
        self.spline = BSpline(points, degree)
        self.duration = max(duration, 0.0001)
        self.easing = easing
        self.delay = delay
        self.elapsed = 0.0
        self.finished = False

        self.t_start = self.spline.knots[degree]
        self.t_end = self.spline.knots[-degree-1]

        self.start_pos = Vector2(sprite.pos)
        self.spline_start_pos = self.spline.de_boor(self.t_start)

    def update(self, dt):
        if self.finished:
            return

        self.elapsed += dt
        if self.elapsed < self.delay:
            return

        t_norm = (self.elapsed - self.delay) / self.duration
        t_norm = min(t_norm, 1.0)
        if self.easing:
            t_norm = self.easing(t_norm)

        t_current = self.t_start + t_norm * (self.t_end - self.t_start)

        # directly move along the spline, no teleport
        self.sprite.pos = self.spline.de_boor(t_current)
        self.sprite.rect.center = self.sprite.pos

        if t_norm >= 1.0:
            self.finished = True


# ---------------------------
# SPRITE CLASS
# ---------------------------
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, position=(0,0), color=(255,255,0), size=(20,20)):
        super().__init__()
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0,0,*size))
        self.rect = self.image.get_rect()
        self.pos = Vector2(position)

        self.animations = []           # sequential animation queue
        self.current_animation = None
        self.parallel_animations = []  # parallel animations

        self.trail = []

    def animate(self, *points, duration=1.0, degree=3, easing=None, delay=0.0, parallel=False):
        anim = Animation(self, points, duration, degree, easing, delay)
        if not self.animations and not self.parallel_animations:
            self.pos = Vector2(points[0])
            self.rect.center = self.pos
        if parallel:
            self.parallel_animations.append(anim)
        else:
            self.animations.append(anim)

    def update(self, dt):
        # sequential
        if self.current_animation is None and self.animations:
            self.current_animation = self.animations.pop(0)

        if self.current_animation:
            self.current_animation.update(dt)
            if self.current_animation.finished:
                self.current_animation = None

        # parallel
        for anim in self.parallel_animations:
            anim.update(dt)
        self.parallel_animations = [a for a in self.parallel_animations if not a.finished]

        # trail
        self.trail.append(Vector2(self.pos))
        if len(self.trail) > 300:
            self.trail.pop(0)

    def draw_trail(self, surface):
        for pos in self.trail:
            pygame.draw.circle(surface, (75,75,75), pos, 1)

# ---------------------------
# MAIN LOOP
# ---------------------------
def randColor():
    return (random.randint(50,200), random.randint(50,200), random.randint(50,200))

def main():
    screen = pygame.display.set_mode((600, 400))
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    # sprite1 = AnimatedSprite(position=(0,0),color=randColor())
    # sprite2 = AnimatedSprite(color=randColor())
    # sprite3 = AnimatedSprite(color=randColor())
    # all_sprites = pygame.sprite.Group(sprite1, sprite2, sprite3)

    delay = 0.5
    delay_ticket = .1
    offset = 50
    for i in range(5):
        sprite = AnimatedSprite(position=(50,225),color=randColor())
        all_sprites.add(sprite)
        sprite.animate((50,225), (50,175), # Slide up
                        duration=0.5,
                        delay=delay_ticket*i,
                        easing=ease_out_quint,
                        degree=1, 
                        parallel=True)
        
        sprite.animate((50,175), (50,0), (200+offset*i,300), # Sweep to hand
                        duration=1.0, 
                        delay=delay_ticket*i + delay, 
                        easing=ease_in_out_quint, 
                        degree=2, 
                        parallel=True)

    # sprite2.animate((50,225), (50,175), # Slide up
    #                 duration=.50,
    #                 delay=0.5,
    #                 easing=ease_out_quint,
    #                 degree=1, 
    #                 parallel=True)
    
    # sprite2.animate((50,175), (50,0), (200,300), # Sweep to hand
    #                 duration=1.0, 
    #                 delay=1.0, 
    #                 easing=ease_in_out_quint, 
    #                 degree=2, 
    #                 parallel=True)


    # sprite1.animate((50,250),(500,300),(500,100),(100,100), duration=4, degree=3, easing=ease_out_expo ,parallel=True)
    # sprite1.animate((100,350),(500,350),(500,50),(100,50), duration=2, degree=2, easing=ease_out_quint, parallel=True)
    # sprite1.animate((50,250),(50,50),(250,50),(250,250), duration=1, degree=2, easing=ease_out_quint ,parallel=True)
    # create sprites and animations
    # for i in range(4):
    #     sprite = AnimatedSprite(color=randColor())
    #     all_sprites.add(sprite)
    #     sprite.animate((50,250),(50,50),(250,50),(250,250), duration=3, degree=2, easing=ease_out_quint)
    #     sprite.animate((300,300),(500,300),(500,100),(300,100), duration=3, degree=3, easing=ease_out_expo, delay=0.5)
    #     sprite.animate((100,350),(500,350),(500,50),(100,50), duration=2, degree=2, easing=ease_out_quint, parallel=True)

    running = True
    
    while running:
        dt = clock.tick(120)/1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        all_sprites.update(dt)

        screen.fill((30,30,30))
        # for s in all_sprites:
        #     s.draw_trail(screen)
        all_sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
