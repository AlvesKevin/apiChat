FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make wait script executable
RUN chmod +x wait-for-postgres.sh

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "chatbot_api.wsgi:application"]