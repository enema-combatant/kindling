FROM python:3.11-slim

WORKDIR /app

COPY shared/requirements-base.txt /tmp/requirements-base.txt
COPY missions/01-memory/app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements-base.txt -r /tmp/requirements.txt

COPY shared/ /app/shared/
COPY missions/01-memory/app/ /app/
COPY missions/01-memory/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 5001

ENTRYPOINT ["/app/entrypoint.sh"]
