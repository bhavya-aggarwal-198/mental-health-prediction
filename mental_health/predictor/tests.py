from unittest.mock import patch

from django.test import TestCase

from .views import FEATURE_COLUMNS


class StubModel:
    feature_names_in_ = FEATURE_COLUMNS

    def predict(self, features):
        self.features = features
        return ["moderate"]


class HomeViewTests(TestCase):
    valid_prediction_data = {
        "study_hours": "4.5",
        "age": "21",
        "avg_daily_usage_hours": "6",
        "daily_unlocks": "40",
        "physical_activity_hours": "1",
        "sleep_hours_per_night": "8",
        "stress_level": "Medium",
        "gender": "Female",
        "academic_level": "Undergraduate",
        "most_used_platform": "Instagram",
        "purpose_of_use": "Entertainment",
        "grouped_country": "Other",
    }

    def test_home_displays_prediction_form(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Make space for")
        self.assertContains(response, 'name="study_hours"')
        self.assertContains(response, "Created by Bhavya Aggarwal")
        self.assertContains(response, "scikit-learn")
        self.assertContains(response, "Portfolio")

    @patch("predictor.views.load_model")
    def test_valid_submission_passes_model_features_in_expected_order(
        self, load_model
    ):
        model = StubModel()
        load_model.return_value = model
        response = self.client.post(
            "/",
            self.valid_prediction_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["prediction"], "moderate")
        self.assertEqual(tuple(model.features.columns), FEATURE_COLUMNS)
        self.assertEqual(model.features.iloc[0]["Age"], 21)

    def test_saved_model_returns_a_prediction(self):
        response = self.client.post("/", self.valid_prediction_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["prediction"], "5.677")
        self.assertEqual(response.context["prediction_percent"], 56.77)
        self.assertContains(response, "OUT OF 10")
        self.assertContains(response, "WELLNESS ESTIMATE")
        self.assertContains(response, "5.7</text>")
        self.assertContains(response, "higher estimated wellness")
        self.assertIsNone(response.context.get("model_error"))

    @patch("predictor.views.load_model")
    def test_invalid_submission_does_not_load_model(self, load_model):
        response = self.client.post("/", {"age": "not-a-number"})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        load_model.assert_not_called()
