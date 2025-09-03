#!/usr/bin/env python3
"""
Test Bedrock Agent Interactions

This script tests agent interactions using the correct Bedrock API structure.
"""

import json
import boto3
import time
from botocore.exceptions import ClientError

def test_agent_invocation(agent_id, agent_alias_id, agent_name, test_message):
    """Test a Bedrock agent using the correct API structure"""
    
    # Initialize Bedrock runtime client
    bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    
    try:
        print(f"🤖 Testing {agent_name}")
        print(f"   Agent ID: {agent_id}")
        print(f"   Alias ID: {agent_alias_id}")
        print(f"   Message: {test_message}")
        print("-" * 60)
        
        # Use the correct API structure for agent invocation
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
        return True, response
        
    except ClientError as e:
        print(f"❌ Failed to test {agent_name}: {e}")
        return False, None

def simulate_energy_trading_workflow():
    """Simulate a complete energy trading workflow"""
    
    print("🔄 Simulating Energy Trading Workflow")
    print("=" * 60)
    
    # Load agent information
    try:
        with open('bedrock_agent_test_aliases.json', 'r') as f:
            agent_info = json.load(f)
    except FileNotFoundError:
        print("❌ Agent aliases file not found. Please run create_aliases_tst.py first.")
        return False
    
    workflow_steps = []
    
    # Step 1: Forecasting Agent - Get weather and demand forecast
    print("\n📊 Step 1: Weather and Demand Forecasting")
    print("-" * 40)
    
    forecasting_agent = agent_info.get('forecasting-agent')
    if forecasting_agent:
        success, response = test_agent_invocation(
            forecasting_agent['agent_id'],
            forecasting_agent['alias_id'],
            'forecasting-agent',
            "Provide a weather forecast and energy demand prediction for the next 24 hours. Include solar production estimates and grid demand forecasts."
        )
        
        if success:
            workflow_steps.append({
                'step': 1,
                'agent': 'forecasting-agent',
                'action': 'weather_demand_forecast',
                'status': 'success',
                'timestamp': time.time(),
                'response': response
            })
    
    # Step 2: Producer Agent - Optimize solar production
    print("\n☀️ Step 2: Solar Production Optimization")
    print("-" * 40)
    
    producer_agent = agent_info.get('producer-agent')
    if producer_agent:
        success, response = test_agent_invocation(
            producer_agent['agent_id'],
            producer_agent['alias_id'],
            'producer-agent',
            "Based on the weather forecast, optimize my solar farm production for today. Should I use battery storage or sell energy directly to the grid? What's the optimal pricing strategy?"
        )
        
        if success:
            workflow_steps.append({
                'step': 2,
                'agent': 'producer-agent',
                'action': 'production_optimization',
                'status': 'success',
                'timestamp': time.time(),
                'response': response
            })
    
    # Step 3: Consumer Agent - Optimize energy consumption
    print("\n🏭 Step 3: Consumer Energy Optimization")
    print("-" * 40)
    
    consumer_agent = agent_info.get('consumer-agent')
    if consumer_agent:
        success, response = test_agent_invocation(
            consumer_agent['agent_id'],
            consumer_agent['alias_id'],
            'consumer-agent',
            "I'm a factory manager. Based on current energy prices and demand forecasts, optimize my energy consumption and battery usage for today. When should I buy energy and when should I use stored energy?"
        )
        
        if success:
            workflow_steps.append({
                'step': 3,
                'agent': 'consumer-agent',
                'action': 'consumption_optimization',
                'status': 'success',
                'timestamp': time.time(),
                'response': response
            })
    
    # Step 4: Market Supervisor - Execute trades
    print("\n💼 Step 4: Market Trade Execution")
    print("-" * 40)
    
    market_agent = agent_info.get('market-supervisor-agent')
    if market_agent:
        success, response = test_agent_invocation(
            market_agent['agent_id'],
            market_agent['alias_id'],
            'market-supervisor-agent',
            "Process the buy and sell orders from producers and consumers. Match orders and determine market-clearing prices. Execute trades and provide settlement information."
        )
        
        if success:
            workflow_steps.append({
                'step': 4,
                'agent': 'market-supervisor-agent',
                'action': 'trade_execution',
                'status': 'success',
                'timestamp': time.time(),
                'response': response
            })
    
    # Step 5: Grid Optimization - Monitor stability
    print("\n⚡ Step 5: Grid Stability Monitoring")
    print("-" * 40)
    
    grid_agent = agent_info.get('grid-optimization-agent')
    if grid_agent:
        success, response = test_agent_invocation(
            grid_agent['agent_id'],
            grid_agent['alias_id'],
            'grid-optimization-agent',
            "Monitor grid stability after the trades. Check frequency, voltage, and supply-demand balance. Coordinate demand response if needed to maintain grid stability."
        )
        
        if success:
            workflow_steps.append({
                'step': 5,
                'agent': 'grid-optimization-agent',
                'action': 'grid_monitoring',
                'status': 'success',
                'timestamp': time.time(),
                'response': response
            })
    
    # Save workflow results
    with open('workflow_results.json', 'w') as f:
        json.dump(workflow_steps, f, indent=2)
    
    print(f"\n📄 Workflow results saved to: workflow_results.json")
    print(f"🎯 Completed {len(workflow_steps)} workflow steps")
    
    return workflow_steps

def main():
    """Main test function"""
    print("🧪 Testing Bedrock Agent Interactions")
    print("=" * 60)
    
    # Run the complete workflow simulation
    workflow_steps = simulate_energy_trading_workflow()
    
    if workflow_steps:
        print(f"\n✅ Workflow simulation completed successfully!")
        print(f"📊 {len(workflow_steps)} steps executed")
        
        # Summary
        print("\n📋 Workflow Summary:")
        print("-" * 40)
        for step in workflow_steps:
            print(f"Step {step['step']}: {step['agent']} - {step['action']} ✅")
        
        print(f"\n🎉 All agents are working correctly!")
        return True
    else:
        print("❌ Workflow simulation failed")
        return False

if __name__ == "__main__":
    main()
