import logging
from random import SystemRandom

import pygame
from pygame import display
from pygame import event as events
from pygame import font, image, mixer, mouse, sprite, time, transform

pygame.init()

clock = time.Clock()
random_generator = SystemRandom()

# Constants
FPS = 60
SCREEN_WIDTH = 864
SCREEN_HEIGHT = 936
HALF_SCREEN_HEIGHT = SCREEN_HEIGHT // 2
HALF_SCREEN_WIDTH = SCREEN_WIDTH // 2
SCROLL_SPEED = 5
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds

# Set game window dimensions and caption
screen = display.set_mode(size=(SCREEN_WIDTH, SCREEN_HEIGHT))
display.set_caption(title="Flappy Bird")

# Load and set game window icon image
icon_img = image.load("Resources/icon.png")
display.set_icon(icon_img)

# Game state variables
ground_scroll = 0
flying = False
game_over = False
last_pipe = time.get_ticks() - PIPE_FREQUENCY
score = 0
passing_through_pipe = False
start_game = False
game_paused = False
collided = 0
fell = 0
running = True

# Load images
title_img = image.load("Resources/title.png").convert_alpha()
background_img = image.load("Resources/background.png").convert_alpha()
ground_img = image.load("Resources/ground.png").convert_alpha()
restart_img = image.load("Resources/restart.png").convert_alpha()
start_img = image.load("Resources/start.png").convert_alpha()
exit_img = image.load("Resources/exit.png").convert_alpha()
resume_img = image.load("Resources/resume.png").convert_alpha()

# Load sound
scored = mixer.Sound("Resources/scored.mp3")
thump = mixer.Sound("Resources/thump.mp3")


def load_high_score():
    """
    Loads the highest score from a text file named 'high_score.txt'.

    :return: high score(int) or 0 if the file does not exist.
    """
    try:
        with open("high_score.txt", "r") as file:
            current_high_score = int(file.read())
            logger.info(f"High score loaded from file: {current_high_score}")
            return current_high_score
    except FileNotFoundError:
        logger.warning("High score file not found. Defaulting to 0.")
        return 0


def render_score_and_high_score(current_score, current_high_score):
    """
    Renders the current score and the highest score onto the game screen.

    :param current_score: The player's current score (int) during gameplay.
    :param current_high_score: The highest score achieved by the player (int) across all sessions.
    """
    high_score_style = font.Font(size=40)
    score_style = font.SysFont(name="Bauhaus 93", size=60)
    high_score_txt = high_score_style.render(
        f"High Score: {current_high_score}", True, (255, 255, 255)
    )
    score_txt = score_style.render(f"{current_score}", True, (255, 255, 255))
    high_score_txt_x = SCREEN_WIDTH - high_score_txt.get_width() - 20
    screen.blit(high_score_txt, (high_score_txt_x, 40))
    screen.blit(score_txt, (HALF_SCREEN_WIDTH, 20))


def save_high_score(current_high_score):
    """
    Saves the high score to a text file ('high_score.txt').

    :param current_high_score: The highest score (int) that should be saved.
    """
    with open("high_score.txt", "w") as file:
        logger.info(f"Saving High score: {current_high_score} to file")
        file.write(str(current_high_score))


def reset_game():
    """
    Resets the game state to its initial conditions for a fresh start.
    This function clears the pipes from the screen, repositions the bird to its starting point,
    and resets the score to 0.

    :return: 0 (score(int)).
    """
    pipe_group.empty()
    bird.rect.x = 100
    bird.rect.y = HALF_SCREEN_HEIGHT
    return 0


def draw_background_and_ground():
    """
    Draws the game background and the ground on the screen.
    """
    # Draw background
    screen.blit(source=background_img, dest=(0, 0))
    # Draw ground
    screen.blit(source=ground_img, dest=(ground_scroll, 768))


def get_logger():
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(filename="game.log", mode="w")
    formatter = logging.Formatter(
        "{asctime}: {name}: {levelname}: {message}", style="{", datefmt="%Y-%m-%d %H:%M"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)
    return log


class Element:
    def __init__(self, x_coord, y_coord, img_surface, scale_factor):
        """
        Initializes an Element object with position, image, and scaling.

        :param x_coord: X-coordinate for the top-left corner of the element.
        :param y_coord: Y-coordinate for the top-left corner of the element.
        :param img_surface: The image surface to display for the element.
        :param scale_factor: Scaling factor for resizing the image.
        """
        width = img_surface.get_width()
        height = img_surface.get_height()
        self.image = transform.scale(
            surface=img_surface,
            size=(int(width * scale_factor), int(height * scale_factor)),
        )
        self.rect = self.image.get_rect()
        self.rect.topleft = (x_coord, y_coord)

    def draw(self):
        """
        Draws the element onto the screen surface.
        """
        screen.blit(source=self.image, dest=(self.rect.x, self.rect.y))


