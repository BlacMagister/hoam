FROM python:3.10-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.10-slim as runtime

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app/src

RUN apt-get update && apt-get install -y libssl-dev
EXPOSE 8080 4001

CMD ["python", "-m", "uvicorn", "src.blockchain.api.rest:app", "--host", "0.0.0.0", "--port", "8080"]
