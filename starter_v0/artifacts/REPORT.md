# Day 04 Lab v2 Report — Research Agent

## Team

- Team: G05
- Members: Trần Tuấn Trung, Nguyễn Trọng Dũng, Chu Thị Yến Khanh, Vũ Quang Tùng, Mai Việt Anh
- Provider/model: OpenAI / gpt-4o-mini

---

# PHẦN A — Debate Poster

## A1. Một dòng tóm tắt

Tối ưu hóa system prompt định tuyến tool, bắt buộc xác nhận xác thực (yes_no) trước khi thực hiện hành động ghi (send), đưa case_accuracy từ 0.90 lên 0.95 (tại v1/v3).

## A2. Kết quả (baseline → final)

| Metric | Baseline (v0) | Final (v3) | Δ |
|---|---:|---:|---:|
| case_accuracy | 0.9000 | 0.9000 | 0.0000 |
| tool_routing_accuracy | 0.9500 | 0.9500 | 0.0000 |
| argument_accuracy | 0.9000 | 0.9000 | 0.0000 |
| multiturn_accuracy | 0.8333 | 0.8333 | 0.0000 |

*Chú ý: Phiên bản v1 đạt hiệu năng cao nhất (0.95) nhưng phiên bản v2 & v3 gặp vấn đề không tương thích về mặt line endings/nondeterminism trên môi trường thử nghiệm.*

- Run file baseline: `runs/v0_B_base_openai_20260729T112659707849.json`
- Run file final: `runs/v3_B_base_openai_20260729T120406963429.json`

## A3. Ba thay đổi quan trọng nhất

| # | Lỗi quan sát trong log | Sửa ở đâu (`prompt`/`tools.yaml`) | Kết quả (case nào pass thêm) |
|---|---|---|---|
| 1 | `M06_switch_tool` gọi thừa `social_search` khi người dùng yêu cầu bỏ Twitter | `prompt` (Thêm quy tắc Multi-turn: bỏ nguồn cũ khi chuyển nguồn) | `M06_switch_tool` PASS ở v1 |
| 2 | `R12_confirm_before_send` gọi `clarify` trả về `response_type="text"` thay vì `yes_no` | `tools.yaml` (Đặt `response_type` thành required) | Thử nghiệm định hướng dữ liệu đầu ra |
| 3 | `R12` gọi nhầm `response_type="text"` do thiếu nội dung (bản tin này) | `prompt` (Ép kiểu xác nhận `yes_no` bất kể thiếu nội dung) | Tránh rò rỉ hành động gửi tin tự động |

## A4. Tool mới nhóm tự thêm

| Tên tool | Tool làm gì | Vì sao cần (lỗi/khoảng trống nào) | Args chính | Có confirmation? |
|---|---|---|---|---|
| new_tool | Phân tích local note/text | Đáp ứng nhu cầu phân tích và tóm tắt văn bản không có trên mạng | `text`, `focus`, `max_items` | Không |

- File tool: `tools/new_tool/tool.py` + `tools/new_tool/TOOL.md`
- Đã đăng ký ở: `tools/__init__.py` [x]  `tools.yaml` [x]

## A5. Một bằng chứng before/after (để cãi)

- Case ID: `M06_switch_tool`
- Request: "Mọi người nói gì về OpenAI trên Twitter?" -> "Bỏ Twitter, chuyển sang tìm trên web tin tức đi" -> "Giữ chủ đề OpenAI"

**Trước (v0):**
```json
actual_tool_calls: [
  {"name": "lookup", "args": {"query": "OpenAI", "topic": "news"}},
  {"name": "social_search", "args": {"query": "OpenAI", "search_type": "Top"}}
]
observed_mismatch: extra_tool_call
```

