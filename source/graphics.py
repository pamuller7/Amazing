from enum import Enum
from typing import Dict, List


class Theme:
    def __init__(
        self,
        wall_color: str,
        draw_color: str,
        entry_color: str,
        head_solver_color: str,
        tail_solver_color: str,
        exit_color: str,
    ) -> None:
        self.wall_color = wall_color
        self.draw_color = draw_color
        self.entry_color = entry_color
        self.head_solver_color = head_solver_color
        self.tail_solver_color = tail_solver_color
        self.exit_color = exit_color


class Colors(Enum):
    BG_GREY = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_ORANGE = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_PURPULE = "\033[45m"
    BG_LIGHT_BLUE = "\033[46m"
    BG_WHITE = "\033[47m"
    WHITE = "\033[97m"
    LIGHT_BLUE = "\033[96m"
    PURPULE = "\033[95m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    GREY = "\033[90m"
    LIGHT_GREY = "\033[89m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


themes: Dict[str, Theme] = {
    "red": Theme(
        Colors.BG_RED.value,
        Colors.BG_ORANGE.value,
        Colors.BG_GREEN.value,
        Colors.BG_ORANGE.value,
        Colors.BG_PURPULE.value,
        Colors.BG_RED.value,
    ),
    "black": Theme(
        Colors.BG_GREY.value,
        Colors.BG_GREY.value,
        Colors.BG_GREY.value,
        Colors.BG_GREY.value,
        Colors.BG_GREY.value,
        Colors.BG_GREY.value,
    ),
    "green": Theme(
        Colors.BG_GREEN.value,
        Colors.BG_PURPULE.value,
        Colors.BG_GREEN.value,
        Colors.BG_ORANGE.value,
        Colors.BG_BLUE.value,
        Colors.BG_RED.value,
    ),
    "squeleton": Theme(
        Colors.BG_WHITE.value,
        Colors.BG_GREY.value,
        Colors.BG_GREEN.value,
        Colors.BG_GREY.value,
        Colors.BG_LIGHT_BLUE.value,
        Colors.BG_RED.value,
    ),
    "rgb": Theme(
        Colors.BG_BLUE.value,
        Colors.BG_GREEN.value,
        Colors.BG_GREEN.value,
        Colors.BG_GREEN.value,
        Colors.BG_RED.value,
        Colors.BG_RED.value,
    ),
}

drawings: Dict[str, List[List[int]]] = {
    "42": [
        [1, 0, 0, 0, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 1],
    ],
    "smiley": [
        [1, 1, 0, 0, 0, 1, 1],
        [1, 1, 0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 0, 0, 0, 1, 1],
        [0, 1, 1, 1, 1, 1, 0],
    ],
    "pac-man": [
        [0, 0, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 1, 1, 1, 1, 1, 0],
    ],
    "no_drawing": [[]],
}
