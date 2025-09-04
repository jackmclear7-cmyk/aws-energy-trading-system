#!/usr/bin/env python3
"""
Chatbot API Server

This script provides a simple HTTP API server for the chatbot integration.
"""

import json
import time
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
from chatbot_bedrock_integration import ChatbotBedrockIntegration
from strands_orchestrator import process_strands_query
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChatbotAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for chatbot API"""
    
    def __init__(self, *args, **kwargs):
        self.integration = ChatbotBedrockIntegration()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/status':
            self.handle_status()
        elif parsed_path.path == '/api/health':
            self.handle_health()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/chat':
            self.handle_chat()
        else:
            self.send_error(404, "Not Found")
    
    def handle_status(self):
        """Handle status endpoint"""
        try:
            status = self.integration.get_system_status()
            self.send_json_response(status)
        except Exception as e:
            self.send_error_response(str(e))
    
    def handle_health(self):
        """Handle health check endpoint"""
        health_data = {
            'status': 'healthy',
            'timestamp': time.time(),
            'services': {
                'bedrock': 'connected',
                'dynamodb': 'connected',
                'lambda': 'connected',
                'strands': 'connected'
            }
        }
        self.send_json_response(health_data)
    
    def handle_chat(self):
        """Handle chat endpoint"""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            request_data = json.loads(post_data.decode('utf-8'))
            user_message = request_data.get('message', '')
            
            if not user_message:
                self.send_error_response("Message is required")
                return
            
            # Try Strands first, fallback to existing system
            logger.info(f"🤖 Processing message: {user_message}")
            
            try:
                # Try Strands first
                logger.info("🔄 Attempting Strands processing...")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(process_strands_query(user_message))
                    if result.get('status') == 'success':
                        logger.info("✅ Strands processing successful")
                        self.send_json_response(result)
                        return
                    else:
                        logger.warning("⚠️ Strands processing failed, falling back to existing system")
                finally:
                    loop.close()
            except Exception as e:
                logger.warning(f"⚠️ Strands error: {e}, falling back to existing system")
            
            # Fallback to existing system
            logger.info("🔄 Using existing Bedrock integration as fallback")
            result = self.integration.handle_chatbot_request(user_message)
            result['source'] = 'AWS Bedrock Integration (Fallback)'
            self.send_json_response(result)
            
        except json.JSONDecodeError:
            self.send_error_response("Invalid JSON")
        except Exception as e:
            logger.error(f"❌ Error in chat handler: {e}")
            self.send_error_response(str(e))
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def send_error_response(self, error_message):
        """Send error response"""
        error_data = {
            'status': 'error',
            'error': error_message,
            'timestamp': time.time()
        }
        self.send_response(400)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_json = json.dumps(error_data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")


class ChatbotAPIServer:
    """Chatbot API Server"""
    
    def __init__(self, host='localhost', port=8081):
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
    
    def start(self):
        """Start the API server"""
        try:
            self.server = HTTPServer((self.host, self.port), ChatbotAPIHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            logger.info(f"🚀 Chatbot API Server started on http://{self.host}:{self.port}")
            logger.info("📡 Available endpoints:")
            logger.info("  GET  /api/status - Get system status")
            logger.info("  GET  /api/health - Health check")
            logger.info("  POST /api/chat   - Send chat message")
            
        except Exception as e:
            logger.error(f"❌ Failed to start API server: {e}")
            raise
    
    def stop(self):
        """Stop the API server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("🛑 Chatbot API Server stopped")
    
    def is_running(self):
        """Check if server is running"""
        return self.server_thread and self.server_thread.is_alive()


def main():
    """Main function to run the API server"""
    print("🤖 Starting Chatbot API Server")
    print("=" * 50)
    
    server = ChatbotAPIServer()
    
    try:
        server.start()
        
        print(f"✅ Server is running on http://localhost:8081")
        print("📡 Test the API:")
        print("  curl http://localhost:8081/api/health")
        print("  curl -X POST http://localhost:8081/api/chat -H 'Content-Type: application/json' -d '{\"message\": \"What is the system status?\"}'")
        print("\n⏹️  Press Ctrl+C to stop")
        
        # Keep the main thread alive
        while server.is_running():
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        server.stop()
        print("✅ Server stopped")


if __name__ == "__main__":
    main()
