FROM python:3.11-slim

WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y \
    nginx \
    gettext-base \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY index.html style.css status-handler.js /app/
COPY shared /app/shared
COPY proxy /app/proxy

# Install Python dependencies
RUN pip install --no-cache-dir \
    websockets \
    google-auth \
    certifi \
    requests

# Configure nginx
RUN echo 'events { worker_connections 1024; } http { include /etc/nginx/mime.types; map $http_upgrade $connection_upgrade { default upgrade; "" close; } server { listen 8080; location / { root /app; try_files $uri $uri/ =404; } location /ws { proxy_pass http://localhost:8081; proxy_http_version 1.1; proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade"; proxy_set_header Host $host; } } }' > /etc/nginx/nginx.conf

# Create startup script
RUN echo '#!/bin/bash\n\
\n\
# Start proxy with output logging\n\
python /app/proxy/proxy.py 2>&1 | tee /var/log/proxy.log &\n\
PROXY_PID=$!\n\
\n\
# Give proxy a moment to start\n\
sleep 10\n\
\n\
# Check if proxy is still running\n\
if ! kill -0 $PROXY_PID 2>/dev/null; then\n\
    echo "Proxy failed to start. Last few lines of log:"\n\
    tail -n 5 /var/log/proxy.log\n\
    exit 1\n\
fi\n\
\n\
# Start nginx\n\
nginx -g "daemon off;"' > /app/start.sh && \
    chmod +x /app/start.sh

EXPOSE 8080

CMD ["/app/start.sh"] 