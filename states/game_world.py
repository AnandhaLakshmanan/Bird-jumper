from random import SystemRandom

import pygame
from pygame import mixer, sprite

from game_utils.game_sprites import Bird, Pipe
from states.pause_menu import PauseMenu
from states.state import State


class GameWorld(State):
    PIPE_FREQUENCY = 1.5
    BIRD_INITIAL_X = 100
    SCORE_Y_POS = 40
    HIGH_SCORE_Y_POS = 40
    GROUND_SCROLL_LIMIT = 35
    PIPE_HEIGHT_RANGE = (-100, 100)

    def __init__(self, game):
        """
        Initializes the GameWorld instance with the necessary properties, loads sound, creates a bird sprite
        & renders a first pair of pipes onto screen as soon as game starts.
        """
        State.__init__(self, game)
        self.random_generator = SystemRandom()
        self.last_pipe = 0
        self.score = 0
        self.passing_through_pipe = None
        try:
            self.scored = mixer.Sound("assets/scored.mp3")
            self.thump = mixer.Sound("assets/thump.mp3")
        except pygame.error as e:
            self.game.logger.error(f"Error while loading sounds: {e}")
        self.bird_group = sprite.Group()
        self.pipe_group = sprite.Group()
        self.bird = Bird(self.BIRD_INITIAL_X, self.game.HALF_SCREEN_HEIGHT - 100, game)
        self.bird_group.add(self.bird)
        self.create_pipe()

    def update(self, delta_time, actions):
        """Update game state, handle animations, and check game logic."""
        if actions["pause"]:
            self.game.logger.info("Pausing the game...")
            new_state = PauseMenu(self.game)
            new_state.enter_state()
        self.animation(delta_time, actions)
        self.check_and_update_score_when_bird_passes_pipe()
        self.check_for_game_over_conditions()
        self.game.reset_keys()

    def create_pipe(self):
        """create a top and bottom pipe with a random height offset."""
        pipe_height = self.random_generator.randint(*self.PIPE_HEIGHT_RANGE)
        top_pipe = Pipe(
            self.game.SCREEN_WIDTH,
            self.game.HALF_SCREEN_HEIGHT + pipe_height,
            "top",
            self.game,
        )
        bottom_pipe = Pipe(
            self.game.SCREEN_WIDTH,
            self.game.HALF_SCREEN_HEIGHT + pipe_height,
            "bottom",
            self.game,
        )
        self.pipe_group.add(top_pipe, bottom_pipe)

    def render(self):
        """Render bird, pipes, and score on the screen."""
        self.bird_group.draw(surface=self.game.screen)
        self.pipe_group.draw(surface=self.game.screen)
        self.game.draw_text(
            f"High Score: {self.game.high_score}",
            self.game.SCREEN_WIDTH,
            self.HIGH_SCORE_Y_POS,
            True,
        )
        self.game.draw_text(
            f"{self.score}", self.game.HALF_SCREEN_WIDTH, self.SCORE_Y_POS
        )

    def animation(self, delta_time, actions):
        """Handle bird and pipe animations, and ground scrolling."""
        self.bird_group.update(delta_time, actions)
        self.last_pipe += delta_time
        if self.last_pipe >= self.PIPE_FREQUENCY:
            self.create_pipe()
            self.last_pipe -= self.PIPE_FREQUENCY
        self.pipe_group.update(delta_time, actions)

        self.game.ground_scroll -= (
            self.game.SCROLL_SPEED * delta_time * self.game.TARGET_FPS
        )
        if abs(self.game.ground_scroll) > self.GROUND_SCROLL_LIMIT:
            self.game.ground_scroll = 0

    def check_and_update_score_when_bird_passes_pipe(self):
        """Check if bird has passed a pipe and update the score."""
        bird = self.bird_group.sprites()[0]
        pipe = self.pipe_group.sprites()[0]
        if len(self.pipe_group) > 0:
            if (
                bird.rect.left > pipe.rect.left
                and bird.rect.right < pipe.rect.right
                and not self.passing_through_pipe
            ):
                self.passing_through_pipe = True

            if self.passing_through_pipe:
                if bird.rect.left > pipe.rect.right:
                    self.score += 1
                    self.game.logger.info(f"Score: {self.score}")
                    if self.score > self.game.high_score:
                        self.game.high_score = self.score
                        self.game.logger.info(
                            f"New High score: {self.game.high_score} !!!"
                        )
                    self.scored.play()
                    self.passing_through_pipe = False

    def check_for_game_over_conditions(self):
        """Trigger game over window once bird flies out of bounds or hits a pipe"""
        if (
            sprite.groupcollide(
                groupa=self.bird_group,
                groupb=self.pipe_group,
                dokilla=False,
                dokillb=False,
            )
            or self.bird.rect.top < 0
            or self.bird.rect.bottom >= self.game.GROUND_Y_POS
        ):
            self.thump.play()
            self.game.save_high_score()
            self.game.logger.info("Game over!!!")
            from states.game_over_menu import GameOverMenu

            new_state = GameOverMenu(self.game, self.score)
            new_state.enter_state()
