"""
URL configuration for rain_prediction_project project.
"""
from django.contrib import admin
from django.urls import path, include
from prediction_api.views import home_view, model_info_view
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('prediction_api.urls')),
    path('test/', TemplateView.as_view(template_name='test.html'), name='test'),
    path('model/', model_info_view, name='model_info'),
    path('', home_view, name='home'),
]
