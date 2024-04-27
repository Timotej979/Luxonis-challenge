# Build arguments
ARG APP_PYTHON_VERSION=3.10.14-alpine3.19
ARG APP_POETRY_VERSION=1.8.0

FROM python:${APP_PYTHON_VERSION}

###################### Add dependencies for different DB connectors if needed and install poetry ######################
RUN apk update && \ 
    apk add --no-cache \
        curl \
        postgresql-client \
        postgresql-contrib && \
    python -m pip install --upgrade pip && \
    curl -sSL https://install.python-poetry.org | python3 - --version=${APP_POETRY_VERSION}

###################### Add local path ###################### 
ENV PATH=/root/.local/bin:$PATH

###################### Set workdir in docker container and copy files over ###################### 
WORKDIR /app
COPY pyproject.toml ./

###################### Configure poetry and install desired packages ######################
RUN poetry config virtualenvs.in-project true --local && \
    poetry install --only main

###################### Copy python files over ######################
COPY . /app
