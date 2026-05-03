# 1. Use an official, lightweight Python computer as our base
FROM python:3.11-slim

# 2. Set the working directory inside the container to /app
WORKDIR /app

# 3. Copy everything from your project folder into the /app folder in Docker
COPY . /app

# 4. Install the required Python packages (with extended timeout for slower networks)
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# 5. Expose port 8501 (the standard port Streamlit uses)
EXPOSE 8501

# 6. The final command to run your app when the container starts
CMD ["streamlit", "run", "gui_app.py", "--server.port=8501", "--server.address=0.0.0.0"]