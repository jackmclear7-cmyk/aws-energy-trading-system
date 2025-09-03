"""
Base Agent Class for Energy Trading System

This module provides the foundation for all agents in the energy trading system,
including A2A communication, MCP tool usage, and common agent behaviors.
"""

import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict

import boto3
import structlog
from pydantic import BaseModel, Field

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@dataclass
class AgentMessage:
    """Represents a message between agents in the A2A communication system."""
    message_id: str
    sender_id: str
    recipient_id: str
    message_type: str
    timestamp: datetime
    payload: Dict[str, Any]
    priority: int = 0
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Create message from dictionary format."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    agent_id: str
    agent_type: str
    name: str
    description: str
    capabilities: List[str]
    trading_parameters: Dict[str, Any] = Field(default_factory=dict)
    communication_settings: Dict[str, Any] = Field(default_factory=dict)
    mcp_tools: List[str] = Field(default_factory=list)
    a2a_endpoints: List[str] = Field(default_factory=list)


class BaseAgent(ABC):
    """
    Base class for all agents in the energy trading system.
    
    Provides common functionality for:
    - A2A communication
    - MCP tool usage
    - Configuration management
    - Logging and monitoring
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent_id = config.agent_id
        self.agent_type = config.agent_type
        self.name = config.name
        
        # Initialize AWS clients
        self.bedrock_client = boto3.client('bedrock-runtime')
        self.timestream_client = boto3.client('timestream-write')
        self.timestream_query_client = boto3.client('timestream-query')
        self.lambda_client = boto3.client('lambda')
        
        # Message queue for A2A communication
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_history: List[AgentMessage] = []
        
        # Agent state
        self.is_running = False
        self.last_heartbeat = datetime.now(timezone.utc)
        
        # Initialize logger
        self.logger = structlog.get_logger().bind(
            agent_id=self.agent_id,
            agent_type=self.agent_type
        )
        
        self.logger.info("Agent initialized", config=config.dict())

    async def start(self):
        """Start the agent and begin processing."""
        self.is_running = True
        self.logger.info("Agent started")
        
        # Start background tasks
        asyncio.create_task(self._message_processor())
        asyncio.create_task(self._heartbeat_monitor())
        
        # Start agent-specific processing
        await self._start_agent_specific()

    async def stop(self):
        """Stop the agent and cleanup resources."""
        self.is_running = False
        self.logger.info("Agent stopped")
        await self._stop_agent_specific()

    @abstractmethod
    async def _start_agent_specific(self):
        """Agent-specific startup logic. Must be implemented by subclasses."""
        pass

    @abstractmethod
    async def _stop_agent_specific(self):
        """Agent-specific cleanup logic. Must be implemented by subclasses."""
        pass

    async def send_message(self, recipient_id: str, message_type: str, payload: Dict[str, Any], 
                          priority: int = 0, correlation_id: Optional[str] = None) -> str:
        """
        Send a message to another agent via A2A communication.
        
        Args:
            recipient_id: ID of the recipient agent
            message_type: Type of message being sent
            payload: Message content
            priority: Message priority (0-9, higher is more important)
            correlation_id: Optional correlation ID for tracking related messages
            
        Returns:
            Message ID of the sent message
        """
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            message_type=message_type,
            timestamp=datetime.now(timezone.utc),
            payload=payload,
            priority=priority,
            correlation_id=correlation_id
        )
        
        # Add to message history
        self.message_history.append(message)
        
        # In a real implementation, this would send via Bedrock Agents A2A
        # For now, we'll simulate by adding to the recipient's queue
        self.logger.info("Message sent", 
                        recipient_id=recipient_id,
                        message_type=message_type,
                        message_id=message.message_id)
        
        return message.message_id

    async def receive_message(self, message: AgentMessage):
        """
        Receive a message from another agent.
        
        Args:
            message: The received message
        """
        await self.message_queue.put(message)
        self.logger.info("Message received", 
                        sender_id=message.sender_id,
                        message_type=message.message_type)

    async def _message_processor(self):
        """Background task to process incoming messages."""
        while self.is_running:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                # Process message
                await self._process_message(message)
                
                # Mark as done
                self.message_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error("Error processing message", error=str(e))

    async def _process_message(self, message: AgentMessage):
        """
        Process a received message. Can be overridden by subclasses.
        
        Args:
            message: The message to process
        """
        self.logger.info("Processing message", 
                        message_type=message.message_type,
                        sender_id=message.sender_id)
        
        # Default message handling - can be overridden
        if message.message_type == "heartbeat":
            await self._handle_heartbeat(message)
        elif message.message_type == "status_request":
            await self._handle_status_request(message)
        else:
            await self._handle_custom_message(message)

    async def _handle_heartbeat(self, message: AgentMessage):
        """Handle heartbeat messages."""
        # Update last heartbeat
        self.last_heartbeat = datetime.now(timezone.utc)
        
        # Send heartbeat response
        await self.send_message(
            recipient_id=message.sender_id,
            message_type="heartbeat_response",
            payload={"status": "healthy", "timestamp": self.last_heartbeat.isoformat()},
            correlation_id=message.correlation_id
        )

    async def _handle_status_request(self, message: AgentMessage):
        """Handle status request messages."""
        status = await self.get_status()
        await self.send_message(
            recipient_id=message.sender_id,
            message_type="status_response",
            payload=status,
            correlation_id=message.correlation_id
        )

    async def _handle_custom_message(self, message: AgentMessage):
        """Handle custom message types. Override in subclasses."""
        self.logger.warning("Unhandled message type", message_type=message.message_type)

    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "name": self.name,
            "is_running": self.is_running,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "message_queue_size": self.message_queue.qsize(),
            "message_history_count": len(self.message_history)
        }

    async def _heartbeat_monitor(self):
        """Background task to monitor agent health."""
        while self.is_running:
            try:
                # Send heartbeat to other agents
                await self._send_heartbeat()
                
                # Wait before next heartbeat
                await asyncio.sleep(30)  # 30 second intervals
                
            except Exception as e:
                self.logger.error("Error in heartbeat monitor", error=str(e))

    async def _send_heartbeat(self):
        """Send heartbeat to other agents."""
        # In a real implementation, this would broadcast to all known agents
        # For now, we'll just log it
        self.logger.debug("Heartbeat sent")

    async def call_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool (Lambda function).
        
        Args:
            tool_name: Name of the MCP tool to call
            parameters: Parameters to pass to the tool
            
        Returns:
            Response from the MCP tool
        """
        try:
            # In a real implementation, this would use the MCP protocol
            # For now, we'll simulate by calling Lambda directly
            response = self.lambda_client.invoke(
                FunctionName=f"energy-demo-{tool_name}",
                InvocationType='RequestResponse',
                Payload=json.dumps(parameters)
            )
            
            response_payload = json.loads(response['Payload'].read())
            self.logger.info("MCP tool called", 
                           tool_name=tool_name,
                           response=response_payload)
            
            return response_payload
            
        except Exception as e:
            self.logger.error("Error calling MCP tool", 
                            tool_name=tool_name,
                            error=str(e))
            raise

    async def store_timeseries_data(self, table_name: str, records: List[Dict[str, Any]]):
        """
        Store time series data in Amazon Timestream.
        
        Args:
            table_name: Name of the Timestream table
            records: List of records to store
        """
        try:
            # Convert records to Timestream format
            timestream_records = []
            for record in records:
                timestream_records.append({
                    'Dimensions': [
                        {'Name': 'agent_id', 'Value': self.agent_id},
                        {'Name': 'agent_type', 'Value': self.agent_type}
                    ],
                    'MeasureName': record.get('measure_name', 'value'),
                    'MeasureValue': str(record.get('value', 0)),
                    'MeasureValueType': 'DOUBLE',
                    'Time': str(int(record.get('timestamp', datetime.now().timestamp()) * 1000))
                })
            
            # Write to Timestream
            self.timestream_client.write_records(
                DatabaseName='energy_demo',
                TableName=table_name,
                Records=timestream_records
            )
            
            self.logger.info("Time series data stored", 
                           table_name=table_name,
                           record_count=len(records))
            
        except Exception as e:
            self.logger.error("Error storing time series data", 
                            table_name=table_name,
                            error=str(e))
            raise

    async def query_timeseries_data(self, query: str) -> List[Dict[str, Any]]:
        """
        Query time series data from Amazon Timestream.
        
        Args:
            query: SQL query to execute
            
        Returns:
            Query results
        """
        try:
            response = self.timestream_query_client.query(QueryString=query)
            
            # Process results
            results = []
            for row in response['Rows']:
                result = {}
                for i, column in enumerate(response['ColumnInfo']):
                    result[column['Name']] = row['Data'][i].get('ScalarValue')
                results.append(result)
            
            self.logger.info("Time series data queried", 
                           query=query,
                           result_count=len(results))
            
            return results
            
        except Exception as e:
            self.logger.error("Error querying time series data", 
                            query=query,
                            error=str(e))
            raise

    def get_config(self) -> Dict[str, Any]:
        """Get agent configuration."""
        return self.config.dict()

    def update_config(self, updates: Dict[str, Any]):
        """Update agent configuration."""
        for key, value in updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        self.logger.info("Configuration updated", updates=updates)
