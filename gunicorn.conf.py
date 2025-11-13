# Gunicorn configuration file
import multiprocessing

# Bind to the port that Render provides
bind = "0.0.0.0:10000"

# Worker processes - use only 1 worker to save memory
workers = 1
worker_class = "sync"

# Timeouts
timeout = 120  # Increase timeout for ML processing
keepalive = 5

# Memory optimization
max_requests = 100
max_requests_jitter = 20

# Logging
accesslog = "-"
errorlog = "-"
