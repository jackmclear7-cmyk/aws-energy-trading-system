#!/usr/bin/env python3
"""
CDK Stack for Energy Trading System using DynamoDB

This stack deploys foundational AWS resources using DynamoDB instead of Timestream.
"""

from aws_cdk import (
    Stack, Tags,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_cloudwatch as cloudwatch,
    Duration, RemovalPolicy
)
from constructs import Construct


class DynamoDBEnergyTradingStack(Stack):
    """
    CDK stack that deploys foundational infrastructure using DynamoDB.
    """
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # Create S3 bucket for data lake
        self.data_lake_bucket = s3.Bucket(
            self, "EnergyTradingDataLake",
            bucket_name="energy-trading-demo-data",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        # Create DynamoDB tables for time-series data
        self.dynamodb_tables = {}
        
        # Energy metrics table
        self.dynamodb_tables["energy_metrics"] = dynamodb.Table(
            self, "EnergyMetricsTable",
            table_name="energy-metrics",
            partition_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="metric_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Market data table
        self.dynamodb_tables["market_data"] = dynamodb.Table(
            self, "MarketDataTable",
            table_name="market-data",
            partition_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="market_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Forecast data table
        self.dynamodb_tables["forecast_data"] = dynamodb.Table(
            self, "ForecastDataTable",
            table_name="forecast-data",
            partition_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="forecast_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Producer metrics table
        self.dynamodb_tables["producer_metrics"] = dynamodb.Table(
            self, "ProducerMetricsTable",
            table_name="producer-metrics",
            partition_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="producer_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Consumer metrics table
        self.dynamodb_tables["consumer_metrics"] = dynamodb.Table(
            self, "ConsumerMetricsTable",
            table_name="consumer-metrics",
            partition_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="consumer_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Grid metrics table
        self.dynamodb_tables["grid_metrics"] = dynamodb.Table(
            self, "GridMetricsTable",
            table_name="grid-metrics",
            partition_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="grid_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Trade data table
        self.dynamodb_tables["trade_data"] = dynamodb.Table(
            self, "TradeDataTable",
            table_name="trade-data",
            partition_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="trade_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Create Lambda functions for MCP tools
        self.lambda_functions = {}
        
        # Weather forecast Lambda
        self.lambda_functions["weather_forecast"] = lambda_.Function(
            self, "WeatherForecastFunction",
            function_name="weather-forecast-demo",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=lambda_.Code.from_inline("""
import json
import random
from datetime import datetime, timedelta

def handler(event, context):
    # Simulate weather forecast data
    forecast = {
        "timestamp": datetime.now().isoformat(),
        "temperature_c": round(random.uniform(15, 30), 1),
        "humidity_percent": round(random.uniform(40, 80), 1),
        "wind_speed_mph": round(random.uniform(5, 20), 1),
        "cloud_cover_percent": round(random.uniform(0, 100), 1),
        "solar_irradiance_wm2": round(random.uniform(200, 1000), 1)
    }
    
    return {
        "statusCode": 200,
        "body": json.dumps(forecast)
    }
            """),
            timeout=Duration.seconds(30)
        )
        
        # Historical data Lambda
        self.lambda_functions["historical_data"] = lambda_.Function(
            self, "HistoricalDataFunction",
            function_name="historical-data-demo",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=lambda_.Code.from_inline("""
import json
import random
from datetime import datetime, timedelta

def handler(event, context):
    # Simulate historical energy data
    historical_data = {
        "timestamp": datetime.now().isoformat(),
        "historical_prices": [round(random.uniform(0.05, 0.15), 3) for _ in range(24)],
        "historical_demand": [round(random.uniform(8, 15), 1) for _ in range(24)],
        "historical_supply": [round(random.uniform(10, 18), 1) for _ in range(24)]
    }
    
    return {
        "statusCode": 200,
        "body": json.dumps(historical_data)
    }
            """),
            timeout=Duration.seconds(30)
        )
        
        # Trading API Lambda
        self.lambda_functions["trading_api"] = lambda_.Function(
            self, "TradingApiFunction",
            function_name="trading-api-demo",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=lambda_.Code.from_inline("""
import json
import random
from datetime import datetime

def handler(event, context):
    # Simulate trading API response
    trade_result = {
        "timestamp": datetime.now().isoformat(),
        "trade_id": f"trade_{random.randint(1000, 9999)}",
        "status": "executed",
        "price": round(random.uniform(0.06, 0.12), 3),
        "quantity": round(random.uniform(1, 5), 1)
    }
    
    return {
        "statusCode": 200,
        "body": json.dumps(trade_result)
    }
            """),
            timeout=Duration.seconds(30)
        )
        
        # Grid management Lambda
        self.lambda_functions["grid_management"] = lambda_.Function(
            self, "GridManagementFunction",
            function_name="grid-management-demo",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=lambda_.Code.from_inline("""
import json
import random
from datetime import datetime

def handler(event, context):
    # Simulate grid management response
    grid_status = {
        "timestamp": datetime.now().isoformat(),
        "frequency_hz": round(random.uniform(59.8, 60.2), 2),
        "voltage_kv": round(random.uniform(13.5, 14.1), 1),
        "stability_score": round(random.uniform(0.7, 1.0), 2),
        "demand_response_active": random.choice([True, False])
    }
    
    return {
        "statusCode": 200,
        "body": json.dumps(grid_status)
    }
            """),
            timeout=Duration.seconds(30)
        )
        
        # Create CloudWatch dashboard
        self.dashboard = cloudwatch.Dashboard(
            self, "EnergyTradingDashboard",
            dashboard_name="EnergyTradingDashboard"
        )
        
        # Create CloudWatch alarm for errors
        self.error_alarm = cloudwatch.Alarm(
            self, "EnergyTradingErrorAlarm",
            alarm_name="EnergyTradingErrors",
            metric=cloudwatch.Metric(
                namespace="AWS/Lambda",
                metric_name="Errors",
                statistic="Sum"
            ),
            threshold=5,
            evaluation_periods=1
        )
        
        # Add tags
        Tags.of(self).add("Project", "EnergyTradingDemo")
        Tags.of(self).add("Environment", "Demo")
