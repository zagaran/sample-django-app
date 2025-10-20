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
RUN uv sync --no-group local-dev --no-sources
RUN uv cache clean

# Remove build dependencies
RUN set -ex \
    && apt-get purge -y --auto-remove $buildDeps \
       $(! command -v gpg > /dev/null || echo 'gnupg dirmngr') \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/app/.venv/bin:$PATH"

# Copy application files and .env.build
COPY . /app/
COPY ./config/.env.build /app/config/.env
COPY .bashrc /root/

# Compile static assets
RUN uv run --no-group local-dev --no-sources manage.py compilescss
RUN uv run --no-group local-dev --no-sources manage.py collectstatic --noinput
RUN rm /app/config/.env

EXPOSE 8080
CMD ["uv", "run", "gunicorn", "--bind", ":8080", "--workers", "15", "config.wsgi:application"]
