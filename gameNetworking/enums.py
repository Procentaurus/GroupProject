from enum import Enum, IntEnum


class MessageType(str, Enum):
    PURCHASE_MOVE = 'purchase_move'
    READY_MOVE = 'ready_move'
    CLASH_ACTION_MOVE = 'clash_action_move'
    CLASH_REACTION_MOVE = 'clash_reaction_move'
    SURRENDER_MOVE = 'surrender_move'


class ResponseTime(IntEnum):
    HUB_TIME = 100
    CLASH_PHASE_RESPONSE_TIME = 30


class GameStage(IntEnum):
    HUB = 0
    CLASH = 1


class PlayerState(str, Enum):
    IN_HUB = "in_hub"
    AWAIT_CLASH_START = "await_clash_start" # after player collected all available cards
    IN_CLASH = "in_clash"
    AWAIT_CLASH_END = "await_clash_end" # after player used all his action cards