import os
import redis
import json
import hashlib
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()

class RedisCache:
    def __init__(self):
        """Initialize Redis connection with configuration"""
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Establish Redis connection with error handling"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            self.redis_client.ping()
            print("✅ Redis connected successfully")
        except redis.ConnectionError as e:
            print(f"⚠️ Redis not available: {e}")
            print("ℹ️ App will continue without caching - performance may be slower")
            self.redis_client = None
        except Exception as e:
            print(f"⚠️ Redis connection error: {e}")
            print("ℹ️ App will continue without caching")
            self.redis_client = None
    
    def _generate_key(self, cache_type: str, identifier: str) -> str:
        """Generate consistent cache keys"""
        key_hash = hashlib.md5(identifier.encode()).hexdigest()
        return f"vector_app:{cache_type}:{key_hash}"
    
    def get(self, cache_type: str, identifier: str) -> Optional[Any]:
        """Get cached data"""
        if not self.redis_client:
            return None
            
        try:
            cache_key = self._generate_key(cache_type, identifier)
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except (redis.RedisError, json.JSONDecodeError) as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, cache_type: str, identifier: str, data: Any, ttl_seconds: int = 86400):
        """Set cached data with TTL"""
        if not self.redis_client:
            return False
            
        try:
            cache_key = self._generate_key(cache_type, identifier)
            serialized_data = json.dumps(data)
            self.redis_client.setex(cache_key, ttl_seconds, serialized_data)
            return True
        except (redis.RedisError, json.JSONEncodeError) as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, cache_type: str, identifier: str) -> bool:
        """Delete cached data"""
        if not self.redis_client:
            return False
            
        try:
            cache_key = self._generate_key(cache_type, identifier)
            return bool(self.redis_client.delete(cache_key))
        except redis.RedisError as e:
            print(f"Cache delete error: {e}")
            return False
    
    def clear_cache_type(self, cache_type: str) -> int:
        """Clear all cache entries of a specific type"""
        if not self.redis_client:
            return 0
            
        try:
            pattern = f"vector_app:{cache_type}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except redis.RedisError as e:
            print(f"Cache clear error: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.redis_client:
            return {"status": "disconnected"}
            
        try:
            info = self.redis_client.info()
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_keys": self.redis_client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0)
            }
        except redis.RedisError as e:
            return {"status": "error", "error": str(e)}

# Global cache instance
cache = RedisCache()

# Cache type constants
class CacheTypes:
    SEARCH_RESULTS = "search"
    VECTOR_STORE = "vector"
    SESSIONS = "session"
    FOLLOWUPS = "followup"