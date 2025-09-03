#!/usr/bin/env python3
"""
CDK Infrastructure Construct for Energy Trading System

This construct defines the foundational AWS resources for the energy trading system.
"""

from aws_cdk import (
    Stack, Tags,
    aws_s3 as s3,
    aws_timestream as timestream,
    aws_lambda as lambda_,
    aws_sagemaker as sagemaker,
    aws_iam as iam,
    aws_logs as logs,
    aws_cloudwatch as cloudwatch,
    Duration, Size, RemovalPolicy
)
from constructs import Construct


class EnergyTradingInfrastructure(Construct):
    """
    Infrastructure construct that provides foundational AWS resources.
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
        
        # Create Timestream database
        self.timestream_database = timestream.CfnDatabase(
            self, "EnergyTradingDatabase",
            database_name="energy-trading-demo"
        )
        
        # Create Timestream tables
        self.timestream_tables = {}
        
        # Energy metrics table
        self.timestream_tables["energy_metrics"] = timestream.CfnTable(
            self, "EnergyMetricsTable",
            database_name=self.timestream_database.database_name,
            table_name="energy-metrics",
            retention_properties=timestream.CfnTable.RetentionPropertiesProperty(
                memory_store_retention_period_in_hours="24",
                magnetic_store_retention_period_in_days="7"
            )
        )
        
        # Market data table
        self.timestream_tables["market_data"] = timestream.CfnTable(
            self, "MarketDataTable",
            database_name=self.timestream_database.database_name,
            table_name="market-data",
            retention_properties=timestream.CfnTable.RetentionPropertiesProperty(
                memory_store_retention_period_in_hours="24",
                magnetic_store_retention_period_in_days="7"
            )
        )
        
        # Forecast data table
        self.timestream_tables["forecast_data"] = timestream.CfnTable(
            self, "ForecastDataTable",
            database_name=self.timestream_database.database_name,
            table_name="forecast-data",
            retention_properties=timestream.CfnTable.RetentionPropertiesProperty(
                memory_store_retention_period_in_hours="24",
                magnetic_store_retention_period_in_days="7"
            )
        )
        
        # Producer metrics table
        self.timestream_tables["producer_metrics"] = timestream.CfnTable(
            self, "ProducerMetricsTable",
            database_name=self.timestream_database.database_name,
            table_name="producer-metrics",
            retention_properties=timestream.CfnTable.RetentionPropertiesProperty(
                memory_store_retention_period_in_hours="24",
                magnetic_store_retention_period_in_days="7"
            )
        )
        
        # Consumer metrics table
        self.timestream_tables["consumer_metrics"] = timestream.CfnTable(
            self, "ConsumerMetricsTable",
            database_name=self.timestream_database.database_name,
            table_name="consumer-metrics",
            retention_properties=timestream.CfnTable.RetentionPropertiesProperty(
                memory_store_retention_period_in_hours="24",
                magnetic_store_retention_period_in_days="7"
            )
        )
        
        # Grid metrics table
        self.timestream_tables["grid_metrics"] = timestream.CfnTable(
            self, "GridMetricsTable",
            database_name=self.timestream_database.database_name,
            table_name="grid-metrics",
            retention_properties=timestream.CfnTable.RetentionPropertiesProperty(
                memory_store_retention_period_in_hours="24",
                magnetic_store_retention_period_in_days="7"
            )
        )
        
        # Trade data table
        self.timestream_tables["trade_data"] = timestream.CfnTable(
            self, "TradeDataTable",
            database_name=self.timestream_database.database_name,
            table_name="trade-data",
            retention_properties=timestream.CfnTable.RetentionPropertiesProperty(
                memory_store_retention_period_in_hours="24",
                magnetic_store_retention_period_in_days="7"
            )
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
        
        # Create SageMaker endpoint (placeholder)
        self.sagemaker_endpoint = sagemaker.CfnEndpoint(
            self, "EnergyForecastingEndpoint",
            endpoint_name="energy-forecasting-demo",
            endpoint_config_name="energy-forecasting-config-demo"
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
