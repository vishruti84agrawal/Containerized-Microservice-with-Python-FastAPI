# Use the official Python 3.11 slim image as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies listed in the requirements file
# The `--no-cache-dir` option prevents caching to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY app/ .

# Copy the public directory (if it contains static files or assets)
COPY ./public ./public

# Command to run the FastAPI application using Uvicorn
# - `main:app` specifies the module (`main.py`) and the FastAPI app instance (`app`)
# - `--host 0.0.0.0` makes the app accessible from outside the container
# - `--port 8001` specifies the port the app will run on
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]