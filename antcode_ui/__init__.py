WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Cell colors -- used for fallback if images fail to load
COLORS = {
    "#": (128, 128, 128),  # Wall
    ".": WHITE,  # Empty spot
    # "@": (255, 0, 0),  # North team's ant hill
    # "X": (0, 0, 255),  # South team's ant hill
    # "A": (0, 255, 0),  # Player A
    # "B": (255, 255, 0),  # Player B
    # "C": (255, 165, 0),  # Player C
    # "D": (0, 255, 255),  # Player D
    # "E": (0, 255, 0),  # Player E
    # "F": (255, 255, 0),  # Player F
    # "G": (255, 165, 0),  # Player G
    # "H": (0, 255, 255),  # Player H,
    # "a": (0, 200, 0),  # Player A with food
    # "b": (200, 200, 0),  # Player B with food
    # "c": (200, 200, 0),  # Player C with food
    # "d": (0, 200, 200),  # Player D with food
    # "e": (0, 200, 0),  # Player E with food
    # "f": (200, 200, 0),  # Player F with food
    # "g": (200, 110, 0),  # Player G with food
    # "h": (0, 200, 200),  # Player H with food,
    # "1": (200, 200, 255),  # Light blue for 1
    # "2": (255, 200, 200),  # Light red for 2
    # "3": (200, 255, 200),  # Light green for 3
    # "4": (255, 255, 200),  # Light yellow for 4
    # "5": (255, 220, 180),  # Peach for 5
    # "6": (180, 220, 255),  # Pale cyan for 6
    # "7": (220, 180, 255),  # Pale purple for 7
    # "8": (255, 180, 220),  # Pale pink for 8
    # "9": (255, 220, 140),  # Pale orange for 9
}

VALID_MAP_CHARS = set("#.@XABCDEFGHabcdefgh123456789")

BLANK_MAP = [
    "#####################",
    "#...................#",
    "#...................#",
    "#...................#",
    "#...................#",
    "#...................#",
    "#...................#",
    "#...................#",
    "#...................#",
    "#...................#",
    "#...................#",
    "#...................#",
    "#...................#",
    "#...................#",
    "#...................#",
    "#...................#",
    "#...................#",
    "#...................#",
    "#...................#",
    "#####################",
]

from .settings import AntSettings
from .simulation import AntSimulation
