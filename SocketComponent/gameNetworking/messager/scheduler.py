import redis
import asyncio
from datetime import timedelta, datetime
from django.utils import timezone
from django.conf import settings
from importlib import import_module

from SocketComponent.loggers import get_server_logger, get_game_logger


redis_client = redis.StrictRedis(
    host=settings.REDIS_SCHEDULER_HOST,
    port=settings.REDIS_SCHEDULER_PORT,
    db=settings.REDIS_SCHEDULER_DB
)


########################### Players' states queues #############################
def delete_player_states_queue(game_id):
    queue_name = f'{game_id}_player_states'
    result = redis_client.delete(queue_name)
    logger = get_game_logger(game_id)
    if result == 1:
        logger.info(f"Player states queue '{queue_name}' has been"
                    " successfully deleted.")
    else:
        logger.warning(f"Player states queue '{queue_name}' has not been"
                    " deleted as it does not exist")

def update_game_user_state(game_id, game_user_id, state):
    redis_client.hset(f'{game_id}_player_states', game_user_id, state)
    logger = get_game_logger(game_id)
    logger.info(f"User({game_user_id})'s state has been updated: {state}")

def check_game_user_state(game_id, game_user_id):
    state = redis_client.hget(f'{game_id}_player_states', game_user_id)
    return state.decode('utf-8')


############################ Games' states queues ##############################
def update_game_state(game_id, state):
    redis_client.hset(settings.GAMES_STATES_QUEUE_NAME, game_id, state)
    logger = get_game_logger(game_id)
    logger.info(f"Game's state has been updated: {state}")

def check_game_state(game_id):
    state = redis_client.hget(settings.GAMES_STATES_QUEUE_NAME, game_id)
    return state.decode('utf-8')

def remove_game_state(game_id):
    redis_client.hdel(settings.GAMES_STATES_QUEUE_NAME, game_id)


logger = get_server_logger()


def add_delayed_task(task_name, delay_in_sec, func_path):
    task_time = datetime.now(timezone.utc) + timedelta(seconds=delay_in_sec)
    if not redis_client.zscore(
        settings.DELAYED_GAME_TASKS_SORTED_SET_NAME, task_name):
        with redis_client.pipeline() as pipe:
            pipe.zadd(
                settings.DELAYED_GAME_TASKS_SORTED_SET_NAME,
                {task_name: task_time.timestamp()}
            )
            pipe.hset(
                settings.TASK_CALLBACK_FUNCTIONS_QUEUE_NAME,
                task_name,
                func_path
            )
            pipe.execute()
    logger.info(f"Added delayed task({task_name})({delay_in_sec})")

def remove_delayed_task(task_name):
    with redis_client.pipeline() as pipe:
        pipe.zrem(settings.DELAYED_GAME_TASKS_SORTED_SET_NAME, task_name)
        pipe.hdel(settings.TASK_CALLBACK_FUNCTIONS_QUEUE_NAME, task_name)
        pipe.execute()
    if not redis_client.zscore(
        settings.DELAYED_GAME_TASKS_SORTED_SET_NAME, task_name):
        logger.info(f"Successfully removed delayed task({task_name})")

async def run_task(task_name):

    def get_func():
        module_name, func_name = func_path.decode().rsplit('.', 1)
        module = import_module(module_name)
        func = getattr(module, func_name)
        return func

    def get_id(task_name):
        _, user_id = task_name.rsplit('_', 1)
        return user_id

    func_path = redis_client.hget(
        settings.TASK_CALLBACK_FUNCTIONS_QUEUE_NAME,
        task_name
    )
    if func_path:
        func = get_func()
        id = get_id(task_name)
        try:
            await func(id)
            logger.info(f"Delayed task({task_name}) has been performed")
            return True
        except Exception as e:
            logger.error(f"Error executing task {task_name}: {e}")
    logger.error(f"Not found funcion to perform delayed task {task_name}")
    return False

async def check_tasks():
    while True:
        now = datetime.now(timezone.utc).timestamp()
        tasks = redis_client.zrangebyscore(
            settings.DELAYED_GAME_TASKS_SORTED_SET_NAME, 0, now
        )
        if tasks:
            for task in tasks:
                task_name = task.decode('utf-8')
                if redis_client.zrem(
                    settings.DELAYED_GAME_TASKS_SORTED_SET_NAME, task_name):
                    success = await run_task(task_name)
                    if success:
                        remove_delayed_task(task_name)
        else:
            await asyncio.sleep(0.1)

def get_all_game_tasks(first_player_id, second_player_id):

    def filter_tasks_by_players(tasks, first_player_id, second_player_id):
        ids = [first_player_id, second_player_id]
        filtered_tasks = {}
        for task_name, task_time in tasks:
            task_name = task_name.decode('utf-8')
            if any(task_name.endswith(id) for id in ids):
                filtered_tasks[task_name] = task_time
        return filtered_tasks

    def reformat_timestamp(task_time):
        task_time = datetime.fromtimestamp(task_time)
        return timezone.make_aware(task_time, timezone=timezone.utc)

    def calculate_time_difference(task_time):
        return (task_time - datetime.now(timezone.utc)).total_seconds()

    remaining_tasks = {}
    tasks = redis_client.zrange(
        settings.DELAYED_GAME_TASKS_SORTED_SET_NAME,
        0, -1, withscores=True)
    filtered_tasks = filter_tasks_by_players(tasks,
                                             first_player_id,
                                             second_player_id)
    for task_name, task_time in filtered_tasks.items():
        task_time = reformat_timestamp(task_time)
        remaining_time = calculate_time_difference(task_time)
        if remaining_time > 0:
            remaining_tasks[task_name] = round(remaining_time, 0)
    return remaining_tasks

def verify_task_exists(task_name):
    return redis_client.hexists(
        settings.TASK_CALLBACK_FUNCTIONS_QUEUE_NAME,
        task_name
    )

def start_task_checker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(check_tasks())
