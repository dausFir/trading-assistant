# Dockerfile for Trading Assistant
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install hatchling && pip install .

# Copy source code
COPY app/ ./app/
COPY .env.example .env

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Expose port for web dashboard
EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "app.web.server:app", "--host", "0.0.0.0", "--port", "8000"]
