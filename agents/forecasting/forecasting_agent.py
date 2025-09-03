"""
Forecasting Agent for Energy Trading System

This agent is responsible for predicting energy supply and demand using ML models
and external data sources. It communicates forecasts to other agents via A2A.
"""

import asyncio
import json
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from ..base_agent import BaseAgent, AgentConfig, AgentMessage


class ForecastingAgentConfig(AgentConfig):
    """Configuration specific to the Forecasting Agent."""
    forecast_horizon_hours: int = 24
    update_interval_minutes: int = 15
    confidence_threshold: float = 0.7
    ml_model_endpoint: str = "energy-forecasting-model"
    weather_api_tool: str = "weather-forecast"
    historical_data_tool: str = "historical-energy-data"


class ForecastingAgent(BaseAgent):
    """
    Forecasting Agent that predicts energy supply and demand.
    
    Uses ML models and external data to generate forecasts and communicates
    them to other agents in the system.
    """

    def __init__(self, config: ForecastingAgentConfig):
        super().__init__(config)
        self.forecast_config = config
        
        # Forecasting state
        self.current_forecast: Optional[Dict[str, Any]] = None
        self.forecast_history: List[Dict[str, Any]] = []
        self.last_forecast_update: Optional[datetime] = None
        
        # ML model state
        self.model_loaded = False
        self.model_performance_metrics: Dict[str, float] = {}
        
        # External data sources
        self.weather_data: Optional[Dict[str, Any]] = None
        self.historical_data: Optional[pd.DataFrame] = None
        
        self.logger.info("Forecasting Agent initialized", config=config.dict())

    async def _start_agent_specific(self):
        """Start forecasting-specific tasks."""
        # Load ML model
        await self._load_ml_model()
        
        # Start forecasting loop
        asyncio.create_task(self._forecasting_loop())
        
        # Start data ingestion loop
        asyncio.create_task(self._data_ingestion_loop())
        
        self.logger.info("Forecasting Agent started")

    async def _stop_agent_specific(self):
        """Stop forecasting-specific tasks."""
        self.logger.info("Forecasting Agent stopped")

    async def _load_ml_model(self):
        """Load the ML forecasting model."""
        try:
            # In a real implementation, this would load a SageMaker model
            # For now, we'll simulate model loading
            self.model_loaded = True
            self.logger.info("ML model loaded successfully")
            
        except Exception as e:
            self.logger.error("Failed to load ML model", error=str(e))
            self.model_loaded = False

    async def _forecasting_loop(self):
        """Main forecasting loop that runs periodically."""
        while self.is_running:
            try:
                # Generate new forecast
                await self._generate_forecast()
                
                # Broadcast forecast to other agents
                await self._broadcast_forecast()
                
                # Store forecast in Timestream
                await self._store_forecast_data()
                
                # Wait for next update
                await asyncio.sleep(self.forecast_config.update_interval_minutes * 60)
                
            except Exception as e:
                self.logger.error("Error in forecasting loop", error=str(e))
                await asyncio.sleep(60)  # Wait before retrying

    async def _data_ingestion_loop(self):
        """Loop for ingesting external data sources."""
        while self.is_running:
            try:
                # Fetch weather data
                await self._fetch_weather_data()
                
                # Fetch historical energy data
                await self._fetch_historical_data()
                
                # Wait before next update
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error("Error in data ingestion loop", error=str(e))
                await asyncio.sleep(60)

    async def _generate_forecast(self):
        """Generate a new energy forecast."""
        try:
            if not self.model_loaded:
                self.logger.warning("ML model not loaded, using fallback forecasting")
                forecast = await self._generate_fallback_forecast()
            else:
                forecast = await self._generate_ml_forecast()
            
            # Add metadata
            forecast['timestamp'] = datetime.now(timezone.utc).isoformat()
            forecast['agent_id'] = self.agent_id
            forecast['confidence_score'] = self._calculate_confidence(forecast)
            
            # Update current forecast
            self.current_forecast = forecast
            self.forecast_history.append(forecast)
            self.last_forecast_update = datetime.now(timezone.utc)
            
            # Keep only recent forecasts
            if len(self.forecast_history) > 100:
                self.forecast_history = self.forecast_history[-100:]
            
            self.logger.info("New forecast generated", 
                           forecast_id=forecast.get('forecast_id'),
                           confidence=forecast.get('confidence_score'))
            
        except Exception as e:
            self.logger.error("Error generating forecast", error=str(e))
            # Use last known forecast if available
            if self.current_forecast:
                self.logger.info("Using previous forecast due to error")

    async def _generate_ml_forecast(self) -> Dict[str, Any]:
        """Generate forecast using ML model."""
        try:
            # Prepare input data
            input_data = await self._prepare_forecast_inputs()
            
            # Call ML model via MCP
            model_response = await self.call_mcp_tool(
                self.forecast_config.ml_model_endpoint,
                {
                    'input_data': input_data,
                    'forecast_horizon': self.forecast_config.forecast_horizon_hours,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            )
            
            # Process model response
            forecast = {
                'forecast_id': f"fc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'supply_forecast': model_response.get('supply_forecast', {}),
                'demand_forecast': model_response.get('demand_forecast', {}),
                'price_forecast': model_response.get('price_forecast', {}),
                'weather_factors': model_response.get('weather_factors', {}),
                'model_version': model_response.get('model_version', 'unknown'),
                'generation_method': 'ml_model'
            }
            
            return forecast
            
        except Exception as e:
            self.logger.error("Error in ML forecasting", error=str(e))
            # Fall back to statistical forecasting
            return await self._generate_fallback_forecast()

    async def _generate_fallback_forecast(self) -> Dict[str, Any]:
        """Generate forecast using statistical methods when ML model fails."""
        try:
            # Simple time-series forecasting using historical patterns
            if self.historical_data is not None and not self.historical_data.empty:
                forecast = await self._statistical_forecast()
            else:
                forecast = await self._baseline_forecast()
            
            forecast['generation_method'] = 'statistical_fallback'
            return forecast
            
        except Exception as e:
            self.logger.error("Error in fallback forecasting", error=str(e))
            return await self._baseline_forecast()

    async def _statistical_forecast(self) -> Dict[str, Any]:
        """Generate forecast using statistical methods."""
        # Simple moving average with seasonal adjustment
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        
        # Get historical data for similar time periods
        similar_data = self.historical_data[
            (self.historical_data['hour'] == current_hour) &
            (self.historical_data['day_of_week'] == current_day)
        ]
        
        if len(similar_data) > 0:
            # Calculate baseline from historical data
            baseline_supply = similar_data['supply'].mean()
            baseline_demand = similar_data['demand'].mean()
            baseline_price = similar_data['price'].mean()
            
            # Apply weather adjustments
            weather_adjustment = self._calculate_weather_adjustment()
            
            forecast = {
                'forecast_id': f"fc_stat_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'supply_forecast': {
                    'baseline': baseline_supply,
                    'weather_adjusted': baseline_supply * weather_adjustment,
                    'confidence_interval': [baseline_supply * 0.8, baseline_supply * 1.2]
                },
                'demand_forecast': {
                    'baseline': baseline_demand,
                    'weather_adjusted': baseline_demand * (2 - weather_adjustment),  # Inverse relationship
                    'confidence_interval': [baseline_demand * 0.8, baseline_demand * 1.2]
                },
                'price_forecast': {
                    'baseline': baseline_price,
                    'projected': baseline_price * (baseline_demand / baseline_supply),
                    'confidence_interval': [baseline_price * 0.7, baseline_price * 1.3]
                },
                'weather_factors': self.weather_data or {},
                'model_version': 'statistical_v1'
            }
            
            return forecast
        else:
            return await self._baseline_forecast()

    async def _baseline_forecast(self) -> Dict[str, Any]:
        """Generate baseline forecast when no historical data is available."""
        # Simple baseline based on time of day
        current_hour = datetime.now().hour
        
        # Typical daily patterns
        if 6 <= current_hour <= 18:  # Daytime
            supply_multiplier = 1.2
            demand_multiplier = 1.3
        else:  # Nighttime
            supply_multiplier = 0.8
            demand_multiplier = 0.7
        
        baseline_supply = 1000  # MW
        baseline_demand = 900   # MW
        baseline_price = 50     # $/MWh
        
        forecast = {
            'forecast_id': f"fc_base_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'supply_forecast': {
                'baseline': baseline_supply,
                'time_adjusted': baseline_supply * supply_multiplier,
                'confidence_interval': [baseline_supply * 0.6, baseline_supply * 1.4]
            },
            'demand_forecast': {
                'baseline': baseline_demand,
                'time_adjusted': baseline_demand * demand_multiplier,
                'confidence_interval': [baseline_demand * 0.6, baseline_demand * 1.4]
            },
            'price_forecast': {
                'baseline': baseline_price,
                'projected': baseline_price * (demand_multiplier / supply_multiplier),
                'confidence_interval': [baseline_price * 0.5, baseline_price * 1.5]
            },
            'weather_factors': {},
            'model_version': 'baseline_v1'
        }
        
        return forecast

    async def _prepare_forecast_inputs(self) -> Dict[str, Any]:
        """Prepare input data for ML model."""
        inputs = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'forecast_horizon': self.forecast_config.forecast_horizon_hours
        }
        
        # Add weather data if available
        if self.weather_data:
            inputs['weather'] = self.weather_data
        
        # Add historical data if available
        if self.historical_data is not None and not self.historical_data.empty:
            # Get recent historical data
            recent_data = self.historical_data.tail(24)  # Last 24 hours
            inputs['historical'] = recent_data.to_dict('records')
        
        return inputs

    async def _fetch_weather_data(self):
        """Fetch weather forecast data using MCP tool."""
        try:
            weather_response = await self.call_mcp_tool(
                self.forecast_config.weather_api_tool,
                {
                    'location': 'energy_grid_region',
                    'forecast_hours': self.forecast_config.forecast_horizon_hours
                }
            )
            
            self.weather_data = weather_response
            self.logger.info("Weather data updated", 
                           data_points=len(weather_response.get('forecast', [])))
            
        except Exception as e:
            self.logger.error("Error fetching weather data", error=str(e))

    async def _fetch_historical_data(self):
        """Fetch historical energy data using MCP tool."""
        try:
            # Query last 7 days of data from Timestream
            query = """
            SELECT time, measure_value::double as value, measure_name
            FROM energy_demo.energy_metrics
            WHERE time > ago(7d)
            ORDER BY time DESC
            """
            
            results = await self.query_timeseries_data(query)
            
            if results:
                # Convert to DataFrame
                df = pd.DataFrame(results)
                df['time'] = pd.to_datetime(df['time'])
                df['hour'] = df['time'].dt.hour
                df['day_of_week'] = df['time'].dt.dayofweek
                
                # Pivot to get supply, demand, and price
                pivoted = df.pivot_table(
                    index=['time', 'hour', 'day_of_week'],
                    columns='measure_name',
                    values='value',
                    aggfunc='mean'
                ).reset_index()
                
                self.historical_data = pivoted
                self.logger.info("Historical data updated", 
                               records=len(pivoted))
            
        except Exception as e:
            self.logger.error("Error fetching historical data", error=str(e))

    def _calculate_weather_adjustment(self) -> float:
        """Calculate weather adjustment factor for forecasts."""
        if not self.weather_data:
            return 1.0
        
        # Simple weather adjustment based on solar conditions
        weather = self.weather_data.get('current', {})
        cloud_cover = weather.get('cloud_cover', 50) / 100.0
        temperature = weather.get('temperature', 20)
        
        # Solar production adjustment
        solar_adjustment = 1.0 - (cloud_cover * 0.3)  # Clouds reduce solar output
        
        # Temperature adjustment for demand
        temp_adjustment = 1.0
        if temperature > 25:  # Hot weather increases demand
            temp_adjustment = 1.1
        elif temperature < 10:  # Cold weather increases demand
            temp_adjustment = 1.05
        
        return (solar_adjustment + temp_adjustment) / 2

    def _calculate_confidence(self, forecast: Dict[str, Any]) -> float:
        """Calculate confidence score for the forecast."""
        confidence = 0.5  # Base confidence
        
        # Adjust based on generation method
        if forecast.get('generation_method') == 'ml_model':
            confidence += 0.3
        elif forecast.get('generation_method') == 'statistical_fallback':
            confidence += 0.1
        
        # Adjust based on data quality
        if self.weather_data and len(self.weather_data.get('forecast', [])) > 0:
            confidence += 0.1
        
        if self.historical_data is not None and len(self.historical_data) > 24:
            confidence += 0.1
        
        # Adjust based on model performance
        if self.model_performance_metrics:
            avg_accuracy = self.model_performance_metrics.get('average_accuracy', 0.5)
            confidence += avg_accuracy * 0.2
        
        return min(confidence, 1.0)

    async def _broadcast_forecast(self):
        """Broadcast current forecast to other agents."""
        if not self.current_forecast:
            return
        
        try:
            # Send forecast to all relevant agents
            agents_to_notify = [
                'producer_agent',
                'consumer_agent', 
                'grid_optimization_agent',
                'market_supervisor_agent'
            ]
            
            for agent_id in agents_to_notify:
                await self.send_message(
                    recipient_id=agent_id,
                    message_type="energy_forecast",
                    payload=self.current_forecast,
                    priority=5,  # High priority for forecasts
                    correlation_id=f"fc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
            
            self.logger.info("Forecast broadcasted", 
                           recipient_count=len(agents_to_notify))
            
        except Exception as e:
            self.logger.error("Error broadcasting forecast", error=str(e))

    async def _store_forecast_data(self):
        """Store forecast data in Timestream."""
        if not self.current_forecast:
            return
        
        try:
            records = []
            timestamp = datetime.now(timezone.utc)
            
            # Store supply forecast
            supply = self.current_forecast.get('supply_forecast', {})
            if 'weather_adjusted' in supply:
                records.append({
                    'measure_name': 'supply_forecast',
                    'value': supply['weather_adjusted'],
                    'timestamp': timestamp
                })
            
            # Store demand forecast
            demand = self.current_forecast.get('demand_forecast', {})
            if 'weather_adjusted' in demand:
                records.append({
                    'measure_name': 'demand_forecast',
                    'value': demand['weather_adjusted'],
                    'timestamp': timestamp
                })
            
            # Store price forecast
            price = self.current_forecast.get('price_forecast', {})
            if 'projected' in price:
                records.append({
                    'measure_name': 'price_forecast',
                    'value': price['projected'],
                    'timestamp': timestamp
                })
            
            # Store confidence score
            records.append({
                'measure_name': 'forecast_confidence',
                'value': self.current_forecast.get('confidence_score', 0.0),
                'timestamp': timestamp
            })
            
            if records:
                await self.store_timeseries_data('forecast_metrics', records)
                
        except Exception as e:
            self.logger.error("Error storing forecast data", error=str(e))

    async def _process_message(self, message: AgentMessage):
        """Process incoming messages specific to forecasting agent."""
        if message.message_type == "forecast_request":
            await self._handle_forecast_request(message)
        elif message.message_type == "model_performance_update":
            await self._handle_model_performance_update(message)
        else:
            await super()._process_message(message)

    async def _handle_forecast_request(self, message: AgentMessage):
        """Handle requests for specific forecasts."""
        try:
            request = message.payload
            forecast_type = request.get('forecast_type', 'general')
            horizon = request.get('horizon_hours', self.forecast_config.forecast_horizon_hours)
            
            # Generate custom forecast if needed
            if forecast_type == 'custom' or horizon != self.forecast_config.forecast_horizon_hours:
                # Store original config
                original_horizon = self.forecast_config.forecast_horizon_hours
                
                # Temporarily update config
                self.forecast_config.forecast_horizon_hours = horizon
                
                # Generate forecast
                await self._generate_forecast()
                
                # Restore original config
                self.forecast_config.forecast_horizon_hours = original_horizon
            
            # Send forecast response
            response_payload = {
                'forecast': self.current_forecast,
                'request_id': request.get('request_id'),
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
            await self.send_message(
                recipient_id=message.sender_id,
                message_type="forecast_response",
                payload=response_payload,
                correlation_id=message.correlation_id
            )
            
        except Exception as e:
            self.logger.error("Error handling forecast request", error=str(e))

    async def _handle_model_performance_update(self, message: AgentMessage):
        """Handle updates to model performance metrics."""
        try:
            metrics = message.payload
            self.model_performance_metrics.update(metrics)
            
            self.logger.info("Model performance updated", metrics=metrics)
            
        except Exception as e:
            self.logger.error("Error updating model performance", error=str(e))

    async def get_status(self) -> Dict[str, Any]:
        """Get forecasting agent status."""
        status = await super().get_status()
        status.update({
            'forecast_status': {
                'current_forecast_id': self.current_forecast.get('forecast_id') if self.current_forecast else None,
                'last_update': self.last_forecast_update.isoformat() if self.last_forecast_update else None,
                'forecast_count': len(self.forecast_history),
                'model_loaded': self.model_loaded,
                'confidence_threshold': self.forecast_config.confidence_threshold
            },
            'data_sources': {
                'weather_data_available': self.weather_data is not None,
                'historical_data_available': self.historical_data is not None,
                'historical_record_count': len(self.historical_data) if self.historical_data is not None else 0
            }
        })
        return status
