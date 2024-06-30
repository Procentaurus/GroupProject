from ...scheduler.scheduler import get_all_delayed_tasks

def get_opponent_player_impl(game, game_user):
    if game_user.id == game.student_player.id:
        return game.teacher_player
    else:
        return game.student_player

def update_after_turn_impl(game):
    current_move_player = game.next_move_player
    current_move_type = game.next_move_type

    if current_move_type == "action":
        game.next_move_type = "reaction"
        if current_move_player == "student":
            game.next_move_player = "teacher"
        else:
            game.next_move_player = "student"
    else:
        game.next_move_type = "action"

    game.save()
    return True

def backup_impl(game, consumer):
    game.turns_to_inc = consumer.get_turns_to_inc()
    game.moves_per_clash = consumer.get_moves_per_clash()
    game.stage = bool(consumer.get_game_stage())
    game.delayed_tasks = get_all_delayed_tasks()
    game.is_backuped = True
    game.save()
