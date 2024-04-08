FROM jupyter/datascience-notebook
# Install python packages
COPY requirements.txt /tmp
RUN --mount=type=cache,target=/root/.cache/pip \
        pip install --upgrade pip && \
        pip install -r /tmp/requirements.txt

#COPY . /app