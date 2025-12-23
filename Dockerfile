FROM python:3.11-slim

# System setup (optional: add build tools if needed)
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose port FastAPI/uvicorn will run on
EXPOSE 8000

# Start the FastAPI application with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]