# Use the official Python image
FROM python:3.12

# Set working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpng-dev \
    libfreetype6-dev \
    libxft-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the current directory into the container
COPY . .

# Expose the FastAPI application port
EXPOSE 8000

# Start the FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
