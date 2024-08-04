
# Here we are using the official Python 3.9 image
FROM python:3.9-slim

# Here we set up the environment variables
ENV PYTHONUNBUFFERED=1
ENV TOKENIZERS_PARALLELISM=false

# Here we install all system dependencies and packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Here we set the working directory
WORKDIR /app

# Here we copy the requirements.txt file to the working directory
# We also install the dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Here we copy the rest of the application code
COPY . /app

# Here we expose the port the app runs on
EXPOSE 5000

# Here we start the Flask application
CMD ["python", "app.py"]
