"""
AWS Strands Orchestrator for Energy Trading System
This module provides a Strands-based orchestration layer for coordinating
multiple Bedrock agents in the energy trading system.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from strands import Agent, tool
from strands.models import BedrockModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnergyTradingStrandsOrchestrator:
    """
    AWS Strands-based orchestrator for the Energy Trading System.
    Coordinates multiple agents and provides intelligent routing of user queries.
    """
    
    def __init__(self):
        self.model = BedrockModel(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            region="us-east-1"
        )
        self.agent = None
        self.tools = []
        self._setup_tools()
        self._setup_agent()
    
    def _setup_tools(self):
        """Setup tools for the Strands agent"""
        
        @tool
        def get_weather_forecast(location: str = "New York") -> str:
            """
            Get weather forecast for energy trading optimization.
            
            Args:
                location: The location to get weather for (e.g., "London", "Manchester", "New York")
            
            Returns:
                Weather forecast data including temperature, cloud cover, wind speed, and solar irradiance
            """
            try:
                # Call our existing weather Lambda function
                import boto3
                lambda_client = boto3.client('lambda')
                
                payload = {
                    "action": "get_forecast",
                    "hours": 12,
                    "location": self._get_location_coordinates(location)
                }
                
                response = lambda_client.invoke(
                    FunctionName='weather-forecast',
                    InvocationType='RequestResponse',
                    Payload=json.dumps(payload)
                )
                
                result = json.loads(response['Payload'].read())
                
                if result.get('statusCode') == 200:
                    forecast_data = json.loads(result['body'])
                    return self._format_weather_response(forecast_data, location)
                else:
                    return f"Unable to get weather forecast for {location}. Please try again."
                    
            except Exception as e:
                logger.error(f"Error getting weather forecast: {e}")
                return f"Error retrieving weather data for {location}. Please try again."
        
        @tool
        def get_system_status() -> str:
            """
            Get the current system status including agent health, grid stability, and performance metrics.
            
            Returns:
                System status report with health indicators and performance metrics
            """
            try:
                # Simulate system status data
                status_data = {
                    "overall_health": "EXCELLENT",
                    "agents_active": 5,
                    "grid_stability": 99.8,
                    "solar_generation": 450,
                    "grid_demand": 1250,
                    "market_price": 0.083,
                    "battery_storage": 85,
                    "recent_trades": 3
                }
                
                return f"""🤖 **System Status Report:**

🟢 **Overall Health: {status_data['overall_health']}**
• All {status_data['agents_active']} AI agents are active and healthy
• Grid stability: {status_data['grid_stability']}% (excellent)
• No alerts or issues detected

📊 **Current Performance:**
• Solar generation: {status_data['solar_generation']} MW (up 12.5%)
• Grid demand: {status_data['grid_demand']} MW (normal)
• Market price: ${status_data['market_price']:.3f}/kWh (down 2.1%)
• Battery storage: {status_data['battery_storage']}% (optimal)

🔄 **Recent Activity:**
• {status_data['recent_trades']} trades executed in the last hour
• All workflow steps completed successfully

Would you like me to show you more details about any specific area?"""
                
            except Exception as e:
                logger.error(f"Error getting system status: {e}")
                return "Unable to retrieve system status. Please try again."
        
        @tool
        def get_market_analysis() -> str:
            """
            Get current market analysis including price trends and trading recommendations.
            
            Returns:
                Market analysis with price trends and trading recommendations
            """
            try:
                # Simulate market analysis
                analysis = {
                    "current_price": 0.083,
                    "trend": "down",
                    "change_percent": -2.1,
                    "recommendation": "Consider increasing direct sales to grid during peak hours",
                    "volatility": "low"
                }
                
                return f"""💰 **Market Analysis:**

📈 **Current Market Conditions:**
• Current price: ${analysis['current_price']:.3f}/kWh
• Trend: {analysis['trend'].title()} {analysis['change_percent']:.1f}%
• Volatility: {analysis['volatility'].title()}

💡 **Trading Recommendations:**
• {analysis['recommendation']}
• Monitor for optimal production windows
• Consider battery storage optimization

📊 **Market Outlook:**
• Stable conditions expected for next 24 hours
• Solar production opportunities during peak hours
• Grid demand within normal parameters"""
                
            except Exception as e:
                logger.error(f"Error getting market analysis: {e}")
                return "Unable to retrieve market analysis. Please try again."
        
        @tool
        def get_battery_status() -> str:
            """
            Get current battery storage status and optimization recommendations.
            
            Returns:
                Battery status with charge level and optimization recommendations
            """
            try:
                # Simulate battery status
                battery_data = {
                    "charge_level": 85,
                    "status": "optimal",
                    "efficiency": 94.2,
                    "cycles_today": 3,
                    "recommendation": "Continue current charging strategy"
                }
                
                return f"""🔋 **Battery Storage Status:**

