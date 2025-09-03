#!/usr/bin/env python3
"""
Simple Energy Trading Demo Script
This script demonstrates basic agent interactions without requiring full AWS infrastructure.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.forecasting.forecasting_agent import ForecastingAgent, ForecastingAgentConfig
from agents.producer.producer_agent import ProducerAgent, ProducerAgentConfig
from agents.consumer.consumer_agent import ConsumerAgent, ConsumerAgentConfig
from agents.market_supervisor.market_supervisor_agent import MarketSupervisorAgent, MarketSupervisorConfig
from agents.grid_optimization.grid_optimization_agent import GridOptimizationAgent, GridOptimizationConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleEnergyDemo:
    """Simple demo of the energy trading system"""
    
    def __init__(self):
        self.agents = {}
        self.running = False
        
    def setup_agents(self):
        """Set up all agents with demo configurations"""
        logger.info("Setting up agents for demo...")
        
        # Forecasting Agent
        forecasting_config = ForecastingAgentConfig(
            agent_id="forecasting-demo",
            agent_type="forecasting",
            name="Forecasting Agent Demo",
            description="Predicts energy supply and demand using ML models and weather data",
            capabilities=["forecasting", "weather_analysis", "ml_prediction"],
            forecast_horizon_hours=4,
            update_interval_minutes=1,
            confidence_threshold=0.7
        )
        self.agents['forecasting'] = ForecastingAgent(forecasting_config)
        
        # Producer Agent (Solar Farm)
        producer_config = ProducerAgentConfig(
            agent_id="solar-farm-demo",
            agent_type="producer",
            name="Solar Farm Producer Demo",
            description="Manages solar energy production and battery storage for optimal trading",
            capabilities=["energy_production", "battery_management", "trading"],
            max_capacity_mw=10.0,
            battery_capacity_mwh=5.0,
            trading_interval_minutes=1,
            min_price_threshold=0.05
        )
        self.agents['producer'] = ProducerAgent(producer_config)
        
        # Consumer Agent (Factory)
        consumer_config = ConsumerAgentConfig(
            agent_id="factory-demo",
            agent_type="consumer",
            name="Factory Consumer Demo",
            description="Manages energy consumption and battery storage for cost optimization",
            capabilities=["energy_consumption", "battery_management", "trading", "demand_response"],
            base_consumption_mw=8.0,
            battery_capacity_mwh=3.0,
            trading_interval_minutes=1,
            max_price_threshold=0.15
        )
        self.agents['consumer'] = ConsumerAgent(consumer_config)
        
        # Market Supervisor Agent
        market_config = MarketSupervisorConfig(
            agent_id="market-supervisor-demo",
            agent_type="market_supervisor",
            name="Market Supervisor Demo",
            description="Orchestrates energy trading by matching buy/sell orders and determining market prices",
            capabilities=["order_matching", "price_discovery", "market_clearing", "trade_execution"],
            clearing_interval_minutes=1,
            price_update_interval_minutes=1,
            max_price_spread=0.05
        )
        self.agents['market'] = MarketSupervisorAgent(market_config)
        
        # Grid Optimization Agent
        grid_config = GridOptimizationConfig(
            agent_id="grid-optimizer-demo",
            agent_type="grid_optimization",
            name="Grid Optimization Demo",
            description="Monitors grid stability and coordinates demand response programs",
            capabilities=["grid_monitoring", "stability_analysis", "demand_response", "emergency_management"],
            monitoring_interval_minutes=1,
            stability_threshold=0.8,
            emergency_threshold=0.5
        )
        self.agents['grid'] = GridOptimizationAgent(grid_config)
        
        logger.info(f"✅ Set up {len(self.agents)} agents for demo")
        
    async def start_agents(self):
        """Start all agents"""
        logger.info("Starting all agents...")
        
        for name, agent in self.agents.items():
            try:
                await agent.start()
                logger.info(f"✅ Started {name} agent")
            except Exception as e:
                logger.error(f"❌ Failed to start {name} agent: {e}")
                
        self.running = True
        logger.info("🚀 All agents started successfully!")
        
    async def stop_agents(self):
        """Stop all agents"""
        logger.info("Stopping all agents...")
        
        for name, agent in self.agents.items():
            try:
                await agent.stop()
                logger.info(f"✅ Stopped {name} agent")
            except Exception as e:
                logger.error(f"❌ Failed to stop {name} agent: {e}")
                
        self.running = False
        logger.info("🛑 All agents stopped")
        
    async def run_demo(self, duration_seconds=60):
        """Run the demo for specified duration"""
        logger.info(f"🎬 Starting demo for {duration_seconds} seconds...")
        
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < duration_seconds:
            await self.show_demo_status()
            await asyncio.sleep(10)  # Update status every 10 seconds
            
        logger.info("🏁 Demo completed!")
        
    async def show_demo_status(self):
        """Show current status of all agents"""
        print("\n" + "="*60)
        print("📊 DEMO STATUS UPDATE")
        print("="*60)
        
        for name, agent in self.agents.items():
            try:
                status = await agent.get_status()
                print(f"🤖 {name.upper()} AGENT:")
                print(f"   Status: {status.get('status', 'Unknown')}")
                print(f"   Messages Sent: {status.get('messages_sent', 0)}")
                print(f"   Messages Received: {status.get('messages_received', 0)}")
                print(f"   Last Activity: {status.get('last_activity', 'Never')}")
                print()
            except Exception as e:
                print(f"❌ {name.upper()} AGENT: Error getting status - {e}")
                
    async def demonstrate_agent_interaction(self):
        """Demonstrate basic agent-to-agent communication"""
        logger.info("🔄 Demonstrating agent interaction...")
        
        # Send a test forecast from forecasting agent to producer agent
        try:
            forecast_message = {
                "type": "forecast",
                "timestamp": time.time(),
                "data": {
                    "supply_forecast": 15.5,
                    "demand_forecast": 12.3,
                    "price_forecast": 0.08,
                    "confidence": 0.85,
                    "horizon_hours": 4
                }
            }
            
            await self.agents['forecasting'].send_message(
                "producer", 
                forecast_message
            )
            logger.info("✅ Sent forecast message from forecasting to producer agent")
            
            # Wait a moment for message processing
            await asyncio.sleep(2)
            
            # Check if producer received the message
            producer_status = await self.agents['producer'].get_status()
            messages_received = producer_status.get('messages_received', 0)
            
            if messages_received > 0:
                logger.info("✅ Producer agent received the forecast message!")
            else:
                logger.warning("⚠️ Producer agent may not have received the message")
                
        except Exception as e:
            logger.error(f"❌ Failed to demonstrate agent interaction: {e}")


async def main():
    """Main demo function"""
    print("⚡ Energy Trading System - Simple Demo ⚡")
    print("=" * 50)
    print()
    
    demo = SimpleEnergyDemo()
    
    try:
        # Set up agents
        demo.setup_agents()
        
        # Start agents
        await demo.start_agents()
        
        # Demonstrate basic interaction
        await demo.demonstrate_agent_interaction()
        
        # Run demo for 60 seconds
        await demo.run_demo(duration_seconds=60)
        
    except KeyboardInterrupt:
        logger.info("🛑 Demo interrupted by user")
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
    finally:
        # Stop all agents
        await demo.stop_agents()
        
    print("\n✨ Demo completed! Check the logs above for details.")
    print("   For a full simulation, run: python scripts/run_simulation.py")


if __name__ == "__main__":
    asyncio.run(main())