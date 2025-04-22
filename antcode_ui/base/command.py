# Standard Library Imports
from copy import deepcopy

# Third-Party Imports
import difflib
from typing import Callable, Optional, Dict
from colorama import Fore, Back, Style

# Local Imports
from .message import Message


class Command:
    """
    A class representing a text command for a console-based application.

    Attributes:
        command (str): The string that identifies the command.
        short_description (str): A brief description of what the command does.
        long_description (str): A detailed description of what the command does.
        executor (Callable[[], bool]): A function that gets executed when the command is run.
        aliases (Optional[list[str]]): A list of alternative command strings for the same command.

    Methods:
        execute() -> bool:
            Executes the command's executor function and returns its result.
    """

    def __init__(
        self,
        command: str,
        short_description: str,
        long_description: str,
        executor: Callable[[Optional[list[str]]], bool],
        aliases: Optional[list[str]] = None,
    ) -> None:
        """
        Initializes the Command object with the given attributes.

        Args:
            command (str): The string representing the command.
            short_description (str): A brief description of the command.
            long_description (str): A detailed description of the command.
            executor (Callable[[], bool]): The function to execute when the command is invoked.
            aliases (Optional[list[str]]): A list of alternative command strings (default is None).
            is_alias (bool): Marks this command as an alias of another command.
        """
        self.command = command
        self.executor = executor
        self.short_description = short_description
        self.long_description = long_description
        self.aliases = aliases if aliases else []

        self.is_alias = False

    def execute(self, args: Optional[list[str]] = None) -> bool:
        """
        Executes the command's executor function.

        Returns:
            bool: The result of the executor function.
        """
        return self.executor(args)

    def alias_copy(self):
        """
        Returns a fully independent copy of this command instance with the `is_alias` flag enabled.

        Returns:
            Command: The `is_alias`-marked copy of this instance
        """
        command_alias = deepcopy(self)
        command_alias.is_alias = True
        return command_alias


class CommandManager:
    """
    A class for managing a collection of commands in a console-based application.

    Attributes:
        commands (Dict[str, Command]): A dictionary of commands where keys are command strings.

    Methods:
        register_command(command: Command) -> None:
            Registers a new command.

        delete_command(command: str) -> None:
            Deletes a command by its string identifier.

        execute_command(command: str) -> bool:
            Executes a command by its string identifier.

        help_command(command_str: Optional[str] = None) -> None:
            Displays help for all commands or a specific command.
    """

    def __init__(self, simulation) -> None:
        """
        Initializes the CommandManager with an empty set of commands.
        """
        self.commands: Dict[str, Command] = {}
        self.simulation = simulation

    def register_command(self, command: Command) -> None:
        """
        Registers a new command in the CommandManager.

        Args:
            command (Command): The command object to register.

        Raises:
            KeyError: If a command with the same string already exists.
        """
        if command.command in self.commands:
            raise KeyError(f"Command '{command.command}' already exists.")
        self.commands[command.command] = command
        if command.aliases:
            for alias in command.aliases:
                self.commands[alias] = command.alias_copy()

    def delete_command(self, command: str) -> None:
        """
        Deletes a command from the CommandManager.

        Args:
            command (str): The command string to delete.

        Raises:
            KeyError: If the command does not exist.
        """
        if command not in self.commands:
            raise KeyError(f"Command '{command}' not found.")
        del self.commands[command]

    def execute_command(self, command: str, args: Optional[list[str]] = None) -> bool:
        """
        Executes a command by its string identifier.

        Args:
            command (str): The command string to execute.

        Returns:
            bool: The result of the command's execution.

        Raises:
            KeyError: If the command does not exist.
        """
        if command not in self.commands:
            raise KeyError(f"Command '{command}' not found.")
        return self.commands[command].execute(args)


