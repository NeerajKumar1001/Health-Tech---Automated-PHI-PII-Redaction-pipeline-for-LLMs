import json
import redis
import logging

try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    print("✓ Connected to Redis Token Vault.")
except redis.ConnectionError:
    print("⚠️ Redis not connected. Ensure Redis server or container is running on port 6379.")
    redis_client = None

DEFAULT_TTL_SECONDS = 3600  # 1 hour HIPAA auto-expiry

def save_token_mapping(session_id: str, mapping: dict, ttl: int = DEFAULT_TTL_SECONDS) -> bool:
    """Stores token mapping in Redis as JSON with a TTL."""
    if not redis_client:
        return False
    try:
        redis_client.set(
            name=f"session:{session_id}",
            value=json.dumps(mapping),
            ex=ttl
        )
        return True
    except Exception as e:
        logging.error(f"Failed to write to Redis Vault: {e}")
        return False

def get_token_mapping(session_id: str) -> dict:
    """Retrieves stored token mapping dictionary from Redis for a given session."""
    if not redis_client:
        return {}
    try:
        data = redis_client.get(f"session:{session_id}")
        if data:
            return json.loads(data)
        return {}
    except Exception as e:
        logging.error(f"Failed to read from Redis Vault: {e}")
        return {}

def clear_session_vault(session_id: str) -> bool:
    """Purges token mapping from Redis upon transaction completion."""
    if not redis_client:
        return False
    try:
        redis_client.delete(f"session:{session_id}")
        return True
    except Exception as e:
        logging.error(f"Failed to clear Redis key: {e}")
        return False