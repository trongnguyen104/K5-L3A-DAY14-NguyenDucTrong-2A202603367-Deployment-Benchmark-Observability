# Benchmark & Observability Report — Day 14

> Copy file này thành `BENCHMARK_REPORT.md` trong repo của bạn và điền đầy đủ.
> Mọi con số phải lấy từ report JSON / CSV / screenshot thật, không ước lượng.

**Họ tên**: Nguyễn Đức Trọng
**Mã sinh viên**: 2A202603367
**Ngày chạy**: 25/11/2026
**Môi trường:** Lenovo ideapad i5, Docker Desktop, 8GB RAM

---

## 1. SLO của agent

| SLI | SLO | Lý do chọn ngưỡng này |
|---|---|---|
| p95 latency `/ask` | < 2.000 ms | Giới hạn thời gian phản hồi của phần lớn request, đồng thời vẫn cho phép xử lý các request có độ trễ cao hơn bình thường. |
| Error rate `/ask` | < 1 % | Đảm bảo hệ thống hoạt động ổn định; tỷ lệ lỗi cao hơn ngưỡng này cần được điều tra. |
| Accuracy trên golden dataset | ≥ 100 % | Theo yêu cầu quality gate của bài lab: agent v2 sau khi sửa Knowledge Base phải đạt 100% và không gây regression. |

---

## 2. Benchmark hiệu năng (develop, `load_test.py`)

### 2.1 Concurrency vs latency (agent v2)

| Concurrency | RPS | p50 (ms) | p95 (ms) | p99 (ms) | Error rate | SLO |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 10 | | | | | | |
| 50 | | | | | | |
| 100 | | | | | | |

**Nhận xét:** RPS có tăng tuyến tính theo concurrency không? Vì sao?

...

### 2.2 Tail latency

| `MOCK_SLOW_RATE` | avg (ms) | p95 (ms) | p99 (ms) |
|---|---|---|---|
| 0 | | | |
| 0.03 (mặc định) | | | |
| 0.1 | | | |

**Nhận xét:** Chỉ số nào nhạy nhất với request chậm? Vì sao SLO không nên đặt theo average?

...

---

## 3. Benchmark chất lượng (develop, `eval/run_eval.py`)

| Chỉ số | Agent v1 | Agent v2 | Agent v2 (sau khi sửa KB) |
|---|---|---|---|
| Accuracy | | | |
| Avg tokens / câu | | | |
| Tổng cost (USD) | | | |
| Cost / câu đúng (USD) | | | |
| Quality gate | PASS / FAIL | PASS / FAIL | PASS / FAIL |

**Những câu v2 trả lời sai ban đầu và cách bạn sửa:**

| ID | Keyword bị thiếu | Bạn đã sửa gì |
|---|---|---|
| | | |

**Nhận xét về trade-off chất lượng / chi phí / latency giữa v1 và v2:**

...

---

## 4. Observability stack (production)

### 4.1 Screenshot

- [ ] Dashboard Grafana khi đang có tải (thấy rõ Golden Signals)
- [ ] Một trace chậm trong Jaeger (thấy span nào chiếm thời gian)
- [ ] Một trace lỗi trong Jaeger (có event `exception`)
- [ ] Trang Alerts của Prometheus với ít nhất 1 alert đang **firing**

### 4.2 Thí nghiệm "phá hệ thống"

| # | Thay đổi | Alert nào firing | Thời gian từ lúc đổi → firing | Panel nào phản ánh rõ nhất |
|---|---|---|---|---|
| A | `MOCK_ERROR_RATE=0.2` | | | |
| B | `MOCK_SLOW_RATE=0.3` | | | |
| C | `LLM_MODEL=mock-llm-large` | | | |
| D | `docker pause` 1 instance | | | |
| E | `AGENT_VERSION=v1` | | | |

**Thí nghiệm E không làm alert nào firing. Bạn sẽ phát hiện loại sự cố này trong production bằng cách nào?**

...

### 4.3 Debug bằng trace

Chọn 1 trace chậm nhất bạn tìm được:

- `trace_id`: ...
- Tổng thời gian: ... ms
- Span chiếm nhiều thời gian nhất: ... (... ms, ...%)
- Dòng log tương ứng (grep theo `trace_id`):

```json

```

---

## 5. Benchmark scaling (production, Locust headless, 100 users, 2 phút)

| Số instance | RPS | p50 (ms) | p95 (ms) | p99 (ms) | Failures |
|---|---|---|---|---|---|
| 1 | | | | | |
| 3 | | | | | |

**Giải thích kết quả:** Scale có cải thiện p95 không? Nút thắt nằm ở đâu?

...

---

## 6. Kết luận

- 3 điều bạn học được về benchmark & observability:
1. Benchmark cần được thực hiện ở nhiều mức concurrency và phải theo dõi đồng thời throughput, latency và error rate. Chỉ nhìn vào RPS không đủ để đánh giá hiệu năng hệ thống.
2. Tail latency, đặc biệt là p95 và p99, giúp phát hiện những request chậm mà average latency có thể che giấu.
3. Observability cần kết hợp metrics, logs và distributed traces. Metrics giúp phát hiện bất thường, logs cung cấp thông tin chi tiết và traces giúp xác định thành phần gây ra độ trễ hoặc lỗi.
- Nếu đưa agent này lên production thật, bạn sẽ thêm metric / alert nào nữa?
  - Metric latency p50, p95, p99 theo endpoint và theo agent_version.
  - Error rate phân loại theo HTTP status code và loại exception.
  - Request rate, số request đang xử lý và số request bị timeout.
  - CPU, memory usage và Redis connection/availability.
  - Token usage, chi phí LLM theo ngày/tháng và tỷ lệ request bị cost guard từ chối.
  - Metric chất lượng như accuracy, tỷ lệ câu trả lời không có căn cứ và tỷ lệ hallucination trên golden dataset.
  - Alert cho error rate tăng cao, p95 vượt SLO, Redis mất kết nối, chi phí vượt ngân sách và chất lượng model suy giảm.
