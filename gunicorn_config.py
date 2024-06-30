# Gunicorn configuration
bind = '0.0.0.0:8040'  # Specify the IP address and port to bind
workers = 4  # Number of worker processes
worker_class = 'uvicorn.workers.UvicornWorker'  # Use Uvicorn worker class
timeout = 60  # Timeout for requests in seconds
keepalive = 2  # Keep-alive interval
loglevel = 'info'  # Log level
 
# Configure the Gunicorn error and access logs
#errorlog = '/home/vagrant/log/bi_api.log'
#Saccesslog = '/home/vagrant/log/bi_api.log'
 
# Example command to run Gunicorn with this configuration:
# gunicorn -c gunicorn_config.py app.main:app