import unittest

from fastapi.testclient import TestClient

from backend.main import app


class DashboardApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_health_endpoint(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_website_and_dashboard_routes(self) -> None:
        website = self.client.get("/")
        self.assertEqual(website.status_code, 200)
        self.assertIn("text/html", website.headers["content-type"])
        self.assertIn("Schooling, Connected", website.text)

        dashboard = self.client.get("/api/dashboard")
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(len(dashboard.json()["records"]), 224)

        static_data = self.client.get("/data/dashboard-data.json")
        self.assertEqual(static_data.status_code, 200)
        self.assertEqual(len(static_data.json()["records"]), 224)

    def test_full_sample_summary(self) -> None:
        response = self.client.get("/api/summary")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["school_count"], 8000)
        self.assertAlmostEqual(
            response.json()["mean_internet_access_percentage"], 59.68, places=2
        )

    def test_all_five_answers_and_state_category_groups(self) -> None:
        response = self.client.get("/api/questions")
        self.assertEqual(response.status_code, 200)
        answers = response.json()["answers"]
        self.assertEqual(set(answers), {"Q1", "Q2", "Q3", "Q4", "Q5"})
        self.assertEqual(answers["Q2"]["school_counts"], {"Rural": 6552, "Urban": 1448})
        self.assertEqual(answers["Q3"]["access_rate_missing_count"], 0)
        self.assertEqual(answers["Q4"]["group_count"], 112)
        self.assertEqual(answers["Q5"]["distributions"]["computers"]["count"], 8000)

    def test_filters_and_bad_filter_values(self) -> None:
        response = self.client.get(
            "/api/questions", params={"area": "Rural", "category": "Primary"}
        )
        self.assertEqual(response.status_code, 200)
        answers = response.json()["answers"]
        self.assertEqual(answers["Q1"]["school_count"], 1637)
        self.assertEqual(answers["Q4"]["group_count"], 28)
        self.assertEqual(sum(answers["Q5"]["school_counts_by_area"].values()), 1637)

        invalid = self.client.get("/api/summary", params={"area": "Everywhere"})
        self.assertEqual(invalid.status_code, 422)

    def test_individual_question_endpoint(self) -> None:
        response = self.client.get("/api/questions/2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["question"], "Q2")
        self.assertEqual(response.json()["answer"]["school_count"], 8000)

        invalid = self.client.get("/api/questions/6")
        self.assertEqual(invalid.status_code, 422)

    def test_pages_origin_is_allowed_by_cors(self) -> None:
        response = self.client.options(
            "/api/summary",
            headers={
                "Origin": "https://pranavigamidi.github.io",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["access-control-allow-origin"],
            "https://pranavigamidi.github.io",
        )


if __name__ == "__main__":
    unittest.main()
