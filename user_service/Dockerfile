# user_service/Dockerfile
FROM python:3.11-slim

# Set the working directory inside the container to /app
# All subsequent commands will be executed relative to this directory
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
