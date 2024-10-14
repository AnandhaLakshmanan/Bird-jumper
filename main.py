import pygame
from pygame import display, font, image, mixer, mouse, sprite, time, transform
from pygame import event as events
from random import SystemRandom


pygame.init()
mixer.init()

clock = time.Clock()
random_generator = SystemRandom()

# Constants
FPS = 60
SCREEN_WIDTH = 864
SCREEN_HEIGHT = 936
SCREEN_HEIGHT_HALF = SCREEN_HEIGHT // 2
SCREEN_WIDTH_HALF = SCREEN_WIDTH // 2
SCROLL_SPEED = 5
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds

# Set game window dimensions and caption
screen = display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
display.set_caption("Flappy Bird")

# Game icon image
icon_img = image.load("Resources/icon.png")
display.set_icon(icon_img)

# Game state variables
ground_scroll = 0
flying = False
game_over = False
last_pipe = time.get_ticks() - PIPE_FREQUENCY
score = 0
pipe_passed = False
start_game = False
game_paused = False
collided = 0
fell = 0

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
            return int(file.read())
    except FileNotFoundError:
        return 0


def render_score_and_high_score(score, high_score):
    """
    Renders the current score and the highest score on the game screen.

    :param score: The player's current score (int) during gameplay.
    :param high_score: The highest score achieved by the player (int) across all sessions.
    """
    high_score_style = font.Font(None, 40)
    score_style = font.SysFont("Bauhaus 93", 60)
    high_score_txt = high_score_style.render(f"High Score: {high_score}", True, (255, 255, 255))
    score_txt = score_style.render(f"{score}", True, (255, 255, 255))
    screen.blit(high_score_txt, (SCREEN_WIDTH_HALF + 250, 40))
    screen.blit(score_txt, (SCREEN_WIDTH_HALF, 20))


def save_high_score(high_score):
    """
    Saves the high score to a text file ('high_score.txt').

    :param high_score: The highest score (int) that should be saved.
    """
    with open("high_score.txt", "w") as file:
        file.write(str(high_score))


def reset_game():
    """
    Resets the game state to its initial conditions for a fresh start. This function clears the pipes from the screen, repositions the bird 
    to its starting point, and resets the score. 
    
    :return: score(int).
    """
    pipe_group.empty()
    bird.rect.x = 100
    bird.rect.y = SCREEN_HEIGHT_HALF
    score = 0
    return score


def draw_background_and_ground():
    """
    Draws the game background and the ground on the screen.
    """
    # Draw background
    screen.blit(background_img, (0, 0))
    # Draw ground
    screen.blit(ground_img, (ground_scroll, 768))


class Element():
    def __init__(self, x, y, image, scale):
        """
        Initializes an Element object with position, image, and scaling.
        
        :param x: X-coordinate for the top-left corner of the element.
        :param y: Y-coordinate for the top-left corner of the element.
        :param image: The image surface to display for the element.
        :param scale: Scaling factor for resizing the image.
        """
        width = image.get_width()
        height = image.get_height()
        self.image = transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, screen):
        """
        Draws the element onto the given screen surface.

        :param screen: The surface where the element will be drawn.
        """
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Button(Element):
    def __init__(self, x, y, image, scale):
        """
        Initializes a Button object, inheriting from Element, with additional click handling.
        
        :param x: X-coordinate for the button's top-left corner.
        :param y: Y-coordinate for the button's top-left corner.
        :param image: The image surface for the button.
        :param scale: Scaling factor for resizing the button image.
        """
        super().__init__(x, y, image, scale)
        self.clicked = False

    def check_if_button_is_pressed(self, screen):
        """
        Checks if the button is pressed, updates its state, and returns the action.

        :param screen: The surface where the button will be checked and drawn.
        :return: True if the button is pressed, False otherwise.
        """
        action = False
        # Get mouse position on screen
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
    def __init__(self, x, y):
        """
        Initializes a Bird object with images for animation and sets the initial position.
        
        :param x: X-coordinate for the bird's center.
        :param y: Y-coordinate for the bird's center.
        """
        sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = image.load(f"Resources/bird{num}.png")
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
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
            # Jump up if user uses mouse left click
            left_click = mouse.get_pressed()[0]

            if left_click == 1 and not self.clicked:
                self.clicked = True
                self.vel = -10

            if left_click == 0:
                self.clicked = False

            # Bird moving animation
            self.counter += 1
            flap_cooldown = 5
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # Rotate the bird
            self.image = transform.rotate(self.images[self.index], self.vel * -2)

        else:
            # Make the bird face down when it falls to ground / collides with pipe
            self.image = transform.rotate(self.images[self.index], -90)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        """
        Initializes a Pipe object with its position and whether it's a top or bottom pipe.
        
        :param x: X-coordinate for the pipe's center.
        :param y: Y-coordinate for the pipe's center.
        :param position: 1 for top pipe, -1 for bottom pipe.
        """
        sprite.Sprite.__init__(self)
        self.image = pygame.image.load("Resources/pipe.png")
        self.rect = self.image.get_rect()
        pipe_gap_half = PIPE_GAP // 2
        if position == 1:
            self.image = transform.flip(self.image, False, True)
            self.rect.bottomleft = (x, y - pipe_gap_half)
        if position == -1:
            self.rect.topleft = (x, y + pipe_gap_half)

    def update(self):
        """
        Updates the pipe's position, moving it left across the screen, and removes it if off-screen.
        """
        self.rect.x -= SCROLL_SPEED
        if self.rect.right < 0:
            self.kill()


