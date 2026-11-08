"""可重現的邊界測試：模型漏資訊時，程式仍能補齊必填欄位。"""

import unittest

from agent import Activity, check_facts, run_reflection


class ReflectionTests(unittest.TestCase):
    def test_three_distinct_calls_and_missing_fact_repair(self):
        replies = iter(
            [
                "桌遊夜來了！地點在圖書館 B1 討論室，免費參加。",
                "保留：語氣友善。修改：缺少時間，也沒有完整活動名稱。",
                "期中考後解壓桌遊夜將在 11/15 18:30 舉行，地點為圖書館 B1 討論室。",
            ]
        )
        calls = []

        def fake_model(system, user, temperature):
            calls.append((system, user, temperature))
            return next(replies)

        activity = Activity(
            "期中考後解壓桌遊夜", "11/15 18:30", "圖書館 B1 討論室", "免費"
        )
        result = run_reflection(activity, fake_model)
        self.assertEqual(len(calls), 3)
        self.assertFalse(result.before["時間"])
        self.assertIn("時間", calls[1][1])
        self.assertIn("缺少時間", calls[2][1])
        self.assertEqual(result.repaired, ("費用",))
        self.assertTrue(all(check_facts(result.final, activity).values()))
        self.assertIn("- 費用：免費", result.final)

    def test_empty_required_field_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "費用"):
            Activity("活動", "11/15", "教室", " ")


if __name__ == "__main__":
    unittest.main()
