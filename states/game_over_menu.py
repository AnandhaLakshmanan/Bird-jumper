from game_utils.ui_elements import Button
from states.game_world import GameWorld
from states.state import State


class GameOverMenu(State):
    def __init__(self, game, score):
        """
        Initializes the Game Over screen state with UI elements.
        :param game: Reference to the main game object.
        """
        State.__init__(self, game)
        self.score = score
        self.restart_button = Button(
            self.game.HALF_SCREEN_WIDTH,
            self.game.HALF_SCREEN_HEIGHT - 100,
            self.game.restart_button_image,
            1.5,
            self.game,
        )
        self.restart_menu_exit_btn = Button(
            self.game.HALF_SCREEN_WIDTH,
            self.game.HALF_SCREEN_HEIGHT,
            self.game.exit_button_image,
            0.5,
            self.game,
        )

    def update(self, delta_time, actions):
        """
        Updates the Game Over screen by checking button presses and handling state transitions.
        :param delta_time: Time elapsed since the last frame.
        :param actions: Dictionary of user actions (like key presses, mouse clicks).
        """
        if self.restart_button.check_if_button_is_pressed():
            self.exit_state()
            self.game.logger.info("Restarting the Game...")
            new_state = GameWorld(self.game)
            new_state.enter_state()
        elif self.restart_menu_exit_btn.check_if_button_is_pressed():
            self.game.running = self.game.playing = False
        self.game.reset_keys()

    def render(self):
        """
        Renders the Game Over screen elements.
        """
        self.game.draw_text(f"Your Score: {self.score}", 350, 200)
        self.game.draw_text(f"High Score: {self.game.high_score}", 350, 250)
        self.restart_button.draw()
        self.restart_menu_exit_btn.draw()
