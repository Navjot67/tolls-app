"""
Gunicorn configuration for production deployment
"""
import multiprocessing
import os

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = os.path.join(os.path.dirname(__file__), "logs", "gunicorn-access.log")
errorlog = os.path.join(os.path.dirname(__file__), "logs", "gunicorn-error.log")
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "toll-app"

# Server mechanics
daemon = False
pidfile = os.path.join(os.path.dirname(__file__), "logs", "gunicorn.pid")
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Performance tuning
max_requests = 1000
max_requests_jitter = 50
preload_app = True

def when_ready(server):
    """Called just after the server is started"""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Called when a worker receives INT or QUIT signal"""
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked"""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application"""
    pass

def worker_abort(worker):
    """Called when a worker receives the ABRT signal"""
    worker.log.info("worker received ABRT signal")

