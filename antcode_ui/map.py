# Standard Library Imports
import os

# Third-Party Imports
import pygame
from typing import Union

# Local Imports
from . import WHITE, COLORS, BLANK_MAP
from .base import Component

   
class MapComponent(Component):
    """
    A component that displays a map on the screen with visual representations for different map elements.

    This class inherits from `Component` and provides functionality for drawing a grid-based map using
    a 2D array of strings (`map_data`). Each character in the `map_data` array represents an element on
    the map, which could be a number, letter, or an alpha character that corresponds to a specific image.
    The class handles rendering map cells, drawing colors, and overlaying text or images depending on the
    type of character in each cell.

    Attributes:
        x (int): The x-coordinate of the top-left corner of the map component.
        y (int): The y-coordinate of the top-left corner of the map component.
        width (int): The width of the map component.
        height (int): The height of the map component.
        map_data (list[str]): A 2D list (array) of strings representing the map. Each string element can contain
                              characters that represent different types of map elements.
        font (pygame.font.Font): A pygame font object used for rendering text on the map.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        map_data: list[str],
        simulation
    ):
        super().__init__(x, y, width, height)
        self.map_data = map_data
        pygame.font.init()
        self.font24 = pygame.font.SysFont(None, 24)
        self.font32 = pygame.font.SysFont(None, 32)
        self.simulation = simulation
        
    def draw_string(self, text: str, x: int, y: int, center: bool, font: pygame.font.Font, screen: Union[pygame.Surface, pygame.SurfaceType]):
        text_surface = font.render(text, True, WHITE)
        text_rect = None
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
        else:
            text_rect = (x, y)
        screen.blit(text_surface, text_rect)
        
    def render_top_bar_north_team(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        northAnthillRect = pygame.Rect(
            self.x, self.y, self.width // 2, self.simulation.settings["cellSize"]
        )
        pygame.draw.rect(screen, (255, 200, 200), northAnthillRect)
        image_path = os.path.join(
            "./antcode_ui/images",
            "north.png",
        )
        if os.path.exists(image_path):
            image = pygame.image.load(image_path)
            image = pygame.transform.scale(
                image,
                (self.simulation.settings["cellSize"], self.simulation.settings["cellSize"]),
            )
            screen.blit(image, (self.x, self.y))
        northScore = f"Score: {self.simulation.maps[self.simulation.current_map_index].north_points}"
        northScoreWidth, northScoreHeight = self.font24.size(northScore)
        self.draw_string(northScore, self.x + self.simulation.settings["cellSize"] + 7, self.y + self.simulation.settings["cellSize"] // 2 - northScoreHeight // 2, False, self.font24, screen)
        for ant, idx in zip(['A', 'B', 'C', 'D'], range(0, 4)):
            if any(ant.lower() in item.lower() for item in self.map_data):
                image_path = os.path.join(
                    "./antcode_ui/images",
                    f"ant-{ant.lower()}.png",
                )
                if os.path.exists(image_path):
                    image = pygame.image.load(image_path)
                    image = pygame.transform.scale(
                        image,
                        (self.simulation.settings["cellSize"], self.simulation.settings["cellSize"]),
                    )
                    screen.blit(image, (self.x + (idx + 1) * self.simulation.settings["cellSize"] + 15 + northScoreWidth, self.y - 2))
                    
    def render_top_bar_south_team(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        # Define top bar region for south team
        southAnthillRect = pygame.Rect(
            self.x + self.width // 2, self.y, self.width // 2, self.simulation.settings["cellSize"]
        )
        pygame.draw.rect(screen, (200, 200, 255), southAnthillRect)
        
        # Load in south team icon
        image_path = os.path.join(
            "./antcode_ui/images",
            "south.png",
        )
        if os.path.exists(image_path):
            image = pygame.image.load(image_path)
            image = pygame.transform.scale(
                image,
                (self.simulation.settings["cellSize"], self.simulation.settings["cellSize"]),
            )
            screen.blit(image, (self.x + self.width - self.simulation.settings["cellSize"], self.y))
            
        # Render score text
        southScore = f"Score: {self.simulation.maps[self.simulation.current_map_index].south_points}"
        southScoreWidth, southScoreHeight = self.font24.size(southScore)
        self.draw_string(southScore, self.x + self.width - (self.simulation.settings["cellSize"] + 7) - southScoreWidth, self.y + self.simulation.settings["cellSize"] // 2 - southScoreHeight // 2, False, self.font24, screen)
        for ant, idx in zip(['E', 'F', 'G', 'H'], range(0, 4)):
            if any(ant.lower() in item.lower() for item in self.map_data):
                image_path = os.path.join(
                    "./antcode_ui/images",
                    f"ant-{ant.lower()}.png",
                )
                if os.path.exists(image_path):
                    image = pygame.image.load(image_path)
                    image = pygame.transform.scale(
                        image,
                        (self.simulation.settings["cellSize"], self.simulation.settings["cellSize"]),
                    )
                    screen.blit(image, (self.x + self.width - ((idx + 2) * self.simulation.settings["cellSize"] + 7) - southScoreWidth, self.y - 2))

    def draw(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        """
        Draws the map on the given screen surface.

        This method iterates through each cell of the map (represented by characters in `map_data`)
        and draws the appropriate visual representation. Depending on the character in the cell, it can
        render a color, a digit, or an image. A border is drawn around each cell, and text is rendered
        for numeric characters.

        Args:
            screen (Union[pygame.Surface, pygame.SurfaceType]): The pygame surface to which the map will be drawn.
        """
        cell_offset = 1 if self.map_data is not BLANK_MAP and self.simulation.settings["showTopBar"] else 0
        
        # Render text stuff
        if self.map_data is not BLANK_MAP and self.simulation.settings["showTopBar"]:
            try:
                self.render_top_bar_north_team(screen)
                self.render_top_bar_south_team(screen)
                            
                stepCounter = f"Step {self.simulation.current_map_index + 1} / {len(self.simulation.maps)}"
                self.draw_string(stepCounter, self.x + self.width // 2, self.y + self.simulation.settings["cellSize"] // 2, True, self.font32, screen)
                
            except TypeError:
                pass
        
        # Render cells
        for row_idx, row in enumerate(self.map_data):
            for col_idx, char in enumerate(row):
                cell_rect = pygame.Rect(
                    self.x + col_idx * self.simulation.settings["cellSize"],
                    self.y + (row_idx + cell_offset) * self.simulation.settings["cellSize"],
                    self.simulation.settings["cellSize"],
                    self.simulation.settings["cellSize"],
                )
                
                # Fancy Graphics
                if self.simulation.settings["fancyGraphics"]:
                    # Grass
                    if row_idx % 4 == 0 and col_idx % 4 == 0:
                        grass_rect = pygame.Rect(
                            self.x + col_idx * self.simulation.settings["cellSize"],
                            self.y + (row_idx + cell_offset) * self.simulation.settings["cellSize"],
                            self.simulation.settings["cellSize"] * 4,
                            self.simulation.settings["cellSize"] * 4,
                        )
                        image_path = os.path.join(
                            "./antcode_ui/images",
                            "empty.png"
                        )
                        if os.path.exists(image_path):
                            image = pygame.image.load(image_path)
                            image = pygame.transform.scale(
                                image,
                                (self.simulation.settings["cellSize"] * 4, self.simulation.settings["cellSize"] * 4),
                            )
                            screen.blit(image, grass_rect.topleft)
                            
                    # Walls
                    if char == '#':
                        image_path = os.path.join(
                            "./antcode_ui/images",
                            "wall.png",
                        )
                        if os.path.exists(image_path):
                            image = pygame.image.load(image_path)
                            image = pygame.transform.scale(
                                image,
                                (self.simulation.settings["cellSize"], self.simulation.settings["cellSize"]),
                            )
                            screen.blit(image, cell_rect.topleft)
                else:
                    pygame.draw.rect(screen, COLORS.get(char, WHITE), cell_rect)

                if char.isdigit():
                    image_path = os.path.join(
                        "./antcode_ui/images",
                        "food.png",
                    )
                    if os.path.exists(image_path):
                        image = pygame.image.load(image_path).convert_alpha()
                        image = pygame.transform.scale(
                            image,
                            (self.simulation.settings["cellSize"], self.simulation.settings["cellSize"]),
                        )
                        screen.blit(image, cell_rect.topleft)
                    
                elif char == "@" or char == "X":
                    image_path = os.path.join(
                        "./antcode_ui/images",
                        f"{'north' if char == '@' else 'south' if char == 'X' else 'error'}.png",
                    )
                    if os.path.exists(image_path):
                        image = pygame.image.load(image_path)
                        image = pygame.transform.scale(
                            image,
                            (self.simulation.settings["cellSize"], self.simulation.settings["cellSize"]),
                        )
                        screen.blit(image, cell_rect.topleft)
                else:
                    if char.isalpha() and char.upper() in "ABCDEFGH":
                        image_path = os.path.join(
                            "./antcode_ui/images",
                            f"ant-{char.lower()}{'-food' if char.islower() else ''}.png",
                        )
                        if os.path.exists(image_path):
                            image = pygame.image.load(image_path)
                            image = pygame.transform.scale(
                                image,
                                (self.simulation.settings["cellSize"], self.simulation.settings["cellSize"]),
                            )
                            screen.blit(image, cell_rect.topleft)

                if char != '#':
                    pygame.draw.rect(screen, (100, 100, 100), cell_rect, 1)