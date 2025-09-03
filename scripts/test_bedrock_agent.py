#!/usr/bin/env python3
"""
Test Bedrock Agent

This script tests a Bedrock agent by sending a message and receiving a response.
"""

import json
import boto3
from botocore.exceptions import ClientError

def test_bedrock_agent():
    """Test a Bedrock agent"""
    
    # Initialize Bedrock runtime client
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    # Agent information
    agent_id = "UOXB87Q220"  # consumer-agent
    agent_alias_id = "TSTALIASID"
    
    # Test message
    test_message = "Hello! I'm a consumer agent representing a factory. Can you help me optimize my energy consumption and battery usage for today?"
    
    try:
        print(f"🤖 Testing Bedrock Agent: {agent_id}")
        print(f"📝 Test message: {test_message}")
        print("=" * 60)
        
        # Invoke the agent
        response = bedrock_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId="test-session-001",
            inputText=test_message
        )
        
        print("✅ Agent response received:")
        print("-" * 40)
        
        # Process the response
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    # Decode the response
                    response_text = chunk['bytes'].decode('utf-8')
                    print(response_text, end='')
        
        print("\n" + "=" * 60)
        print("🎉 Bedrock agent test completed successfully!")
        
        return True
        
    except ClientError as e:
        print(f"❌ Failed to test Bedrock agent: {e}")
        return False

def test_agent_with_energy_scenario():
    """Test agent with a specific energy trading scenario"""
    
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    # Agent information
    agent_id = "UOXB87Q220"  # consumer-agent
    agent_alias_id = "TSTALIASID"
    
    # Energy trading scenario
    scenario = """
I'm a factory manager and I need help with energy trading decisions for tomorrow. Here's my situation:

- Current energy price: $0.08/kWh
- My factory consumes 50 MWh per day
- I have a 20 MWh battery storage system
- Weather forecast shows sunny conditions (good for solar production)
- Peak demand hours are 2-6 PM when prices typically spike to $0.12/kWh

What should be my energy trading strategy for tomorrow? Should I:
1. Buy energy now at $0.08/kWh and store it in my battery?
2. Wait and buy during off-peak hours?
3. Use my battery during peak hours to avoid high prices?

Please provide a detailed strategy with specific recommendations.
"""
    
    try:
        print(f"🏭 Testing Energy Trading Scenario")
        print("=" * 60)
        
        # Invoke the agent
        response = bedrock_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId="energy-scenario-001",
            inputText=scenario
        )
        
        print("✅ Agent response:")
        print("-" * 40)
        
        # Process the response
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    # Decode the response
                    response_text = chunk['bytes'].decode('utf-8')
                    print(response_text, end='')
        
        print("\n" + "=" * 60)
        print("🎉 Energy trading scenario test completed!")
        
        return True
        
    except ClientError as e:
        print(f"❌ Failed to test energy scenario: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing AWS Bedrock Agent for Energy Trading")
    print("=" * 60)
    
    # Test basic agent functionality
    print("\n1. Testing basic agent functionality...")
    basic_test = test_bedrock_agent()
    
    if basic_test:
        print("\n2. Testing energy trading scenario...")
        scenario_test = test_agent_with_energy_scenario()
        
        if scenario_test:
            print("\n🎉 All tests passed! Bedrock agent is working correctly.")
        else:
            print("\n⚠️  Basic test passed, but scenario test failed.")
    else:
        print("\n❌ Basic agent test failed.")

if __name__ == "__main__":
    main()
