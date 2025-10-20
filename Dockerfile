# ----------------------------------- NPM ------------------------------------ #

FROM node:20-slim AS node-deps

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
RUN npm run build

# ---------------------------------- Python ---------------------------------- #

FROM python:3.11.4-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

ADD pyproject.toml /app/pyproject.toml
ADD uv.lock /app/uv.lock

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
    && apt-get install -y $buildDeps $deps --no-install-recommends

# Install web app dependencies
RUN uv sync --no-dev --locked

# Remove build dependencies
RUN set -ex \
    && apt-get purge -y --auto-remove $buildDeps \
       $(! command -v gpg > /dev/null || echo 'gnupg dirmngr') \
    && rm -rf /var/lib/apt/lists/*
    
RUN uv cache clean

ENV PATH="/app/.venv/bin:$PATH"

# Copy Node dependencies from node-deps stage
COPY --from=node-deps /app/node_modules /app/node_modules
COPY --from=node-deps /app/package*.json /app/
COPY --from=node-deps /app/static/js/dist/ /app/static/js/dist/

# Copy application files and .env.build
COPY . /app/
COPY ./config/.env.build /app/config/.env
COPY .bashrc /root/

# Compile static assets
RUN uv run manage.py compilescss
RUN uv run manage.py collectstatic --noinput
RUN rm /app/config/.env

EXPOSE 8080
CMD ["uv", "run", "gunicorn", "--bind", ":8080", "--workers", "15", "config.wsgi:application"]
