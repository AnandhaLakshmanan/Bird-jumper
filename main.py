import pygame
from pygame import display, font, image, mixer, mouse, sprite, time, transform
from pygame import event as events
from random import SystemRandom


pygame.init()
mixer.init()

clock = time.Clock()
# constants
FPS = 60
SCREEN_WIDTH = 864
SCREEN_HIEGHT = 936
random_generator = SystemRandom()

screen = display.set_mode((SCREEN_WIDTH, SCREEN_HIEGHT))
display.set_caption("Flappy Bird")

# icon image
icon_img = image.load("Resources/icon.png")
display.set_icon(icon_img)

# game state variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500  # milliseconds
last_pipe = time.get_ticks() - pipe_frequency
score = 0
pipe_passed = False
start_game = False
game_paused = False
collided = 0
fell = 0
menu_state = "paused_menu"


# load images
title_img = image.load("Resources/title.png").convert_alpha()
background_img = image.load("Resources/background.png").convert_alpha()
ground_img = image.load("Resources/ground.png").convert_alpha()
restart_img = image.load("Resources/restart.png").convert_alpha()
start_img = image.load("Resources/start.png").convert_alpha()
exit_img = image.load("Resources/exit.png").convert_alpha()
resume_img = image.load("Resources/resume.png").convert_alpha()

# load sound
scored = mixer.Sound("Resources/scored.mp3")
thump = mixer.Sound("Resources/thump.mp3")


