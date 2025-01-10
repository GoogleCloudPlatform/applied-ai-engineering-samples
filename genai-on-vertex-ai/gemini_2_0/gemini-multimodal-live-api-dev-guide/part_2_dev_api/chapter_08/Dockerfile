# Use nginx to serve static files
FROM nginx:alpine

# Copy all files from current directory to nginx's web root
# This includes both the app files and the shared directory
COPY . /usr/share/nginx/html/

# The port that nginx will listen on (required for Cloud Run)
EXPOSE 8080

# Configure nginx to serve files on port 8080
RUN echo 'server { \
    listen 8080; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf