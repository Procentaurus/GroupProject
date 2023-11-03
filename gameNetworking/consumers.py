from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json

from .models import *
from .middlewares import *
from .queries import *
from .serializers import GameSerializer

class GameConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):

        conflict_side = self.scope["url_route"]["kwargs"]["conflict_side"]

        token = self.scope.get("token")
        if token is not None:

            game_user = await create_game_user(token, conflict_side, self.channel_name)
            self.game_user_id = game_user.id

            number_of_teachers_waiting = await get_number_of_waiting_players("teacher")
            number_of_students_waiting = await get_number_of_waiting_players("student")

            if number_of_teachers_waiting > 0 and number_of_students_waiting > 0:

                longest_waiting_teacher_player = await get_longest_waiting_player("teacher")
                longest_waiting_student_player = await get_longest_waiting_player("student")

                game = await create_game(longest_waiting_teacher_player, longest_waiting_student_player)
                self.game_id = game.id

                await self.channel_layer.group_add(f"game_{self.game_id}", longest_waiting_teacher_player.channel_name)
                await self.channel_layer.group_add(f"game_{self.game_id}", longest_waiting_student_player.channel_name)

                longest_waiting_teacher_player.in_game = True
                longest_waiting_student_player.in_game = False

                game_serialized = GameSerializer(game).data

                await self.send_message_to_group(
                    f"game_{self.game_id}",
                    game_serialized,
                    "game_start")

            await self.accept()

    async def disconnect(self):

        self.send_message_to_group(f"game_{self.game_id}",None,'game_end')

        game = await Game.objects.get(id=self.game_id)
        game.teacher_player.delete()
        game.student_player.delete()
        game.delete()

        self.close()

    async def receive(self, text_data):

        message = json.loads(text_data)
        message_type = message.get('type')
        move = message.get("move")

        game = await Game.objects.get(id=self.game_id)
        game_user = await GameUser.objects.get(id=self.game_user_id)

        if self.game.next_move == game_user.conflict_side:
            if message_type == 'made_move':
                await self.send_message_to_group(f"game_{self.game_id}",move,'made_move')
                game.next_move = "teacher" if game_user.conflict_side == "student" else "student"
            else:
                await self.error("Wrong message type.")
        else:
            await self.error("Not your turn.")

    async def send_message_to_group(self, group_name, data, event_type):
        await self.channel_layer.group_send(
            group_name,
            {
                'type': event_type,
                'data': data,
            }
        )

    async def game_start(self, event):
        game_data = event['data']

        await self.send_json({
            'event': "game_start",
            'data':game_data
        })

    async def game_end(self, event):
        winner = event['data']

        await self.send_json({
            'event': "game_end",
            'winner':winner
        })

    async def error(self, info):
        await self.send_json({
            'event': "made_error",
            'info': info
        })