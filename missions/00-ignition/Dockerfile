FROM python:3.11-slim

WORKDIR /app

# Install shared dependencies first (cached layer)
COPY shared/requirements-base.txt /tmp/requirements-base.txt
COPY missions/00-ignition/app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements-base.txt -r /tmp/requirements.txt

# Copy shared modules
COPY shared/ /app/shared/

# Copy application
COPY missions/00-ignition/app/ /app/

# Pull the model on first startup, then run the app
COPY missions/00-ignition/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/app/entrypoint.sh"]
