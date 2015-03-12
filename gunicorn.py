import os as _os, sys as _sys
_HOME = _os.environ.get("TRJ_HOME")
if _HOME is None:
    print("Environment variable TRJ_HOME not set. Exiting.")
    _sys.exit( 1 )


# IP and port to bind to.
bind = ['127.0.0.1:8080']

# Maximum number of pending connections.
backlog = 2048

# Number of worker processes to handle connections.
workers = 20

# Fork main process to background.
daemon = True

# PID file to write to.
pidfile = _os.path.join(_HOME, "web.gunicorn.pid")

# Allow connections from any frontend proxy.
# forwarded_allow_ips = '*'

# Logging configuration.
accesslog = _os.path.join(_HOME, "web.gunicorn.access.log")
errorlog = _os.path.join(_HOME, "web.gunicorn.error.log")
loglevel = "warning"

# Gunicorn process name.
proc_name = "trajectory-gunicorn"

# Path to source directory.
pythonpath = _os.path.join(_HOME, "src", "main", "python")
