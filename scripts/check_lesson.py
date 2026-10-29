#!/usr/bin/env python3
"""Conservative checks for lesson drafts; NOT a semantic compliance certificate.

Exit 0: no covered mechanical findings; 1: findings; 2: input/check error.
The caller must still review meaning, prerequisites, coverage and continuity.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


LABEL = re.compile(
    r"^(思考题|分析|答案|Thinking question|Thought exercise|Analysis|Answer)\s*[:：]\s*(.*)$",
    re.IGNORECASE,
)
KINDS = {
    "思考题": "question", "thinking question": "question", "thought exercise": "question",
    "分析": "analysis", "analysis": "analysis", "答案": "answer", "answer": "answer",
}
PROGRESS = re.compile(r"^(?:【进度】|\[Progress\]|【Progress】)", re.IGNORECASE)
BANNED = [
    ("comprehension_check", r"懂了吗|明白了吗|这样清楚吗|有哪里不懂吗|能跟上吗|注意到了吗|你发现了吗|是不是很神奇|对吧[？?]"),
    ("learner_task", r"先猜一猜|用自己的话说说|试着回答|动手试试|运行一下告诉我结果|课后练习|留作练习|先自己想"),
    ("deferred_answer", r"下一轮揭晓|答案留给你|答案见(?:后文|下次)|回答后再揭晓"),
    ("feedback_dependency", r"如果你懂了|回复.{0,12}后我再讲|要不要(?:我)?继续|有问题随时问|还有什么想了解"),
    ("mastery_claim", r"你已经掌握|现在你学会了|你已经学会"),
    ("comprehension_check", r"\b(?:do you understand|does that make sense|can you follow)\b"),
    ("learner_task", r"\b(?:try it yourself|tell me the result|in your own words|guess what happens)\b"),
    ("feedback_dependency", r"\b(?:let me know if you|would you like me to continue|any questions)\b"),
    ("mastery_claim", r"\byou (?:have|['’]ve) (?:now )?mastered\b"),
]


def clean(line):
    line = re.sub(r"^\s*(?:>\s*)+", "", line).strip()
    line = re.sub(r"^#{1,6}\s+", "", line)
    return line.replace("**", "").strip()


def prose_lines(text):
    """Ignore fenced literal content, but inspect Markdown quote prose."""
    fence = None
    opening = None
    result = []
    for number, raw in enumerate(text.splitlines(), 1):
        line = re.sub(r"^\s*(?:>\s*)+", "", raw)
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if marker:
            token, tail = marker.groups()
            if fence is None:
                fence, opening = token, number
                continue
            if token[0] == fence[0] and len(token) >= len(fence) and not tail.strip():
                fence = None
                continue
        if fence is None:
            result.append((number, clean(line)))
    return result, opening if fence else None


def check(text):
    lines, unclosed = prose_lines(text)
    findings = []

    def add(code, number, detail):
        findings.append({"code": code, "line": number, "detail": detail})

    if not text.strip():
        add("empty_draft", 1, "教学稿为空。")
    if unclosed:
        add("unclosed_fence", unclosed, "代码围栏没有闭合，无法可靠检查后文。")
    meaningful = [(n, s) for n, s in lines if s]
    progress = [(n, s) for n, s in meaningful if PROGRESS.match(s)]
    if not progress:
        add("missing_progress", len(text.splitlines()) or 1, "缺少末尾进度行。")
    elif len(progress) > 1:
        add("duplicate_progress", progress[1][0], "每条回复应只有一个最终进度行。")
    if progress and meaningful[-1][0] != progress[-1][0]:
        add("content_after_progress", progress[-1][0], "进度行之后仍有文本。")
    # A code block after progress is also visible content, even if ignored as prose.
    if progress:
        tail = text.splitlines()[progress[-1][0]:]
        if any(s.strip() for s in tail):
            if not any(f["code"] == "content_after_progress" for f in findings):
                add("content_after_progress", progress[-1][0], "进度行之后仍有内容。")

    exercise = None
    phase = None
    content = {}

    def finish():
        if exercise is not None:
            for kind in ("question", "analysis", "answer"):
                if not content.get(kind):
                    add("exercise_missing_" + kind, exercise, "思考题必须依次有非空题干、分析和答案。")

    for number, line in lines:
        if not line:
            continue
        label = LABEL.match(line)
        if label:
            kind = KINDS[label[1].lower()]
            if kind == "question":
                finish()
                exercise, phase, content = number, "question", {}
            elif exercise is None:
                add("orphan_exercise_label", number, "分析或答案前未识别到思考题。")
                phase = None
            else:
                expected = "question" if kind == "analysis" else "analysis"
                if phase != expected:
                    add("exercise_order", number, "题干、分析、答案的顺序不正确或标签重复。")
                phase = kind
            if exercise is not None:
                content[kind] = bool(label[2].strip())
        elif PROGRESS.match(line):
            finish()
            exercise, phase, content = None, None, {}
        elif exercise is not None and phase:
            content[phase] = True

        # Inline code is literal syntax; a question mark there is not a question.
        visible = re.sub(r"(`+).*?\1", "", line)
        question_stem = exercise is not None and phase == "question"
        if re.search(r"[？?]", visible) and not question_stem:
            add("question_outside_exercise", number, "思考题题干之外存在问号；需审阅并改为陈述句。")
        for code, pattern in BANNED:
            if re.search(pattern, visible, re.IGNORECASE):
                add(code, number, "发现需修订或结合上下文审阅的措辞：" + visible[:160])
    finish()
    return {
        "status": "mechanical_findings" if findings else "no_mechanical_findings",
        "draft_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "semantic_compliance": "not_assessed",
        "scope": "固定措辞、问号位置、思考题标签与非空性、代码围栏、末尾进度行；不验证内容含义。",
        "findings": findings,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft", type=Path, help="UTF-8 Markdown lesson draft")
    args = parser.parse_args()
    try:
        report = check(args.draft.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        print(json.dumps({"status": "check_error", "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