class HelpCommand(Command):
    """
    A special command for displaying help information for all commands or a specific command.

    This extends the Command class and accepts one optional argument for looking up a specific command.

    Methods:
        execute(command_str: Optional[str] = None) -> bool:
            Executes the help command, showing information for a specific command or all commands.
    """

    def __init__(self, command_manager: CommandManager) -> None:
        """
        Initializes the HelpCommand with a reference to the CommandManager.

        Args:
            command_manager (CommandManager): The CommandManager instance to interact with.
        """
        super().__init__(
            command="help",
            short_description="Display this help message.",
            long_description="Displays a list of all available commands with their descriptions, "
            "or a specific command's long description and aliases if provided.",
            executor=self.execute,
        )
        self.command_manager = command_manager

    def help_command(self, command_str: Optional[str] = None) -> None:
        """
        Displays help for all commands or a specific command.

        Args:
            command_str (Optional[str]): The specific command string to show help for (default is None).

        Displays a list of commands with their short descriptions. If a command string is provided,
        it will display the long description and aliases.
        """
        if command_str:
            if command_str in self.command_manager.commands:
                command = self.command_manager.commands[command_str]
                print(
                    f"{Style.DIM}{command.command}{Style.NORMAL} - {command.short_description}\n\n{command.long_description}"
                )
                if command.aliases:
                    if command.long_description != "":
                        print()
                    print(
                        f"Aliases: {Fore.GREEN}{', '.join('<ENTER>' if alias == '' and command.command == 'toggle' else alias for alias in command.aliases)}{Fore.RESET}"
                    )
            else:
                print(f"Command '{command_str}' not found.")
        else:
            print("Available commands\n")
            print(
                f'Type {Style.DIM}"help [command]"{Style.NORMAL} to view help for a specific command\n'
            )
            cmd_list = [
                command.command
                for command in self.command_manager.commands.values()
                if not command.is_alias
            ]
            cmd_list.sort()
            for i, string in enumerate(cmd_list):
                print(
                    string.ljust(max(map(len, cmd_list), default=0) + 5),
                    end="\n" if (i + 1) % 2 == 0 else "",
                )
            print()

    def execute(self, args: Optional[list[str]] = None) -> bool:
        """
        Executes the help command, either displaying help for all commands or a specific command.

        Args:
            args (Optional[[list[str]]]): Array of command arguments as strings

        Returns:
            bool: Always returns True as the help command typically does not fail.
        """
        command_str = args[0] if args and len(args) > 0 else None
        self.help_command(command_str)
        return True


