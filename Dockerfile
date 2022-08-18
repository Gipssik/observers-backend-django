FROM python:3.10.5



RUN pip install poetry==1.1.14
RUN apt-get update &&  \
    apt-get install --no-install-recommends --assume-yes postgresql-client

# Configuring poetry
RUN poetry config virtualenvs.create false

# Copying requirements of a project
COPY pyproject.toml poetry.lock /app/src/
WORKDIR /app/src

# Installing requirements
RUN poetry install --no-dev

# Copying actuall application
COPY . /app/src/

RUN python manage.py collectstatic --noinput -i rest_framework
