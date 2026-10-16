FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_PATH=/data/cities.db \
    PORT=8000

WORKDIR /app
COPY app.py database.py weather.py ./

RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /data \
    && chown appuser:appuser /data

USER appuser

EXPOSE 8000
VOLUME ["/data"]
CMD ["python", "app.py"]
