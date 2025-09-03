#!/usr/bin/env python3
"""
Simple Setup for AWS Bedrock Agents

This script creates Bedrock agents with basic configuration for the energy trading system.
"""

import json
import time
import logging
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleBedrockAgentSetup:
    """Simple setup for Bedrock agents"""
    
    def __init__(self, region='us-east-1'):
        self.region = region
        self.bedrock_agent_client = boto3.client('bedrock-agent', region_name=region)
        self.bedrock_runtime_client = boto3.client('bedrock-runtime', region_name=region)
        
    def get_account_id(self):
        """Get AWS account ID"""
        sts_client = boto3.client('sts')
        return sts_client.get_caller_identity()['Account']
    
    def create_simple_agent(self, agent_name, agent_type, instructions):
        """Create a simple Bedrock agent"""
        
        try:
            logger.info(f"Creating Bedrock agent: {agent_name}")
            
            # Create agent
            response = self.bedrock_agent_client.create_agent(
                agentName=agent_name,
                agentResourceRoleArn=f"arn:aws:iam::{self.get_account_id()}:role/BedrockAgentRole",
                foundationModel="anthropic.claude-3-5-sonnet-20241022-v2:0",
                instruction=instructions,
                description=f"Bedrock agent for {agent_type} in energy trading system",
                idleSessionTTLInSeconds=1800
            )
            
            agent_id = response['agent']['agentId']
            logger.info(f"✅ Created agent {agent_name} with ID: {agent_id}")
            
            return agent_id
            
        except ClientError as e:
            logger.error(f"❌ Failed to create agent {agent_name}: {e}")
            return None
    
    def create_agent_alias(self, agent_id, agent_name):
        """Create an alias for the agent"""
        
        try:
            # First, prepare the agent
            logger.info(f"Preparing agent {agent_name}...")
            
            prepare_response = self.bedrock_agent_client.prepare_agent(
                agentId=agent_id
            )
            
            # Wait for preparation to complete
            time.sleep(10)
            
            # Create agent version
            logger.info(f"Creating version for agent {agent_name}...")
            
            version_response = self.bedrock_agent_client.create_agent_version(
                agentId=agent_id,
                description=f"Version 1 for {agent_name}"
            )
            
            version = version_response['agentVersion']['version']
            logger.info(f"✅ Created version {version} for agent {agent_name}")
            
            # Create alias
            logger.info(f"Creating alias for agent {agent_name}...")
            
            alias_response = self.bedrock_agent_client.create_agent_alias(
                agentId=agent_id,
                agentAliasName="TSTALIASID",
                description=f"Alias for {agent_name}",
                routingConfiguration=[
                    {
                        'agentVersion': version
                    }
                ]
            )
            
            alias_id = alias_response['agentAlias']['agentAliasId']
            logger.info(f"✅ Created alias {alias_id} for agent {agent_name}")
            
            return {
                'agent_id': agent_id,
                'version': version,
                'alias_id': alias_id
            }
            
        except ClientError as e:
            logger.error(f"❌ Failed to create alias for agent {agent_name}: {e}")
            return None
    
    def setup_all_agents(self):
        """Setup all Bedrock agents for the energy trading system"""
        
        logger.info("🚀 Setting up Bedrock Agents for Energy Trading System")
        logger.info("=" * 60)
        
        # Agent instructions
        instructions = {
            "forecasting_agent": """
You are a Forecasting Agent for an energy trading system. Your role is to:

1. **Weather Analysis**: Analyze weather data to predict solar energy production
2. **Demand Forecasting**: Predict energy demand based on historical patterns  
3. **Price Forecasting**: Forecast energy prices based on supply/demand dynamics
4. **Grid Forecasting**: Predict grid stability and potential issues

**Key Responsibilities:**
- Use weather data to predict solar irradiance and energy production
- Analyze historical consumption patterns to forecast demand
- Consider seasonal trends, time-of-day patterns, and special events
- Provide confidence intervals for all forecasts
- Update forecasts every 15 minutes during market hours

**Communication:**
- Broadcast forecasts to all agents via A2A messaging
- Respond to specific forecast requests from other agents
- Alert on significant forecast changes (>20% deviation)

Always provide forecasts in JSON format with timestamp, forecast_horizon, confidence_score, predicted_values, and reasoning.
""",

            "producer_agent": """
You are a Producer Agent representing a Solar Farm in an energy trading system. Your role is to:

1. **Production Management**: Optimize solar energy production and battery storage
2. **Market Participation**: Decide when and at what price to sell energy
3. **Battery Optimization**: Manage battery charge/discharge cycles
4. **Revenue Maximization**: Maximize profits while maintaining grid stability

**Key Responsibilities:**
- Monitor solar production capacity and weather forecasts
- Decide optimal times to sell energy based on price predictions
- Manage battery storage to smooth production and capture price arbitrage
- Submit sell orders to the market supervisor
- Respond to grid stability requests (demand response)

**Decision Making:**
- Sell when prices are high (>$0.10/kWh)
- Store energy in battery when prices are low (<$0.06/kWh)
- Participate in demand response when grid stability is at risk
- Consider weather forecasts for production planning

**Communication:**
- Send production forecasts to market supervisor
- Respond to demand response signals from grid optimization agent
- Coordinate with other producers for grid stability
""",

            "consumer_agent": """
You are a Consumer Agent representing a Factory with battery storage in an energy trading system. Your role is to:

1. **Demand Management**: Optimize energy consumption and battery usage
2. **Market Participation**: Decide when and at what price to buy energy
3. **Battery Optimization**: Manage battery charge/discharge for cost savings
4. **Demand Response**: Reduce consumption when grid stability is at risk

**Key Responsibilities:**
- Monitor energy consumption patterns and production schedules
- Decide optimal times to buy energy based on price predictions
- Manage battery storage to reduce peak demand charges
- Submit buy orders to the market supervisor
- Participate in demand response programs

**Decision Making:**
- Buy energy when prices are low (<$0.08/kWh)
- Use battery storage during peak price periods (>$0.12/kWh)
- Reduce consumption during demand response events
- Optimize for both cost and production continuity

**Communication:**
- Send consumption forecasts to market supervisor
- Respond to demand response signals from grid optimization agent
- Coordinate with other consumers for grid stability
""",

            "market_supervisor_agent": """
You are a Market Supervisor Agent for an energy trading system. Your role is to:

1. **Order Matching**: Match buy and sell orders to execute trades
2. **Price Discovery**: Determine market-clearing prices
3. **Market Coordination**: Ensure fair and efficient market operation
4. **Trade Settlement**: Process and record all trades

**Key Responsibilities:**
- Collect buy and sell orders from all market participants
- Match orders based on price, quantity, and timing
- Calculate market-clearing prices using uniform pricing
- Execute trades and notify all parties
- Maintain order book and market data
- Ensure market integrity and prevent manipulation

**Market Rules:**
- Use uniform pricing (all trades at same clearing price)
- Prioritize orders by price (highest buy, lowest sell)
- Execute trades immediately when orders match
- Maintain transparency in pricing and execution

**Communication:**
- Broadcast market prices and trade results to all agents
- Send trade confirmations to individual participants
- Provide market status updates and alerts
- Coordinate with grid optimization for stability
""",

            "grid_optimization_agent": """
You are a Grid Optimization Agent for an energy trading system. Your role is to:

1. **Grid Monitoring**: Monitor grid stability, frequency, and voltage
2. **Stability Management**: Ensure grid remains stable and reliable
3. **Demand Response**: Coordinate demand response programs
4. **Emergency Response**: Handle grid emergencies and outages

**Key Responsibilities:**
- Monitor grid frequency, voltage, and stability metrics
- Detect potential grid instability or overload conditions
- Trigger demand response programs when needed
- Coordinate with all agents to maintain grid balance
- Provide grid status updates and alerts

**Grid Management:**
- Maintain frequency between 59.8-60.2 Hz
- Keep voltage within ±5% of nominal
- Monitor supply-demand balance
- Trigger demand response when imbalance >10%

**Communication:**
- Broadcast grid status updates to all agents
- Send demand response signals to consumers
- Coordinate emergency responses
- Provide grid stability recommendations
"""
        }
        
        agents = {
            "forecasting-agent": {
                "type": "forecasting",
                "instructions": instructions["forecasting_agent"]
            },
            "producer-agent": {
                "type": "producer", 
                "instructions": instructions["producer_agent"]
            },
            "consumer-agent": {
                "type": "consumer",
                "instructions": instructions["consumer_agent"]
            },
            "market-supervisor-agent": {
                "type": "market_supervisor",
                "instructions": instructions["market_supervisor_agent"]
            },
            "grid-optimization-agent": {
                "type": "grid_optimization",
                "instructions": instructions["grid_optimization_agent"]
            }
        }
        
        created_agents = {}
        
        for agent_name, config in agents.items():
            # Create agent
            agent_id = self.create_simple_agent(
                agent_name=agent_name,
                agent_type=config["type"],
                instructions=config["instructions"]
            )
            
            if agent_id:
                # Create alias
                alias_info = self.create_agent_alias(agent_id, agent_name)
                if alias_info:
                    created_agents[agent_name] = alias_info
        
        # Save agent information to file
        with open('bedrock_agent_info.json', 'w') as f:
            json.dump(created_agents, f, indent=2)
        
        logger.info(f"\n📄 Agent information saved to: bedrock_agent_info.json")
        logger.info(f"🎉 Successfully created {len(created_agents)} Bedrock agents")
        
        return created_agents


def main():
    """Main setup function"""
    print("🤖 Setting up AWS Bedrock Agents for Energy Trading System")
    print("=" * 60)
    
    setup = SimpleBedrockAgentSetup()
    
    try:
        agents = setup.setup_all_agents()
        
        if agents:
            print(f"\n✅ Successfully created {len(agents)} Bedrock agents:")
            for name, info in agents.items():
                print(f"   - {name}:")
                print(f"     Agent ID: {info['agent_id']}")
                print(f"     Version: {info['version']}")
                print(f"     Alias ID: {info['alias_id']}")
        else:
            print("❌ No agents were created successfully")
            
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main()
