#!/usr/bin/env python3
"""
Setup AWS Bedrock Agents for Energy Trading System

This script creates and configures Bedrock agents for each agent type in the system.
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


class BedrockAgentSetup:
    """Setup and configure Bedrock agents"""
    
    def __init__(self, region='us-east-1'):
        self.region = region
        self.bedrock_agent_client = boto3.client('bedrock-agent', region_name=region)
        self.bedrock_runtime_client = boto3.client('bedrock-runtime', region_name=region)
        self.iam_client = boto3.client('iam')
        
    def create_agent_instructions(self):
        """Create agent instructions for each agent type"""
        
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

**Tools Available:**
- Weather forecast API (get current and predicted weather)
- Historical data API (access past energy data)
- Timestream database (store and retrieve time-series data)

**Output Format:**
Always provide forecasts in JSON format with:
- timestamp
- forecast_horizon (hours ahead)
- confidence_score (0-1)
- predicted_values
- reasoning

**Communication:**
- Broadcast forecasts to all agents via A2A messaging
- Respond to specific forecast requests from other agents
- Alert on significant forecast changes (>20% deviation)
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

**Tools Available:**
- Weather forecast API (predict solar production)
- Trading API (submit sell orders, check market prices)
- Timestream database (store production metrics)
- Battery management system

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

**Tools Available:**
- Weather forecast API (predict energy needs)
- Trading API (submit buy orders, check market prices)
- Timestream database (store consumption metrics)
- Battery management system
- Production scheduling system

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

**Tools Available:**
- Trading API (process orders and execute trades)
- Timestream database (store market data and trades)
- Market data feeds (real-time price information)

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

**Tools Available:**
- Grid management API (monitor grid status)
- Timestream database (store grid metrics)
- Emergency communication systems
- Demand response coordination tools

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
        
        return instructions
    
    def create_agent_tools(self):
        """Create tool definitions for Bedrock agents"""
        
        tools = {
            "weather_forecast_tool": {
                "name": "get_weather_forecast",
                "description": "Get current weather conditions and forecast data for energy production planning",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "Geographic location for weather data"
                            },
                            "forecast_hours": {
                                "type": "integer",
                                "description": "Number of hours to forecast ahead (1-24)"
                            }
                        },
                        "required": ["location"]
                    }
                }
            },
            
            "historical_data_tool": {
                "name": "get_historical_data",
                "description": "Retrieve historical energy data for analysis and forecasting",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "data_type": {
                                "type": "string",
                                "enum": ["prices", "demand", "supply", "trades"],
                                "description": "Type of historical data to retrieve"
                            },
                            "time_range": {
                                "type": "string",
                                "description": "Time range for data (e.g., '24h', '7d', '30d')"
                            }
                        },
                        "required": ["data_type"]
                    }
                }
            },
            
            "trading_tool": {
                "name": "submit_trade_order",
                "description": "Submit buy or sell orders to the energy market",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "order_type": {
                                "type": "string",
                                "enum": ["buy", "sell"],
                                "description": "Type of order (buy or sell)"
                            },
                            "quantity": {
                                "type": "number",
                                "description": "Amount of energy in MWh"
                            },
                            "price": {
                                "type": "number",
                                "description": "Price per MWh in dollars"
                            },
                            "agent_id": {
                                "type": "string",
                                "description": "ID of the agent submitting the order"
                            }
                        },
                        "required": ["order_type", "quantity", "price", "agent_id"]
                    }
                }
            },
            
            "grid_status_tool": {
                "name": "get_grid_status",
                "description": "Get current grid stability and status information",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "metrics": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific grid metrics to retrieve"
                            }
                        }
                    }
                }
            },
            
            "data_storage_tool": {
                "name": "store_metrics",
                "description": "Store time-series metrics in the database",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Name of the table to store data in"
                            },
                            "data": {
                                "type": "object",
                                "description": "Data to store with timestamp"
                            }
                        },
                        "required": ["table_name", "data"]
                    }
                }
            }
        }
        
        return tools
    
    def create_agent_action_groups(self):
        """Create action groups for Bedrock agents"""
        
        action_groups = {
            "energy_trading_actions": {
                "actionGroupName": "EnergyTradingActions",
                "description": "Actions for energy trading operations",
                "actionGroupExecutor": {
                    "lambda": "arn:aws:lambda:us-east-1:899469778368:function:energy-trading-actions"
                },
                "apiSchema": {
                    "payload": json.dumps({
                        "openapi": "3.0.0",
                        "info": {
                            "title": "Energy Trading API",
                            "version": "1.0.0",
                            "description": "API for energy trading operations"
                        },
                        "paths": {
                            "/weather": {
                                "get": {
                                    "summary": "Get weather forecast",
                                    "parameters": [
                                        {
                                            "name": "location",
                                            "in": "query",
                                            "required": True,
                                            "schema": {"type": "string"}
                                        }
                                    ],
                                    "responses": {
                                        "200": {
                                            "description": "Weather forecast data",
                                            "content": {
                                                "application/json": {
                                                    "schema": {
                                                        "type": "object",
                                                        "properties": {
                                                            "temperature": {"type": "number"},
                                                            "humidity": {"type": "number"},
                                                            "solar_irradiance": {"type": "number"}
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            "/trade": {
                                "post": {
                                    "summary": "Submit trade order",
                                    "requestBody": {
                                        "required": True,
                                        "content": {
                                            "application/json": {
                                                "schema": {
                                                    "type": "object",
                                                    "properties": {
                                                        "order_type": {"type": "string"},
                                                        "quantity": {"type": "number"},
                                                        "price": {"type": "number"}
                                                    }
                                                }
                                            }
                                        }
                                    },
                                    "responses": {
                                        "200": {
                                            "description": "Trade order submitted"
                                        }
                                    }
                                }
                            }
                        }
                    })
                }
            }
        }
        
        return action_groups
    
    def create_bedrock_agent(self, agent_name, agent_type, instructions, tools=None, action_groups=None):
        """Create a Bedrock agent"""
        
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
            
            # Create agent version
            version_response = self.bedrock_agent_client.create_agent_action_group(
                agentId=agent_id,
                agentVersion="DRAFT",
                actionGroupName="EnergyTradingActions",
                description="Actions for energy trading operations",
                actionGroupExecutor={
                    'lambda': f"arn:aws:lambda:us-east-1:{self.get_account_id()}:function:energy-trading-actions"
                }
            )
            
            logger.info(f"✅ Created action group for {agent_name}")
            
            return agent_id
            
        except ClientError as e:
            logger.error(f"❌ Failed to create agent {agent_name}: {e}")
            return None
    
    def get_account_id(self):
        """Get AWS account ID"""
        sts_client = boto3.client('sts')
        return sts_client.get_caller_identity()['Account']
    
    def setup_all_agents(self):
        """Setup all Bedrock agents for the energy trading system"""
        
        logger.info("🚀 Setting up Bedrock Agents for Energy Trading System")
        logger.info("=" * 60)
        
        instructions = self.create_agent_instructions()
        tools = self.create_agent_tools()
        action_groups = self.create_agent_action_groups()
        
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
            agent_id = self.create_bedrock_agent(
                agent_name=agent_name,
                agent_type=config["type"],
                instructions=config["instructions"]
            )
            
            if agent_id:
                created_agents[agent_name] = agent_id
        
        # Save agent IDs to file
        with open('bedrock_agent_ids.json', 'w') as f:
            json.dump(created_agents, f, indent=2)
        
        logger.info(f"\n📄 Agent IDs saved to: bedrock_agent_ids.json")
        logger.info(f"🎉 Successfully created {len(created_agents)} Bedrock agents")
        
        return created_agents


def main():
    """Main setup function"""
    print("🤖 Setting up AWS Bedrock Agents for Energy Trading System")
    print("=" * 60)
    
    setup = BedrockAgentSetup()
    
    try:
        agents = setup.setup_all_agents()
        
        if agents:
            print(f"\n✅ Successfully created {len(agents)} Bedrock agents:")
            for name, agent_id in agents.items():
                print(f"   - {name}: {agent_id}")
        else:
            print("❌ No agents were created successfully")
            
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main()
