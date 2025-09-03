#!/usr/bin/env python3
"""
Main Energy Trading Simulation Script

This script orchestrates all agents and runs the complete energy trading simulation.
It demonstrates A2A communication, MCP tool usage, and real-time energy market dynamics.
"""

import asyncio
import json
import logging
import signal
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional
import argparse

# Add project root to path
sys.path.append('.')

from agents.forecasting.forecasting_agent import ForecastingAgent, ForecastingAgentConfig
from agents.producer.producer_agent import ProducerAgent, ProducerAgentConfig
from agents.consumer.consumer_agent import ConsumerAgent, ConsumerAgentConfig
from agents.market_supervisor.market_supervisor_agent import MarketSupervisorAgent, MarketSupervisorConfig
from agents.grid_optimization.grid_optimization_agent import GridOptimizationAgent, GridOptimizationConfig


class EnergyTradingSimulation:
    """
    Main simulation class that orchestrates all agents and runs the energy trading simulation.
    """
    
    def __init__(self, config: Dict[str, any]):
        self.config = config
        self.agents: Dict[str, any] = {}
        self.simulation_start_time: Optional[datetime] = None
        self.is_running = False
        
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        self.logger.info("Energy Trading Simulation initialized", config=config)

    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(f'energy_simulation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
            ]
        )

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.is_running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def initialize_agents(self):
        """Initialize all agents with their configurations."""
        try:
            self.logger.info("Initializing agents...")
            
            # Initialize Forecasting Agent
            forecasting_config = ForecastingAgentConfig(
                agent_id="forecasting_agent",
                agent_type="forecasting",
                name="Energy Forecasting Agent",
                description="Predicts energy supply and demand using ML models",
                capabilities=["ml_forecasting", "weather_integration", "historical_analysis"],
                forecast_horizon_hours=24,
                update_interval_minutes=15,
                confidence_threshold=0.7
            )
            self.agents['forecasting_agent'] = ForecastingAgent(forecasting_config)
            
            # Initialize Producer Agent (Solar Farm)
            producer_config = ProducerAgentConfig(
                agent_id="producer_agent",
                agent_type="producer",
                name="Solar Farm Producer Agent",
                description="Solar farm that produces renewable energy",
                capabilities=["energy_production", "battery_storage", "market_trading"],
                max_capacity_mw=100.0,
                min_price_per_mwh=20.0,
                max_price_per_mwh=200.0,
                battery_capacity_mwh=50.0,
                trading_interval_minutes=5
            )
            self.agents['producer_agent'] = ProducerAgent(producer_config)
            
            # Initialize Consumer Agent (Factory)
            consumer_config = ConsumerAgentConfig(
                agent_id="consumer_agent",
                agent_type="consumer",
                name="Factory Consumer Agent",
                description="Factory with battery storage that consumes energy",
                capabilities=["energy_consumption", "battery_optimization", "demand_response"],
                base_consumption_mw=80.0,
                max_consumption_mw=120.0,
                battery_capacity_mwh=100.0,
                trading_interval_minutes=5,
                demand_response_enabled=True
            )
            self.agents['consumer_agent'] = ConsumerAgent(consumer_config)
            
            # Initialize Market Supervisor Agent
            market_config = MarketSupervisorConfig(
                agent_id="market_supervisor_agent",
                agent_type="market_supervisor",
                name="Energy Market Supervisor Agent",
                description="Central orchestrator of the energy market",
                capabilities=["order_matching", "price_discovery", "market_clearing"],
                market_clearing_interval_minutes=1,
                price_discovery_method="uniform_pricing",
                market_fee_percentage=0.001
            )
            self.agents['market_supervisor_agent'] = MarketSupervisorAgent(market_config)
            
            # Initialize Grid Optimization Agent
            grid_config = GridOptimizationConfig(
                agent_id="grid_optimization_agent",
                agent_type="grid_optimization",
                name="Grid Optimization Agent",
                description="Monitors and optimizes grid stability",
                capabilities=["grid_monitoring", "demand_response", "emergency_response"],
                grid_stability_threshold=0.95,
                demand_response_threshold=0.8,
                monitoring_interval_seconds=30
            )
            self.agents['grid_optimization_agent'] = GridOptimizationAgent(grid_config)
            
            self.logger.info(f"All {len(self.agents)} agents initialized successfully")
            
        except Exception as e:
            self.logger.error("Error initializing agents", error=str(e))
            raise

    async def start_agents(self):
        """Start all agents."""
        try:
            self.logger.info("Starting agents...")
            
            # Start all agents concurrently
            start_tasks = []
            for agent_id, agent in self.agents.items():
                start_tasks.append(agent.start())
            
            await asyncio.gather(*start_tasks)
            
            self.logger.info("All agents started successfully")
            
        except Exception as e:
            self.logger.error("Error starting agents", error=str(e))
            raise

    async def stop_agents(self):
        """Stop all agents gracefully."""
        try:
            self.logger.info("Stopping agents...")
            
            # Stop all agents concurrently
            stop_tasks = []
            for agent_id, agent in self.agents.items():
                stop_tasks.append(agent.stop())
            
            await asyncio.gather(*stop_tasks, return_exceptions=True)
            
            self.logger.info("All agents stopped successfully")
            
        except Exception as e:
            self.logger.error("Error stopping agents", error=str(e))

    async def run_simulation(self, duration_minutes: int = 60):
        """Run the main simulation loop."""
        try:
            self.simulation_start_time = datetime.now(timezone.utc)
            self.is_running = True
            
            self.logger.info(f"Starting simulation for {duration_minutes} minutes")
            self.logger.info(f"Simulation start time: {self.simulation_start_time}")
            
            # Start agents
            await self.start_agents()
            
            # Run simulation for specified duration
            start_time = time.time()
            end_time = start_time + (duration_minutes * 60)
            
            while self.is_running and time.time() < end_time:
                # Monitor simulation status
                await self._monitor_simulation_status()
                
                # Wait before next status check
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Check if we should continue
                if not self.is_running:
                    break
            
            # Calculate actual runtime
            actual_duration = (time.time() - start_time) / 60
            self.logger.info(f"Simulation completed. Actual duration: {actual_duration:.2f} minutes")
            
        except Exception as e:
            self.logger.error("Error running simulation", error=str(e))
            raise
        finally:
            # Always stop agents
            await self.stop_agents()

    async def _monitor_simulation_status(self):
        """Monitor the status of all agents and the simulation."""
        try:
            current_time = datetime.now(timezone.utc)
            runtime = (current_time - self.simulation_start_time).total_seconds() / 60
            
            # Get status from all agents
            agent_statuses = {}
            for agent_id, agent in self.agents.items():
                try:
                    status = await agent.get_status()
                    agent_statuses[agent_id] = status
                except Exception as e:
                    self.logger.warning(f"Could not get status from {agent_id}: {e}")
                    agent_statuses[agent_id] = {"error": str(e)}
            
            # Log simulation status
            self.logger.info(f"Simulation status - Runtime: {runtime:.2f} minutes")
            
            # Log agent statuses (summary)
            for agent_id, status in agent_statuses.items():
                if "error" not in status:
                    self.logger.debug(f"{agent_id}: {status.get('is_running', 'unknown')}")
                else:
                    self.logger.warning(f"{agent_id}: {status['error']}")
            
            # Check for critical issues
            await self._check_critical_issues(agent_statuses)
            
        except Exception as e:
            self.logger.error("Error monitoring simulation status", error=str(e))

    async def _check_critical_issues(self, agent_statuses: Dict[str, any]):
        """Check for critical issues that might require simulation shutdown."""
        try:
            critical_issues = []
            
            for agent_id, status in agent_statuses.items():
                if "error" in status:
                    critical_issues.append(f"{agent_id}: {status['error']}")
                elif not status.get('is_running', False):
                    critical_issues.append(f"{agent_id}: Not running")
            
            if critical_issues:
                self.logger.warning("Critical issues detected", issues=critical_issues)
                
                # If too many critical issues, consider stopping simulation
                if len(critical_issues) > len(self.agents) * 0.5:  # More than 50% of agents have issues
                    self.logger.error("Too many critical issues, stopping simulation")
                    self.is_running = False
            
        except Exception as e:
            self.logger.error("Error checking critical issues", error=str(e))

    async def generate_simulation_report(self) -> Dict[str, any]:
        """Generate a comprehensive simulation report."""
        try:
            report = {
                'simulation_info': {
                    'start_time': self.simulation_start_time.isoformat() if self.simulation_start_time else None,
                    'end_time': datetime.now(timezone.utc).isoformat(),
                    'duration_minutes': None,
                    'status': 'completed' if self.is_running else 'stopped'
                },
                'agents_summary': {},
                'overall_performance': {}
            }
            
            # Calculate duration
            if self.simulation_start_time:
                duration = (datetime.now(timezone.utc) - self.simulation_start_time).total_seconds() / 60
                report['simulation_info']['duration_minutes'] = duration
            
            # Get final status from all agents
            for agent_id, agent in self.agents.items():
                try:
                    status = await agent.get_status()
                    report['agents_summary'][agent_id] = {
                        'agent_type': status.get('agent_type', 'unknown'),
                        'is_running': status.get('is_running', False),
                        'last_heartbeat': status.get('last_heartbeat', None),
                        'message_count': status.get('message_history_count', 0)
                    }
                except Exception as e:
                    report['agents_summary'][agent_id] = {
                        'error': str(e)
                    }
            
            # Calculate overall performance metrics
            total_messages = sum(
                summary.get('message_count', 0) 
                for summary in report['agents_summary'].values() 
                if 'error' not in summary
            )
            
            running_agents = sum(
                1 for summary in report['agents_summary'].values() 
                if summary.get('is_running', False)
            )
            
            report['overall_performance'] = {
                'total_agents': len(self.agents),
                'running_agents': running_agents,
                'total_messages_exchanged': total_messages,
                'success_rate': running_agents / len(self.agents) if self.agents else 0
            }
            
            return report
            
        except Exception as e:
            self.logger.error("Error generating simulation report", error=str(e))
            return {"error": str(e)}

    async def save_simulation_report(self, report: Dict[str, any], filename: str = None):
        """Save the simulation report to a file."""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"simulation_report_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"Simulation report saved to {filename}")
            
        except Exception as e:
            self.logger.error("Error saving simulation report", error=str(e))


