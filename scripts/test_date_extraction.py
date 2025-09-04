#!/usr/bin/env python3
"""
Test script to debug date extraction functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot_bedrock_integration import ChatbotBedrockIntegration
from datetime import datetime

def test_date_extraction():
    """Test the date extraction functionality"""
    integration = ChatbotBedrockIntegration()
    
    test_queries = [
        "What is the weather forecast for Manchester on Friday?",
        "What is the weather forecast for Manchester tomorrow?",
        "What is the weather forecast for Manchester today?",
        "What is the weather forecast for Manchester on Monday?",
        "What is the weather forecast for Manchester next Friday?"
    ]
    
    print("🔍 Testing Date Extraction:")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        
        # Test location extraction
        location = integration.extract_location_from_query(query)
        print(f"📍 Location: {location}")
        
        # Test date extraction
        date_info = integration.extract_date_from_query(query)
        print(f"📅 Date Info: {date_info}")
        
        if date_info.get('target_date'):
            print(f"🗓️  Target Date: {date_info['target_date']}")
            print(f"📊 Days Offset: {date_info['offset_days']}")
        
        if date_info.get('specific_time'):
            print(f"⏰ Specific Time: {date_info['specific_time']}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_date_extraction()

