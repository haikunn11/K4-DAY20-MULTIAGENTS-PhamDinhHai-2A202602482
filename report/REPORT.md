# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Phạm Đình Hải | 2A202602482 | Cá nhân, 100% |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `openai:gpt-4.1-mini`, `0`, `60`.
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents 0.7.21`; Windows 11 cho phát triển, Docker/Linux cho kiểm thử chính thức.
- Số lần chạy tác vụ đã dùng / ngân sách: 21 lần (18 kết quả chính thức và 3 lần phát triển skills-auto); ngân sách không được chỉ định.
- Commit của tag `freeze`: `0630af8`.

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
| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 6/10 | 6/10 | 6/10 |
| data-learn | 5/8 | 1/8 | 5/8 |
| logs-learn | 1/9 | 1/9 | 1/9 |
| code-eval | 6/11 | 6/11 | 6/11 |
| data-eval | 5/9 | 2/9 | 5/9 |
| logs-eval | 1/10 | 0/10 | 6/10 |
| Mean score - learning tasks | 0.45 | 0.28 | 0.45 |
| Mean score - evaluation tasks | 0.40 | 0.26 | 0.57 |
| Mean tokens per run | 59,159 | 47,230 | 52,202 |
| Runs that read a skill | 0/6 | 0/6 | 0/6 |

condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     12/18         0/12          56,899      0/3
baseline      learn    12/18         0/9           61,419      0/3
subagents     eval      8/18         0/12          43,924      0/3
subagents     learn     8/18         0/9           50,536      0/3
skills-auto   eval     17/18         0/12          52,504      0/3
skills-auto   learn    12/18         0/9           51,901      0/3
```

Không có run nào có `error` hoặc `skills_modified = true`. `verify_freeze.py` chạy trong Linux báo `checked 6 runs of skill conditions: OK`. Khi chạy verifier trên Windows, hash khác do `hash_skills` dùng ký tự phân cách đường dẫn (`\` so với `/`); đối chiếu trong cùng môi trường Linux xác nhận hash của sáu run đúng với skill đã freeze.

## 8. Phân tích

1. Trên task học, baseline và skills-auto cùng đạt trung bình 0,45; subagents giảm còn 0,28. Trên task đánh giá, skills-auto đạt 0,57, cao hơn baseline 0,40; subagents giảm còn 0,26. Chênh lệch skills-auto chủ yếu đến từ `logs-eval` (6/10 so với baseline 1/10), không phải cải thiện đồng đều: code và data giữ nguyên baseline. Vì không có skill nào được đọc và nhiễu task học lớn, kết quả không đủ để kết luận skill gây ra cải thiện.
2. Baseline đạt 12/18 check kỹ thuật ở cả learn và eval nhưng 0/9 và 0/12 check quy ước. Subagents giảm check kỹ thuật xuống 8/18 ở cả hai vai trò và vẫn 0 check quy ước. Skills-auto giữ 12/18 kỹ thuật trên learn và tăng lên 17/18 trên eval, nhưng vẫn 0/12 quy ước eval. Như vậy quy ước mới không được giải quyết; phần tăng chỉ nằm ở check kỹ thuật của log.
3. Ở `logs-eval`, skills-auto đạt `entry_count`, `timestamps_utc`, `levels_uppercase`, `repeat_counts`, `counts_by_service`, trong khi baseline chỉ đạt `valid_structure`. Trace cho thấy agent viết parser Python thay vì chép JSON thủ công, nhưng `skills_read = 0`, nên chỉ có thể nói hành vi trùng với mô tả skill, không thể nói agent đã đọc và làm theo skill. Bốn check `rule_service_names`, `rule_sorted_errors`, `rule_schema_header`, `rule_source_line` đều không đạt; không đọc `SKILL.md` giải thích vì sao các chỉ dẫn quy ước chi tiết không được áp dụng.
4. Token trung bình toàn bộ run: baseline 59.159, subagents 47.230, skills-auto 52.202. Nếu lấy trung bình learn/eval bằng nhau, điểm trung bình xấp xỉ 0,425; 0,270; 0,510, tương ứng khoảng 7,2; 5,7; 9,8 điểm chuẩn hóa trên một triệu token. Skills-auto có tỷ lệ điểm/token cao nhất trong mẫu này; subagents thấp nhất. Token thấp của subagents phần nào do data/logs kết thúc sớm với kết quả kém, nên không phải tiết kiệm hiệu quả.
5. `validate_skill` loại marker eval và curator chỉ đọc run có `role == learn`; ba skill không chứa id/tệp/con số của eval, nên không thấy rò rỉ dữ liệu. Có nguy cơ quá khớp quy ước học, nhưng dữ liệu không cho thấy “học thuộc” thành công vì mọi điều kiện vẫn đạt 0 check quy ước eval và `skills_read = 0`.
6. Với cùng bộ skill, lần phát triển so với sau freeze: code 6/10 → 6/10 (0), data 4/8 → 5/8 (+0,125), logs 5/9 → 1/9 (-0,444). Điểm trung bình task học giảm khoảng 0,107 (0,552 → 0,445). Biến động này lớn hơn nhiều chênh lệch ở một số ô của bảng, nên kết luận từ một lần chạy phải rất thận trọng.

## 9. Hạn chế và tính hợp lệ

1. Chỉ có ba task cho mỗi vai trò và mỗi cấu hình chính thức chạy một lần; một outlier như `logs-eval` có thể thay đổi mạnh trung bình, làm độ tin cậy thống kê thấp.
2. Mô hình có tính ngẫu nhiên dù temperature bằng 0; chênh lệch logs-learn 5/9 xuống 1/9 với cùng skill cho thấy backend/model/tool trajectory vẫn gây nhiễu đáng kể.
3. Các task và house rule do giảng viên thiết kế, nên kết quả có thể không đại diện cho dự án phần mềm, dữ liệu và log thực tế.
4. Chỉ dùng một model (`gpt-4.1-mini`); kết luận về subagent và skill có thể thay đổi với model có khả năng lập kế hoạch hoặc dùng tool khác.
5. `skills_read` chỉ đếm `read_file` ở luồng chính; nó không đo ảnh hưởng của metadata `name`/`description` đã xuất hiện trong system prompt, và cũng không thấy hoạt động bên trong subagent.

## 10. Kết luận

Trong thí nghiệm này, subagents không cải thiện điểm và có hiệu quả điểm/token thấp hơn baseline. Skills-auto đạt điểm đánh giá trung bình cao nhất, chủ yếu nhờ check kỹ thuật của một task log, nhưng không cải thiện bất kỳ house rule đánh giá nào. Vì `skills_read = 0` ở mọi run và cùng skill tạo kết quả task học biến động mạnh, chưa thể quy cải thiện cho nội dung skill. Quy trình freeze không phát hiện rò rỉ dữ liệu và verifier Linux báo OK. Bước tiếp theo nên lặp mỗi cấu hình nhiều lần và cải thiện cơ chế bắt buộc đọc skill phù hợp trước khi so sánh lại.

## Phụ lục

- Lệnh đã chạy (theo thứ tự): tạo `.venv`; `pip install -e .`; `pytest`; `scripts/tour.py`; các lệnh `lab.runner` cho baseline/subagents/skills-auto; `lab.curator`; commit `hypotheses`; tag `freeze`; `verify_freeze.py`; `lab.compare`; `check_breakdown.py`.
- Thử thách mở rộng (nếu có): không thực hiện.
- Ghi chú khác: các lần chạy Linux thực hiện trong container `lab-deepagents-work`; verifier cần chạy cùng môi trường Linux do hash có chứa ký tự phân cách đường dẫn.
