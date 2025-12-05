# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8000 for the FastAPI app
EXPOSE 8000

# Define environment variable for ML Service URL (can be overridden in docker run)
# host.docker.internal allows access to the host machine's localhost (for testing with ML service running locally)
ENV ML_SERVICE_URL="http://host.docker.internal:8001"

# Run main.py when the container launches using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
