FROM nvcr.io/nvidia/pytorch:23.10-py3

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY services/stt/requirements.txt /app/services/stt/requirements.txt
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --no-cache-dir -r /app/services/stt/requirements.txt
RUN pip install --upgrade lhotse

COPY shared /app/shared
COPY services/stt /app/services/stt

ENV PYTHONPATH=/app:$PYTHONPATH

WORKDIR /app/services/stt

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]