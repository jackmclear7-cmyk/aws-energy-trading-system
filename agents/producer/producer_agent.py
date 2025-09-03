"""
Producer Agent for Energy Trading System

This agent represents a solar farm that produces renewable energy and decides
when and at what price to sell it based on market conditions and forecasts.
"""

import asyncio
import json
import random
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..base_agent import BaseAgent, AgentConfig, AgentMessage


class ProducerAgentConfig(AgentConfig):
    """Configuration specific to the Producer Agent."""
    max_capacity_mw: float = 100.0  # Maximum solar farm capacity
    min_price_per_mwh: float = 20.0  # Minimum selling price
    max_price_per_mwh: float = 200.0  # Maximum selling price
    battery_capacity_mwh: float = 50.0  # Battery storage capacity
    battery_efficiency: float = 0.9  # Battery round-trip efficiency
    trading_interval_minutes: int = 5  # How often to make trading decisions
    forecast_weight: float = 0.7  # Weight given to forecasts vs market prices
    risk_tolerance: float = 0.5  # Risk tolerance (0=conservative, 1=aggressive)


class ProducerAgent(BaseAgent):
    """
    Producer Agent representing a solar farm.
    
    Makes autonomous decisions about energy production and pricing based on:
    - Current solar conditions
    - Market forecasts
    - Battery storage status
    - Historical performance
    """

    def __init__(self, config: ProducerAgentConfig):
        super().__init__(config)
        self.producer_config = config
        
        # Production state
        self.current_production: float = 0.0
        self.battery_level: float = 0.0
        self.available_capacity: float = config.max_capacity_mw
        
        # Market state
        self.current_market_price: float = 50.0
        self.price_history: List[Tuple[datetime, float]] = []
        self.forecast_data: Optional[Dict[str, Any]] = None
        
        # Trading state
        self.active_offers: List[Dict[str, Any]] = []
        self.completed_trades: List[Dict[str, Any]] = []
        self.total_revenue: float = 0.0
        self.total_energy_sold: float = 0.0
        
        # Solar conditions
        self.solar_irradiance: float = 0.0
        self.weather_conditions: Dict[str, Any] = {}
        self.equipment_efficiency: float = 0.85
        
        # Performance metrics
        self.uptime_percentage: float = 0.95
        self.maintenance_schedule: List[Dict[str, Any]] = []
        
        self.logger.info("Producer Agent initialized", config=config.dict())

    async def _start_agent_specific(self):
        """Start producer-specific tasks."""
        # Initialize solar conditions
        await self._update_solar_conditions()
        
        # Start production monitoring
        asyncio.create_task(self._production_monitoring_loop())
        
        # Start trading loop
        asyncio.create_task(self._trading_loop())
        
        # Start market analysis
        asyncio.create_task(self._market_analysis_loop())
        
        self.logger.info("Producer Agent started")

    async def _stop_agent_specific(self):
        """Stop producer-specific tasks."""
        self.logger.info("Producer Agent stopped")

    async def _production_monitoring_loop(self):
        """Monitor and update production capacity."""
        while self.is_running:
            try:
                # Update solar conditions
                await self._update_solar_conditions()
                
                # Calculate current production
                await self._calculate_production()
                
                # Update battery status
                await self._update_battery_status()
                
                # Store production data
                await self._store_production_data()
                
                # Wait before next update
                await asyncio.sleep(60)  # 1 minute intervals
                
            except Exception as e:
                self.logger.error("Error in production monitoring", error=str(e))
                await asyncio.sleep(60)

    async def _trading_loop(self):
        """Main trading decision loop."""
        while self.is_running:
            try:
                # Analyze market conditions
                market_analysis = await self._analyze_market_conditions()
                
                # Make trading decisions
                trading_decisions = await self._make_trading_decisions(market_analysis)
                
                # Execute trades
                await self._execute_trading_decisions(trading_decisions)
                
                # Update market offers
                await self._update_market_offers()
                
                # Wait before next trading cycle
                await asyncio.sleep(self.producer_config.trading_interval_minutes * 60)
                
            except Exception as e:
                self.logger.error("Error in trading loop", error=str(e))
                await asyncio.sleep(60)

    async def _market_analysis_loop(self):
        """Analyze market conditions and update pricing strategy."""
        while self.is_running:
            try:
                # Get current market prices
                await self._fetch_market_prices()
                
                # Update price history
                await self._update_price_history()
                
                # Analyze price trends
                price_trends = await self._analyze_price_trends()
                
                # Adjust pricing strategy
                await self._adjust_pricing_strategy(price_trends)
                
                # Wait before next analysis
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error("Error in market analysis", error=str(e))
                await asyncio.sleep(60)

    async def _update_solar_conditions(self):
        """Update current solar conditions using MCP tools."""
        try:
            # Get current time and location
            current_time = datetime.now(timezone.utc)
            current_hour = current_time.hour
            
            # Get weather data if available
            if self.forecast_data and 'weather_factors' in self.forecast_data:
                weather = self.forecast_data['weather_factors']
                self.weather_conditions = weather
                
                # Calculate solar irradiance based on time and weather
                self.solar_irradiance = self._calculate_solar_irradiance(current_hour, weather)
            else:
                # Fallback calculation based on time of day
                self.solar_irradiance = self._calculate_solar_irradiance(current_hour, {})
            
            self.logger.debug("Solar conditions updated", 
                            irradiance=self.solar_irradiance,
                            weather=self.weather_conditions)
            
        except Exception as e:
            self.logger.error("Error updating solar conditions", error=str(e))

    def _calculate_solar_irradiance(self, hour: int, weather: Dict[str, Any]) -> float:
        """Calculate solar irradiance based on time and weather conditions."""
        # Base solar curve (peak at noon)
        if 6 <= hour <= 18:  # Daylight hours
            # Parabolic curve peaking at noon
            noon_offset = abs(12 - hour)
            base_irradiance = max(0, 1000 - (noon_offset ** 2) * 20)
        else:
            base_irradiance = 0
        
        # Apply weather adjustments
        weather_adjustment = 1.0
        if weather:
            cloud_cover = weather.get('cloud_cover', 0) / 100.0
            weather_adjustment = 1.0 - (cloud_cover * 0.6)  # Clouds reduce irradiance
            
            # Additional weather factors
            if weather.get('precipitation', 0) > 0:
                weather_adjustment *= 0.3  # Rain significantly reduces output
            
            if weather.get('wind_speed', 0) > 20:
                weather_adjustment *= 0.9  # High winds slightly reduce output
        
        # Apply seasonal adjustments
        current_month = datetime.now().month
        seasonal_factor = 1.0
        if current_month in [12, 1, 2]:  # Winter
            seasonal_factor = 0.7
        elif current_month in [6, 7, 8]:  # Summer
            seasonal_factor = 1.2
        
        final_irradiance = base_irradiance * weather_adjustment * seasonal_factor
        return max(0, final_irradiance)

    async def _calculate_production(self):
        """Calculate current energy production."""
        try:
            # Calculate theoretical production
            theoretical_production = self.solar_irradiance * self.producer_config.max_capacity_mw / 1000
            
            # Apply equipment efficiency
            self.current_production = theoretical_production * self.equipment_efficiency
            
            # Apply uptime factor
            self.current_production *= self.uptime_percentage
            
            # Check for maintenance
            if await self._is_maintenance_time():
                self.current_production *= 0.1  # Reduced output during maintenance
            
            # Update available capacity
            self.available_capacity = min(
                self.producer_config.max_capacity_mw,
                self.current_production + self.battery_level
            )
            
            self.logger.debug("Production calculated", 
                            current_production=self.current_production,
                            available_capacity=self.available_capacity)
            
        except Exception as e:
            self.logger.error("Error calculating production", error=str(e))

    async def _update_battery_status(self):
        """Update battery storage status."""
        try:
            # Natural discharge (small amount)
            self.battery_level *= 0.999  # 0.1% discharge per minute
            
            # Ensure battery level stays within bounds
            self.battery_level = max(0, min(
                self.battery_level,
                self.producer_config.battery_capacity_mwh
            ))
            
        except Exception as e:
            self.logger.error("Error updating battery status", error=str(e))

    async def _analyze_market_conditions(self) -> Dict[str, Any]:
        """Analyze current market conditions for trading decisions."""
        try:
            analysis = {
                'current_price': self.current_market_price,
                'price_trend': 'stable',
                'demand_level': 'medium',
                'supply_level': 'medium',
                'volatility': 'low',
                'recommended_action': 'hold'
            }
            
            # Analyze price trends
            if len(self.price_history) >= 3:
                recent_prices = [price for _, price in self.price_history[-3:]]
                if recent_prices[-1] > recent_prices[0] * 1.05:
                    analysis['price_trend'] = 'rising'
                    analysis['recommended_action'] = 'sell'
                elif recent_prices[-1] < recent_prices[0] * 0.95:
                    analysis['price_trend'] = 'falling'
                    analysis['recommended_action'] = 'hold'
            
            # Consider forecast data
            if self.forecast_data:
                forecast = self.forecast_data
                supply_forecast = forecast.get('supply_forecast', {})
                demand_forecast = forecast.get('demand_forecast', {})
                
                if 'weather_adjusted' in supply_forecast and 'weather_adjusted' in demand_forecast:
                    supply = supply_forecast['weather_adjusted']
                    demand = demand_forecast['weather_adjusted']
                    
                    if demand > supply * 1.1:
                        analysis['demand_level'] = 'high'
                        analysis['recommended_action'] = 'sell'
                    elif supply > demand * 1.1:
                        analysis['supply_level'] = 'high'
                        analysis['recommended_action'] = 'hold'
            
            # Consider current production
            if self.current_production > self.producer_config.max_capacity_mw * 0.8:
                analysis['supply_level'] = 'high'
                if analysis['recommended_action'] == 'hold':
                    analysis['recommended_action'] = 'sell'
            
            self.logger.info("Market analysis completed", analysis=analysis)
            return analysis
            
        except Exception as e:
            self.logger.error("Error analyzing market conditions", error=str(e))
            return {'recommended_action': 'hold'}

    async def _make_trading_decisions(self, market_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Make trading decisions based on market analysis."""
        try:
            decisions = []
            recommended_action = market_analysis.get('recommended_action', 'hold')
            
            if recommended_action == 'sell' and self.available_capacity > 0:
                # Calculate optimal selling price
                optimal_price = await self._calculate_optimal_price(market_analysis)
                
                # Calculate quantity to sell
                quantity_to_sell = await self._calculate_quantity_to_sell(market_analysis)
                
                if quantity_to_sell > 0:
                    decision = {
                        'action': 'sell',
                        'quantity_mw': quantity_to_sell,
                        'price_per_mwh': optimal_price,
                        'priority': 'high' if market_analysis.get('demand_level') == 'high' else 'medium',
                        'valid_until': (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
                    }
                    decisions.append(decision)
                    
                    self.logger.info("Trading decision made", decision=decision)
            
            elif recommended_action == 'hold' and self.battery_level < self.producer_config.battery_capacity_mwh * 0.8:
                # Consider charging battery if prices are low
                if self.current_market_price < self.producer_config.min_price_per_mwh * 1.2:
                    decision = {
                        'action': 'charge_battery',
                        'quantity_mw': min(
                            self.producer_config.battery_capacity_mwh - self.battery_level,
                            self.current_production * 0.5
                        ),
                        'price_per_mwh': self.current_market_price,
                        'priority': 'low',
                        'valid_until': (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
                    }
                    decisions.append(decision)
            
            return decisions
            
        except Exception as e:
            self.logger.error("Error making trading decisions", error=str(e))
            return []

    async def _calculate_optimal_price(self, market_analysis: Dict[str, Any]) -> float:
        """Calculate optimal selling price based on market conditions."""
        try:
            base_price = self.current_market_price
            
            # Adjust based on demand level
            demand_multiplier = 1.0
            if market_analysis.get('demand_level') == 'high':
                demand_multiplier = 1.15
            elif market_analysis.get('demand_level') == 'low':
                demand_multiplier = 0.95
            
            # Adjust based on supply level
            supply_multiplier = 1.0
            if market_analysis.get('supply_level') == 'low':
                supply_multiplier = 1.1
            elif market_analysis.get('supply_level') == 'high':
                supply_multiplier = 0.9
            
            # Adjust based on price trend
            trend_multiplier = 1.0
            if market_analysis.get('price_trend') == 'rising':
                trend_multiplier = 1.05
            elif market_analysis.get('price_trend') == 'falling':
                trend_multiplier = 0.98
            
            # Calculate optimal price
            optimal_price = base_price * demand_multiplier * supply_multiplier * trend_multiplier
            
            # Apply risk tolerance
            risk_adjustment = 1.0 + (self.producer_config.risk_tolerance - 0.5) * 0.1
            optimal_price *= risk_adjustment
            
            # Ensure price is within bounds
            optimal_price = max(
                self.producer_config.min_price_per_mwh,
                min(optimal_price, self.producer_config.max_price_per_mwh)
            )
            
            return round(optimal_price, 2)
            
        except Exception as e:
            self.logger.error("Error calculating optimal price", error=str(e))
            return self.current_market_price

    async def _calculate_quantity_to_sell(self, market_analysis: Dict[str, Any]) -> float:
        """Calculate optimal quantity to sell."""
        try:
            # Start with available capacity
            base_quantity = self.available_capacity
            
            # Adjust based on market conditions
            if market_analysis.get('demand_level') == 'high':
                # Sell more when demand is high
                base_quantity *= 1.2
            elif market_analysis.get('demand_level') == 'low':
                # Sell less when demand is low
                base_quantity *= 0.8
            
            # Adjust based on price trend
            if market_analysis.get('price_trend') == 'rising':
                # Hold some back if prices are rising
                base_quantity *= 0.9
            elif market_analysis.get('price_trend') == 'falling':
                # Sell more if prices are falling
                base_quantity *= 1.1
            
            # Consider battery level
            if self.battery_level > self.producer_config.battery_capacity_mwh * 0.7:
                # Sell more if battery is well-charged
                base_quantity *= 1.1
            
            # Ensure quantity is within bounds
            final_quantity = max(0, min(base_quantity, self.available_capacity))
            
            return round(final_quantity, 2)
            
        except Exception as e:
            self.logger.error("Error calculating quantity to sell", error=str(e))
            return 0.0

    async def _execute_trading_decisions(self, decisions: List[Dict[str, Any]]):
        """Execute trading decisions by sending offers to market."""
        try:
            for decision in decisions:
                if decision['action'] == 'sell':
                    # Create market offer
                    offer = {
                        'offer_id': f"offer_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
                        'producer_id': self.agent_id,
                        'quantity_mw': decision['quantity_mw'],
                        'price_per_mwh': decision['price_per_mwh'],
                        'priority': decision['priority'],
                        'valid_until': decision['valid_until'],
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Send offer to market supervisor
                    await self.send_message(
                        recipient_id='market_supervisor_agent',
                        message_type='energy_offer',
                        payload=offer,
                        priority=decision['priority'] == 'high' and 8 or 5
                    )
                    
                    # Add to active offers
                    self.active_offers.append(offer)
                    
                    self.logger.info("Market offer sent", offer=offer)
                
                elif decision['action'] == 'charge_battery':
                    # Charge battery (simulate by reducing available capacity)
                    charge_amount = min(
                        decision['quantity_mw'],
                        self.producer_config.battery_capacity_mwh - self.battery_level
                    )
                    
                    self.battery_level += charge_amount * self.producer_config.battery_efficiency
                    self.available_capacity -= charge_amount
                    
                    self.logger.info("Battery charging initiated", 
                                  charge_amount=charge_amount,
                                  new_battery_level=self.battery_level)
            
        except Exception as e:
            self.logger.error("Error executing trading decisions", error=str(e))

    async def _update_market_offers(self):
        """Update and clean up market offers."""
        try:
            current_time = datetime.now(timezone.utc)
            expired_offers = []
            
            for offer in self.active_offers:
                valid_until = datetime.fromisoformat(offer['valid_until'])
                if current_time > valid_until:
                    expired_offers.append(offer)
            
            # Remove expired offers
            for expired_offer in expired_offers:
                self.active_offers.remove(expired_offer)
                
                # Notify market supervisor of expired offer
                await self.send_message(
                    recipient_id='market_supervisor_agent',
                    message_type='offer_expired',
                    payload={'offer_id': expired_offer['offer_id']}
                )
                
                self.logger.info("Offer expired", offer_id=expired_offer['offer_id'])
            
        except Exception as e:
            self.logger.error("Error updating market offers", error=str(e))

    async def _fetch_market_prices(self):
        """Fetch current market prices using MCP tools."""
        try:
            # In a real implementation, this would call a market data API
            # For now, we'll simulate price updates
            price_change = random.uniform(-0.05, 0.05)  # ±5% change
            self.current_market_price *= (1 + price_change)
            
            # Ensure price stays reasonable
            self.current_market_price = max(10, min(300, self.current_market_price))
            
        except Exception as e:
            self.logger.error("Error fetching market prices", error=str(e))

    async def _update_price_history(self):
        """Update price history with current market price."""
        try:
            current_time = datetime.now(timezone.utc)
            self.price_history.append((current_time, self.current_market_price))
            
            # Keep only recent price history (last 24 hours)
            cutoff_time = current_time - timedelta(hours=24)
            self.price_history = [
                (timestamp, price) for timestamp, price in self.price_history
                if timestamp > cutoff_time
            ]
            
        except Exception as e:
            self.logger.error("Error updating price history", error=str(e))

    async def _analyze_price_trends(self) -> Dict[str, Any]:
        """Analyze price trends from historical data."""
        try:
            if len(self.price_history) < 2:
                return {'trend': 'insufficient_data'}
            
            # Calculate simple moving average
            recent_prices = [price for _, price in self.price_history[-12:]]  # Last 12 data points
            if recent_prices:
                sma = sum(recent_prices) / len(recent_prices)
                current_price = self.current_market_price
                
                if current_price > sma * 1.02:
                    trend = 'rising'
                elif current_price < sma * 0.98:
                    trend = 'falling'
                else:
                    trend = 'stable'
                
                return {
                    'trend': trend,
                    'moving_average': sma,
                    'current_price': current_price,
                    'deviation': (current_price - sma) / sma
                }
            
            return {'trend': 'insufficient_data'}
            
        except Exception as e:
            self.logger.error("Error analyzing price trends", error=str(e))
            return {'trend': 'error'}

    async def _adjust_pricing_strategy(self, price_trends: Dict[str, Any]):
        """Adjust pricing strategy based on price trends."""
        try:
            trend = price_trends.get('trend', 'stable')
            
            if trend == 'rising':
                # Increase minimum price slightly
                self.producer_config.min_price_per_mwh *= 1.02
                self.logger.info("Pricing strategy adjusted for rising prices", 
                               new_min_price=self.producer_config.min_price_per_mwh)
            
            elif trend == 'falling':
                # Decrease minimum price slightly
                self.producer_config.min_price_per_mwh *= 0.98
                self.logger.info("Pricing strategy adjusted for falling prices", 
                               new_min_price=self.producer_config.min_price_per_mwh)
            
            # Ensure minimum price stays reasonable
            self.producer_config.min_price_per_mwh = max(10, self.producer_config.min_price_per_mwh)
            
        except Exception as e:
            self.logger.error("Error adjusting pricing strategy", error=str(e))

    async def _store_production_data(self):
        """Store production data in Timestream."""
        try:
            records = []
            timestamp = datetime.now(timezone.utc)
            
            # Store production metrics
            records.extend([
                {
                    'measure_name': 'solar_production',
                    'value': self.current_production,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'battery_level',
                    'value': self.battery_level,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'available_capacity',
                    'value': self.available_capacity,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'solar_irradiance',
                    'value': self.solar_irradiance,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'market_price',
                    'value': self.current_market_price,
                    'timestamp': timestamp
                }
            ])
            
            if records:
                await self.store_timeseries_data('producer_metrics', records)
                
        except Exception as e:
            self.logger.error("Error storing production data", error=str(e))

    async def _is_maintenance_time(self) -> bool:
        """Check if it's time for maintenance."""
        try:
            current_time = datetime.now(timezone.utc)
            
            # Check if any maintenance is scheduled for current time
            for maintenance in self.maintenance_schedule:
                start_time = datetime.fromisoformat(maintenance['start_time'])
                end_time = datetime.fromisoformat(maintenance['end_time'])
                
                if start_time <= current_time <= end_time:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error("Error checking maintenance time", error=str(e))
            return False

    async def _process_message(self, message: AgentMessage):
        """Process incoming messages specific to producer agent."""
        if message.message_type == "energy_forecast":
            await self._handle_energy_forecast(message)
        elif message.message_type == "trade_executed":
            await self._handle_trade_executed(message)
        elif message.message_type == "offer_accepted":
            await self._handle_offer_accepted(message)
        elif message.message_type == "offer_rejected":
            await self._handle_offer_rejected(message)
        else:
            await super()._process_message(message)

    async def _handle_energy_forecast(self, message: AgentMessage):
        """Handle energy forecasts from forecasting agent."""
        try:
            self.forecast_data = message.payload
            self.logger.info("Energy forecast received", 
                           forecast_id=self.forecast_data.get('forecast_id'))
            
        except Exception as e:
            self.logger.error("Error handling energy forecast", error=str(e))

    async def _handle_trade_executed(self, message: AgentMessage):
        """Handle trade execution notifications."""
        try:
            trade = message.payload
            trade_id = trade.get('trade_id')
            
            # Add to completed trades
            self.completed_trades.append(trade)
            
            # Update metrics
            quantity = trade.get('quantity_mw', 0)
            price = trade.get('price_per_mwh', 0)
            revenue = quantity * price
            
            self.total_revenue += revenue
            self.total_energy_sold += quantity
            
            # Remove from active offers
            offer_id = trade.get('offer_id')
            self.active_offers = [o for o in self.active_offers if o.get('offer_id') != offer_id]
            
            self.logger.info("Trade executed", 
                           trade_id=trade_id,
                           revenue=revenue,
                           total_revenue=self.total_revenue)
            
        except Exception as e:
            self.logger.error("Error handling trade execution", error=str(e))

    async def _handle_offer_accepted(self, message: AgentMessage):
        """Handle offer acceptance notifications."""
        try:
            offer = message.payload
            offer_id = offer.get('offer_id')
            
            self.logger.info("Offer accepted", offer_id=offer_id)
            
        except Exception as e:
            self.logger.error("Error handling offer acceptance", error=str(e))

    async def _handle_offer_rejected(self, message: AgentMessage):
        """Handle offer rejection notifications."""
        try:
            offer = message.payload
            offer_id = offer.get('offer_id')
            reason = offer.get('reason', 'unknown')
            
            # Remove from active offers
            self.active_offers = [o for o in self.active_offers if o.get('offer_id') != offer_id]
            
            self.logger.info("Offer rejected", 
                           offer_id=offer_id,
                           reason=reason)
            
        except Exception as e:
            self.logger.error("Error handling offer rejection", error=str(e))

    async def get_status(self) -> Dict[str, Any]:
        """Get producer agent status."""
        status = await super().get_status()
        status.update({
            'production_status': {
                'current_production_mw': self.current_production,
                'battery_level_mwh': self.battery_level,
                'available_capacity_mw': self.available_capacity,
                'solar_irradiance': self.solar_irradiance,
                'equipment_efficiency': self.equipment_efficiency,
                'uptime_percentage': self.uptime_percentage
            },
            'trading_status': {
                'current_market_price': self.current_market_price,
                'active_offers_count': len(self.active_offers),
                'completed_trades_count': len(self.completed_trades),
                'total_revenue': self.total_revenue,
                'total_energy_sold_mwh': self.total_energy_sold
            },
            'market_analysis': {
                'price_history_count': len(self.price_history),
                'forecast_data_available': self.forecast_data is not None,
                'last_forecast_id': self.forecast_data.get('forecast_id') if self.forecast_data else None
            }
        })
        return status
