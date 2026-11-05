import unittest

from silvercare_history_mcp.server import get_health_history


class HealthHistoryTests(unittest.IsolatedAsyncioTestCase):
    async def query(self, **overrides):
        params = {
            "user_id": "user_001",
            "metric_type": "heart_rate",
            "start_time": "2026-10-26T00:00:00Z",
            "end_time": "2026-11-02T23:59:59Z",
            "limit": 20,
        }
        params.update(overrides)
        return await get_health_history(**params)

    async def test_returns_three_heart_rate_records(self):
        result = await self.query()
        self.assertTrue(result["success"])
        self.assertEqual(result["total"], 3)
        self.assertEqual(
            [record["record_id"] for record in result["records"]],
            ["hr_001", "hr_002", "hr_003"],
        )
        self.assertIsNone(result["error"])

    async def test_limit_returns_latest_records_in_chronological_order(self):
        result = await self.query(limit=2)
        self.assertEqual(result["total"], 2)
        self.assertEqual(
            [record["record_id"] for record in result["records"]],
            ["hr_002", "hr_003"],
        )

    async def test_no_matching_records_is_success(self):
        result = await self.query(
            start_time="2027-01-01T00:00:00Z",
            end_time="2027-01-02T00:00:00Z",
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["records"], [])
        self.assertEqual(result["total"], 0)

    async def test_invalid_time_format(self):
        result = await self.query(start_time="not-a-time")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["code"], "INVALID_TIME_FORMAT")

    async def test_invalid_time_range(self):
        result = await self.query(
            start_time="2026-11-03T00:00:00Z",
            end_time="2026-11-02T00:00:00Z",
        )
        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["code"], "INVALID_TIME_RANGE")

    async def test_unknown_user(self):
        result = await self.query(user_id="unknown")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["code"], "USER_NOT_FOUND")

    async def test_all_supported_metrics_have_units(self):
        expected_units = {
            "heart_rate": "bpm",
            "blood_pressure": "mmHg",
            "temperature": "°C",
            "spo2": "%",
        }
        for metric_type, unit in expected_units.items():
            with self.subTest(metric_type=metric_type):
                result = await self.query(metric_type=metric_type)
                self.assertTrue(result["success"])
                self.assertEqual(result["records"][0]["unit"], unit)


if __name__ == "__main__":
    unittest.main()
