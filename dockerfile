
# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt


# Copy project
COPY . /code/

# Set work directory back to Django project
WORKDIR /code

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]