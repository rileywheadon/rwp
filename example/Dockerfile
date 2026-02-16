FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY app.py ./

EXPOSE 5000

CMD ["python", "app.py"]
