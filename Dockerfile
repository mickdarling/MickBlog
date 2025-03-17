FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=mickblog.settings
ENV PATH="/app/scripts:${PATH}"

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create static and media directories
RUN mkdir -p /app/staticfiles
RUN mkdir -p /app/media

# Create and set permissions for scripts directory
RUN mkdir -p /app/scripts
COPY scripts/* /app/scripts/
RUN chmod +x /app/scripts/*

# Expose port
EXPOSE 8000

# Run the application
CMD ["./scripts/entrypoint.sh"]