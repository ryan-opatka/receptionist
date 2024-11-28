FROM python:3.9-slim

WORKDIR /app

# Copy application files
COPY . .

RUN pip install --upgrade pip
# Install dependencies
RUN pip install -r requirements.txt

# Set environment variable
ENV PORT 8080

# Expose the port
EXPOSE 8080

# Run the application
CMD exec gunicorn --bind :$PORT answer:app
