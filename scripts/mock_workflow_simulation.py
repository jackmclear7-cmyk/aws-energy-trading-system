#!/usr/bin/env python3
"""
Mock Energy Trading Workflow Simulation

This script simulates the energy trading workflow with realistic agent interactions
and generates data for the frontend dashboard.
"""

import json
import time
import random
from datetime import datetime, timedelta

def generate_mock_workflow_data():
    """Generate realistic mock data for the energy trading workflow"""
    
    print("🔄 Generating Mock Energy Trading Workflow")
    print("=" * 60)
    
    workflow_steps = []
    current_time = time.time()
    
    # Step 1: Forecasting Agent - Weather and Demand Forecast
    print("📊 Step 1: Weather and Demand Forecasting")
    print("-" * 40)
    
    forecast_data = {
        'step': 1,
        'agent': 'forecasting-agent',
        'action': 'weather_demand_forecast',
        'status': 'success',
        'timestamp': current_time,
        'duration': 2.3,
        'data': {
            'weather_forecast': {
                'temperature': 22.5,
                'humidity': 65,
                'wind_speed': 12.3,
                'cloud_cover': 30,
                'solar_irradiance': 850
            },
            'demand_forecast': {
                'peak_demand': 1250,  # MW
                'off_peak_demand': 800,  # MW
                'demand_growth': 2.3  # %
            },
            'solar_production': {
                'expected_generation': 450,  # MW
                'capacity_factor': 0.75,
                'peak_hours': 6
            }
        },
        'response': "Based on current weather conditions, I predict 450MW of solar generation today with peak demand reaching 1250MW. Cloud cover is minimal, so solar production should be optimal."
    }
    
    workflow_steps.append(forecast_data)
    current_time += 2.3
    
    # Step 2: Producer Agent - Solar Production Optimization
    print("☀️ Step 2: Solar Production Optimization")
    print("-" * 40)
    
    producer_data = {
        'step': 2,
        'agent': 'producer-agent',
        'action': 'production_optimization',
        'status': 'success',
        'timestamp': current_time,
        'duration': 1.8,
        'data': {
            'production_strategy': {
                'direct_sale': 300,  # MW
                'battery_storage': 150,  # MW
                'optimal_pricing': 0.085  # $/kWh
            },
            'battery_management': {
                'charge_during': 'off-peak',
                'discharge_during': 'peak',
                'storage_efficiency': 0.92
            },
            'market_participation': {
                'bid_price': 0.082,  # $/kWh
                'offer_quantity': 300,  # MW
                'market_clearing': True
            }
        },
        'response': "I'll sell 300MW directly to the grid at $0.082/kWh and store 150MW in batteries for peak hours. This strategy maximizes revenue while maintaining grid stability."
    }
    
    workflow_steps.append(producer_data)
    current_time += 1.8
    
    # Step 3: Consumer Agent - Energy Consumption Optimization
    print("🏭 Step 3: Consumer Energy Optimization")
    print("-" * 40)
    
    consumer_data = {
        'step': 3,
        'agent': 'consumer-agent',
        'action': 'consumption_optimization',
        'status': 'success',
        'timestamp': current_time,
        'duration': 2.1,
        'data': {
            'consumption_strategy': {
                'grid_purchase': 200,  # MW
                'battery_usage': 50,  # MW
                'demand_response': 25  # MW
            },
            'cost_optimization': {
                'expected_cost': 16800,  # $/day
                'savings_vs_baseline': 12.5,  # %
                'peak_avoidance': 75  # MW
            },
            'battery_management': {
                'charge_during': 'off-peak',
                'discharge_during': 'peak',
                'state_of_charge': 0.85
            }
        },
        'response': "I'll purchase 200MW from the grid during off-peak hours and use 50MW from batteries during peak. This reduces costs by 12.5% while maintaining production."
    }
    
    workflow_steps.append(consumer_data)
    current_time += 2.1
    
    # Step 4: Market Supervisor - Trade Execution
    print("💼 Step 4: Market Trade Execution")
    print("-" * 40)
    
    market_data = {
        'step': 4,
        'agent': 'market-supervisor-agent',
        'action': 'trade_execution',
        'status': 'success',
        'timestamp': current_time,
        'duration': 1.5,
        'data': {
            'order_matching': {
                'buy_orders': 3,
                'sell_orders': 2,
                'matched_trades': 5,
                'total_volume': 500  # MW
            },
            'price_discovery': {
                'market_clearing_price': 0.083,  # $/kWh
                'price_volatility': 0.02,
                'liquidity': 'high'
            },
            'trade_settlement': {
                'total_value': 41500,  # $
                'settlement_time': 'T+1',
                'payment_status': 'pending'
            }
        },
        'response': "Successfully matched 5 trades totaling 500MW at a clearing price of $0.083/kWh. Total trade value is $41,500. Settlement will occur T+1."
    }
    
    workflow_steps.append(market_data)
    current_time += 1.5
    
    # Step 5: Grid Optimization - Stability Monitoring
    print("⚡ Step 5: Grid Stability Monitoring")
    print("-" * 40)
    
    grid_data = {
        'step': 5,
        'agent': 'grid-optimization-agent',
        'action': 'grid_monitoring',
        'status': 'success',
        'timestamp': current_time,
        'duration': 1.2,
        'data': {
            'grid_metrics': {
                'frequency': 59.98,  # Hz
                'voltage': 1.02,  # p.u.
                'power_balance': 0.95,
                'stability_margin': 0.15
            },
            'demand_response': {
                'active_programs': 2,
                'total_reduction': 75,  # MW
                'response_time': 2.3  # minutes
            },
            'grid_health': {
                'status': 'stable',
                'alerts': 0,
                'maintenance_required': False
            }
        },
        'response': "Grid is stable with frequency at 59.98Hz and voltage within normal range. Demand response programs are active, reducing load by 75MW. No alerts or maintenance required."
    }
    
    workflow_steps.append(grid_data)
    
    # Save workflow results
    with open('workflow_results.json', 'w') as f:
        json.dump(workflow_steps, f, indent=2)
    
    print(f"\n📄 Workflow results saved to: workflow_results.json")
    print(f"🎯 Completed {len(workflow_steps)} workflow steps")
    
    return workflow_steps

