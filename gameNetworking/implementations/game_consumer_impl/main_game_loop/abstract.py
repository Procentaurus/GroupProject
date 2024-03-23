from abc import ABC, abstractmethod


class StageHandler(ABC):

    def __init__(self, consumer, game, message_type, data):
        self._consumer = consumer
        self._game = game
        self._message_type = message_type
        self._data = data

    @abstractmethod
    async def perform_stage(self):
        pass

class MoveHandler(ABC):

    def __init__(self, consumer):
        self._consumer = consumer

    @abstractmethod
    async def _verify_move(self):
        pass

    @abstractmethod
    async def _perform_move_mechanics(self):
        pass

    async def perform_move(self):
        if not await self._verify_move(): return
        await self._perform_move_mechanics()