high_score = load_high_score()

# Create group for bird and pipes
bird_group = sprite.Group()
pipe_group = sprite.Group()
bird = Bird(100, SCREEN_HEIGHT_HALF)
bird_group.add(bird)

# Create UI buttons
title = Element(SCREEN_WIDTH_HALF - 270, 30, title_img, 2)
restart_btn = Button(SCREEN_WIDTH_HALF - 80, SCREEN_HEIGHT_HALF - 100, restart_img, 1.5)
restart_exit_btn = Button(SCREEN_WIDTH_HALF - 50, SCREEN_HEIGHT_HALF, exit_img, 0.5)
start_btn = Button(SCREEN_WIDTH_HALF - 130, SCREEN_HEIGHT_HALF - 130, start_img, 0.8)
exit_btn = Button(SCREEN_WIDTH_HALF - 110, SCREEN_HEIGHT_HALF + 50, exit_img, 0.8)
resume_btn = Button(SCREEN_WIDTH_HALF - 105, SCREEN_HEIGHT_HALF - 150, resume_img, 0.8)
pause_menu_exit_btn = Button(SCREEN_WIDTH_HALF - 100, SCREEN_HEIGHT_HALF + 50, exit_img, 0.8)


running = True
while running:
    clock.tick(FPS)

    # Display start menu
    if not start_game:
        draw_background_and_ground()
        title.draw(screen)
        start_btn.draw(screen)
        exit_btn.draw(screen)

        if start_btn.check_if_button_is_pressed(screen):
            start_game = True
        if exit_btn.check_if_button_is_pressed(screen):
            save_high_score(high_score)
            running = False

    # Display pause menu
    elif game_paused and not game_over and flying:
        draw_background_and_ground()
        resume_btn.draw(screen)
        pause_menu_exit_btn.draw(screen)
        
        if resume_btn.check_if_button_is_pressed(screen):
            game_paused = False
        if pause_menu_exit_btn.check_if_button_is_pressed(screen):
            save_high_score(high_score)
            running = False

    else:
        # Draw background
        screen.blit(background_img, (0, 0))

        # Draw bird
        bird_group.draw(screen)
        bird_group.update()

        # Draw pipes
        pipe_group.draw(screen)

        # Draw ground
        screen.blit(ground_img, (ground_scroll, 768))

        # Check if bird passed the pipe, update score and high score (if needed).
        if len(pipe_group) > 0:
            if (
                bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left
                and bird_group.sprites()[0].rect.right
                < pipe_group.sprites()[0].rect.right
                and not pipe_passed
            ):
                pipe_passed = True

            if pipe_passed:
                if (
                    bird_group.sprites()[0].rect.left
                    > pipe_group.sprites()[0].rect.right
                ):
                    score += 1
                    if score > high_score:
                        high_score = score
                    mixer.Sound.play(scored)
                    pipe_passed = False

            render_score_and_high_score(score, high_score)

        # Check for collision between bird and pipe
        if (
            sprite.groupcollide(bird_group, pipe_group, False, False)
            or bird.rect.top < 0
        ):
            collided += 1
            play_thump = True
            game_over = True
            if collided == 1:
                mixer.Sound.play(thump)

        # Check if bird fell to ground
        if bird.rect.bottom >= 768:
            fell += 1
            game_over = True
            flying = False
            if fell == 1:
                mixer.Sound.play(thump)

        # Generate new pipes if bird is flying
        if not game_over and flying:
            time_now = time.get_ticks()
            if time_now - last_pipe > PIPE_FREQUENCY:
                pipe_height = random_generator.randint(-100, 100)
                top_pipe = Pipe(SCREEN_WIDTH, SCREEN_HEIGHT_HALF + pipe_height, 1)
                bot_pipe = Pipe(SCREEN_WIDTH, SCREEN_HEIGHT_HALF + pipe_height, -1)

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

        # Display game over menu 
        if game_over:
            restart_btn.draw(screen)
            restart_exit_btn.draw(screen)
            if restart_btn.check_if_button_is_pressed(screen):
                game_over = False
                fell = 0
                collided = 0
                score = reset_game()
            if restart_exit_btn.check_if_button_is_pressed(screen):
                save_high_score(high_score)
                running = False

    # Check for events
    for event in events.get():
        if (
            event.type == pygame.QUIT or
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
        ):
            running = False

        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and flying is False
            and game_over is False
        ):
            flying = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_paused = True

    pygame.display.update()


pygame.quit()
