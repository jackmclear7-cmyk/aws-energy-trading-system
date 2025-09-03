// Energy Trading System Dashboard JavaScript

class EnergyTradingDashboard {
    constructor() {
        this.workflowData = null;
        this.eventsData = null;
        this.isAnimating = false;
        this.init();
    }

    async init() {
        console.log('🚀 Initializing Energy Trading Dashboard');
        
        // Load data
        await this.loadData();
        
        // Initialize dashboard
        this.initializeWorkflow();
        this.initializeMetrics();
        this.initializeEvents();
        
        // Start real-time updates
        this.startRealTimeUpdates();
        
        console.log('✅ Dashboard initialized successfully');
    }

    async loadData() {
        try {
            // Load workflow data
            const workflowResponse = await fetch('../workflow_results.json');
            this.workflowData = await workflowResponse.json();
            
            // Load events data
            const eventsResponse = await fetch('../real_time_events.json');
            this.eventsData = await eventsResponse.json();
            
            console.log('📊 Data loaded successfully');
        } catch (error) {
            console.error('❌ Error loading data:', error);
            // Use mock data if files don't exist
            this.workflowData = this.getMockWorkflowData();
            this.eventsData = this.getMockEventsData();
        }
    }

    initializeWorkflow() {
        console.log('🔄 Initializing workflow visualization');
        
        const workflowContainer = document.querySelector('.workflow-container');
        if (!workflowContainer) return;

        // Animate workflow steps
        this.workflowData.forEach((step, index) => {
            setTimeout(() => {
                this.animateWorkflowStep(step, index);
            }, index * 500);
        });
    }

    animateWorkflowStep(step, index) {
        const stepElement = document.querySelector(`[data-step="${step.step}"]`);
        if (!stepElement) return;

        // Add animation class
        stepElement.classList.add('animate-in');
        
        // Update step content with real data
        const stepContent = stepElement.querySelector('.step-content');
        if (stepContent) {
            const title = stepContent.querySelector('h3');
            const description = stepContent.querySelector('p');
            const duration = stepContent.querySelector('.duration');
            
            if (title) title.textContent = this.getStepTitle(step.agent, step.action);
            if (description) description.textContent = this.getStepDescription(step.agent, step.action);
            if (duration) duration.textContent = `${step.duration}s`;
        }

        // Add completion effect
        setTimeout(() => {
            stepElement.classList.add('completed');
        }, 1000);
    }

    getStepTitle(agent, action) {
        const titles = {
            'forecasting-agent': {
                'weather_demand_forecast': 'Weather & Demand Forecast'
            },
            'producer-agent': {
                'production_optimization': 'Solar Production Optimization'
            },
            'consumer-agent': {
                'consumption_optimization': 'Consumer Energy Optimization'
            },
            'market-supervisor-agent': {
                'trade_execution': 'Market Trade Execution'
            },
            'grid-optimization-agent': {
                'grid_monitoring': 'Grid Stability Monitoring'
            }
        };
        
        return titles[agent]?.[action] || 'Processing';
    }

    getStepDescription(agent, action) {
        const descriptions = {
            'forecasting-agent': {
                'weather_demand_forecast': 'Analyzing weather patterns and energy demand forecasts'
            },
            'producer-agent': {
                'production_optimization': 'Optimizing solar farm output and battery usage'
            },
            'consumer-agent': {
                'consumption_optimization': 'Optimizing factory energy consumption and costs'
            },
            'market-supervisor-agent': {
                'trade_execution': 'Matching orders and executing energy trades'
            },
            'grid-optimization-agent': {
                'grid_monitoring': 'Monitoring grid health and stability metrics'
            }
        };
        
        return descriptions[agent]?.[action] || 'Processing request';
    }

    initializeMetrics() {
        console.log('📊 Initializing metrics visualization');
        
        // Animate metrics with real data
        if (this.workflowData && this.workflowData.length > 0) {
            this.updateMetricsWithData();
        }
        
        // Add hover effects
        const metricCards = document.querySelectorAll('.metric-card');
        metricCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-4px) scale(1.02)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
            });
        });
    }

    updateMetricsWithData() {
        // Update metrics with real data from workflow
        const forecastStep = this.workflowData.find(step => step.agent === 'forecasting-agent');
        const producerStep = this.workflowData.find(step => step.agent === 'producer-agent');
        const marketStep = this.workflowData.find(step => step.agent === 'market-supervisor-agent');
        
        if (forecastStep && forecastStep.data) {
            // Update solar generation
            const solarMetric = document.querySelector('.metric-card:nth-child(1) .metric-value');
            if (solarMetric && forecastStep.data.solar_production) {
                solarMetric.textContent = `${forecastStep.data.solar_production.expected_generation} MW`;
            }
            
            // Update grid demand
            const demandMetric = document.querySelector('.metric-card:nth-child(2) .metric-value');
            if (demandMetric && forecastStep.data.demand_forecast) {
                demandMetric.textContent = `${forecastStep.data.demand_forecast.peak_demand.toLocaleString()} MW`;
            }
        }
        
        if (marketStep && marketStep.data) {
            // Update market price
            const priceMetric = document.querySelector('.metric-card:nth-child(3) .metric-value');
            if (priceMetric && marketStep.data.price_discovery) {
                priceMetric.textContent = `$${marketStep.data.price_discovery.market_clearing_price}/kWh`;
            }
        }
    }

    initializeEvents() {
        console.log('📈 Initializing events timeline');
        
        const eventTimeline = document.getElementById('eventTimeline');
        if (!eventTimeline) return;

        // Clear existing events
        eventTimeline.innerHTML = '';

        // Add events with animation
        this.eventsData.forEach((event, index) => {
            setTimeout(() => {
                this.addEventToTimeline(event);
            }, index * 100);
        });
    }

    addEventToTimeline(event) {
        const eventTimeline = document.getElementById('eventTimeline');
        if (!eventTimeline) return;

        const eventElement = document.createElement('div');
        eventElement.className = 'event-item';
        eventElement.innerHTML = `
            <div class="event-icon ${event.severity}">
                <i class="fas ${this.getEventIcon(event.type)}"></i>
            </div>
            <div class="event-content">
                <div class="event-message">${event.message}</div>
                <div class="event-time">${this.formatTime(event.timestamp)}</div>
            </div>
        `;

        // Add animation
        eventElement.style.opacity = '0';
        eventElement.style.transform = 'translateX(-20px)';
        
        eventTimeline.appendChild(eventElement);
        
        // Animate in
        setTimeout(() => {
            eventElement.style.transition = 'all 0.3s ease';
            eventElement.style.opacity = '1';
            eventElement.style.transform = 'translateX(0)';
        }, 50);

        // Keep only last 10 events
        const events = eventTimeline.querySelectorAll('.event-item');
        if (events.length > 10) {
            events[0].remove();
        }
    }

    getEventIcon(eventType) {
        const icons = {
            'trade_executed': 'fa-exchange-alt',
            'price_updated': 'fa-dollar-sign',
            'demand_response_triggered': 'fa-bolt',
            'battery_charged': 'fa-battery-full',
            'battery_discharged': 'fa-battery-quarter',
            'grid_alert': 'fa-exclamation-triangle',
            'weather_update': 'fa-cloud-sun',
            'market_clearing': 'fa-chart-line'
        };
        
        return icons[eventType] || 'fa-info-circle';
    }

    formatTime(timestamp) {
        const date = new Date(timestamp * 1000);
        return date.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        });
    }

    startRealTimeUpdates() {
        console.log('🔄 Starting real-time updates');
        
        // Update metrics every 5 seconds
        setInterval(() => {
            this.updateMetrics();
        }, 5000);
        
        // Add new events every 10 seconds
        setInterval(() => {
            this.addRandomEvent();
        }, 10000);
    }

    updateMetrics() {
        // Simulate real-time metric updates
        const metricValues = document.querySelectorAll('.metric-value');
        metricValues.forEach(metric => {
            const currentValue = metric.textContent;
            const value = parseFloat(currentValue.replace(/[^\d.]/g, ''));
            
            if (!isNaN(value)) {
                const change = (Math.random() - 0.5) * 0.1; // ±5% change
                const newValue = value * (1 + change);
                metric.textContent = currentValue.replace(value.toString(), newValue.toFixed(1));
            }
        });
    }

    addRandomEvent() {
        const eventTypes = [
            'trade_executed',
            'price_updated',
            'demand_response_triggered',
            'battery_charged',
            'battery_discharged',
            'grid_alert',
            'weather_update',
            'market_clearing'
        ];
        
        const agents = [
            'producer-agent',
            'consumer-agent',
            'market-supervisor-agent',
            'grid-optimization-agent'
        ];
        
        const severities = ['info', 'success', 'warning', 'error'];
        
        const newEvent = {
            id: `event_${Date.now()}`,
            timestamp: Date.now() / 1000,
            type: eventTypes[Math.floor(Math.random() * eventTypes.length)],
            agent: agents[Math.floor(Math.random() * agents.length)],
            message: `Real-time update: ${eventTypes[Math.floor(Math.random() * eventTypes.length)].replace('_', ' ')}`,
            severity: severities[Math.floor(Math.random() * severities.length)],
            data: {
                value: Math.random() * 1000,
                unit: 'MW',
                change: (Math.random() - 0.5) * 0.2
            }
        };
        
        this.addEventToTimeline(newEvent);
    }

    getMockWorkflowData() {
        return [
            {
                step: 1,
                agent: 'forecasting-agent',
                action: 'weather_demand_forecast',
                status: 'success',
                timestamp: Date.now() / 1000 - 300,
                duration: 2.3
            },
            {
                step: 2,
                agent: 'producer-agent',
                action: 'production_optimization',
                status: 'success',
                timestamp: Date.now() / 1000 - 250,
                duration: 1.8
            },
            {
                step: 3,
                agent: 'consumer-agent',
                action: 'consumption_optimization',
                status: 'success',
                timestamp: Date.now() / 1000 - 200,
                duration: 2.1
            },
            {
                step: 4,
                agent: 'market-supervisor-agent',
                action: 'trade_execution',
                status: 'success',
                timestamp: Date.now() / 1000 - 150,
                duration: 1.5
            },
            {
                step: 5,
                agent: 'grid-optimization-agent',
                action: 'grid_monitoring',
                status: 'success',
                timestamp: Date.now() / 1000 - 100,
                duration: 1.2
            }
        ];
    }

    getMockEventsData() {
        const events = [];
        const now = Date.now() / 1000;
        
        for (let i = 0; i < 10; i++) {
            events.push({
                id: `event_${i}`,
                timestamp: now - (i * 300),
                type: 'trade_executed',
                agent: 'market-supervisor-agent',
                message: `Trade executed: ${Math.random() * 100} MW at $${(Math.random() * 0.1 + 0.05).toFixed(3)}/kWh`,
                severity: 'success',
                data: {
                    value: Math.random() * 100,
                    unit: 'MW',
                    change: Math.random() * 0.1
                }
            });
        }
        
        return events;
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new EnergyTradingDashboard();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    .workflow-step.animate-in {
        animation: slideInFromLeft 0.6s ease-out;
    }
    
    .workflow-step.completed {
        border-left-color: #22c55e;
    }
    
    .workflow-step.completed .step-icon {
        background: linear-gradient(135deg, #22c55e, #16a34a);
    }
    
    @keyframes slideInFromLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .metric-card {
        transition: all 0.3s ease;
    }
    
    .agent-card {
        transition: all 0.3s ease;
    }
    
    .event-item {
        transition: all 0.3s ease;
    }
`;
document.head.appendChild(style);
