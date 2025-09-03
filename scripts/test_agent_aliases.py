#!/usr/bin/env python3
"""
Test Bedrock Agent Aliases

This script tests all Bedrock agents using their test aliases.
"""

import json
import boto3
from botocore.exceptions import ClientError

def test_agent_with_alias(agent_id, agent_alias_id, agent_name, test_message):
    """Test a Bedrock agent using its alias"""
    
    # Initialize Bedrock runtime client
    bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    
    try:
        print(f"🤖 Testing {agent_name}")
        print(f"   Agent ID: {agent_id}")
        print(f"   Alias ID: {agent_alias_id}")
        print(f"   Message: {test_message}")
        print("-" * 60)
        
        # Invoke the agent
        response = bedrock_runtime.retrieve_and_generate(
            input={'text': test_message},
            retrieveAndGenerateConfiguration={
                'type': 'AGENT',
                'agentConfiguration': {
                    'agentId': agent_id,
                    'agentAliasId': agent_alias_id
                }
            }
        )
        
        print("✅ Agent response received:")
        print("-" * 40)
        
        # Process the response
        if 'output' in response and 'text' in response['output']:
            response_text = response['output']['text']
            print(response_text)
        else:
            print("Response format:", json.dumps(response, indent=2))
        
        print("=" * 60)
        return True
        
    except ClientError as e:
        print(f"❌ Failed to test {agent_name}: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Bedrock Agent Aliases")
    print("=" * 60)
    
    # Load agent information
    try:
        with open('bedrock_agent_test_aliases.json', 'r') as f:
            agent_info = json.load(f)
    except FileNotFoundError:
        print("❌ Agent aliases file not found. Please run create_aliases_tst.py first.")
        return False
    
    # Test messages for each agent type
    test_messages = {
        "consumer-agent": "Hello! I'm a factory manager. Can you help me optimize my energy consumption and battery usage for today? I need to reduce costs while maintaining production.",
        "forecasting-agent": "Can you provide a weather forecast and energy demand prediction for the next 24 hours? I need this for production planning.",
        "producer-agent": "I'm managing a solar farm. What's the optimal strategy for selling energy today? Should I use battery storage or sell directly?",
        "market-supervisor-agent": "What's the current market status? Are there any active buy or sell orders that need to be matched?",
        "grid-optimization-agent": "What's the current grid stability status? Are there any issues that require demand response coordination?"
    }
    
    results = {}
    
    for agent_name, info in agent_info.items():
        agent_id = info['agent_id']
        alias_id = info['alias_id']
        test_message = test_messages.get(agent_name, "Hello! Can you help me with energy trading decisions?")
        
        success = test_agent_with_alias(agent_id, alias_id, agent_name, test_message)
        results[agent_name] = success
        
        print()  # Add spacing between tests
    
    # Summary
    print("📊 Test Results Summary")
    print("=" * 60)
    
    successful_tests = sum(1 for success in results.values() if success)
    total_tests = len(results)
    
    for agent_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {agent_name}")
    
    print(f"\n🎯 Overall: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests == total_tests:
        print("🎉 All agents are working correctly with their aliases!")
    else:
        print("⚠️ Some agents have issues. Check the error messages above.")
    
    return successful_tests == total_tests

if __name__ == "__main__":
    main()
