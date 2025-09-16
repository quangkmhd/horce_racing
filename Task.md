# Chuỗi hành động — AI tạo script bình luận trận đua ngựa (step-by-step)

Dưới đây là **quy trình hành động** rõ ràng, có thể triển khai (real-time hoặc offline) cho hệ thống AI tự động tạo *script* bình luận trận đua ngựa. Mỗi bước nêu cả input, output và các quy tắc quan trọng.

---

## 1 — Tổng quan ngắn

Hệ thống xử lý video thành từng clip nhỏ → mô-đun detection & tracking trích xuất trạng thái → phát hiện sự kiện (event detection) → chuyển thành **structured event** → cập nhật memory (short/long) → tạo prompt cho LLM → LLM sinh script bình luận theo persona & style → post-process, đồng bộ thời gian, xuất file script (văn bản).

---

## 2 — Quy trình theo clip / theo trận (chi tiết từng bước)

1. **Ingest & Preprocessing**
    - Input: video.
    - Hành động: chuẩn hóa fps, extract timestamp.
2. **Segment video thành clips nhỏ**
    - Quy tắc: micro-chunk (0.5–3s) để realtime, macro-chunk (5–30s) cho phân tích sự kiện.
    - Output: danh sách clip có khoảng thời gian (start, end).
    - Name clips: 1_name_start_end, 2_name_start_end,…
3. **Video detection (horse, jockey, bib, áo)**
    - Model Qwen 2.5 vl: detector chuyên biệt: prompt (horse, jockey, bib_number, silks color, OCR cho bib number; màu áo hashing cho color id; xác định jockey).
    - 
    - Tính centroid(t), speed
    - Tính distance_between_adjacent, relative_speed.
    - 
    - Các loại event: bứt tốc (sudden accel), overtaking, collision, fall, finish_line_cross.
    - Cơ chế: rule-based thresholds + learned classifier trên các window (ví dụ: 2s–6s).
    - Output:text stucture time-series trạng thái cho mỗi horse. list of event_candidates với start_time, end_time, event_type, score.
4. **Short-term Memory update (ephemeral)**
    - Lưu last N events (ví dụ N=10) + latest positions để tránh lặp lại.
    - Dùng để giữ ngữ cảnh cho bình luận tiếp theo.
5. **Long-term Memory lookup/update**
    - Truy vấn DB: horse history, jockey form, tournament stats.
    - Cập nhật aggregated stats (lap times, wins, tendencies).
6. **Generate Commentary Prompt (prompt engineering)**
    - Chèn structured_event + memory snapshot + persona + tone + constraints (time budget, vocabulary).
    - Ví dụ template ở phần sau.
7. **LLM Generate — tạo script bình luận llama**
    - Input: prompt; Output: candidate scripts (n phiên bản nếu muốn chọn).
    - Kết hợp rules: độ dài tối đa, không lặp thông tin, avoid hallucination → nếu referencing stats, attach confidence.

---

## 4 — Memory design (short-term & long-term)

- **Short-term memory (ephemeral)**
    - Schema: `{recent_events: [...], current_positions: {...}, last_comment_timestamp}`
    - TTL: expire sau 30–120s hoặc sau race end.
    - Dùng để tránh lặp và giữ ngữ cảnh.
- **Long-term memory (persisted per race series / horse / jockey)**
    - Schema per horse: `{horse_id, name, stable, historical_wins, preferred_distance, last_5_races_stats}`
    - Cập nhật sau mỗi race; dùng cho color/drama lines trong bình luận.

Quy tắc sử dụng memory:

- Short-term overrides long-term for immediate facts (e.g., current position).
- Khi LLM cần historical fact, kèm theo confidence và source (DB / inference).

---

## 5 — Prompt template mẫu cho LLM

```
[Persona]: "Chuyên gia kịch tính" (voice: intense, brevity: medium)
[Context]: Race ID = {race_id}. Clip time = {clip_start} - {clip_end}.
[ShortTermMemory]: {recent_events_summary}
[LongTermMemory]: {horse_A: last3_wins, horse_B: poor_starts}
[StructuredEvent]: {structured_event_json}

Task: Viết script bình luận ngắn (30-40 words) và 1 câu reaction ngắn (5-8 words) dành cho khoảnh khắc này.
Constraints:
- Không lặp lại thông tin đã nói trong 15s trước.
- Nếu confidence < 0.6, bắt đầu bằng "Có vẻ..."
- Nếu event.replay_suggested == true, append "[REPLAY]" tag.
Output format (JSON):
{
 "text": "...",
 "reaction": "...",
 "start_time": ...,
 "end_time": ...,
 "persona": "...",
 "confidence": ...
}

```

---

## 6 — Persona & style examples (quick)

- **Chuyên gia phân tích**: nhiều dữ kiện, mô tả kỹ thuật.
- **Kịch tính**: câu ngắn, lên cao độ ở climax, nhiều cảm thán.
- **Hài hước**: chơi chữ, light-tone (dùng cẩn thận với events nhạy cảm).
- **Family-friendly**: an toàn, tránh từ ngữ kích động.

---

## 7 — Luật & guardrails (không được vi phạm)

- Không bịa stats/historical facts — nếu không chắc, ghi "theo dữ liệu hiện có" hoặc omit.
- Tránh cá nhân tấn công hoặc ngôn ngữ xúc phạm.
- Khi event low-confidence: dùng ngôn từ phòng ngừa.

---

---

## 9 — Timeline ví dụ (một highlight, ngắn gọn)

1. Detect sudden acceleration at t=00:15 → make candidate.
2. Track IDs 7 & 3 show crossing positions → mark overtaking at 00:16–00:17.
3. Build structured_event + query long-term (horse7 last 3 races).
4. Update short-term memory (push event).
5. Generate prompt → LLM produce: `"Ngựa số 7 bứt lên như tên lửa! Vượt qua số 3 ngay phía trước..."`.
6. Post-process, tag [REPLAY], TTS voice = "kịch tính".
7. Store script + audio, display subtitle at 00:16–00:18.