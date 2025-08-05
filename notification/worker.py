#!/usr/bin/env python3
"""
Taskiq Worker cho background task processing, tích hợp chuẩn với MongoDB, Redis.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from taskiq_redis import RedisStreamBroker, RedisAsyncResultBackend
from taskiq import TaskiqEvents

from config.settings import settings
from config.database import connect_to_mongo, close_mongo_connection

broker = RedisStreamBroker(url=settings.taskiq_broker_url)
broker = broker.with_result_backend(
    RedisAsyncResultBackend(redis_url=settings.taskiq_broker_url)
)

@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def worker_startup(state):
    await connect_to_mongo()
    print("[WORKER] MongoDB connected.")

@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def worker_shutdown(state):
    await close_mongo_connection()
    print("[WORKER] MongoDB disconnected.")

import tasks.import_customers
import tasks.send_notification
