# Redis Setup for Vector Project

## Quick Start with Docker (Recommended)

1. **Start Redis with Docker Compose:**
   ```bash
   # From the project root directory
   docker-compose up -d redis
   ```

2. **Verify Redis is running:**
   ```bash
   docker-compose ps
   # Should show redis container as "Up"
   ```

3. **Test connection:**
   ```bash
   # Test Redis connection
   docker exec -it vector-redis redis-cli ping
   # Should return: PONG
   ```

4. **Optional: Start Redis UI (Redis Commander):**
   ```bash
   docker-compose up -d redis-commander
   # Access at: http://localhost:8081
   ```

## Alternative: Local Redis Installation

### Windows:
```bash
# Download from: https://github.com/tporadowski/redis/releases
# Or use Chocolatey:
choco install redis-64

# Start Redis:
redis-server
```

### macOS:
```bash
brew install redis
brew services start redis
```

### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

## Environment Configuration

1. **Copy environment template:**
   ```bash
   cd vector-backend
   cp .env.example .env
   ```

2. **Update .env file with your Redis URL:**
   ```
   REDIS_URL=redis://localhost:6379
   ```

## Install Python Dependencies

```bash
cd vector-backend
pip install -r requirements.txt
```

## Testing the Cache

```bash
# Test the cache implementation
cd vector-backend
python -c "
from cache_config import cache
print('Cache stats:', cache.get_stats())
"
```

## Cache Management Commands

```bash
# Connect to Redis CLI
redis-cli

# View all keys
KEYS *

# View cache statistics
INFO stats

# Clear all cache
FLUSHDB

# Monitor real-time commands
MONITOR
```

## Troubleshooting

### Connection Issues:
```bash
# Check if Redis is running
redis-cli ping

# Check Redis logs (Docker)
docker-compose logs redis

# Check port availability
netstat -an | grep 6379
```

### Cache Not Working:
- Verify Redis connection in Python:
  ```python
  from cache_config import cache
  print(cache.get_stats())
  ```
- Check if Redis service is running
- Verify REDIS_URL in .env file

### Performance Monitoring:
```bash
# Redis performance info
redis-cli info stats

# Memory usage
redis-cli info memory

# Connected clients
redis-cli info clients
```

## Production Considerations

1. **Set a password:**
   ```bash
   # In redis.conf
   requirepass your_secure_password

   # Update REDIS_URL
   REDIS_URL=redis://:your_secure_password@localhost:6379
   ```

2. **Backup configuration:**
   ```bash
   # Enable RDB snapshots
   save 900 1
   save 300 10
   save 60 10000
   ```

3. **Memory limits:**
   ```bash
   # Set max memory (in redis.conf)
   maxmemory 512mb
   maxmemory-policy allkeys-lru
   ```