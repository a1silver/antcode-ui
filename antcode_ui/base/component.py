# Third-Party Imports
import pygame
from typing import Union


class Component:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.active = True

    def update(self):
        """Method to update the component state every frame."""
        pass

    def draw(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        """Method to draw the component on the screen."""
        pass

    def handle_event(self, event: pygame.event.Event):
        """Method to handle events like mouse or keyboard input."""
        pass

    def handle_mouse_event(self, event: pygame.event.Event):
        """Handle mouse events like clicking, moving, etc."""
        pass

    def handle_keyboard_event(self, event: pygame.event.Event):
        """Handle keyboard events like key presses."""
        pass
