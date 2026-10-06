# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| | | |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `openai:gpt-4.1-mini`, `0`, `60`.
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents 0.7.21`; Windows 11 cho phát triển, Docker/Linux cho kiểm thử chính thức.
- Số lần chạy tác vụ đã dùng / ngân sách:
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): `subagents` sẽ không vượt `baseline` trên tác vụ đánh giá và sẽ không hiệu quả hơn về token. Trên tập học, điểm kỹ thuật giảm từ 12/18 xuống 8/18; chỉ 2/3 tác vụ có gọi subagent, còn `code-learn` không gọi nhưng vẫn dùng nhiều token hơn baseline (92.665 so với 55.711).
- H2 (skills-auto so với baseline): `skills-auto` có thể cải thiện một số quy ước đã xuất hiện trong feedback học, đặc biệt với log, nhưng không chắc cải thiện điểm trung bình đánh giá. Lần phát triển tăng `logs-learn` từ 1/9 lên 5/9 nhưng không task nào đọc toàn bộ `SKILL.md` (`skills_read = 0`), và skill tự sinh có nguy cơ quá khớp.
- H3 (tác vụ học so với tác vụ đánh giá): hiệu quả trên tác vụ đánh giá dự kiến thấp hơn hoặc biến động hơn tác vụ học vì mỗi task đánh giá có dữ liệu khác và thêm quy ước mới chưa xuất hiện trong feedback học; skill chỉ mã hóa các quy trình và quy ước đã quan sát.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có các công cụ tệp `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`; công cụ shell `execute`; và công cụ giao việc `task`. Công cụ `execute` cho phép chạy lệnh.
2. `general-purpose` dùng cho nghiên cứu câu hỏi phức tạp, tìm tệp/nội dung và tác vụ nhiều bước; nó có cùng công cụ với tác tử chính. Mỗi lần gọi mặc định là stateless: subagent chỉ thấy prompt được giao và trả về một báo cáo cuối, không thấy toàn bộ ngữ cảnh của tác tử chính.
3. Từ `task`: “Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report.” Từ `execute`: “You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search.”

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `tests_not_modified` | A. Bỏ qua đặc tả | Agent sửa tệp test có sẵn dù đề ghi “Do not modify the existing files in tests/”. |
| `code-learn` | `rule_type_hints` | E. Vi phạm quy ước tổ chức | `RULE: every public function ... has type annotations` trên mọi tham số và giá trị trả về. |
| `code-learn` | `rule_regression_tests` | E. Vi phạm quy ước tổ chức | Thiếu `tests/test_regressions.py` với ít nhất ba test cho các lỗi đã sửa. |
| `code-learn` | `rule_changelog` | E. Vi phạm quy ước tổ chức | Thiếu ít nhất ba bullet `fix(<function name>): ...` dưới `## Unreleased`. |
| `data-learn` | `rule_money_in_cents` | E. Vi phạm quy ước tổ chức | Tiền trong `answer.json` phải là integer cents; agent ghi `3130.24`. |
| `data-learn` | `rule_meta_block` | E. Vi phạm quy ước tổ chức | Thiếu object `meta` gồm `source`, `rows_in`, `rows_used`. |
| `data-learn` | `rule_clean_csv` | E. Vi phạm quy ước tổ chức | Thiếu `clean.csv` theo schema và chuẩn hóa Acme yêu cầu. |
| `logs-learn` | `entry_count` | D. Bỏ sót dữ liệu/định dạng | Check báo “wrong number of entries (got 20)”; trace cho thấy agent đọc log theo hai đoạn rồi tự viết JSON thủ công. |
| `logs-learn` | `timestamps_utc` | D. Bỏ sót dữ liệu/định dạng | Chỉ 9/25 timestamp khớp, cho thấy chuyển múi giờ/bao phủ entry chưa đầy đủ. |
| `logs-learn` | `exception_fields` | D. Bỏ sót dữ liệu/định dạng | 16 giá trị `exception` sai. |
| `logs-learn` | `repeat_counts` | D. Bỏ sót dữ liệu/định dạng | 16 `repeat_count` sai. |
| `logs-learn` | `counts_by_service` | D. Bỏ sót dữ liệu/định dạng | Tổng theo service sai do entry và repeat count sai. |
| `logs-learn` | `rule_service_names` | E. Vi phạm quy ước tổ chức | Service phải lowercase và đổi `-` thành `_`. |
| `logs-learn` | `rule_sorted_errors` | E. Vi phạm quy ước tổ chức | Phải sắp xếp theo service rồi timestamp tăng dần. |
| `logs-learn` | `rule_schema_header` | E. Vi phạm quy ước tổ chức | Thiếu `schema_version: 2` và `generated_by: log-triage`. |

