from enum import Enum

class MessageType(str, Enum):
    COLLECTING_MOVE = 'collecting_move'
    CLASH_ACTION_MOVE = 'clash_action_move'
    CLASH_REACTION_MOVE = 'clash_reaction_move'
    SURRENDER_MOVE = 'surrender_move'