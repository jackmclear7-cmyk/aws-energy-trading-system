// Energy Trading Chatbot Integration

class EnergyTradingChatbotIntegration {
    constructor() {
        this.isOpen = false;
        this.isMinimized = false;
        this.messages = [];
        this.currentUser = 'User';
        this.dashboard = null;
        this.init();
    }

    init() {
        console.log('🤖 Initializing Energy Trading Chatbot Integration');
        
        // Wait for dashboard to be ready
        this.waitForDashboard();
        
        // Initialize chatbot
        this.setupEventListeners();
        this.addWelcomeMessage();
        
        console.log('✅ Chatbot integration initialized successfully');
    }

    waitForDashboard() {
        // Wait for the main dashboard to be ready
        if (window.energyTradingDashboard) {
            this.dashboard = window.energyTradingDashboard;
            this.setupDashboardIntegration();
        } else {
            setTimeout(() => this.waitForDashboard(), 100);
        }
    }

    setupDashboardIntegration() {
        // Integrate with the main dashboard
        this.dashboard.onMetricUpdate = (metric, value) => {
            this.handleMetricUpdate(metric, value);
        };
        
        this.dashboard.onWorkflowStepComplete = (step, data) => {
            this.handleWorkflowUpdate(step, data);
        };
        
        this.dashboard.onAgentStatusChange = (agent, status) => {
            this.handleAgentStatusChange(agent, status);
        };
    }

