"""
AWS Weather Lambda Function for MCP Integration
This function provides real weather data for the energy trading system
"""

import json
import boto3
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Lambda handler for weather forecast requests
    """
    try:
        logger.info(f"Weather Lambda invoked with event: {event}")
        
        # Parse the request
        action = event.get('action', 'get_forecast')
        hours = event.get('hours', 24)
        location = event.get('location', {'latitude': 40.7128, 'longitude': -74.0060})  # NYC default
        target_date = event.get('target_date')  # ISO format date string
        target_time = event.get('target_time')  # Time period like 'morning', 'afternoon'
        
        if action == 'get_forecast':
            return get_weather_forecast(location, hours, target_date, target_time)
        elif action == 'get_current':
            return get_current_weather(location)
        elif action == 'get_solar_forecast':
            return get_solar_forecast(location, hours)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid action',
                    'available_actions': ['get_forecast', 'get_current', 'get_solar_forecast']
                })
            }
            
    except Exception as e:
        logger.error(f"Error in weather lambda: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to get weather data'
            })
        }

def get_weather_forecast(location: Dict, hours: int, target_date: str = None, target_time: str = None) -> Dict:
    """
    Get weather forecast using OpenWeatherMap API
    """
    try:
        current_time = datetime.now()
        
        # Parse target date if provided
        target_datetime = None
        if target_date:
            try:
                target_datetime = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                logger.info(f"Target date requested: {target_datetime}")
            except Exception as e:
                logger.warning(f"Invalid target date format: {target_date}, error: {e}")
        
        # Try to get real weather data from OpenWeatherMap
        # Note: In production, you would use a real API key
        api_key = os.environ.get('OPENWEATHER_API_KEY', 'demo_key')
        
        if api_key == 'demo_key':
            # Use realistic simulated data for demo
            logger.info("Using simulated weather data for demo - NOT REAL WEATHER DATA")
            forecast_data = generate_realistic_weather_data(location, hours, target_datetime, target_time)
            source = "Simulated Weather Data (Demo - Not Real)"
        else:
            # Use real OpenWeatherMap API
            try:
                forecast_data = get_real_weather_data(location, hours, api_key)
                source = "OpenWeatherMap API (Real Weather Data)"
            except Exception as api_error:
                logger.warning(f"Real API failed, using simulated data: {api_error}")
                forecast_data = generate_realistic_weather_data(location, hours, target_datetime, target_time)
                source = "Simulated Weather Data (API Failed)"
        
        # Store forecast in DynamoDB for caching
        try:
            table = dynamodb.Table('weather-forecast-cache')
            table.put_item(
                Item={
                    'location': f"{location['latitude']},{location['longitude']}",
                    'timestamp': current_time.isoformat(),
                    'forecast': forecast_data,
                    'ttl': int((current_time + timedelta(hours=1)).timestamp())
                }
            )
        except Exception as e:
            logger.warning(f"Failed to cache weather data: {e}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'location': location,
                'forecast_hours': hours,
                'forecast': forecast_data,
                'generated_at': current_time.isoformat(),
                'source': source
            })
        }
        
    except Exception as e:
        logger.error(f"Error getting weather forecast: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to get weather forecast'
            })
        }

def generate_realistic_weather_data(location: Dict, hours: int, target_datetime: datetime = None, target_time: str = None) -> list:
    """Generate realistic weather data for demo purposes with location awareness"""
    current_time = datetime.now()
    forecast_data = []
    
    # Get location coordinates
    lat = location.get('latitude', 40.7128)
    lon = location.get('longitude', -74.0060)
    
    # Define location-specific weather patterns
    location_weather = get_location_weather_profile(lat, lon)
    
    # If target date is specified, adjust the forecast to focus on that date
    start_time = current_time
    if target_datetime:
        # Calculate hours until target date
        hours_until_target = int((target_datetime - current_time).total_seconds() / 3600)
        if hours_until_target > 0:
            # Start forecast from target date
            start_time = target_datetime
            hours = min(hours, 24)  # Focus on the target day
            logger.info(f"Generating forecast for target date: {target_datetime}, starting from: {start_time}")
        else:
            logger.info(f"Target date is in the past or today, using current time")
    else:
        logger.info(f"No target date specified, using current time: {current_time}")
    
    logger.info(f"Final start_time: {start_time}, hours: {hours}")
    
    for i in range(min(hours, 48)):  # Max 48 hours
        forecast_time = start_time + timedelta(hours=i)
        
        # Debug logging for target date
        if target_datetime and i == 0:
            logger.info(f"First forecast timestamp: {forecast_time}, Target date: {target_datetime}")
        
        # Generate realistic weather patterns based on time of day and location
        hour_of_day = forecast_time.hour
        
        # Temperature varies by time of day and location
        base_temp = location_weather['base_temp'] + 10 * (1 + 0.5 * (1 + (hour_of_day - 12) / 12))
        temperature = round(base_temp + (i % 24) * 0.3 + location_weather['temp_variation'], 1)
        
        # Cloud cover varies by time, day, and location
        cloud_cover = max(0, min(100, 
            location_weather['base_cloud_cover'] + 
            (i % 12) * 3 + 
            (hour_of_day % 8) * 2 + 
            location_weather['cloud_variation']
        ))
        
        # Wind speed varies by location and time
        wind_speed = round(
            location_weather['base_wind'] + 
            (i % 8) * 1.2 + 
            (hour_of_day % 6) * 0.5 + 
            location_weather['wind_variation'], 1
        )
        
        # Solar irradiance depends on time of day, cloud cover, and location
        if 6 <= hour_of_day <= 18:  # Daylight hours
            solar_factor = max(0, 1 - abs(hour_of_day - 12) / 6)
            base_irradiance = location_weather['base_solar'] * solar_factor
        else:
            base_irradiance = 0
        
        solar_irradiance = max(0, base_irradiance * (1 - cloud_cover / 100))
        solar_efficiency = max(0.3, 1.0 - (cloud_cover / 120))
        
        forecast_data.append({
            'timestamp': forecast_time.isoformat(),
            'temperature': temperature,
            'cloud_cover': round(cloud_cover, 1),
            'wind_speed': wind_speed,
            'humidity': round(55 + (i % 25), 1),
            'pressure': round(1013 + (i % 15) - 7, 1),
            'visibility': round(max(5, 15 - (cloud_cover / 15)), 1),
            'uv_index': max(0, min(11, 3 + (hour_of_day - 6) * 0.5 if 6 <= hour_of_day <= 18 else 0)),
            'precipitation_probability': max(0, min(100, cloud_cover * 0.6)),
            'solar_irradiance': round(solar_irradiance, 1),
            'solar_efficiency': round(solar_efficiency, 3)
        })
    
    return forecast_data

def get_location_weather_profile(lat: float, lon: float) -> Dict:
    """Get location-specific weather profile based on coordinates"""
    
    # Define weather profiles for different regions
    # London, UK
    if 51.0 <= lat <= 52.0 and -1.0 <= lon <= 1.0:
        return {
            'base_temp': 12,  # Cooler base temperature
            'temp_variation': -2,  # Generally cooler
            'base_cloud_cover': 65,  # More cloudy
            'cloud_variation': 10,  # Higher cloud variation
            'base_wind': 8,  # Windier
            'wind_variation': 3,  # More wind variation
            'base_solar': 800,  # Lower solar irradiance
            'location_name': 'London, UK'
        }
    
    # Manchester, UK
    elif 53.0 <= lat <= 54.0 and -3.0 <= lon <= -1.0:
        return {
            'base_temp': 10,  # Even cooler
            'temp_variation': -3,  # Cooler than London
            'base_cloud_cover': 75,  # Very cloudy
            'cloud_variation': 15,  # High cloud variation
            'base_wind': 10,  # Very windy
            'wind_variation': 4,  # High wind variation
            'base_solar': 700,  # Lower solar irradiance
            'location_name': 'Manchester, UK'
        }
    
    # New York, USA
    elif 40.0 <= lat <= 41.0 and -75.0 <= lon <= -73.0:
        return {
            'base_temp': 15,  # Moderate temperature
            'temp_variation': 0,  # Standard variation
            'base_cloud_cover': 45,  # Moderate cloud cover
            'cloud_variation': 8,  # Moderate variation
            'base_wind': 6,  # Moderate wind
            'wind_variation': 2,  # Moderate wind variation
            'base_solar': 950,  # Good solar irradiance
            'location_name': 'New York, USA'
        }
    
    # Los Angeles, USA
    elif 33.0 <= lat <= 35.0 and -119.0 <= lon <= -117.0:
        return {
            'base_temp': 20,  # Warmer
            'temp_variation': 3,  # Warmer variation
            'base_cloud_cover': 25,  # Less cloudy
            'cloud_variation': 5,  # Lower cloud variation
            'base_wind': 4,  # Less windy
            'wind_variation': 1,  # Lower wind variation
            'base_solar': 1100,  # High solar irradiance
            'location_name': 'Los Angeles, USA'
        }
    
    # Sydney, Australia
    elif -34.0 <= lat <= -33.0 and 150.0 <= lon <= 152.0:
        return {
            'base_temp': 18,  # Moderate temperature
            'temp_variation': 2,  # Moderate variation
            'base_cloud_cover': 40,  # Moderate cloud cover
            'cloud_variation': 7,  # Moderate variation
            'base_wind': 7,  # Moderate wind
            'wind_variation': 2,  # Moderate wind variation
            'base_solar': 1000,  # Good solar irradiance
            'location_name': 'Sydney, Australia'
        }
    
    # Default profile (unknown location)
    else:
        return {
            'base_temp': 15,  # Default temperature
            'temp_variation': 0,  # No variation
            'base_cloud_cover': 50,  # Default cloud cover
            'cloud_variation': 10,  # Default variation
            'base_wind': 6,  # Default wind
            'wind_variation': 2,  # Default wind variation
            'base_solar': 900,  # Default solar irradiance
            'location_name': f'Location ({lat:.2f}, {lon:.2f})'
        }

def get_real_weather_data(location: Dict, hours: int, api_key: str) -> list:
    """Get real weather data from OpenWeatherMap API"""
    import requests
    
    lat = location.get('latitude', 40.7128)
    lon = location.get('longitude', -74.0060)
    
    try:
        # OpenWeatherMap One Call API 2.5 (free tier compatible)
        url = f"https://api.openweathermap.org/data/2.5/onecall"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': 'metric',
            'exclude': 'minutely,alerts'
        }
        
        logger.info(f"Making API request to: {url}")
        logger.info(f"API key (first 8 chars): {api_key[:8]}...")
        
        response = requests.get(url, params=params, timeout=10)
        logger.info(f"API response status: {response.status_code}")
        
        if response.status_code == 401:
            logger.error("API key unauthorized - may need activation (up to 2 hours)")
            raise Exception("API key unauthorized - may need activation (up to 2 hours)")
        elif response.status_code == 403:
            logger.error("API key forbidden - check subscription")
            raise Exception("API key forbidden - check subscription")
        
        response.raise_for_status()
        
        data = response.json()
        
        # Process the real weather data
        forecast_data = []
        current_time = datetime.now()
        
        # Current weather
        current = data.get('current', {})
        forecast_data.append({
            'timestamp': current_time.isoformat(),
            'temperature': round(current.get('temp', 20), 1),
            'cloud_cover': current.get('clouds', 0),
            'wind_speed': round(current.get('wind_speed', 0), 1),
            'humidity': current.get('humidity', 50),
            'pressure': current.get('pressure', 1013),
            'visibility': round(current.get('visibility', 10000) / 1000, 1),
            'uv_index': current.get('uvi', 0),
            'precipitation_probability': current.get('pop', 0) * 100,
            'solar_irradiance': max(0, current.get('uvi', 0) * 25),  # Rough conversion
            'solar_efficiency': max(0.3, 1.0 - (current.get('clouds', 0) / 120))
        })
        
        # Hourly forecast
        hourly_data = data.get('hourly', [])
        for i, hour_data in enumerate(hourly_data[:min(hours-1, 48)]):
            forecast_time = current_time + timedelta(hours=i+1)
            forecast_data.append({
                'timestamp': forecast_time.isoformat(),
                'temperature': round(hour_data.get('temp', 20), 1),
                'cloud_cover': hour_data.get('clouds', 0),
                'wind_speed': round(hour_data.get('wind_speed', 0), 1),
                'humidity': hour_data.get('humidity', 50),
                'pressure': hour_data.get('pressure', 1013),
                'visibility': round(hour_data.get('visibility', 10000) / 1000, 1),
                'uv_index': hour_data.get('uvi', 0),
                'precipitation_probability': hour_data.get('pop', 0) * 100,
                'solar_irradiance': max(0, hour_data.get('uvi', 0) * 25),
                'solar_efficiency': max(0.3, 1.0 - (hour_data.get('clouds', 0) / 120))
            })
        
        logger.info(f"Successfully retrieved real weather data: {len(forecast_data)} entries")
        return forecast_data
        
    except Exception as e:
        logger.error(f"Failed to get real weather data: {e}")
        raise Exception(f"Real weather API failed: {e}")

def get_current_weather(location: Dict) -> Dict:
    """
    Get current weather conditions
    """
    try:
        current_time = datetime.now()
        
        # Generate current weather data
        current_weather = {
            'timestamp': current_time.isoformat(),
            'temperature': 24.5,
            'cloud_cover': 15.0,
            'wind_speed': 8.2,
            'humidity': 65.0,
            'pressure': 1013.2,
            'visibility': 10.0,
            'uv_index': 6,
            'precipitation_probability': 5.0,
            'solar_irradiance': 920.0,
            'solar_efficiency': 0.85,
            'weather_condition': 'Partly Cloudy',
            'feels_like': 26.0
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'location': location,
                'current_weather': current_weather,
                'generated_at': current_time.isoformat(),
                'source': 'AWS Weather API (simulated)'
            })
        }
        
    except Exception as e:
        logger.error(f"Error getting current weather: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to get current weather'
            })
        }

def get_solar_forecast(location: Dict, hours: int) -> Dict:
    """
    Get solar-specific forecast for energy generation
    """
    try:
        current_time = datetime.now()
        solar_data = []
        
        for i in range(min(hours, 24)):  # Max 24 hours for solar
            forecast_time = current_time + timedelta(hours=i)
            hour = forecast_time.hour
            
            # Solar generation is highest during daylight hours
            if 6 <= hour <= 18:  # Daylight hours
                # Peak generation around noon
                solar_factor = max(0, 1 - abs(hour - 12) / 6)
                base_irradiance = 1000 * solar_factor
                efficiency = 0.85 * solar_factor
            else:
                base_irradiance = 0
                efficiency = 0
            
            # Add some variation for cloud cover
            cloud_factor = 1 - (15 + (i % 8) * 5) / 100
            final_irradiance = base_irradiance * cloud_factor
            final_efficiency = efficiency * cloud_factor
            
            solar_data.append({
                'timestamp': forecast_time.isoformat(),
                'solar_irradiance': round(final_irradiance, 1),
                'solar_efficiency': round(final_efficiency, 3),
                'expected_generation_mw': round(final_irradiance * 0.5, 1),  # 0.5 MW per 1000 W/m²
                'cloud_cover': round(15 + (i % 8) * 5, 1),
                'daylight_hours': 6 <= hour <= 18
            })
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'location': location,
                'solar_forecast_hours': hours,
                'solar_data': solar_data,
                'generated_at': current_time.isoformat(),
                'source': 'AWS Weather API (simulated)'
            })
        }
        
    except Exception as e:
        logger.error(f"Error getting solar forecast: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to get solar forecast'
            })
        }

# For local testing
if __name__ == "__main__":
    # Test the function locally
    test_event = {
        'action': 'get_forecast',
        'hours': 24,
        'location': {'latitude': 40.7128, 'longitude': -74.0060}
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
