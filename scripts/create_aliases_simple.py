#!/usr/bin/env python3
"""
Create Agent Aliases - Simplified Version

This script creates production aliases for all Bedrock agents using their DRAFT versions.
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


class SimpleAliasManager:
    """Simple alias manager for Bedrock agents"""
    
    def __init__(self, region='us-east-1'):
        self.region = region
        self.bedrock_agent_client = boto3.client('bedrock-agent', region_name=region)
        
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
    
    def create_agent_alias(self, agent_id, agent_name, alias_name="PROD"):
        """Create an alias for the agent using DRAFT version"""
        try:
            logger.info(f"Creating alias '{alias_name}' for agent {agent_name}...")
            
            response = self.bedrock_agent_client.create_agent_alias(
                agentId=agent_id,
                agentAliasName=alias_name,
                description=f"Production alias for {agent_name}",
                routingConfiguration=[
                    {
                        'agentVersion': 'DRAFT'
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
    
    def setup_all_aliases(self):
        """Setup aliases for all agents"""
        
        logger.info("🏷️ Creating Agent Aliases for Production Deployment")
        logger.info("=" * 60)
        
        # Get all existing agents
        response = self.bedrock_agent_client.list_agents()
        all_agents = {agent['agentName']: agent['agentId'] for agent in response['agentSummaries']}
        
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
            
            # Create alias
            alias_id = self.create_agent_alias(agent_id, agent_name)
            if not alias_id:
                logger.error(f"❌ Skipping {agent_name} due to alias creation failure")
                continue
            
            # Store agent information
            agent_info[agent_name] = {
                'agent_id': agent_id,
                'version': 'DRAFT',
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
    
    manager = SimpleAliasManager()
    
    try:
        agent_info = manager.setup_all_aliases()
        
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
