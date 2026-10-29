#!/usr/bin/env python3
"""Tests of the checker, not tests of model compliance or teaching quality."""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from check_lesson import check


PROGRESS = "【进度】本轮已讲完：平均数｜还没讲：更多例子｜下一轮讲：更多例子。"
LESSON = (
    "这次讲平均数。\n"
    "三个人分别拿到 2、4、6 颗糖，共 12 颗，重新平分后每人拿 4 颗。\n"
    "这个 4 叫作**平均数**，表示把这组数量平分后每份的数量。\n"
    "**思考题：** 两个人分别拿到 2、6 颗糖，平均数是多少？\n"
    "**分析：** 合起来有 8 颗，平均分成两份，每份 4 颗。\n"
    "**答案：** 平均数是 4 颗。\n" + PROGRESS
)


class CheckerTests(unittest.TestCase):
    def codes(self, text):
        return {item["code"] for item in check(text)["findings"]}

    def test_complete_exercise(self):
        self.assertEqual(check(LESSON)["findings"], [])

    def test_semantics_never_certified(self):
        report = check("平均数是描述集中趋势的统计量。\n" + PROGRESS)
        self.assertEqual(report["status"], "no_mechanical_findings")
        self.assertEqual(report["semantic_compliance"], "not_assessed")

    def test_hash_identifies_checked_text(self):
        self.assertEqual(check(LESSON)["draft_sha256"], hashlib.sha256(LESSON.encode()).hexdigest())
        self.assertNotEqual(check(LESSON)["draft_sha256"], check(LESSON + "追加")["draft_sha256"])

    def test_missing_answer(self):
        self.assertIn("exercise_missing_answer", self.codes(LESSON.replace("**答案：** 平均数是 4 颗。\n", "")))

    def test_empty_analysis(self):
        self.assertIn("exercise_missing_analysis", self.codes(LESSON.replace("合起来有 8 颗，平均分成两份，每份 4 颗。", "")))

    def test_empty_stem(self):
        self.assertIn("exercise_missing_question", self.codes("思考题：\n分析：相加后平分。\n答案：4。\n" + PROGRESS))

    def test_answer_order(self):
        self.assertIn("exercise_order", self.codes("思考题：多少？\n答案：4。\n分析：相加后平分。\n" + PROGRESS))

    def test_each_question_requires_answer(self):
        self.assertIn("exercise_missing_answer", self.codes("思考题：多少？\n分析：相加。\n" + LESSON))

    def test_question_in_analysis(self):
        self.assertIn("question_outside_exercise", self.codes(LESSON.replace("**分析：**", "**分析：** 为什么？")))

    def test_unlabelled_question(self):
        self.assertIn("question_outside_exercise", self.codes("为什么会这样？\n" + PROGRESS))

    def test_task_without_question_mark(self):
        self.assertIn("learner_task", self.codes("动手试试，然后运行一下告诉我结果。\n" + PROGRESS))

    def test_quote_does_not_hide_request(self):
        self.assertIn("comprehension_check", self.codes("> 懂了吗\n" + PROGRESS))

    def test_mastery_claim(self):
        self.assertIn("mastery_claim", self.codes("你已经掌握了平均数。\n" + PROGRESS))

    def test_deferred_answer(self):
        self.assertIn("deferred_answer", self.codes("答案留给你，下一轮揭晓。\n" + PROGRESS))

    def test_progress_required(self):
        self.assertIn("missing_progress", self.codes("平均数已经讲完。"))

    def test_no_tail_after_progress(self):
        self.assertIn("content_after_progress", self.codes(LESSON + "\n继续学习下一节。"))

    def test_no_code_tail_after_progress(self):
        self.assertIn("content_after_progress", self.codes(LESSON + "\n```python\nprint(1)\n```"))

    def test_unclosed_fence_blocks_check(self):
        self.assertIn("unclosed_fence", self.codes("```python\nprint(1)\n" + PROGRESS))

    def test_code_question_mark_is_not_prose_question(self):
        self.assertNotIn("question_outside_exercise", self.codes("```python\nprint('?')\n```\n" + PROGRESS))

    def test_inline_literal_question_mark(self):
        self.assertNotIn("question_outside_exercise", self.codes("`?` 是一个字符。\n" + PROGRESS))

    def test_longer_nested_fence(self):
        self.assertNotIn("unclosed_fence", self.codes("````markdown\n```python\nprint('?')\n```\n````\n" + PROGRESS))

    def test_english_exercise(self):
        report = check("Thought exercise: What is the mean?\nAnalysis: Add and divide.\nAnswer: Four.\n[Progress] Covered: mean.")
        self.assertEqual(report["findings"], [])

    def test_english_feedback_request(self):
        self.assertIn("feedback_dependency", self.codes("Let me know if you understand.\n[Progress] Covered: mean."))

    def test_empty_input_fails(self):
        self.assertIn("empty_draft", self.codes(""))

    def test_cli_exit_codes(self):
        script = Path(__file__).with_name("check_lesson.py")
        with tempfile.TemporaryDirectory() as folder:
            draft = Path(folder) / "draft.md"
            draft.write_text(LESSON, encoding="utf-8")
            good = subprocess.run([sys.executable, str(script), str(draft)], capture_output=True, text=True)
            self.assertEqual(good.returncode, 0)
            self.assertEqual(json.loads(good.stdout)["semantic_compliance"], "not_assessed")
            draft.write_text("懂了吗？", encoding="utf-8")
            bad = subprocess.run([sys.executable, str(script), str(draft)], capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1)
            missing = subprocess.run([sys.executable, str(script), str(Path(folder) / "missing.md")], capture_output=True, text=True)
            self.assertEqual(missing.returncode, 2)


if __name__ == "__main__":
    unittest.main()
