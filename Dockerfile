FROM python:3.11-trixie

# reduces file creation
ENV PYTHONDONTWRITEBYTECODE=1
# disables output buffering so logs are flushed to console
ENV PYTHONUNBUFFERED=1

FROM node:24-slim AS node-deps

WORKDIR /app

# Install required system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends bzip2

# Add only files needed for dependency installation
COPY package.json ./

# Install Node dependencies with caching
RUN npm install && npm cache clean --force

# Build vue dist
COPY . /app/
RUN npm run vue-build

# END_FEATURE vue
# ---------------------------------- Python ---------------------------------- #

FROM python:3.12.13-slim-trixie

# Set working directory
WORKDIR /app

# LTS Version of Node is 22
ARG NODE_VERSION=22
# START_FEATURE django_react
# if using nwb, nwb requires Node 16. TODO remove nwb
ARG NODE_VERSION=16
# END_FEATURE django_react
# install node
RUN curl -fsSL https://deb.nodesource.com/setup_{$NODE_VERSION}.x | bash -
RUN apt-get update && apt install nodejs -y

# Install system and python dependencies
RUN set -ex \
    && buildDeps=" \
      build-essential \
      libpq-dev \
    " \
    && deps=" \
      curl \
      vim \
      nano \
      procps \
      postgresql-client \
      git \
      # (editing)
      vim \
      # (debug)
      curl \
      htop \
    " \
    && apt-get update && apt-get install -y $buildDeps $deps --no-install-recommends

# Create Django user to avoid running as root
ARG UID=1000
ARG GID=1000
ARG CREATE_GROUP=True

RUN if [ "$CREATE_GROUP" = "True" ]; then groupadd -g ${GID} django; fi
RUN useradd -m django -u ${UID} -g ${GID}
RUN chown -R ${UID}:${GID} /app


# Add bash config for ssh
RUN echo 'alias db="python manage.py shell_plus"' >> "/root/.bashrc"
RUN echo 'alias db="python manage.py shell_plus"' >> "/home/django/.bashrc"

RUN echo '\
"\e[A":history-search-backward \n\
"\e[B":history-search-forward' \
>> "/root/.inputrc"
RUN echo '\
"\\e[A":history-search-backward \n\
"\\e[B":history-search-forward' \
>> "/home/django/.inputrc"

# Install python dependencies
ADD requirements.txt /app/requirements.txt
RUN set -ex \
    && pip install --no-cache-dir -r /app/requirements.txt

# Generate self-signed SSL cert for E2E encryption
# Note: after pip install so that it will regenerate at same frequency
RUN mkdir -p /etc/pki/tls/certs
RUN openssl req -x509 -newkey rsa:4096 -keyout /etc/pki/tls/certs/server.key -out /etc/pki/tls/certs/server.crt -days 3650 -nodes -subj "/CN=*.mbta.com"
RUN chmod -R a+rX /etc/pki

# Cleanup installs
RUN set -ex \
    && apt purge -y --auto-remove $buildDeps \
       $(! command -v gpg > /dev/null || echo 'gnupg dirmngr') \
    && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/env
ENV PATH=/env/bin:$PATH

# START_FEATURE django_react
COPY ./nwb.config.js /app/nwb.config.js
# END_FEATURE django_react
COPY ./package.json /app/package.json
COPY ./package-lock.json /app/package-lock.json
RUN npm install

# Copy project files into the container
COPY . /app/
# Add temporary copy of env file to allow running management commands
COPY ./config/.env.build /app/config/.env

# Compile static assets
# START_FEATURE sass_bootstrap
RUN python manage.py compilescss
# END_FEATURE sass_bootstrap
RUN python manage.py collectstatic --noinput
RUN rm /app/config/.env

# Remove node_modules to save space
RUN rm -rf /app/node_modules

# Remove system dependencies (reduce size)
RUN set -ex \
    && apt purge -y --auto-remove $buildDeps $(! command -v gpg > /dev/null || echo 'gnupg dirmngr') \
    && rm -rf /var/lib/apt/lists/*

# Set user to avoid running container command as root
USER django

EXPOSE 8080

CMD ["gunicorn", "--bind", ":8080", "--certfile=/etc/pki/tls/certs/server.crt", "--keyfile=/etc/pki/tls/certs/server.key", "--workers", "2", "--threads", "5", "config.wsgi:application", "--access-logfile", "-", "--error-logfile", "-"]
