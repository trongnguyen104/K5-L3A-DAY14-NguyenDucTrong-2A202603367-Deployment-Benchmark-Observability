"""
Rate limiting (tiêu chí 7).

Yêu cầu:
  • Mỗi API key tối đa RATE_LIMIT_PER_MINUTE request trong 60 giây (sliding window)
  • Vượt giới hạn → HTTP 429, nên kèm header Retry-After
  • State lưu trong Redis để mọi worker / instance dùng chung và vẫn còn sau khi
    restart agent (script chấm sẽ restart agent để kiểm tra)
"""

import hashlib
import time

from fastapi import HTTPException

from app.config import settings
from app.redis_client import r


RATE_LIMIT_SCRIPT = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local max_requests = tonumber(ARGV[3])
local request_id = ARGV[4]

redis.call("ZREMRANGEBYSCORE", key, 0, now - window)

local count = redis.call("ZCARD", key)

if count >= max_requests then
    local oldest = redis.call("ZRANGE", key, 0, 0, "WITHSCORES")
    local retry_after = window

    if oldest[2] then
        retry_after = math.max(
            1,
            math.ceil(tonumber(oldest[2]) + window - now)
        )
    end

    return {0, retry_after}
end

redis.call("ZADD", key, now, request_id)
redis.call("EXPIRE", key, window + 5)

return {1, 0}
"""

def check_rate_limit(key: str) -> None:
    # TODO: gợi ý dùng Redis sorted set: ZREMRANGEBYSCORE → ZCARD → ZADD → EXPIRE
    # raise NotImplementedError("TODO: check_rate_limit")
    now = time.time()
    window = 60

    # Không lưu API key gốc trong Redis.
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    redis_key = f"rate_limit:{key_hash}"

    request_id = f"{now}:{time.time_ns()}"

    try:
        result = r.eval(
            RATE_LIMIT_SCRIPT,
            1,
            redis_key,
            now,
            window,
            settings.rate_limit_per_minute,
            request_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Rate limiter unavailable",
        ) from exc

    allowed, retry_after = int(result[0]), int(result[1])

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(retry_after)},
        )