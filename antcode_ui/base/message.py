# Third-Party Imports
from typing import Any, Optional


class Message:
    """
    A class for encapsulating a message with optional additional data that can be passed between threads in a thread-safe queue.
    The data can be of any type and is stored as an optional attribute.

    Attributes:
        message (str): The content of the message.
        data (Optional[Any]): Optional additional data associated with the message.

    Methods:
        __init__(message: str, data: Optional[Any] = None): Initializes the message object with a message and optional data.
    """

    def __init__(self, message: str, data: Optional[Any] = None) -> None:
        """
        Initializes a message object with a given message string and optional data.

        Args:
            message (str): The message content.
            data (Optional[Any], optional): Optional additional data associated with the message.
        """
        self.message = message
        self.data = data
