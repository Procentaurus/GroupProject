import redis
import threading
import asyncio
from datetime import timedelta, datetime
from django.utils import timezone
from django.conf import settings
from importlib import import_module

redis_client = redis.StrictRedis(
    host=settings.REDIS_SCHEDULER_HOST,
    port=settings.REDIS_SCHEDULER_PORT,
    db=settings.REDIS_SCHEDULER_DB
)

def add_delayed_task(task_name, delay_in_sec, func_path):
    print(f"add_delayed_task, task_name={task_name}, delay={delay_in_sec}")
    task_time = datetime.now(timezone.utc) + timedelta(seconds=delay_in_sec)
    redis_client.zadd('tasks', {task_name: task_time.timestamp()})
    redis_client.hset('task_funcs', task_name, func_path)

def remove_delayed_task(task_name):
    print(f"remove_delayed_task, task_name={task_name}")
    redis_client.zrem('tasks', task_name)
    redis_client.hdel('task_funcs', task_name)

async def run_task(task_name):

    def get_func():
        module_name, func_name = func_path.decode().rsplit('.', 1)
        module = import_module(module_name)
        func = getattr(module, func_name)
        return func

    def get_id(task_name):
        _, user_id = task_name.rsplit('_', 1)
        return user_id

    func_path = redis_client.hget('task_funcs', task_name)
    if func_path:
        func = get_func()
        id = get_id(task_name)
        await func(id)

async def check_tasks():
    while True:
        now = datetime.now(timezone.utc).timestamp()
        tasks = redis_client.zrangebyscore('tasks', 0, now)
        if tasks:
            for task in tasks:
                await run_task(task.decode('utf-8'))
                remove_delayed_task(task.decode('utf-8'))
                await asyncio.sleep(0.005)
        await asyncio.sleep(0.1)

def get_all_game_tasks(first_player_id, second_player_id):
    remaining_tasks = {}
    tasks = redis_client.zrange('tasks', 0, -1, withscores=True)

    def filter_tasks_by_players():
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
        return (
            task_time - datetime.now(timezone.utc) - timedelta(hours=2)
        ).total_seconds()

    filtered_tasks = filter_tasks_by_players()
    for task_name, task_time in filtered_tasks.items():
        task_time = reformat_timestamp(task_time)
        remaining_time = calculate_time_difference(task_time)
        if remaining_time > 0:
            remaining_tasks[task_name] = round(remaining_time, 0)
    return remaining_tasks

def verify_task_exists(task_name):
    return redis_client.hexists('task_funcs', task_name)

def start_task_checker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(check_tasks())

threading.Thread(target=start_task_checker, daemon=True).start()
