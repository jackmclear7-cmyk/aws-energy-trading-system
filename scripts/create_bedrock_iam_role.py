#!/usr/bin/env python3
"""
Create IAM Role for Bedrock Agents

This script creates the necessary IAM role and policies for Bedrock agents to access AWS services.
"""

import json
import boto3
from botocore.exceptions import ClientError

def create_bedrock_agent_role():
    """Create IAM role for Bedrock agents"""
    
    iam_client = boto3.client('iam')
    
    # Trust policy for Bedrock agents and Lambda
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": [
                        "bedrock.amazonaws.com",
                        "lambda.amazonaws.com"
                    ]
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Policy for accessing AWS services
    access_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "lambda:InvokeFunction",
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:ListBucket",
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "*"
            }
        ]
    }
    
    try:
        # Create the role
        print("Creating IAM role for Bedrock agents...")
        
        response = iam_client.create_role(
            RoleName='BedrockAgentRole',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Bedrock agents to access AWS services'
        )
        
        print("✅ Created IAM role: BedrockAgentRole")
        
        # Create and attach the policy
        print("Creating and attaching access policy...")
        
        policy_response = iam_client.create_policy(
            PolicyName='BedrockAgentAccessPolicy',
            PolicyDocument=json.dumps(access_policy),
            Description='Policy for Bedrock agents to access AWS services'
        )
        
        policy_arn = policy_response['Policy']['Arn']
        
        iam_client.attach_role_policy(
            RoleName='BedrockAgentRole',
            PolicyArn=policy_arn
        )
        
        print("✅ Created and attached access policy")
        print(f"   Policy ARN: {policy_arn}")
        
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("⚠️  IAM role already exists")
            return True
        else:
            print(f"❌ Failed to create IAM role: {e}")
            return False

def main():
    """Main function"""
    print("🔐 Creating IAM Role for Bedrock Agents")
    print("=" * 50)
    
    success = create_bedrock_agent_role()
    
    if success:
        print("\n🎉 IAM role setup completed successfully!")
        print("   Bedrock agents can now access AWS services.")
    else:
        print("\n❌ IAM role setup failed!")
        return False
    
    return True

if __name__ == "__main__":
    main()
