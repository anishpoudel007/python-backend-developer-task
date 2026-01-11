# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /code

# Upgrade pip and install uv
RUN pip install --upgrade pip

COPY requirements.txt /code/

RUN pip install -r requirements.txt


# Copy all project files
COPY . /code/

# Run migrations and start Uvicorn
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
