from states.state import State
from ui_elements import Button


class PauseMenu(State):
    def __init__(self, game):
        """
        Initializes the Pause screen state with UI elements.
        :param game: Reference to the main game object.
        """
        State.__init__(self, game)
        self.resume_btn = Button(
            self.game.HALF_SCREEN_WIDTH,
            self.game.HALF_SCREEN_HEIGHT - 150,
            self.game.resume_button_image,
            0.8,
            self.game,
        )
        self.pause_menu_exit_btn = Button(
            self.game.HALF_SCREEN_WIDTH,
            self.game.HALF_SCREEN_HEIGHT + 50,
            self.game.exit_button_image,
            0.8,
            self.game,
        )

    def update(self, delta_time, actions):
        """
        Updates the Pause screen by checking button presses and handling state transitions.
        :param delta_time: Time elapsed since the last frame.
        :param actions: Dictionary of user actions (like key presses, mouse clicks).
        """
        if self.resume_btn.check_if_button_is_pressed():
            self.game.logger.info("Resuming the game...")
            self.exit_state()
        elif self.pause_menu_exit_btn.check_if_button_is_pressed():
            self.game.save_high_score()
            self.game.running, self.game.playing = False, False
        self.game.reset_keys()

    def render(self):
        """
        Renders the Pause screen elements.
        """
        self.prev_state.render()
        self.resume_btn.draw()
        self.pause_menu_exit_btn.draw()
