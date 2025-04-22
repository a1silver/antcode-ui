# Standard Library Imports
import os

# Third-Party Imports
import pygame
from typing import Union, Optional

# Local Imports
from . import WHITE, BLACK, COLORS, BLANK_MAP
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

    NORTH_ANTS = ["A", "B", "C", "D"]
    SOUTH_ANTS = ["E", "F", "G", "H"]

    NORTH_TEAM_COLOR = (255, 200, 200)
    SOUTH_TEAM_COLOR = (200, 200, 255)

    def __init__(
        self, x: int, y: int, width: int, height: int, map_data: list[str], simulation
    ):
        super().__init__(x, y, width, height)
        self.map_data = map_data
        pygame.font.init()
        self.font24 = pygame.font.SysFont(None, 24)
        self.font32 = pygame.font.SysFont(None, 32)
        self.simulation = simulation

    def is_ant_alive(self, ant: str) -> bool:
        """
        Checks if a given ant is present on the map.

        Args:
            ant (str): The identifier of the ant (e.g., 'A', 'B', 'C', etc.).

        Returns:
            bool: True if the given ant is present on the map.
        """
        return any(ant.lower() in item.lower() for item in self.map_data)

    def is_ant_holding_food(self, ant: str) -> bool:
        """
        Checks if a given ant is alive and holding food.

        Args:
            ant (str): The identifier of the ant (e.g., 'A', 'B', 'C', etc.).

        Returns:
            bool: True if the given ant is alive and holding food.
        """

        return self.is_ant_alive(ant) and any(
            ant.lower() in item for item in self.map_data
        )

    def draw_string(
        self,
        text: str,
        x: int,
        y: int,
        center: bool,
        font: pygame.font.Font,
        screen: Union[pygame.Surface, pygame.SurfaceType],
        color: tuple[int, int, int, Optional[int]] = WHITE,
    ):
        """
        Draws a string on the screen at the given position.

        Args:
            text (str): The text to draw.
            x (int): X-coordinate of the text position.
            y (int): Y-coordinate of the text position.
            center (bool): If True, centers the text at (x, y).
            font (pygame.font.Font): The font to use.
            screen (pygame.Surface): The pygame surface to draw on.
        """
        text_surface = font.render(text, True, color)
        text_rect = None
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
        else:
            text_rect = (x, y)
        screen.blit(text_surface, text_rect)

    def render_top_bar_north_team(
        self, screen: Union[pygame.Surface, pygame.SurfaceType]
    ):
        """
        Draws the top bar for the north team, showing their score and ants.

        Args:
            screen (pygame.Surface): The pygame surface to draw on.
        """
        northAnthillRect = pygame.Rect(
            self.x, self.y, self.width // 2, self.simulation.settings["cellSize"]
        )
        pygame.draw.rect(screen, MapComponent.NORTH_TEAM_COLOR, northAnthillRect)
        image_path = os.path.join(
            "./antcode_ui/images",
            "north.png",
        )
        if os.path.exists(image_path):
            image = pygame.image.load(image_path)
            image = pygame.transform.scale(
                image,
                (
                    self.simulation.settings["cellSize"],
                    self.simulation.settings["cellSize"],
                ),
            )
            screen.blit(image, (self.x, self.y))
        northScore = f"Score: {self.simulation.maps[self.simulation.current_map_index].north_points}"
        northScoreWidth, northScoreHeight = self.font24.size(northScore)
        self.draw_string(
            northScore,
            self.x + self.simulation.settings["cellSize"] + 7,
            self.y + self.simulation.settings["cellSize"] // 2 - northScoreHeight // 2,
            False,
            self.font24,
            screen,
        )
        for ant, idx in zip(MapComponent.NORTH_ANTS, range(0, 4)):
            image_path = os.path.join(
                "./antcode_ui/images",
                f"ant-{ant.lower()}{'-food' if self.is_ant_holding_food(ant) and self.is_ant_alive(ant) else ''}.png",
            )
            if os.path.exists(image_path):
                image = pygame.image.load(image_path)
                image = pygame.transform.scale(
                    image,
                    (
                        self.simulation.settings["cellSize"],
                        self.simulation.settings["cellSize"],
                    ),
                )
                screen.blit(
                    image,
                    (
                        self.x
                        + (idx + 1) * self.simulation.settings["cellSize"]
                        + 15
                        + northScoreWidth,
                        self.y - 2,
                    ),
                )
                if not self.is_ant_alive(ant):
                    dead_ant = os.path.join("./antcode_ui/images", "dead.png")
                    if os.path.exists(dead_ant):
                        overlay_image = pygame.image.load(dead_ant)
                        overlay_image = pygame.transform.scale(
                            overlay_image,
                            (
                                self.simulation.settings["cellSize"],
                                self.simulation.settings["cellSize"],
                            ),
                        )
                        screen.blit(
                            overlay_image,
                            (
                                self.x
                                + (idx + 1) * self.simulation.settings["cellSize"]
                                + 15
                                + northScoreWidth,
                                self.y - 2,
                            ),
                        )
                self.draw_string(
                    ant,
                    self.x
                    + (idx + 2) * self.simulation.settings["cellSize"]
                    + 5
                    + northScoreWidth,
                    self.y + self.simulation.settings["cellSize"] - 12,
                    True,
                    self.font24,
                    screen,
                    WHITE if self.is_ant_alive(ant) else BLACK,
                )

    def render_top_bar_south_team(
        self, screen: Union[pygame.Surface, pygame.SurfaceType]
    ):
        """
        Draws the top bar for the south team, showing their score and ants.

        Args:
            screen (pygame.Surface): The pygame surface to draw on.
        """
        # Define top bar region for south team
        southAnthillRect = pygame.Rect(
            self.x + self.width // 2,
            self.y,
            self.width // 2,
            self.simulation.settings["cellSize"],
        )
        pygame.draw.rect(screen, MapComponent.SOUTH_TEAM_COLOR, southAnthillRect)

        # Load in south team icon
        image_path = os.path.join(
            "./antcode_ui/images",
            "south.png",
        )
        if os.path.exists(image_path):
            image = pygame.image.load(image_path)
            image = pygame.transform.scale(
                image,
                (
                    self.simulation.settings["cellSize"],
                    self.simulation.settings["cellSize"],
                ),
            )
            screen.blit(
                image,
                (self.x + self.width - self.simulation.settings["cellSize"], self.y),
            )

        # Render score text
        southScore = f"Score: {self.simulation.maps[self.simulation.current_map_index].south_points}"
        southScoreWidth, southScoreHeight = self.font24.size(southScore)
        self.draw_string(
            southScore,
            self.x
            + self.width
            - (self.simulation.settings["cellSize"] + 7)
            - southScoreWidth,
            self.y + self.simulation.settings["cellSize"] // 2 - southScoreHeight // 2,
            False,
            self.font24,
            screen,
        )
        for ant, idx in zip(reversed(MapComponent.SOUTH_ANTS), range(0, 4)):
            image_path = os.path.join(
                "./antcode_ui/images",
                f"ant-{ant.lower()}{'-food' if self.is_ant_holding_food(ant) and self.is_ant_alive(ant) else ''}.png",
            )
            if os.path.exists(image_path):
                image = pygame.image.load(image_path)
                image = pygame.transform.scale(
                    image,
                    (
                        self.simulation.settings["cellSize"],
                        self.simulation.settings["cellSize"],
                    ),
                )
                screen.blit(
                    image,
                    (
                        self.x
                        + self.width
                        - ((idx + 2) * self.simulation.settings["cellSize"] + 7)
                        - southScoreWidth,
                        self.y - 2,
                    ),
                )
                if not self.is_ant_alive(ant):
                    dead_ant = os.path.join(
                        "./antcode_ui/images",
                        "dead.png",
                    )
                    if os.path.exists(dead_ant):
                        overlay_image = pygame.image.load(dead_ant)
                        overlay_image = pygame.transform.scale(
                            overlay_image,
                            (
                                self.simulation.settings["cellSize"],
                                self.simulation.settings["cellSize"],
                            ),
                        )
                        screen.blit(
                            overlay_image,
                            (
                                self.x
                                + self.width
                                - ((idx + 2) * self.simulation.settings["cellSize"] + 7)
                                - southScoreWidth,
                                self.y - 2,
                            ),
                        )
                self.draw_string(
                    ant,
                    self.x
                    + self.width
                    - ((idx + 1) * self.simulation.settings["cellSize"] + 17)
                    - southScoreWidth,
                    self.y + self.simulation.settings["cellSize"] - 12,
                    True,
                    self.font24,
                    screen,
                    WHITE if self.is_ant_alive(ant) else BLACK,
                )

    def draw(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        """
        Draws the map on the given screen surface with interactive hover effects and tooltips.

        Args:
            screen (Union[pygame.Surface, pygame.SurfaceType]): The pygame surface to which the map will be drawn.
        """
        cell_offset = (
            1
            if self.map_data is not BLANK_MAP and self.simulation.settings["showTopBar"]
            else 0
        )

        # Render top bar
        if self.map_data is not BLANK_MAP and self.simulation.settings["showTopBar"]:
            try:
                self.render_top_bar_north_team(screen)
                self.render_top_bar_south_team(screen)

                stepCounter = f"Step {self.simulation.current_map_index + 1} / {len(self.simulation.maps)}"
                self.draw_string(
                    stepCounter,
                    self.x + self.width // 2,
                    self.y + self.simulation.settings["cellSize"] // 2,
                    True,
                    self.font32,
                    screen,
                )

            except TypeError:
                pass

        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered_cell = None

        # Render cells
        for row_idx, row in enumerate(self.map_data):
            for col_idx, char in enumerate(row):
                cell_rect = pygame.Rect(
                    self.x + col_idx * self.simulation.settings["cellSize"],
                    self.y
                    + (row_idx + cell_offset) * self.simulation.settings["cellSize"],
                    self.simulation.settings["cellSize"],
                    self.simulation.settings["cellSize"],
                )

                # Check if the cell is hovered
                if cell_rect.collidepoint(mouse_x, mouse_y):
                    hovered_cell = (cell_rect, char, row_idx, col_idx)

                # Fancy Graphics
                if self.simulation.settings["fancyGraphics"]:
                    # Grass
                    if row_idx % 4 == 0 and col_idx % 4 == 0:
                        grass_rect = pygame.Rect(
                            self.x + col_idx * self.simulation.settings["cellSize"],
                            self.y
                            + (row_idx + cell_offset)
                            * self.simulation.settings["cellSize"],
                            self.simulation.settings["cellSize"] * 4,
                            self.simulation.settings["cellSize"] * 4,
                        )
                        image_path = os.path.join("./antcode_ui/images", "empty.png")
                        if os.path.exists(image_path):
                            image = pygame.image.load(image_path)
                            image = pygame.transform.scale(
                                image,
                                (
                                    self.simulation.settings["cellSize"] * 4,
                                    self.simulation.settings["cellSize"] * 4,
                                ),
                            )
                            screen.blit(image, grass_rect.topleft)

                    # Walls
                    if char == "#":
                        image_path = os.path.join(
                            "./antcode_ui/images",
                            "wall.png",
                        )
                        if os.path.exists(image_path):
                            image = pygame.image.load(image_path)
                            image = pygame.transform.scale(
                                image,
                                (
                                    self.simulation.settings["cellSize"],
                                    self.simulation.settings["cellSize"],
                                ),
                            )
                            screen.blit(image, cell_rect.topleft)
                else:
                    pygame.draw.rect(screen, COLORS.get(char, WHITE), cell_rect)

                if char.isdigit():
                    if (
                        self.simulation.settings["foodpileInfo"] == 1
                        or self.simulation.settings["foodpileInfo"] == 3
                    ):
                        overlay = pygame.Surface(
                            (cell_rect.width, cell_rect.height), pygame.SRCALPHA
                        )
                        overlay.fill((248, 232, 187, 191))
                        screen.blit(overlay, cell_rect.topleft)

                    image_path = os.path.join("./antcode_ui/images", "food.png")
                    if os.path.exists(image_path):
                        image = pygame.image.load(image_path).convert_alpha()
                        image = pygame.transform.scale(
                            image,
                            (
                                self.simulation.settings["cellSize"],
                                self.simulation.settings["cellSize"],
                            ),
                        )
                        screen.blit(image, cell_rect.topleft)

                    if (
                        self.simulation.settings["foodpileInfo"] == 2
                        or self.simulation.settings["foodpileInfo"] == 3
                    ):
                        self.draw_string(
                            char,
                            cell_rect.left + 5,
                            cell_rect.top + 5,
                            False,
                            self.font24,
                            screen,
                            BLACK,
                        )
                elif char == "@" or char == "X":
                    # Draw slightly transparent square to denote team color
                    if self.simulation.settings["anthillInfo"] == 1:
                        if char == "@":
                            overlay = pygame.Surface(
                                (cell_rect.width, cell_rect.height), pygame.SRCALPHA
                            )
                            overlay.fill(MapComponent.NORTH_TEAM_COLOR + (191,))
                            screen.blit(overlay, cell_rect.topleft)
                        elif char == "X":
                            overlay = pygame.Surface(
                                (cell_rect.width, cell_rect.height), pygame.SRCALPHA
                            )
                            overlay.fill(MapComponent.SOUTH_TEAM_COLOR + (191,))
                            screen.blit(overlay, cell_rect.topleft)
                    image_path = os.path.join(
                        "./antcode_ui/images",
                        f"{'north' if char == '@' else 'south'}.png",
                    )
                    if os.path.exists(image_path):
                        image = pygame.image.load(image_path)
                        image = pygame.transform.scale(
                            image,
                            (
                                self.simulation.settings["cellSize"],
                                self.simulation.settings["cellSize"],
                            ),
                        )
                        screen.blit(image, cell_rect.topleft)
                else:
                    if char.isalpha() and char.upper() in "ABCDEFGH":
                        # Draw slightly transparent square to denote team color
                        if (
                            self.simulation.settings["antInfo"] == 1
                            or self.simulation.settings["antInfo"] == 3
                        ):
                            if char.upper() in MapComponent.NORTH_ANTS:
                                overlay = pygame.Surface(
                                    (cell_rect.width, cell_rect.height), pygame.SRCALPHA
                                )
                                overlay.fill(MapComponent.NORTH_TEAM_COLOR + (191,))
                                screen.blit(overlay, cell_rect.topleft)
                            elif char.upper() in MapComponent.SOUTH_ANTS:
                                overlay = pygame.Surface(
                                    (cell_rect.width, cell_rect.height), pygame.SRCALPHA
                                )
                                overlay.fill(MapComponent.SOUTH_TEAM_COLOR + (191,))
                                screen.blit(overlay, cell_rect.topleft)

                        image_path = os.path.join(
                            "./antcode_ui/images",
                            f"ant-{char.lower()}{'-food' if char.islower() else ''}.png",
                        )
                        if os.path.exists(image_path):
                            image = pygame.image.load(image_path)
                            image = pygame.transform.scale(
                                image,
                                (
                                    self.simulation.settings["cellSize"],
                                    self.simulation.settings["cellSize"],
                                ),
                            )
                            screen.blit(image, cell_rect.topleft)

                        if (
                            self.simulation.settings["antInfo"] == 2
                            or self.simulation.settings["antInfo"] == 3
                        ):
                            self.draw_string(
                                char.upper(),
                                cell_rect.left + 5,
                                cell_rect.top + 5,
                                False,
                                self.font24,
                                screen,
                                BLACK,
                            )

                if char != "#":
                    pygame.draw.rect(screen, (100, 100, 100), cell_rect, 1)

        # Render hovered cell overlay and tooltip
        keys = pygame.key.get_pressed()
        if hovered_cell and pygame.mouse.get_focused():
            cell_rect, char, cell_x, cell_y = hovered_cell

            if self.simulation.settings["hoverOverlay"]:
                # Draw semi-transparent overlay
                overlay = pygame.Surface(
                    (cell_rect.width, cell_rect.height), pygame.SRCALPHA
                )
                overlay.fill((255, 255, 255, 128))  # White with 50% opacity
                screen.blit(overlay, cell_rect.topleft)

            if (
                self.simulation.settings["tooltips"] == 1
                and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
            ) or self.simulation.settings["tooltips"] == 2:
                # Tooltip position adjustment
                tooltip_text = [f"Cell ({cell_x}, {cell_y})"]
                if char == "#":
                    tooltip_text.append("Wall")
                elif char.isdigit():
                    tooltip_text.append(f"Food pile ({char})")
                elif char == "@":
                    tooltip_text.append("North Ant Hill")
                    tooltip_text.append(
                        f"Score: {self.simulation.maps[self.simulation.current_map_index].north_points}"
                    )
                elif char == "X":
                    tooltip_text.append("South Ant Hill")
                    tooltip_text.append(
                        f"Score: {self.simulation.maps[self.simulation.current_map_index].south_points}"
                    )
                elif char.isalpha() and char.upper() in "ABCDEFGH":
                    team = "North Team" if char.upper() in "ABCD" else "South Team"
                    tooltip_text.append(f"Ant {char.upper()}, {team}")
                    if char in "abcdefgh":
                        tooltip_text.append("Holding food")

                tooltip_font = pygame.font.Font(None, 24)

                # Render each line of the tooltip
                rendered_lines = [
                    tooltip_font.render(line, True, (255, 255, 255))
                    for line in tooltip_text
                ]
                line_heights = [line.get_height() for line in rendered_lines]
                tooltip_width = max(line.get_width() for line in rendered_lines)
                tooltip_height = (
                    sum(line_heights) + (len(line_heights) - 1) * 4
                )  # Add spacing between lines

                tooltip_x = mouse_x + 25
                tooltip_y = mouse_y + 25

                if tooltip_x + tooltip_width > screen.get_width():
                    tooltip_x = mouse_x - tooltip_width - 10
                if tooltip_y + tooltip_height > screen.get_height():
                    tooltip_y = mouse_y - tooltip_height - 10

                # Draw tooltip background
                tooltip_bg = pygame.Surface((tooltip_width + 4, tooltip_height + 4))
                tooltip_bg.fill((0, 0, 0))  # Black background
                screen.blit(tooltip_bg, (tooltip_x - 2, tooltip_y - 2))

                # Draw each line of the tooltip
                current_y = tooltip_y
                for line_surface in rendered_lines:
                    screen.blit(line_surface, (tooltip_x, current_y))
                    current_y += line_surface.get_height() + 4
