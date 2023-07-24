# The builder image, used to build the virtual environment
FROM python:3.11-buster as builder
# Update package index and install git, then install Poetry
RUN apt-get update && apt-get install -y git
RUN pip install poetry==1.4.2

# Set Poetry behavior
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
# Container will listen on 8080
ENV HOST=0.0.0.0
ENV LISTEN_PORT 8080
EXPOSE 8080
WORKDIR /app
COPY pyproject.toml poetry.lock ./
# Use Poetry to install dependencies, excluding dev dependencies
# Removing cache directory minimizes image size (at cost of speed)
RUN poetry install --without dev --no-root
RUN rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.11-buster as runtime

# Set environment variables for VENV and add to PATH
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

# Copy the virtual environment directory from the builder stage to the same location in the runtime
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

#COPY ./demo_app ./demo_app
COPY ./.streamlit ./.streamlit
COPY ./requirements.txt ./requirements.txt

# Update package index and install essential build tools (required for chromadb dependency hnswlib)
RUN apt-get update --fix-missing && apt-get install -y --fix-missing build-essential
RUN pip install -r requirements.txt

#RUN curl https://dl-ssl.google.com/linux/linux_signing_key.pub -o /tmp/google.pub \
#    && cat /tmp/google.pub | apt-key add -; rm /tmp/google.pub \
#    && echo 'deb http://dl.google.com/linux/chrome/deb/ stable main' > /etc/apt/sources.list.d/google.list \
#    && mkdir -p /usr/share/desktop-directories \
#    && apt-get -y update && apt-get install -y google-chrome-stable
# Disable the SUID sandbox so that chrome can launch without being in a privileged container
#RUN dpkg-divert --add --rename --divert /opt/google/chrome/google-chrome.real /opt/google/chrome/google-chrome \
#    && echo "#!/bin/bash\nexec /opt/google/chrome/google-chrome.real --no-sandbox --disable-setuid-sandbox \"\$@\"" #> /opt/google/chrome/google-chrome \
#    && chmod 755 /opt/google/chrome/google-chrome
# 
#RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/115.0.5790.98/linux64/chromedriver-linux64.zip \
#    && unzip chromedriver-linux64.zip \
#    && cp chromedriver-linux64/chromedriver /usr/local/bin/chromedriver

RUN mkdir -p /usr/src/app
RUN mkdir -p /chromadb
CMD ["streamlit", "run", "usr/src/app/main.py", "--server.port", "8080"]
