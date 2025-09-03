#!/usr/bin/env python3
"""
Create Agent Aliases for Bedrock Agents

This script creates production aliases for all Bedrock agents in the energy trading system.
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


class AgentAliasManager:
    """Manage Bedrock agent aliases for production deployment"""
    
    def __init__(self, region='us-east-1'):
        self.region = region
        self.bedrock_agent_client = boto3.client('bedrock-agent', region_name=region)
        
    def get_account_id(self):
        """Get AWS account ID"""
        sts_client = boto3.client('sts')
        return sts_client.get_caller_identity()['Account']
    
    def prepare_agent(self, agent_id, agent_name):
        """Prepare an agent for deployment"""
        try:
            logger.info(f"Preparing agent {agent_name} (ID: {agent_id})...")
            
            # Check current status
            response = self.bedrock_agent_client.get_agent(agentId=agent_id)
            current_status = response['agent']['agentStatus']
            
            if current_status == 'PREPARED':
                logger.info(f"✅ Agent {agent_name} is already prepared")
                return True
            elif current_status == 'NOT_PREPARED':
                # Prepare the agent
                prepare_response = self.bedrock_agent_client.prepare_agent(agentId=agent_id)
                logger.info(f"🔄 Started preparing agent {agent_name}")
                
                # Wait for preparation to complete
                max_wait_time = 300  # 5 minutes
                wait_time = 0
                while wait_time < max_wait_time:
                    time.sleep(10)
                    wait_time += 10
                    
                    response = self.bedrock_agent_client.get_agent(agentId=agent_id)
                    status = response['agent']['agentStatus']
                    
                    if status == 'PREPARED':
                        logger.info(f"✅ Agent {agent_name} preparation completed")
                        return True
                    elif status == 'FAILED':
                        logger.error(f"❌ Agent {agent_name} preparation failed")
                        return False
                    
                    logger.info(f"⏳ Agent {agent_name} still preparing... ({wait_time}s)")
                
                logger.error(f"❌ Agent {agent_name} preparation timed out")
                return False
            else:
                logger.warning(f"⚠️ Agent {agent_name} is in unexpected status: {current_status}")
                return False
                
        except ClientError as e:
            logger.error(f"❌ Failed to prepare agent {agent_name}: {e}")
            return False
    
    def create_agent_version(self, agent_id, agent_name):
        """Create a version for the agent"""
        try:
            logger.info(f"Creating version for agent {agent_name}...")
            
            response = self.bedrock_agent_client.create_agent_version(
                agentId=agent_id,
                description=f"Version 1 for {agent_name} - Production Ready"
            )
            
            version = response['agentVersion']['version']
            logger.info(f"✅ Created version {version} for agent {agent_name}")
            return version
            
        except ClientError as e:
            logger.error(f"❌ Failed to create version for agent {agent_name}: {e}")
            return None
    
    def create_agent_alias(self, agent_id, agent_name, version, alias_name="PROD"):
        """Create an alias for the agent"""
        try:
            logger.info(f"Creating alias '{alias_name}' for agent {agent_name}...")
            
            response = self.bedrock_agent_client.create_agent_alias(
                agentId=agent_id,
                agentAliasName=alias_name,
                description=f"Production alias for {agent_name}",
                routingConfiguration=[
                    {
                        'agentVersion': version
                    }
                ]
            )
            
            alias_id = response['agentAlias']['agentAliasId']
            logger.info(f"✅ Created alias '{alias_name}' (ID: {alias_id}) for agent {agent_name}")
            return alias_id
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConflictException':
                logger.warning(f"⚠️ Alias '{alias_name}' already exists for agent {agent_name}")
                # Get existing alias
                try:
                    response = self.bedrock_agent_client.get_agent_alias(
                        agentId=agent_id,
                        agentAliasId=alias_name
                    )
                    alias_id = response['agentAlias']['agentAliasId']
                    logger.info(f"✅ Using existing alias '{alias_name}' (ID: {alias_id}) for agent {agent_name}")
                    return alias_id
                except ClientError as get_error:
                    logger.error(f"❌ Failed to get existing alias for agent {agent_name}: {get_error}")
                    return None
            else:
                logger.error(f"❌ Failed to create alias for agent {agent_name}: {e}")
                return None
    
    def create_remaining_agents(self):
        """Create the remaining agents (market-supervisor and grid-optimization)"""
        
        # Agent instructions
        instructions = {
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
        
        agents_to_create = [
            ("market-supervisor-agent", "market_supervisor", instructions["market_supervisor_agent"]),
            ("grid-optimization-agent", "grid_optimization", instructions["grid_optimization_agent"])
        ]
        
        created_agents = {}
        
        for agent_name, agent_type, instruction in agents_to_create:
            try:
                logger.info(f"Creating agent: {agent_name}")
                
                response = self.bedrock_agent_client.create_agent(
                    agentName=agent_name,
                    agentResourceRoleArn=f"arn:aws:iam::{self.get_account_id()}:role/BedrockAgentRole",
                    foundationModel="anthropic.claude-3-5-sonnet-20241022-v2:0",
                    instruction=instruction,
                    description=f"Bedrock agent for {agent_type} in energy trading system",
                    idleSessionTTLInSeconds=1800
                )
                
                agent_id = response['agent']['agentId']
                logger.info(f"✅ Created agent {agent_name} with ID: {agent_id}")
                created_agents[agent_name] = agent_id
                
            except ClientError as e:
                logger.error(f"❌ Failed to create agent {agent_name}: {e}")
        
        return created_agents
    
    def setup_all_agent_aliases(self):
        """Setup aliases for all agents"""
        
        logger.info("🚀 Setting up Agent Aliases for Production Deployment")
        logger.info("=" * 60)
        
        # First, create any missing agents
        logger.info("Creating missing agents...")
        created_agents = self.create_remaining_agents()
        
        # Get all existing agents
        response = self.bedrock_agent_client.list_agents()
        all_agents = {agent['agentName']: agent['agentId'] for agent in response['agentSummaries']}
        
        # Add newly created agents
        all_agents.update(created_agents)
        
        logger.info(f"Found {len(all_agents)} agents total")
        
        # Process each agent
        agent_info = {}
        
        for agent_name, agent_id in all_agents.items():
            logger.info(f"\n📋 Processing agent: {agent_name}")
            logger.info("-" * 40)
            
            # Prepare agent
            if not self.prepare_agent(agent_id, agent_name):
                logger.error(f"❌ Skipping {agent_name} due to preparation failure")
                continue
            
            # Create version
            version = self.create_agent_version(agent_id, agent_name)
            if not version:
                logger.error(f"❌ Skipping {agent_name} due to version creation failure")
                continue
            
            # Create alias
            alias_id = self.create_agent_alias(agent_id, agent_name, version)
            if not alias_id:
                logger.error(f"❌ Skipping {agent_name} due to alias creation failure")
                continue
            
            # Store agent information
            agent_info[agent_name] = {
                'agent_id': agent_id,
                'version': version,
                'alias_id': alias_id,
                'alias_name': 'PROD'
            }
        
        # Save agent information to file
        with open('bedrock_agent_aliases.json', 'w') as f:
            json.dump(agent_info, f, indent=2)
        
        logger.info(f"\n📄 Agent alias information saved to: bedrock_agent_aliases.json")
        logger.info(f"🎉 Successfully set up aliases for {len(agent_info)} agents")
        
        return agent_info


def main():
    """Main setup function"""
    print("🏷️ Creating Agent Aliases for Production Deployment")
    print("=" * 60)
    
    manager = AgentAliasManager()
    
    try:
        agent_info = manager.setup_all_agent_aliases()
        
        if agent_info:
            print(f"\n✅ Successfully set up aliases for {len(agent_info)} agents:")
            print("-" * 60)
            for name, info in agent_info.items():
                print(f"📋 {name}:")
                print(f"   Agent ID: {info['agent_id']}")
                print(f"   Version: {info['version']}")
                print(f"   Alias: {info['alias_name']} (ID: {info['alias_id']})")
                print()
            
            print("🎯 All agents are now ready for production use!")
            print("   You can invoke agents using their alias IDs.")
        else:
            print("❌ No agent aliases were created successfully")
            
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main()
