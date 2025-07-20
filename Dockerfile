# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy requirements
COPY pyproject.toml poetry.lock* requirements.txt* ./

# Install dependencies
RUN pip install --upgrade pip
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-root || pip install -r requirements.txt

# Copy the entire app
COPY . .

# Expose FastAPI app port
EXPOSE 8000

# Default command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
