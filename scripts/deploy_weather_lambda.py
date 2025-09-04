"""
Deploy Weather Lambda Function to AWS
This script creates and deploys the weather Lambda function for MCP integration
"""

import boto3
import json
import zipfile
import os
import time
from botocore.exceptions import ClientError

def create_weather_lambda():
    """
    Create and deploy the weather Lambda function
    """
    print("🌤️ Deploying Weather Lambda Function for MCP Integration")
    print("=" * 60)
    
    # Initialize AWS clients
    lambda_client = boto3.client('lambda')
    iam_client = boto3.client('iam')
    
    function_name = 'weather-forecast'
    role_name = 'weather-lambda-role'
    
    try:
        # Step 1: Create IAM role for Lambda
        print("📋 Step 1: Creating IAM role...")
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        # Create role
        try:
            role_response = iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Role for Weather Lambda function'
            )
            print(f"✅ Created IAM role: {role_name}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                print(f"ℹ️ IAM role {role_name} already exists")
            else:
                raise e
        
        # Attach policies
        policies = [
            'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
            'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
            'arn:aws:iam::aws:policy/AmazonWeatherFullAccess'  # For AWS Weather API
        ]
        
        for policy_arn in policies:
            try:
                iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
                print(f"✅ Attached policy: {policy_arn}")
            except ClientError as e:
                if e.response['Error']['Code'] == 'EntityAlreadyExists':
                    print(f"ℹ️ Policy {policy_arn} already attached")
                else:
                    print(f"⚠️ Warning: Could not attach policy {policy_arn}: {e}")
        
        # Wait for role to be ready
        print("⏳ Waiting for IAM role to be ready...")
        time.sleep(10)
        
        # Get role ARN
        role_response = iam_client.get_role(RoleName=role_name)
        role_arn = role_response['Role']['Arn']
        print(f"✅ Role ARN: {role_arn}")
        
        # Step 2: Create Lambda deployment package
        print("\n📦 Step 2: Creating deployment package...")
        
        # Create zip file
        zip_path = 'weather_lambda.zip'
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            # Add the Lambda function code
            zip_file.write('scripts/weather_lambda_function.py', 'lambda_function.py')
            
            # Add any additional dependencies if needed
            # For now, we only use boto3 which is available in Lambda runtime
        
        print(f"✅ Created deployment package: {zip_path}")
        
        # Step 3: Create or update Lambda function
        print("\n🚀 Step 3: Creating Lambda function...")
        
        with open(zip_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        try:
            # Try to create new function
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.9',
                Role=role_arn,
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_content},
                Description='Weather forecast function for energy trading system MCP integration',
                Timeout=30,
                MemorySize=256,
                Environment={
                    'Variables': {
                        'LOG_LEVEL': 'INFO',
                        'CACHE_TTL': '3600'
                    }
                },
                Tags={
                    'Project': 'EnergyTradingDemo',
                    'Component': 'WeatherAPI',
                    'Purpose': 'MCPIntegration'
                }
            )
            print(f"✅ Created Lambda function: {function_name}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceConflictException':
                # Function exists, update it
                print(f"ℹ️ Function {function_name} exists, updating...")
                
                # Update function code
                lambda_client.update_function_code(
                    FunctionName=function_name,
                    ZipFile=zip_content
                )
                
                # Update function configuration
                lambda_client.update_function_configuration(
                    FunctionName=function_name,
                    Runtime='python3.9',
                    Role=role_arn,
                    Handler='lambda_function.lambda_handler',
                    Description='Weather forecast function for energy trading system MCP integration',
                    Timeout=30,
                    MemorySize=256,
                    Environment={
                        'Variables': {
                            'LOG_LEVEL': 'INFO',
                            'CACHE_TTL': '3600'
                        }
                    }
                )
                
                print(f"✅ Updated Lambda function: {function_name}")
            else:
                raise e
        
        # Step 4: Test the function
        print("\n🧪 Step 4: Testing Lambda function...")
        
        test_payload = {
            'action': 'get_forecast',
            'hours': 24,
            'location': {'latitude': 40.7128, 'longitude': -74.0060}
        }
        
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_payload)
        )
        
        result = json.loads(response['Payload'].read())
        
        if result.get('statusCode') == 200:
            print("✅ Lambda function test successful!")
            print(f"📊 Response: {json.dumps(result, indent=2)[:200]}...")
        else:
            print(f"❌ Lambda function test failed: {result}")
        
        # Step 5: Create DynamoDB table for caching
        print("\n🗄️ Step 5: Creating DynamoDB cache table...")
        
        dynamodb = boto3.resource('dynamodb')
        
        try:
            table = dynamodb.create_table(
                TableName='weather-forecast-cache',
                KeySchema=[
                    {
                        'AttributeName': 'location',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'timestamp',
                        'KeyType': 'RANGE'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'location',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'timestamp',
                        'AttributeType': 'S'
                    }
                ],
                BillingMode='PAY_PER_REQUEST',
                Tags=[
                    {
                        'Key': 'Project',
                        'Value': 'EnergyTradingDemo'
                    },
                    {
                        'Key': 'Component',
                        'Value': 'WeatherCache'
                    }
                ]
            )
            
            print("⏳ Waiting for table to be created...")
            table.wait_until_exists()
            print("✅ Created DynamoDB table: weather-forecast-cache")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print("ℹ️ DynamoDB table weather-forecast-cache already exists")
            else:
                print(f"⚠️ Warning: Could not create DynamoDB table: {e}")
        
        # Cleanup
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print(f"🧹 Cleaned up deployment package: {zip_path}")
        
        print("\n🎉 Weather Lambda Function Deployment Complete!")
        print("=" * 60)
        print(f"✅ Function Name: {function_name}")
        print(f"✅ Function ARN: {lambda_client.get_function(FunctionName=function_name)['Configuration']['FunctionArn']}")
        print(f"✅ IAM Role: {role_arn}")
        print(f"✅ Cache Table: weather-forecast-cache")
        print("\n📡 Test the function:")
        print(f"aws lambda invoke --function-name {function_name} --payload '{{\"action\":\"get_forecast\",\"hours\":24}}' response.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Error deploying weather Lambda function: {e}")
        return False

if __name__ == "__main__":
    success = create_weather_lambda()
    if success:
        print("\n🚀 Weather Lambda function is ready for MCP integration!")
    else:
        print("\n❌ Deployment failed. Please check the errors above.")

