from enum import IntEnum, Enum

class GameStage(IntEnum):
    HUB = 0
    CLASH = 1

class PlayerState(str, Enum):
    IN_HUB = "in_hub"
    AWAIT_CLASH_START = "await_clash_start" # after player collected all available cards
    IN_CLASH = "in_clash"
    AWAIT_CLASH_END = "await_clash_end" # after player used all his action cards

