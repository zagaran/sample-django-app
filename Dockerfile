# START_FEATURE docker
FROM python:3.8.8-slim-buster

WORKDIR /app

ADD requirements.txt /app/requirements.txt

RUN set -ex \
    && buildDeps=" \
      build-essential \
      libpq-dev \
    " \
    && deps=" \
      postgresql-client-11 \
    " \
    && apt-get update && apt-get install -y $buildDeps $deps --no-install-recommends \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && apt-get purge -y --auto-remove $buildDeps \
       $(! command -v gpg > /dev/null || echo 'gnupg dirmngr') \
    && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

COPY . /app/

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "config.wsgi:application"]
# END_FEATURE docker