class Button(Element):
    def __init__(self, x_coord, y_coord, img_surface, scale_factor):
        """
        Initializes a Button object, inheriting from Element, with additional click handling.
        :param x_coord: X-coordinate for the button's top-left corner.
        :param y_coord: Y-coordinate for the button's top-left corner.
        :param img_surface: The image surface for the button.
        :param scale_factor: Scaling factor for resizing the button image.
        """
        super().__init__(x_coord, y_coord, img_surface, scale_factor)
        self.clicked = False

    def check_if_button_is_pressed(self):
        """
        Checks if the button is pressed, updates its state, and returns the action.
        :return: True if the button is pressed, False otherwise.
        """
        action = False
        pos = mouse.get_pos()
        # Check if user has mouse over the button & if it is being clicked
        if self.rect.collidepoint(pos):
            if mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True
            if mouse.get_pressed()[0] == 0:
                self.clicked = False
        return action


class Bird(pygame.sprite.Sprite):
    def __init__(self, x_coord, y_coord):
        """
        Initializes a Bird object with images for animation and sets the initial position.

        :param x_coord: X-coordinate for the bird's center.
        :param y_coord: Y-coordinate for the bird's center.
        """
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = image.load(f"Resources/bird{num}.png")
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x_coord, y_coord)
        self.vel = 0
        self.clicked = False

    def update(self):
        """
        Updates the bird's movement, handles jumping, moving & rotation animations.
        """
        if flying:
            # Bird downward movement (gravity)
            self.vel += 0.5
            self.vel = min(self.vel, 8)
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if not game_over:
            # Jump up only if user uses left mouse click
            left_click = mouse.get_pressed()[0]
            if left_click == 1 and not self.clicked:
                self.clicked = True
                self.vel = -10

            if left_click == 0:
                self.clicked = False

            # Bird flapping animation
            self.counter += 1
            flap_cooldown = 5
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0

            # Rotate the bird
            self.image = transform.rotate(
                surface=self.images[self.index], angle=self.vel * -2
            )

        else:
            # Make the bird face down when it falls to ground / collides with pipe
            self.image = transform.rotate(surface=self.images[self.index], angle=-90)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x_coord, y_coord, position):
        """
        Initializes a Pipe object with its position and whether it's a top or bottom pipe.

        :param x_coord: X-coordinate for the pipe's center.
        :param y_coord: Y-coordinate for the pipe's center.
        :param position: 1 for top pipe, -1 for bottom pipe.
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("Resources/pipe.png")
        self.rect = self.image.get_rect()
        pipe_gap_half = PIPE_GAP // 2
        if position == 1:
            self.image = transform.flip(surface=self.image, flip_x=False, flip_y=True)
            self.rect.bottomleft = (x_coord, y_coord - pipe_gap_half)
        if position == -1:
            self.rect.topleft = (x_coord, y_coord + pipe_gap_half)

    def update(self):
        """
        Updates the pipe's position, moving it left across the screen, and removes it if off-screen.
        """
        self.rect.x -= SCROLL_SPEED
        if self.rect.right < 0:
            self.kill()


# Create group for bird and pipes
bird_group = sprite.Group()
pipe_group = sprite.Group()

bird = Bird(100, HALF_SCREEN_HEIGHT)
bird_group.add(bird)

# Create UI buttons
title = Element(HALF_SCREEN_WIDTH - 270, 30, title_img, 2)
restart_btn = Button(HALF_SCREEN_WIDTH - 80, HALF_SCREEN_HEIGHT - 100, restart_img, 1.5)
restart_menu_exit_btn = Button(
    HALF_SCREEN_WIDTH - 50, HALF_SCREEN_HEIGHT, exit_img, 0.5
)
start_btn = Button(HALF_SCREEN_WIDTH - 130, HALF_SCREEN_HEIGHT - 130, start_img, 0.8)
exit_btn = Button(HALF_SCREEN_WIDTH - 110, HALF_SCREEN_HEIGHT + 50, exit_img, 0.8)
resume_btn = Button(HALF_SCREEN_WIDTH - 105, HALF_SCREEN_HEIGHT - 150, resume_img, 0.8)
pause_menu_exit_btn = Button(
    HALF_SCREEN_WIDTH - 100, HALF_SCREEN_HEIGHT + 50, exit_img, 0.8
)

logger = get_logger()
logger.info("Game: Flappy Bird initialized.")
high_score = load_high_score()
while running:
    clock.tick(FPS)
    # Display start menu
    if not start_game:
        draw_background_and_ground()
        title.draw()
        start_btn.draw()
        exit_btn.draw()
        if start_btn.check_if_button_is_pressed():
            logger.info("Start button pressed. Game started...")
            start_game = True
            flying = True
        if exit_btn.check_if_button_is_pressed():
            logger.info("Exit button pressed. Game is closing...")
            save_high_score(high_score)
            running = False

    # Display pause menu
    elif game_paused and not game_over and flying:
        draw_background_and_ground()
        resume_btn.draw()
        pause_menu_exit_btn.draw()
        if resume_btn.check_if_button_is_pressed():
            logger.info("Resume button pressed. Game is resumed...")
            game_paused = False
        if pause_menu_exit_btn.check_if_button_is_pressed():
            logger.info("Exit button pressed. Game is closing...")
            save_high_score(high_score)
            running = False

    else:
        # Draw background
        screen.blit(background_img, (0, 0))

        # Draw bird
        bird_group.draw(surface=screen)
        bird_group.update()

        # Draw pipes
        pipe_group.draw(surface=screen)

        # Draw ground
        screen.blit(ground_img, (ground_scroll, 768))

        # Generate new pipes as bird moves forward.
        if not game_over and flying:
            time_now = time.get_ticks()
            if time_now - last_pipe > PIPE_FREQUENCY:
                pipe_height = random_generator.randint(-100, 100)
                top_pipe = Pipe(SCREEN_WIDTH, HALF_SCREEN_HEIGHT + pipe_height, 1)
                bot_pipe = Pipe(SCREEN_WIDTH, HALF_SCREEN_HEIGHT + pipe_height, -1)
                pipe_group.add(top_pipe)
                pipe_group.add(bot_pipe)
                last_pipe = time_now

            # Scroll the ground as bird moves forward
            screen.blit(ground_img, (ground_scroll, 768))
            ground_scroll -= SCROLL_SPEED
            if abs(ground_scroll) > 35:
                ground_scroll = 0

            # Update pipes to screen
            pipe_group.update()

        # Check if bird passed the pipe, update score and high score (if needed).
        if len(pipe_group) > 0:
            if (
                bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left
                and bird_group.sprites()[0].rect.right
                < pipe_group.sprites()[0].rect.right
                and not passing_through_pipe
            ):
                passing_through_pipe = True

            if passing_through_pipe:
                if (
                    bird_group.sprites()[0].rect.left
                    > pipe_group.sprites()[0].rect.right
                ):
                    score += 1
                    logger.info(f"Score increased: {score}")
                    if score > high_score:
                        high_score = score
                        logger.info(f"New high score: {high_score}")
                    scored.play()
                    passing_through_pipe = False

            render_score_and_high_score(score, high_score)

        # Game over once bird collides with a pipe or if bird goes above the scrren
        if (
            sprite.groupcollide(
                groupa=bird_group, groupb=pipe_group, dokilla=False, dokillb=False
            )
            or bird.rect.top < 0
        ):
            collided += 1
            game_over = True
            if collided == 1:
                logger.warning(
                    "Collision detected: Bird hit a pipe or flew out of bounds."
                )
                thump.play()

        # Check if bird fell to ground
        if bird.rect.bottom >= 768:
            fell += 1
            game_over = True
            flying = False
            if fell == 1:
                logger.warning("Bird hit the ground.")
                thump.play()

        # Display game over menu
        if game_over:
            restart_btn.draw()
            restart_menu_exit_btn.draw()
            if restart_btn.check_if_button_is_pressed():
                logger.info("Restart button pressed. Game is reset...")
                game_over = False
                fell = 0
                collided = 0
                score = reset_game()
            if restart_menu_exit_btn.check_if_button_is_pressed():
                logger.info("Exit button pressed. Game is closing...")
                save_high_score(high_score)
                running = False

    # Check for events
    for event in events.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            logger.info("Game window closed.")
            running = False

        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and not flying
            and not game_over
        ):
            flying = True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            logger.info("Game paused.")
            game_paused = True

    pygame.display.update()
