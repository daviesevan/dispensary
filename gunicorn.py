# gunicorn_config.py

# The number of worker processes for handling requests
workers = 4

# The type of worker process (sync, eventlet, gevent, or gthread)
worker_class = "sync"

# The maximum number of pending connections that each worker can handle
backlog = 2048

# The maximum number of requests a worker can process before being restarted
max_requests = 1000

# The maximum time a worker can be idle before being restarted
timeout = 30

# Logging
loglevel = "info"
errorlog = "/path/to/gunicorn_error.log"
accesslog = "/path/to/gunicorn_access.log"