⚡ **Current Status:**
• Charge level: {battery_data['charge_level']}% ({battery_data['status']})
• Efficiency: {battery_data['efficiency']}%
• Charge cycles today: {battery_data['cycles_today']}

💡 **Optimization Recommendations:**
• {battery_data['recommendation']}
• Monitor for peak demand periods
• Consider grid export during high-price windows

📊 **Performance Metrics:**
• All systems operating within normal parameters
• No maintenance alerts
• Optimal charging efficiency maintained"""
                
            except Exception as e:
                logger.error(f"Error getting battery status: {e}")
                return "Unable to retrieve battery status. Please try again."
        
        @tool
        def get_grid_status() -> str:
            """
            Get current grid stability and monitoring information.
            
            Returns:
                Grid status with stability metrics and monitoring data
            """
            try:
                # Simulate grid status
                grid_data = {
                    "stability": 99.8,
                    "frequency": 60.02,
                    "voltage": 120.1,
                    "load": 78.5,
                    "status": "stable"
                }
                
                return f"""⚡ **Grid Status Report:**

🔌 **Grid Stability:**
• Overall stability: {grid_data['stability']}% (excellent)
• Frequency: {grid_data['frequency']} Hz (normal)
• Voltage: {grid_data['voltage']} V (optimal)
• Load: {grid_data['load']}% (normal)

📊 **Monitoring Status:**
• Grid status: {grid_data['status'].title()}
• No stability alerts
• All monitoring systems operational
• Demand response systems ready

🔄 **Grid Management:**
• Automatic load balancing active
• Frequency regulation optimal
• Voltage control within parameters"""
                
            except Exception as e:
                logger.error(f"Error getting grid status: {e}")
                return "Unable to retrieve grid status. Please try again."
        
        # Add tools to the list
        self.tools = [
            get_weather_forecast,
            get_system_status,
            get_market_analysis,
            get_battery_status,
            get_grid_status
        ]
    
    def _setup_agent(self):
        """Setup the Strands agent with tools and model"""
        try:
            self.agent = Agent(
                name="EnergyTradingOrchestrator",
                model=self.model,
                tools=self.tools,
                system_prompt="""You are an intelligent Energy Trading System Orchestrator powered by AWS Strands. 
                
Your role is to:
1. Understand user queries about energy trading, weather, system status, market analysis, battery storage, and grid operations
2. Route queries to the appropriate tools and services
3. Provide comprehensive, accurate responses with actionable insights
4. Coordinate between different aspects of the energy trading system

Key capabilities:
- Weather forecasting for solar production optimization
- System health monitoring and status reporting
- Market analysis and trading recommendations
- Battery storage optimization
- Grid stability monitoring

Always provide detailed, helpful responses with relevant data and actionable recommendations. Use emojis and formatting to make responses clear and engaging."""
            )
            logger.info("✅ Strands agent initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing Strands agent: {e}")
            raise
    
    def _get_location_coordinates(self, location: str) -> Dict[str, float]:
        """Get coordinates for a location name"""
        location_map = {
            'london': {'latitude': 51.5074, 'longitude': -0.1278},
            'manchester': {'latitude': 53.4808, 'longitude': -2.2426},
            'new york': {'latitude': 40.7128, 'longitude': -74.0060},
            'new york city': {'latitude': 40.7128, 'longitude': -74.0060},
            'nyc': {'latitude': 40.7128, 'longitude': -74.0060},
            'sydney': {'latitude': -33.8688, 'longitude': 151.2093},
            'los angeles': {'latitude': 34.0522, 'longitude': -118.2437},
            'la': {'latitude': 34.0522, 'longitude': -118.2437}
        }
        
        location_lower = location.lower().strip()
        return location_map.get(location_lower, {'latitude': 40.7128, 'longitude': -74.0060})  # Default to NYC
    
    def _format_weather_response(self, forecast_data: Dict, location: str) -> str:
        """Format weather forecast data for display"""
        try:
            if 'full_forecast' in forecast_data and forecast_data['full_forecast']:
                current = forecast_data['full_forecast'][0]
                source = forecast_data.get('source', 'AWS Weather API')
                
                # Build multi-hour forecast summary
                forecast_summary = ""
                if len(forecast_data['full_forecast']) > 1:
                    forecast_summary = "\n\n📅 **12-Hour Forecast Summary:**\n"
                    for i, hour_data in enumerate(forecast_data['full_forecast'][:12]):
                        hour_time = hour_data.get('timestamp', '').split('T')[1][:5] if hour_data.get('timestamp') else f"+{i}h"
                        temp = hour_data.get('temperature', 0)
                        clouds = hour_data.get('cloud_cover', 0)
                        solar = hour_data.get('solar_irradiance', 0)
                        forecast_summary += f"• {hour_time}: {temp}°C, {clouds}% clouds, {solar} W/m² solar\n"
                
                # Determine conditions quality
                cloud_cover = current.get('cloud_cover', 15)
                if cloud_cover < 20:
                    conditions = "excellent"
                    emoji = "☀️"
                elif cloud_cover < 50:
                    conditions = "good"
                    emoji = "⛅"
                else:
                    conditions = "moderate"
                    emoji = "☁️"
                
                # Calculate solar generation estimate
                irradiance = current.get('solar_irradiance', 920)
                efficiency = current.get('solar_efficiency', 0.85)
                expected_generation = round(irradiance * 0.5 * efficiency, 1)
                
                return f"""🌤️ **Weather Forecast Analysis** ({source})

