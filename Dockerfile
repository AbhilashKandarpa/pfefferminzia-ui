# Frontend build stage
FROM node:18-alpine as frontend-build

WORKDIR /app/frontend
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Backend build stage
FROM python:3.12-slim as backend-build

# Add build argument
ARG ALAN_API_KEY
ENV ALAN_API_KEY=$ALAN_API_KEY

WORKDIR /app/backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .

# Final stage
FROM python:3.12-slim

# Install Node.js and npm
RUN apt-get update && apt-get install -y \
    curl \
    && curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend files and Python packages
COPY --from=backend-build /app/backend /app
COPY --from=backend-build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend files
COPY --from=frontend-build /app/frontend /app/frontend

EXPOSE 3000 8000

# Copy and prepare startup script
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]