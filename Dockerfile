FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates ./templates
RUN adduser --disabled-password --gecos "" --uid 10001 appuser \
    && mkdir -p /app/instance \
    && chown -R appuser:appuser /app

USER appuser
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
