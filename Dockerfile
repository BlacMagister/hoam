FROM python:3.10-slim-bullseye as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.10-slim-bullseye as runtime

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8080 4001
CMD ["uvicorn", "src.blockchain.api.rest:app", "--host", "0.0.0.0", "--port", "8080"]
