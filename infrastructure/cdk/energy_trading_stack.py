#!/usr/bin/env python3
"""
CDK Stack for Energy Trading System

This stack defines the main infrastructure components for the energy trading system.
"""

from aws_cdk import (
    Stack, Tags,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_applicationautoscaling as appscaling,
    aws_logs as logs,
    aws_iam as iam,
    Duration, Size
)
from constructs import Construct

from energy_trading_infrastructure import EnergyTradingInfrastructure


class EnergyTradingStack(Stack):
    """
    Main CDK stack for the energy trading system.
    """
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # Create the infrastructure components
        infrastructure = EnergyTradingInfrastructure(
            self, "EnergyTradingInfrastructure"
        )
        
        # Create ECS cluster for running agents
        self._create_ecs_cluster()
        
        # Create ECS services for each agent type
        self._create_agent_services(infrastructure)
        
        # Create monitoring and logging
        self._create_monitoring_resources(infrastructure)
        
        # Add tags
        Tags.of(self).add("Project", "EnergyTradingSystem")
        Tags.of(self).add("Environment", "demo")

    def _create_ecs_cluster(self):
        """Create ECS cluster for running the energy trading agents."""
        
        # Create VPC
        self.vpc = ec2.Vpc(
            self, "EnergyTradingVPC",
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ]
        )
        
        # Create ECS cluster
        self.cluster = ecs.Cluster(
            self, "EnergyTradingCluster",
            vpc=self.vpc,
            cluster_name="energy-trading-cluster",
            container_insights=True
        )
        
        # Add capacity to cluster
        self.cluster.add_capacity(
            "DefaultAutoScalingGroupCapacity",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3,
                ec2.InstanceSize.MEDIUM
            ),
            desired_capacity=2,
            min_capacity=1,
            max_capacity=5
        )

    def _create_agent_services(self, infrastructure):
        """Create ECS services for each agent type."""
        
        # Common task execution role
        task_execution_role = iam.Role(
            self, "AgentTaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
            ]
        )
        
        # Add permissions for accessing infrastructure
        task_execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "timestream:WriteRecords",
                    "timestream:Select",
                    "timestream:DescribeEndpoints",
                    "lambda:InvokeFunction",
                    "s3:GetObject",
                    "s3:PutObject",
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=["*"]
            )
        )
        
        # Create Forecasting Agent service
        self.forecasting_service = self._create_agent_service(
            "forecasting-agent",
            "Forecasting Agent",
            task_execution_role,
            infrastructure,
            environment={
                "TIMESTREAM_DATABASE": infrastructure.timestream_database.database_name,
                "FORECAST_TABLE": infrastructure.timestream_tables["forecast_data"].table_name,
                "WEATHER_LAMBDA": infrastructure.lambda_functions["weather_forecast"].function_name,
                "HISTORICAL_LAMBDA": infrastructure.lambda_functions["historical_data"].function_name
            }
        )
        
        # Create Producer Agent service
        self.producer_service = self._create_agent_service(
            "producer-agent",
            "Producer Agent",
            task_execution_role,
            infrastructure,
            environment={
                "TIMESTREAM_DATABASE": infrastructure.timestream_database.database_name,
                "PRODUCER_TABLE": infrastructure.timestream_tables["producer_metrics"].table_name,
                "MARKET_SUPERVISOR_ID": "market_supervisor_agent"
            }
        )
        
        # Create Consumer Agent service
        self.consumer_service = self._create_agent_service(
            "consumer-agent",
            "Consumer Agent",
            task_execution_role,
            infrastructure,
            environment={
                "TIMESTREAM_DATABASE": infrastructure.timestream_database.database_name,
                "CONSUMER_TABLE": infrastructure.timestream_tables["consumer_metrics"].table_name,
                "MARKET_SUPERVISOR_ID": "market_supervisor_agent"
            }
        )
        
        # Create Market Supervisor Agent service
        self.market_service = self._create_agent_service(
            "market-supervisor-agent",
            "Market Supervisor Agent",
            task_execution_role,
            infrastructure,
            environment={
                "TIMESTREAM_DATABASE": infrastructure.timestream_database.database_name,
                "MARKET_TABLE": infrastructure.timestream_tables["market_data"].table_name,
                "TRADE_TABLE": infrastructure.timestream_tables["trade_data"].table_name
            }
        )
        
        # Create Grid Optimization Agent service
        self.grid_service = self._create_agent_service(
            "grid-optimization-agent",
            "Grid Optimization Agent",
            task_execution_role,
            infrastructure,
            environment={
                "TIMESTREAM_DATABASE": infrastructure.timestream_database.database_name,
                "GRID_TABLE": infrastructure.timestream_tables["grid_metrics"].table_name
            }
        )

    def _create_agent_service(self, service_name: str, display_name: str, 
                            task_execution_role: iam.Role, infrastructure: EnergyTradingInfrastructure,
                            environment: dict = None):
        """Create an ECS service for a specific agent type."""
        
        # Create task definition
        task_definition = ecs.FargateTaskDefinition(
            self, f"{service_name}-task",
            execution_role=task_execution_role,
            task_role=task_execution_role,
            memory_limit_mib=512,
            cpu=256
        )
        
        # Add container to task definition
        container = task_definition.add_container(
            f"{service_name}-container",
            image=ecs.ContainerImage.from_asset(f"../agents/{service_name.replace('-', '/')}"),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix=service_name,
                log_retention=logs.RetentionDays.ONE_WEEK
            ),
            environment=environment or {},
            health_check=ecs.HealthCheck(
                command=["CMD-SHELL", "python -c 'import requests; requests.get(\"http://localhost:8000/health\")'"],
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                retries=3,
                start_period=Duration.seconds(60)
            )
        )
        
        # Add port mapping
        container.add_port_mappings(
            ecs.PortMapping(container_port=8000)
        )
        
        # Create service
        service = ecs.FargateService(
            self, f"{service_name}-service",
            cluster=self.cluster,
            task_definition=task_definition,
            service_name=service_name,
            desired_count=1,
            assign_public_ip=True,
            security_groups=[
                ec2.SecurityGroup(
                    self, f"{service_name}-sg",
                    vpc=self.vpc,
                    description=f"Security group for {display_name}",
                    allow_all_outbound=True
                )
            ]
        )
        
        # Add auto-scaling
        scaling = service.auto_scale_task_count(
            min_capacity=1,
            max_capacity=3
        )
        
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60)
        )
        
        scaling.scale_on_memory_utilization(
            "MemoryScaling",
            target_utilization_percent=80,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60)
        )
        
        return service

    def _create_monitoring_resources(self, infrastructure):
        """Create monitoring and logging resources."""
        
        # CloudWatch log group for all services
        self.log_group = logs.LogGroup(
            self, "EnergyTradingLogs",
            log_group_name="/aws/ecs/energy-trading",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=logs.RemovalPolicy.DESTROY
        )
        
        # CloudWatch dashboard for monitoring
        self.monitoring_dashboard = logs.CfnDashboard(
            self, "EnergyTradingMonitoringDashboard",
            dashboard_name="EnergyTradingMonitoring",
            dashboard_body="""
            {
                "widgets": [
                    {
                        "type": "metric",
                        "properties": {
                            "metrics": [
                                ["AWS/ECS", "CPUUtilization", "ServiceName", "forecasting-agent-service"],
                                ["AWS/ECS", "CPUUtilization", "ServiceName", "producer-agent-service"],
                                ["AWS/ECS", "CPUUtilization", "ServiceName", "consumer-agent-service"],
                                ["AWS/ECS", "CPUUtilization", "ServiceName", "market-supervisor-agent-service"],
                                ["AWS/ECS", "CPUUtilization", "ServiceName", "grid-optimization-agent-service"]
                            ],
                            "period": 300,
                            "stat": "Average",
                            "region": "us-east-1",
                            "title": "Agent CPU Utilization"
                        }
                    },
                    {
                        "type": "metric",
                        "properties": {
                            "metrics": [
                                ["AWS/ECS", "MemoryUtilization", "ServiceName", "forecasting-agent-service"],
                                ["AWS/ECS", "MemoryUtilization", "ServiceName", "producer-agent-service"],
                                ["AWS/ECS", "MemoryUtilization", "ServiceName", "consumer-agent-service"],
                                ["AWS/ECS", "MemoryUtilization", "ServiceName", "market-supervisor-agent-service"],
                                ["AWS/ECS", "MemoryUtilization", "ServiceName", "grid-optimization-agent-service"]
                            ],
                            "period": 300,
                            "stat": "Average",
                            "region": "us-east-1",
                            "title": "Agent Memory Utilization"
                        }
                    },
                    {
                        "type": "metric",
                        "properties": {
                            "metrics": [
                                ["AWS/Timestream", "UserRecords", "DatabaseName", "energy_trading_db"]
                            ],
                            "period": 300,
                            "stat": "Sum",
                            "region": "us-east-1",
                            "title": "Timestream Records Written"
                        }
                    }
                ]
            }
            """
        )
        
        # CloudWatch alarms for service health
        self._create_service_alarms()

    def _create_service_alarms(self):
        """Create CloudWatch alarms for service health monitoring."""
        
        # CPU utilization alarm
        self.cpu_alarm = logs.CfnMetricFilter(
            self, "HighCPUAlarm",
            log_group_name="/aws/ecs/energy-trading",
            metric_transformations=[
                logs.CfnMetricFilter.MetricTransformationProperty(
                    metric_name="HighCPUUtilization",
                    metric_namespace="EnergyTrading",
                    metric_value="1"
                )
            ],
            filter_pattern="[timestamp, level, service, message]"
        )
        
        # Memory utilization alarm
        self.memory_alarm = logs.CfnMetricFilter(
            self, "HighMemoryAlarm",
            log_group_name="/aws/ecs/energy-trading",
            metric_transformations=[
                logs.CfnMetricFilter.MetricTransformationProperty(
                    metric_name="HighMemoryUtilization",
                    metric_namespace="EnergyTrading",
                    metric_value="1"
                )
            ],
            filter_pattern="[timestamp, level, service, message]"
        )
        
        # Error rate alarm
        self.error_alarm = logs.CfnMetricFilter(
            self, "HighErrorRateAlarm",
            log_group_name="/aws/ecs/energy-trading",
            metric_transformations=[
                logs.CfnMetricFilter.MetricTransformationProperty(
                    metric_name="HighErrorRate",
                    metric_namespace="EnergyTrading",
                    metric_value="1"
                )
            ],
            filter_pattern="[timestamp, level=ERROR, service, message]"
        )
