"""
Grid Optimization Agent for Energy Trading System

This agent monitors overall grid stability, coordinates demand response programs,
and ensures the energy grid operates efficiently and reliably.
"""

import asyncio
import json
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..base_agent import BaseAgent, AgentConfig, AgentMessage


class GridOptimizationConfig(AgentConfig):
    """Configuration specific to the Grid Optimization Agent."""
    grid_stability_threshold: float = 0.95  # Minimum grid stability score
    demand_response_threshold: float = 0.8  # Activate DR when supply/demand < 0.8
    frequency_deviation_threshold: float = 0.1  # Hz deviation threshold
    voltage_deviation_threshold: float = 0.05  # Voltage deviation threshold
    monitoring_interval_seconds: int = 30  # Grid monitoring frequency
    emergency_response_time_seconds: int = 10  # Emergency response time
    max_demand_response_mw: float = 200.0  # Maximum demand response capacity


class GridOptimizationAgent(BaseAgent):
    """
    Grid Optimization Agent that monitors and optimizes grid stability.
    
    Responsibilities:
    - Monitor grid frequency, voltage, and stability metrics
    - Coordinate demand response programs
    - Detect and respond to grid emergencies
    - Optimize grid operations for efficiency
    - Coordinate with other agents for grid stability
    """

    def __init__(self, config: GridOptimizationConfig):
        super().__init__(config)
        self.grid_config = config
        
        # Grid state
        self.grid_frequency: float = 60.0  # Hz (nominal)
        self.grid_voltage: float = 120.0  # V (nominal)
        self.grid_stability_score: float = 1.0
        self.grid_load: float = 0.0  # MW
        self.grid_supply: float = 0.0  # MW
        
        # Grid metrics
        self.frequency_history: List[Tuple[datetime, float]] = []
        self.voltage_history: List[Tuple[datetime, float]] = []
        self.stability_history: List[Tuple[datetime, float]] = []
        self.load_history: List[Tuple[datetime, float]] = []
        
        # Demand response state
        self.demand_response_active: bool = False
        self.demand_response_participants: List[str] = []
        self.demand_response_target: float = 0.0
        self.demand_response_duration: timedelta = timedelta(minutes=0)
        
        # Emergency state
        self.emergency_mode: bool = False
        self.emergency_type: Optional[str] = None
        self.emergency_start_time: Optional[datetime] = None
        
        # Grid optimization
        self.optimization_algorithms: List[str] = ['frequency_regulation', 'voltage_control', 'load_balancing']
        self.optimization_status: Dict[str, bool] = {alg: False for alg in self.optimization_algorithms}
        
        # Performance metrics
        self.grid_uptime: float = 1.0
        self.emergency_response_count: int = 0
        self.demand_response_savings: float = 0.0
        
        self.logger.info("Grid Optimization Agent initialized", config=config.dict())

    async def _start_agent_specific(self):
        """Start grid optimization-specific tasks."""
        # Start grid monitoring
        asyncio.create_task(self._grid_monitoring_loop())
        
        # Start demand response coordination
        asyncio.create_task(self._demand_response_coordination_loop())
        
        # Start emergency monitoring
        asyncio.create_task(self._emergency_monitoring_loop())
        
        # Start grid optimization
        asyncio.create_task(self._grid_optimization_loop())
        
        # Start performance reporting
        asyncio.create_task(self._performance_reporting_loop())
        
        self.logger.info("Grid Optimization Agent started")

    async def _stop_agent_specific(self):
        """Stop grid optimization-specific tasks."""
        self.logger.info("Grid Optimization Agent stopped")

    async def _grid_monitoring_loop(self):
        """Main grid monitoring loop."""
        while self.is_running:
            try:
                # Collect grid metrics
                await self._collect_grid_metrics()
                
                # Calculate grid stability
                await self._calculate_grid_stability()
                
                # Check for grid issues
                await self._check_grid_issues()
                
                # Store grid data
                await self._store_grid_data()
                
                # Wait before next monitoring cycle
                await asyncio.sleep(self.grid_config.monitoring_interval_seconds)
                
            except Exception as e:
                self.logger.error("Error in grid monitoring loop", error=str(e))
                await asyncio.sleep(60)

    async def _demand_response_coordination_loop(self):
        """Coordinate demand response programs."""
        while self.is_running:
            try:
                # Check if demand response is needed
                if self._should_activate_demand_response():
                    await self._activate_demand_response()
                
                # Update demand response status
                await self._update_demand_response_status()
                
                # Coordinate with participants
                await self._coordinate_demand_response()
                
                # Wait before next coordination cycle
                await asyncio.sleep(60)  # 1 minute intervals
                
            except Exception as e:
                self.logger.error("Error in demand response coordination", error=str(e))
                await asyncio.sleep(60)

    async def _emergency_monitoring_loop(self):
        """Monitor for grid emergencies."""
        while self.is_running:
            try:
                # Check for emergency conditions
                if self._detect_emergency_conditions():
                    await self._activate_emergency_mode()
                
                # Update emergency status
                await self._update_emergency_status()
                
                # Wait before next check
                await asyncio.sleep(10)  # 10 second intervals for emergencies
                
            except Exception as e:
                self.logger.error("Error in emergency monitoring", error=str(e))
                await asyncio.sleep(60)

    async def _grid_optimization_loop(self):
        """Optimize grid operations."""
        while self.is_running:
            try:
                # Run frequency regulation
                await self._optimize_frequency_regulation()
                
                # Run voltage control
                await self._optimize_voltage_control()
                
                # Run load balancing
                await self._optimize_load_balancing()
                
                # Wait before next optimization cycle
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error("Error in grid optimization", error=str(e))
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
                await asyncio.sleep(600)  # 10 minutes
                
            except Exception as e:
                self.logger.error("Error in performance reporting", error=str(e))
                await asyncio.sleep(60)

    async def _collect_grid_metrics(self):
        """Collect current grid metrics using MCP tools."""
        try:
            # In a real implementation, this would call grid monitoring APIs
            # For now, we'll simulate grid metrics
            
            # Simulate frequency variations
            frequency_variation = np.random.normal(0, 0.1)  # ±0.1 Hz variation
            self.grid_frequency = 60.0 + frequency_variation
            
            # Simulate voltage variations
            voltage_variation = np.random.normal(0, 2.0)  # ±2V variation
            self.grid_voltage = 120.0 + voltage_variation
            
            # Simulate load and supply
            base_load = 1000.0  # MW
            load_variation = np.random.normal(0, 50.0)  # ±50 MW variation
            self.grid_load = max(0, base_load + load_variation)
            
            # Supply follows load with some variation
            supply_variation = np.random.normal(0, 30.0)  # ±30 MW variation
            self.grid_supply = self.grid_load + supply_variation
            
            # Store historical data
            current_time = datetime.now(timezone.utc)
            self.frequency_history.append((current_time, self.grid_frequency))
            self.voltage_history.append((current_time, self.grid_voltage))
            self.load_history.append((current_time, self.grid_load))
            
            # Keep only recent history (last 24 hours)
            cutoff_time = current_time - timedelta(hours=24)
            self.frequency_history = [(t, v) for t, v in self.frequency_history if t > cutoff_time]
            self.voltage_history = [(t, v) for t, v in self.voltage_history if t > cutoff_time]
            self.load_history = [(t, v) for t, v in self.load_history if t > cutoff_time]
            
        except Exception as e:
            self.logger.error("Error collecting grid metrics", error=str(e))

    async def _calculate_grid_stability(self):
        """Calculate overall grid stability score."""
        try:
            # Calculate frequency stability (0-1 scale)
            frequency_deviation = abs(self.grid_frequency - 60.0) / 60.0
            frequency_stability = max(0, 1.0 - frequency_deviation / self.grid_config.frequency_deviation_threshold)
            
            # Calculate voltage stability (0-1 scale)
            voltage_deviation = abs(self.grid_voltage - 120.0) / 120.0
            voltage_stability = max(0, 1.0 - voltage_deviation / self.grid_config.voltage_deviation_threshold)
            
            # Calculate supply-demand stability (0-1 scale)
            if self.grid_load > 0:
                supply_demand_ratio = self.grid_supply / self.grid_load
                supply_demand_stability = min(1.0, supply_demand_ratio)
            else:
                supply_demand_stability = 1.0
            
            # Calculate overall stability score (weighted average)
            self.grid_stability_score = (
                frequency_stability * 0.4 +
                voltage_stability * 0.3 +
                supply_demand_stability * 0.3
            )
            
            # Store stability history
            current_time = datetime.now(timezone.utc)
            self.stability_history.append((current_time, self.grid_stability_score))
            
            # Keep only recent history
            cutoff_time = current_time - timedelta(hours=24)
            self.stability_history = [(t, v) for t, v in self.stability_history if t > cutoff_time]
            
            self.logger.debug("Grid stability calculated", 
                            stability_score=self.grid_stability_score,
                            frequency_stability=frequency_stability,
                            voltage_stability=voltage_stability,
                            supply_demand_stability=supply_demand_stability)
            
        except Exception as e:
            self.logger.error("Error calculating grid stability", error=str(e))

    async def _check_grid_issues(self):
        """Check for grid issues and take corrective action."""
        try:
            # Check stability threshold
            if self.grid_stability_score < self.grid_config.grid_stability_threshold:
                self.logger.warning("Grid stability below threshold", 
                                  stability_score=self.grid_stability_score,
                                  threshold=self.grid_config.grid_stability_threshold)
                
                # Take corrective action
                await self._take_corrective_action()
            
            # Check frequency deviation
            if abs(self.grid_frequency - 60.0) > self.grid_config.frequency_deviation_threshold * 60.0:
                self.logger.warning("Grid frequency deviation detected", 
                                  frequency=self.grid_frequency,
                                  deviation=abs(self.grid_frequency - 60.0))
            
            # Check voltage deviation
            if abs(self.grid_voltage - 120.0) > self.grid_config.voltage_deviation_threshold * 120.0:
                self.logger.warning("Grid voltage deviation detected", 
                                  voltage=self.grid_voltage,
                                  deviation=abs(self.grid_voltage - 120.0))
            
            # Check supply-demand balance
            if self.grid_load > 0 and self.grid_supply / self.grid_load < self.grid_config.demand_response_threshold:
                self.logger.warning("Supply-demand imbalance detected", 
                                  ratio=self.grid_supply / self.grid_load,
                                  threshold=self.grid_config.demand_response_threshold)
                
        except Exception as e:
            self.logger.error("Error checking grid issues", error=str(e))

    async def _take_corrective_action(self):
        """Take corrective action for grid issues."""
        try:
            # Determine the type of issue
            if abs(self.grid_frequency - 60.0) > self.grid_config.frequency_deviation_threshold * 60.0:
                # Frequency issue - activate frequency regulation
                await self._activate_frequency_regulation()
            
            elif abs(self.grid_voltage - 120.0) > self.grid_config.voltage_deviation_threshold * 120.0:
                # Voltage issue - activate voltage control
                await self._activate_voltage_control()
            
            elif self.grid_load > 0 and self.grid_supply / self.grid_load < self.grid_config.demand_response_threshold:
                # Supply-demand issue - activate demand response
                await self._activate_demand_response()
            
            self.logger.info("Corrective action taken for grid stability issue")
            
        except Exception as e:
            self.logger.error("Error taking corrective action", error=str(e))

    def _should_activate_demand_response(self) -> bool:
        """Determine if demand response should be activated."""
        try:
            # Check if already active
            if self.demand_response_active:
                return False
            
            # Check supply-demand ratio
            if self.grid_load > 0:
                supply_demand_ratio = self.grid_supply / self.grid_load
                if supply_demand_ratio < self.grid_config.demand_response_threshold:
                    return True
            
            # Check grid stability
            if self.grid_stability_score < self.grid_config.grid_stability_threshold:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error("Error determining demand response activation", error=str(e))
            return False

    async def _activate_demand_response(self):
        """Activate demand response program."""
        try:
            # Calculate target reduction
            if self.grid_load > 0:
                current_ratio = self.grid_supply / self.grid_load
                target_ratio = self.grid_config.demand_response_threshold + 0.1  # Add 10% buffer
                reduction_needed = self.grid_load * (1 - current_ratio / target_ratio)
                self.demand_response_target = min(reduction_needed, self.grid_config.max_demand_response_mw)
            else:
                self.demand_response_target = self.grid_config.max_demand_response_mw
            
            # Set duration (30 minutes)
            self.demand_response_duration = timedelta(minutes=30)
            
            # Activate demand response
            self.demand_response_active = True
            
            # Notify all agents
            await self._broadcast_demand_response_signal()
            
            self.logger.info("Demand response activated", 
                           target_reduction=self.demand_response_target,
                           duration=self.demand_response_duration)
            
        except Exception as e:
            self.logger.error("Error activating demand response", error=str(e))

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
                    
                    # Notify agents that demand response has ended
                    await self._broadcast_demand_response_end()
                    
                    self.logger.info("Demand response ended")
                else:
                    # Reduce remaining duration
                    self.demand_response_duration -= timedelta(minutes=1)
            
        except Exception as e:
            self.logger.error("Error updating demand response status", error=str(e))

    async def _coordinate_demand_response(self):
        """Coordinate demand response with participating agents."""
        try:
            if not self.demand_response_active:
                return
            
            # Get list of participating agents
            participants = ['consumer_agent']  # In a real system, this would be dynamic
            
            # Calculate reduction per participant
            reduction_per_participant = self.demand_response_target / max(len(participants), 1)
            
            # Send demand response signals
            for participant_id in participants:
                signal = {
                    'target_reduction_mw': reduction_per_participant,
                    'duration_minutes': int(self.demand_response_duration.total_seconds() / 60),
                    'incentive_rate': 0.15,  # 15% incentive
                    'priority': 'high'
                }
                
                await self.send_message(
                    recipient_id=participant_id,
                    message_type='demand_response_signal',
                    payload=signal,
                    priority=7
                )
            
            self.logger.debug("Demand response coordinated", 
                            participants=len(participants),
                            reduction_per_participant=reduction_per_participant)
            
        except Exception as e:
            self.logger.error("Error coordinating demand response", error=str(e))

    def _detect_emergency_conditions(self) -> bool:
        """Detect if emergency conditions exist."""
        try:
            # Check for critical frequency deviation
            if abs(self.grid_frequency - 60.0) > 0.5:  # ±0.5 Hz
                return True
            
            # Check for critical voltage deviation
            if abs(self.grid_voltage - 120.0) > 10.0:  # ±10V
                return True
            
            # Check for critical supply-demand imbalance
            if self.grid_load > 0 and self.grid_supply / self.grid_load < 0.7:
                return True
            
            # Check for critical stability score
            if self.grid_stability_score < 0.8:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error("Error detecting emergency conditions", error=str(e))
            return False

    async def _activate_emergency_mode(self):
        """Activate emergency mode for grid protection."""
        try:
            if self.emergency_mode:
                return  # Already in emergency mode
            
            # Determine emergency type
            if abs(self.grid_frequency - 60.0) > 0.5:
                emergency_type = "frequency_emergency"
            elif abs(self.grid_voltage - 120.0) > 10.0:
                emergency_type = "voltage_emergency"
            elif self.grid_load > 0 and self.grid_supply / self.grid_load < 0.7:
                emergency_type = "supply_demand_emergency"
            else:
                emergency_type = "stability_emergency"
            
            # Activate emergency mode
            self.emergency_mode = True
            self.emergency_type = emergency_type
            self.emergency_start_time = datetime.now(timezone.utc)
            self.emergency_response_count += 1
            
            # Take emergency actions
            await self._take_emergency_actions(emergency_type)
            
            # Notify all agents
            await self._broadcast_emergency_signal(emergency_type)
            
            self.logger.warning("Emergency mode activated", 
                              emergency_type=emergency_type,
                              response_count=self.emergency_response_count)
            
        except Exception as e:
            self.logger.error("Error activating emergency mode", error=str(e))

    async def _take_emergency_actions(self, emergency_type: str):
        """Take emergency actions based on emergency type."""
        try:
            if emergency_type == "frequency_emergency":
                # Activate all frequency regulation resources
                await self._activate_emergency_frequency_regulation()
                
            elif emergency_type == "voltage_emergency":
                # Activate all voltage control resources
                await self._activate_emergency_voltage_control()
                
            elif emergency_type == "supply_demand_emergency":
                # Activate maximum demand response
                await self._activate_emergency_demand_response()
                
            elif emergency_type == "stability_emergency":
                # Activate all optimization algorithms
                await self._activate_emergency_optimization()
            
            self.logger.info("Emergency actions taken", emergency_type=emergency_type)
            
        except Exception as e:
            self.logger.error("Error taking emergency actions", error=str(e))

    async def _update_emergency_status(self):
        """Update emergency mode status."""
        try:
            if not self.emergency_mode:
                return
            
            # Check if emergency conditions have resolved
            if not self._detect_emergency_conditions():
                # Exit emergency mode
                self.emergency_mode = False
                self.emergency_type = None
                self.emergency_start_time = None
                
                # Notify agents that emergency has ended
                await self._broadcast_emergency_end()
                
                self.logger.info("Emergency mode ended")
            
        except Exception as e:
            self.logger.error("Error updating emergency status", error=str(e))

    async def _optimize_frequency_regulation(self):
        """Optimize grid frequency regulation."""
        try:
            # Check if frequency regulation is needed
            if abs(self.grid_frequency - 60.0) > 0.05:  # ±0.05 Hz threshold
                # Activate frequency regulation
                self.optimization_status['frequency_regulation'] = True
                
                # Send frequency regulation signal to producers
                regulation_signal = {
                    'regulation_type': 'frequency',
                    'target_frequency': 60.0,
                    'current_frequency': self.grid_frequency,
                    'deviation': self.grid_frequency - 60.0,
                    'priority': 'medium'
                }
                
                await self.send_message(
                    recipient_id='producer_agent',
                    message_type='frequency_regulation_signal',
                    payload=regulation_signal,
                    priority=6
                )
                
                self.logger.info("Frequency regulation activated", 
                               current_frequency=self.grid_frequency,
                               deviation=regulation_signal['deviation'])
            else:
                # Deactivate frequency regulation
                self.optimization_status['frequency_regulation'] = False
            
        except Exception as e:
            self.logger.error("Error optimizing frequency regulation", error=str(e))

    async def _optimize_voltage_control(self):
        """Optimize grid voltage control."""
        try:
            # Check if voltage control is needed
            if abs(self.grid_voltage - 120.0) > 2.0:  # ±2V threshold
                # Activate voltage control
                self.optimization_status['voltage_control'] = True
                
                # Send voltage control signal to producers
                control_signal = {
                    'control_type': 'voltage',
                    'target_voltage': 120.0,
                    'current_voltage': self.grid_voltage,
                    'deviation': self.grid_voltage - 120.0,
                    'priority': 'medium'
                }
                
                await self.send_message(
                    recipient_id='producer_agent',
                    message_type='voltage_control_signal',
                    payload=control_signal,
                    priority=6
                )
                
                self.logger.info("Voltage control activated", 
                               current_voltage=self.grid_voltage,
                               deviation=control_signal['deviation'])
            else:
                # Deactivate voltage control
                self.optimization_status['voltage_control'] = False
            
        except Exception as e:
            self.logger.error("Error optimizing voltage control", error=str(e))

    async def _optimize_load_balancing(self):
        """Optimize grid load balancing."""
        try:
            # Check if load balancing is needed
            if self.grid_load > 0 and abs(self.grid_supply - self.grid_load) / self.grid_load > 0.05:
                # Activate load balancing
                self.optimization_status['load_balancing'] = True
                
                # Send load balancing signal to market supervisor
                balancing_signal = {
                    'balancing_type': 'load',
                    'current_load': self.grid_load,
                    'current_supply': self.grid_supply,
                    'imbalance': (self.grid_supply - self.grid_load) / self.grid_load,
                    'priority': 'medium'
                }
                
                await self.send_message(
                    recipient_id='market_supervisor_agent',
                    message_type='load_balancing_signal',
                    payload=balancing_signal,
                    priority=6
                )
                
                self.logger.info("Load balancing activated", 
                               load=self.grid_load,
                               supply=self.grid_supply,
                               imbalance=balancing_signal['imbalance'])
            else:
                # Deactivate load balancing
                self.optimization_status['load_balancing'] = False
            
        except Exception as e:
            self.logger.error("Error optimizing load balancing", error=str(e))

    async def _activate_emergency_frequency_regulation(self):
        """Activate emergency frequency regulation."""
        try:
            # Send emergency frequency regulation signal
            emergency_signal = {
                'regulation_type': 'emergency_frequency',
                'target_frequency': 60.0,
                'current_frequency': self.grid_frequency,
                'deviation': self.grid_frequency - 60.0,
                'priority': 'emergency',
                'response_time': self.grid_config.emergency_response_time_seconds
            }
            
            await self.send_message(
                recipient_id='producer_agent',
                message_type='emergency_frequency_regulation',
                payload=emergency_signal,
                priority=9
            )
            
            self.logger.warning("Emergency frequency regulation activated", 
                              signal=emergency_signal)
            
        except Exception as e:
            self.logger.error("Error activating emergency frequency regulation", error=str(e))

    async def _activate_emergency_voltage_control(self):
        """Activate emergency voltage control."""
        try:
            # Send emergency voltage control signal
            emergency_signal = {
                'control_type': 'emergency_voltage',
                'target_voltage': 120.0,
                'current_voltage': self.grid_voltage,
                'deviation': self.grid_voltage - 120.0,
                'priority': 'emergency',
                'response_time': self.grid_config.emergency_response_time_seconds
            }
            
            await self.send_message(
                recipient_id='producer_agent',
                message_type='emergency_voltage_control',
                payload=emergency_signal,
                priority=9
            )
            
            self.logger.warning("Emergency voltage control activated", 
                              signal=emergency_signal)
            
        except Exception as e:
            self.logger.error("Error activating emergency voltage control", error=str(e))

    async def _activate_emergency_demand_response(self):
        """Activate emergency demand response."""
        try:
            # Calculate maximum demand response needed
            emergency_target = min(
                self.grid_load * 0.3,  # Up to 30% of load
                self.grid_config.max_demand_response_mw
            )
            
            # Send emergency demand response signal
            emergency_signal = {
                'target_reduction_mw': emergency_target,
                'duration_minutes': 15,  # 15 minutes for emergency
                'incentive_rate': 0.25,  # 25% incentive for emergency
                'priority': 'emergency',
                'response_time': self.grid_config.emergency_response_time_seconds
            }
            
            await self.send_message(
                recipient_id='consumer_agent',
                message_type='emergency_demand_response',
                payload=emergency_signal,
                priority=9
            )
            
            self.logger.warning("Emergency demand response activated", 
                              signal=emergency_signal)
            
        except Exception as e:
            self.logger.error("Error activating emergency demand response", error=str(e))

    async def _activate_emergency_optimization(self):
        """Activate emergency optimization for all algorithms."""
        try:
            # Activate all optimization algorithms
            for algorithm in self.optimization_algorithms:
                self.optimization_status[algorithm] = True
            
            # Send emergency optimization signal
            emergency_signal = {
                'optimization_type': 'emergency_all',
                'algorithms': self.optimization_algorithms,
                'priority': 'emergency',
                'response_time': self.grid_config.emergency_response_time_seconds
            }
            
            await self.send_message(
                recipient_id='producer_agent',
                message_type='emergency_optimization',
                payload=emergency_signal,
                priority=9
            )
            
            self.logger.warning("Emergency optimization activated", 
                              signal=emergency_signal)
            
        except Exception as e:
            self.logger.error("Error activating emergency optimization", error=str(e))

    async def _broadcast_demand_response_signal(self):
        """Broadcast demand response signal to all agents."""
        try:
            signal = {
                'demand_response_active': True,
                'target_reduction_mw': self.demand_response_target,
                'duration_minutes': int(self.demand_response_duration.total_seconds() / 60),
                'incentive_rate': 0.15,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Send to relevant agents
            agents_to_notify = ['consumer_agent', 'market_supervisor_agent']
            
            for agent_id in agents_to_notify:
                await self.send_message(
                    recipient_id=agent_id,
                    message_type='demand_response_announcement',
                    payload=signal,
                    priority=6
                )
            
            self.logger.info("Demand response signal broadcasted", 
                           recipient_count=len(agents_to_notify))
            
        except Exception as e:
            self.logger.error("Error broadcasting demand response signal", error=str(e))

    async def _broadcast_demand_response_end(self):
        """Broadcast demand response end signal."""
        try:
            signal = {
                'demand_response_active': False,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Send to relevant agents
            agents_to_notify = ['consumer_agent', 'market_supervisor_agent']
            
            for agent_id in agents_to_notify:
                await self.send_message(
                    recipient_id=agent_id,
                    message_type='demand_response_end',
                    payload=signal,
                    priority=5
                )
            
            self.logger.info("Demand response end signal broadcasted", 
                           recipient_count=len(agents_to_notify))
            
        except Exception as e:
            self.logger.error("Error broadcasting demand response end signal", error=str(e))

    async def _broadcast_emergency_signal(self, emergency_type: str):
        """Broadcast emergency signal to all agents."""
        try:
            signal = {
                'emergency_type': emergency_type,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'grid_conditions': {
                    'frequency': self.grid_frequency,
                    'voltage': self.grid_voltage,
                    'stability_score': self.grid_stability_score,
                    'supply_demand_ratio': self.grid_supply / self.grid_load if self.grid_load > 0 else 1.0
                }
            }
            
            # Send to all agents
            agents_to_notify = [
                'forecasting_agent',
                'producer_agent',
                'consumer_agent',
                'market_supervisor_agent'
            ]
            
            for agent_id in agents_to_notify:
                await self.send_message(
                    recipient_id=agent_id,
                    message_type='grid_emergency',
                    payload=signal,
                    priority=9
                )
            
            self.logger.warning("Emergency signal broadcasted", 
                              emergency_type=emergency_type,
                              recipient_count=len(agents_to_notify))
            
        except Exception as e:
            self.logger.error("Error broadcasting emergency signal", error=str(e))

    async def _broadcast_emergency_end(self):
        """Broadcast emergency end signal."""
        try:
            signal = {
                'emergency_ended': True,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'duration_minutes': (datetime.now(timezone.utc) - self.emergency_start_time).total_seconds() / 60 if self.emergency_start_time else 0
            }
            
            # Send to all agents
            agents_to_notify = [
                'forecasting_agent',
                'producer_agent',
                'consumer_agent',
                'market_supervisor_agent'
            ]
            
            for agent_id in agents_to_notify:
                await self.send_message(
                    recipient_id=agent_id,
                    message_type='grid_emergency_end',
                    payload=signal,
                    priority=7
                )
            
            self.logger.info("Emergency end signal broadcasted", 
                           recipient_count=len(agents_to_notify))
            
        except Exception as e:
            self.logger.error("Error broadcasting emergency end signal", error=str(e))

    async def _generate_performance_report(self) -> Dict[str, Any]:
        """Generate a performance report for grid operations."""
        try:
            report = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'grid_metrics': {
                    'frequency_hz': self.grid_frequency,
                    'voltage_v': self.grid_voltage,
                    'stability_score': self.grid_stability_score,
                    'load_mw': self.grid_load,
                    'supply_mw': self.grid_supply
                },
                'grid_health': {
                    'uptime_percentage': self.grid_uptime,
                    'emergency_response_count': self.emergency_response_count,
                    'demand_response_savings': self.demand_response_savings
                },
                'optimization_status': self.optimization_status,
                'demand_response_status': {
                    'active': self.demand_response_active,
                    'target_reduction_mw': self.demand_response_target,
                    'duration_minutes': int(self.demand_response_duration.total_seconds() / 60) if self.demand_response_duration else 0
                },
                'emergency_status': {
                    'active': self.emergency_mode,
                    'type': self.emergency_type,
                    'start_time': self.emergency_start_time.isoformat() if self.emergency_start_time else None
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
                'market_supervisor_agent'
            ]
            
            for agent_id in agents_to_notify:
                await self.send_message(
                    recipient_id=agent_id,
                    message_type='grid_performance_report',
                    payload=report,
                    priority=3
                )
            
            self.logger.info("Performance report broadcasted", 
                           recipient_count=len(agents_to_notify))
            
        except Exception as e:
            self.logger.error("Error broadcasting performance report", error=str(e))

    async def _store_grid_data(self):
        """Store grid data in Timestream."""
        try:
            records = []
            timestamp = datetime.now(timezone.utc)
            
            # Store grid metrics
            records.extend([
                {
                    'measure_name': 'grid_frequency',
                    'value': self.grid_frequency,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'grid_voltage',
                    'value': self.grid_voltage,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'grid_stability_score',
                    'value': self.grid_stability_score,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'grid_load',
                    'value': self.grid_load,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'grid_supply',
                    'value': self.grid_supply,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'demand_response_active',
                    'value': 1.0 if self.demand_response_active else 0.0,
                    'timestamp': timestamp
                },
                {
                    'measure_name': 'emergency_mode',
                    'value': 1.0 if self.emergency_mode else 0.0,
                    'timestamp': timestamp
                }
            ])
            
            if records:
                await self.store_timeseries_data('grid_metrics', records)
                
        except Exception as e:
            self.logger.error("Error storing grid data", error=str(e))

    async def _process_message(self, message: AgentMessage):
        """Process incoming messages specific to grid optimization agent."""
        if message.message_type == "energy_forecast":
            await self._handle_energy_forecast(message)
        elif message.message_type == "market_performance_report":
            await self._handle_market_performance_report(message)
        elif message.message_type == "grid_status_request":
            await self._handle_grid_status_request(message)
        else:
            await super()._process_message(message)

    async def _handle_energy_forecast(self, message: AgentMessage):
        """Handle energy forecasts from forecasting agent."""
        try:
            forecast_data = message.payload
            self.logger.info("Energy forecast received", 
                           forecast_id=forecast_data.get('forecast_id'))
            
            # Use forecast data for grid optimization
            # This could include adjusting demand response thresholds
            # or preparing for expected load changes
            
        except Exception as e:
            self.logger.error("Error handling energy forecast", error=str(e))

    async def _handle_market_performance_report(self, message: AgentMessage):
        """Handle market performance reports."""
        try:
            market_report = message.payload
            self.logger.info("Market performance report received", 
                           session_id=market_report.get('session_id'))
            
            # Use market data for grid optimization
            # This could include adjusting grid parameters based on market conditions
            
        except Exception as e:
            self.logger.error("Error handling market performance report", error=str(e))

    async def _handle_grid_status_request(self, message: AgentMessage):
        """Handle grid status requests."""
        try:
            # Generate current grid status
            status = await self.get_status()
            
            # Send status response
            await self.send_message(
                recipient_id=message.sender_id,
                message_type='grid_status_response',
                payload=status,
                correlation_id=message.correlation_id
            )
            
        except Exception as e:
            self.logger.error("Error handling grid status request", error=str(e))

    async def get_status(self) -> Dict[str, Any]:
        """Get grid optimization agent status."""
        status = await super().get_status()
        status.update({
            'grid_status': {
                'frequency_hz': self.grid_frequency,
                'voltage_v': self.grid_voltage,
                'stability_score': self.grid_stability_score,
                'load_mw': self.grid_load,
                'supply_mw': self.grid_supply,
                'uptime_percentage': self.grid_uptime
            },
            'demand_response_status': {
                'active': self.demand_response_active,
                'target_reduction_mw': self.demand_response_target,
                'duration_minutes': int(self.demand_response_duration.total_seconds() / 60) if self.demand_response_duration else 0,
                'participants_count': len(self.demand_response_participants),
                'savings': self.demand_response_savings
            },
            'emergency_status': {
                'active': self.emergency_mode,
                'type': self.emergency_type,
                'start_time': self.emergency_start_time.isoformat() if self.emergency_start_time else None,
                'response_count': self.emergency_response_count
            },
            'optimization_status': self.optimization_status,
            'grid_health': {
                'stability_threshold': self.grid_config.grid_stability_threshold,
                'demand_response_threshold': self.grid_config.demand_response_threshold,
                'monitoring_interval': self.grid_config.monitoring_interval_seconds
            }
        })
        return status
