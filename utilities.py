import pygame
from typing import Callable, Optional, Tuple, List, Any

# pygame.mixer.init()


class AnimationScheduler:
    """General Animation scheduler for Pygame"""

    class Animation:
        def __init__(self, obj: Any, target_pos: Tuple[int,int], duration: float,
                     start_time: float = 0.0, start_pos: Optional[Tuple[int,int]] = None,
                     get_position: Optional[Callable[[], Tuple[int,int]]] = None):
            """
            Represents a single animation applied to an object.

            Attributes
            ----------
                obj : Any
                    The object being moved. Must have either a `.rect` or `.position`.
                target_pos : pygame.Vector2
                    Final position the object will animate to.
                duration : float
                    Duration of the animation in seconds.
                start_time : float
                    When the animation began.
                start_pos : Optional[pygame.Vector2]
                    Starting position of the animation. If None, the object's current position is used.
                get_position : Optional[Callable[[], Tuple[int, int]]]
                    Optional function used to query the object's position.
                elapsed : float
                    Time since animation started.
            """
            self.obj = obj
            self.target_pos = pygame.Vector2(target_pos)
            self.duration = max(duration, 0.0001)
            self.start_time = start_time
            self.start_pos = pygame.Vector2(start_pos) if start_pos else None
            self.get_position = get_position
            self.elapsed = 0.0
            self.started = False

        def start(self):
            """Initialize start_pos if not set (lazy evaluation)."""
            if self.start_pos is None:
                if self.get_position:
                    self.start_pos = pygame.Vector2(self.get_position())
                elif hasattr(self.obj, "rect"):
                    self.start_pos = pygame.Vector2(self.obj.rect.topleft)
                elif hasattr(self.obj, "position"):
                    self.start_pos = pygame.Vector2(self.obj.position)
                else:
                    raise ValueError("Object has no rect or position for animation.")
            self.started = True

        def update(self, dt: float):
            if not self.started:
                self.start()
            self.elapsed += dt
            t = min(self.elapsed / self.duration, 1.0)
            eased_t = t*t*(3-2*t)  # smoothstep
            new_pos = self.start_pos.lerp(self.target_pos, eased_t)

            # Apply new position
            if hasattr(self.obj, "rect"):
                self.obj.rect.topleft = (new_pos.x, new_pos.y)
            elif hasattr(self.obj, "position"):
                self.obj.position = (new_pos.x, new_pos.y)
            else:
                raise ValueError("Object has no rect or position for animation.")

            return t >= 1.0 

    def __init__(self):
        """
        Initialize the animation scheduler.

        Attributes
        ----------
        animations : list[Animation]
            Queued animations to be executed.
        current_time : float
            Total running time elapsed of all animations queued. Used to check for starting delays.
        """
        self.animations: List[AnimationScheduler.Animation] = []
        self.current_time: float = 0.0

    def add(self, obj: Any, target_pos: Tuple[int,int], duration: float,
            start_time: float = 0.0, start_pos: Optional[Tuple[int,int]] = None,
            get_position: Optional[Callable[[], Tuple[int,int]]] = None):
        """
        Queue a new animation.

        Parameters
        ----------
        obj : Any
            Object to animate.
        target_pos : tuple[int, int]
            Final coordinates.
        duration : float
            Animation duration in seconds.
        start_time : float, optional
            Delay before animation begins.
        start_pos : tuple[int, int] | None, optional
            Override starting position.
        get_position : callable | None, optional
            Lazy starting position.
        """
        anim = AnimationScheduler.Animation(obj, target_pos, duration, start_time, start_pos, get_position)
        self.animations.append(anim)

    def update(self, dt: float):
        """
        Update all queued animations.

        Parameters
        ----------
        dt : float
            Time since last update.

        Notes
        -----
        Pops animation from the queue wheb completed
        """
        self.current_time += dt
        finished = []
        for anim in self.animations:
            if self.current_time >= anim.start_time:
                done = anim.update(dt)
                if done:
                    finished.append(anim)
        for anim in finished:
            self.animations.remove(anim)


class BaseSprite(pygame.sprite.Sprite):
    """
    Base class for sprites using an image.

    Attributes
    ----------
    image : pygame.Surface
        The sprite's image surface.
    rect : pygame.Rect
        The rectangle representing the sprite's position and size.
    """

    def __init__(self, image_path: str, pos: Tuple[int, int] = (0, 0), scale: float = 4) -> None:
        """
        Initialize a BaseSprite with an image.

        Parameters
        ----------
        image_path : str
            Path to the image file.
        pos : tuple of int, optional
            Top-left position of the sprite. Default is (0,0).
        scale : float, optional
            Scaling factor for the image. Default is 4.
        """
        super().__init__()
        # Load and scale the image
        self.image: pygame.Surface = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale_by(self.image, scale)
        # Create rect for positioning
        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)
    
    def update(self, dt: float) -> None:
        """
        Update the sprite.

        Parameters
        ----------
        dt : float
            Time elapsed since last update in seconds.

        Notes
        -----
        Override this method in subclasses to provide custom behavior.
        """
        pass  # Override if needed


class Button(BaseSprite):
    """
    Interactive button sprite that can call functions on click and release.
    """

    def __init__(self, image_path: str, pos: Tuple[int, int], scale: float=4, name=None,
                 on_click_func: Optional[Callable[[Any], None]]=None,
                 on_release_func: Optional[Callable[[Any], None]]=None,
                 sound_path=None
                 ) -> None:

        super().__init__(image_path, pos, scale)

        self.name = name
        self.on_click_func = on_click_func
        self.on_release_func = on_release_func

        # Safe sound loading
        self.click_sound = pygame.mixer.Sound(sound_path) if sound_path else None


    def on_release(self, *args) -> None:
        """Handle button release event."""
        if self.on_release_func:
            self.on_release_func(self)


    def on_click(self, *args) -> None:
        """Handle button click event."""

        # Play sound if present
        if self.click_sound:
            self.click_sound.play()

        # Call user callback
        if self.on_click_func:
            self.on_click_func(self)


    def handle_event(self, event: pygame.event.Event, local_mouse: Tuple[int, int]) -> None:
        """Check for mouse events and trigger callbacks."""
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(local_mouse):
            self.on_click()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.on_release()


    def __repr__(self) -> str:
        return f"Button(name={self.name!r}, pos={self.rect.topleft}, rect={self.rect})"

    def __str__(self) -> str:
        return f"Button '{self.name}' at {self.rect.topleft}"

