FROM python:3.9-slim

# Set working directory in container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Set Flask environment variable
ENV FLASK_APP=your_package.app

# Expose port 9090
EXPOSE 9090

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=9090"]