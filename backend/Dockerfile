FROM python:3.12.4-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/backend

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p data logs

EXPOSE 8012

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8012"]
