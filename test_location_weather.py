#!/usr/bin/env python3
"""
Test location-specific weather data
"""

import boto3
import json

def test_location_weather():
    """Test weather data for different locations"""
    lambda_client = boto3.client('lambda')
    
    locations = [
        {'name': 'London', 'coords': {'latitude': 51.5074, 'longitude': -0.1278}},
        {'name': 'Manchester', 'coords': {'latitude': 53.4808, 'longitude': -2.2426}},
        {'name': 'New York', 'coords': {'latitude': 40.7128, 'longitude': -74.0060}},
        {'name': 'Los Angeles', 'coords': {'latitude': 34.0522, 'longitude': -118.2437}}
    ]
    
    print("🌤️ Testing Location-Specific Weather Data")
    print("=" * 50)
    
    for location in locations:
        print(f"\n📍 Testing {location['name']}:")
        print(f"   Coordinates: {location['coords']['latitude']:.4f}, {location['coords']['longitude']:.4f}")
        
        try:
            response = lambda_client.invoke(
                FunctionName='weather-forecast',
                InvocationType='RequestResponse',
                Payload=json.dumps({
                    'action': 'get_forecast',
                    'hours': 24,
                    'location': location['coords']
                })
            )
            
            result = json.loads(response['Payload'].read())
            
            if result.get('statusCode') == 200:
                body = json.loads(result.get('body', '{}'))
                forecast_data = body.get('forecast', [])
                
                if forecast_data:
                    first_forecast = forecast_data[0]
                    print(f"   Temperature: {first_forecast.get('temperature')}°C")
                    print(f"   Cloud Cover: {first_forecast.get('cloud_cover')}%")
                    print(f"   Wind Speed: {first_forecast.get('wind_speed')} m/s")
                    print(f"   Solar Irradiance: {first_forecast.get('solar_irradiance')} W/m²")
                    print(f"   Solar Efficiency: {first_forecast.get('solar_efficiency'):.1%}")
                else:
                    print("   ❌ No forecast data")
            else:
                print(f"   ❌ Lambda error: {result}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_location_weather()

