# Standard Library Imports
import os
import re
import sys
import threading
from queue import Queue
from typing import Optional, Tuple

# Third-Party Imports
import pygame
from PyQt5.QtWidgets import QApplication, QFileDialog
from colorama import Fore, Back, Style

# Local Imports
from . import BLACK, VALID_MAP_CHARS, BLANK_MAP
from .base import (
    Command,
    CommandManager,
    HelpCommand,
    ConfigCommand,
    Component,
    Message,
    Round,
)
from .map import MapComponent
from .settings import AntSettings


class AntSimulation:
    """
    A class to simulate the movement and interactions of ants on a map, managing
    the simulation loop, handling user input, and rendering components.

    The simulation runs in a graphical window where users can control the playback
    of a series of rounds through commands like pausing, stepping forward/backward,
    or skipping to the first or last step. It handles events such as mouse clicks
    and keyboard inputs, dispatching them to all active components. Maps for the
    simulation can be loaded from a file, and the simulation will display the state
    of the map for each round.

    Attributes:
        settings (AntSettings): Configuration settings for the simulation, including
            playback speed and pause options.
        running (threading.Event): An event to control the simulation loop.
        commands (CommandManager): An object to keep track of all available simulation commands.
        command_queue (Queue): A queue for processing user commands asynchronously.
        components (list[Component]): A list of visual components that are part of the simulation.
        current_map_index (int): Index of the current map being displayed.
        screen_width (int): Width of the simulation screen.
        screen_height (int): Height of the simulation screen.
        screen (pygame.Surface): The Pygame surface used for rendering the simulation.
        clock (pygame.time.Clock): Clock for controlling the frame rate of the simulation.
        board_size (Optional[Tuple[int, int]]): Size of the map (rows, columns).
        winner (Optional[str]): Winner of the game
        maps (Optional[list[Round]]): List of loaded rounds with map data for each round.
        map_component (MapComponent): The component responsible for displaying the map.
        map_switch_interval (int): Interval in milliseconds between automatic map switches.
        last_map_switch_time (int): The last time the map was switched.

    Methods:
        reset_screen() -> None:
            Adjusts the screen size based on the current map dimensions.
        add_component(component: Component) -> None:
            Adds a visual component to the simulation.
        load_maps() -> None:
            Loads map data from a file and sets up the simulation with the loaded maps.
        skip_start() -> None:
            Resets the simulation to the first step.
        step_backward() -> None:
            Moves the simulation one step backward.
        play_pause() -> None:
            Toggles the simulation between playing and paused states.
        step_forward() -> None:
            Moves the simulation one step forward.
        skip_end() -> None:
            Jumps to the last step in the simulation.
        handle_event(event: pygame.event.Event) -> None:
            Dispatches a general event to all components.
        handle_mouse_event(event: pygame.event.Event) -> None:
            Dispatches a mouse-related event to all components.
        handle_keyboard_event(event: pygame.event.Event) -> None:
            Dispatches a keyboard-related event to all components.
        exit() -> None:
            Saves settings and exits the simulation.
        run() -> None:
            Runs the main simulation loop, handling events, commands, and rendering.
        get_console_input() -> None:
            Runs a loop to accept console commands and enqueue them for processing.
    """

    def reset_screen(self) -> None:
        """
        Adjust the screen size based on the current map dimensions.
        Updates the map component size and resizes the Pygame window accordingly.
        """
        screen_width = len(self.map_component.map_data[0]) * self.settings["cellSize"]
        screen_height = (
            len(self.map_component.map_data)
            + (
                1
                if self.map_component.map_data is not BLANK_MAP
                and self.settings["showTopBar"]
                else 0
            )
        ) * self.settings["cellSize"]
        self.map_component.width = screen_width
        self.map_component.height = screen_height
        
        if self.has_five_ants:
            MapComponent.NORTH_ANTS = ["A", "B", "C", "D", "E"]
            MapComponent.SOUTH_ANTS = ["F", "G", "H", "I", "J"]
        else:
            MapComponent.NORTH_ANTS = ["A", "B", "C", "D"]
            MapComponent.SOUTH_ANTS = ["E", "F", "G", "H"]
        self.screen = pygame.display.set_mode((screen_width, screen_height))

    def add_component(self, component: Component) -> None:
        """
        Add a visual component to the simulation.

        Args:
            component (Component): The component to add.
        """
        self.components.append(component)

    def load_maps(self) -> None:
        """
        Load and parse map data from a file.

        Opens a file dialog for the user to select a map file, extracts
        board size, rounds, and winner details, and updates the simulation state.
        If loading fails, it falls back to a blank map.
        """
        # Open file dialog to select a map file
        app = QApplication([])
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        filename, _ = QFileDialog.getOpenFileName(
            None, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options
        )

        self.has_five_ants = False

        # If no file is selected or the file doesn't exist, reset to blank map
        if not filename or not os.path.exists(filename):
            self.board_size = (None, None)
            self.winner = None
            self.maps = None
            self.current_map_index = 0
            self.map_component.map_data = BLANK_MAP
            self.reset_screen()
            return

        rounds = []
        board_size = None
        winner = None

        try:
            # Read file content
            with open(filename, "r") as file:
                content = file.read()

            # Split file content into sections using "============================"
            sections = content.split("=" * 30)

            # Extract board size from the first section
            first_section = sections[0].strip()
            size_match = re.search(r"SIZE (\d+) (\d+)", first_section)

            if size_match:
                rows, cols = map(int, size_match.groups())
                board_size = (rows, cols)
            else:
                raise ValueError("Board size not found.")

            # Extract winner from the last section
            last_section = sections[len(sections) - 1].strip()
            winner_match = re.search(r"WINNER (\w+)", last_section)

            if winner_match:
                winner = winner_match.group(1)
            else:
                raise ValueError("Winner not found.")

            # Process each round's data
            for section in sections[1:]:
                stripped = section.strip()
                lines = stripped.split("\n")

                # Skip empty sections and those that are missing lines
                if stripped == "" or not len(lines) == 4 + board_size[0]:
                    continue

                # Extract round number
                round_match = re.search(r"ROUND (\d+)", lines[0])
                if round_match:
                    round_number = int(round_match.group(1))
                else:
                    raise ValueError(f"Round number not found in section: {section}")

                # Extract team scores
                north_match = re.search(r"NORTH (\d+)", lines[1])
                south_match = re.search(r"SOUTH (\d+)", lines[2])

                if north_match and south_match:
                    north_points = int(north_match.group(1))
                    south_points = int(south_match.group(1))
                else:
                    raise ValueError(f"Team points not found in section: {section}")

                try:
                    # Locate board data within the section
                    board_start_idx = lines.index("=" * 25) + 1
                    board = lines[board_start_idx : board_start_idx + board_size[0]]

                    # Validate board dimensions and characters
                    for line in board:
                        if len(line) != board_size[1] or not set(line).issubset(
                            VALID_MAP_CHARS
                        ):
                            raise ValueError(
                                f"Invalid map format or invalid characters detected: {line}"
                            )
                        if {'I', 'J'} <= set(line): # Board has five ants]
                            self.has_five_ants = True

                except ValueError:
                    raise ValueError(
                        f"Valid board data not found in section: {section}"
                    )

                # Store the parsed round data
                round_obj = Round(round_number, north_points, south_points, board)
                rounds.append(round_obj)

            # Ensure exactly 200 rounds exist
            if not len(rounds) == 200:
                raise ValueError(
                    f"File contains incomplete game data ({len(rounds)} rounds, {200 - len(rounds)} missing)"
                )

            print(f"Successfully loaded map from {Fore.GREEN}{filename}{Fore.RESET}")
            # Update simulation state with loaded data
            self.board_size = board_size
            self.winner = winner
            self.maps = rounds
            self.current_map_index = 0
            self.map_component.map_data = self.maps[self.current_map_index].board
            self.reset_screen()
        except ValueError as e:
            # Handle errors by resetting to a blank map
            print(f"{Fore.LIGHTRED_EX}Error loading maps: {e}{Fore.RESET}")
            self.current_map_index = 0
            self.board_size = (None, None)
            self.winner = None
            self.maps = None
            self.map_component.map_data = BLANK_MAP
            self.reset_screen()

    def skip_start(self) -> None:
        """
        Reset the simulation to the first step.

        If the simulation is configured to pause on step changes, it will pause.
        """
        if self.maps is None or len(self.maps) == 0:
            return

        if self.settings["pauseOnStep"]:
            self.settings.simulationPaused = True

        self.current_map_index = 0
        self.map_component.map_data = self.maps[self.current_map_index].board

    def step_backward(self) -> None:
        """
        Move the simulation one step backward.

        Wraps around to the last step if already at the beginning.
        Pauses the simulation if configured to do so on step changes.
        """
        if self.maps is None or len(self.maps) == 0:
            return

        if self.settings["pauseOnStep"]:
            self.settings.simulationPaused = True

        self.current_map_index = (self.current_map_index - 1) % len(self.maps)
        self.map_component.map_data = self.maps[self.current_map_index].board

    def play_pause(self) -> None:
        """
        Toggle the simulation playback state between paused and playing.
        """
        if self.maps is None or len(self.maps) == 0:
            return

        if self.settings.simulationPaused:
            self.settings.simulationPaused = False
        else:
            self.settings.simulationPaused = True

    def step_forward(self) -> None:
        """
        Move the simulation one step forward.

        Wraps around to the first step if already at the end.
        Pauses the simulation if configured to do so on step changes.
        """
        if self.maps is None or len(self.maps) == 0:
            return

        if self.settings["pauseOnStep"]:
            self.settings.simulationPaused = True

        self.current_map_index = (self.current_map_index + 1) % len(self.maps)
        self.map_component.map_data = self.maps[self.current_map_index].board

    def skip_end(self) -> None:
        """
        Jump to the last step in the simulation.

        If the simulation is set to pause on step changes, it will pause.
        """
        if self.maps is None or len(self.maps) == 0:
            return

        if self.settings["pauseOnStep"]:
            self.settings.simulationPaused = True

        self.current_map_index = len(self.maps) - 1
        self.map_component.map_data = self.maps[self.current_map_index].board

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Dispatch a general event to all components.

        Args:
            event (pygame.event.Event): The event to handle.
        """
        for component in self.components:
            component.handle_event(event)

    def handle_mouse_event(self, event: pygame.event.Event) -> None:
        """
        Dispatch a mouse-related event to all components.

        Args:
            event (pygame.event.Event): The mouse event to handle.
        """
        if event.type in [
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION,
        ]:
            for component in self.components:
                component.handle_mouse_event(event)

    def handle_keyboard_event(self, event: pygame.event.Event) -> None:
        """
        Dispatch a keyboard-related event to all components.

        Args:
            event (pygame.event.Event): The keyboard event to handle.
        """
        if event.type in [pygame.KEYDOWN, pygame.KEYUP]:
            for component in self.components:
                component.handle_keyboard_event(event)

    def exit(self) -> None:
        """
        Save settings, clean up resources, and exit the simulation.

        Ensures proper shutdown of the program, including saving settings
        and quitting Pygame.
        """
        if isinstance(sys.exc_info()[1], KeyboardInterrupt):
            print()
        print("Quitting AntCode")
        self.settings.save()
        pygame.quit()
        sys.exit()

    def run(self) -> None:
        """
        Run the main simulation loop.

        Handles user inputs, processes commands, updates the screen,
        and manages the simulation's progression.
        """
        try:
            print("--------------------------------------------------------")
            print(Fore.CYAN)
            print(
                f"                 _    {Fore.GREEN}_____          _      {Fore.CYAN}"
            )
            print(
                f"     /\\         | |  {Fore.GREEN}/ ____|        | |     {Fore.CYAN}"
            )
            print(
                f"    /  \\   _ __ | |_{Fore.GREEN}| |     ___   __| | ___ {Fore.CYAN}"
            )
            print(
                f"   / /\\ \\ | '_ \\| __| {Fore.GREEN}|    / _ \\ / _` |/ _ \\{Fore.CYAN}"
            )
            print(
                f"  / ____ \\| | | | |_{Fore.GREEN}| |___| (_) | (_| |  __/{Fore.CYAN}"
            )
            print(
                f" /_/    \\_\\_| |_|\\__|{Fore.GREEN}\\_____|___/ \\__,_|\\___|{Fore.CYAN}"
            )
            print(f"                                            ")
            print(f"{Fore.RESET}                                            ")

            print(
                f"{Style.BRIGHT}AntCode - {Style.NORMAL}A team resource collection game for CS courses"
            )
            print(
                f"Thanks to:\n    {Fore.CYAN}\033]8;;https://github.com/Grace-H\033\\@Grace-H\033]8;;\033\\{Fore.RESET} for the simulation code\n    {Fore.CYAN}\033]8;;https://github.com/a1silver\033\\@a1silver\033]8;;\033\\{Fore.RESET} for the UI implementation"
            )
            print(
                f'Type {Style.DIM}"help"{Style.NORMAL} to see the full list of commands available'
            )
            if self.settings["fancyGraphics"]:
                print(
                    "\nWARNING: Fancy graphics is enabled. Type 'config fancyGraphics false' to disable if you encounter lag."
                )

            self.running = threading.Event()

            self.console_input_thread = threading.Thread(
                target=self.get_console_input, daemon=True
            )
            self.console_input_thread.start()

            while not self.running.is_set():
                self.clock.tick(30)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running.set()
                        print(Style.NORMAL, end="")
                        continue

                    self.handle_mouse_event(event)
                    self.handle_keyboard_event(event)
                    self.handle_event(event)

                while not self.command_queue.empty():
                    message = self.command_queue.get()
                    command = message.message

                    if command == "load":
                        self.load_maps()
                    elif command == "generate":
                        print(Style.NORMAL)
                        os.system(f"{sys.executable} ./antcode/main.py")
                    elif command == "config":
                        try:
                            self.settings[message.data[0]] = message.data[1]
                            print(
                                f"Updated {Style.DIM}'{message.data[0]}'{Style.NORMAL} to {Fore.GREEN}'{message.data[1]}'{Fore.RESET}"
                            )

                            if (
                                message.data[0] == "cellSize"
                                or message.data[0] == "showTopBar"
                            ):
                                self.reset_screen()
                            elif message.data[0] == "stepsPerSecond":
                                self.map_switch_interval = (
                                    1000 // self.settings["stepsPerSecond"]
                                )
                        except TypeError as e:
                            print(f"{Fore.LIGHTRED_EX}{e}{Fore.RESET}")
                    else:
                        if self.maps is None:
                            print(
                                f"{Fore.LIGHTRED_EX}No map is currently loaded{Fore.RESET}"
                            )
                        else:
                            if command == "toggle":
                                self.settings.simulationPaused = (
                                    not self.settings.simulationPaused
                                )
                                print(
                                    f"Simulation {f'{Fore.GREEN}un' if not self.settings.simulationPaused else Fore.YELLOW}paused{Fore.RESET}"
                                )
                            elif command == "pause":
                                self.settings.simulationPaused = True
                                print(f"Simulation {Fore.YELLOW}paused{Fore.RESET}")
                            elif command == "play":
                                self.settings.simulationPaused = False
                                print(f"Simulation {Fore.GREEN}unpaused{Fore.RESET}")
                            elif command == "skip-start":
                                self.skip_start()
                                print(
                                    f"Step: {Fore.YELLOW if self.current_map_index + 1 == len(self.maps) else Fore.GREEN}{self.current_map_index + 1}{Fore.RESET} / {Fore.YELLOW}{len(self.maps)}{Fore.RESET}"
                                )
                            elif command == "step-back":
                                self.step_backward()
                                print(
                                    f"Step: {Fore.YELLOW if self.current_map_index + 1 == len(self.maps) else Fore.GREEN}{self.current_map_index + 1}{Fore.RESET} / {Fore.YELLOW}{len(self.maps)}{Fore.RESET}"
                                )
                            elif command == "step-forward":
                                self.step_forward()
                                print(
                                    f"Step: {Fore.YELLOW if self.current_map_index + 1 == len(self.maps) else Fore.GREEN}{self.current_map_index + 1}{Fore.RESET} / {Fore.YELLOW}{len(self.maps)}{Fore.RESET}"
                                )
                            elif command == "skip-end":
                                self.skip_end()
                                print(
                                    f"Step: {Fore.YELLOW if self.current_map_index + 1 == len(self.maps) else Fore.GREEN}{self.current_map_index + 1}{Fore.RESET} / {Fore.YELLOW}{len(self.maps)}{Fore.RESET}"
                                )
                            elif command == "steps":
                                print(
                                    f"Step: {Fore.YELLOW if self.current_map_index + 1 == len(self.maps) else Fore.GREEN}{self.current_map_index + 1}{Fore.RESET} / {Fore.YELLOW}{len(self.maps)}{Fore.RESET}"
                                )
                            elif command == "score":
                                print(
                                    f"North Score: {self.maps[self.current_map_index].north_points}\nSouth Score: {self.maps[self.current_map_index].south_points}"
                                )
                            elif command == "winner":
                                print(f"Winner for this game: {self.winner}")
                    if self.command_queue.empty():
                        self.command_queue.put(Message("CONTINUE"))
                        break

                current_time = pygame.time.get_ticks()

                if (
                    self.maps is not None
                    and current_time - self.last_map_switch_time
                    >= self.map_switch_interval
                    and not self.settings.simulationPaused
                ):
                    self.last_map_switch_time = current_time
                    self.current_map_index = (self.current_map_index + 1) % len(
                        self.maps
                    )
                    self.map_component.map_data = self.maps[
                        self.current_map_index
                    ].board

                    if (
                        self.current_map_index == len(self.maps) - 1
                        and self.settings["stopOnLastStep"]
                    ):
                        self.settings.simulationPaused = True

                self.screen.fill(BLACK)

                for component in self.components:
                    component.draw(self.screen)

                pygame.display.flip()
                pygame.display.update()

            self.exit()
        except KeyboardInterrupt:
            print(Style.NORMAL, end="")
            self.exit()

    def __init__(self):
        """
        Initialize the AntSimulation instance with settings, components, and simulation state.
        """
        self.settings = AntSettings("settings.json")

        self.running = None

        self.command_manager = CommandManager(self)
        self.command_manager.register_command(HelpCommand(self.command_manager))
        self.command_manager.register_command(ConfigCommand(self.command_manager))
        self.command_manager.register_command(
            Command(
                "load",
                "Load a new game",
                "Open an interactive file dialog where you can choose an Antcode map file.  The file will be evaluated for validity; any non-Antcode map files will be ignored.",
                lambda args: self.command_queue.put(Message("load")),
            )
        )
        self.command_manager.register_command(
            Command(
                "toggle",
                "Toggle the simulation playback state",
                "Toggle simulation playback.  If the simulation is currently running, it will be paused, and vice versa.",
                lambda args: self.command_queue.put(Message("toggle")),
                [""],
            )
        )
        self.command_manager.register_command(
            Command(
                "pause",
                "Pause the simulation",
                "Temporarily stop playback of the simulation by preventing map data from updating.  Functionality of other commands is not affected.",
                lambda args: self.command_queue.put(Message("pause")),
            )
        )
        self.command_manager.register_command(
            Command(
                "play",
                "Unpause the simulation",
                "Resume playback of the simulation.",
                lambda args: self.command_queue.put(Message("play")),
            )
        )
        self.command_manager.register_command(
            Command(
                "skip-start",
                "Skip to the start",
                "Skip to the very start of the simulation, or in other words, the first step.",
                lambda args: self.command_queue.put(Message("skip-start")),
                ["ss", "aa"],
            )
        )
        self.command_manager.register_command(
            Command(
                "step-back",
                "Step once backward",
                "Decrement the step counter and update the map data.",
                lambda args: self.command_queue.put(Message("step-back")),
                ["step-backward", "sb", "a"],
            )
        )
        self.command_manager.register_command(
            Command(
                "step-forward",
                "Step once forward",
                "Increment the step counter and update the map data.",
                lambda args: self.command_queue.put(Message("step-forward")),
                ["step-front", "step", "sf", "d", "s"],
            )
        )
        self.command_manager.register_command(
            Command(
                "skip-end",
                "Skip to the end",
                "Skip to the very end of the simulation, or in other words, the last step.",
                lambda args: self.command_queue.put(Message("skip-end")),
                ["se", "dd"],
            )
        )
        self.command_manager.register_command(
            Command(
                "steps",
                "View current steps out of the total",
                "Print the step number the simulation is currently on and the total number of steps in the loaded map.",
                lambda args: self.command_queue.put(Message("steps")),
            )
        )
        self.command_manager.register_command(
            Command(
                "score",
                "View the current score for each team",
                "Print the North and South teams' scores for the current step.",
                lambda args: self.command_queue.put(Message("score")),
            )
        )
        self.command_manager.register_command(
            Command(
                "winner",
                "View the game's winner",
                "Print the loaded game's winner.  This value is independent of the current step.",
                lambda args: self.command_queue.put(Message("winner")),
            )
        )
        self.command_manager.register_command(
            Command(
                "generate",
                "Generate a new test map",
                "Run the original text-based Antcode simulation to generate new games and maps.",
                lambda args: self.command_queue.put(Message("generate")),
                ["gen"],
            )
        )
        self.command_manager.register_command(
            Command(
                "quit",
                "Quit the simulation",
                "Save all settings and shut down the program.",
                lambda args: self.running.set(),
                ["exit"],
            )
        )

        self.command_queue = Queue()

        self.components = []
        self.current_map_index = 0

        self.screen_width, self.screen_height = (
            len(BLANK_MAP[0]) * self.settings["cellSize"],
            (len(BLANK_MAP)) * self.settings["cellSize"],
        )
        pygame.init()
        pygame.display.set_caption("AntCode")
        try:
            pygame.display.set_icon(pygame.image.load("antcode_ui/images/icon.png"))
        except FileNotFoundError as e:
            print(f"Failed to set pygame icon: {e}")
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        self.clock = pygame.time.Clock()

        self.board_size: Optional[Tuple[int, int]] = None
        self.winner: Optional[str] = None
        self.maps: Optional[list[Round]] = None
        self.has_five_ants = False

        self.map_component = MapComponent(
            0, 0, self.screen_width, self.screen_height, BLANK_MAP, self
        )
        self.add_component(self.map_component)

        self.map_switch_interval = 1000 // self.settings["stepsPerSecond"]
        self.last_map_switch_time = pygame.time.get_ticks()

    def get_console_input(self) -> None:
        """
        Run the main console input loop for handling user commands.

        This function continuously prompts the user for input until the application is stopped.
        Commands are interpreted dynamically, and recognized commands are added to the command queue for processing by the main thread.

        Returns:
            None
        """
        while not self.running.is_set():
            try:
                print("--------------------------------------------------------")
                commandList = input(f"> {Style.DIM}").lower().split(" ")
                print(Style.NORMAL, end="")
                command = commandList[0:1][0]
                args = commandList[1:]

                try:
                    if (
                        self.command_manager.execute_command(command, args) is False
                        or command == "help"
                    ):
                        continue
                except KeyError as e:
                    message = str(e)
                    print(message[1 : len(message) - 1])
                    continue

                while True:
                    cmdList = [msg.message for msg in list(self.command_queue.queue)]
                    if cmdList == ["CONTINUE"]:
                        self.command_queue.get()
                        break
            except EOFError:
                break
