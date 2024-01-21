from enum import IntEnum, Enum

class GameStage(IntEnum):
    FIRST_COLLECTING = 0
    FIRST_CLASH = 1
    SECOND_COLLECTING = 2
    SECOND_CLASH = 3


class PlayerState(str, Enum):
    IN_COLLECTING = "in_collecting"
    AWAIT_CLASH_START = "await_clash_start" # after player collected all available cards
    IN_CLASH = "in_clash"
    AWAIT_CLASH_END = "await_clash_end" # after player used all his action cards
