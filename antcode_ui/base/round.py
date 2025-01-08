class Round:
    """
    A class representing a round in a game, with associated points and board state.

    This class holds information about a specific round of a game, including the round number, the points scored by the north and south teams, and the game board for that round.

    Attributes:
        number (int): The round number.
        north_points (int): The points scored by the north team in the round.
        south_points (int): The points scored by the south team in the round.
        board (list[str]): The game board for the round.

    Methods:
        __init__(number: int, north_points: int, south_points: int, board: Any): Initializes the round with the number, team points, and board.
    """

    def __init__(
        self, number: int, north_points: int, south_points: int, board: list[str]
    ):
        self.number = number
        self.north_points = north_points
        self.south_points = south_points
        self.board = board