Nhận xét: nhóm E chiếm 9/15 check thất bại; nhóm D có 5/15 và nhóm A có 1/15. Baseline đạt 12/18 check kỹ thuật nhưng 0/9 check quy ước. Skill có thể mã hóa các quy ước E và checklist phân tích log để giảm lỗi D, nhưng quy ước mới ở tập đánh giá vẫn là thử thách tổng quát hóa.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa: `explorer` đọc đặc tả và báo cáo không sửa file; `implementer` thay đổi file và kiểm thử; `reviewer` kiểm tra độc lập theo yêu cầu và edge case. Thiết kế tách khám phá, thực thi và xác minh để giảm bỏ sót đặc tả.
- `subagent_calls`: `code-learn = 0`, `data-learn = 1`, `logs-learn = 1`. Việc `code-learn` không gọi subagent là lựa chọn hợp lệ của agent chính dù system prompt khuyến khích giao việc.
- Khi có giao việc, kết quả cuối vẫn cần agent chính xác minh; điểm thấp của data (1/8) và logs (1/9) cho thấy báo cáo subagent hoặc việc tích hợp báo cáo không đủ để bảo đảm đầu ra đúng.
- Token: baseline trung bình 61.419; subagents trung bình 50.536. Tuy trung bình thấp hơn do data/logs kết thúc sớm với điểm kém, `code-learn` lại tăng từ 55.711 lên 92.665 token mà điểm giữ nguyên 6/10. Vì vậy chưa có bằng chứng đa tác tử đáng chi phí.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator: 1. Số skill bị xóa: 0. Cả ba skill hợp lệ về định dạng và không chứa marker của tập đánh giá. Không sửa tay nội dung skill.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `enforce-type-annotations` | Tổng quát cho package Python | Chủ yếu đúng; câu “placeholder or inferred type” có thể tạo annotation quá chung, cần xem là hạn chế. | 11 dòng; description nêu đúng tình huống kiểm tra public function; `skills_read = 0` ở mọi task. |
| `add-regression-tests-and-changelog` | Tổng quát cho quy trình sửa lỗi có convention | Đúng với feedback: mỗi bug có regression test, cập nhật `## Unreleased`, không sửa test cũ và chạy full suite. | 11 dòng; description kích hoạt khi sửa bug; `skills_read = 0`. |
| `parse-and-normalize-logs-for-errors` | Tổng quát cho log có traceback/repeat/timezone | Đúng với đề và feedback; bao phủ service normalization, sort và schema metadata. | 16 dòng; description kích hoạt rõ cho log ERROR/CRITICAL; `skills_read = 0`. |

Kết quả Phần 3.4: code 6/10 (81.400 token), data 4/8 (80.029), logs 5/9 (70.025). Không lần nào gọi `read_file` trên `SKILL.md`; cải thiện logs vì thế chưa chứng minh agent làm theo toàn bộ skill, có thể do metadata skill trong prompt hoặc nhiễu giữa các lần chạy.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

```text
(dán bảng ở đây)
```

## 8. Phân tích

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ học và tác vụ đánh giá?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`).
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp.
4. So sánh chi phí token và hiệu quả điểm trên mỗi token.
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào không?
6. So sánh nhiễu giữa lần chạy Phần 3.4 và sau đóng băng.

## 9. Hạn chế và tính hợp lệ

1.
2.
3.

## 10. Kết luận

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có):
- Ghi chú khác:
