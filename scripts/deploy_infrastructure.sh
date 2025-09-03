#!/bin/bash

# Infrastructure Deployment Script
# This script deploys the AWS infrastructure for the energy trading system

set -e

echo "🏗️  Energy Trading System - Infrastructure Deployment"
echo "======================================================"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install AWS CLI first."
    echo "   Visit: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI configured"

# Check if CDK is installed
if ! command -v cdk &> /dev/null; then
    echo "❌ AWS CDK is not installed. Installing..."
    npm install -g aws-cdk
fi

echo "✅ AWS CDK available"

# Get current AWS account and region
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region)

echo "📋 Deployment Details:"
echo "   AWS Account: $AWS_ACCOUNT"
echo "   AWS Region: $AWS_REGION"
echo ""

# Confirm deployment
read -p "Do you want to proceed with deployment? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

# Navigate to CDK directory
cd infrastructure/cdk

# Install dependencies
echo "📥 Installing CDK dependencies..."
npm install

# Bootstrap CDK (if needed)
echo "🚀 Bootstrapping CDK..."
cdk bootstrap

# Deploy the stack
echo "🏗️  Deploying infrastructure stack..."
cdk deploy --require-approval never

echo ""
echo "🎉 Infrastructure deployment completed!"
echo ""
echo "Next steps:"
echo "1. Update your config files with the deployed resource names"
echo "2. Run the simulation: python scripts/run_simulation.py"
echo "3. Check the AWS Console for deployed resources"
echo ""

# Show deployed resources
echo "📋 Deployed Resources:"
echo "   - S3 Bucket: energy-trading-demo-data"
echo "   - Timestream Database: energy-trading-demo"
echo "   - Lambda Functions: weather-forecast, historical-data, trading-api, grid-management"
echo "   - SageMaker Endpoint: energy-forecasting-demo"
echo "   - ECS Cluster: energy-trading-cluster"
echo "   - CloudWatch Dashboard: EnergyTradingDashboard"
echo ""

echo "✨ Deployment completed successfully!"
