from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from .models import WeatherPrediction
from .ml_model import get_weather_model

def home_view(request):
    """Render the main HTML page"""
    return render(request, 'index.html')

def model_info_view(request):
    """Render the model information page"""
    return render(request, 'model_info.html')

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def validate_weather_input(data):
    """Enhanced validation for weather input data with range checks"""
    required_fields = {
        'temperature': (-50.0, 60.0),  # Celsius
        'feels_like_max': (-50.0, 70.0),  # Celsius
        'dew_point': (-50.0, 40.0),  # Celsius
        'humidity': (0.0, 100.0),  # Percentage
        'sea_level_pressure': (28.0, 32.0),  # inHg
        'wind_speed': (0.0, 200.0),  # mph
        'wind_direction': (0.0, 360.0),  # degrees
        'cloud_cover': (0.0, 100.0),  # percentage
        'wind_gust': (0.0, 300.0),  # mph
        'visibility': (0.0, 50.0)  # miles
    }
    errors = {}
    for field, (min_val, max_val) in required_fields.items():
        if field not in data:
            errors[field] = f'{field} is required'
        else:
            try:
                value = float(data[field])
                if not (min_val <= value <= max_val):
                    errors[field] = f'{field} must be between {min_val} and {max_val}'
            except (ValueError, TypeError):
                errors[field] = f'{field} must be a valid number'
    return errors

@require_http_methods(["POST"])
def predict_rain(request):
    """API endpoint for rain prediction"""
    print("=== PREDICTION REQUEST STARTED ===")
    try:
        # Parse JSON data
        print(f"Raw request body: {request.body}")
        data = json.loads(request.body.decode('utf-8'))
        print(f"Parsed JSON data: {data}")
        
        # Validate input data
        print("Starting validation...")
        validation_errors = validate_weather_input(data)
        if validation_errors:
            print(f"Validation errors: {validation_errors}")
            return JsonResponse({
                'error': 'Invalid input data',
                'details': validation_errors
            }, status=400)
        print("Validation passed!")
        
        # Convert to float with additional validation
        try:
            input_data = {
                'temperature': float(data['temperature']),
                'feels_like_max': float(data['feels_like_max']),
                'dew_point': float(data['dew_point']),
                'humidity': float(data['humidity']),
                'sea_level_pressure': float(data['sea_level_pressure']),
                'wind_speed': float(data['wind_speed']),
                'wind_direction': float(data['wind_direction']),
                'cloud_cover': float(data['cloud_cover']),
                'wind_gust': float(data['wind_gust']),
                'visibility': float(data['visibility'])
            }
        except (ValueError, TypeError) as e:
            return JsonResponse({
                'error': 'Invalid numeric values',
                'details': 'All fields must be valid numbers'
            }, status=400)
        
        print(f"Validated input: {input_data}")
          # Make prediction with error handling
        try:
            weather_model = get_weather_model()
            prediction_result = weather_model.predict(input_data)
            print(f"Prediction result: {prediction_result}")
        except Exception as e:
            print(f"Model prediction failed: {str(e)}")
            return JsonResponse({
                'error': 'Model prediction failed',
                'details': 'Unable to process prediction request'
            }, status=500)
        
        # Save to database
        weather_prediction = WeatherPrediction.objects.create(
            temperature=input_data['temperature'],
            feels_like_max=input_data['feels_like_max'],
            dew_point=input_data['dew_point'],
            humidity=input_data['humidity'],
            sea_level_pressure=input_data['sea_level_pressure'],
            wind_speed=input_data['wind_speed'],
            wind_direction=input_data['wind_direction'],
            cloud_cover=input_data['cloud_cover'],
            wind_gust=input_data['wind_gust'],
            visibility=input_data['visibility'],
            rain_probability=prediction_result['rain_probability'],
            prediction_result=prediction_result['prediction_result'],
            confidence=prediction_result['confidence'],
            ip_address=get_client_ip(request)
        )
        
        # Prepare response
        response_data = {
            'rain_probability': prediction_result['rain_probability'],
            'prediction_result': prediction_result['prediction_result'],
            'confidence': prediction_result['confidence'],
            'probability_level': prediction_result['probability_level'],
            'recommendation': prediction_result['recommendation'],
            'input_data': input_data,
            'prediction_id': weather_prediction.id
        }
        
        return JsonResponse(response_data, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return JsonResponse({
            'error': 'Prediction failed',
            'details': 'Internal server error'
        }, status=500)

@require_http_methods(["GET"])
def get_predictions_history(request):
    """Get prediction history"""
    try:
        predictions = WeatherPrediction.objects.all().order_by('-created_at')[:50]
        
        predictions_data = []
        for pred in predictions:
            predictions_data.append({
                'id': pred.id,
                'temperature': pred.temperature,
                'humidity': pred.humidity,
                'sea_level_pressure': pred.sea_level_pressure,
                'wind_speed': pred.wind_speed,
                'rain_probability': pred.rain_probability,
                'prediction_result': pred.prediction_result,
                'created_at': pred.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse(predictions_data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({
            'error': 'Failed to fetch history',
            'details': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_model_info(request):
    """Get model information"""
    model_info = {
        'model_type': '3-Layer Neural Network',
        'architecture': '10 → 5 → 5 → 1',
        'activation_function': 'Sigmoid',
        'loss_function': 'Binary Cross Entropy',
        'optimizer': 'SGD',
        'training_data': {
            'source': 'Cambodia Weather Data',
            'period': '2022-2024',
            'features': 10
        },
        'input_features': [
            'Temperature (°C)',
            'Feels Like Maximum (°C)',
            'Dew Point (°C)',
            'Humidity (%)',
            'Sea Level Pressure (inHg)',
            'Wind Speed (mph)',
            'Wind Direction (degrees)',
            'Visibility (miles)',
            'Cloud Cover (%)',
            'Wind Gust (mph)'
        ]
    }
    return JsonResponse(model_info, status=200)

@require_http_methods(["GET"])
def health_check(request):
    """API health check"""
    try:
        # Test model loading
        test_data = {
            'temperature': 25.0,
            'feels_like_max': 30.0,
            'dew_point': 20.0,
            'humidity': 65.0,
            'sea_level_pressure': 30.0,
            'wind_speed': 10.0,
            'wind_direction': 180.0,
            'cloud_cover': 50.0,
            'wind_gust': 15.0,
            'visibility': 10.0
        }
        weather_model = get_weather_model()
        weather_model.predict(test_data)
        
        return JsonResponse({
            'status': 'healthy',
            'model_loaded': True,
            'message': 'API is working correctly'
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'model_loaded': False,
            'error': str(e)
        }, status=500)
