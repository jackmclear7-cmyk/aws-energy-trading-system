#!/usr/bin/env python3
"""
CDK App for Energy Trading System Infrastructure

This CDK app deploys the AWS infrastructure needed for the energy trading system,
including Timestream, Lambda functions, and other supporting services.
"""

import os
from aws_cdk import (
    App, Environment, Tags,
    aws_timestream as timestream,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_s3 as s3,
    aws_sagemaker as sagemaker,
    aws_quicksight as quicksight,
    aws_logs as logs,
    aws_events as events,
    aws_events_targets as targets,
    Duration, RemovalPolicy
)
from constructs import Construct

from energy_trading_stack import EnergyTradingStack


class EnergyTradingInfrastructure(Construct):
    """
    Infrastructure construct for the energy trading system.
    """
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # Create S3 bucket for data lake
        self.data_lake = s3.Bucket(
            self, "EnergyDataLake",
            bucket_name=f"energy-trading-data-{os.environ.get('CDK_DEFAULT_ACCOUNT', 'demo')}",
            versioned=True,
            removal_policy=RemovalPolicy.RETAIN,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DataRetention",
                    enabled=True,
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(30)
                        ),
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(90)
                        )
                    ]
                )
            ]
        )
        
        # Create Timestream database and tables
        self.timestream_db = timestream.CfnDatabase(
            self, "EnergyTradingDatabase",
            database_name="energy_trading_db"
        )
        
        # Energy metrics table
        self.energy_metrics_table = timestream.CfnTable(
            self, "EnergyMetricsTable",
            database_name=self.timestream_db.database_name,
            table_name="energy_metrics",
            retention_properties=timestream.CfnTable.RetentionPropertiesProperty(
                memory_store_retention_period_in_hours=24,
                magnetic_store_retention_period_in_days=7
            )
        )
        
        # Market metrics table
        self.market_metrics_table = timestream.CfnTable(
            self, "MarketMetricsTable",
            database_name=self.timestream_db.database_name,
            table_name="market_metrics",
            retention_properties=timestream.CfnTable.RetentionPropertiesProperty(
                memory_store_retention_period_in_hours=24,
                magnetic_store_retention_period_in_days=7
            )
        )
        
        # Forecast metrics table
        self.forecast_metrics_table = timestream.CfnTable(
            self, "ForecastMetricsTable",
            database_name=self.timestream_db.database_name,
            table_name="forecast_metrics",
            retention_properties=timestream.CfnTable.RetentionPropertiesProperty(
                memory_store_retention_period_in_hours=24,
                magnetic_store_retention_period_in_days=7
            )
        )
        
        # Producer metrics table
        self.producer_metrics_table = timestream.CfnTable(
            self, "ProducerMetricsTable",
            database_name=self.timestream_db.database_name,
            table_name="producer_metrics",
            retention_properties=timestream.CfnTable.RetentionPropertiesProperty(
                memory_store_retention_period_in_hours=24,
                magnetic_store_retention_period_in_days=7
            )
        )
        
        # Consumer metrics table
        self.consumer_metrics_table = timestream.CfnTable(
            self, "ConsumerMetricsTable",
            database_name=self.timestream_db.database_name,
            table_name="consumer_metrics",
            retention_properties=timestream.CfnTable.RetentionPropertiesProperty(
                memory_store_retention_period_in_hours=24,
                magnetic_store_retention_period_in_days=7
            )
        )
        
        # Grid metrics table
        self.grid_metrics_table = timestream.CfnTable(
            self, "GridMetricsTable",
            database_name=self.timestream_db.database_name,
            table_name="grid_metrics",
            retention_properties=timestream.CfnTable.RetentionPropertiesProperty(
                memory_store_retention_period_in_hours=24,
                magnetic_store_retention_period_in_days=7
            )
        )
        
        # Trade metrics table
        self.trade_metrics_table = timestream.CfnTable(
            self, "TradeMetricsTable",
            database_name=self.timestream_db.database_name,
            table_name="trade_metrics",
            retention_properties=timestream.CfnTable.RetentionPropertiesProperty(
                memory_store_retention_period_in_hours=24,
                magnetic_store_retention_period_in_days=7
            )
        )
        
        # Create Lambda functions for MCP tools
        self._create_mcp_lambda_functions()
        
        # Create SageMaker endpoint for ML forecasting
        self._create_sagemaker_endpoint()
        
        # Create QuickSight dashboard
        self._create_quicksight_dashboard()
        
        # Create CloudWatch dashboards and alarms
        self._create_monitoring_resources()
        
        # Add tags
        Tags.of(self).add("Project", "EnergyTradingSystem")
        Tags.of(self).add("Environment", os.environ.get("CDK_DEFAULT_ENVIRONMENT", "demo"))

    def _create_mcp_lambda_functions(self):
        """Create Lambda functions that serve as MCP tools."""
        
        # Common Lambda execution role
        lambda_role = iam.Role(
            self, "MCPLambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        
        # Add Timestream permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "timestream:WriteRecords",
                    "timestream:DescribeEndpoints"
                ],
                resources=["*"]
            )
        )
        
        # Weather forecast Lambda function
        self.weather_forecast_lambda = lambda_.Function(
            self, "WeatherForecastLambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambda/weather-forecast"),
            role=lambda_role,
            function_name="energy-demo-weather-forecast",
            timeout=Duration.seconds(30),
            environment={
                "TIMESTREAM_DATABASE": self.timestream_db.database_name,
                "TIMESTREAM_TABLE": self.forecast_metrics_table.table_name
            }
        )
        
        # Historical energy data Lambda function
        self.historical_data_lambda = lambda_.Function(
            self, "HistoricalDataLambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambda/historical-data"),
            role=lambda_role,
            function_name="energy-demo-historical-energy-data",
            timeout=Duration.seconds(30),
            environment={
                "TIMESTREAM_DATABASE": self.timestream_db.database_name,
                "S3_BUCKET": self.data_lake.bucket_name
            }
        )
        
        # Energy forecasting model Lambda function
        self.forecasting_model_lambda = lambda_.Function(
            self, "ForecastingModelLambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambda/forecasting-model"),
            role=lambda_role,
            function_name="energy-demo-energy-forecasting-model",
            timeout=Duration.seconds(60),
            environment={
                "TIMESTREAM_DATABASE": self.timestream_db.database_name,
                "SAGEMAKER_ENDPOINT": "energy-forecasting-endpoint"
            }
        )

    def _create_sagemaker_endpoint(self):
        """Create SageMaker endpoint for ML forecasting."""
        
        # SageMaker execution role
        sagemaker_role = iam.Role(
            self, "SageMakerExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
            ]
        )
        
        # Add S3 permissions
        sagemaker_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket"
                ],
                resources=[
                    self.data_lake.bucket_arn,
                    f"{self.data_lake.bucket_arn}/*"
                ]
            )
        )
        
        # Add Timestream permissions
        sagemaker_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "timestream:Select",
                    "timestream:DescribeEndpoints"
                ],
                resources=["*"]
            )
        )
        
        # Note: In a real implementation, you would create a SageMaker model and endpoint
        # For this demo, we'll create a placeholder
        self.sagemaker_endpoint = sagemaker.CfnEndpoint(
            self, "EnergyForecastingEndpoint",
            endpoint_name="energy-forecasting-endpoint",
            endpoint_config_name="energy-forecasting-config"
        )

    def _create_quicksight_dashboard(self):
        """Create QuickSight dashboard for visualization."""
        
        # QuickSight admin role
        quicksight_role = iam.Role(
            self, "QuickSightAdminRole",
            assumed_by=iam.ServicePrincipal("quicksight.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonQuickSightServiceRolePolicy")
            ]
        )
        
        # Add data source permissions
        quicksight_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "timestream:Select",
                    "timestream:DescribeEndpoints"
                ],
                resources=["*"]
            )
        )
        
        # Note: QuickSight dashboard creation via CDK is limited
        # In a real implementation, you would create the dashboard via the AWS Console or API

    def _create_monitoring_resources(self):
        """Create CloudWatch dashboards and alarms."""
        
        # CloudWatch dashboard for energy metrics
        self.energy_dashboard = logs.CfnDashboard(
            self, "EnergyMetricsDashboard",
            dashboard_name="EnergyTradingMetrics",
            dashboard_body="""
            {
                "widgets": [
                    {
                        "type": "metric",
                        "properties": {
                            "metrics": [
                                ["AWS/Timestream", "UserRecords", "DatabaseName", "energy_trading_db", "TableName", "energy_metrics"]
                            ],
                            "period": 300,
                            "stat": "Sum",
                            "region": "us-east-1",
                            "title": "Energy Metrics Records"
                        }
                    }
                ]
            }
            """
        )
        
        # CloudWatch alarm for high error rate
        self.error_alarm = events.CfnRule(
            self, "ErrorAlarmRule",
            name="EnergyTradingErrorAlarm",
            description="Alarm for high error rate in energy trading system",
            event_pattern={
                "source": ["aws.lambda"],
                "detail-type": ["Lambda Function Execution Result"],
                "detail": {
                    "status": ["Failed"]
                }
            },
            targets=[
                targets.SnsTopic(
                    topic=events.CfnRule.TargetProperty(
                        id="ErrorNotification"
                    )
                )
            ]
        )


def main():
    """Main CDK app entry point."""
    app = App()
    
    # Get environment variables
    env = Environment(
        account=os.environ.get('CDK_DEFAULT_ACCOUNT'),
        region=os.environ.get('CDK_DEFAULT_REGION', 'us-east-1')
    )
    
    # Create the main stack
    EnergyTradingStack(
        app, "EnergyTradingSystem",
        env=env,
        description="Energy Trading System Infrastructure"
    )
    
    app.synth()


if __name__ == "__main__":
    main()
