# Use the official Python runtime image
FROM python:3.13  

# Set the working directory
WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV PYTHONIOENCODING UTF-8

# Set environment variables for Django
ENV DJANGO_SETTINGS_MODULE hospital_appointment.settings


RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY hospital_appointment/requirements.txt .
RUN pip install -r requirements.txt

# Copy the application code
COPY hospital_appointment/ .

# Expose the port the app runs on
EXPOSE 8000

# Run Django’s development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]