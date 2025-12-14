import pygame
import numpy as np
from scipy.interpolate import BSpline

# pygame.init()

def clamp01(t):
    return np.clip(t, 0.0, 1.0)


def ease_linear(t):
    return clamp01(t)

_prev = 0.0  # module-level memory
def ease_jitter_step(t, steps=15, intensity=0.03):
    t = clamp01(t)
    base = t
    offset = (np.random.uniform(-1, 1) * intensity)
    
    # Quantize to little steps
    stepped = round(base * steps) / steps

    return clamp01(stepped + offset)

def ease_jitter_start(t, intensity=0.03, decay=4):
    t = clamp01(t)
    jitter = np.sin(t * 60) * intensity * (1 - t)**decay
    return clamp01(t + jitter)

def ease_jitter_beats(t, intensity=0.02, f1=30, f2=33):
    t = clamp01(t)
    jitter = (np.sin(t*f1) + np.sin(t*f2)) * 0.5 * intensity
    return clamp01(t + jitter)

def ease_jitter_noise(t, intensity=0., speed=80.0):
    t = clamp01(t)

    # 1D smooth noise by interpolating between random values
    i = int(t * speed)
    f = (t * speed) - i
    a = np.random.RandomState(i).rand() * 2 - 1
    b = np.random.RandomState(i+1).rand() * 2 - 1
    smooth = (1 - np.cos(f * np.pi)) * 0.5  # smoothstep
    n = a * (1 - smooth) + b * smooth

    return clamp01(t + n * intensity)


def ease_jitter_random(t, intensity=0.015, damping=0.8):
    global _prev
    t = clamp01(t)

    # Random target noise
    target = (np.random.uniform(-1,1) * intensity)

    # Smooth the noise so it doesn’t jump too hard
    _prev = _prev * damping + target * (1 - damping)

    return clamp01(t + _prev)


def ease_jitter(t, intensity=0.2, freq=40.0):
    t = clamp01(t)

    # Add high-frequency noise around the linear value
    jitter = (np.sin(t * freq) * intensity)

    # Keep final output in [0,1]
    return clamp01(t + jitter)

#======================
# QUAD (t^2)
#======================
def ease_in_quad(t):
    t = clamp01(t)
    return t * t

def ease_out_quad(t):
    t = clamp01(t)
    return 1 - (1 - t) * (1 - t)

def ease_in_out_quad(t):
    t = clamp01(t)
    if t < 0.5:
        return 2 * t * t
    return 1 - pow(-2*t + 2, 2) / 2


#======================
# CUBIC (t^3)
#======================
def ease_in_cubic(t):
    t = clamp01(t)
    return t*t*t

def ease_out_cubic(t):
    t = clamp01(t)
    return 1 - pow(1 - t, 3)

def ease_in_out_cubic(t):
    t = clamp01(t)
    if t < 0.5:
        return 4 * t*t*t
    return 1 - pow(-2*t + 2, 3) / 2


#======================
# QUART
#======================
def ease_in_quart(t):
    t = clamp01(t)
    return t*t*t*t

def ease_out_quart(t):
    t = clamp01(t)
    return 1 - pow(1 - t, 4)

def ease_in_out_quart(t):
    t = clamp01(t)
    if t < 0.5:
        return 8 * pow(t, 4)
    return 1 - pow(-2*t + 2, 4) / 2


#======================
# QUINT
#======================
def ease_in_quint(t):
    t = clamp01(t)
    return t**5

def ease_out_quint(t):
    t = clamp01(t)
    return 1 - pow(1 - t, 5)

def ease_in_out_quint(t):
    t = clamp01(t)
    if t < 0.5:
        return 16 * t**5
    return 1 - pow(-2*t + 2, 5) / 2


#======================
# SINE
#======================
def ease_in_sine(t):
    t = clamp01(t)
    return 1 - np.cos((t * np.pi) / 2)

def ease_out_sine(t):
    t = clamp01(t)
    return np.sin((t * np.pi) / 2)

