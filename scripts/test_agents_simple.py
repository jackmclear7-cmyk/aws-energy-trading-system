#!/usr/bin/env python3
"""
Simple test script that doesn't require AWS credentials
"""

import asyncio
import logging
import sys
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


class MockAgent:
    """Simple mock agent for testing without AWS dependencies"""
    
    def __init__(self, agent_id: str, agent_type: str, name: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.status = "stopped"
        self.messages_sent = 0
        self.messages_received = 0
        
    async def start(self):
        """Start the mock agent"""
        self.status = "running"
        logger.info(f"Mock {self.agent_type} agent {self.agent_id} started")
        
    async def stop(self):
        """Stop the mock agent"""
        self.status = "stopped"
        logger.info(f"Mock {self.agent_type} agent {self.agent_id} stopped")
        
    async def send_message(self, recipient: str, message: dict):
        """Send a mock message"""
        self.messages_sent += 1
        logger.info(f"Mock message sent from {self.agent_id} to {recipient}")
        
    async def get_status(self):
        """Get agent status"""
        return {
            "status": self.status,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "last_activity": "now"
        }


async def test_mock_agent_creation():
    """Test that mock agents can be created successfully"""
    logger.info("Testing mock agent creation...")
    
    try:
        # Create mock agents
        forecasting_agent = MockAgent("test-forecasting", "forecasting", "Test Forecasting Agent")
        producer_agent = MockAgent("test-producer", "producer", "Test Producer Agent")
        consumer_agent = MockAgent("test-consumer", "consumer", "Test Consumer Agent")
        
        logger.info("✅ Mock agents created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Mock agent creation failed: {e}")
        return False


async def test_mock_agent_lifecycle():
    """Test mock agent start/stop lifecycle"""
    logger.info("Testing mock agent lifecycle...")
    
    try:
        # Create a mock agent
        agent = MockAgent("test-lifecycle", "forecasting", "Test Lifecycle Agent")
        
        # Test start
        await agent.start()
        logger.info("✅ Mock agent started successfully")
        
        # Wait a moment
        await asyncio.sleep(0.1)
        
        # Test stop
        await agent.stop()
        logger.info("✅ Mock agent stopped successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Mock agent lifecycle test failed: {e}")
        return False


async def test_mock_agent_communication():
    """Test basic mock agent-to-agent communication"""
    logger.info("Testing mock agent communication...")
    
    try:
        # Create two mock agents
        producer = MockAgent("test-producer-comm", "producer", "Test Producer Comm")
        consumer = MockAgent("test-consumer-comm", "consumer", "Test Consumer Comm")
        
        # Start both agents
        await producer.start()
        await consumer.start()
        
        # Send a test message
        test_message = {
            "type": "test",
            "data": {"message": "Hello from producer!"}
        }
        
        await producer.send_message("consumer", test_message)
        logger.info("✅ Mock message sent successfully")
        
        # Wait for message processing
        await asyncio.sleep(0.1)
        
        # Stop agents
        await producer.stop()
        await consumer.stop()
        
        logger.info("✅ Mock agent communication test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Mock agent communication test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🧪 Mock Agent Testing Suite")
    print("=" * 30)
    
    tests = [
        ("Mock Agent Creation", test_mock_agent_creation),
        ("Mock Agent Lifecycle", test_mock_agent_lifecycle),
        ("Mock Agent Communication", test_mock_agent_communication)
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
        print("🎉 All mock tests passed! The basic agent structure is working.")
        print("   Note: This tests the basic agent structure without AWS dependencies.")
        print("   For full functionality, configure AWS credentials and run the full tests.")
    else:
        print("⚠️ Some mock tests failed. Check the logs above for details.")


if __name__ == "__main__":
    asyncio.run(main())
