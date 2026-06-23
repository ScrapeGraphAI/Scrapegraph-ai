FROM python:3.12-slim
WORKDIR /app
COPY backend/pyproject.toml .
RUN pip install --no-cache-dir -e ..
RUN pip install --no-cache-dir fastapi uvicorn[standard] crawl4ai
COPY backend/ .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
