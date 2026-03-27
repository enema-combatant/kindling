FROM python:3.11-slim

WORKDIR /app

COPY shared/requirements-base.txt /tmp/requirements-base.txt
COPY missions/02-retrieval/app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements-base.txt -r /tmp/requirements.txt

COPY shared/ /app/shared/
# Reuse Mission 01's ingest module
COPY missions/01-memory/app/ingest.py /app/ingest.py
COPY missions/02-retrieval/app/ /app/
COPY missions/02-retrieval/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 5002

ENTRYPOINT ["/app/entrypoint.sh"]
