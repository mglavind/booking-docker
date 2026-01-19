# Stage 1: Base build stage
FROM python:3.13-bookworm
# Create the app directory
RUN mkdir /app

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 
 
# Set the working directory
WORKDIR /app

RUN apt-get update && apt-get install -y curl

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the requirements file first (better caching)
COPY src/requirements.txt .

RUN uv pip install -r requirements.txt --system

COPY src/ .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip 
 
# Expose the application port
EXPOSE 8000 

# Start the application
CMD ["./entrypoint.sh"]
