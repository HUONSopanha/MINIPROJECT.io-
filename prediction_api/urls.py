from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.predict_rain, name='predict_rain'),
    path('history/', views.get_predictions_history, name='predictions_history'),
    path('model-info/', views.get_model_info, name='model_info'),
    path('health/', views.health_check, name='health_check'),
]
