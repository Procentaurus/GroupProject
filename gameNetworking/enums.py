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