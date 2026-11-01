from django.db import models
from django.utils import timezone

class WeatherPrediction(models.Model):
    # Input parameters
    temperature = models.FloatField()
    feels_like_max = models.FloatField()
    dew_point = models.FloatField()
    humidity = models.FloatField()
    sea_level_pressure = models.FloatField()
    wind_speed = models.FloatField()
    wind_direction = models.FloatField()
    visibility = models.FloatField()
    cloud_cover = models.FloatField()
    wind_gust = models.FloatField()
    
    # Prediction results
    rain_probability = models.FloatField()
    prediction_result = models.CharField(max_length=50)
    confidence = models.FloatField()
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Rain Prediction - {self.rain_probability:.2%} at {self.created_at}"
