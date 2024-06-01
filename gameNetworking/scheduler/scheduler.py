import time
import redis
import threading
import asyncio
from django.conf import settings
from importlib import import_module

redis_client = redis.StrictRedis(
    host=settings.REDIS_SCHEDULER_HOST,
    port=settings.REDIS_SCHEDULER_PORT,
    db=settings.REDIS_SCHEDULER_DB
)

def add_delayed_task(task_name, delay_in_sec, func_path):
    task_time = time.time() + delay_in_sec
    redis_client.zadd('tasks', {task_name: task_time})
    redis_client.hset('task_funcs', task_name, func_path)

def remove_task(task_name):
    redis_client.zrem('tasks', task_name)
    redis_client.hdel('task_funcs', task_name)
   
async def run_task(task_name):

    def get_func():
        module_name, func_name = func_path.decode().rsplit('.', 1)
        module = import_module(module_name)
        func = getattr(module, func_name)
        return func

    def get_user_id(task_name):
        _, user_id = task_name.rsplit('_', 1)
        return user_id

    func_path = redis_client.hget('task_funcs', task_name)
    if func_path:
        func = get_func()
        user_id = get_user_id(task_name)
        await func(user_id)
        redis_client.hdel('task_funcs', task_name)

async def check_tasks():
    while True:
        now = time.time()
        tasks = redis_client.zrangebyscore('tasks', 0, now)
        if tasks:
            for task in tasks:
                await run_task(task.decode('utf-8'))
                redis_client.zrem('tasks', task)
        await asyncio.sleep(1)

def start_task_checker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(check_tasks())

threading.Thread(target=start_task_checker, daemon=True).start()