def load_high_score():
    """
    Reads high score value from text document named "high_score.txt"
    """
    try:
        with open("high_score.txt", "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return 0


def draw_high_score(high_score):
    """
    Creates high score text with value and draws it on screen
    :param high_score: int
    """
    style = font.Font(None, 40)
    text = style.render("High Score: " + str(high_score), True, (255, 255, 255))
    screen.blit(text, (SCREEN_WIDTH // 2 + 250, 40))


def draw_score(score):
    """
    Creates score value and draws it on screen
    :param score: int
    """
    style = font.SysFont("Bauhaus 93", 60)
    img = style.render(str(score), True, (255, 255, 255))
    screen.blit(img, (SCREEN_WIDTH // 2, 20))


def save_high_score(high_score):
    """
    Write high score value to text document named "high_score.txt"
    """
    with open("high_score.txt", "w") as file:
        file.write(str(high_score))


def reset_game():
    """
    Resets bird to initial position, clears pipes & score, restart the game once restart button is pressed
    """
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(SCREEN_HIEGHT / 2)
    score = 0
    return score


class Title:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, screen):
        action = False
        # get mouse position
        pos = mouse.get_pos()

        # check mouseover button and if user is clicking it
        if self.rect.collidepoint(pos):
            if mouse.get_pressed()[0] == 1 and self.clicked is False:
                self.clicked = True
                action = True
            if mouse.get_pressed()[0] == 0:
                self.clicked = False

        # draw button on screen
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
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
        if flying:
            # bird downward movement (gravity)
            self.vel += 0.5
            self.vel = min(self.vel, 8)
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if game_over is False:
            # jump up
            left_click = mouse.get_pressed()[0]

            if left_click == 1 and self.clicked is False:
                self.clicked = True
                self.vel = -10

            if left_click == 0:
                self.clicked = False

            # bird moving animation
            self.counter += 1
            flap_cooldown = 5
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # rotate the bird
            self.image = transform.rotate(self.images[self.index], self.vel * -2)

        else:
            self.image = transform.rotate(self.images[self.index], -90)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        sprite.Sprite.__init__(self)
        self.image = pygame.image.load("Resources/pipe.png")
        self.rect = self.image.get_rect()
        # position : 1 means top & -1 means bottom
        if position == 1:
            self.image = transform.flip(self.image, False, True)
            self.rect.bottomleft = (x, y - int(pipe_gap / 2))
        if position == -1:
            self.rect.topleft = (x, y + int(pipe_gap / 2))

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


high_score = load_high_score()

# Create group for bird and pipes
bird_group = sprite.Group()
pipe_group = sprite.Group()
flappy = Bird(100, int(SCREEN_HIEGHT / 2))
bird_group.add(flappy)

# create buttons
title = Title(SCREEN_WIDTH // 2 - 270, 30, title_img, 2)
restart_btn = Button(SCREEN_WIDTH // 2 - 80, SCREEN_HIEGHT // 2 - 100, restart_img, 1.5)
rst_exit_btn = Button(SCREEN_WIDTH // 2 - 50, SCREEN_HIEGHT // 2, exit_img, 0.5)
start_btn = Button(SCREEN_WIDTH // 2 - 130, SCREEN_HIEGHT // 2 - 130, start_img, 0.8)
exit_btn = Button(SCREEN_WIDTH // 2 - 110, SCREEN_HIEGHT // 2 + 50, exit_img, 0.8)
resume_btn = Button(SCREEN_WIDTH // 2 - 105, SCREEN_HIEGHT // 2 - 150, resume_img, 0.8)
pause_menu_exit_btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HIEGHT // 2 + 50, exit_img, 0.8)


running = True
while running:
    clock.tick(FPS)

    if start_game is False:
        # draw background
        screen.blit(background_img, (0, 0))

        # draw ground
        screen.blit(ground_img, (ground_scroll, 768))
        title.draw(screen)

        # add buttons
        if start_btn.draw(screen):
            start_game = True
        if exit_btn.draw(screen):
            save_high_score(high_score)
            running = False

    # check if game is paused
    elif game_paused is True:
        # draw background
        screen.blit(background_img, (0, 0))

        # draw ground
        screen.blit(ground_img, (ground_scroll, 768))
        if menu_state == "paused_menu":
            # display pause menu
            if resume_btn.draw(screen):
                game_paused = False
            if pause_menu_exit_btn.draw(screen):
                save_high_score(high_score)
                running = False

    else:
        # draw background
        screen.blit(background_img, (0, 0))

        # draw bird
        bird_group.draw(screen)
        bird_group.update()

        # draw pipes
        pipe_group.draw(screen)

        # draw ground
        screen.blit(ground_img, (ground_scroll, 768))

        # check if bird passed the pipe, update score and high score if needed.
        if len(pipe_group) > 0:
            if (
                bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left
                and bird_group.sprites()[0].rect.right
                < pipe_group.sprites()[0].rect.right
                and pipe_passed is False
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


            # Update score and high score (if changed) on screen
            draw_score(score)
            draw_high_score(high_score)

        # check for collision between bird and pipe
        if (
            sprite.groupcollide(bird_group, pipe_group, False, False)
            or flappy.rect.top < 0
        ):
            collided += 1
            play_thump = True
            game_over = True
            if collided == 1:
                mixer.Sound.play(thump)

        # check if bird falls to ground
        if flappy.rect.bottom >= 768:
            fell += 1
            game_over = True
            flying = False
            if fell == 1:
                mixer.Sound.play(thump)

        # generate new pipes if bird is flying
        if game_over is False and flying is True:

            time_now = time.get_ticks()
            if time_now - last_pipe > pipe_frequency:
                pipe_height = random_generator.randint(-100, 100)
                top_pipe = Pipe(SCREEN_WIDTH, SCREEN_HIEGHT // 2 + pipe_height, 1)
                bot_pipe = Pipe(SCREEN_WIDTH, SCREEN_HIEGHT // 2 + pipe_height, -1)

                pipe_group.add(top_pipe)
                pipe_group.add(bot_pipe)
                last_pipe = time_now

            # scroll the ground as bird moves forward
            screen.blit(ground_img, (ground_scroll, 768))
            ground_scroll -= scroll_speed
            if abs(ground_scroll) > 35:
                ground_scroll = 0

            # update pipes to screen
            pipe_group.update()

        # Display game over menu 
        if game_over:
            if restart_btn.draw(screen):
                game_over = False
                fell = 0
                collided = 0
                score = reset_game()
            if rst_exit_btn.draw(screen):
                save_high_score(high_score)
                running = False

    for event in events.get():
        if event.type == pygame.QUIT:
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
