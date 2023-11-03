from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json

from .models import *
from .serializers import *

class GameConsumer(AsyncJsonWebsocketConsumer):

    teachers_waiting = 0
    students_waiting = 0

    @classmethod
    async def get_number_of_teachers_waiting(cls, conflict_side):
        if conflict_side == "teacher":
            return cls.teachers_waiting
        elif conflict_side == "student":
            return cls.students_waiting
    
    @classmethod
    async def dec_number_of_users_waiting(cls, conflict_side):
        if conflict_side == "teacher":
            cls.teachers_waiting -= 1
        elif conflict_side == "student":
            cls.students_waiting -= 1

    @classmethod
    async def inc_number_of_users_waiting(cls, conflict_side):
        if conflict_side == "teacher":
            cls.teachers_waiting += 1
        elif conflict_side == "student":
            cls.students_waiting += 1

    async def connect(self):

        conflict_side = self.scope["url_route"]["kwargs"]["conflict_side"]

        # extracting and checking validity of token
        query_string = self.scope["token"].decode("utf-8")
        query_params = dict(q.split('=') for q in query_string.split('&'))
        token_string = query_params.get("token")
        token = await GameAuthenticationToken.objects.get(id=token_string)

        if token is not None:
            game_user = await GameUser.objects.create(user_id=token.user_id, conflict_side=conflict_side, channel_name=self.channel_name)
            game_user.save()
            self.game_user_id = game_user.id

            GameConsumer.inc_number_of_users_waiting(self.user.conflict_side)

            if GameConsumer.get_number_of_users_waiting("teacher") > 0 and GameConsumer.get_number_of_users_waiting("student") > 0:

                longest_waiting_teacher_player = await GameUser.objects.filter(conflict_side="teacher")[0]
                longest_waiting_student_player = await GameUser.objects.filter(conflict_side="student")[0]

                game = await Game.objects.create(teacher_player=longest_waiting_teacher_player, student_player=longest_waiting_student_player)
                self.game_id = game.id

                await self.channel_layer.group_add(f"game_{self.game_id}", longest_waiting_teacher_player.channel_name)
                await self.channel_layer.group_add(f"game_{self.game_id}", longest_waiting_student_player.channel_name)

                longest_waiting_teacher_player.in_game = True
                longest_waiting_student_player.in_game = False

                GameConsumer.dec_number_of_users_waiting("teacher")
                GameConsumer.dec_number_of_users_waiting("student")

                self.send_message_to_group(
                    f"game_{self.game_id}",
                    GameSerializer(game),
                    "game_start")

            self.accept()

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
                await self.error_message("Wrong message type.")
        else:
            await self.error_message("Not your turn.")

    async def send_message_to_group(self, group_name, data, event_type):
        await self.channel_layer.group_send(
            group_name,
            {
                'type': event_type,
                'data': data,
            }
        )

    async def game_start_message(self, event):
        game_data = event['game_start']

        await self.send_json({
            'event': "game_start",
            'data':game_data
        })

    async def game_end_message(self, event):
        winner = event['game_end']

        await self.send_json({
            'event': "game_end",
            'winner':winner
        })
        
    async def error_message(self, info):
        await self.send_json({
            'event': "made_error",
            'info': info
        })