#!/usr/bin/env python3
"""
Simple Energy Trading Demo Script (No AWS Required)
This script demonstrates basic agent interactions without requiring AWS infrastructure.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleAgent:
    """Simple agent for demo without AWS dependencies"""
    
    def __init__(self, agent_id: str, agent_type: str, name: str, description: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.status = "stopped"
        self.messages_sent = 0
        self.messages_received = 0
        self.last_activity = None
        self.data = {}
        
    async def start(self):
        """Start the agent"""
        self.status = "running"
        self.last_activity = time.time()
        logger.info(f"🚀 Started {self.name} ({self.agent_type})")
        
    async def stop(self):
        """Stop the agent"""
        self.status = "stopped"
        logger.info(f"🛑 Stopped {self.name}")
        
    async def send_message(self, recipient: str, message: dict):
        """Send a message to another agent"""
        self.messages_sent += 1
        self.last_activity = time.time()
        logger.info(f"📤 {self.name} sent message to {recipient}: {message.get('type', 'unknown')}")
        
    async def receive_message(self, sender: str, message: dict):
        """Receive a message from another agent"""
        self.messages_received += 1
        self.last_activity = time.time()
        logger.info(f"📥 {self.name} received message from {sender}: {message.get('type', 'unknown')}")
        
    async def get_status(self):
        """Get agent status"""
        return {
            "status": self.status,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "last_activity": f"{time.time() - self.last_activity:.1f}s ago" if self.last_activity else "Never"
        }


class SimpleEnergyDemo:
    """Simple demo of the energy trading system"""
    
    def __init__(self):
        self.agents = {}
        self.running = False
        
    def setup_agents(self):
        """Set up all agents for demo"""
        logger.info("Setting up agents for demo...")
        
        # Forecasting Agent
        self.agents['forecasting'] = SimpleAgent(
            "forecasting-demo",
            "forecasting",
            "Forecasting Agent",
            "Predicts energy supply and demand using ML models and weather data"
        )
        
        # Producer Agent (Solar Farm)
        self.agents['producer'] = SimpleAgent(
            "solar-farm-demo",
            "producer",
            "Solar Farm Producer",
            "Manages solar energy production and battery storage for optimal trading"
        )
        
        # Consumer Agent (Factory)
        self.agents['consumer'] = SimpleAgent(
            "factory-demo",
            "consumer",
            "Factory Consumer",
            "Manages energy consumption and battery storage for cost optimization"
        )
        
        # Market Supervisor Agent
        self.agents['market'] = SimpleAgent(
            "market-supervisor-demo",
            "market_supervisor",
            "Market Supervisor",
            "Orchestrates energy trading by matching buy/sell orders and determining market prices"
        )
        
        # Grid Optimization Agent
        self.agents['grid'] = SimpleAgent(
            "grid-optimizer-demo",
            "grid_optimization",
            "Grid Optimizer",
            "Monitors grid stability and coordinates demand response programs"
        )
        
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
        cycle = 0
        
        while self.running and (time.time() - start_time) < duration_seconds:
            cycle += 1
            await self.simulate_energy_trading_cycle(cycle)
            await self.show_demo_status()
            await asyncio.sleep(10)  # Update every 10 seconds
            
        logger.info("🏁 Demo completed!")
        
    async def simulate_energy_trading_cycle(self, cycle: int):
        """Simulate one cycle of energy trading"""
        logger.info(f"🔄 Energy Trading Cycle {cycle}")
        
        # 1. Forecasting Agent generates forecast
        forecast_message = {
            "type": "forecast",
            "data": {
                "supply_forecast": 15.5 + (cycle * 0.1),
                "demand_forecast": 12.3 + (cycle * 0.05),
                "price_forecast": 0.08 + (cycle * 0.001),
                "confidence": 0.85,
                "horizon_hours": 4
            }
        }
        await self.agents['forecasting'].send_message("producer", forecast_message)
        await self.agents['producer'].receive_message("forecasting", forecast_message)
        
        # 2. Producer Agent makes trading decision
        if cycle % 2 == 0:  # Every other cycle
            offer_message = {
                "type": "energy_offer",
                "data": {
                    "quantity_mw": 5.0,
                    "price_per_mwh": 0.075,
                    "duration_hours": 1
                }
            }
            await self.agents['producer'].send_message("market", offer_message)
            await self.agents['market'].receive_message("producer", offer_message)
        
        # 3. Consumer Agent makes trading decision
        if cycle % 3 == 0:  # Every third cycle
            bid_message = {
                "type": "energy_bid",
                "data": {
                    "quantity_mw": 3.0,
                    "max_price_per_mwh": 0.085,
                    "duration_hours": 1
                }
            }
            await self.agents['consumer'].send_message("market", bid_message)
            await self.agents['market'].receive_message("consumer", bid_message)
        
        # 4. Market Supervisor clears market
        if cycle % 4 == 0:  # Every fourth cycle
            trade_message = {
                "type": "trade_executed",
                "data": {
                    "quantity_mw": 2.5,
                    "price_per_mwh": 0.08,
                    "buyer": "consumer",
                    "seller": "producer"
                }
            }
            await self.agents['market'].send_message("producer", trade_message)
            await self.agents['market'].send_message("consumer", trade_message)
            await self.agents['producer'].receive_message("market", trade_message)
            await self.agents['consumer'].receive_message("market", trade_message)
        
        # 5. Grid Optimization Agent monitors stability
        if cycle % 5 == 0:  # Every fifth cycle
            grid_message = {
                "type": "grid_status",
                "data": {
                    "stability_score": 0.9 - (cycle * 0.01),
                    "frequency_hz": 60.0,
                    "voltage_kv": 13.8
                }
            }
            await self.agents['grid'].send_message("all", grid_message)
            for agent_name, agent in self.agents.items():
                if agent_name != 'grid':
                    await agent.receive_message("grid", grid_message)
        
    async def show_demo_status(self):
        """Show current status of all agents"""
        print("\n" + "="*80)
        print("📊 ENERGY TRADING DEMO STATUS")
        print("="*80)
        
        for name, agent in self.agents.items():
            try:
                status = await agent.get_status()
                print(f"🤖 {name.upper()} AGENT:")
                print(f"   Name: {agent.name}")
                print(f"   Status: {status['status']}")
                print(f"   Messages Sent: {status['messages_sent']}")
                print(f"   Messages Received: {status['messages_received']}")
                print(f"   Last Activity: {status['last_activity']}")
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
            
            await self.agents['forecasting'].send_message("producer", forecast_message)
            await self.agents['producer'].receive_message("forecasting", forecast_message)
            logger.info("✅ Demonstrated forecast communication between agents")
            
        except Exception as e:
            logger.error(f"❌ Failed to demonstrate agent interaction: {e}")


async def main():
    """Main demo function"""
    print("⚡ Energy Trading System - Simple Demo (No AWS Required) ⚡")
    print("=" * 70)
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
        
    print("\n✨ Demo completed! This demonstrated:")
    print("   - Agent creation and lifecycle management")
    print("   - Agent-to-agent communication (A2A)")
    print("   - Energy trading simulation")
    print("   - Grid optimization monitoring")
    print("\n   For full AWS functionality, configure credentials and run:")
    print("   python scripts/run_simulation.py")


if __name__ == "__main__":
    asyncio.run(main())
