#!/usr/bin/env python3
"""
Test AWS Integration for Energy Trading System

This script tests the deployed AWS infrastructure including Lambda functions,
DynamoDB tables, and S3 bucket.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import boto3
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AWSIntegrationTester:
    """Test AWS infrastructure integration"""
    
    def __init__(self):
        self.lambda_client = boto3.client('lambda')
        self.dynamodb = boto3.resource('dynamodb')
        self.s3_client = boto3.client('s3')
        
    async def test_lambda_functions(self):
        """Test all Lambda functions"""
        logger.info("Testing Lambda functions...")
        
        lambda_functions = [
            "weather-forecast-demo",
            "historical-data-demo", 
            "trading-api-demo",
            "grid-management-demo"
        ]
        
        results = {}
        
        for function_name in lambda_functions:
            try:
                logger.info(f"Testing {function_name}...")
                
                response = self.lambda_client.invoke(
                    FunctionName=function_name,
                    Payload=json.dumps({})
                )
                
                # Read the response
                payload = json.loads(response['Payload'].read())
                
                if payload.get('statusCode') == 200:
                    body = json.loads(payload.get('body', '{}'))
                    results[function_name] = {
                        'status': 'success',
                        'data': body
                    }
                    logger.info(f"✅ {function_name} working correctly")
                else:
                    results[function_name] = {
                        'status': 'error',
                        'error': payload
                    }
                    logger.error(f"❌ {function_name} returned error: {payload}")
                    
            except ClientError as e:
                results[function_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                logger.error(f"❌ {function_name} failed: {e}")
                
        return results
    
    async def test_dynamodb_tables(self):
        """Test DynamoDB tables"""
        logger.info("Testing DynamoDB tables...")
        
        table_names = [
            "energy-metrics",
            "market-data",
            "forecast-data",
            "producer-metrics",
            "consumer-metrics",
            "grid-metrics",
            "trade-data"
        ]
        
        results = {}
        
        for table_name in table_names:
            try:
                logger.info(f"Testing table {table_name}...")
                
                table = self.dynamodb.Table(table_name)
                
                # Test table exists and is accessible
                response = self.dynamodb.meta.client.describe_table(TableName=table_name)
                
                results[table_name] = {
                    'status': 'success',
                    'item_count': response['Table'].get('ItemCount', 0),
                    'table_status': response['Table']['TableStatus']
                }
                logger.info(f"✅ Table {table_name} accessible")
                
                # Test writing a sample record
                timestamp = int(time.time())
                sample_item = {
                    'timestamp': str(timestamp),
                    f'{table_name.split("-")[0]}_id': 'test',
                    'test_data': 'integration_test'
                }
                
                table.put_item(Item=sample_item)
                logger.info(f"✅ Successfully wrote test data to {table_name}")
                
            except ClientError as e:
                results[table_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                logger.error(f"❌ Table {table_name} failed: {e}")
                
        return results
    
    async def test_s3_bucket(self):
        """Test S3 bucket"""
        logger.info("Testing S3 bucket...")
        
        bucket_name = "energy-trading-demo-data"
        
        try:
            # Test bucket exists and is accessible
            response = self.s3_client.head_bucket(Bucket=bucket_name)
            
            # Test uploading a test file
            test_key = f"test/integration_test_{int(time.time())}.json"
            test_data = {
                "test": "integration_test",
                "timestamp": time.time(),
                "message": "AWS integration test successful"
            }
            
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=json.dumps(test_data),
                ContentType='application/json'
            )
            
            logger.info(f"✅ Successfully uploaded test file to S3 bucket {bucket_name}")
            
            # Test reading the file back
            response = self.s3_client.get_object(Bucket=bucket_name, Key=test_key)
            retrieved_data = json.loads(response['Body'].read())
            
            if retrieved_data == test_data:
                logger.info("✅ Successfully retrieved test file from S3")
                return {'status': 'success', 'bucket': bucket_name}
            else:
                logger.error("❌ Retrieved data doesn't match uploaded data")
                return {'status': 'error', 'error': 'Data mismatch'}
                
        except ClientError as e:
            logger.error(f"❌ S3 bucket test failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def run_integration_test(self):
        """Run complete integration test"""
        logger.info("🚀 Starting AWS Integration Test")
        logger.info("=" * 50)
        
        results = {}
        
        # Test Lambda functions
        results['lambda_functions'] = await self.test_lambda_functions()
        
        # Test DynamoDB tables
        results['dynamodb_tables'] = await self.test_dynamodb_tables()
        
        # Test S3 bucket
        results['s3_bucket'] = await self.test_s3_bucket()
        
        # Generate summary
        self.generate_summary(results)
        
        return results
    
    def generate_summary(self, results):
        """Generate test summary"""
        logger.info("\n" + "=" * 50)
        logger.info("📊 AWS INTEGRATION TEST SUMMARY")
        logger.info("=" * 50)
        
        # Lambda functions summary
        lambda_results = results.get('lambda_functions', {})
        lambda_success = sum(1 for r in lambda_results.values() if r.get('status') == 'success')
        lambda_total = len(lambda_results)
        
        logger.info(f"🔧 Lambda Functions: {lambda_success}/{lambda_total} working")
        for name, result in lambda_results.items():
            status = "✅" if result.get('status') == 'success' else "❌"
            logger.info(f"   {status} {name}")
        
        # DynamoDB tables summary
        dynamodb_results = results.get('dynamodb_tables', {})
        dynamodb_success = sum(1 for r in dynamodb_results.values() if r.get('status') == 'success')
        dynamodb_total = len(dynamodb_results)
        
        logger.info(f"🗄️  DynamoDB Tables: {dynamodb_success}/{dynamodb_total} working")
        for name, result in dynamodb_results.items():
            status = "✅" if result.get('status') == 'success' else "❌"
            logger.info(f"   {status} {name}")
        
        # S3 bucket summary
        s3_result = results.get('s3_bucket', {})
        s3_status = "✅" if s3_result.get('status') == 'success' else "❌"
        logger.info(f"🪣 S3 Bucket: {s3_status} {s3_result.get('bucket', 'N/A')}")
        
        # Overall status
        total_tests = lambda_total + dynamodb_total + 1  # +1 for S3
        total_success = lambda_success + dynamodb_success + (1 if s3_result.get('status') == 'success' else 0)
        
        logger.info(f"\n🎯 Overall: {total_success}/{total_tests} tests passed")
        
        if total_success == total_tests:
            logger.info("🎉 All AWS services are working correctly!")
            logger.info("   The energy trading system is ready for full deployment.")
        else:
            logger.info("⚠️  Some AWS services have issues. Check the logs above.")
        
        return total_success == total_tests


async def main():
    """Main test function"""
    print("🧪 AWS Integration Test for Energy Trading System")
    print("=" * 60)
    
    tester = AWSIntegrationTester()
    
    try:
        results = await tester.run_integration_test()
        
        # Save results to file
        with open('aws_integration_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"\n📄 Detailed results saved to: aws_integration_test_results.json")
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
