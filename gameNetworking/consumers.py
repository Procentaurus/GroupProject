from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.exceptions import StopConsumer
from autobahn.exception import Disconnected
import logging

from gameMechanics.functions import *

from .models import *
from .middlewares import *
from .queries import *
from .serializers import GameSerializer
from .enums import *

logger = logging.getLogger(__name__)

class GameConsumer(AsyncJsonWebsocketConsumer):

    def __init__(self, *args, **kwargs): # intialization of variables used only by the current user
        super().__init__(*args, **kwargs)

        # game creation
        self.game_id = None
        self.game_user_id = None
        self.opponent_channel_name = None

        # game closure
        self.winner = None
        self.closure_from_user_side = True

        # game run
        self.number_of_game_iteartions = 1
        self.moves_table = [[2,[2,2],1,[1,1]]*self.number_of_game_iteartions]

        self.last_move_send_time = None

    async def connect(self):

        access_token = self.scope.get("token")
        conflict_side = self.scope["url_route"]["kwargs"]["conflict_side"]

        # check if user is using valid token
        if access_token is None:
            await self.close()
            return

        # check if user has chosen a playable conflict side
        if conflict_side != "teacher" and conflict_side != "student":
            await self.close()
            return
        
        game_user = await create_game_user(access_token, conflict_side, self.channel_name)
        self.game_user_id = game_user.id
        # await delete_game_token(game_user)

        number_of_teachers_waiting = await get_number_of_waiting_game_users("teacher")
        number_of_students_waiting = await get_number_of_waiting_game_users("student")

        if number_of_teachers_waiting > 0 and number_of_students_waiting > 0: # initialization of the game itself

            is_teacher = True if game_user.conflict_side == "teacher" else False

            # Initializing game
            player2 = await get_longest_waiting_game_user("student") if is_teacher else await get_longest_waiting_game_user("teacher")
            player1 = game_user

            player1.in_game = True
            player2.in_game = True

            # creating game object
            logger.debug("The game has started")
            game = await create_game(player1, player2)
            self.game_id = game.id
            self.opponent_channel_name = player2.channel_name
            game_serialized = GameSerializer(game).data

            # adding both players' channels to one group
            await self.channel_layer.group_add(f"game_{self.game_id}", player2.channel_name) # group name is game_{UUID of game entity object}
            await self.channel_layer.group_add(f"game_{self.game_id}", player1.channel_name)

            # sending info about game to players and opponent's consumer
            await self.send_message_to_opponent({"game_id": str(self.game_id), "channel_name": self.channel_name}, "game_creation")
            await self.send_message_to_group(game_serialized, "game_start")

            # TODO get first task to each player
            initial_task_for_student = None
            initial_task_for_teacher = None
            opponent_task, my_task = None, None

            opponent_task = initial_task_for_student if is_teacher else initial_task_for_teacher
            my_task = initial_task_for_teacher if is_teacher else initial_task_for_student

            # sending initial tasks to players
            await self.send_message_to_opponent({"task": opponent_task}, "collect_action")
            await self.accept() # accepting user's connection to websocket 
            await self.send_json({"type": "collect_action", "task": my_task})

        else:
            await self.accept() # accepting user's connection to websocket

    async def cleanup(self): # standard cleanup procedure that should be triggered after self.close()

        self.closure_from_user_side = False

        # sending end info with the all data (for now only winner)
        winner = self.winner
        await self.send_message_to_group(winner,"game_end")
        await self.perform_cleanup()

    async def perform_cleanup(self): # is called after game's end, when the end was triggered by the opponent or from standard cleanup procedure

        if self.game_id is None: # block used when opponents consumer already deleted game and game users' data
            flag = await delete_game_user(self.game_user_id)
            if not flag:
                logger.warning("Couldnt delete GameUser from db.")
        else: # block used when no cleaning was perfomed by opponent's consumer
            game = await get_game(self.game_id)
            if game is not None:

                teacher_player, student_player = await get_both_players_from_game(self.game_id)
                flag1, flag2, flag3 = None, None, None

                if student_player is not None:
                    flag1 = await delete_game_user(student_player.id)
                if teacher_player is not None:
                    flag2 = await delete_game_user(teacher_player.id)
                flag3 = await delete_game(self.game_id)

                if not flag3:
                    logger.debug("Couldnt delete Game from db.")
                if not flag1 or not flag2:
                    logger.debug("Couldnt delete GameUser from db.")

    async def disconnect(self, *args):
        
        if self.closure_from_user_side:  # disconnnect from user side
            if self.game_id is not None:
                await self.send_message_to_opponent(None, "game_end")
            await self.perform_cleanup()
        if self.game_id is not None:
            await self.channel_layer.group_discard(f"game_{self.game_id}", self.channel_name)
            
        raise StopConsumer()

    async def receive_json(self, data): # responsible for managing current user messages, effectively main game loop function

        if self.game_id is not None:    # has game started or not

            message_type = data.get('type')
            game = await get_game(self.game_id)
            game_user = await get_game_user_by_id(self.game_user_id)
            game_stage = check_game_stage(self.moves_table[0])

            if game_stage == GameStage.FIRST_COLLECTING or game_stage == GameStage.SECOND_COLLECTING:

                if message_type == MessageType.COLLECTING_MOVE:

                    if (game_stage == GameStage.FIRST_COLLECTING and self.moves_table[0][GameStage.FIRST_COLLECTING] > 0) \
                        or (game_stage == GameStage.SECOND_COLLECTING and self.moves_table[0][GameStage.SECOND_COLLECTING] > 0):   # if the particular stage is in action
                                                                                                                                   # and player has moves left in the stage
                            # choice = data.get("choice")

                            # TODO get appriopriate cards
                            cards = None
                            # TODO save these cards connection with gameuser

                            self.moves_table[0][game_stage] -= 1

                            if self.moves_table[0][game_stage] == 0:
                                await self.send_json({"type": "collect_action", "cards": cards})
                            else:
                                # TODO get a new choice
                                next_task = None
                                await self.send_json({"type": "collect_action", "cards": cards, "task": next_task})
                    else:
                        logger.debug("Too much moves in the game stage.")
                        self.error("You have no more moves in that stage.")

                elif message_type == MessageType.SURRENDER_MOVE:
                    self.winner = "student" if game_user.conflict_side == "teacher" else "teacher"
                    await self.cleanup()
                else:
                    await self.error("Wrong message type in the current game stage.")
                    logger.debug("Wrong message type")
                
            elif game_stage == GameStage.FIRST_CLASH or game_stage == GameStage.SECOND_CLASH:
                
                if message_type == MessageType.CLASH_ACTION_MOVE:

                    if game.next_move_type != "action":
                        await self.error("Wrong message type. It is time for reaction.")
                        return

                    if game.next_move_player != game_user.conflict_side:
                        await self.error("Not your turn.")
                        return
                    
                    if (game_stage == GameStage.FIRST_CLASH and self.moves_table[0][GameStage.FIRST_CLASH][0] > 0) \
                        or (game_stage == GameStage.SECOND_CLASH and self.moves_table[0][GameStage.SECOND_CLASH][0] > 0):

                        action_card_id = data.get("action_card")

                        # action_card_exist = await check_action_card_exist(action_card_id)
                        # if not action_card_exist:
                        #     await self.error("Provided card doesnt exist")
                        #     return
                        
                        # game_user = await get_game_user_by_id(self.game_user_id)
                        # action_card_connected = await check_action_card_connected(game_user, action_card_id)
                        # if not action_card_connected:
                        #     await self.error("You do not own this card")
                        #     return

                        # succesful_removal = await remove_action_card_connection(game_user, action_card_id)
                        # if not succesful_removal:
                        #     logger.error("Couldnt delete action cards from user")
                        #     self.error("Server error occured")

                        self.moves_table[0][game_stage][0] -= 1
                        flag = await update_game_turn(self.game_id)
                        if not flag:
                            logger.error("Couldnt update game turn")
                            await self.send_message_to_group("Server error occured", "error")

                        await self.send_message_to_opponent({"action_card":action_card_id}, "opponent_move")
                        
                    else:
                        logger.debug("Too much moves in the stage.")
                        await self.error("You have no more moves in that stage.")

                elif message_type == MessageType.CLASH_REACTION_MOVE:

                    if game.next_move_player != game_user.conflict_side:
                        await self.error("Not your turn.")
                        return
                    
                    if game.next_move_type != "reaction":
                        await self.error("Wrong message type. It is time for action.")
                        logger.debug("Wrong message type.")
                        return

                    if (game_stage == GameStage.FIRST_CLASH and self.moves_table[0][GameStage.FIRST_CLASH][1] > 0) \
                        or (game_stage == GameStage.SECOND_CLASH and self.moves_table[0][GameStage.SECOND_CLASH][1] > 0):

                        reaction_cards_ids = data.get("reaction_cards")
                        
                        # all_reaction_cards_exist = await check_reaction_cards_exist(reaction_cards_ids)
                        # if not all_reaction_cards_exist:
                        #     await self.error("Some of provided cards dont exist")
                        #     return
                        
                        # game_user = await get_game_user_by_id(self.game_user_id)
                        # all_reaction_cards_connected = await check_reaction_cards_connected(game_user, reaction_cards_ids)
                        # if not all_reaction_cards_connected:
                        #     await self.error("You do not own all of used cards")
                        #     return

                        # # TODO calculate changes in morale

                        # succesful_removal = await remove_reaction_cards_connection(game_user, reaction_cards_ids)
                        # if not succesful_removal:
                        #     logger.error("Couldnt delete reaction cards from user")
                        #     self.error("Server error occured")

                        student_new_morale = None
                        teacher_new_morale = None

                        self.moves_table[0][game_stage][1] -= 1
                        flag = await update_game_turn(self.game_id)
                        if not flag:
                            logger.error("Couldnt update game turn.")
                            await self.send_message_to_group("Server error occured.","error")

                        await self.send_message_to_opponent({"reaction_cards": reaction_cards_ids}, "opponent_move")
                        await self.send_message_to_group({
                            "student_new_morale": student_new_morale,
                            "teacher_new_morale": teacher_new_morale,
                            }, "clash_result")

                    else:
                        self.error("You have no more moves in that stage.")
                        logger.debug("No more moves in the stage.")
                    
                elif message_type == MessageType.SURRENDER_MOVE:
                    self.winner = "student" if game_user.conflict_side == "teacher" else "teacher"
                    await self.cleanup()
                else:
                    await self.error("Wrong message type in the current game stage.")
            else:
                if self.winner is None:
                    logger.error("Neither game stage is taking place.")
                    await self.send_message_to_group("Server error occured", "error")
                else:
                    await self.send_message_to_group(self.winner, "game_end")
                    logger.debug("Game has ended.")
        else:
            await self.error("The game hasn't started yet.")

    async def send_message_to_group(self, data, event): # sends messages to both players' clients
        await self.channel_layer.group_send(
            f"game_{self.game_id}",
            {
                'type': event,
                'data': data,
            }
        )

    async def send_message_to_opponent(self, data, event):
        await self.channel_layer.send(
            self.opponent_channel_name,
            {
                'type': event,
                'data': data,
            }
        )

    
    #
    # Functions managing messages from opponent and group, each one handles one type that is the fucntion's name
    #
        
    async def opponent_move(self, data):
        data = data['data']
        if data.get("action_card") is not None:
            await self.send_json({
                'type': "opponent_move",
                'action_card':  data['action_card']
            })
        elif data.get("reaction_cards") is not None:
            await self.send_json({
                'type': "opponent_move",
                'reaction_cards':  data["reaction_cards"]
            })
        else:
            logger.debug("Wrong type of move.")
            pass

    async def clash_result(self, data):
        data = data["data"]
        student_new_morale = data["student_new_morale"]
        teacher_new_morale = data["teacher_new_morale"]

        await self.send_json({
            'type': "clash_result",
            'student_new_morale': student_new_morale,
            'teacher_new_morale': teacher_new_morale
        })

    async def collect_action(self, data):
        data = data['data']
        task = data['task']
        await self.send_json({
            'type': "collect_action",
            'task': task
        })

    async def game_start(self, data):
        game_data = data['data']

        await self.send_json({
            'type': "game_start",
            'next_move': game_data.get("next_move_player"),
            'start_datetime': game_data.get("start_datetime")
        })

    async def game_end(self, data):
        winner = data['data']
        try:
            await self.send_json({
                'type': "game_end",
                'winner': winner
            })
        except Disconnected:
            logger.warning("Tried to sent through closed socket.")
            
        await self.close()

    async def game_creation(self, data):
        data = data['data']
        self.game_id = data["game_id"]
        self.opponent_channel_name = data["channel_name"]

    async def error(self, info):
        await self.send_json({
            'type': "error",
            'info': info
        })