# Production Deployment Guide

## 🚀 Deployment Options

### Docker Deployment (Recommended)

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libsm6 libxext6 libxrender-dev
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN mkdir -p uploads results logs models

EXPOSE 5000
HEALTHCHECK --interval=30s CMD python -c "import requests; requests.get('http://localhost:5000/api/health')"

CMD ["python", "src/app.py"]
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  medical-diagnosis:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

### Run Docker

```bash
docker build -t medical-diagnosis:latest .
docker-compose up -d
```

### Cloud Deployment

**AWS (Elastic Beanstalk):**
```bash
eb init -p python-3.9 medical-diagnosis
eb create medical-diagnosis-prod
eb deploy
```

**Google Cloud (Cloud Run):**
```bash
gcloud run deploy medical-diagnosis \
  --source . \
  --platform managed \
  --memory 4Gi
```

**Azure (App Service):**
```bash
az webapp up --name medical-diagnosis-app
```

## 🔐 Security

### HTTPS Configuration (Nginx)
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/certs/certificate.crt;
    ssl_certificate_key /etc/nginx/certs/private.key;
    
    location / {
        proxy_pass http://medical-diagnosis:5000;
    }
}
```

### Environment Variables
```bash
FLASK_ENV=production
MAX_UPLOAD_SIZE=10485760
API_KEY=your-secret-key
```

## 📊 Monitoring

### Logging
```python
import logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO
)
```

### Health Check
```bash
curl http://localhost:5000/api/health
```

---

For more information, see README.md and QUICKSTART.md
