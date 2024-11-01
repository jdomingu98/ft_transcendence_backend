
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

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["sh", "entrypoint.sh"]
