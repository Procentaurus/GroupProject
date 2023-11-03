from channels.generic.websocket import AsyncJsonWebsocketConsumer
import enum

from .models import *

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
            self.game_user = await GameUser.objects.create(user_id=token.user_id, conflict_side=conflict_side, channel_name=self.channel_name)
            self.game_user.save()

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

            self.accept()

    async def disconnect(self):
        self.game_user.delete()
        self.close()

    # async def send_message_to_group(self, group_name, message_data, event_type):
    #     await self.channel_layer.group_send(
    #         group_name,
    #         {
    #             'type': event_type,
    #             'message': message_data,
    #         }
    #     )


    # async def receive(self):
    #     pass