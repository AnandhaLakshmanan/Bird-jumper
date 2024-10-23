from states.game_world import GameWorld
from states.state import State
from ui_elements import Button, Element


class Title(State):
    def __init__(self, game):
        """
        Initializes the title screen state with UI elements.
        :param game: Reference to the main game object.
        """
        State.__init__(self, game)
        self.title = Element(
            self.game.HALF_SCREEN_WIDTH, 150, self.game.title_image, 2, self.game
        )
        self.start_btn = Button(
            self.game.HALF_SCREEN_WIDTH,
            self.game.HALF_SCREEN_HEIGHT - 130,
            self.game.start_button_image,
            0.8,
            self.game,
        )
        self.exit_btn = Button(
            self.game.HALF_SCREEN_WIDTH,
            self.game.HALF_SCREEN_HEIGHT + 50,
            self.game.exit_button_image,
            0.8,
            self.game,
        )

    def update(self, delta_time, actions):
        """
        Updates the title screen by checking button presses and handling state transitions.
        :param delta_time: Time elapsed since the last frame.
        :param actions: Dictionary of user actions (like key presses, mouse clicks).
        """
        if self.start_btn.check_if_button_is_pressed():
            self.game.logger.info("Starting the game...")
            new_state = GameWorld(self.game)
            new_state.enter_state()
        elif self.exit_btn.check_if_button_is_pressed():
            self.game.running = self.game.playing = False
        self.game.reset_keys()

    def render(self):
        """
        Renders the title screen elements.
        """
        self.title.draw()
        self.start_btn.draw()
        self.exit_btn.draw()
