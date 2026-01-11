# Deployment Guide

## Development Setup

### Quick Start
```bash
# Clone repository
git clone https://github.com/nithishvaduganathan/data-leakage-checker.git
cd data-leakage-checker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python run.py
```

Access at: http://localhost:5000

## Production Deployment

### Using Gunicorn (Recommended)

```bash
# Install Gunicorn
pip install gunicorn

# Set environment variables
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export FLASK_HOST="0.0.0.0"
export FLASK_PORT="8000"

# Run with Gunicorn (4 worker processes)
gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 run:app
```

### Using Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV SECRET_KEY="change-this-in-production"
ENV FLASK_HOST="0.0.0.0"
ENV FLASK_PORT="5000"

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

Build and run:
```bash
docker build -t data-leakage-checker .
docker run -p 5000:5000 -e SECRET_KEY="your-secret" data-leakage-checker
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| SECRET_KEY | Flask secret key for sessions | dev-secret-key-change-in-production | Yes (Production) |
| FLASK_DEBUG | Enable debug mode | False | No |
| FLASK_HOST | Host to bind to | 127.0.0.1 | No |
| FLASK_PORT | Port to bind to | 5000 | No |

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for large file uploads
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # Increase max upload size
    client_max_body_size 50M;
}
```

## Security Checklist

- [ ] Set strong SECRET_KEY from environment
- [ ] Disable debug mode in production
- [ ] Use HTTPS/TLS certificates
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Monitor error logs
- [ ] Implement rate limiting
- [ ] Regular backups

## Monitoring

### Health Check Endpoint
```bash
curl http://localhost:5000/
```

### Log Files
```bash
# View application logs
tail -f /var/log/gunicorn/access.log
tail -f /var/log/gunicorn/error.log
```

## Troubleshooting

### Issue: Module not found
```bash
pip install -r requirements.txt
```

### Issue: Permission denied on uploads
```bash
chmod 755 app/static/uploads
chmod 755 app/static/cleaned
```

### Issue: Port already in use
```bash
# Change port in environment
export FLASK_PORT="5001"
```

## Maintenance

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Clear Uploaded Files
```bash
rm -rf app/static/uploads/*
rm -rf app/static/cleaned/*
```

### Backup
```bash
tar -czf backup-$(date +%Y%m%d).tar.gz app/static/
```
