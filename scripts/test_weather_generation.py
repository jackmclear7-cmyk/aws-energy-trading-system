#!/usr/bin/env python3
"""
Test script to debug weather generation with target dates
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from weather_lambda_function import generate_realistic_weather_data
from datetime import datetime, timedelta

def test_weather_generation():
    """Test the weather generation with target dates"""
    
    # Test location (Manchester)
    location = {'latitude': 53.4808, 'longitude': -2.2426}
    
    # Test current time
    current_time = datetime.now()
    print(f"Current time: {current_time}")
    
    # Test target date (Friday)
    target_date = current_time + timedelta(days=2)  # Friday
    print(f"Target date: {target_date}")
    
    print("\n" + "="*50)
    print("Testing weather generation with target date...")
    print("="*50)
    
    # Generate weather for target date
    forecast_data = generate_realistic_weather_data(
        location=location,
        hours=12,
        target_datetime=target_date,
        target_time=None
    )
    
    print(f"\nGenerated {len(forecast_data)} forecast entries:")
    for i, forecast in enumerate(forecast_data[:5]):  # Show first 5
        timestamp = forecast.get('timestamp', 'N/A')
        temp = forecast.get('temperature', 0)
        clouds = forecast.get('cloud_cover', 0)
        print(f"  {i+1}. {timestamp} - {temp}°C, {clouds}% clouds")
    
    print(f"\nFirst forecast timestamp: {forecast_data[0].get('timestamp')}")
    print(f"Target date was: {target_date}")

if __name__ == "__main__":
    test_weather_generation()

