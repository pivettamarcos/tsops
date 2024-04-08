FROM ghcr.io/mlflow/mlflow:v2.11.3
# Install python packages
COPY requirements.txt /tmp
RUN --mount=type=cache,target=/root/.cache/pip \
        pip install --upgrade pip && \
        pip install -r /tmp/requirements.txt
