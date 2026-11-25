"""
Production AI Agent — Part 6 Final Project (bản khung)

Hoàn thành các TODO để đạt đủ 12 tiêu chí trong README.md, rồi kiểm tra:
    python check_production_ready.py

Bản khung này chạy được (uvicorn app.main:app) nhưng chưa đạt tiêu chí nào.
"""
import json
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.auth import verify_api_key
from app.config import settings
from app.cost_guard import check_budget, record_cost
from app.rate_limiter import check_rate_limit
from app.redis_client import redis_healthy
from utils.mock_llm import ask as llm_ask

# TODO (tiêu chí 10 — Structured logging):
#   Mỗi dòng log của app phải là 1 JSON object hợp lệ, vd
#   {"ts": "...", "lvl": "INFO", "event": "request", "path": "/ask", "status": 200, "ms": 12.3}
#   Gợi ý: tự viết logging.Formatter dùng json.dumps.
class JSONFormatter(logging.Formatter):
    """Định dạng mỗi dòng log thành một JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "lvl": record.levelname,
            "event": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

logger = logging.getLogger("agent")
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(handler)
logger.propagate = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting")

    yield

    logger.info("Application shutting down")


app = FastAPI(
    title="Production AI Agent",
    lifespan=lifespan,
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


# TODO (tiêu chí 4): GET /health — liveness: luôn trả 200 khi process còn chạy
#                    (kể cả khi Redis chưa kết nối được)
# TODO (tiêu chí 5): GET /ready  — readiness: 200 khi sẵn sàng, 503 khi Redis không kết nối được

@app.get("/health")
def health():
    """Liveness: process còn chạy thì trả HTTP 200."""

    return {
        "status": "ok",
        "environment": settings.environment,
    }
@app.get("/ready")
def ready():
    """Readiness: chỉ sẵn sàng khi Redis kết nối được."""

    if not redis_healthy():
        return JSONResponse(
            status_code=503,
            content={
                "ready": False,
                "redis": "unavailable",
            },
        )

    return {
        "ready": True,
        "redis": "connected",
    }

@app.post("/ask")
def ask(body: AskRequest, api_key: str = Depends(verify_api_key)):
    # TODO (tiêu chí 6): bắt buộc header X-API-Key → thêm Depends(verify_api_key)
    # TODO (tiêu chí 7): check_rate_limit(...) → 429 khi vượt giới hạn
    # TODO (tiêu chí 8): check_budget() trước khi gọi LLM, record_cost(...) sau khi gọi → 402 khi hết budget
    start_time = time.perf_counter()
    try:
        # 1. Rate limiting
        check_rate_limit(api_key)
        # 2. Kiểm tra ngân sách trước khi gọi LLM
        check_budget()
        # 3. Gọi LLM
        answer = llm_ask(body.question)
        # 4. Ước lượng token cho mock LLM.
        # Khi dùng LLM thật, thay bằng usage.input_tokens
        # và usage.output_tokens từ API response.
        input_tokens = max(1, len(body.question) // 4)
        output_tokens = max(1, len(str(answer)) // 4)
        # 5. Ghi nhận chi phí
        cost = record_cost(input_tokens, output_tokens)
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            json.dumps(
                {
                    "event": "request",
                    "path": "/ask",
                    "status": 200,
                    "ms": elapsed_ms,
                },
                ensure_ascii=False,
            )
        )
        return {"question": body.question,"answer": answer,"estimated_cost_usd": cost}

    except HTTPException as exc:
        elapsed_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.warning(
            json.dumps(
                {
                    "event": "request",
                    "path": "/ask",
                    "status": exc.status_code,
                    "ms": elapsed_ms,
                },
                ensure_ascii=False,
            )
        )
        raise

    except Exception:
        logger.exception("Unexpected error while processing request")
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )

# TODO (tiêu chí 11 — Graceful shutdown):
#   Khi nhận SIGTERM: ngừng nhận request mới, xử lý xong request đang chạy rồi thoát (exit code 0).
#   Gợi ý: dùng lifespan của FastAPI để dọn dẹp. Nếu tự đăng ký signal handler cho SIGTERM thì
#   phải gọi lại handler cũ của uvicorn, nếu không process sẽ không bao giờ tắt.
@app.get("/test-slow")
def test_slow():
    time.sleep(5)
    return {"status": "completed"}