{emoji} **Current Conditions:**
• Temperature: {current.get('temperature', 24)}°C
• Cloud cover: {current.get('cloud_cover', 15)}% ({conditions} conditions)
• Wind speed: {current.get('wind_speed', 8)} m/s
• Humidity: {current.get('humidity', 65)}%
• Solar irradiance: {current.get('solar_irradiance', 920)} W/m²
• Solar efficiency: {current.get('solar_efficiency', 0.85):.1%}

☀️ **Solar Production Impact:**
• Expected generation: {expected_generation} MW
• Peak efficiency: {current.get('solar_efficiency', 0.85):.1%}
• UV index: {current.get('uv_index', 6)} (moderate)
• Precipitation chance: {current.get('precipitation_probability', 0)}%{forecast_summary}

💡 **Recommendation:**
{'Excellent conditions for solar generation. Consider maximizing production and direct grid sales.' if cloud_cover < 20 else 'Good conditions with some cloud cover. Monitor for optimal production windows.' if cloud_cover < 50 else 'Moderate conditions. Consider battery storage optimization.'}

Would you like me to show more detailed hourly data or adjust the production strategy?"""
            else:
                return f"Weather forecast data for {location} is currently unavailable. Please try again."
                
        except Exception as e:
            logger.error(f"Error formatting weather response: {e}")
            return f"Error processing weather data for {location}. Please try again."
    
    async def process_query(self, user_message: str) -> Dict[str, Any]:
        """
        Process a user query using the Strands agent
        
        Args:
            user_message: The user's message/query
            
        Returns:
            Response dictionary with status and response text
        """
        try:
            logger.info(f"🤖 Processing query with Strands: {user_message}")
            
            if not self.agent:
                raise Exception("Strands agent not initialized")
            
            # Use Strands agent to process the query
            response = await self.agent.invoke_async(user_message)
            
            logger.info(f"✅ Strands response generated successfully")
            
            return {
                'status': 'success',
                'user_message': user_message,
                'response': str(response),
                'source': 'AWS Strands Orchestrator',
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing query with Strands: {e}")
            return {
                'status': 'error',
                'user_message': user_message,
                'response': f"I apologize, but I encountered an error processing your request: {str(e)}. Please try again.",
                'source': 'AWS Strands Orchestrator (Error)',
                'timestamp': time.time()
            }

# Global orchestrator instance
strands_orchestrator = None

def get_strands_orchestrator() -> EnergyTradingStrandsOrchestrator:
    """Get or create the global Strands orchestrator instance"""
    global strands_orchestrator
    if strands_orchestrator is None:
        strands_orchestrator = EnergyTradingStrandsOrchestrator()
    return strands_orchestrator

async def process_strands_query(user_message: str) -> Dict[str, Any]:
    """Process a query using the Strands orchestrator"""
    orchestrator = get_strands_orchestrator()
    return await orchestrator.process_query(user_message)

if __name__ == "__main__":
    # Test the Strands orchestrator
    async def test_strands():
        orchestrator = EnergyTradingStrandsOrchestrator()
        
        test_queries = [
            "What's the weather forecast for Manchester?",
            "What is the system status?",
            "Show me the market analysis",
            "How are the batteries performing?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing: {query}")
            result = await orchestrator.process_query(query)
            print(f"✅ Response: {result['response'][:200]}...")
    
    asyncio.run(test_strands())
