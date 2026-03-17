# START_FEATURE ecs
# START_FEATURE vue
# ----------------------------------- NPM ------------------------------------ #

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

ADD requirements.txt /app/requirements.txt

# Install system and python dependencies
RUN set -ex \
    && buildDeps=" \
      build-essential \
      libpq-dev \
    " \
    && deps=" \
      postgresql-client \
      git \
      # (editing)
      vim \
      # (debug)
      curl \
      htop \
    " \
    && apt-get update \
    && apt-get install -y $buildDeps $deps --no-install-recommends \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && apt-get purge -y --auto-remove $buildDeps \
       $(! command -v gpg > /dev/null || echo 'gnupg dirmngr') \
    && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

# START_FEATURE vue
# Copy Node dependencies from node-deps stage
COPY --from=node-deps /app/node_modules /app/node_modules
COPY --from=node-deps /app/package*.json /app/
COPY --from=node-deps /app/static/js/dist/ /app/static/js/dist/
# END_FEATURE vue

# Copy application files and .env.example
COPY . /app/
COPY ./config/.env.example /app/config/.env
COPY .bashrc /root/

# Compile static assets
# START_FEATURE sass_bootstrap
RUN python manage.py compilescss
# END_FEATURE sass_bootstrap
RUN python manage.py collectstatic --noinput
RUN rm /app/config/.env

EXPOSE 8080
CMD ["gunicorn", "--bind", ":8080", "--workers", "15", "config.wsgi:application"]
# END_FEATURE ecs
