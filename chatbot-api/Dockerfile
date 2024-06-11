# Base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ .

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["python", "main.py"]