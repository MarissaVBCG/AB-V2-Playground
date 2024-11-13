# Use the official Python image from Docker Hub
FROM python:3.12.3-slim

# Set the working directory
WORKDIR /app

# Install dependencies for Chrome, Xvfb, tkinter, gnome-screenshot, xclip, and other tools
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    xvfb \
    python3-tk \
    gnome-screenshot \
    xclip \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files to the container, including images and scripts
COPY . /app

# Copy all .png files to /app directory in the container
COPY *.png /app/

# Set up the display for Xvfb
ENV DISPLAY=:99

# Run the application
CMD ["python", "controller.py"]
