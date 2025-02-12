.PHONY: install test run docker

install:
	pip install --upgrade pip
	pip install -r requirements.txt

migrate:
	python src/main.py migrate

test:
	pytest -v --cov=src --cov-report=html

run:
	uvicorn src.blockchain.api.rest:app --reload

docker-build:
	docker build -t blockchain-pro .

docker-run:
	docker run -p 8080:8080 -p 4001:4001 blockchain-pro

lint:
	ruff check src
	black --check src

format:
	black src
	ruff --fix src

security:
	bandit -r src
	safety check
