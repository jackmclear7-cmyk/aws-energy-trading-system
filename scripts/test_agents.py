#!/usr/bin/env python3
"""
Test script to verify agent functionality
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.forecasting.forecasting_agent import ForecastingAgent, ForecastingAgentConfig
from agents.producer.producer_agent import ProducerAgent, ProducerAgentConfig
from agents.consumer.consumer_agent import ConsumerAgent, ConsumerAgentConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_agent_creation():
    """Test that agents can be created successfully"""
    logger.info("Testing agent creation...")
    
    try:
        # Test Forecasting Agent
        forecasting_config = ForecastingAgentConfig(
            agent_id="test-forecasting",
            agent_type="forecasting",
            name="Test Forecasting Agent",
            description="Test forecasting agent for validation",
            capabilities=["forecasting"],
            forecast_horizon_hours=2,
            update_interval_minutes=1
        )
        forecasting_agent = ForecastingAgent(forecasting_config)
        logger.info("✅ Forecasting agent created successfully")
        
        # Test Producer Agent
        producer_config = ProducerAgentConfig(
            agent_id="test-producer",
            agent_type="producer",
            name="Test Producer Agent",
            description="Test producer agent for validation",
            capabilities=["energy_production"],
            max_capacity_mw=5.0,
            battery_capacity_mwh=2.0
        )
        producer_agent = ProducerAgent(producer_config)
        logger.info("✅ Producer agent created successfully")
        
        # Test Consumer Agent
        consumer_config = ConsumerAgentConfig(
            agent_id="test-consumer",
            agent_type="consumer",
            name="Test Consumer Agent",
            description="Test consumer agent for validation",
            capabilities=["energy_consumption"],
            base_consumption_mw=3.0,
            battery_capacity_mwh=1.5
        )
        consumer_agent = ConsumerAgent(consumer_config)
        logger.info("✅ Consumer agent created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent creation failed: {e}")
        return False


async def test_agent_lifecycle():
    """Test agent start/stop lifecycle"""
    logger.info("Testing agent lifecycle...")
    
    try:
        # Create a simple agent
        config = ForecastingAgentConfig(
            agent_id="test-lifecycle",
            agent_type="forecasting",
            name="Test Lifecycle Agent",
            description="Test agent for lifecycle validation",
            capabilities=["forecasting"],
            forecast_horizon_hours=1,
            update_interval_minutes=1
        )
        agent = ForecastingAgent(config)
        
        # Test start
        await agent.start()
        logger.info("✅ Agent started successfully")
        
        # Wait a moment
        await asyncio.sleep(2)
        
        # Test stop
        await agent.stop()
        logger.info("✅ Agent stopped successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent lifecycle test failed: {e}")
        return False


async def test_agent_communication():
    """Test basic agent-to-agent communication"""
    logger.info("Testing agent communication...")
    
    try:
        # Create two agents
        producer_config = ProducerAgentConfig(
            agent_id="test-producer-comm",
            agent_type="producer",
            name="Test Producer Comm",
            description="Test producer for communication",
            capabilities=["energy_production"],
            max_capacity_mw=5.0
        )
        consumer_config = ConsumerAgentConfig(
            agent_id="test-consumer-comm",
            agent_type="consumer",
            name="Test Consumer Comm",
            description="Test consumer for communication",
            capabilities=["energy_consumption"],
            base_consumption_mw=3.0
        )
        
        producer = ProducerAgent(producer_config)
        consumer = ConsumerAgent(consumer_config)
        
        # Start both agents
        await producer.start()
        await consumer.start()
        
        # Send a test message
        test_message = {
            "type": "test",
            "data": {"message": "Hello from producer!"}
        }
        
        await producer.send_message("consumer", test_message)
        logger.info("✅ Message sent successfully")
        
        # Wait for message processing
        await asyncio.sleep(1)
        
        # Stop agents
        await producer.stop()
        await consumer.stop()
        
        logger.info("✅ Agent communication test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent communication test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🧪 Agent Testing Suite")
    print("=" * 30)
    
    tests = [
        ("Agent Creation", test_agent_creation),
        ("Agent Lifecycle", test_agent_lifecycle),
        ("Agent Communication", test_agent_communication)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            result = await test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 30)
    print("📊 TEST SUMMARY")
    print("=" * 30)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")


if __name__ == "__main__":
    asyncio.run(main())
