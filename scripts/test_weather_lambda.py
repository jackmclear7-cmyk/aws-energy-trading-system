"""
Test the Weather Lambda Function
"""

import boto3
import json
import time

def test_weather_lambda():
    """Test the weather Lambda function"""
    print("🧪 Testing Weather Lambda Function")
    print("=" * 40)
    
    # Initialize Lambda client
    lambda_client = boto3.client('lambda')
    
    # Test payload
    test_payload = {
        'action': 'get_forecast',
        'hours': 24,
        'location': {
            'latitude': 40.7128,
            'longitude': -74.0060
        }
    }
    
    try:
        print("📡 Invoking weather-forecast Lambda function...")
        
        response = lambda_client.invoke(
            FunctionName='weather-forecast',
            InvocationType='RequestResponse',
            Payload=json.dumps(test_payload)
        )
        
        # Parse response
        result = json.loads(response['Payload'].read())
        
        print(f"✅ Lambda function response:")
        print(f"Status Code: {result.get('statusCode')}")
        
        if result.get('statusCode') == 200:
            body = json.loads(result.get('body', '{}'))
            print(f"✅ Success! Weather data received")
            print(f"📊 Forecast data points: {len(body.get('forecast', []))}")
            
            # Show first forecast
            forecast = body.get('forecast', [])
            if forecast:
                first_forecast = forecast[0]
                print(f"\n🌤️ Sample Forecast Data:")
                print(f"• Temperature: {first_forecast.get('temperature')}°C")
                print(f"• Cloud Cover: {first_forecast.get('cloud_cover')}%")
                print(f"• Solar Irradiance: {first_forecast.get('solar_irradiance')} W/m²")
                print(f"• Solar Efficiency: {first_forecast.get('solar_efficiency'):.1%}")
            
            return True
        else:
            print(f"❌ Lambda function error: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Lambda function: {e}")
        return False

def test_chatbot_integration():
    """Test the chatbot integration with the weather Lambda"""
    print("\n🤖 Testing Chatbot Integration")
    print("=" * 40)
    
    try:
        # Import the chatbot integration
        import sys
        sys.path.append('.')
        from scripts.chatbot_bedrock_integration import ChatbotBedrockIntegration
        
        # Create integration instance
        integration = ChatbotBedrockIntegration()
        
        # Test weather forecast
        print("📡 Testing weather forecast integration...")
        result = integration.get_weather_forecast()
        
        if result.get('status') == 'success':
            print("✅ Chatbot integration successful!")
            print(f"📊 Source: {result.get('source')}")
            
            forecast = result.get('forecast', {})
            print(f"\n🌤️ Weather Data:")
            print(f"• Temperature: {forecast.get('temperature')}°C")
            print(f"• Cloud Cover: {forecast.get('cloud_cover')}%")
            print(f"• Solar Irradiance: {forecast.get('solar_irradiance')} W/m²")
            print(f"• Solar Efficiency: {forecast.get('solar_efficiency'):.1%}")
            
            return True
        else:
            print(f"❌ Chatbot integration failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing chatbot integration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Weather Lambda Integration Test")
    print("=" * 50)
    
    # Test Lambda function
    lambda_success = test_weather_lambda()
    
    # Test chatbot integration
    chatbot_success = test_chatbot_integration()
    
    print("\n📋 Test Results:")
    print("=" * 20)
    print(f"Lambda Function: {'✅ PASS' if lambda_success else '❌ FAIL'}")
    print(f"Chatbot Integration: {'✅ PASS' if chatbot_success else '❌ FAIL'}")
    
    if lambda_success and chatbot_success:
        print("\n🎉 All tests passed! Weather integration is working!")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")

