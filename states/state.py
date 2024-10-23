class State:
    def __init__(self, game):
        """
        Initializes the State with a reference to the game instance.
        :param game: Reference to the main game object.
        """
        self.game = game
        self.prev_state = None

    def update(self, delta_time, actions):
        """
        Updates the current state based on the elapsed time and user actions.
        :param delta_time: Time elapsed since the last frame.
        :param actions: Dictionary of user actions (like key presses, mouse clicks).
        """
        pass

    def render(self):
        """
        Renders the current state to the screen.
        """
        pass

    def enter_state(self):
        """
        Adds(Enters) the current game state, manages the state stack, keeps track of previous game state.
        """
        if len(self.game.state_stack) > 1:
            self.prev_state = self.game.state_stack[-1]
        self.game.state_stack.append(self)

    def exit_state(self):
        """
        Removes(Exits) the current game state from the state stack.
        """
        self.game.state_stack.pop()
