FROM python:3.11-slim

WORKDIR /app

COPY requirements-server.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install chromium --with-deps

COPY server.py .
COPY status.json status_data.json

EXPOSE 10000

CMD ["python", "server.py"]
