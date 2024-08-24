from enum import Enum, IntEnum


class MessageType(str, Enum):
    PURCHASE_MOVE = 'purchase_move'
    READY_MOVE = 'ready_move'
    ACTION_MOVE = 'action_move'
    REACTION_MOVE = 'reaction_move'
    SURRENDER_MOVE = 'surrender_move'
    REROLL_MOVE = 'reroll_move'


class ResponseTime(IntEnum):
    HUB_TIME = 100
    CLASH_PHASE_RESPONSE_TIME = 30


class GameStage(IntEnum):
    HUB = 0
    CLASH = 1


class PlayerState(str, Enum):
    IN_HUB = "in_hub"

    # after player collected all available cards
    AWAIT_CLASH_START = "await_clash_start"
    IN_CLASH = "in_clash"

    # after player used all his action cards
    AWAIT_CLASH_END = "await_clash_end"


class GameState(str, Enum):
    DELETED = 'deleted'
    BACKUPED = 'backuped'
    ONGOING = 'ongoing'
