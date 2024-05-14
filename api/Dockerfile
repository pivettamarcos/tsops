FROM python:3.9-slim

WORKDIR /app

COPY /api/requirements.txt /tmp
RUN --mount=type=cache,target=/root/.cache/pip \
        pip install --upgrade pip && \
        pip install -r /tmp/requirements.txt

COPY /api/app /app
COPY ../mlflow_projects/ts-forecast /app/ts-forecast

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# cd ..
# docker build -f api/Dockerfile -t api-tsops .
# docker run -p 8000:8000 api-tsops 