def ease_in_out_sine(t):
    t = clamp01(t)
    return -(np.cos(np.pi * t) - 1) / 2


#======================
# EXPO
#======================
def ease_in_expo(t):
    t = clamp01(t)
    return 0 if t == 0 else pow(2, 10*(t - 1))

def ease_out_expo(t):
    t = clamp01(t)
    return 1 if t == 1 else 1 - pow(2, -10*t)

def ease_in_out_expo(t):
    t = clamp01(t)
    if t == 0 or t == 1:
        return t
    if t < 0.5:
        return pow(2, 20*t - 11)
    return 1 - pow(2, -20*t + 11)


#======================
# CIRC (circular arc)
#======================
def ease_in_circ(t):
    t = clamp01(t)
    return 1 - np.sqrt(1 - t*t)

def ease_out_circ(t):
    t = clamp01(t)
    return np.sqrt(1 - pow(t - 1, 2))

def ease_in_out_circ(t):
    t = clamp01(t)
    if t < 0.5:
        return (1 - np.sqrt(1 - 4*t*t)) / 2
    return (np.sqrt(1 - pow(-2*t + 2, 2)) + 1) / 2


#======================
# BACK (overshoot)
#======================
def ease_in_back(t, s=1.70158):
    t = clamp01(t)
    return (s + 1)*t*t*t - s*t*t

def ease_out_back(t, s=1.70158):
    t = clamp01(t)
    return 1 + (s + 1)*pow(t-1,3) + s*pow(t-1,2)

def ease_in_out_back(t, s=1.70158):
    t = clamp01(t)
    s *= 1.525
    if t < 0.5:
        return pow(2*t, 2) * ((s+1)*2*t - s) / 2
    return (pow(2*t - 2, 2) * ((s+1)*(t*2 - 2) + s) + 2) / 2


#======================
# ELASTIC (spring)
#======================
def ease_in_elastic(t):
    t = clamp01(t)
    if t in (0,1):
        return t
    return -pow(2, 10*(t-1)) * np.sin((t - 1.075) * (2*np.pi) / 0.3)

def ease_out_elastic(t):
    t = clamp01(t)
    if t in (0,1):
        return t
    return pow(2, -10*t) * np.sin((t - 0.075) * (2*np.pi) / 0.3) + 1

def ease_in_out_elastic(t):
    t = clamp01(t)
    if t in (0,1):
        return t
    if t < 0.5:
        return -0.5 * pow(2, 20*t - 11) * np.sin((20*t - 11.125) * (2*np.pi) / 0.45)
    return pow(2, -20*t + 11) * np.sin((20*t - 11.125) * (2*np.pi) / 0.45) * 0.5 + 1


#======================
# BOUNCE (physics-ish)
#======================
def _bounce_calc(t):
    if t < 1/2.75:
        return 7.5625 * t * t
    elif t < 2/2.75:
        t -= 1.5/2.75
        return 7.5625 * t*t + 0.75
    elif t < 2.5/2.75:
        t -= 2.25/2.75
        return 7.5625 * t*t + 0.9375
    else:
        t -= 2.625/2.75
        return 7.5625 * t*t + 0.984375

def ease_out_bounce(t):
    return _bounce_calc(clamp01(t))

def ease_in_bounce(t):
    t = clamp01(t)
    return 1 - ease_out_bounce(1 - t)

def ease_in_out_bounce(t):
    t = clamp01(t)
    if t < 0.5:
        return (1 - ease_out_bounce(1 - 2*t)) / 2
    return (1 + ease_out_bounce(2*t - 1)) / 2


