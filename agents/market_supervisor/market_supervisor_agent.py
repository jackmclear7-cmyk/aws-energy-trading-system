"""
Market Supervisor Agent for Energy Trading System

This agent is the central orchestrator of the energy market. It receives all
buy/sell orders, matches them, determines market-clearing prices, and
facilitates trades between producers and consumers.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict
import heapq

from ..base_agent import BaseAgent, AgentConfig, AgentMessage


class MarketSupervisorConfig(AgentConfig):
    """Configuration specific to the Market Supervisor Agent."""
    market_clearing_interval_minutes: int = 1  # How often to clear the market
    max_order_age_minutes: int = 30  # Maximum age of orders before expiration
    price_discovery_method: str = "uniform_pricing"  # uniform_pricing or pay_as_bid
    min_trade_size_mw: float = 1.0  # Minimum trade size
    max_trade_size_mw: float = 1000.0  # Maximum trade size
    market_fee_percentage: float = 0.001  # 0.1% market fee
    emergency_stop_threshold: float = 0.8  # Stop trading if supply/demand ratio < 0.8


class MarketOrder:
    """Represents a market order (bid or offer)."""
    
    def __init__(self, order_id: str, order_type: str, agent_id: str, 
                 quantity_mw: float, price_per_mwh: float, timestamp: datetime,
                 priority: int = 5, valid_until: Optional[datetime] = None):
        self.order_id = order_id
        self.order_type = order_type  # 'bid' or 'offer'
        self.agent_id = agent_id
        self.quantity_mw = quantity_mw
        self.price_per_mwh = price_per_mwh
        self.timestamp = timestamp
        self.priority = priority
        self.valid_until = valid_until or (timestamp + timedelta(minutes=30))
        self.filled_quantity = 0.0
        self.status = 'active'  # active, partially_filled, filled, expired, cancelled
        
    def is_valid(self) -> bool:
        """Check if the order is still valid."""
        return datetime.now(timezone.utc) <= self.valid_until and self.status == 'active'
    
    def can_fill(self, quantity: float) -> bool:
        """Check if the order can be filled with the given quantity."""
        return self.filled_quantity + quantity <= self.quantity_mw
    
    def fill(self, quantity: float):
        """Fill the order with the given quantity."""
        self.filled_quantity += quantity
        if self.filled_quantity >= self.quantity_mw:
            self.status = 'filled'
        elif self.filled_quantity > 0:
            self.status = 'partially_filled'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order to dictionary format."""
        return {
            'order_id': self.order_id,
            'order_type': self.order_type,
            'agent_id': self.agent_id,
            'quantity_mw': self.quantity_mw,
            'price_per_mwh': self.price_per_mwh,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority,
            'valid_until': self.valid_until.isoformat(),
            'filled_quantity': self.filled_quantity,
            'status': self.status
        }


