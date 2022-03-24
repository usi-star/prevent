FROM python

# Ubuntu building variables.
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# Install Python and utilities.
RUN apt-get update && apt-get -y upgrade && \
    apt-get install -y python3-pip git libblas-dev liblapack-dev libatlas-base-dev gfortran

# Install Pipenv.
RUN pip3 install pipenv

# Prepare the work directory.
RUN mkdir /app
WORKDIR /app

# Install the environment.
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pipenv install --deploy --system

# Copy the source files.
COPY . /app
RUN mkdir -p /app/intermediate/new_training
RUN mkdir -p /app/log

# Exec the main Python file.
ENTRYPOINT ["python3", "ranker_app.py"]
