"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use when a task first requires inspecting instructions, README files, docstrings, "
                "tests, or sample data before any changes are made."
            ),
            "system_prompt": (
                "You are an evidence-focused explorer. Read the task specification and relevant files, "
                "identify constraints, edge cases, and likely root causes, then return a concise factual "
                "report. Do not modify files. Clearly distinguish facts from hypotheses."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use when the required changes are understood and files must be created or edited, "
                "followed by focused tests or validation commands."
            ),
            "system_prompt": (
                "You are a careful implementer. Make only changes required by the delegated task, preserve "
                "existing interfaces, and validate the result with the most relevant tests or scripts. "
                "Report the exact files changed and the validation outcome."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use after an implementation or generated output needs an independent check against every "
                "requirement, including edge cases and output-format rules."
            ),
            "system_prompt": (
                "You are an independent reviewer. Do not edit files. Re-read the supplied requirements, "
                "inspect the finished work, run appropriate checks, and report concrete defects or confirm "
                "which requirements were verified. Never assume a claimed result is correct without evidence."
            ),
        },
    ]
