FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/instance /app/static/img/uploads

ENV PORT=5050
ENV HOST=0.0.0.0
ENV FLASK_ENV=production

EXPOSE 5050

CMD ["gunicorn", "--bind", "0.0.0.0:5050", "--workers", "3", "--threads", "2", "app:app"]
