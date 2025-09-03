#!/usr/bin/env python3
"""
CDK App for Energy Trading System using DynamoDB

This app deploys foundational infrastructure using DynamoDB instead of Timestream.
"""

import os
from aws_cdk import App, Environment
from dynamodb_infrastructure import DynamoDBEnergyTradingStack

# Get AWS account and region from environment or use defaults
account = os.environ.get('CDK_DEFAULT_ACCOUNT')
region = os.environ.get('CDK_DEFAULT_REGION', 'us-east-1')

# Create environment object
env = Environment(account=account, region=region)

# Create CDK app
app = App()

# Create the stack
DynamoDBEnergyTradingStack(
    app, "DynamoDBEnergyTradingSystem",
    env=env,
    description="Energy Trading System Infrastructure with DynamoDB"
)

# Synthesize the app
app.synth()
