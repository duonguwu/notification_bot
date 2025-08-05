from motor.motor_asyncio import AsyncIOMotorClient
from umongo.frameworks import MotorAsyncIOInstance
from .settings import settings

import redis.asyncio as redis_mod

class Database:
    client: AsyncIOMotorClient = None
    redis: redis_mod.Redis = None

db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    mongo_db = db.client[settings.mongodb_database]
    db.instance = MotorAsyncIOInstance(mongo_db)
    print("Connected to MongoDB.")

def get_umongo_instance():
    if db.instance is None:
        raise RuntimeError("Instance not connected. Call connect_to_mongo() first.")
    return db.instance

async def close_mongo_connection():
    """Close database connection."""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB.")


async def connect_to_redis():
    """Create Redis connection."""
    db.redis = redis_mod.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True
    )
    print("Connected to Redis.")


async def close_redis_connection():
    """Close Redis connection."""
    if db.redis:
        await db.redis.close()
        print("Disconnected from Redis.")


def get_database():
    """Get database instance."""
    if db.client is None:
        raise RuntimeError("Database not connected. Call connect_to_mongo() first.")
    return db.client[settings.mongodb_database]


def get_redis():
    """Get Redis instance."""
    if db.redis is None:
        raise RuntimeError("Redis not connected. Call connect_to_redis() first.")
    return db.redis
