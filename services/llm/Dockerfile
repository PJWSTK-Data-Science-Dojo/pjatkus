FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY services/llm/requirements.txt /app/services/llm/requirements.txt
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --no-cache-dir -r /app/services/llm/requirements.txt

COPY shared /app/shared
COPY services/llm /app/services/llm

ENV PYTHONPATH=/app:$PYTHONPATH

WORKDIR /app/services/llm

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]