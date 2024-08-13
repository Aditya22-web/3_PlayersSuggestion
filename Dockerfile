# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy all files from the root directory into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Install Node.js and npm
RUN apt-get update && apt-get install -y nodejs npm
# Build the Svelte frontend
RUN npm install && npm run build

# Make sure the build output is in the correct directory
RUN mkdir -p /app/build
RUN mv /app/__sapper__/build/* /app/build/

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--root-path", "/app/build"]
