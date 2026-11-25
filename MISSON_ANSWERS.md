#  Delivery Checklist — Day 14 Lab Submission

> **Student Name:** Nguyễn Đức Trọng  
> **Student ID:** 2A202603367  
> **Date:** 25/11/2026

---

##  Submission Requirements

Submit a **GitHub repository** containing:

### 1. Mission Answers (40 points)

Create a file `MISSION_ANSWERS.md` with your answers to all exercises:

```markdown
# Day 14 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. API key hardcode trong code
2. Không có config management
3. Print thay vì proper logging
4. Không có health check endpoint
5. Port cố định — không đọc từ environment
...

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config | Hardcode | Env vars | Dễ thay đổi cấu hình giữa Development và Production, tránh lộ secrets trong source code. |
| Health check | Không có | Có `/health` | Giúp kiểm tra ứng dụng có đang hoạt động và sẵn sàng nhận request hay không. |
| Logging | print() | JSON | Dễ phân tích, tìm kiếm và giám sát lỗi trong môi trường production. |
| Shutdown | Đột ngột | Graceful | Cho phép hoàn thành request đang xử lý, giải phóng tài nguyên và đóng kết nối an toàn. |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: là Docker image có sẵn môi trường Python, được sử dụng làm nền tảng để xây dựng container.
2. Working directory: là thư mục làm việc mặc định bên trong container. Các lệnh tiếp theo như `COPY`, `RUN`, `CMD` sẽ sử dụng thư mục này làm vị trí mặc định.
...

### Exercise 2.3: Image size comparison
- Develop: [1660] MB
- Production: [240] MB
- Difference: [14.46]%

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://lucid-quietude-production-2f5b8f50.up.railway.app/
- Screenshot: https://github.com/trongnguyen104/K5-L3A-DAY14-NguyenDucTrong-2A202603367-Deployment-Benchmark-Observability/blob/main/03-cloud-deployment/railway/Screenshot_railway.png

## Part 4: API Security

### Exercise 4.1-4.3: Test results
| Exercise | Test | Expected HTTP Status |
|---|---|---|
| 4.1 | Không có API Key | 401 Unauthorized |
| 4.1 | API Key hợp lệ | 200 OK |
| 4.2 | JWT hợp lệ | 200 OK |
| 4.2 | Không có JWT | 401 Unauthorized |
| 4.3 | Trong giới hạn Rate Limit | 200 OK |
| 4.3 | Vượt giới hạn Rate Limit | 429 Too Many Requests |

### Exercise 4.4: Cost guard implementation
**Phương pháp tiếp cận (Approach):**
1. Định dạng khóa theo chu kỳ
2. Thao tác nguyên tử (Atomic Operations)
3. Tự động hết hạn (TTL)
4. Phân cấp bảo vệ (Tiered Defense)

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
[Your explanations and test results]

**1. Health Check (`/health`)**
- Gửi GET request đến `/health`.
- Kết quả: HTTP 200 OK.
- Trạng thái ứng dụng: `ok`.
- Memory usage: 89.6%.

**2. Readiness Check (`/ready`)**
- Gửi GET request đến `/ready`.
- Kết quả: HTTP 200 OK.
- Readiness: `true`.
- In-flight requests: 1.

**3. Agent Request (`/ask`)**
- Gửi POST request với câu hỏi `hello`.
- Kết quả: HTTP 200 OK.
- Agent nhận và xử lý câu hỏi thành công.

**4. Graceful Shutdown**
- Khởi chạy Uvicorn và xác định PID: `18512`.
- Gửi đồng thời 2 request đến `/ask` bằng Background Jobs.
- Sau 500 ms, nhấn `Ctrl + C` để dừng server.
- Uvicorn nhận tín hiệu SIGINT (signal 2) và thực hiện graceful shutdown.
- Cả 2 request đều hoàn thành với HTTP 200 OK trước khi server kết thúc.

**Kết quả kiểm thử:**

| Test | Kết quả | Trạng thái |
|---|---|---|
| Health Check | HTTP 200 | PASS |
| Readiness Check | HTTP 200 | PASS |
| Agent Request | HTTP 200 | PASS |
| Concurrent Requests | Cả 2 request thành công | PASS |
| Graceful Shutdown | Hoàn thành request trước khi dừng | PASS |

**Nhận xét:** Hệ thống xử lý thành công các request đang thực hiện trước khi tắt server, giúp hạn chế mất dữ liệu và gián đoạn dịch vụ. Có xuất hiện `CancelledError` trong quá trình shutdown, cần kiểm tra thêm để đảm bảo vòng đời ứng dụng kết thúc sạch.
---

### 2. Full Source Code - Lab 06 Complete (60 points)

Your final production-ready agent, built from the skeleton in `06-lab-complete/` (xem mục **Hợp đồng** trong [06-lab-complete/README.md](06-lab-complete/README.md)):

```
your-repo/
├── app/
│   ├── main.py              # Main application
│   ├── config.py            # Configuration
│   ├── auth.py              # Authentication
│   ├── rate_limiter.py      # Rate limiting (Redis)
│   ├── cost_guard.py        # Cost protection (Redis)
│   └── redis_client.py      # Redis connection + health
├── utils/
│   └── mock_llm.py          # Mock LLM (provided)
├── check_production_ready.py  # Grading script (provided, do not modify)
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Full stack
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── .dockerignore            # Docker ignore
├── railway.toml             # Railway config (or render.yaml)
└── README.md                # Setup instructions
```

**Requirements:**
-  **`python check_production_ready.py` báo `PASS 12/12`** (chạy đầy đủ, có Docker) — dán phần "📋 Checklist Deliverable" của output vào `MISSION_ANSWERS.md`
-  All code runs without errors
-  Multi-stage Dockerfile (image < 500 MB)
-  API key authentication
-  Rate limiting (10 req/min)
-  Cost guard ($10/month)
-  Health + readiness checks
-  Graceful shutdown
-  Stateless design (Redis)
-  No hardcoded secrets

---

### 3. Service Domain Link

Create a file `DEPLOYMENT.md` with your deployed service information:

````markdown
# Deployment Information

## Public URL
https://your-agent.railway.app

## Platform
Railway / Render / Cloud Run

## Test Commands

### Health Check
```bash
curl https://your-agent.railway.app/health
# Expected: {"status": "ok"}
```

### API Test (with authentication)
```bash
curl -X POST https://your-agent.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
```

## Environment Variables Set
- PORT
- REDIS_URL
- AGENT_API_KEY
- LOG_LEVEL

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
````

---

### 4. Benchmark & Observability Report — Part 7 (20 points)

Copy [06-lab-complete/benchmark-observability/BENCHMARK_REPORT_TEMPLATE.md](06-lab-complete/benchmark-observability/BENCHMARK_REPORT_TEMPLATE.md) thành `BENCHMARK_REPORT.md` và điền đầy đủ, kèm các file bằng chứng:

```
your-repo/
├── BENCHMARK_REPORT.md
├── reports/
│   ├── load_v2_c1.json ... load_v2_c100.json   # load_test.py --out
│   ├── eval_v1.json
│   ├── eval_v2.json
│   └── eval_v2_fixed.json                      # sau khi sửa knowledge base
├── benchmark-results/
│   ├── scale_1_stats.csv                       # Locust headless
│   └── scale_3_stats.csv
└── screenshots/
    ├── grafana-dashboard.png
    ├── jaeger-slow-trace.png
    ├── jaeger-error-trace.png
    └── prometheus-alert-firing.png