# -----------------------------
# Simple Spline wrapper
# -----------------------------
class Spline:
    """
    Wrapper around scipy BSpline to handle 2D paths.
    """
    def __init__(self, points, degree: int = 1):
        """
        :param points: list of [x,y] control points
        :param degree: degree of B-spline
        """
        self.points = np.array(points)
        self.degree = degree
        n = len(points)
        # Clamping ensures the curve starts and ends exactly at the first and last
        # control points.
        self.knots = np.concatenate((
            np.zeros(degree),
            np.linspace(0, 1, n - degree + 1),
            np.ones(degree)
        ))
        # Create separate splines for x and y
        self.spline_x = BSpline(self.knots, self.points[:,0], degree)
        self.spline_y = BSpline(self.knots, self.points[:,1], degree)

    def evaluate(self, t: float) -> np.ndarray:
        """
        Evaluate spline at normalized time t.
        :param t: 0 to 1
        :return: np.array([x, y])
        """
        t = np.clip(t, 0, 1)
        return np.array([self.spline_x(t), self.spline_y(t)])

    def derivative(self, t: float) -> np.ndarray:
        """
        Compute the first derivative (velocity) at t.
        Sampling the derivative allows us to determine lean direction and speed.

        :param t float: zero to one
        :return: np.array([dx, dy])
        """
        t = np.clip(t, 0, 1)
        dx = self.spline_x.derivative()(t)
        dy = self.spline_y.derivative()(t)
        return np.array([dx, dy])

# -----------------------------
# Single animation instance
# -----------------------------
class AnimationInstance:
    """
    Handles animation of a single sprite along a Spline path.
    Supports lean rotation based on velocity with damping and soft asymptotic max angle.
    """
    def __init__(self, sprite, path, duration=1.0, **kwargs):
        """
        :param sprite: The Pygame sprite to animate
        :param path: The Spline path the sprite follows
        :param duration: Duration of the animation (seconds)
        :param kwargs: Optional parameters:
            - delay: float, seconds to wait before starting
            - easing: function, easing function
            - lean: bool, whether to lean based on velocity
            - lean_delta: float, how far ahead to sample for tangent
            - damping: float, how quickly rotation interpolates
            - max_angle: float, maximum lean angle in degrees
            - velocity_scale: float, scale rotation by velocity
            - end_angle: float, final rotation angle in degrees
        """
        self.sprite = sprite
        self.path = path
        self.duration = duration
        self.elapsed = 0.0
        self.started = False
        self.complete = False
        self.base_image = self.sprite.image.convert_alpha()

        self.original_image = sprite.image.copy()
        self.current_angle = 0.0

        # Pull optional parameters from kwargs with defaults
        self.delay = kwargs.get('delay', 0.0)
        self.easing = kwargs.get('easing', lambda t: t)
        self.lean = kwargs.get('lean', False)
        self.lean_delta = kwargs.get('lean_delta', 0.2)
        self.damping = kwargs.get('damping', 0.01)
        self.max_angle = kwargs.get('max_angle', 10)
        self.velocity_scale = kwargs.get('velocity_scale', 3.0)
        self.end_angle = kwargs.get('end_angle', 0)
        self.on_complete = kwargs.get('on_complete', None)

    def update(self, dt: float):
        """
        Update the animation by dt seconds.
        :param dt: delta time in seconds
        """

        # Wait for delay before starting.
        if self.elapsed < self.delay:
            self.delay -= dt
            return

        self.elapsed += dt
        
        # idk how it works but it does. no touch.
        t = min(self.elapsed / self.duration, 1) 

        # Depending on the easing function, progress `t` along the timeline faster
        # or slower.
        t_eased = self.easing(t)

        # Set the sprites' position from the spline.
        pos = self.path.evaluate(t_eased)
        self.sprite.rect.center = pos

        # target_angle = self.current_angle
        LEVEL_OUT_START=0.9
        if self.lean:
            # Get the velocity from the deriative 
            look_t = min(t_eased + self.lean_delta, 1.0)
            velocity = self.path.derivative(look_t)
            speed = np.linalg.norm(velocity)

            # Set the angle based on the velocity's direction
            if speed > 1e-5:
                angle = np.degrees(np.arctan2(velocity[1], velocity[0]))
            else:
                angle = 0.0

            # Scale the lean angle based on the speed to make it feel more lively.
            # (Higher speed = more rotation).
            angle *= self.velocity_scale

            # As the sprite reaches the end of its path, we softly level it out to
            # prevent it from ending the animation, looking at where it's heading.
            angle *= (1 - t_eased) 

            # Hard clamping the angle would make the sprite look like it hit an invisible 
            # wall when it reaches the max angle. So instead, we interpolate
            # from the current angle to the max angle so that it softly aproaches the max
            # angle. 
            angle = self.max_angle * np.tanh(angle / self.max_angle)
            if t_eased > LEVEL_OUT_START:
                # Normalize 0 → 1 inside the level-out window
                u = (t_eased - LEVEL_OUT_START) / (1.0 - LEVEL_OUT_START)
                u = min(max(u, 0.0), 1.0)

                # Smoothstep for nice easing
                u = u * u * (3 - 2 * u)

                # Blend toward 0 degrees
                angle = (1 - u) * angle
            
            # Dampen the angle to make it no point exactly where it heading. The GOAT of
            # making the animations look nice. 
            self.current_angle += (angle - self.current_angle) * self.damping
        target_angle = self.current_angle
            
        # Apply rotation to sprite
        rotated = pygame.transform.rotozoom(
            self.base_image,
            -target_angle,
            1.0
        )
        self.sprite.image = rotated
        self.sprite.rect = rotated.get_rect(center=pos)

        # Mark as complete to signal that it no longer needs to be updated.
        if self.elapsed >= self.duration:
            self.complete = True
            self.sprite.image = self.base_image
            self.sprite.rect = self.base_image.get_rect(center=self.sprite.rect.center)
            self.current_angle = 0.0
            if self.on_complete:
                self.on_complete(self.sprite)

        # self.sprite.image = pygame.transform.rotate(self.original_image,
        #                                             -target_angle)
        # self.sprite.rect = self.sprite.image.get_rect(center=pos)

