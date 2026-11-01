from rest_framework import serializers
from .models import WeatherPrediction

class WeatherInputSerializer(serializers.Serializer):
    temperature = serializers.FloatField(min_value=-20.0, max_value=50.0)
    feels_like_max = serializers.FloatField(min_value=-20.0, max_value=60.0)
    dew_point = serializers.FloatField(min_value=-30.0, max_value=40.0)
    humidity = serializers.FloatField(min_value=0.0, max_value=100.0)
    sea_level_pressure = serializers.FloatField(min_value=28.0, max_value=32.0)
    wind_speed = serializers.FloatField(min_value=0.0, max_value=100.0)
    wind_direction = serializers.FloatField(min_value=0.0, max_value=360.0)
    visibility = serializers.FloatField(min_value=0.0, max_value=50.0)
    cloud_cover = serializers.FloatField(min_value=0.0, max_value=100.0)
    wind_gust = serializers.FloatField(min_value=0.0, max_value=150.0)

class WeatherPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherPrediction
        fields = '__all__'
        read_only_fields = ['created_at', 'ip_address']

class PredictionResultSerializer(serializers.Serializer):
    rain_probability = serializers.FloatField()
    prediction_result = serializers.CharField()
    confidence = serializers.FloatField()
    probability_level = serializers.CharField()
    recommendation = serializers.CharField()
    input_data = WeatherInputSerializer()
