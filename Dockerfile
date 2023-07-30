# Use the official Python image as the base image
FROM python:3.11.3

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . .

# Expose the port your Flask app will be running on
EXPOSE 5000

# Set environment variables if needed (optional)
# ENV FLASK_ENV=production
# ENV FLASK_APP=app.py

# (Optional) Uncomment the line below to create the database file
# RUN python create_db.py

# Command to run your Flask app using Gunicorn (adjust if needed)
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000", "--workers", "4"]
