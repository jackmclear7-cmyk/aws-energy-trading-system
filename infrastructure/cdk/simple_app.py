#!/usr/bin/env python3
"""
Simple CDK App for Energy Trading System

This app deploys only the foundational infrastructure without ECS services.
"""

import os
from aws_cdk import App, Environment
from simple_infrastructure import SimpleEnergyTradingStack

# Get AWS account and region from environment or use defaults
account = os.environ.get('CDK_DEFAULT_ACCOUNT')
region = os.environ.get('CDK_DEFAULT_REGION', 'us-east-1')

# Create environment object
env = Environment(account=account, region=region)

# Create CDK app
app = App()

# Create the stack
SimpleEnergyTradingStack(
    app, "SimpleEnergyTradingSystem",
    env=env,
    description="Simple Energy Trading System Infrastructure"
)

# Synthesize the app
app.synth()
