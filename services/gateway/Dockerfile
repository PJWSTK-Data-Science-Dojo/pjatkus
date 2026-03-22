FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY services/gateway/requirements.txt /app/services/gateway/requirements.txt
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --no-cache-dir -r /app/services/gateway/requirements.txt

COPY shared /app/shared
COPY services/gateway /app/services/gateway

ENV PYTHONPATH=/app:$PYTHONPATH

WORKDIR /app/services/gateway

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]