def generate_real_time_events():
    """Generate real-time events for the dashboard"""
    
    events = []
    current_time = time.time()
    
    # Generate events over the last hour
    for i in range(20):
        event_time = current_time - (3600 - i * 180)  # Every 3 minutes
        
        event_types = [
            'trade_executed',
            'price_updated',
            'demand_response_triggered',
            'battery_charged',
            'battery_discharged',
            'grid_alert',
            'weather_update',
            'market_clearing'
        ]
        
        event = {
            'id': f"event_{i+1}",
            'timestamp': event_time,
            'type': random.choice(event_types),
            'agent': random.choice(['producer-agent', 'consumer-agent', 'market-supervisor-agent', 'grid-optimization-agent']),
            'message': f"Event {i+1} occurred",
            'severity': random.choice(['info', 'warning', 'success', 'error']),
            'data': {
                'value': random.uniform(100, 1000),
                'unit': 'MW',
                'change': random.uniform(-0.1, 0.1)
            }
        }
        
        events.append(event)
    
    # Save events
    with open('real_time_events.json', 'w') as f:
        json.dump(events, f, indent=2)
    
    return events

def main():
    """Main simulation function"""
    print("🎭 Mock Energy Trading Workflow Simulation")
    print("=" * 60)
    
    # Generate workflow data
    workflow_steps = generate_mock_workflow_data()
    
    # Generate real-time events
    events = generate_real_time_events()
    
    print(f"\n✅ Simulation completed successfully!")
    print(f"📊 {len(workflow_steps)} workflow steps generated")
    print(f"📈 {len(events)} real-time events generated")
    
    # Summary
    print("\n📋 Workflow Summary:")
    print("-" * 40)
    for step in workflow_steps:
        print(f"Step {step['step']}: {step['agent']} - {step['action']} ✅")
    
    print(f"\n🎉 Mock data ready for frontend dashboard!")
    return True

if __name__ == "__main__":
    main()
