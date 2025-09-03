#!/usr/bin/env python3
"""
Create Lambda Function for Energy Trading Actions

This script creates a Lambda function that serves as the action group executor for Bedrock agents.
"""

import json
import boto3
import zipfile
import os
from pathlib import Path
from botocore.exceptions import ClientError

def create_lambda_function():
    """Create Lambda function for energy trading actions"""
    
    lambda_client = boto3.client('lambda')
    
    # Lambda function code
    lambda_code = '''
import json
import boto3
import random
from datetime import datetime, timedelta

def lambda_handler(event, context):
    """
    Lambda function to handle energy trading actions for Bedrock agents
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    # Parse the event
    action = event.get('actionGroup', '')
    api_path = event.get('apiPath', '')
    method = event.get('httpMethod', '')
    parameters = event.get('parameters', [])
    request_body = event.get('requestBody', {})
    
    # Initialize AWS clients
    dynamodb = boto3.resource('dynamodb')
    s3_client = boto3.client('s3')
    
    try:
        if api_path == '/weather' and method == 'GET':
            return handle_weather_request(parameters)
        elif api_path == '/trade' and method == 'POST':
            return handle_trade_request(request_body)
        elif api_path == '/historical' and method == 'GET':
            return handle_historical_request(parameters)
        elif api_path == '/grid-status' and method == 'GET':
            return handle_grid_status_request()
        elif api_path == '/store-metrics' and method == 'POST':
            return handle_store_metrics_request(request_body)
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Endpoint not found'})
            }
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def handle_weather_request(parameters):
    """Handle weather forecast requests"""
    
    # Extract location parameter
    location = "default"
    for param in parameters:
        if param['name'] == 'location':
            location = param['value']
            break
    
    # Simulate weather data
    weather_data = {
        'location': location,
        'timestamp': datetime.now().isoformat(),
        'temperature_c': round(random.uniform(15, 30), 1),
        'humidity_percent': round(random.uniform(40, 80), 1),
        'wind_speed_mph': round(random.uniform(5, 20), 1),
        'cloud_cover_percent': round(random.uniform(0, 100), 1),
        'solar_irradiance_wm2': round(random.uniform(200, 1000), 1),
        'forecast_hours': 24
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(weather_data)
    }

def handle_trade_request(request_body):
    """Handle trade order requests"""
    
    if isinstance(request_body, str):
        request_body = json.loads(request_body)
    
    # Validate required fields
    required_fields = ['order_type', 'quantity', 'price', 'agent_id']
    for field in required_fields:
        if field not in request_body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Missing required field: {field}'})
            }
    
    # Create trade record
    trade_id = f"trade_{random.randint(1000, 9999)}"
    trade_record = {
        'trade_id': trade_id,
        'timestamp': datetime.now().isoformat(),
        'order_type': request_body['order_type'],
        'quantity': request_body['quantity'],
        'price': request_body['price'],
        'agent_id': request_body['agent_id'],
        'status': 'executed',
        'total_value': request_body['quantity'] * request_body['price']
    }
    
    # Store in DynamoDB
    try:
        table = boto3.resource('dynamodb').Table('trade-data')
        table.put_item(Item=trade_record)
    except Exception as e:
        print(f"Error storing trade: {e}")
    
    return {
        'statusCode': 200,
        'body': json.dumps(trade_record)
    }

def handle_historical_request(parameters):
    """Handle historical data requests"""
    
    # Extract parameters
    data_type = "prices"
    time_range = "24h"
    
    for param in parameters:
        if param['name'] == 'data_type':
            data_type = param['value']
        elif param['name'] == 'time_range':
            time_range = param['value']
    
    # Generate historical data
    historical_data = {
        'data_type': data_type,
        'time_range': time_range,
        'timestamp': datetime.now().isoformat(),
        'data': []
    }
    
    # Generate sample data points
    hours = 24 if time_range == "24h" else 168 if time_range == "7d" else 720
    
    for i in range(hours):
        timestamp = datetime.now() - timedelta(hours=i)
        if data_type == "prices":
            value = round(random.uniform(0.05, 0.15), 3)
        elif data_type == "demand":
            value = round(random.uniform(8, 15), 1)
        elif data_type == "supply":
            value = round(random.uniform(10, 18), 1)
        else:
            value = round(random.uniform(0, 100), 1)
        
        historical_data['data'].append({
            'timestamp': timestamp.isoformat(),
            'value': value
        })
    
    return {
        'statusCode': 200,
        'body': json.dumps(historical_data)
    }

def handle_grid_status_request():
    """Handle grid status requests"""
    
    grid_status = {
        'timestamp': datetime.now().isoformat(),
        'frequency_hz': round(random.uniform(59.8, 60.2), 2),
        'voltage_kv': round(random.uniform(13.5, 14.1), 1),
        'stability_score': round(random.uniform(0.7, 1.0), 2),
        'demand_response_active': random.choice([True, False]),
        'total_demand_mw': round(random.uniform(100, 200), 1),
        'total_supply_mw': round(random.uniform(95, 205), 1)
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(grid_status)
    }

def handle_store_metrics_request(request_body):
    """Handle store metrics requests"""
    
    if isinstance(request_body, str):
        request_body = json.loads(request_body)
    
    table_name = request_body.get('table_name')
    data = request_body.get('data', {})
    
    if not table_name:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing table_name'})
        }
    
    # Add timestamp if not present
    if 'timestamp' not in data:
        data['timestamp'] = datetime.now().isoformat()
    
    try:
        table = boto3.resource('dynamodb').Table(table_name)
        table.put_item(Item=data)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'success', 'message': 'Data stored successfully'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Failed to store data: {str(e)}'})
        }
'''
    
    # Create deployment package
    print("Creating Lambda deployment package...")
    
    # Create temporary directory
    temp_dir = Path('/tmp/lambda_package')
    temp_dir.mkdir(exist_ok=True)
    
    # Write Lambda code
    with open(temp_dir / 'lambda_function.py', 'w') as f:
        f.write(lambda_code)
    
    # Create zip file
    zip_path = temp_dir / 'energy_trading_actions.zip'
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        zip_file.write(temp_dir / 'lambda_function.py', 'lambda_function.py')
    
    # Read zip file
    with open(zip_path, 'rb') as f:
        zip_content = f.read()
    
    try:
        # Create Lambda function
        print("Creating Lambda function...")
        
        response = lambda_client.create_function(
            FunctionName='energy-trading-actions',
            Runtime='python3.11',
            Role=f'arn:aws:iam::{get_account_id()}:role/BedrockAgentRole',
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='Lambda function for energy trading actions in Bedrock agents',
            Timeout=30,
            MemorySize=256
        )
        
        print("✅ Created Lambda function: energy-trading-actions")
        print(f"   Function ARN: {response['FunctionArn']}")
        
        # Clean up
        os.remove(zip_path)
        os.remove(temp_dir / 'lambda_function.py')
        temp_dir.rmdir()
        
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceConflictException':
            print("⚠️  Lambda function already exists")
            return True
        else:
            print(f"❌ Failed to create Lambda function: {e}")
            return False

def get_account_id():
    """Get AWS account ID"""
    sts_client = boto3.client('sts')
    return sts_client.get_caller_identity()['Account']

def main():
    """Main function"""
    print("⚡ Creating Lambda Function for Energy Trading Actions")
    print("=" * 60)
    
    success = create_lambda_function()
    
    if success:
        print("\n🎉 Lambda function setup completed successfully!")
        print("   Bedrock agents can now execute energy trading actions.")
    else:
        print("\n❌ Lambda function setup failed!")
        return False
    
    return True

if __name__ == "__main__":
    main()
