import torch
import joblib
import numpy as np
import os
from django.conf import settings

class WeatherPredictionModel:
    def __init__(self):
        self.model_params = None
        self.training_stats = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model and statistics"""
        try:
            model_path = os.path.join(settings.MODEL_FILES_PATH, 'rainNueralNetwork.joblib')
            stats_path = os.path.join(settings.MODEL_FILES_PATH, 'training_stats.joblib')
            self.model_params = joblib.load(model_path)
            self.training_stats = joblib.load(stats_path)
            print("Model and training statistics loaded successfully!")
        except FileNotFoundError as e:
            print(f"Model files not found: {e}")
            raise e
    
    def neural_network_model(self, X, W1, b1, W2, b2, W3, b3):
        """3-layer neural network model"""
        # Layer 1
        Z1 = torch.matmul(X, W1) + b1
        A1 = torch.sigmoid(Z1)
        
        # Layer 2
        Z2 = torch.matmul(A1, W2) + b2
        A2 = torch.sigmoid(Z2)
        
        # Layer 3
        Z3 = torch.matmul(A2, W3) + b3
        output = torch.sigmoid(Z3)
        
        return output
    def predict(self, input_data):
        """Make prediction based on input weather data"""
        print(f"=== MODEL PREDICTION STARTED ===")
        print(f"Input data received: {input_data}")
        
        # Force garbage collection to prevent memory issues
        import gc
        gc.collect()
        
        try:
            if self.model_params is None or self.training_stats is None:
                print("ERROR: Model not loaded properly")
                raise ValueError("Model not loaded properly")
            
            print("Model params loaded successfully")
            
            # Convert input to numpy array (10 features - including visibility)
            # Create a fresh copy to avoid any state issues
            features = np.array([[
                float(input_data['temperature']),
                float(input_data['feels_like_max']),
                float(input_data['dew_point']),
                float(input_data['humidity']),
                float(input_data['sea_level_pressure']),
                float(input_data['wind_speed']),
                float(input_data['wind_direction']),
                float(input_data['visibility']),
                float(input_data['cloud_cover']),
                float(input_data['wind_gust'])
            ]], dtype=np.float32)
            
            print(f"Features array shape: {features.shape}")
            print(f"Features array: {features}")
            
            # Scale the input using training statistics - create fresh copies
            mean_values = (self.training_stats['mean'].values.copy() 
                          if hasattr(self.training_stats['mean'], 'values') 
                          else np.array(self.training_stats['mean'], dtype=np.float32).copy())
            std_values = (self.training_stats['std'].values.copy() 
                         if hasattr(self.training_stats['std'], 'values') 
                         else np.array(self.training_stats['std'], dtype=np.float32).copy())
            
            print(f"Mean values: {mean_values}")
            print(f"Std values: {std_values}")
            
            # Ensure we have fresh arrays for scaling to avoid in-place modifications
            features_copy = features.copy()
            scaled_input = (features_copy - mean_values) / std_values
            print(f"Scaled input: {scaled_input}")
            
            # Convert to tensor with explicit copying and ensure no gradients
            input_tensor = torch.tensor(scaled_input.copy(), dtype=torch.float32, requires_grad=False)
            print(f"Input tensor shape: {input_tensor.shape}")
            
            # Make prediction with no_grad to prevent gradient accumulation
            with torch.no_grad():
                print("Making prediction with neural network...")
                # Create fresh copies of model parameters to avoid any modification
                W1 = self.model_params['W1'].clone().detach().requires_grad_(False)
                b1 = self.model_params['b1'].clone().detach().requires_grad_(False)
                W2 = self.model_params['W2'].clone().detach().requires_grad_(False)
                b2 = self.model_params['b2'].clone().detach().requires_grad_(False)
                W3 = self.model_params['W3'].clone().detach().requires_grad_(False)
                b3 = self.model_params['b3'].clone().detach().requires_grad_(False)
                
                prediction = self.neural_network_model(
                    input_tensor, W1, b1, W2, b2, W3, b3
                )
                
                rain_probability = float(prediction.item())
                print(f"Raw prediction: {rain_probability}")
            
            # Clear any potential tensor references
            del input_tensor, W1, b1, W2, b2, W3, b3, prediction
            
            # Generate results
            prediction_result = "Rain Expected" if rain_probability >= 0.5 else "No Rain Expected"
            confidence = max(rain_probability, 1 - rain_probability) * 100
            
            # Determine probability level
            if rain_probability >= 0.7:
                probability_level = "High"
            elif rain_probability >= 0.4:
                probability_level = "Medium"
            else:
                probability_level = "Low"
            
            # Generate recommendation
            if rain_probability >= 0.8:
                recommendation = "VERY HIGH CHANCE OF RAIN - Indoor activities recommended or heavy rain gear required"
            elif rain_probability >= 0.6:
                recommendation = "HIGH CHANCE OF RAIN - Bring umbrella and rain protection"
            elif rain_probability >= 0.4:
                recommendation = "MODERATE CHANCE OF RAIN - Consider bringing light rain gear"
            elif rain_probability >= 0.2:
                recommendation = "LOW CHANCE OF RAIN - Generally clear weather expected"
            else:
                recommendation = "EXCELLENT WEATHER CONDITIONS - Ideal for outdoor activities"
            
            result = {
                'rain_probability': rain_probability * 100,  # Convert to percentage
                'prediction_result': prediction_result,
                'confidence': confidence,
                'probability_level': probability_level,
                'recommendation': recommendation
            }
            
            print(f"Final prediction result: {result}")
            print("=== MODEL PREDICTION COMPLETED ===")
            return result
            
        except Exception as e:
            print(f"Error during prediction: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return a safe default response instead of crashing
            return {
                'rain_probability': 0.0,
                'prediction_result': "Failed Prediction",
                'confidence': 0.0,
                'probability_level': "Unknown",
                'recommendation': "Unable to make prediction - please try again"
            }

# Thread-safe singleton instance
_weather_model = None
_model_lock = None

def get_weather_model():
    """Get or create the weather model instance (thread-safe)"""
    global _weather_model, _model_lock
    
    if _model_lock is None:
        import threading
        _model_lock = threading.Lock()
    
    if _weather_model is None:
        with _model_lock:
            # Double-check locking pattern
            if _weather_model is None:
                print("Creating new WeatherPredictionModel instance...")
                _weather_model = WeatherPredictionModel()
                print("WeatherPredictionModel instance created successfully")
    
    return _weather_model
