"""
Consumer Agent for Energy Trading System

This agent represents a factory with battery storage that consumes energy and
optimizes when to buy energy and when to use stored energy based on prices.
"""

import asyncio
import json
import random
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..base_agent import BaseAgent, AgentConfig, AgentMessage


class ConsumerAgentConfig(AgentConfig):
    """Configuration specific to the Consumer Agent."""
    base_consumption_mw: float = 80.0  # Base factory consumption
    max_consumption_mw: float = 120.0  # Maximum consumption during peak operations
    min_consumption_mw: float = 40.0   # Minimum consumption during maintenance
    battery_capacity_mwh: float = 100.0  # Battery storage capacity
    battery_efficiency: float = 0.9  # Battery round-trip efficiency
    max_price_per_mwh: float = 150.0  # Maximum price willing to pay
    min_price_per_mwh: float = 15.0   # Minimum price willing to pay
    trading_interval_minutes: int = 5  # How often to make trading decisions
    demand_response_enabled: bool = True  # Whether to participate in demand response
    peak_shaving_enabled: bool = True  # Whether to use battery for peak shaving


class ConsumerAgent(BaseAgent):
    """
    Consumer Agent representing a factory with battery storage.
    
    Makes autonomous decisions about energy consumption and purchasing based on:
    - Current energy prices
    - Battery storage status
    - Production schedules
    - Market forecasts
    - Grid stability signals
    """

    def __init__(self, config: ConsumerAgentConfig):
        super().__init__(config)
        self.consumer_config = config
        
        # Consumption state
        self.current_consumption: float = config.base_consumption_mw
        self.battery_level: float = config.battery_capacity_mwh * 0.5  # Start at 50%
        self.available_battery_capacity: float = config.battery_capacity_mwh * 0.5
        
        # Market state
        self.current_market_price: float = 50.0
        self.price_history: List[Tuple[datetime, float]] = []
        self.forecast_data: Optional[Dict[str, Any]] = None
        
        # Trading state
        self.active_bids: List[Dict[str, Any]] = []
        self.completed_purchases: List[Dict[str, Any]] = []
        self.total_energy_purchased: float = 0.0
        self.total_cost: float = 0.0
        
        # Production schedule
        self.production_schedule: List[Dict[str, Any]] = []
        self.current_shift: str = "day"  # day, night, maintenance
        
        # Demand response
        self.demand_response_active: bool = False
        self.demand_response_target: float = 0.0
        self.demand_response_duration: timedelta = timedelta(minutes=0)
        
        # Performance metrics
        self.energy_cost_savings: float = 0.0
        self.peak_shaving_savings: float = 0.0
        self.demand_response_revenue: float = 0.0
        
        self.logger.info("Consumer Agent initialized", config=config.dict())

    async def _start_agent_specific(self):
        """Start consumer-specific tasks."""
        # Initialize production schedule
        await self._initialize_production_schedule()
        
        # Start consumption monitoring
        asyncio.create_task(self._consumption_monitoring_loop())
        
        # Start trading loop
        asyncio.create_task(self._trading_loop())
        
        # Start battery optimization
        asyncio.create_task(self._battery_optimization_loop())
        
        # Start demand response monitoring
        asyncio.create_task(self._demand_response_loop())
        
        self.logger.info("Consumer Agent started")

    async def _stop_agent_specific(self):
        """Stop consumer-specific tasks."""
        self.logger.info("Consumer Agent stopped")

    async def _initialize_production_schedule(self):
        """Initialize the production schedule."""
        try:
            # Create a typical weekly production schedule
            current_time = datetime.now(timezone.utc)
            
            # Day shift: 6 AM - 6 PM, high consumption
            # Night shift: 6 PM - 6 AM, medium consumption
            # Maintenance: 2 AM - 6 AM, low consumption
            
            self.production_schedule = [
                {
                    'shift': 'day',
                    'start_hour': 6,
                    'end_hour': 18,
                    'consumption_multiplier': 1.2,
                    'description': 'High production shift'
                },
                {
                    'shift': 'night',
                    'start_hour': 18,
                    'end_hour': 6,
                    'consumption_multiplier': 0.9,
                    'description': 'Medium production shift'
                },
                {
                    'shift': 'maintenance',
                    'start_hour': 2,
                    'end_hour': 6,
                    'consumption_multiplier': 0.5,
                    'description': 'Low consumption maintenance'
                }
            ]
            
            self.logger.info("Production schedule initialized", 
                           schedule_count=len(self.production_schedule))
            
        except Exception as e:
            self.logger.error("Error initializing production schedule", error=str(e))

    async def _consumption_monitoring_loop(self):
        """Monitor and update energy consumption."""
        while self.is_running:
            try:
                # Update current shift
                await self._update_current_shift()
                
                # Calculate current consumption
                await self._calculate_consumption()
                
                # Update battery status
                await self._update_battery_status()
                
                # Store consumption data
                await self._store_consumption_data()
                
                # Wait before next update
                await asyncio.sleep(60)  # 1 minute intervals
                
            except Exception as e:
                self.logger.error("Error in consumption monitoring", error=str(e))
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
                
                # Update market bids
                await self._update_market_bids()
                
                # Wait before next trading cycle
                await asyncio.sleep(self.consumer_config.trading_interval_minutes * 60)
                
            except Exception as e:
                self.logger.error("Error in trading loop", error=str(e))
                await asyncio.sleep(60)

    async def _battery_optimization_loop(self):
        """Optimize battery usage for cost savings."""
        while self.is_running:
            try:
                # Analyze price patterns
                price_patterns = await self._analyze_price_patterns()
                
                # Optimize battery charging/discharging
                await self._optimize_battery_usage(price_patterns)
                
                # Calculate savings
                await self._calculate_energy_savings()
                
                # Wait before next optimization
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error("Error in battery optimization", error=str(e))
                await asyncio.sleep(60)

    async def _demand_response_loop(self):
        """Monitor and respond to demand response signals."""
        while self.is_running:
            try:
                # Check for demand response opportunities
                if self.consumer_config.demand_response_enabled:
                    await self._check_demand_response_opportunities()
                
                # Update demand response status
                await self._update_demand_response_status()
                
                # Wait before next check
                await asyncio.sleep(60)  # 1 minute intervals
                
            except Exception as e:
                self.logger.error("Error in demand response loop", error=str(e))
                await asyncio.sleep(60)

    async def _update_current_shift(self):
        """Update the current production shift."""
        try:
            current_hour = datetime.now(timezone.utc).hour
            
            for schedule in self.production_schedule:
                start_hour = schedule['start_hour']
                end_hour = schedule['end_hour']
                
                # Handle shifts that cross midnight
                if start_hour > end_hour:
                    if current_hour >= start_hour or current_hour < end_hour:
                        self.current_shift = schedule['shift']
                        break
                else:
                    if start_hour <= current_hour < end_hour:
                        self.current_shift = schedule['shift']
                        break
            
            self.logger.debug("Current shift updated", shift=self.current_shift)
            
        except Exception as e:
            self.logger.error("Error updating current shift", error=str(e))

    async def _calculate_consumption(self):
        """Calculate current energy consumption."""
        try:
            # Get base consumption for current shift
            shift_config = next(
                (s for s in self.production_schedule if s['shift'] == self.current_shift),
                None
            )
            
            if shift_config:
                base_consumption = self.consumer_config.base_consumption_mw
                multiplier = shift_config['consumption_multiplier']
                self.current_consumption = base_consumption * multiplier
            else:
                self.current_consumption = self.consumer_config.base_consumption_mw
            
            # Apply demand response adjustments
            if self.demand_response_active:
                self.current_consumption = max(
                    self.consumer_config.min_consumption_mw,
                    self.current_consumption - self.demand_response_target
                )
            
            # Ensure consumption stays within bounds
            self.current_consumption = max(
                self.consumer_config.min_consumption_mw,
                min(self.current_consumption, self.consumer_config.max_consumption_mw)
            )
            
            self.logger.debug("Consumption calculated", 
                            current_consumption=self.current_consumption,
                            shift=self.current_shift)
            
        except Exception as e:
            self.logger.error("Error calculating consumption", error=str(e))

    async def _update_battery_status(self):
        """Update battery storage status."""
        try:
            # Natural discharge (small amount)
            self.battery_level *= 0.999  # 0.1% discharge per minute
            
            # Ensure battery level stays within bounds
            self.battery_level = max(0, min(
                self.battery_level,
                self.consumer_config.battery_capacity_mwh
            ))
            
            # Update available battery capacity
            self.available_battery_capacity = self.battery_level
            
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
                    analysis['recommended_action'] = 'buy'
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
                        analysis['recommended_action'] = 'buy'
                    elif supply > demand * 1.1:
                        analysis['supply_level'] = 'high'
                        analysis['recommended_action'] = 'hold'
            
            # Consider current consumption and battery level
            if self.current_consumption > self.consumer_config.base_consumption_mw * 1.1:
                analysis['demand_level'] = 'high'
                if analysis['recommended_action'] == 'hold':
                    analysis['recommended_action'] = 'buy'
            
            if self.battery_level < self.consumer_config.battery_capacity_mwh * 0.3:
                analysis['recommended_action'] = 'buy'
            
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
            
            if recommended_action == 'buy':
                # Calculate optimal buying price
                optimal_price = await self._calculate_optimal_price(market_analysis)
                
                # Calculate quantity to buy
                quantity_to_buy = await self._calculate_quantity_to_buy(market_analysis)
                
                if quantity_to_buy > 0:
                    decision = {
                        'action': 'buy',
                        'quantity_mw': quantity_to_buy,
                        'price_per_mwh': optimal_price,
                        'priority': 'high' if market_analysis.get('demand_level') == 'high' else 'medium',
                        'valid_until': (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
                    }
                    decisions.append(decision)
                    
                    self.logger.info("Trading decision made", decision=decision)
            
            elif recommended_action == 'hold' and self.consumer_config.peak_shaving_enabled:
                # Consider using battery for peak shaving if prices are high
                if self.current_market_price > self.consumer_config.max_price_per_mwh * 0.8:
                    decision = {
                        'action': 'use_battery',
                        'quantity_mw': min(
                            self.battery_level,
                            self.current_consumption * 0.3
                        ),
                        'price_per_mwh': self.current_market_price,
                        'priority': 'medium',
                        'valid_until': (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
                    }
                    decisions.append(decision)
            
            return decisions
            
        except Exception as e:
            self.logger.error("Error making trading decisions", error=str(e))
            return []

    async def _calculate_optimal_price(self, market_analysis: Dict[str, Any]) -> float:
        """Calculate optimal buying price based on market conditions."""
        try:
            base_price = self.current_market_price
            
            # Adjust based on demand level
            demand_multiplier = 1.0
            if market_analysis.get('demand_level') == 'high':
                demand_multiplier = 1.1
            elif market_analysis.get('demand_level') == 'low':
                demand_multiplier = 0.95
            
            # Adjust based on supply level
            supply_multiplier = 1.0
            if market_analysis.get('supply_level') == 'low':
                supply_multiplier = 1.05
            elif market_analysis.get('supply_level') == 'high':
                supply_multiplier = 0.95
            
            # Adjust based on price trend
            trend_multiplier = 1.0
            if market_analysis.get('price_trend') == 'rising':
                trend_multiplier = 1.02
            elif market_analysis.get('price_trend') == 'falling':
                trend_multiplier = 0.98
            
            # Calculate optimal price
            optimal_price = base_price * demand_multiplier * supply_multiplier * trend_multiplier
            
            # Ensure price is within bounds
            optimal_price = max(
                self.consumer_config.min_price_per_mwh,
                min(optimal_price, self.consumer_config.max_price_per_mwh)
            )
            
            return round(optimal_price, 2)
            
        except Exception as e:
            self.logger.error("Error calculating optimal price", error=str(e))
            return self.current_market_price

    async def _calculate_quantity_to_buy(self, market_analysis: Dict[str, Any]) -> float:
        """Calculate optimal quantity to buy."""
        try:
            # Start with current consumption needs
            base_quantity = self.current_consumption
            
            # Adjust based on battery level
            if self.battery_level < self.consumer_config.battery_capacity_mwh * 0.3:
                # Need to charge battery
                base_quantity += (self.consumer_config.battery_capacity_mwh - self.battery_level) * 0.5
            
            # Adjust based on market conditions
            if market_analysis.get('demand_level') == 'high':
                # Buy more when demand is high
                base_quantity *= 1.1
            elif market_analysis.get('demand_level') == 'low':
                # Buy less when demand is low
                base_quantity *= 0.9
            
            # Adjust based on price trend
            if market_analysis.get('price_trend') == 'rising':
                # Buy more if prices are rising
                base_quantity *= 1.05
            elif market_analysis.get('price_trend') == 'falling':
                # Buy less if prices are falling
                base_quantity *= 0.95
            
            # Ensure quantity is reasonable
            final_quantity = max(0, min(base_quantity, self.consumer_config.max_consumption_mw * 1.5))
            
            return round(final_quantity, 2)
            
        except Exception as e:
            self.logger.error("Error calculating quantity to buy", error=str(e))
            return 0.0

    async def _execute_trading_decisions(self, decisions: List[Dict[str, Any]]):
        """Execute trading decisions by sending bids to market."""
        try:
            for decision in decisions:
                if decision['action'] == 'buy':
                    # Create market bid
                    bid = {
                        'bid_id': f"bid_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
                        'consumer_id': self.agent_id,
                        'quantity_mw': decision['quantity_mw'],
                        'price_per_mwh': decision['price_per_mwh'],
                        'priority': decision['priority'],
                        'valid_until': decision['valid_until'],
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Send bid to market supervisor
                    await self.send_message(
                        recipient_id='market_supervisor_agent',
                        message_type='energy_bid',
                        payload=bid,
                        priority=decision['priority'] == 'high' and 8 or 5
                    )
                    
                    # Add to active bids
                    self.active_bids.append(bid)
                    
                    self.logger.info("Market bid sent", bid=bid)
                
                elif decision['action'] == 'use_battery':
                    # Use battery for peak shaving
                    use_amount = min(
                        decision['quantity_mw'],
                        self.battery_level
                    )
                    
                    self.battery_level -= use_amount
                    self.available_battery_capacity = self.battery_level
                    
                    # Calculate savings
                    savings = use_amount * self.current_market_price
                    self.peak_shaving_savings += savings
                    
                    self.logger.info("Battery used for peak shaving", 
                                  use_amount=use_amount,
                                  savings=savings,
                                  new_battery_level=self.battery_level)
            
        except Exception as e:
            self.logger.error("Error executing trading decisions", error=str(e))

    async def _update_market_bids(self):
        """Update and clean up market bids."""
        try:
            current_time = datetime.now(timezone.utc)
            expired_bids = []
            
            for bid in self.active_bids:
                valid_until = datetime.fromisoformat(bid['valid_until'])
                if current_time > valid_until:
                    expired_bids.append(bid)
            
            # Remove expired bids
            for expired_bid in expired_bids:
                self.active_bids.remove(expired_bid)
                
                # Notify market supervisor of expired bid
                await self.send_message(
                    recipient_id='market_supervisor_agent',
                    message_type='bid_expired',
                    payload={'bid_id': expired_bid['bid_id']}
                )
                
                self.logger.info("Bid expired", bid_id=expired_bid['bid_id'])
            
        except Exception as e:
            self.logger.error("Error updating market bids", error=str(e))

    async def _analyze_price_patterns(self) -> Dict[str, Any]:
        """Analyze price patterns for battery optimization."""
        try:
            if len(self.price_history) < 24:
                return {'pattern': 'insufficient_data'}
            
            # Analyze daily patterns
            current_hour = datetime.now(timezone.utc).hour
            daily_prices = []
            
            for timestamp, price in self.price_history[-24:]:
                if timestamp.hour == current_hour:
                    daily_prices.append(price)
            
            if daily_prices:
                avg_price = sum(daily_prices) / len(daily_prices)
                current_price = self.current_market_price
                
                if current_price < avg_price * 0.9:
                    pattern = 'low_price_opportunity'
                elif current_price > avg_price * 1.1:
                    pattern = 'high_price_avoid'
                else:
                    pattern = 'normal_price'
                
                return {
                    'pattern': pattern,
                    'average_price': avg_price,
                    'current_price': current_price,
                    'price_difference': current_price - avg_price
                }
            
            return {'pattern': 'insufficient_data'}
            
        except Exception as e:
            self.logger.error("Error analyzing price patterns", error=str(e))
            return {'pattern': 'error'}

    async def _optimize_battery_usage(self, price_patterns: Dict[str, Any]):
        """Optimize battery usage based on price patterns."""
        try:
            pattern = price_patterns.get('pattern', 'normal_price')
            
            if pattern == 'low_price_opportunity':
                # Charge battery when prices are low
                if self.battery_level < self.consumer_config.battery_capacity_mwh * 0.8:
                    charge_amount = min(
                        self.consumer_config.battery_capacity_mwh - self.battery_level,
                        self.current_consumption * 0.5
                    )
                    
                    if charge_amount > 0:
                        # Simulate charging by reducing available capacity
                        self.available_battery_capacity -= charge_amount
                        
                        self.logger.info("Battery charging optimized for low prices", 
                                      charge_amount=charge_amount)
            
            elif pattern == 'high_price_avoid':
                # Use battery when prices are high
                if self.battery_level > self.consumer_config.battery_capacity_mwh * 0.3:
                    use_amount = min(
                        self.battery_level * 0.2,
                        self.current_consumption * 0.3
                    )
                    
                    if use_amount > 0:
                        self.battery_level -= use_amount
                        self.available_battery_capacity = self.battery_level
                        
                        # Calculate savings
                        savings = use_amount * self.current_market_price
                        self.peak_shaving_savings += savings
                        
                        self.logger.info("Battery used to avoid high prices", 
                                      use_amount=use_amount,
                                      savings=savings)
            
        except Exception as e:
            self.logger.error("Error optimizing battery usage", error=str(e))

    async def _calculate_energy_savings(self):
        """Calculate energy cost savings from battery optimization."""
        try:
            # Calculate potential savings from not buying at current price
            if self.battery_level > 0:
                potential_savings = self.battery_level * self.current_market_price
                self.energy_cost_savings = max(self.energy_cost_savings, potential_savings)
            
        except Exception as e:
            self.logger.error("Error calculating energy savings", error=str(e))

    async def _check_demand_response_opportunities(self):
        """Check for demand response opportunities."""
        try:
            # In a real implementation, this would check for grid operator signals
            # For now, we'll simulate based on price thresholds
            
            if (self.current_market_price > self.consumer_config.max_price_per_mwh * 0.9 and
                not self.demand_response_active and
                self.battery_level > self.consumer_config.battery_capacity_mwh * 0.4):
                
                # Activate demand response
                self.demand_response_active = True
                self.demand_response_target = self.current_consumption * 0.2
                self.demand_response_duration = timedelta(minutes=30)
                
                self.logger.info("Demand response activated", 
                               target_reduction=self.demand_response_target,
                               duration=self.demand_response_duration)
                
        except Exception as e:
            self.logger.error("Error checking demand response opportunities", error=str(e))

    async def _update_demand_response_status(self):
        """Update demand response status."""
        try:
            if self.demand_response_active:
                # Check if demand response period has ended
                if self.demand_response_duration <= timedelta(0):
                    # End demand response
                    self.demand_response_active = False
                    self.demand_response_target = 0.0
                    self.demand_response_duration = timedelta(minutes=0)
                    
                    # Calculate revenue
                    revenue = self.demand_response_target * self.current_market_price * 0.1  # 10% of avoided cost
                    self.demand_response_revenue += revenue
                    
                    self.logger.info("Demand response ended", revenue=revenue)
                else:
                    # Reduce remaining duration
                    self.demand_response_duration -= timedelta(minutes=1)
            
        except Exception as e:
            self.logger.error("Error updating demand response status", error=str(e))

    async def _store_consumption_data(self):
        """Store consumption data in Timestream."""
        try:
            records = []
            timestamp = datetime.now(timezone.utc)
            
            # Store consumption metrics
            records.extend([
                {
                    'measure_name': 'factory_consumption',
                    'value': self.current_consumption,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'battery_level',
                    'value': self.battery_level,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'available_battery_capacity',
                    'value': self.available_battery_capacity,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'market_price',
                    'value': self.current_market_price,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'demand_response_active',
                    'value': 1.0 if self.demand_response_active else 0.0,
                    'timestamp': timestamp
                }
            ])
            
            if records:
                await self.store_timeseries_data('consumer_metrics', records)
                
        except Exception as e:
            self.logger.error("Error storing consumption data", error=str(e))

    async def _process_message(self, message: AgentMessage):
        """Process incoming messages specific to consumer agent."""
        if message.message_type == "energy_forecast":
            await self._handle_energy_forecast(message)
        elif message.message_type == "trade_executed":
            await self._handle_trade_executed(message)
        elif message.message_type == "bid_accepted":
            await self._handle_bid_accepted(message)
        elif message.message_type == "bid_rejected":
            await self._handle_bid_rejected(message)
        elif message.message_type == "demand_response_signal":
            await self._handle_demand_response_signal(message)
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
            
            # Add to completed purchases
            self.completed_purchases.append(trade)
            
            # Update metrics
            quantity = trade.get('quantity_mw', 0)
            price = trade.get('price_per_mwh', 0)
            cost = quantity * price
            
            self.total_energy_purchased += quantity
            self.total_cost += cost
            
            # Remove from active bids
            bid_id = trade.get('bid_id')
            self.active_bids = [b for b in self.active_bids if b.get('bid_id') != bid_id]
            
            self.logger.info("Trade executed", 
                           trade_id=trade_id,
                           cost=cost,
                           total_cost=self.total_cost)
            
        except Exception as e:
            self.logger.error("Error handling trade execution", error=str(e))

    async def _handle_bid_accepted(self, message: AgentMessage):
        """Handle bid acceptance notifications."""
        try:
            bid = message.payload
            bid_id = bid.get('bid_id')
            
            self.logger.info("Bid accepted", bid_id=bid_id)
            
        except Exception as e:
            self.logger.error("Error handling bid acceptance", error=str(e))

    async def _handle_bid_rejected(self, message: AgentMessage):
        """Handle bid rejection notifications."""
        try:
            bid = message.payload
            bid_id = bid.get('bid_id')
            reason = bid.get('reason', 'unknown')
            
            # Remove from active bids
            self.active_bids = [b for b in self.active_bids if b.get('bid_id') != bid_id]
            
            self.logger.info("Bid rejected", 
                           bid_id=bid_id,
                           reason=reason)
            
        except Exception as e:
            self.logger.error("Error handling bid rejection", error=str(e))

    async def _handle_demand_response_signal(self, message: AgentMessage):
        """Handle demand response signals from grid operator."""
        try:
            signal = message.payload
            target_reduction = signal.get('target_reduction_mw', 0)
            duration_minutes = signal.get('duration_minutes', 30)
            incentive_rate = signal.get('incentive_rate', 0.1)
            
            if self.consumer_config.demand_response_enabled and target_reduction > 0:
                # Activate demand response
                self.demand_response_active = True
                self.demand_response_target = min(target_reduction, self.current_consumption * 0.3)
                self.demand_response_duration = timedelta(minutes=duration_minutes)
                
                self.logger.info("Demand response signal received", 
                               target_reduction=self.demand_response_target,
                               duration=self.demand_response_duration,
                               incentive_rate=incentive_rate)
            
        except Exception as e:
            self.logger.error("Error handling demand response signal", error=str(e))

    async def get_status(self) -> Dict[str, Any]:
        """Get consumer agent status."""
        status = await super().get_status()
        status.update({
            'consumption_status': {
                'current_consumption_mw': self.current_consumption,
                'battery_level_mwh': self.battery_level,
                'available_battery_capacity_mwh': self.available_battery_capacity,
                'current_shift': self.current_shift,
                'demand_response_active': self.demand_response_active
            },
            'trading_status': {
                'current_market_price': self.current_market_price,
                'active_bids_count': len(self.active_bids),
                'completed_purchases_count': len(self.completed_purchases),
                'total_energy_purchased_mwh': self.total_energy_purchased,
                'total_cost': self.total_cost
            },
            'optimization_metrics': {
                'energy_cost_savings': self.energy_cost_savings,
                'peak_shaving_savings': self.peak_shaving_savings,
                'demand_response_revenue': self.demand_response_revenue,
                'forecast_data_available': self.forecast_data is not None
            }
        })
        return status
