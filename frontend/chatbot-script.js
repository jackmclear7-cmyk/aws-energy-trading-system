// Energy Trading Chatbot JavaScript

class EnergyTradingChatbot {
    constructor() {
        this.isOpen = false;
        this.isMinimized = false;
        this.messages = [];
        this.currentUser = 'User';
        this.init();
    }

    init() {
        console.log('🤖 Initializing Energy Trading Chatbot');
        
        // Initialize event listeners
        this.setupEventListeners();
        
        // Add welcome message
        this.addWelcomeMessage();
        
        console.log('✅ Chatbot initialized successfully');
    }

    setupEventListeners() {
        // Floating chat button
        const floatingBtn = document.getElementById('floatingChatBtn');
        floatingBtn.addEventListener('click', () => this.toggleChat());

        // Chat controls
        const minimizeBtn = document.getElementById('minimizeBtn');
        const closeBtn = document.getElementById('closeBtn');
        
        minimizeBtn.addEventListener('click', () => this.minimizeChat());
        closeBtn.addEventListener('click', () => this.closeChat());

        // Message input
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        sendBtn.addEventListener('click', () => this.sendMessage());

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
        voiceBtn.addEventListener('click', () => this.toggleVoiceInput());
    }

    toggleChat() {
        const chatbot = document.querySelector('.chatbot-container');
        
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }

    openChat() {
        const chatbot = document.querySelector('.chatbot-container');
        const floatingBtn = document.getElementById('floatingChatBtn');
        
        chatbot.classList.add('show');
        floatingBtn.style.display = 'none';
        this.isOpen = true;
        
        // Focus on input
        setTimeout(() => {
            document.getElementById('messageInput').focus();
        }, 300);
    }

    closeChat() {
        const chatbot = document.querySelector('.chatbot-container');
        const floatingBtn = document.getElementById('floatingChatBtn');
        
        chatbot.classList.remove('show');
        floatingBtn.style.display = 'flex';
        this.isOpen = false;
        this.isMinimized = false;
    }

    minimizeChat() {
        const chatbot = document.querySelector('.chatbot-container');
        
        if (this.isMinimized) {
            chatbot.classList.remove('minimized');
            this.isMinimized = false;
        } else {
            chatbot.classList.add('minimized');
            this.isMinimized = true;
        }
    }

    addWelcomeMessage() {
        // Welcome message is already in HTML
        this.messages.push({
            type: 'bot',
            text: 'Hello! I\'m your Energy Trading Assistant. I can help you with system status, weather forecasts, market analysis, and more. What would you like to know?',
            timestamp: new Date()
        });
    }

    sendMessage() {
        const messageInput = document.getElementById('messageInput');
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
        const response = this.getBotResponse(userMessage);
        this.addMessage('bot', response);
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
            if (Math.random() < 0.1) { // 10% chance every interval
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

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const chatbot = new EnergyTradingChatbot();
    
    // Start real-time updates
    chatbot.startRealTimeUpdates();
    
    // Make chatbot globally accessible for debugging
    window.energyTradingChatbot = chatbot;
});

// Add some CSS animations
const style = document.createElement('style');
style.textContent = `
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
document.head.appendChild(style);
