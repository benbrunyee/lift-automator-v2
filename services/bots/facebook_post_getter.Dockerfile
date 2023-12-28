FROM ubuntu:24.04

# Install dependencies
RUN apt-get update && apt-get install -y  \
  curl \
  wget \
  xvfb \
  unzip \
  python3 \
  python3-pip \
  python3-dev \
  build-essential \
  libssl-dev \
  libffi-dev \
  python3-setuptools \
  python3-venv

# Set up the Chrome PPA
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Update the package list and install chrome
RUN apt-get update -y
RUN apt-get install -y google-chrome-stable

# Install Chromedriver
RUN CHROME_VERSION=$(google-chrome --product-version | cut -d '.' -f 1-3) && \
  DRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROME_VERSION") && \
  wget -q --continue -P /chromedriver "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$DRIVER_VERSION/linux64/chromedriver-linux64.zip" && \
  unzip /chromedriver/chromedriver* -d /chromedriver

# Add the chromedriver to the PATH
ENV PATH $PATH:/chromedriver

# Create a directory for the app code
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Copy the requirements.txt first for better cache on later pushes
COPY ./facebook_post_getter/requirements.txt /usr/src/app/requirements.txt

# Install dependencies
RUN python3 -m venv venv && ./venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the encryption key
COPY ./facebook_post_getter/key.txt /usr/src/app/key.txt

# Copy the service account key
COPY ./lib/service_account_key.json /usr/src/app/service_account_key.json

# Copy the environment variables
COPY ./facebook_post_getter/.env /usr/src/app/.env

# Copy the code
COPY ./lib /usr/src/app/lib
COPY ./facebook_post_getter/facebook_post_getter.py /usr/src/app/facebook_post_getter.py

# Run the application
CMD ["./venv/bin/python", "facebook_post_getter.py"]