class AnimationManager:
    """
    Manages multiple simultaneous AnimationInstances.
    """
    def __init__(self):
        self.animations = []

    def add(self, sprite, positions, duration=1.0, **kwargs):
        """
        Add a new animation.

        :param sprite: The sprite to animate
        :param positions: List of positions (2 points = linear, >2 points = spline)
        :param duration: Duration in seconds
        :param kwargs: Optional parameters passed to AnimationInstance
        """
        path = Spline(positions, degree=kwargs.get('degree', 1))
        anim = AnimationInstance(sprite, path, duration, **kwargs)
        self.animations.append(anim)

    def update(self, dt: float):
        """
        Update all animations and remove complete ones.
        :param dt: delta time in seconds
        """
        for anim in self.animations:
            anim.update(dt)
        self.animations = [a for a in self.animations if not a.complete]


# -----------------------------
# Animated sprite (rectangle)
# -----------------------------
class AnimatedSprite(pygame.sprite.Sprite):
    """
    Simple rectangular sprite that can be animated.
    """
    def __init__(self, position=(0,0), color=(255,0,0), width=20, height=10):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=position)

def horizontal_arc_with_angles_deg_list(p0, p1, radius, num_points=10, above=True):
    p0 = np.array(p0, dtype=float)
    p1 = np.array(p1, dtype=float)
    
    # Distance between points
    d = np.linalg.norm(p1 - p0)
    if d/2 > radius:
        raise ValueError("Radius too small for given points")
    
    # Midpoint
    mid = (p0 + p1) / 2
    
    # Height of center above/below midpoint
    h = np.sqrt(radius**2 - (d/2)**2)
    center_y = mid[1] + h if above else mid[1] - h
    center = [mid[0], mid[1]+h]  # as list
    
    # Angles along the circle (for evenly spaced points in angle)
    angle0 = np.arctan2(p0[1]-center[1], p0[0]-center[0])
    angle1 = np.arctan2(p1[1]-center[1], p1[0]-center[0])
    angles_on_arc = np.linspace(angle0, angle1, num_points)
    
    # Points on the arc
    x = center[0] + radius * np.cos(angles_on_arc)
    y = center[1] + radius * np.sin(angles_on_arc)
    points = [(float(xi), float(yi)) for xi, yi in zip(x, y)]
    
    # Angles from each point to center in degrees
    angles_to_center_deg = [float(angle)-90 for angle in np.degrees(np.arctan2(center[1] - y, center[0] - x))]
    
    return points, angles_to_center_deg

