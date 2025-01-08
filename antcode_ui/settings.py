# Standard Library Imports
import json

# Third-Party Imports
from typing import Dict, Any


class AntSettings:
    """
    A class for managing simulation settings stored in a JSON file.

    This class provides functionality to load and save settings, retrieve and set specific values, and validate data types for each setting. The settings are stored as key-value pairs in a dictionary, with type hints used to ensure values are of the correct type.

    Attributes:
        json_file (str): Path to the JSON file storing the settings.
        data (Dict[str, Any]): A dictionary holding the settings data.
        type_hints (Dict[str, str]): A dictionary holding the expected types for each setting.
        simulationPaused (bool): Indicates whether the simulation is paused or running.

    Methods:
        __getitem__(key: str) -> Any: Retrieves the value for a given key.
        __setitem__(key: str, value: Any) -> None: Sets the value for a given key and validates its type.
        __delitem__(key: str) -> None: Deletes the key-value pair for a given key.
        __contains__(key: str) -> bool: Checks if a key exists in the settings data.
        __repr__() -> str: Returns a string representation of the settings data.
        save() -> None: Saves the current settings data and type hints to the JSON file.
        load() -> None: Loads the settings data and type hints from the JSON file.
        _validate_type(value: Any, expected_type: str) -> bool: Validates if a value matches the expected type.
    """

    DEFAULT_SETTINGS = {
        "pauseOnStep": [True, "bool"],
        "stepsPerSecond": [5, "int"],
        "cellSize": [30, "int"],
        "autoSave": [True, "bool"],
        "stopOnLastStep": [True, "bool"],
        "fancyGraphics": [False, "bool"],
        "showTopBar": [True, "bool"],
    }
    SETTINGS_DESCRIPTIONS = {
        "pauseOnStep": "Pause the simulation instantly if the user manually steps forward or backward.",
        "stepsPerSecond": "How many times the simulation's map will advance to the next step per second.",
        "cellSize": "How many pixels tall and wide each map cell will be.",
        "autoSave": "Auto-save the simulation configuration when modifying settings.",
        "stopOnLastStep": "Instantly pause the simulation when the last step is reached.",
        "fancyGraphics": "Whether plain colors or detailed graphics are used to render certain cells.",
        "showTopBar": "Show or hide the panel containing key game details such as step number and team scores."
    }

    def __init__(self, json_file: str) -> None:
        """
        Initializes the AntSettings object with the given JSON file.

        Args:
            json_file (str): Path to the JSON file used to store the settings.
        """
        self.json_file = json_file
        self.data: Dict[str, Any] = {}
        self.type_hints: Dict[str, str] = {}
        self.descriptions: Dict[str, str] = {}

        self.simulationPaused = True

        self.load()

    def __getitem__(self, key: str) -> Any:
        """
        Fetches the value associated with the given key.

        Args:
            key (str): The key to retrieve the value for.

        Returns:
            Any: The value associated with the key.

        Raises:
            KeyError: If the key does not exist in the data.
        """
        return self.data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Sets the value for a given key. If the key already exists, validates the type of the value.

        Args:
            key (str): The key to set the value for.
            value (Any): The value to associate with the key.

        Raises:
            TypeError: If the value type does not match the expected type.
        """
        if key in self.data:
            expected_type = self.type_hints[key]
            if not self._validate_type(value, expected_type):
                raise TypeError(
                    f"Expected value of type '{expected_type}' for key '{key}', got '{type(value).__name__}' instead."
                )

        self.data[key] = value

        if self.data["autoSave"]:
            self.save()

    def __delitem__(self, key: str) -> None:
        """
        Deletes the key-value pair for the given key.

        Args:
            key (str): The key to delete from the data.
        """
        del self.data[key]
        del self.type_hints[key]

        if self.data["autoSave"]:
            self.save()

    def __contains__(self, key: str) -> bool:
        """
        Checks if a key exists in the settings data.

        Args:
            key (str): The key to check for existence.

        Returns:
            bool: True if the key exists in the data, False otherwise.
        """
        return key in self.data

    def __repr__(self) -> str:
        """
        Returns a string representation of the settings data.

        Returns:
            str: String representation of the data dictionary.
        """
        return repr(self.data)

    def save(self) -> None:
        """
        Saves the current settings data and type hints to the JSON file.

        Raises:
            IOError: If there is an issue writing to the file.
        """
        combined_data = {
            key: [self.data[key], self.type_hints[key]] for key in self.data
        }
        with open(self.json_file, "w") as file:
            json.dump(combined_data, file, indent=4)

    def load(self) -> None:
        """
        Loads the settings data and type hints from the JSON file.
        If the loading fails (e.g., file not found or invalid JSON),
        the default settings will be applied. It also ensures that if any key is missing
        or if the type of any setting value is invalid, the default values are applied.
        """
        try:
            with open(self.json_file, "r") as file:
                combined_data = json.load(file)
                self.data = {}
                self.type_hints = {}

                for key, (value, expected_type) in self.DEFAULT_SETTINGS.items():
                    if key in combined_data:
                        current_value = combined_data[key][0]
                        current_type = combined_data[key][1]
                        if self._validate_type(current_value, current_type):
                            self.data[key] = current_value
                            self.type_hints[key] = current_type
                        else:
                            self.data[key] = value
                            self.type_hints[key] = expected_type
                    else:
                        self.data[key] = value
                        self.type_hints[key] = expected_type

                self.save()

        except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
            self.data = {key: value[0] for key, value in self.DEFAULT_SETTINGS.items()}
            self.type_hints = {
                key: value[1] for key, value in self.DEFAULT_SETTINGS.items()
            }
            self.save()

        self.descriptions = {
            key: value for key, value in self.SETTINGS_DESCRIPTIONS.items()
        }
        
    def get_key_type(self, key: str) -> str:
        """
        Get the proper type name for a given config key

        Args:
            key (str): The key to get a type name for

        Returns:
            str: The resulting type name
        """
        type_map = {
            "bool": "boolean",
            "int": "integer",
            "float": "float",
            "str": "string",
        }
        if key in self.type_hints and self.type_hints[key] in type_map:
            return type_map[self.type_hints[key]]
        return "none"

    @staticmethod
    def _validate_type(value: Any, expected_type: str) -> bool:
        """
        Validates whether a value matches the expected type.

        Args:
            value (Any): The value to validate.
            expected_type (str): The expected type as a string.

        Returns:
            bool: True if the value matches the expected type, False otherwise.
        """
        type_map = {
            "bool": bool,
            "int": int,
            "float": float,
            "str": str,
            "list": list,
            "dict": dict,
            "NoneType": type(None),
        }
        return isinstance(value, type_map.get(expected_type, object))
