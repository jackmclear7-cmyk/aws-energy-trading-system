#!/usr/bin/env python3
"""
Update IAM Role for Bedrock Agents to include Lambda trust

This script updates the existing IAM role to trust both Bedrock and Lambda services.
"""

import json
import boto3
from botocore.exceptions import ClientError

def update_bedrock_agent_role():
    """Update IAM role for Bedrock agents to include Lambda trust"""
    
    iam_client = boto3.client('iam')
    
    # Updated trust policy for Bedrock agents and Lambda
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
    
    try:
        # Update the role's trust policy
        print("Updating IAM role trust policy...")
        
        response = iam_client.update_assume_role_policy(
            RoleName='BedrockAgentRole',
            PolicyDocument=json.dumps(trust_policy)
        )
        
        print("✅ Updated IAM role trust policy")
        print("   Role now trusts both Bedrock and Lambda services")
        
        return True
        
    except ClientError as e:
        print(f"❌ Failed to update IAM role: {e}")
        return False

def main():
    """Main function"""
    print("🔐 Updating IAM Role for Bedrock Agents")
    print("=" * 50)
    
    success = update_bedrock_agent_role()
    
    if success:
        print("\n🎉 IAM role update completed successfully!")
        print("   Bedrock agents and Lambda functions can now use this role.")
    else:
        print("\n❌ IAM role update failed!")
        return False
    
    return True

if __name__ == "__main__":
    main()
