# Python image to use.
FROM python:3.12-slim

# Set the working directory to /app
WORKDIR /app

# copy current directory files
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Run app.py when the container launches
ENTRYPOINT ["python", "api.py"]