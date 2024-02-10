from enum import Enum, IntEnum

class MessageType(str, Enum):
    COLLECTING_MOVE = 'collecting_move'
    CLASH_ACTION_MOVE = 'clash_action_move'
    CLASH_REACTION_MOVE = 'clash_reaction_move'
    SURRENDER_MOVE = 'surrender_move'


class ResponseTime(IntEnum):
    COLLECTION_PHASE_RESPONSE_TIME = 15
    CLASH_PHASE_RESPONSE_TIME = 30