    setupEventListeners() {
        // Floating chat button
        const floatingBtn = document.getElementById('floatingChatBtn');
        console.log('🔍 Looking for floating chat button:', floatingBtn);
        if (floatingBtn) {
            console.log('✅ Found floating chat button, adding event listener');
            floatingBtn.addEventListener('click', () => {
                console.log('🖱️ Chat button clicked!');
                this.toggleChat();
            });
        } else {
            console.error('❌ Floating chat button not found!');
        }

        // Chat controls
        const minimizeBtn = document.getElementById('minimizeBtn');
        const closeBtn = document.getElementById('closeBtn');
        
        if (minimizeBtn) {
            minimizeBtn.addEventListener('click', () => this.minimizeChat());
        }
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeChat());
        }

        // Message input
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        
        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
        }
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }

        // Quick action buttons
        const quickActionBtns = document.querySelectorAll('.quick-action-btn');
        quickActionBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const query = btn.getAttribute('data-query');
                this.sendQuickMessage(query);
            });
        });

        // Voice input (placeholder)
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => this.toggleVoiceInput());
        }
    }

    toggleChat() {
        console.log('🔄 Toggling chat, current state:', this.isOpen);
        const chatbot = document.getElementById('chatbotContainer');
        const floatingBtn = document.getElementById('floatingChatBtn');
        
        console.log('🔍 Chatbot container:', chatbot);
        console.log('🔍 Floating button:', floatingBtn);
        
        if (this.isOpen) {
            console.log('📤 Closing chat');
            this.closeChat();
        } else {
            console.log('📥 Opening chat');
            this.openChat();
        }
    }

    openChat() {
        console.log('📥 Opening chat...');
        const chatbot = document.getElementById('chatbotContainer');
        const floatingBtn = document.getElementById('floatingChatBtn');
        
        console.log('🔍 Chatbot container found:', chatbot);
        console.log('🔍 Floating button found:', floatingBtn);
        
        if (chatbot) {
            console.log('✅ Adding show class to chatbot');
            chatbot.classList.add('show');
            this.isOpen = true;
            console.log('✅ Chat is now open');
        } else {
            console.error('❌ Chatbot container not found!');
        }
        
        if (floatingBtn) {
            console.log('✅ Hiding floating button');
            floatingBtn.style.display = 'none';
        }
        
        // Focus on input
        setTimeout(() => {
            const messageInput = document.getElementById('messageInput');
            if (messageInput) {
                console.log('🎯 Focusing on input');
                messageInput.focus();
            } else {
                console.error('❌ Message input not found!');
            }
        }, 300);
    }

    closeChat() {
        const chatbot = document.getElementById('chatbotContainer');
        const floatingBtn = document.getElementById('floatingChatBtn');
        
        if (chatbot) {
            chatbot.classList.remove('show');
            this.isOpen = false;
            this.isMinimized = false;
        }
        
        if (floatingBtn) {
            floatingBtn.style.display = 'flex';
        }
    }

    minimizeChat() {
        const chatbot = document.getElementById('chatbotContainer');
        
        if (chatbot) {
            if (this.isMinimized) {
                chatbot.classList.remove('minimized');
                this.isMinimized = false;
            } else {
                chatbot.classList.add('minimized');
                this.isMinimized = true;
            }
        }
    }

    addWelcomeMessage() {
        // Welcome message is already in HTML, but we can add it to our messages array
        this.messages.push({
            type: 'bot',
            text: 'Hello! I\'m your Energy Trading Assistant. I can help you with system status, weather forecasts, market analysis, and more. What would you like to know?',
            timestamp: new Date()
        });
    }

    sendMessage() {
        const messageInput = document.getElementById('messageInput');
        if (!messageInput) return;
        
        const message = messageInput.value.trim();
        
        if (message) {
            this.addMessage('user', message);
            messageInput.value = '';
            
            // Show typing indicator
            this.showTypingIndicator();
            
            // Simulate bot response
            setTimeout(() => {
                this.hideTypingIndicator();
                this.generateBotResponse(message);
            }, 1500);
        }
    }

    sendQuickMessage(query) {
        this.addMessage('user', query);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Simulate bot response
        setTimeout(() => {
            this.hideTypingIndicator();
            this.generateBotResponse(query);
        }, 1000);
    }

    addMessage(type, text) {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const avatar = type === 'bot' ? 'fas fa-robot' : 'fas fa-user';
        const time = new Date().toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="${avatar}"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${text}</div>
                <div class="message-time">${time}</div>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Store message
        this.messages.push({
            type: type,
            text: text,
            timestamp: new Date()
        });
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="message-text">
                    <div class="typing-dots">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    generateBotResponse(userMessage) {
        console.log('🤖 Generating bot response for:', userMessage);
        // Try to get response from API first
        this.getAPIResponse(userMessage).then(response => {
            console.log('📨 API Response received:', response);
            if (response && response.status === 'success') {
                console.log('✅ Using API response');
                this.addMessage('bot', response.response);
                this.triggerDashboardInteraction(userMessage, response.response);
            } else {
                console.log('⚠️ API response failed, using fallback');
                // Fallback to local response
                const localResponse = this.getBotResponse(userMessage);
                this.addMessage('bot', localResponse);
                this.triggerDashboardInteraction(userMessage, localResponse);
            }
        }).catch(error => {
            console.error('❌ Error getting API response:', error);
            // Fallback to local response
            const localResponse = this.getBotResponse(userMessage);
            this.addMessage('bot', localResponse);
            this.triggerDashboardInteraction(userMessage, localResponse);
        });
    }

        async getAPIResponse(userMessage) {
        try {
            console.log('🌐 Calling API for message:', userMessage);
            const response = await fetch('http://localhost:8081/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage
                })
            });

            console.log('📡 API Response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('✅ API Response data:', data);
            return data;
        } catch (error) {
            console.error('❌ API request failed:', error);
            return null;
        }
    }

    triggerDashboardInteraction(userMessage, response) {
        const lowerMessage = userMessage.toLowerCase();
        
        // Highlight relevant dashboard elements based on user query
        if (lowerMessage.includes('status') || lowerMessage.includes('system')) {
            this.highlightDashboardElements(['metrics', 'agents']);
        } else if (lowerMessage.includes('weather') || lowerMessage.includes('forecast')) {
            this.highlightDashboardElements(['workflow-step-1']);
        } else if (lowerMessage.includes('price') || lowerMessage.includes('market')) {
            this.highlightDashboardElements(['workflow-step-4', 'metric-price']);
        } else if (lowerMessage.includes('battery') || lowerMessage.includes('storage')) {
            this.highlightDashboardElements(['metric-battery']);
        } else if (lowerMessage.includes('grid') || lowerMessage.includes('stability')) {
            this.highlightDashboardElements(['workflow-step-5', 'agents']);
        }
    }

    highlightDashboardElements(elementIds) {
        // Remove previous highlights
        document.querySelectorAll('.dashboard-highlight').forEach(el => {
            el.classList.remove('dashboard-highlight');
        });
        
        // Add highlights to new elements
        elementIds.forEach(id => {
            const element = document.getElementById(id) || document.querySelector(`[data-step="${id.replace('workflow-step-', '')}"]`);
            if (element) {
                element.classList.add('dashboard-highlight');
                
                // Remove highlight after 3 seconds
                setTimeout(() => {
                    element.classList.remove('dashboard-highlight');
                }, 3000);
            }
        });
    }

    getBotResponse(message) {
        const lowerMessage = message.toLowerCase();
        
        // System status queries
        if (lowerMessage.includes('status') || lowerMessage.includes('system')) {
            return `🤖 **System Status Report:**
            
🟢 **Overall Health: EXCELLENT**
• All 5 AI agents are active and healthy
• Grid stability: 99.8% (excellent)
• No alerts or issues detected

📊 **Current Performance:**
• Solar generation: 450 MW (up 12.5%)
• Grid demand: 1,250 MW (normal)
• Market price: $0.083/kWh (down 2.1%)
• Battery storage: 85% (optimal)

🔄 **Recent Activity:**
• 3 trades executed in the last hour
• All workflow steps completed successfully

Would you like me to show you more details about any specific area?`;
        }
        
        // Weather queries
        if (lowerMessage.includes('weather') || lowerMessage.includes('forecast')) {
            return `🌤️ **Weather Forecast Analysis:**
            
**Tomorrow's Conditions:**
• Temperature: 24°C (ideal for solar)
• Cloud cover: 15% (excellent conditions)
• Wind speed: 8 mph (minimal impact)
• Solar irradiance: 920 W/m² (high)

☀️ **Solar Production Impact:**
• Expected generation: 520 MW (+15% vs today)
• Peak hours: 6 hours (10 AM - 4 PM)
• Battery charging opportunity: High

💡 **Recommendation:**
Consider increasing direct sales to the grid during peak hours. The high solar irradiance suggests excellent production conditions.

Would you like me to adjust the production strategy based on this forecast?`;
        }
        
        // Market price queries
        if (lowerMessage.includes('price') || lowerMessage.includes('market')) {
            return `💰 **Market Analysis:**
            
📈 **Current Market Conditions:**
• Current price: $0.083/kWh
• Price trend: Declining (-2.1% today)
• Demand forecast: Peak at 2 PM (1,350 MW)
• Supply forecast: High solar generation expected

🎯 **Trading Recommendation:**
**WAIT** - I recommend holding your stored energy because:
• Peak demand is expected at 2 PM (in 3 hours)
• Prices typically rise 15-20% during peak hours
• Current storage: 150 MW available
• Potential profit: +$1,250 if you wait

⏰ **Optimal Timing:**
• Best sell time: 1:45 PM - 2:15 PM
• Expected peak price: $0.095-0.098/kWh
• Risk level: Low (high confidence forecast)

Would you like me to set up an automatic sell order for the optimal time?`;
        }
        
        // Battery queries
        if (lowerMessage.includes('battery') || lowerMessage.includes('storage')) {
            return `🔋 **Battery Storage Status:**
            
**Current Battery Status:**
• Charge level: 85% (optimal)
• Available capacity: 150 MW
• Efficiency: 92%
• Last charge: 2 hours ago

⚡ **Performance Metrics:**
• Charge cycles today: 3
• Total energy stored: 1,200 MWh
• Average charge time: 4.2 hours
• Discharge efficiency: 91.5%

🎯 **Optimization Strategy:**
• Charge during off-peak (11 PM - 6 AM)
• Discharge during peak (2 PM - 6 PM)
• Current strategy: Price-based optimization

💡 **Recommendation:**
Battery performance is excellent. Consider increasing storage capacity during the next off-peak period to maximize profit potential.

Would you like me to adjust the battery charging strategy?`;
        }
        
        // Grid stability queries
        if (lowerMessage.includes('grid') || lowerMessage.includes('stability')) {
            return `⚡ **Grid Stability Report:**
            
🟢 **Current Grid Status:**
• Frequency: 59.98 Hz (normal)
• Voltage: 1.02 p.u. (optimal)
• Power balance: +15 MW surplus
• Stability margin: 18% (excellent)

📊 **Grid Performance:**
• Uptime: 99.8% (excellent)
• Last outage: 15 days ago
• Response time: 2.3 minutes
• Demand response: Active

🔄 **Recent Activity:**
• 2 demand response events today
• All agents coordinating effectively
• No stability concerns

✅ **Status: All systems operating normally**

The grid is in excellent condition with no issues detected. All monitoring systems are functioning properly.

Would you like me to show you the detailed grid metrics?`;
        }
        
        // Help queries
        if (lowerMessage.includes('help') || lowerMessage.includes('what can you do')) {
            return `🤖 **I can help you with:**
            
📊 **System Monitoring:**
• Real-time system status and health
• Performance metrics and analytics
• Agent activity and coordination

🌤️ **Weather & Forecasting:**
• Weather forecasts and solar predictions
• Demand forecasting and analysis
• Production optimization recommendations

💰 **Market Analysis:**
• Current market prices and trends
• Trading recommendations and timing
• Profit optimization strategies

⚡ **Grid Management:**
• Grid stability monitoring
• Demand response coordination
• Emergency response protocols

🔋 **Battery Optimization:**
• Storage status and performance
• Charging/discharging strategies
• Efficiency optimization

📈 **Reports & Insights:**
• Performance analysis and trends
• Cost optimization opportunities
• Historical data and comparisons

Just ask me anything about your energy trading system!`;
        }
        
        // Default response
        return `🤖 I understand you're asking about "${message}". Let me help you with that.

I can provide information about:
• System status and performance
• Weather forecasts and solar predictions
• Market analysis and trading recommendations
• Grid stability and monitoring
• Battery optimization strategies
• Performance reports and insights

Could you be more specific about what you'd like to know? For example:
• "What's the current system status?"
• "Show me the weather forecast"
• "What's the market price?"
• "How are the batteries performing?"

I'm here to help optimize your energy trading operations!`;
    }

    // Dashboard integration methods
    handleMetricUpdate(metric, value) {
        // Handle real-time metric updates from dashboard
        console.log(`📊 Metric update: ${metric} = ${value}`);
        
        // Add system update message if chat is open
        if (this.isOpen && Math.random() < 0.3) { // 30% chance
            this.addSystemUpdate(`📊 ${metric} updated to ${value}`);
        }
    }

    handleWorkflowUpdate(step, data) {
        // Handle workflow step completion
        console.log(`🔄 Workflow step ${step} completed:`, data);
        
        // Add workflow update message if chat is open
        if (this.isOpen && Math.random() < 0.5) { // 50% chance
            this.addSystemUpdate(`🔄 Workflow step ${step} completed successfully`);
        }
    }

    handleAgentStatusChange(agent, status) {
        // Handle agent status changes
        console.log(`🤖 Agent ${agent} status: ${status}`);
        
        // Add agent update message if chat is open
        if (this.isOpen && status !== 'active') {
            this.addSystemUpdate(`🤖 ${agent} status changed to ${status}`);
        }
    }

    addSystemUpdate(message) {
        this.addMessage('bot', message);
    }

    toggleVoiceInput() {
        // Placeholder for voice input functionality
        console.log('🎤 Voice input toggled');
        
        // Show notification
        this.addMessage('bot', '🎤 Voice input is coming soon! For now, please type your message.');
    }

    // Utility methods
    formatTime(date) {
        return date.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    // Simulate real-time updates
    startRealTimeUpdates() {
        setInterval(() => {
            // Simulate occasional system updates
            if (Math.random() < 0.1 && this.isOpen) { // 10% chance every interval
                this.addSystemUpdate();
            }
        }, 30000); // Every 30 seconds
    }

    addSystemUpdate() {
        const updates = [
            "📊 System update: Solar generation increased to 465 MW",
            "💰 Market update: Price updated to $0.084/kWh",
            "🔋 Battery update: Storage level now at 87%",
            "⚡ Grid update: Stability maintained at 99.9%",
            "🔄 Trade update: New trade executed for 75 MW"
        ];
        
        const randomUpdate = updates[Math.floor(Math.random() * updates.length)];
        this.addMessage('bot', randomUpdate);
    }
}

// Initialize chatbot integration when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for the main dashboard to initialize
    setTimeout(() => {
        const chatbotIntegration = new EnergyTradingChatbotIntegration();
        
        // Start real-time updates
        chatbotIntegration.startRealTimeUpdates();
        
        // Make chatbot globally accessible for debugging
        window.energyTradingChatbotIntegration = chatbotIntegration;
    }, 1000);
});

// Add CSS for dashboard highlighting
const chatbotStyle = document.createElement('style');
chatbotStyle.textContent = `
    .dashboard-highlight {
        animation: highlightPulse 2s ease-in-out;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
    }
    
    @keyframes highlightPulse {
        0%, 100% {
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
        }
        50% {
            box-shadow: 0 0 30px rgba(102, 126, 234, 0.8);
        }
    }
    
    .message {
        animation: slideInMessage 0.3s ease;
    }
    
    @keyframes slideInMessage {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .quick-action-btn {
        animation: fadeInButton 0.3s ease;
    }
    
    @keyframes fadeInButton {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
`;
document.head.appendChild(chatbotStyle);
