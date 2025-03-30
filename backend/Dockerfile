# Use an x86 base image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy files
COPY requirements.txt .
COPY main.py .
COPY model_final.pth .
COPY detectron2_setup.sh .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run Detectron2 setup script
RUN chmod +x detectron2_setup.sh && ./detectron2_setup.sh

# Expose port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
