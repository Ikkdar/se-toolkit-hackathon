FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir "https://github.com/inno-se-toolkit/qwen-code-api/archive/refs/heads/main.zip"

EXPOSE 8080

CMD ["python", "-m", "qwen_code_api.main"]