def randColor():
    """Return a random RGB color tuple."""
    return tuple(np.random.randint(50,256,3))





# # -----------------------------
# # Pygame setup
# # -----------------------------
# WIDTH, HEIGHT = 640*2, 329*2
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# clock = pygame.time.Clock()
# all_sprites = pygame.sprite.Group()


# # Setup
# anim_manager = AnimationManager()


# # Clips front of sprites
# clip = AnimatedSprite((100,400), color=(30,30,30), width=90, height=90*1.6)

# for i in range(5):
#     sprite = AnimatedSprite((100,400), color=randColor(), width=52, height=80)
#     all_sprites.add(sprite)


# def animate_to_hand(tickets):
#     delay_ticket = 0.25
#     start_pos = (100,400)
#     stacking_offset = 10
#     h_offset = HEIGHT - tickets[0].rect.height #26
#     gap = 12 + tickets[0].rect.width
#     dur = 1


#     for i, ticket in enumerate(tickets):
#         anim_manager.add(
#             ticket,
#             [(100,400),(100 , 150 + ( i* stacking_offset))],
#             duration=dur,
#             delay=(delay_ticket*i),
#             easing=ease_out_quart,
#             degree=1,
#             lean=True
#         )
#         anim_manager.add(
#             ticket,
#             [(100, 150 + (i*stacking_offset)), (300,0), (400+i*gap,h_offset)],
#             duration=dur*2,
#             delay=(delay_ticket*i) + dur,
#             easing=ease_in_out_quint,
#             degree=2,
#             lean=True
#         )

# animate_to_hand(all_sprites.sprites())



# # for i in range(5):
# #     sprite = AnimatedSprite((100,400), color=randColor(), width=90, height=90*1.6)
# #     all_sprites.add(sprite)

# #     x = random.randint(-10,10)
# #     y = random.randint(-10,10)

# #     # Slide up (linear)
# #     anim_manager.add(sprite, [(100,400),(100 + x, 150 + (i*stacking_offset)-y)],
# #                      duration=dur,
# #                      delay=(delay_ticket*i),
# #                      easing=ease_out_quart,
# #                      degree=1,
# #                      lean=True)
    
# #     # Sweep to hand (spline with lean)
# #     p = points[i]
# #     anim_manager.add(sprite, [(100+x, 150-y + (i*stacking_offset)),(300,0), (p[0] +x, p[1]+y/2)],
# #                      duration=dur*2,
# #                      delay=(delay_ticket*i) + dur,
# #                      easing=ease_in_out_quint,
# #                      degree=2,
# #                      lean=True,
# #                      end_angle=angles_deg[i])

# # # sprites = [AnimatedSprite(position=(50,225), color=randColor()) for _ in range(5)]
# # for s in sprites:
# #     all_sprites.add(s)

# # create_fan_animations(
# #     anim_manager,
# #     sprites,
# #     start_pos=(50,225),
# #     hand_pos=(400, 300),
# #     spread=150,
# #     duration=1.0,
# #     delay_step=0.1,
# #     lean=True,
# #     damping=0.05,
# #     max_angle=15,
# #     velocity_scale=2.0,
# #     easing=ease_in_out_quint
# # )

# all_sprites.add(clip)

# # -----------------------------
# # Main loop
# # -----------------------------
# running = True
# while running:
#     dt = clock.tick(60)/1000  # Convert milliseconds to seconds
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     anim_manager.update(dt)
#     all_sprites.update(dt)

#     screen.fill((30,30,30))
#     all_sprites.draw(screen)
#     pygame.display.flip()

# pygame.quit()
