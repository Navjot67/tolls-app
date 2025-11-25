# Production Deployment Guide

This is the **recommended production setup** for the E-ZPass Toll App.

## Why This Approach?

### Current Issues:
- ❌ Using Flask's development server (not production-ready)
- ❌ No process management (app crashes = downtime)
- ❌ No worker processes (single-threaded)
- ❌ Manual nginx setup complexity

### Production Solution:
- ✅ Gunicorn WSGI server (production-grade)
- ✅ Systemd service (auto-restart, process management)
- ✅ Multiple workers (better performance)
- ✅ Automated setup script
- ✅ Proper logging and monitoring

## Architecture

```
Internet → Domain (DNS) → Nginx (Port 443) → Gunicorn (Port 5000) → Flask App
```

## Quick Setup

### 1. Install Dependencies
```bash
cd /Users/ghuman/tolls
pip install -r requirements.txt
```

### 2. Create Logs Directory
```bash
mkdir -p logs
```

### 3. Update Service File
Edit `toll-app.service`:
- Replace `YOUR_USER` with your username
- Replace `YOUR_GROUP` with your group (usually same as username)
- Update paths if different

### 4. Install Systemd Service
```bash
sudo cp toll-app.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable toll-app
sudo systemctl start toll-app
```

### 5. Check Status
```bash
sudo systemctl status toll-app
```

### 6. Setup Nginx
```bash
sudo ./setup-domain.sh
```

## Manual Setup

### Step 1: Start Gunicorn Manually (Testing)
```bash
cd /Users/ghuman/tolls
source venv/bin/activate  # If using virtual environment
gunicorn --config gunicorn_config.py app:app
```

### Step 2: Install as Systemd Service
```bash
# Copy service file
sudo cp toll-app.service /etc/systemd/system/

# Edit service file
sudo nano /etc/systemd/system/toll-app.service
# Update USER, GROUP, and paths

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable toll-app
sudo systemctl start toll-app

# Check status
sudo systemctl status toll-app
```

### Step 3: View Logs
```bash
# Systemd logs
sudo journalctl -u toll-app -f

# Gunicorn logs
tail -f logs/gunicorn-access.log
tail -f logs/gunicorn-error.log
```

## Configuration

### Gunicorn Workers
Edit `gunicorn_config.py` to adjust:
- `workers`: Number of worker processes (default: CPU cores * 2 + 1)
- `timeout`: Request timeout in seconds
- `bind`: Address and port

### Environment Variables
Create/update `.env` file:
```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
```

## Monitoring

### Check Service Status
```bash
sudo systemctl status toll-app
```

### View Real-time Logs
```bash
sudo journalctl -u toll-app -f
```

### Restart Service
```bash
sudo systemctl restart toll-app
```

### Stop Service
```bash
sudo systemctl stop toll-app
```

## Troubleshooting

### Service Won't Start
1. Check logs: `sudo journalctl -u toll-app -n 50`
2. Check Gunicorn config: `gunicorn --check-config gunicorn_config.py`
3. Test manually: `gunicorn --config gunicorn_config.py app:app`

### Port Already in Use
- Check if Flask dev server is running: `ps aux | grep app.py`
- Kill it: `pkill -f "python.*app.py"`
- Or change port in `gunicorn_config.py`

### Permission Issues
- Ensure user in service file has access to app directory
- Check file permissions: `ls -la /Users/ghuman/tolls`

### High Memory Usage
- Reduce workers in `gunicorn_config.py`
- Monitor: `htop` or `top`

## Performance Tuning

### For Low Traffic (< 100 req/min):
```python
workers = 2
worker_class = "sync"
```

### For Medium Traffic (100-1000 req/min):
```python
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
```

### For High Traffic (> 1000 req/min):
```python
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
```
(Requires: `pip install gevent`)

## Security

### Firewall
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### SSL/TLS
- Use Let's Encrypt (free): `sudo certbot --nginx -d YOUR_DOMAIN`
- Auto-renewal: `sudo certbot renew --dry-run`

### Environment Variables
- Never commit `.env` file
- Use strong `SECRET_KEY`
- Rotate credentials regularly

## Backup & Recovery

### Backup Important Files
```bash
# User data
cp users.json users.json.backup

# Account config
cp accounts_config.json accounts_config.json.backup

# Logs (optional)
tar -czf logs-backup.tar.gz logs/
```

### Restore
```bash
cp users.json.backup users.json
cp accounts_config.json.backup accounts_config.json
sudo systemctl restart toll-app
```

## Comparison: Dev vs Production

| Feature | Development | Production |
|---------|------------|------------|
| Server | Flask dev server | Gunicorn |
| Workers | 1 | Multiple (CPU * 2 + 1) |
| Process Management | Manual | Systemd |
| Auto-restart | No | Yes |
| Logging | Console | Files + Journal |
| Performance | Low | High |
| Security | Basic | Enhanced |

## Next Steps

1. ✅ Set up Gunicorn + Systemd
2. ✅ Configure domain with Nginx
3. ✅ Set up SSL certificate
4. ✅ Configure monitoring
5. ✅ Set up backups
6. ✅ Test failover scenarios

## Alternative: Cloud Platforms

For easier deployment, consider:
- **Heroku**: `git push heroku main`
- **DigitalOcean App Platform**: One-click deploy
- **AWS Elastic Beanstalk**: Managed deployment
- **Railway**: Simple deployment
- **Render**: Free tier available

These platforms handle:
- Process management
- SSL certificates
- Scaling
- Monitoring

See `CLOUD_DEPLOYMENT.md` for cloud-specific guides.

