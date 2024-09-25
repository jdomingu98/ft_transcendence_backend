# Base image
FROM python:3.12-slim

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

# Expose the port for the Django app
EXPOSE 8000

# Start the Django application
# WSGI server for Python applications
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi:application"]
