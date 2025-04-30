FROM python:3.10

# Set working directory
WORKDIR /app/myproject

# Copy files
COPY . /app
RUN pip install -r /app/requirements.txt

# Run Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
