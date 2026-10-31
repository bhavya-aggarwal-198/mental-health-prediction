# Mental Health Prediction

A Django web application that predicts a mental-health-related outcome from submitted information using a trained machine-learning model.

## Run locally

```powershell
cd mental_health
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

For deployment, set `DJANGO_SECRET_KEY` to a secure, unique value.
