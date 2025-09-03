#!/usr/bin/env python3
"""
Simple visualization script for the energy trading demo
"""

import matplotlib.pyplot as plt
import numpy as np
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def create_demo_visualization():
    """Create a simple visualization of the energy trading system"""
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('⚡ Energy Trading System Demo', fontsize=16, fontweight='bold')
    
    # Generate sample data
    time_points = np.arange(0, 24, 0.5)  # 30-minute intervals for 24 hours
    
    # 1. Energy Supply and Demand
    solar_production = 10 * np.sin(np.pi * (time_points - 6) / 12) * (time_points >= 6) * (time_points <= 18)
    wind_production = 5 + 2 * np.sin(2 * np.pi * time_points / 24)
    total_supply = solar_production + wind_production
    
    base_demand = 8 + 3 * np.sin(2 * np.pi * (time_points - 6) / 24)
    peak_demand = base_demand + 2 * np.sin(4 * np.pi * time_points / 24)
    
    ax1.plot(time_points, total_supply, 'g-', label='Total Supply', linewidth=2)
    ax1.plot(time_points, peak_demand, 'r-', label='Demand', linewidth=2)
    ax1.fill_between(time_points, 0, total_supply, alpha=0.3, color='green')
    ax1.fill_between(time_points, 0, peak_demand, alpha=0.3, color='red')
    ax1.set_xlabel('Hour of Day')
    ax1.set_ylabel('Power (MW)')
    ax1.set_title('Energy Supply vs Demand')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Energy Prices
    base_price = 0.08 + 0.02 * np.sin(2 * np.pi * time_points / 24)
    price_volatility = 0.01 * np.random.normal(0, 1, len(time_points))
    energy_prices = base_price + price_volatility
    
    ax2.plot(time_points, energy_prices, 'b-', linewidth=2)
    ax2.fill_between(time_points, 0, energy_prices, alpha=0.3, color='blue')
    ax2.set_xlabel('Hour of Day')
    ax2.set_ylabel('Price ($/kWh)')
    ax2.set_title('Energy Market Prices')
    ax2.grid(True, alpha=0.3)
    
    # 3. Battery Storage Levels
    battery_charge = np.zeros_like(time_points)
    battery_charge[0] = 2.5  # Start at 50% capacity
    
    for i in range(1, len(time_points)):
        # Simple battery logic: charge when supply > demand, discharge when demand > supply
        if total_supply[i] > peak_demand[i]:
            # Charge battery
            charge_rate = min(1.0, (total_supply[i] - peak_demand[i]) * 0.5)
            battery_charge[i] = min(5.0, battery_charge[i-1] + charge_rate * 0.5)
        else:
            # Discharge battery
            discharge_rate = min(1.0, (peak_demand[i] - total_supply[i]) * 0.5)
            battery_charge[i] = max(0.0, battery_charge[i-1] - discharge_rate * 0.5)
    
    ax3.plot(time_points, battery_charge, 'purple', linewidth=2)
    ax3.fill_between(time_points, 0, battery_charge, alpha=0.3, color='purple')
    ax3.set_xlabel('Hour of Day')
    ax3.set_ylabel('Battery Level (MWh)')
    ax3.set_title('Battery Storage Levels')
    ax3.grid(True, alpha=0.3)
    
    # 4. Grid Stability Score
    stability_score = np.ones_like(time_points)
    for i in range(len(time_points)):
        supply_demand_ratio = total_supply[i] / (peak_demand[i] + 0.1)  # Avoid division by zero
        if 0.9 <= supply_demand_ratio <= 1.1:
            stability_score[i] = 1.0
        elif 0.8 <= supply_demand_ratio <= 1.2:
            stability_score[i] = 0.8
        else:
            stability_score[i] = 0.6
    
    ax4.plot(time_points, stability_score, 'orange', linewidth=2)
    ax4.fill_between(time_points, 0, stability_score, alpha=0.3, color='orange')
    ax4.set_xlabel('Hour of Day')
    ax4.set_ylabel('Stability Score')
    ax4.set_title('Grid Stability Score')
    ax4.set_ylim(0, 1.1)
    ax4.grid(True, alpha=0.3)
    
    # Add stability zones
    ax4.axhspan(0.8, 1.0, alpha=0.2, color='green', label='Stable')
    ax4.axhspan(0.6, 0.8, alpha=0.2, color='yellow', label='Warning')
    ax4.axhspan(0.0, 0.6, alpha=0.2, color='red', label='Critical')
    ax4.legend()
    
    plt.tight_layout()
    return fig


def create_agent_activity_chart():
    """Create a chart showing agent activity over time"""
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Sample agent activity data
    agents = ['Forecasting', 'Producer', 'Consumer', 'Market', 'Grid']
    activity_levels = [0.9, 0.7, 0.8, 0.6, 0.5]  # Relative activity levels
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    bars = ax.bar(agents, activity_levels, color=colors, alpha=0.8)
    
    # Add value labels on bars
    for bar, level in zip(bars, activity_levels):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{level:.1f}', ha='center', va='bottom', fontweight='bold')
    
    ax.set_ylabel('Activity Level')
    ax.set_title('🤖 Agent Activity Levels')
    ax.set_ylim(0, 1.0)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add activity descriptions
    descriptions = [
        'Generating forecasts',
        'Managing solar production',
        'Optimizing consumption',
        'Clearing market orders',
        'Monitoring grid stability'
    ]
    
    for i, (agent, desc) in enumerate(zip(agents, descriptions)):
        ax.text(i, -0.1, desc, ha='center', va='top', fontsize=9, 
                style='italic', color='gray')
    
    plt.tight_layout()
    return fig


def main():
    """Main visualization function"""
    print("📊 Creating Energy Trading System Visualizations...")
    
    try:
        # Create main system visualization
        fig1 = create_demo_visualization()
        fig1.savefig('energy_trading_system.png', dpi=300, bbox_inches='tight')
        print("✅ Saved: energy_trading_system.png")
        
        # Create agent activity chart
        fig2 = create_agent_activity_chart()
        fig2.savefig('agent_activity.png', dpi=300, bbox_inches='tight')
        print("✅ Saved: agent_activity.png")
        
        # Show the plots
        plt.show()
        
        print("\n🎉 Visualizations created successfully!")
        print("   - energy_trading_system.png: System overview")
        print("   - agent_activity.png: Agent activity levels")
        
    except Exception as e:
        print(f"❌ Error creating visualizations: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
