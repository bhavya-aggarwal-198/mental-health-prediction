from functools import lru_cache
from numbers import Real
from pathlib import Path

import joblib
import pandas as pd
from django import forms
from django.conf import settings
from django.shortcuts import render
from sklearn.compose import _column_transformer


FEATURE_COLUMNS = (
    "Study_Hours",
    "Age",
    "Avg_Daily_Usage_Hours",
    "Daily_Unlocks",
    "Physical_Activity_Hours",
    "Sleep_Hours_Per_Night",
    "Stress_Level",
    "Gender",
    "Academic_Level",
    "Most_Used_Platform",
    "Purpose_Of_Use",
    "Grouped_country",
)

GENDER_CHOICES = (("Female", "Female"), ("Male", "Male"))
ACADEMIC_LEVEL_CHOICES = (
    ("Graduate", "Graduate"),
    ("High School", "High School"),
    ("Undergraduate", "Undergraduate"),
)
PLATFORM_CHOICES = tuple(
    (value, value)
    for value in (
        "Facebook",
        "Instagram",
        "KakaoTalk",
        "LINE",
        "LinkedIn",
        "Snapchat",
        "TikTok",
        "Twitter",
        "VKontakte",
        "WeChat",
        "WhatsApp",
        "YouTube",
    )
)
PURPOSE_CHOICES = tuple(
    (value, value)
    for value in ("Education", "Entertainment", "Networking", "News")
)
COUNTRY_CHOICES = tuple(
    (value, value)
    for value in (
        "Australia",
        "Canada",
        "France",
        "Germany",
        "India",
        "Mexico",
        "Other",
        "Turkey",
        "UK",
        "USA",
    )
)


class MentalHealthPredictionForm(forms.Form):
    study_hours = forms.DecimalField(
        label="Study hours per day",
        min_value=0,
        max_value=24,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"step": "0.1"}),
    )
    age = forms.IntegerField(label="Age", min_value=1, max_value=120)
    avg_daily_usage_hours = forms.DecimalField(
        label="Average daily device usage (hours)",
        min_value=0,
        max_value=24,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"step": "0.1"}),
    )
    daily_unlocks = forms.IntegerField(label="Daily device unlocks", min_value=0)
    physical_activity_hours = forms.DecimalField(
        label="Physical activity per day (hours)",
        min_value=0,
        max_value=24,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"step": "0.1"}),
    )
    sleep_hours_per_night = forms.DecimalField(
        label="Sleep per night (hours)",
        min_value=0,
        max_value=24,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"step": "0.1"}),
    )
    stress_level = forms.ChoiceField(
        label="Stress level",
        choices=(
            ("Low", "Low"),
            ("Medium", "Medium"),
            ("High", "High"),
            ("Very High", "Very High"),
        ),
    )
    gender = forms.ChoiceField(
        label="Gender",
        choices=GENDER_CHOICES,
    )
    academic_level = forms.ChoiceField(
        label="Academic level",
        choices=ACADEMIC_LEVEL_CHOICES,
    )
    most_used_platform = forms.ChoiceField(
        label="Most used platform",
        choices=PLATFORM_CHOICES,
    )
    purpose_of_use = forms.ChoiceField(
        label="Main purpose of use",
        choices=PURPOSE_CHOICES,
    )
    grouped_country = forms.ChoiceField(
        label="Country group",
        choices=COUNTRY_CHOICES,
    )

    def model_input(self) -> dict[str, object]:
        values = self.cleaned_data
        return {
            "Study_Hours": float(values["study_hours"]),
            "Age": values["age"],
            "Avg_Daily_Usage_Hours": float(values["avg_daily_usage_hours"]),
            "Daily_Unlocks": values["daily_unlocks"],
            "Physical_Activity_Hours": float(values["physical_activity_hours"]),
            "Sleep_Hours_Per_Night": float(values["sleep_hours_per_night"]),
            "Stress_Level": values["stress_level"],
            "Gender": values["gender"],
            "Academic_Level": values["academic_level"],
            "Most_Used_Platform": values["most_used_platform"],
            "Purpose_Of_Use": values["purpose_of_use"],
            "Grouped_country": values["grouped_country"],
        }


@lru_cache(maxsize=1)
def load_model():
    model_path = Path(settings.BASE_DIR) / "model" / "Mental_health_model.pkl"
    if not hasattr(_column_transformer, "_RemainderColsList"):
        legacy_remainder_columns = type(
            "_RemainderColsList",
            (list,),
            {"__module__": _column_transformer.__name__},
        )
        _column_transformer._RemainderColsList = legacy_remainder_columns

    try:
        model = joblib.load(model_path)
    except AttributeError as error:
        raise RuntimeError(
            "The saved model is incompatible with the installed scikit-learn "
            "version. It was saved with scikit-learn 1.6.1; run this project "
            "with that version or re-export the model using the installed version."
        ) from error

    model_features = tuple(getattr(model, "feature_names_in_", ()))
    if model_features != FEATURE_COLUMNS:
        raise RuntimeError(
            "The saved model's input columns do not match the prediction form."
        )
    return model


def home(request):
    form = MentalHealthPredictionForm(request.POST or None)
    context = {"form": form}

    if request.method == "POST" and form.is_valid():
        try:
            model = load_model()
        except RuntimeError as error:
            context["model_error"] = str(error)
            return render(request, "home.html", context, status=503)

        model_input = pd.DataFrame(
            [form.model_input()],
            columns=FEATURE_COLUMNS,
        )
        prediction = model.predict(model_input)[0]
        if hasattr(prediction, "item"):
            prediction = prediction.item()
        if isinstance(prediction, Real):
            score = float(prediction)
            context["prediction"] = f"{score:.3f}"
            context["prediction_percent"] = max(0.0, min(100.0, score * 10))
        else:
            context["prediction"] = str(prediction)

    return render(request, "home.html", context)