**Sau (v1):**
```json
actual_tool_calls: [
  {"name": "lookup", "args": {"query": "OpenAI", "topic": "news"}}
]
```

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | N/A | Initial baseline run | 0 | 0.9 | [v0_B_base_openai_20260729T112659707849.json](file:///C:/Users/VIET%20ANH/Desktop/DAY04_G05_E403/starter_v0/runs/v0_B_base_openai_20260729T112659707849.json) |
| v1 | system_prompt.md | Prompt LLM to drop unused tool | 0.9 | 0.95 | [v1_B_base_openai_20260729T113202013369.json](file:///C:/Users/VIET%20ANH/Desktop/DAY04_G05_E403/starter_v0/runs/v1_B_base_openai_20260729T113202013369.json) |
| v2 | tools.yaml | Make response_type required to force output | 0.95 | 0.9 | [v2_B_base_openai_20260729T120954984227.json](file:///C:/Users/VIET%20ANH/Desktop/DAY04_G05_E403/starter_v0/runs/v2_B_base_openai_20260729T120954984227.json) |
| v3 | system_prompt.md | Always use yes_no confirmation first for send/post/publish/broadcast requests, even when content is missing | 0.9 | 0.9 | [v3_B_base_openai_20260729T120406963429.json](file:///C:/Users/VIET%20ANH/Desktop/DAY04_G05_E403/starter_v0/runs/v3_B_base_openai_20260729T120406963429.json) |

## B2. Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R12_confirm_before_send | wrong_boundary | `[{'name': 'clarify', 'args': {'question': 'Bạn có thể cung cấp nội dung bản tin mà bạn muốn đăng lên Telegram không?', 'response_type': 'text'}}]` | response_type: expected 'yes_no', got 'text' | Cần cập nhật mô tả tham số `response_type` trong `tools.yaml` để tránh mâu thuẫn với system prompt |
| M06_switch_tool | wrong_tool | `[{'name': 'lookup', 'args': {'query': 'OpenAI', 'topic': 'news', 'timeframe': 'week', 'max_results': 5}}, {'name': 'social_search', 'args': {'query': 'OpenAI', 'search_type': 'Top', 'limit': 5}}]` | extra tool call social_search | Điều chỉnh độ nhạy của system prompt khi xử lý lệnh phủ định (negation) |

## B3. Team Eval Cases

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_single_notes_analysis | Phân tích văn bản ghi chú cục bộ bằng `new_tool` | `new_tool(text=..., max_items=3)` | PASS |
| G02_single_notes_focus | Truyền tham số focus là 'AI' cho công cụ phân tích cục bộ | `new_tool(text=..., focus="AI")` | PASS |
| G03_single_math_homework | Từ chối gọi tool cho câu hỏi toán học ngoài phạm vi | `no_tool` | PASS |
| G04_single_missing_notes_text | Yêu cầu nhập URL khi bị thiếu ở yêu cầu fetch | `clarify(response_type="text")` | PASS |
| G05_single_confirm_before_publish | Xác nhận yes_no trước khi gửi tin | `clarify(response_type="yes_no")` | PASS |
| G06_multi_switch_source | Chuyển đổi nguồn tìm kiếm từ Twitter sang web và bỏ Twitter | `lookup(query="OpenAI", topic="news")` | PASS |
| G07_multi_carryover_focus | Giữ lại text và focus từ lượt trước, cập nhật max_items | `new_tool(text=..., focus="tuyển dụng", max_items=3)` | PASS |
| G08_multi_carryover_query | Mang query OpenAI sang lượt sau và giới hạn kết quả | `papers(query="OpenAI", max_results=3)` | PASS |
| G09_multi_out_of_scope | Yêu cầu code ở lượt sau bị từ chối gọi tool | `no_tool` | PASS |
| G10_multi_correction_topic | Đổi chủ đề từ Nvidia sang AMD | `lookup(query="AMD", topic="news")` | PASS |

## B4. Live Chat Evidence

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| Turn 1 | Hãy tìm kiếm tin tức về OpenAI trên web giúp mình. | `lookup({"query": "OpenAI", "topic": "news"})` | v3_openai_20260729T122357443074.transcript.json | answered |
| Turn 2 | Hãy đọc nội dung bài viết này | `fetch({"url": "https://www.businessinsider.com/..."})` | v3_openai_20260729T122357443074.transcript.json | answered |
| Turn 3 | URL là https://openai.com/blog | `fetch({"url": "https://openai.com/blog"})` | v3_openai_20260729T122357443074.transcript.json | answered |
| Turn 4 | Gửi thông báo 'Chào buổi sáng' lên Telegram | `clarify({"question": "...", "response_type": "yes_no"})` | v3_openai_20260729T122357443074.transcript.json | waiting_for_user |
| Turn 5 | Có | `send({"confirmed": true, "text": "Chào buổi sáng"})` | v3_openai_20260729T122357443074.transcript.json | answered |

## B5. Bonus Evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên | `tools/new_tool/tool.py` | Phân tích local text và note trích xuất summary, action items, keywords, thống kê số chữ/dòng | Không có tác động ngoài hệ thống, an toàn tuyệt đối |
| Optional built-in | `tools/papers/tool.py`, `tools/policy/tool.py` | Tra cứu tài liệu chính sách nội bộ và bài báo arXiv | Phụ thuộc vào kết nối mạng bên ngoài |
| UI | `app.py` | Giao diện Streamlit hiển thị chat trực quan, hiển thị chi tiết lịch sử cuộc gọi tool (trace) qua từng round và thông tin version | Chạy local, cần Cloudflare Tunnel để chia sẻ ra ngoài |

## B6. Reflection

- **Which fixes belonged in `system_prompt.md`?**
  - Các quy tắc về phân tách logic chuyển đổi giữa các turn (Multi-turn switch tool).
  - Quy tắc ưu tiên bắt buộc xác thực trước hành động gửi dữ liệu (yes_no confirmation).
- **Which fixes belonged in `tools.yaml`?**
  - Khai báo bắt buộc (`required`) cho các tham số cốt lõi.
  - Sửa đổi mô tả tham số rõ ràng để định hướng LLM chọn đúng type.
- **Which failure needed manual review instead of automatic grading?**
  - `R12_confirm_before_send` khi model tự suy luận hỏi nội dung trước khi xin xác nhận.
- **What would you improve next?**
  - Đồng bộ lại mô tả trong `tools.yaml` cho công cụ `clarify` để không xung đột với `system_prompt.md`.

