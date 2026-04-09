ARG REGISTRY_PREFIX_DOCKER_HUB=
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY smoke_test.py ./smoke_test.py

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
