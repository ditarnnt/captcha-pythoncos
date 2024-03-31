# Use the official Python image with Alpine Linux as it's small and more secure
FROM python:3.9-alpine

# Install dependencies required for Pillow (PIL)
RUN apk --no-cache add jpeg-dev zlib-dev
RUN apk --no-cache add --virtual .build-deps build-base linux-headers

# Set work directory
WORKDIR /app

# Copy the dependencies file to the working directory
COPY app/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Remove build dependencies to reduce container size
RUN apk del .build-deps

# Copy the content of the local src directory to the working directory
COPY app/ .

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
