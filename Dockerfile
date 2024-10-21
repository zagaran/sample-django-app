# START_FEATURE docker
FROM python:3.11.4-slim-buster

WORKDIR /app

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
    " \
    && apt update && apt install -y $buildDeps $deps --no-install-recommends


# Install python dependencies
ADD requirements.txt /app/requirements.txt
RUN set -ex \
    && pip install --no-cache-dir -r /app/requirements.txt

# Cleanup installs
RUN set -ex \
    && apt purge -y --auto-remove $buildDeps \
       $(! command -v gpg > /dev/null || echo 'gnupg dirmngr') \
    && rm -rf /var/lib/apt/lists/*


ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

# START_FEATURE django_react
# LTS Version of Node
ARG NODE_VERSION=22

# install node
RUN curl -fsSL https://deb.nodesource.com/setup_{$NODE_VERSION}.x | bash -
RUN apt-get update && apt install nodejs -y

COPY ./nwb.config.js /app/nwb.config.js
COPY ./package.json /app/package.json
COPY ./package-lock.json /app/package-lock.json
RUN npm install
# END_FEATURE django_react

COPY . /app/

# Add temporary copy of env file to allow running management commands
COPY ./config/.env.example /app/config/.env

# START_FEATURE django_react
RUN ./node_modules/.bin/nwb build --no-vendor
# END_FEATURE django_react

# START_FEATURE sass_bootstrap
RUN python manage.py compilescss
# END_FEATURE sass_bootstrap

RUN python manage.py collectstatic --noinput

RUN rm /app/config/.env

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "config.wsgi:application", "--access-logfile", "-", "--error-logfile", "-"]
# END_FEATURE docker
