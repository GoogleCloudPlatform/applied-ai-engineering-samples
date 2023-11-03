# Python image to use.
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# copy current directory files
COPY . .

# Run app when the container launches
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]