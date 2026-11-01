# Cambodia Rain Prediction

A Django web application that predicts the likelihood of rain from weather conditions. The application uses a bundled three-layer neural network trained on Cambodia weather data and provides both a browser interface and JSON API endpoints.

## Features

- Rain prediction from 10 weather measurements
- Neural-network inference using PyTorch and bundled Joblib model files
- Probability, confidence, prediction label, and weather recommendation
- Prediction history stored in SQLite
- Model information and health-check endpoints
- Responsive web interface for entering weather data

## Technology Stack

- Python
- Django
- Django REST Framework
- PyTorch
- NumPy, pandas, scikit-learn, and Joblib
- SQLite
- Bootstrap and Font Awesome for the web interface

## Project Structure

```text
django_rain_prediction/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── rainNueralNetwork.joblib
├── training_stats.joblib
├── rain_prediction_project/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── prediction_api/
│   ├── ml_model.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
└── templates/
    ├── index.html
    ├── model_info.html
    └── test.html
```

## Requirements

- Python 3.9 or newer
- pip

The trained model files `rainNueralNetwork.joblib` and `training_stats.joblib` must remain in the project root because Django loads them from `MODEL_FILES_PATH`.

## Installation

1. Open a terminal in the directory containing `manage.py`.

2. Create and activate a virtual environment:

   **Windows PowerShell**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS/Linux**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

5. Start the development server:

   ```bash
   python manage.py runserver
   ```

6. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in a browser.

## Web Pages

| URL | Description |
| --- | --- |
| `/` | Main rain prediction interface |
| `/model/` | Neural-network and training information |
| `/test/` | Test page |
| `/admin/` | Django administration |

## API Endpoints

All API routes are under `/api/`.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/predict/` | Validate input, run a prediction, and save it to history |
| `GET` | `/api/history/` | Return the latest 50 predictions |
| `GET` | `/api/model-info/` | Return model architecture and input-feature information |
| `GET` | `/api/health/` | Verify that the API and model are available |

### Prediction Request

Send JSON to `/api/predict/` with these 10 fields:

```json
{
  "temperature": 30,
  "feels_like_max": 35,
  "dew_point": 24,
  "humidity": 75,
  "sea_level_pressure": 29.8,
  "wind_speed": 10,
  "wind_direction": 180,
  "visibility": 10,
  "cloud_cover": 80,
  "wind_gust": 18
}
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 30,
    "feels_like_max": 35,
    "dew_point": 24,
    "humidity": 75,
    "sea_level_pressure": 29.8,
    "wind_speed": 10,
    "wind_direction": 180,
    "visibility": 10,
    "cloud_cover": 80,
    "wind_gust": 18
  }'
```

The response includes:

- `rain_probability`: predicted probability as a percentage
- `prediction_result`: `Rain Expected` or `No Rain Expected`
- `confidence`: model confidence percentage
- `probability_level`: `Low`, `Medium`, or `High`
- `recommendation`: weather-related guidance
- `input_data`: normalized request values
- `prediction_id`: saved database record ID

### Health Check

```bash
curl http://127.0.0.1:8000/api/health/
```

A healthy response contains:

```json
{
  "status": "healthy",
  "model_loaded": true,
  "message": "API is working correctly"
}
```

## Model

The application uses a sigmoid neural network with the following architecture:

```text
10 input features → 5 neurons → 5 neurons → 1 output
```

The model uses normalized input values based on the statistics stored in `training_stats.joblib`. The model metadata describes training on Cambodia weather data from 2022–2024.

Input features:

1. Temperature (°C)
2. Feels-like maximum temperature (°C)
3. Dew point (°C)
4. Humidity (%)
5. Sea-level pressure (inHg)
6. Wind speed (mph)
7. Wind direction (degrees)
8. Visibility (miles)
9. Cloud cover (%)
10. Wind gust (mph)

## Database

The default database is SQLite at `db.sqlite3`. Each successful prediction stores the input measurements, prediction result, probability, confidence, timestamp, and client IP address.

To create an administrator account:

```bash
python manage.py createsuperuser
```

Then visit [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

## Production Notes

Before deploying this application:

- Set `DEBUG = False`.
- Replace the development `SECRET_KEY`.
- Configure `ALLOWED_HOSTS` for the deployment domain.
- Set appropriate CORS origins instead of allowing all origins.
- Use a production WSGI or ASGI server.
- Store model files and database data using a suitable deployment strategy.
- Review logging and error handling before exposing the API publicly.

## License

No license is currently specified for this project.
