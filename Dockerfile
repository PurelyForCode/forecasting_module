FROM python:3.13.7-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password appuser
USER appuser

EXPOSE 8000

# For production: Gunicorn with Uvicorn workers
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
