from channels.db import database_sync_to_async

from ...messager.scheduler import get_all_game_tasks, update_game_state
from ...enums import GameStage, GameState


@database_sync_to_async
def get_opponent_player(self, game_user):
    if game_user.id == self.student_player.id:
        return self.teacher_player
    else:
        return self.student_player

@database_sync_to_async
def update_after_turn(self):
    current_move_player = self.next_move_player
    current_move_type = self.next_move_type

    if current_move_type == "action":
        self.next_move_type = "reaction"
        if current_move_player == "student":
            self.next_move_player = "teacher"
        else:
            self.next_move_player = "student"
    else:
        self.next_move_type = "action"

    self.save()
    return True

@database_sync_to_async
def backup(self, consumer):
    self.turns_to_inc = consumer.get_turns_to_inc()
    self.moves_per_clash = consumer.get_moves_per_clash()
    self.stage = True if consumer.get_game_stage() == GameStage.CLASH else False
    self.delayed_tasks = get_all_game_tasks(
        str(consumer.get_game_user().id), str(consumer.get_opponent().id)
    )
    self.save()
    update_game_state(str(self.id), GameState.BACKUPED)
