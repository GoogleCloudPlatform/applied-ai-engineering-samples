# Chapter 12: Project Vastra - Mobile-First Multimodal AI Assistant (Vertex API)

This chapter implements the mobile-first multimodal assistant demonstrated in [Chapter 8 (Project Pastra)](../../part_2_dev_api/chapter_08/README.md), but using the Vertex AI API instead of the Development API. We call it "Project Vastra" to distinguish it from the Development API version.

**Key Differences from Chapter 8:**

1. **API Endpoint:** Uses the Vertex AI WebSocket endpoint through a proxy instead of the direct Development API endpoint
2. **Authentication:** Uses service account authentication through the proxy instead of an API key
3. **Model Path:** Uses the full Vertex AI model path format: `projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/gemini-2.0-flash-exp`
4. **Setup Configuration:** Includes additional Vertex AI-specific configuration parameters in the setup message
5. **⚠️ Complex Deployment Architecture:** Unlike Project Pastra which could be deployed as a single service, Project Vastra requires a more complex setup:
   - Main application service (Cloud Run)
   - WebSocket proxy service (separate Cloud Run instance)
   - Service account configuration
   - IAM role setup for service-to-service communication

6. **Deployment Complexity:**
   - Chapter 8 (Pastra) uses a simple nginx-based static file server
   - Chapter 12 (Vastra) requires a Python-based proxy server running alongside nginx
   - Additional environment variables for Vertex AI configuration
   - More complex service account and IAM setup

7. **Infrastructure Requirements:**
   - Chapter 8: Single Cloud Run service with API key
   - Chapter 12: Two Cloud Run services, service account, IAM roles
   - Additional networking setup for service-to-service communication
   - More complex monitoring and logging requirements

8. **Security Considerations:**
   - Chapter 8: Simple API key management
   - Chapter 12: Service account key management
   - IAM role configuration
   - Service-to-service authentication

The core functionality remains identical to Chapter 8, including:
- Mobile-first UI design
- Touch-friendly controls
- Status indicators
- Cloud Run deployment
- Enhanced user experience
- All multimodal capabilities from Chapter 10
- Function calling capabilities from Chapter 11 (with single-tool limitation)

## Deployment Architecture

The deployment is more complex due to the proxy server requirement:

```
Client <-> Cloud Run (Main App) <-> Cloud Run (Proxy) <-> Vertex AI
```

Key components:
1. **Main Application Service:**
   - Serves the web interface
   - Handles media processing
   - Manages client connections

2. **Proxy Service:**
   - Authenticates with Vertex AI
   - Manages WebSocket connections
   - Handles service account credentials
   - Routes messages between client and API

## Dockerfile Explained

Our `Dockerfile` is more complex than Chapter 8's version due to the dual-service nature:

```dockerfile
# Base image with Python for proxy server
FROM python:3.11-slim

# Set up working directory
WORKDIR /app

# Install both nginx (for static files) and system utilities
RUN apt-get update && apt-get install -y \
    nginx \
    gettext-base \  # For environment variable substitution
    procps \        # For process management
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY index.html style.css status-handler.js /app/
COPY shared /app/shared
COPY proxy /app/proxy

# Install Python dependencies for proxy
RUN pip install --no-cache-dir \
    websockets \    # For WebSocket handling
    google-auth \   # For Vertex AI authentication
    certifi \      # For SSL certificates
    requests       # For HTTP requests

# Configure nginx with WebSocket support
# - Serves static files on port 8080
# - Proxies WebSocket connections to local proxy server
RUN echo 'events { worker_connections 1024; } http { ... }' > /etc/nginx/nginx.conf

# Start script manages both services:
# 1. Starts Python proxy server
# 2. Monitors proxy startup
# 3. Launches nginx
CMD ["/app/start.sh"]
```

Key differences from Chapter 8's Dockerfile:
1. **Base Image:**
   - Chapter 8: Simple nginx:alpine for static files
   - Chapter 12: Python image with additional nginx installation

2. **Service Management:**
   - Chapter 8: Single nginx service
   - Chapter 12: Dual-service setup (nginx + Python proxy)

3. **Configuration:**
   - Chapter 8: Basic nginx config for static files
   - Chapter 12: Complex nginx config with WebSocket proxy

4. **Dependencies:**
   - Chapter 8: None required
   - Chapter 12: Python packages and system utilities

5. **Startup Process:**
   - Chapter 8: Direct nginx startup
   - Chapter 12: Orchestrated startup with health checks

## Nginx Configuration Details

The nginx configuration is more complex in Chapter 12 to handle both static files and WebSocket proxying:

```nginx
events {
    worker_connections 1024;  # Handle up to 1024 simultaneous connections
}

http {
    include /etc/nginx/mime.types;  # Proper MIME type handling for static files
    
    # WebSocket upgrade mapping
    map $http_upgrade $connection_upgrade {
        default upgrade;  # Default to upgrade for WebSocket connections
        '' close;        # Close connection if no upgrade header
    }
    
    server {
        listen 8080;  # Required for Cloud Run
        
        # Serve static files (HTML, JS, CSS)
        location / {
            root /app;
            try_files $uri $uri/ =404;
        }
        
        # Proxy WebSocket connections to local proxy server
        location /ws {
            proxy_pass http://localhost:8081;  # Forward to Python proxy
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }
    }
}
```

This configuration:
1. Serves static files from `/app` directory
2. Routes WebSocket connections to the Python proxy on port 8081
3. Properly handles WebSocket upgrades and connection management
4. Ensures correct MIME types for static files

## Startup Script Details

The `start.sh` script orchestrates the dual-service startup:

```bash
#!/bin/bash

# Start proxy with output logging
python /app/proxy/proxy.py 2>&1 | tee /var/log/proxy.log &
PROXY_PID=$!

# Give proxy a moment to start
sleep 10

# Check if proxy is still running
if ! kill -0 $PROXY_PID 2>/dev/null; then
    echo "Proxy failed to start. Last few lines of log:"
    tail -n 5 /var/log/proxy.log
    exit 1
fi

# Start nginx
nginx -g "daemon off;"
```

The script:
1. **Starts Proxy Server:**
   - Launches Python proxy in background
   - Captures all output (stdout and stderr) to log file
   - Stores process ID for monitoring

2. **Health Check:**
   - Waits for proxy to initialize
   - Verifies proxy is still running
   - Shows logs if startup failed

3. **Nginx Launch:**
   - Starts nginx in foreground mode
   - Required for proper container operation
   - Ensures container stays running

This orchestration ensures:
- Both services are running
- Proper startup order
- Error detection and logging
- Container health management

For detailed technical information about the base implementation, including:
- Mobile-first UI design
- Cloud Run deployment
- Status management
- Project structure
- Usage instructions
- Design philosophy

Please refer to the comprehensive documentation in [Chapter 8's README](../../part_2_dev_api/chapter_08/README.md).

## Code Comparison

You can compare the implementations by looking at:
- [Chapter 12 index.html](./index.html) (Vertex API version)
- [Chapter 8 index.html](../../part_2_dev_api/chapter_08/index.html) (Development API version)

The main differences are in the deployment architecture, service configuration, and authentication handling, while the core mobile-first UI and user experience remain the same.