
# Base image
FROM python:3.12-slim

ARG PASSPHRASE

# Install the OpenSSH client
RUN apt-get update && apt-get install -y openssh-client

# Set environment variables
# Avoid .pyc files generation, which saves disk space
ENV PYTHONDONTWRITEBYTECODE 1

# The output is not buffered, it is sent directly to the console.
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy the entire project into the container
COPY . /app/

# Generate private and public keys
RUN yes | ssh-keygen -t rsa -b 2048 -m PEM -f jwtRS256.key -N "$PASSPHRASE"

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN python manage.py migrate

# Run the Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