def create_default_config() -> Dict[str, any]:
    """Create a default simulation configuration."""
    return {
        'simulation_duration_minutes': 60,
        'log_level': 'INFO',
        'save_reports': True,
        'agent_configs': {
            'forecasting': {
                'forecast_horizon_hours': 24,
                'update_interval_minutes': 15
            },
            'producer': {
                'max_capacity_mw': 100.0,
                'trading_interval_minutes': 5
            },
            'consumer': {
                'base_consumption_mw': 80.0,
                'trading_interval_minutes': 5
            },
            'market': {
                'market_clearing_interval_minutes': 1
            },
            'grid': {
                'monitoring_interval_seconds': 30
            }
        }
    }


async def main():
    """Main entry point for the simulation."""
    parser = argparse.ArgumentParser(description='Energy Trading Simulation')
    parser.add_argument('--duration', type=int, default=60, 
                       help='Simulation duration in minutes (default: 60)')
    parser.add_argument('--config', type=str, 
                       help='Path to configuration file')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Logging level')
    parser.add_argument('--save-report', action='store_true', 
                       help='Save simulation report to file')
    
    args = parser.parse_args()
    
    # Create configuration
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config file: {e}")
            return
    else:
        config = create_default_config()
    
    # Override config with command line arguments
    config['simulation_duration_minutes'] = args.duration
    config['log_level'] = args.log_level
    config['save_reports'] = args.save_report
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Create and run simulation
    simulation = EnergyTradingSimulation(config)
    
    try:
        # Initialize agents
        await simulation.initialize_agents()
        
        # Run simulation
        await simulation.run_simulation(duration_minutes=config['simulation_duration_minutes'])
        
        # Generate and save report
        if config.get('save_reports', False):
            report = await simulation.generate_simulation_report()
            await simulation.save_simulation_report(report)
            
            # Print summary
            print("\n" + "="*50)
            print("SIMULATION COMPLETED")
            print("="*50)
            print(f"Duration: {report['simulation_info']['duration_minutes']:.2f} minutes")
            print(f"Agents: {report['overall_performance']['running_agents']}/{report['overall_performance']['total_agents']} running")
            print(f"Messages exchanged: {report['overall_performance']['total_messages_exchanged']}")
            print(f"Success rate: {report['overall_performance']['success_rate']:.2%}")
            print("="*50)
        
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
    except Exception as e:
        print(f"Simulation failed: {e}")
        logging.error("Simulation failed", error=str(e))
    finally:
        # Ensure agents are stopped
        await simulation.stop_agents()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulation terminated")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
