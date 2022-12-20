ARG PYTHON_VERSION=3.10-slim-bullseye

# define an alias for the specfic python version used in this file.
FROM python:${PYTHON_VERSION} as python

# Python 'run' stage
FROM python as python-run-stage

ARG BUILD_ENVIRONMENT=local
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # psycopg2 dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  # dependencies for building Python packages
  build-essential \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY ./compose/production/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//g' /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./compose/local/django/start.sh /start.sh
RUN sed -i 's/\r$//g' /start.sh
RUN chmod +x /start.sh

COPY ./compose/local/django/celery/start_worker.sh /start_worker.sh
RUN sed -i 's/\r$//g' /start_worker.sh
RUN chmod +x /start_worker.sh

COPY ./compose/local/django/celery/start_beat.sh /start_beat.sh
RUN sed -i 's/\r$//g' /start_beat.sh
RUN chmod +x /start_beat.sh

COPY ./compose/local/django/celery/start_flower.sh /start_flower.sh
RUN sed -i 's/\r$//g' /start_flower.sh
RUN chmod +x /start_flower.sh

# Requirements are installed here to ensure they will be cached.
COPY ./requirements .

# Create Python Dependency and Sub-Dependency Wheels.
RUN pip install -r ${BUILD_ENVIRONMENT}.txt

# copy application code to WORKDIR
COPY . ${APP_HOME}

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/start.sh"]
