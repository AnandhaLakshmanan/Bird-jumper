from pygame import mouse, transform


class Element:
    def __init__(self, x_coord, y_coord, img_surface, scale_factor, game):
        """
        Initializes an Element object with position, image, and scaling.

        :param x_coord: X-coordinate for the top-left corner of the element.
        :param y_coord: Y-coordinate for the top-left corner of the element.
        :param img_surface: The image surface to display for the element.
        :param scale_factor: Scaling factor for resizing the image.
        """
        self.game = game
        width = img_surface.get_width()
        height = img_surface.get_height()
        self.image = transform.scale(
            surface=img_surface,
            size=(int(width * scale_factor), int(height * scale_factor)),
        )
        self.rect = self.image.get_rect()
        self.rect.center = (x_coord, y_coord)

    def draw(self):
        """
        Draws the element onto the screen surface.
        """
        self.game.screen.blit(source=self.image, dest=(self.rect.x, self.rect.y))


class Button(Element):
    def __init__(self, x_coord, y_coord, img_surface, scale_factor, game):
        """
        Initializes a Button object, inheriting from Element class, with additional click handling.
        :param x_coord: X-coordinate for the button's top-left corner.
        :param y_coord: Y-coordinate for the button's top-left corner.
        :param img_surface: The image surface for the button.
        :param scale_factor: Scaling factor for resizing the button image.
        """
        super().__init__(x_coord, y_coord, img_surface, scale_factor, game)
        self.clicked = False

    def check_if_button_is_pressed(self):
        """
        Checks if the button is pressed, updates its state, and returns the action.
        :return: True if the button is pressed, False otherwise.
        """
        action = False
        pos = mouse.get_pos()
        # Check if user presses the on the button using left click
        if self.rect.collidepoint(pos):
            if mouse.get_pressed(num_buttons=3)[0] and not self.clicked:
                self.clicked = True
                action = True
            if not mouse.get_pressed(num_buttons=3)[0]:
                self.clicked = False
        return action