```

**Requirements:**
-  Load test ở 4 mức concurrency, có p50/p95/p99 và đối chiếu SLO
-  Eval v1 vs v2, sửa knowledge base để v2 đạt 100% không regression
-  Dashboard Grafana có tải, 1 trace chậm + 1 trace lỗi trong Jaeger
-  Ít nhất 2 alert firing, ghi lại thời gian phát hiện
-  Số liệu trong report khớp với file JSON/CSV

> **Cách tính điểm:** tổng thô 120 (40 + 60 + 20), quy đổi về thang 100.

---

##  Pre-Submission Checklist

- [ ] Repository is public (or instructor has access)
- [ ] `MISSION_ANSWERS.md` completed with all exercises
- [ ] `DEPLOYMENT.md` has working public URL
- [ ] All source code in `app/` directory
- [ ] `README.md` has clear setup instructions
- [ ] No `.env` file committed (only `.env.example`)
- [ ] No hardcoded secrets in code
- [ ] Public URL is accessible and working
- [ ] Screenshots included in `screenshots/` folder
- [ ] Repository has clear commit history
- [ ] `python check_production_ready.py` → `PASS 12/12`
- [ ] `BENCHMARK_REPORT.md` điền đủ, có `reports/`, `benchmark-results/` và screenshot Part 7

---

##  Self-Test

Before submitting, verify your deployment:

```bash
# 1. Health check
curl https://your-app.railway.app/health

# 2. Authentication required
curl https://your-app.railway.app/ask
# Should return 401

# 3. With API key works
curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
  -X POST -d '{"user_id":"test","question":"Hello"}'
# Should return 200

# 4. Rate limiting
for i in {1..15}; do 
  curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
    -X POST -d '{"user_id":"test","question":"test"}'; 
done
# Should eventually return 429

# 5. Part 7 — eval quality gate (agent v2 đang chạy ở local)
cd 06-lab-complete/benchmark-observability/develop
python eval/run_eval.py --min-accuracy 1.0
# Should print: Quality gate ... ✅ PASS
```

---

##  Submission

**Submit your GitHub repository URL:**

```
https://github.com/your-username/day14-agent-deployment
```

---

##  Quick Tips

1.  Test your public URL from a different device
2.  Make sure repository is public or instructor has access
3.  Include screenshots of working deployment
4.  Write clear commit messages
5.  Test all commands in DEPLOYMENT.md work
6.  No secrets in code or commit history

---

##  Need Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [CODE_LAB.md](CODE_LAB.md)
- Ask in office hours
- Post in discussion forum

---

**Good luck! **
