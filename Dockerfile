# Use nginx as the base image for serving static files
FROM nginx:alpine

# PERF-019: Only copy necessary web files (exclude .git, desktop-app, wiki, etc.)
COPY index.html /usr/share/nginx/html/
COPY script.js /usr/share/nginx/html/
COPY styles.css /usr/share/nginx/html/
COPY sw.js /usr/share/nginx/html/
COPY manifest.json /usr/share/nginx/html/
COPY robots.txt /usr/share/nginx/html/
COPY sitemap.xml /usr/share/nginx/html/
COPY assets/icon.jpg /usr/share/nginx/html/assets/

# Create a custom nginx configuration with compression and security
# PERF-020: Added gzip compression for text-based assets
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    # Enable gzip compression (PERF-020) \
    gzip on; \
    gzip_vary on; \
    gzip_proxied any; \
    gzip_comp_level 6; \
    gzip_min_length 256; \
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript image/svg+xml; \
    \
    # Handle client-side routing for SPA \
    location / { \
    try_files $uri $uri/ /index.html; \
    } \
    \
    # Cache static assets config \
    location = /sw.js { \
        add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0" always; \
        expires off; \
    } \
    location ~* \.(html|js|css)$ { \
        add_header Cache-Control "no-cache" always; \
    } \
    location ~* \.(png|jpg|jpeg|gif|ico|svg)$ { \
        expires 1y; \
        add_header Cache-Control "public, no-transform"; \
    } \
    \
    # Security headers \
    add_header X-Frame-Options "SAMEORIGIN" always; \
    add_header X-Content-Type-Options "nosniff" always; \
    add_header X-XSS-Protection "1; mode=block" always; \
    add_header Referrer-Policy "strict-origin-when-cross-origin" always; \
    # PERF-029: Content Security Policy for defense-in-depth \
    add_header Content-Security-Policy "default-src '"'"'self'"'"'; script-src '"'"'self'"'"' cdnjs.cloudflare.com cdn.jsdelivr.net '"'"'unsafe-inline'"'"'; style-src '"'"'self'"'"' cdnjs.cloudflare.com cdn.jsdelivr.net '"'"'unsafe-inline'"'"'; img-src '"'"'self'"'"' https: data: blob:; font-src '"'"'self'"'"' cdn.jsdelivr.net; connect-src '"'"'self'"'"' api.github.com raw.githubusercontent.com http://localhost:8000 cdnjs.cloudflare.com cdn.jsdelivr.net;" always; \
    }' > /etc/nginx/conf.d/default.conf

# Limit worker processes to 1 to prevent resource exhaustion on cloud hosts (e.g. Railway)
RUN sed -i 's/worker_processes.*/worker_processes 1;/g' /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

