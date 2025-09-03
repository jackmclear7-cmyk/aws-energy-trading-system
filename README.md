# Multi-Agent Energy Trading and Grid Optimization System ⚡️

A demonstration of AWS Bedrock Agents, A2A (Agent-to-Agent) communication, and MCP (Model Context Protocol) integration for decentralized energy market simulation.

## 🎯 Demo Overview

This system simulates a decentralized energy market where AI agents autonomously trade energy, forecast supply and demand, and optimize grid stability. It showcases real-time collaboration between specialized agents representing different stakeholders in the energy ecosystem.

## 🏗️ Architecture

### Core Components
- **Forecasting Agent**: Predicts energy supply and demand using ML models
- **Producer Agent**: Solar farm that decides when and at what price to sell energy
- **Consumer Agent**: Factory with battery storage that optimizes energy purchases
- **Grid Optimization Agent**: Monitors and maintains grid stability
- **Market Supervisor Agent**: Central orchestrator that facilitates trades

### AWS Services
- **Amazon Bedrock Agents**: Agent orchestration and management
- **Amazon Timestream**: Time-series data storage for energy metrics
- **AWS Lambda**: Tool implementations for external API calls
- **Amazon SageMaker**: ML model hosting for forecasting
- **Amazon QuickSight**: Real-time dashboard visualization
- **Amazon S3**: Data lake for historical and real-time data

### Protocols
- **A2A (Agent-to-Agent)**: Inter-agent communication layer
- **MCP (Model Context Protocol)**: External service integration

## 🎬 Working Demo (No AWS Required!)

**Try it now!** The system includes a fully functional demo that works without AWS credentials:

```bash
# Run the quick start script
./quick_start.sh

# Or run the simple demo directly
python scripts/demo_simple.py
```

This demo showcases:
- ✅ **Agent Creation & Lifecycle**: All 5 agent types starting and stopping
- ✅ **A2A Communication**: Real-time message passing between agents
- ✅ **Energy Trading**: Buy/sell orders, market clearing, trade execution
- ✅ **Grid Monitoring**: Stability monitoring and status updates
- ✅ **Live Status Dashboard**: Real-time agent activity and message counts

## 🚀 Full AWS Deployment

### Prerequisites
- AWS CLI configured with appropriate permissions
- Python 3.9+
- Node.js 18+ (for some Lambda functions)
- Docker (for local development)

### Installation

1. **Clone and setup the project:**
```bash
git clone <repository-url>
cd aws-agents-energy-demo
```

2. **Install dependencies:**
```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
npm install
```

3. **Deploy infrastructure:**
```bash
# Deploy AWS resources
python scripts/deploy_infrastructure.py

# Deploy agents
python scripts/deploy_agents.py
```

4. **Start the simulation:**
```bash
python scripts/run_simulation.py
```

5. **View the dashboard:**
```bash
# Open QuickSight dashboard URL from deployment output
```

## 📁 Project Structure

```
├── agents/                 # Agent implementations
│   ├── forecasting/        # Forecasting agent
│   ├── producer/          # Producer agent (solar farm)
│   ├── consumer/          # Consumer agent (factory)
│   ├── grid_optimization/ # Grid optimization agent
│   └── market_supervisor/ # Market supervisor agent
├── infrastructure/         # Infrastructure as code
│   ├── cdk/              # CDK stacks
│   └── terraform/        # Terraform configurations
├── lambda/                # Lambda function implementations
├── data/                  # Sample data and schemas
├── scripts/               # Deployment and utility scripts
├── tests/                 # Test suite
└── docs/                  # Documentation
```

## 🔧 Configuration

### Environment Variables
```bash
export AWS_REGION=us-east-1
export BEDROCK_AGENT_ID=<your-agent-id>
export TIMESTREAM_DATABASE=<database-name>
export SAGEMAKER_ENDPOINT=<endpoint-name>
```

### Agent Configuration
Each agent can be configured via JSON files in the `config/` directory. Key settings include:
- Trading parameters (min/max prices, quantities)
- Forecasting horizons
- Grid stability thresholds
- Communication protocols

## 📊 Dashboard

The QuickSight dashboard provides real-time visualization of:
- Energy prices and trading activity
- Supply and demand curves
- Grid stability metrics
- Agent performance and decision logs
- Historical trends and patterns

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/unit/
```

### Integration Tests
```bash
python -m pytest tests/integration/
```

### Load Testing
```bash
python scripts/load_test.py --agents 10 --duration 3600
```

## 📈 Monitoring and Logging

- **CloudWatch Logs**: Agent activity and decision logs
- **CloudWatch Metrics**: Performance and trading metrics
- **X-Ray**: Distributed tracing for agent interactions
- **CloudTrail**: API call auditing

## 🔒 Security

- IAM roles with least privilege access
- VPC isolation for sensitive components
- Encryption at rest and in transit
- API Gateway rate limiting
- WAF protection for web interfaces

## 🚨 Troubleshooting

### Common Issues
1. **Agent communication failures**: Check A2A configuration and IAM permissions
2. **MCP tool errors**: Verify Lambda function permissions and API endpoints
3. **Data ingestion issues**: Check Timestream permissions and data format
4. **Performance problems**: Monitor CloudWatch metrics and adjust agent parameters

### Debug Mode
Enable debug logging by setting the `DEBUG` environment variable:
```bash
export DEBUG=true
python scripts/run_simulation.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:
- Create a GitHub issue
- Check the [documentation](docs/)
- Review [troubleshooting guide](docs/troubleshooting.md)

## 🔮 Future Enhancements

- Integration with real energy trading platforms
- Advanced ML models for price prediction
- Blockchain-based smart contracts
- IoT device integration for real-time monitoring
- Multi-region deployment for global energy markets