class ConfigCommand(Command):
    def __init__(self, command_manager: CommandManager) -> None:
        super().__init__(
            command="config",
            short_description="Modify simulation settings",
            long_description="Start an interactive text prompt to view, query, or modify the simulation's configuration options.",
            executor=self.execute,
        )
        self.command_manager = command_manager

    def get_sorted_key_matches(self, key_name: str) -> list[tuple[str, float]]:
        """
        Retrieve a sorted list of setting keys ranked by similarity to the given key name.

        Args:
            key_name (str): The input key name to compare against existing keys.

        Returns:
            list[tuple[str, float]]: A list of tuples containing key names and their similarity scores.
        """
        keys = list(self.command_manager.simulation.settings.data.keys())

        similarity_scores = {
            key: difflib.SequenceMatcher(None, key_name, key).ratio() for key in keys
        }

        sorted_keys_with_scores = sorted(
            similarity_scores.items(), key=lambda item: item[1], reverse=True
        )

        return sorted_keys_with_scores

    def get_best_match_key(self, key_name: str) -> str:
        """
        Retrieve the best-matching configuration key based on similarity to the provided input.

        This function uses a scoring mechanism to determine the similarity between the given key name
        and the available configuration keys. If no suitable match is found, it provides feedback
        to the user and returns `False`.

        Args:
            key_name (str): The name of the key to search for.

        Returns:
            str: The best-matching key name if a good match is found.
            bool: Returns `False` if no matches or no sufficiently good match is found.
        """
        sorted_matches = self.get_sorted_key_matches(key_name)

        if not sorted_matches:
            print("No key found.")
            return False

        scores = [score for _, score in sorted_matches]
        if max(scores) < 0.2 or (max(scores) - min(scores) < 0.1 and max(scores) < 0.3):
            print("No good match found.")
            return False

        return sorted_matches[0][0]

    def update_config(
        self, config_key: Optional[str] = None, config_value: Optional[str] = None
    ) -> bool:
        """
        Interactively update or query configuration settings.

        This function provides a menu with three options:
        1. Modify an existing configuration setting.
        2. Query the value of a configuration setting.
        3. View all current settings and their descriptions.

        For options 1 and 2, it uses a similarity-based matching algorithm to find the best
        match for the input key. Users can update the matched key's value or view its details.
        Option 3 prints all current settings with their descriptions.

        Returns:
            bool:
                - `True` if a setting is successfully modified.
                - `False` otherwise (e.g., user cancels, queries a value, or views settings).
        """
        if config_key:
            matched_key = self.get_best_match_key(config_key)

            if not matched_key:
                return False

            new_value = None

            if config_value:
                new_value = config_value
            else:
                new_value = input(
                    f"Enter a new {self.command_manager.simulation.settings.get_key_type(matched_key)} value for '{matched_key}' (leave blank to cancel): {Style.DIM}"
                )
                print(Style.NORMAL, end="")

            if new_value == "":
                return False

            try:
                if "." in new_value:
                    new_value = float(new_value)
                else:
                    new_value = int(new_value)
            except ValueError:
                if new_value.lower() in {"true", "false"}:
                    new_value = new_value.lower() == "true"
                elif new_value.lower() == "none":
                    new_value = None

            self.command_manager.simulation.command_queue.put(
                Message("config", (matched_key, new_value))
            )
            return True

        option = -1
        while option < 1 or option > 3:
            try:
                print(
                    f"{Style.DIM}(1){Style.NORMAL} Modify a setting\n{Style.DIM}(2){Style.NORMAL} Query a setting\n{Style.DIM}(3){Style.NORMAL} View all settings"
                )
                tempInput = input(f"> {Style.DIM}")
                print(Style.NORMAL, end="")
                if tempInput == "":
                    option = 1
                    break
                option = int(tempInput)
            except ValueError:
                print("Please enter a number 1 to 3.")

        if option == 1:
            key_name = input(
                f"Enter a key name (leave blank to cancel): {Style.DIM}"
            ).strip()
            print(Style.NORMAL, end="")

            if key_name == "":
                return False

            matched_key = self.get_best_match_key(key_name)

            if not matched_key:
                return False

            new_value = input(
                f"\n{Style.BRIGHT}>{Style.NORMAL} {Style.DIM}{matched_key}{Style.NORMAL}: {Fore.GREEN}{self.command_manager.simulation.settings[matched_key]}{Fore.RESET}\n  {self.command_manager.simulation.settings.get_key_description(matched_key)}\n\nEnter a new {Fore.CYAN}{self.command_manager.simulation.settings.get_key_type(matched_key)}{Fore.RESET} value for {Style.DIM}'{matched_key}'{Style.NORMAL} (leave blank to cancel): {Style.DIM}"
            )
            print(Style.NORMAL, end="")

            if new_value == "":
                return False

            try:
                if "." in new_value:
                    new_value = float(new_value)
                else:
                    new_value = int(new_value)
            except ValueError:
                if new_value.lower() in {"true", "false"}:
                    new_value = new_value.lower() == "true"
                elif new_value.lower() == "none":
                    new_value = None

            self.command_manager.simulation.command_queue.put(
                Message("config", (matched_key, new_value))
            )
            return True
        elif option == 2:
            key_name = input(
                f"Enter a key name (leave blank to cancel): {Style.DIM}"
            ).strip()
            print(Style.NORMAL, end="")

            if key_name == "":
                return False

            matched_key = self.get_best_match_key(key_name)

            print(
                f"{Style.BRIGHT}>{Style.NORMAL} {Style.DIM}{matched_key}{Style.NORMAL}: {Fore.GREEN}{self.command_manager.simulation.settings[matched_key]}{Fore.RESET}\n  {self.command_manager.simulation.settings.descriptions[matched_key]}"
            )
            return False
        elif option == 3:
            for key, value in self.command_manager.simulation.settings.data.items():
                print(
                    f"{Style.BRIGHT}>{Style.NORMAL} {Style.DIM}{key}{Style.NORMAL}: {Fore.GREEN}{value}{Fore.RESET}\n  {self.command_manager.simulation.settings.descriptions[key]}"
                )
            return False
        else:  # We shouldn't ever reach here
            return False

    def execute(self, args: Optional[list[str]] = None) -> bool:
        """
        Executes the config command.

        Args:
            args (Optional[[list[str]]]): Array of command arguments as strings

        Returns:
            bool: Always returns True as errors are handled internally
        """
        config_key = args[0] if args and len(args) > 0 else None
        config_value = args[1] if args and len(args) > 1 else None
        return self.update_config(config_key, config_value)
