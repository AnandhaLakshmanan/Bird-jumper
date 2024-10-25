import os
import time

import pygame
from pygame import display, image

from game_utils.logger import Logger
from states.title_screen import Title


class Game:
    FPS = 60
    SCREEN_WIDTH, SCREEN_HEIGHT = 864, 936
    HALF_SCREEN_HEIGHT, HALF_SCREEN_WIDTH = SCREEN_HEIGHT // 2, SCREEN_WIDTH // 2
    SCROLL_SPEED = 5
    TARGET_FPS = 60
    WHITE = (255, 255, 255)
    HIGH_SCORE_X_OFFSET = 20
    GROUND_Y_POS = 768
    ASSETS_DIR = os.path.join("assets")

    def __init__(self, logger):
        """
        Initializes the Game instance with the necessary properties, loads assets & high score,
        sets initial state to title screen
        """
        self.logger = logger
        self.logger.info("Game initialized...")
        pygame.init()
        self.running = self.playing = True
        self.actions = {"jump": False, "pause": False}
        self.dt, self.prev_time = 0, 0
        self.screen = display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.SRCALPHA
        )
        display.set_caption(title="Flappy Bird")
        self.ground_scroll = 0
        self.font = pygame.font.SysFont(name="Futura", size=40)
        self.high_score = self.load_high_score()
        try:
            self.icon_img = image.load(os.path.join(self.ASSETS_DIR, "icon.png"))
            self.background_img = image.load(
                os.path.join(self.ASSETS_DIR, "background.png")
            ).convert_alpha()
            self.ground_img = image.load(
                os.path.join(self.ASSETS_DIR, "ground.png")
            ).convert_alpha()
            self.title_image = image.load(
                os.path.join(self.ASSETS_DIR, "Title.png")
            ).convert_alpha()
            self.start_button_image = image.load(
                os.path.join(self.ASSETS_DIR, "start.png")
            ).convert_alpha()
            self.bird_images = [
                image.load(
                    os.path.join(self.ASSETS_DIR, f"bird{num}.png")
                ).convert_alpha()
                for num in range(1, 4)
            ]
            self.pipe_image = image.load(
                os.path.join(self.ASSETS_DIR, "pipe.png")
            ).convert_alpha()
            self.resume_button_image = image.load(
                os.path.join(self.ASSETS_DIR, "resume.png")
            ).convert_alpha()
            self.restart_button_image = image.load(
                os.path.join(self.ASSETS_DIR, "restart.png")
            ).convert_alpha()
            self.exit_button_image = image.load(
                os.path.join(self.ASSETS_DIR, "exit.png")
            ).convert_alpha()
        except pygame.error as e:
            self.logger.error(f"Error while loading assets {e}")
        else:
            display.set_icon(self.icon_img)
        self.state_stack = []
        self.title_screen = Title(self)
        self.state_stack.append(self.title_screen)
        self.clock = pygame.time.Clock()

    def game_loop(self):
        """Main game loop"""
        while self.playing:
            self.clock.tick(self.FPS)
            self.get_dt()
            self.get_events()
            self.render()
            self.update()
            self.reset_keys()
        self.logger.info("Exiting the game...")

    def get_events(self):
        """Handle all player input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                self.running, self.playing = False, False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.actions["jump"] = True

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.actions["pause"] = True

    def update(self):
        """Update the current state"""
        self.state_stack[-1].update(self.dt, self.actions)

    def render(self):
        """Render the current frame onto screen"""
        self.screen.blit(source=self.background_img, dest=(0, 0))
        self.screen.blit(
            source=self.ground_img, dest=(self.ground_scroll, self.GROUND_Y_POS)
        )
        self.state_stack[-1].render()
        pygame.display.flip()

    def get_dt(self):
        """Calculate delta time (time between each frame) for smooth animations"""
        now = time.time()
        self.dt = now - self.prev_time
        self.prev_time = now

    def draw_text(self, text, x, y, in_game_high_score=False):
        """Draws text on the screen"""
        text_surface = self.font.render(text, True, self.WHITE)
        # For in-game high score to be always visible inside the screen
        if in_game_high_score:
            x = x - text_surface.get_width() - self.HIGH_SCORE_X_OFFSET
        self.screen.blit(source=text_surface, dest=(x, y))

    def reset_keys(self):
        """Reset action keys."""
        for action in self.actions:
            self.actions[action] = False

    def load_high_score(self):
        """
        Loads the highest score from a text file named 'high_score.txt'.

        :return: high score(int) or 0 if the file does not exist.
        """
        try:
            with open("high_score.txt", "r") as file:
                current_high_score = int(file.read())
                self.logger.info(
                    f"Loading the high score: {current_high_score} from text file"
                )
                return current_high_score
        except FileNotFoundError:
            self.logger.info("File not found. Returning 0 as high score")
            return 0

    def save_high_score(self):
        """
        Saves the high score to a text file ('high_score.txt').
        """
        with open("high_score.txt", "w") as file:
            self.logger.info(
                f"Saving the high score: {self.high_score} to the text file"
            )
            file.write(str(self.high_score))


if __name__ == "__main__":
    log = Logger(name="Flappy-Bird").get_logger()
    g = Game(log)
    while g.running:
        g.game_loop()
