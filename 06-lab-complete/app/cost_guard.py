"""
Cost guard (tiêu chí 8).

Yêu cầu:
  • Cộng dồn chi phí LLM (tính theo token) vào Redis
  • Tổng chi phí vượt DAILY_BUDGET_USD (hoặc MONTHLY_BUDGET_USD) → HTTP 402
"""
from datetime import datetime, timezone

from fastapi import HTTPException

from app.config import settings
from app.redis_client import r

# Giá USD / 1K tokens (tham khảo gpt-4o-mini)
PRICE_INPUT_PER_1K = 0.00015
PRICE_OUTPUT_PER_1K = 0.0006

def _budget_key() -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"cost:{today}"

def check_budget() -> None:
    """Gọi TRƯỚC khi gọi LLM. Hết budget → raise HTTPException(status_code=402)."""
    # raise NotImplementedError("TODO: check_budget")
    try:
        current_cost = float(r.get(_budget_key()) or 0)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Cost guard unavailable",
        ) from exc

    if current_cost >= settings.daily_budget_usd:
        raise HTTPException(
            status_code=402,
            detail="Daily budget exceeded",
        )


def record_cost(input_tokens: int, output_tokens: int) -> float:
    """Gọi SAU khi gọi LLM. Cộng chi phí của request vào tổng, trả về chi phí request."""
    # raise NotImplementedError("TODO: record_cost")
    input_tokens = max(0, input_tokens)
    output_tokens = max(0, output_tokens)

    cost = (
        input_tokens / 1000 * PRICE_INPUT_PER_1K
        + output_tokens / 1000 * PRICE_OUTPUT_PER_1K
    )

    key = _budget_key()

    try:
        pipe = r.pipeline()
        pipe.incrbyfloat(key, cost)
        pipe.expire(key, 2 * 24 * 60 * 60)
        pipe.execute()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Unable to record request cost",
        ) from exc

    return cost