import pygame
from pygame import transform


class Bird(pygame.sprite.Sprite):
    MAX_FALL_SPEED = 8
    ROTATION_FACTOR = -2
    JUMP_VELOCITY = -7
    FLAP_ANIMATION_DURATION = 0.1

    def __init__(self, x_coord, y_coord, game):
        """
        Initializes a Bird object with images for animation and sets the initial position.

        :param x_coord: X-coordinate for the bird's center.
        :param y_coord: Y-coordinate for the bird's center.
        """
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.images = self.game.bird_images
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x_coord, y_coord)
        self.vel = 0
        self.animation_timer = 0

    def update(self, delta_time, actions):
        """
        Updates the bird's movement, handles jumping & flapping animation.
        """
        # Bird downward movement (gravity)
        self.vel += 0.5 * delta_time * self.game.TARGET_FPS
        self.vel = min(self.vel, self.MAX_FALL_SPEED)
        if self.rect.bottom < self.game.GROUND_Y_POS:
            self.rect.y += int(self.vel)

        # Jump if user uses left mouse click
        if actions["jump"]:
            self.vel = self.JUMP_VELOCITY

        # Bird flapping animation
        self.animation_timer += delta_time
        if self.animation_timer >= self.FLAP_ANIMATION_DURATION:
            self.animation_timer = 0
            self.index = (self.index + 1) % len(self.images)

        # Rotate the bird based on velocity
        self.image = transform.rotate(
            surface=self.images[self.index], angle=self.vel * self.ROTATION_FACTOR
        )


class Pipe(pygame.sprite.Sprite):
    PIPE_VERTICAL_GAP = 150

    def __init__(self, x, y, pipe_position, game):
        """
        Initializes a Pipe object with its position, creates a top or bottom pipe.

        :param x: X-coordinate for the pipe.
        :param y: Y-coordinate for the pipe.
        :param pipe_position: pipe position.
        """
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = self.game.pipe_image
        self.rect = self.image.get_rect()
        pipe_gap_half = self.PIPE_VERTICAL_GAP // 2
        if pipe_position == "top":
            self.image = transform.flip(surface=self.image, flip_x=False, flip_y=True)
            self.rect.bottomleft = (x, y - pipe_gap_half)
        if pipe_position == "bottom":
            self.rect.topleft = (x, y + pipe_gap_half)

    def update(self, delta_time, actions):
        """
        Updates the pipe's position, moving it left across the screen, and removing it once it is off-screen
        """
        self.rect.x -= self.game.SCROLL_SPEED * delta_time * self.game.TARGET_FPS
        if self.rect.right < 0:
            self.kill()
