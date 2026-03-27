FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY shared/requirements-base.txt /tmp/requirements-base.txt
COPY missions/03-voice/app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements-base.txt -r /tmp/requirements.txt

COPY shared/ /app/shared/
COPY missions/01-memory/app/ingest.py /app/ingest.py
COPY missions/02-retrieval/app/rag.py /app/rag.py
COPY missions/03-voice/app/ /app/
COPY missions/03-voice/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 5003

ENTRYPOINT ["/app/entrypoint.sh"]
