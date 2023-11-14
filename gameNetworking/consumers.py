from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.exceptions import StopConsumer
from autobahn.exception import Disconnected

from .models import *
from .middlewares import *
from .queries import *
from .serializers import GameSerializer

class GameConsumer(AsyncJsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_id = None
        self.game_user_id = None
        self.winner = None
        self.closure_from_user_side = True

    async def connect(self):

        token = self.scope.get("token")
        access = bool(token)
        conflict_side = self.scope["url_route"]["kwargs"]["conflict_side"]

        # check if user is using valid token
        if not access:
            await self.close()

        # check if user has chosen a playable conflict side
        if conflict_side != "teacher" and conflict_side != "student":
            await self.close()
        

        game_user = await create_game_user(token, conflict_side, self.channel_name)
        self.game_user_id = game_user.id

        number_of_teachers_waiting = await get_number_of_waiting_game_users("teacher")
        number_of_students_waiting = await get_number_of_waiting_game_users("student")

        if number_of_teachers_waiting > 0 and number_of_students_waiting > 0:

            # Initializing game
            longest_waiting_teacher_player = await get_longest_waiting_game_user("teacher")
            longest_waiting_student_player = await get_longest_waiting_game_user("student")

            longest_waiting_teacher_player.in_game = True
            longest_waiting_student_player.in_game = True

            await delete_game_authentication_token(longest_waiting_teacher_player)
            await delete_game_authentication_token(longest_waiting_student_player)

            game = await create_game(longest_waiting_teacher_player, longest_waiting_student_player)
            self.game_id = game.id
            game_serialized = GameSerializer(game).data

            await self.channel_layer.group_add(f"game_{self.game_id}", longest_waiting_teacher_player.channel_name)
            await self.channel_layer.group_add(f"game_{self.game_id}", longest_waiting_student_player.channel_name)

            await self.send_message_to_opponent(str(self.game_id), "game_id_creation")
            await self.send_message_to_group(game_serialized, "game_start")

        await self.accept()

    async def cleanup(self):
        self.closure_from_user_side = False
        winner = self.winner
        await self.send_message_to_group(winner,"game_end")
        await self.perform_cleanup()

    async def perform_cleanup(self):

        if self.game_id is None:
            flag = await delete_game_user(self.game_user_id)
            if not flag:
                #TODO logging
                pass
        else:
            game = await get_game(self.game_id)
            if game is not None:

                teacher_player, student_player = await get_both_players_from_game(self.game_id)
                flag1, flag2, flag3 = None, None, None

                if student_player is not None:
                    flag1 = await delete_game_user(student_player.id)
                if teacher_player is not None:
                    flag2 = await delete_game_user(teacher_player.id)
                flag3 = await delete_game(self.game_id)

    async def disconnect(self, *args):

        if self.closure_from_user_side:  # disconnnect from user side
            if self.game_id is not None:
                await self.send_message_to_opponent(None,"game_end")
            await self.perform_cleanup()
        if self.game_id is not None:
            await self.channel_layer.group_discard(f"game_{self.game_id}", self.channel_name)
            
        raise StopConsumer()

    async def receive_json(self, content):

        if self.game_id is not None:

            message_type = content.get('type')
            move = content.get("move")

            game = await get_game(self.game_id)
            game_user = await get_game_user_by_id(self.game_user_id)

            if game.next_move == game_user.conflict_side:
                if message_type == 'made_move':
                    await self.send_message_to_opponent(move,'made_move')
                    game = await update_game(self.game_id, game_user.conflict_side)
                elif message_type == 'win_move':
                    self.winner = game_user.conflict_side
                    await self.cleanup()
                else:
                    await self.error("Wrong message type.")
            else:
                await self.error("Not your turn.")
        else:
                await self.error("The game hasnt started yet.")

    async def send_message_to_group(self, data, event_type):
        await self.channel_layer.group_send(
            f"game_{self.game_id}",
            {
                'type': event_type,
                'data': data,
            }
        )

    async def send_message_to_opponent(self, data, event_type):
        
        user = await get_game_user_by_id(self.game_user_id)
        teacher_player, student_player = await get_both_players_from_game(self.game_id)
        opponent_channel = teacher_player.channel_name if user.conflict_side == "student" else student_player.channel_name 

        await self.channel_layer.send(
            opponent_channel,
            {
                'type': event_type,
                'data': data,
            }
        )

    async def made_move(self, event):
        move = event['data']

        await self.send_json({
            'event': "made_move",
            'move': move
        })

    async def game_start(self, event):
        game_data = event['data']

        await self.send_json({
            'event': "game_start",
            'data':game_data
        })

    async def game_end(self, event):
        winner = event['data']

        try:
            await self.send_json({
                'event': "game_end",
                'winner': winner
            })
        except Disconnected:
            print("Tried to sent through closed protocol.")
            
        await self.close()

    async def game_id_creation(self, event):
        game_id = event['data']
        self.game_id = game_id

    async def error(self, info):
        await self.send_json({
            'event': "made_error",
            'info': info
        })