class MarketSupervisorAgent(BaseAgent):
    """
    Market Supervisor Agent that orchestrates the energy market.
    
    Responsibilities:
    - Receive and validate buy/sell orders
    - Match orders based on price and time priority
    - Determine market-clearing prices
    - Execute trades and notify participants
    - Maintain market order book
    - Monitor market health and stability
    """

    def __init__(self, config: MarketSupervisorConfig):
        super().__init__(config)
        self.market_config = config
        
        # Market state
        self.order_book: Dict[str, MarketOrder] = {}
        self.bids: List[MarketOrder] = []  # Buy orders (max heap)
        self.offers: List[MarketOrder] = []  # Sell orders (min heap)
        
        # Market metrics
        self.market_clearing_price: float = 50.0
        self.last_clearing_time: Optional[datetime] = None
        self.total_volume_traded: float = 0.0
        self.total_trades_executed: int = 0
        self.market_volatility: float = 0.0
        
        # Trading session
        self.session_id: str = str(uuid.uuid4())
        self.session_start_time: datetime = datetime.now(timezone.utc)
        self.is_trading_active: bool = True
        
        # Market health monitoring
        self.supply_demand_ratio: float = 1.0
        self.price_spread: float = 0.0
        self.order_flow_rate: float = 0.0
        
        # Performance metrics
        self.average_trade_size: float = 0.0
        self.market_efficiency: float = 0.0
        self.liquidity_score: float = 0.0
        
        self.logger.info("Market Supervisor Agent initialized", config=config.dict())

    async def _start_agent_specific(self):
        """Start market supervisor-specific tasks."""
        # Start market clearing loop
        asyncio.create_task(self._market_clearing_loop())
        
        # Start market health monitoring
        asyncio.create_task(self._market_health_monitoring_loop())
        
        # Start order book maintenance
        asyncio.create_task(self._order_book_maintenance_loop())
        
        # Start performance reporting
        asyncio.create_task(self._performance_reporting_loop())
        
        self.logger.info("Market Supervisor Agent started")

    async def _stop_agent_specific(self):
        """Stop market supervisor-specific tasks."""
        self.logger.info("Market Supervisor Agent stopped")

    async def _market_clearing_loop(self):
        """Main market clearing loop."""
        while self.is_running:
            try:
                if self.is_trading_active:
                    # Clear the market
                    await self._clear_market()
                    
                    # Update market metrics
                    await self._update_market_metrics()
                    
                    # Store market data
                    await self._store_market_data()
                
                # Wait before next clearing
                await asyncio.sleep(self.market_config.market_clearing_interval_minutes * 60)
                
            except Exception as e:
                self.logger.error("Error in market clearing loop", error=str(e))
                await asyncio.sleep(60)

    async def _market_health_monitoring_loop(self):
        """Monitor market health and stability."""
        while self.is_running:
            try:
                # Calculate market health metrics
                await self._calculate_market_health()
                
                # Check for emergency conditions
                await self._check_emergency_conditions()
                
                # Wait before next check
                await asyncio.sleep(60)  # 1 minute intervals
                
            except Exception as e:
                self.logger.error("Error in market health monitoring", error=str(e))
                await asyncio.sleep(60)

    async def _order_book_maintenance_loop(self):
        """Maintain order book and clean up expired orders."""
        while self.is_running:
            try:
                # Clean up expired orders
                await self._cleanup_expired_orders()
                
                # Rebalance order heaps
                await self._rebalance_order_heaps()
                
                # Wait before next maintenance
                await asyncio.sleep(30)  # 30 second intervals
                
            except Exception as e:
                self.logger.error("Error in order book maintenance", error=str(e))
                await asyncio.sleep(60)

    async def _performance_reporting_loop(self):
        """Generate and broadcast performance reports."""
        while self.is_running:
            try:
                # Generate performance report
                report = await self._generate_performance_report()
                
                # Broadcast to all agents
                await self._broadcast_performance_report(report)
                
                # Wait before next report
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error("Error in performance reporting", error=str(e))
                await asyncio.sleep(60)

    async def _clear_market(self):
        """Clear the market by matching orders and executing trades."""
        try:
            if not self.bids or not self.offers:
                self.logger.debug("No orders to match")
                return
            
            # Sort orders by priority and price
            sorted_bids = sorted(self.bids, key=lambda x: (-x.priority, -x.price_per_mwh, x.timestamp))
            sorted_offers = sorted(self.offers, key=lambda x: (-x.priority, x.price_per_mwh, x.timestamp))
            
            trades_executed = []
            
            # Match orders
            for bid in sorted_bids:
                if not bid.is_valid():
                    continue
                    
                for offer in sorted_offers:
                    if not offer.is_valid():
                        continue
                    
                    # Check if orders can match
                    if bid.price_per_mwh >= offer.price_per_mwh:
                        # Calculate trade quantity
                        trade_quantity = min(
                            bid.quantity_mw - bid.filled_quantity,
                            offer.quantity_mw - offer.filled_quantity
                        )
                        
                        if trade_quantity >= self.market_config.min_trade_size_mw:
                            # Execute trade
                            trade = await self._execute_trade(bid, offer, trade_quantity)
                            trades_executed.append(trade)
                            
                            # Update order status
                            bid.fill(trade_quantity)
                            offer.fill(trade_quantity)
                            
                            # Remove filled orders from heaps
                            if bid.status == 'filled':
                                self.bids.remove(bid)
                            if offer.status == 'filled':
                                self.offers.remove(offer)
                            
                            # Break if bid is filled
                            if bid.status == 'filled':
                                break
            
            # Update market clearing price
            if trades_executed:
                await self._update_market_clearing_price(trades_executed)
                self.last_clearing_time = datetime.now(timezone.utc)
                
                self.logger.info("Market cleared", 
                               trades_executed=len(trades_executed),
                               total_volume=sum(t['quantity_mw'] for t in trades_executed),
                               clearing_price=self.market_clearing_price)
            
        except Exception as e:
            self.logger.error("Error clearing market", error=str(e))

    async def _execute_trade(self, bid: MarketOrder, offer: MarketOrder, quantity: float) -> Dict[str, Any]:
        """Execute a trade between a bid and offer."""
        try:
            # Determine trade price based on pricing method
            if self.market_config.price_discovery_method == "uniform_pricing":
                trade_price = (bid.price_per_mwh + offer.price_per_mwh) / 2
            else:  # pay_as_bid
                trade_price = bid.price_per_mwh
            
            # Calculate market fee
            market_fee = quantity * trade_price * self.market_config.market_fee_percentage
            
            # Create trade record
            trade = {
                'trade_id': f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
                'bid_id': bid.order_id,
                'offer_id': offer.order_id,
                'buyer_id': bid.agent_id,
                'seller_id': offer.agent_id,
                'quantity_mw': quantity,
                'price_per_mwh': trade_price,
                'total_value': quantity * trade_price,
                'market_fee': market_fee,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'session_id': self.session_id
            }
            
            # Update metrics
            self.total_volume_traded += quantity
            self.total_trades_executed += 1
            
            # Notify participants
            await self._notify_trade_execution(trade)
            
            # Store trade data
            await self._store_trade_data(trade)
            
            return trade
            
        except Exception as e:
            self.logger.error("Error executing trade", error=str(e))
            raise

    async def _update_market_clearing_price(self, trades: List[Dict[str, Any]]):
        """Update the market clearing price based on executed trades."""
        try:
            if not trades:
                return
            
            # Calculate volume-weighted average price
            total_volume = sum(trade['quantity_mw'] for trade in trades)
            weighted_price = sum(
                trade['quantity_mw'] * trade['price_per_mwh'] for trade in trades
            )
            
            new_clearing_price = weighted_price / total_volume
            
            # Calculate price volatility
            if self.market_clearing_price > 0:
                price_change = abs(new_clearing_price - self.market_clearing_price) / self.market_clearing_price
                self.market_volatility = (self.market_volatility * 0.9) + (price_change * 0.1)
            
            self.market_clearing_price = new_clearing_price
            
        except Exception as e:
            self.logger.error("Error updating market clearing price", error=str(e))

    async def _notify_trade_execution(self, trade: Dict[str, Any]):
        """Notify participants of trade execution."""
        try:
            # Notify buyer
            await self.send_message(
                recipient_id=trade['buyer_id'],
                message_type='trade_executed',
                payload=trade,
                priority=8
            )
            
            # Notify seller
            await self.send_message(
                recipient_id=trade['seller_id'],
                message_type='trade_executed',
                payload=trade,
                priority=8
            )
            
            # Broadcast trade to all agents for transparency
            await self.send_message(
                recipient_id='broadcast',
                message_type='trade_announcement',
                payload=trade,
                priority=5
            )
            
        except Exception as e:
            self.logger.error("Error notifying trade execution", error=str(e))

    async def _calculate_market_health(self):
        """Calculate market health metrics."""
        try:
            # Calculate supply-demand ratio
            total_supply = sum(order.quantity_mw for order in self.offers if order.is_valid())
            total_demand = sum(order.quantity_mw for order in self.bids if order.is_valid())
            
            if total_demand > 0:
                self.supply_demand_ratio = total_supply / total_demand
            else:
                self.supply_demand_ratio = 1.0
            
            # Calculate price spread
            if self.bids and self.offers:
                best_bid = max(order.price_per_mwh for order in self.bids if order.is_valid())
                best_offer = min(order.price_per_mwh for order in self.offers if order.is_valid())
                self.price_spread = best_offer - best_bid
            else:
                self.price_spread = 0.0
            
            # Calculate order flow rate
            current_time = datetime.now(timezone.utc)
            recent_orders = [
                order for order in self.order_book.values()
                if (current_time - order.timestamp).total_seconds() < 300  # Last 5 minutes
            ]
            self.order_flow_rate = len(recent_orders) / 5.0  # Orders per minute
            
            # Calculate liquidity score
            if self.market_clearing_price > 0:
                self.liquidity_score = min(1.0, self.total_volume_traded / (self.market_clearing_price * 100))
            else:
                self.liquidity_score = 0.0
            
            # Calculate market efficiency
            if self.total_trades_executed > 0:
                self.market_efficiency = min(1.0, self.total_volume_traded / (self.total_trades_executed * 10))
            else:
                self.market_efficiency = 0.0
            
            # Calculate average trade size
            if self.total_trades_executed > 0:
                self.average_trade_size = self.total_volume_traded / self.total_trades_executed
            else:
                self.average_trade_size = 0.0
            
        except Exception as e:
            self.logger.error("Error calculating market health", error=str(e))

    async def _check_emergency_conditions(self):
        """Check for emergency market conditions."""
        try:
            # Check supply-demand imbalance
            if self.supply_demand_ratio < self.market_config.emergency_stop_threshold:
                if self.is_trading_active:
                    self.is_trading_active = False
                    self.logger.warning("Trading stopped due to supply-demand imbalance", 
                                      ratio=self.supply_demand_ratio)
                    
                    # Notify all agents
                    await self._broadcast_emergency_signal("supply_demand_imbalance")
            
            # Check for extreme price volatility
            if self.market_volatility > 0.5:  # 50% price change
                self.logger.warning("High market volatility detected", 
                                  volatility=self.market_volatility)
                
                # Notify all agents
                await self._broadcast_emergency_signal("high_volatility")
            
            # Check for order book imbalance
            if len(self.bids) > len(self.offers) * 3 or len(self.offers) > len(self.bids) * 3:
                self.logger.warning("Order book imbalance detected", 
                                  bid_count=len(self.bids),
                                  offer_count=len(self.offers))
                
        except Exception as e:
            self.logger.error("Error checking emergency conditions", error=str(e))

    async def _cleanup_expired_orders(self):
        """Clean up expired orders from the order book."""
        try:
            current_time = datetime.now(timezone.utc)
            expired_orders = []
            
            for order in self.order_book.values():
                if not order.is_valid():
                    expired_orders.append(order.order_id)
                    
                    # Notify agent of expired order
                    if order.order_type == 'bid':
                        await self.send_message(
                            recipient_id=order.agent_id,
                            message_type='bid_expired',
                            payload={'bid_id': order.order_id, 'reason': 'expired'}
                        )
                    else:
                        await self.send_message(
                            recipient_id=order.agent_id,
                            message_type='offer_expired',
                            payload={'offer_id': order.order_id, 'reason': 'expired'}
                        )
            
            # Remove expired orders
            for order_id in expired_orders:
                order = self.order_book.pop(order_id, None)
                if order:
                    if order in self.bids:
                        self.bids.remove(order)
                    if order in self.offers:
                        self.offers.remove(order)
            
            if expired_orders:
                self.logger.info("Expired orders cleaned up", count=len(expired_orders))
            
        except Exception as e:
            self.logger.error("Error cleaning up expired orders", error=str(e))

    async def _rebalance_order_heaps(self):
        """Rebalance the order heaps for efficient matching."""
        try:
            # Rebuild bid heap (max heap by price, then priority, then time)
            self.bids = sorted(
                [order for order in self.bids if order.is_valid()],
                key=lambda x: (-x.priority, -x.price_per_mwh, x.timestamp)
            )
            
            # Rebuild offer heap (min heap by price, then priority, then time)
            self.offers = sorted(
                [order for order in self.offers if order.is_valid()],
                key=lambda x: (-x.priority, x.price_per_mwh, x.timestamp)
            )
            
        except Exception as e:
            self.logger.error("Error rebalancing order heaps", error=str(e))

    async def _generate_performance_report(self) -> Dict[str, Any]:
        """Generate a performance report for the market."""
        try:
            report = {
                'session_id': self.session_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'market_metrics': {
                    'clearing_price': self.market_clearing_price,
                    'total_volume_traded': self.total_volume_traded,
                    'total_trades_executed': self.total_trades_executed,
                    'market_volatility': self.market_volatility,
                    'last_clearing_time': self.last_clearing_time.isoformat() if self.last_clearing_time else None
                },
                'market_health': {
                    'supply_demand_ratio': self.supply_demand_ratio,
                    'price_spread': self.price_spread,
                    'order_flow_rate': self.order_flow_rate,
                    'liquidity_score': self.liquidity_score,
                    'market_efficiency': self.market_efficiency
                },
                'order_book_status': {
                    'total_orders': len(self.order_book),
                    'active_bids': len(self.bids),
                    'active_offers': len(self.offers),
                    'average_trade_size': self.average_trade_size
                },
                'trading_status': {
                    'is_trading_active': self.is_trading_active,
                    'session_duration_minutes': (datetime.now(timezone.utc) - self.session_start_time).total_seconds() / 60
                }
            }
            
            return report
            
        except Exception as e:
            self.logger.error("Error generating performance report", error=str(e))
            return {}

    async def _broadcast_performance_report(self, report: Dict[str, Any]):
        """Broadcast performance report to all agents."""
        try:
            # Send to all known agents
            agents_to_notify = [
                'forecasting_agent',
                'producer_agent',
                'consumer_agent',
                'grid_optimization_agent'
            ]
            
            for agent_id in agents_to_notify:
                await self.send_message(
                    recipient_id=agent_id,
                    message_type='market_performance_report',
                    payload=report,
                    priority=3
                )
            
            self.logger.info("Performance report broadcasted", 
                           recipient_count=len(agents_to_notify))
            
        except Exception as e:
            self.logger.error("Error broadcasting performance report", error=str(e))

    async def _broadcast_emergency_signal(self, signal_type: str):
        """Broadcast emergency signal to all agents."""
        try:
            signal = {
                'signal_type': signal_type,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'market_conditions': {
                    'supply_demand_ratio': self.supply_demand_ratio,
                    'market_volatility': self.market_volatility,
                    'price_spread': self.price_spread
                }
            }
            
            # Send to all agents
            agents_to_notify = [
                'forecasting_agent',
                'producer_agent',
                'consumer_agent',
                'grid_optimization_agent'
            ]
            
            for agent_id in agents_to_notify:
                await self.send_message(
                    recipient_id=agent_id,
                    message_type='emergency_signal',
                    payload=signal,
                    priority=9  # Highest priority
                )
            
            self.logger.warning("Emergency signal broadcasted", 
                              signal_type=signal_type,
                              recipient_count=len(agents_to_notify))
            
        except Exception as e:
            self.logger.error("Error broadcasting emergency signal", error=str(e))

    async def _store_market_data(self):
        """Store market data in Timestream."""
        try:
            records = []
            timestamp = datetime.now(timezone.utc)
            
            # Store market metrics
            records.extend([
                {
                    'measure_name': 'market_clearing_price',
                    'value': self.market_clearing_price,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'total_volume_traded',
                    'value': self.total_volume_traded,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'total_trades_executed',
                    'value': self.total_trades_executed,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'market_volatility',
                    'value': self.market_volatility,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'supply_demand_ratio',
                    'value': self.supply_demand_ratio,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'price_spread',
                    'value': self.price_spread,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'order_flow_rate',
                    'value': self.order_flow_rate,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'liquidity_score',
                    'value': self.liquidity_score,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'market_efficiency',
                    'value': self.market_efficiency,
                    'timestamp': timestamp
                }
            ])
            
            if records:
                await self.store_timeseries_data('market_metrics', records)
                
        except Exception as e:
            self.logger.error("Error storing market data", error=str(e))

    async def _store_trade_data(self, trade: Dict[str, Any]):
        """Store trade data in Timestream."""
        try:
            records = []
            timestamp = datetime.fromisoformat(trade['timestamp'])
            
            # Store trade metrics
            records.extend([
                {
                    'measure_name': 'trade_quantity',
                    'value': trade['quantity_mw'],
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'trade_price',
                    'value': trade['price_per_mwh'],
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'trade_value',
                    'value': trade['total_value'],
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'market_fee',
                    'value': trade['market_fee'],
                    'timestamp': timestamp
                }
            ])
            
            if records:
                await self.store_timeseries_data('trade_metrics', records)
                
        except Exception as e:
            self.logger.error("Error storing trade data", error=str(e))

    async def _process_message(self, message: AgentMessage):
        """Process incoming messages specific to market supervisor agent."""
        if message.message_type == "energy_offer":
            await self._handle_energy_offer(message)
        elif message.message_type == "energy_bid":
            await self._handle_energy_bid(message)
        elif message.message_type == "offer_expired":
            await self._handle_offer_expired(message)
        elif message.message_type == "bid_expired":
            await self._handle_bid_expired(message)
        elif message.message_type == "market_status_request":
            await self._handle_market_status_request(message)
        else:
            await super()._process_message(message)

    async def _handle_energy_offer(self, message: AgentMessage):
        """Handle energy offers from producers."""
        try:
            offer_data = message.payload
            
            # Create market order
            order = MarketOrder(
                order_id=offer_data['offer_id'],
                order_type='offer',
                agent_id=offer_data['producer_id'],
                quantity_mw=offer_data['quantity_mw'],
                price_per_mwh=offer_data['price_per_mwh'],
                timestamp=datetime.fromisoformat(offer_data['timestamp']),
                priority=offer_data.get('priority', 5),
                valid_until=datetime.fromisoformat(offer_data['valid_until'])
            )
            
            # Add to order book
            self.order_book[order.order_id] = order
            self.offers.append(order)
            
            # Rebalance offer heap
            self.offers.sort(key=lambda x: (-x.priority, x.price_per_mwh, x.timestamp))
            
            self.logger.info("Energy offer received", 
                           offer_id=order.order_id,
                           quantity=order.quantity_mw,
                           price=order.price_per_mwh)
            
        except Exception as e:
            self.logger.error("Error handling energy offer", error=str(e))

    async def _handle_energy_bid(self, message: AgentMessage):
        """Handle energy bids from consumers."""
        try:
            bid_data = message.payload
            
            # Create market order
            order = MarketOrder(
                order_id=bid_data['bid_id'],
                order_type='bid',
                agent_id=bid_data['consumer_id'],
                quantity_mw=bid_data['quantity_mw'],
                price_per_mwh=bid_data['price_per_mwh'],
                timestamp=datetime.fromisoformat(bid_data['timestamp']),
                priority=bid_data.get('priority', 5),
                valid_until=datetime.fromisoformat(bid_data['valid_until'])
            )
            
            # Add to order book
            self.order_book[order.order_id] = order
            self.bids.append(order)
            
            # Rebalance bid heap
            self.bids.sort(key=lambda x: (-x.priority, -x.price_per_mwh, x.timestamp))
            
            self.logger.info("Energy bid received", 
                           bid_id=order.order_id,
                           quantity=order.quantity_mw,
                           price=order.price_per_mwh)
            
        except Exception as e:
            self.logger.error("Error handling energy bid", error=str(e))

    async def _handle_offer_expired(self, message: AgentMessage):
        """Handle expired offer notifications."""
        try:
            offer_data = message.payload
            offer_id = offer_data['offer_id']
            
            # Remove from order book
            if offer_id in self.order_book:
                order = self.order_book.pop(offer_id)
                if order in self.offers:
                    self.offers.remove(order)
                
                self.logger.info("Offer expired and removed", offer_id=offer_id)
            
        except Exception as e:
            self.logger.error("Error handling expired offer", error=str(e))

    async def _handle_bid_expired(self, message: AgentMessage):
        """Handle expired bid notifications."""
        try:
            bid_data = message.payload
            bid_id = bid_data['bid_id']
            
            # Remove from order book
            if bid_id in self.order_book:
                order = self.order_book.pop(bid_id)
                if order in self.bids:
                    self.bids.remove(order)
                
                self.logger.info("Bid expired and removed", bid_id=bid_id)
            
        except Exception as e:
            self.logger.error("Error handling expired bid", error=str(e))

    async def _handle_market_status_request(self, message: AgentMessage):
        """Handle market status requests."""
        try:
            # Generate current market status
            status = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'is_trading_active': self.is_trading_active,
                'market_clearing_price': self.market_clearing_price,
                'order_book_summary': {
                    'total_orders': len(self.order_book),
                    'active_bids': len(self.bids),
                    'active_offers': len(self.offers)
                },
                'recent_activity': {
                    'total_volume_traded': self.total_volume_traded,
                    'total_trades_executed': self.total_trades_executed,
                    'last_clearing_time': self.last_clearing_time.isoformat() if self.last_clearing_time else None
                }
            }
            
            # Send status response
            await self.send_message(
                recipient_id=message.sender_id,
                message_type='market_status_response',
                payload=status,
                correlation_id=message.correlation_id
            )
            
        except Exception as e:
            self.logger.error("Error handling market status request", error=str(e))

    async def get_status(self) -> Dict[str, Any]:
        """Get market supervisor agent status."""
        status = await super().get_status()
        status.update({
            'market_status': {
                'is_trading_active': self.is_trading_active,
                'session_id': self.session_id,
                'session_start_time': self.session_start_time.isoformat(),
                'market_clearing_price': self.market_clearing_price,
                'last_clearing_time': self.last_clearing_time.isoformat() if self.last_clearing_time else None
            },
            'order_book_status': {
                'total_orders': len(self.order_book),
                'active_bids': len(self.bids),
                'active_offers': len(self.offers),
                'order_book_size': len(self.order_book)
            },
            'trading_metrics': {
                'total_volume_traded': self.total_volume_traded,
                'total_trades_executed': self.total_trades_executed,
                'average_trade_size': self.average_trade_size,
                'market_volatility': self.market_volatility
            },
            'market_health': {
                'supply_demand_ratio': self.supply_demand_ratio,
                'price_spread': self.price_spread,
                'order_flow_rate': self.order_flow_rate,
                'liquidity_score': self.liquidity_score,
                'market_efficiency': self.market_efficiency
            }
        })
        return status
