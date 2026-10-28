---
imported_hash: 836be665d79f7393
title: Overview
summary: mlflow artifacts download \ --run-id ${MODELRUNID} \ --artifact-path model \ --dst-path .
order: 24
kind: reading
section: Deployment / Web service mlflow
source: learn-ai-engineering/data-engineering/DataTalks MLOps/04-deployment/web-service-mlflow/README.md
---

## Getting the model for deployment from MLflow

* Take the code from the previous video
* Train another model, register with MLflow
* Put the model into a scikit-learn pipeline
* Model deployment with tracking server
* Model deployment without the tracking server

Starting the MLflow server with S3:

```bash
mlflow server \
    --backend-store-uri=sqlite:///mlflow.db \
    --default-artifact-root=s3://mlflow-models-alexey/
```

Downloading the artifact

```bash
export MLFLOW_TRACKING_URI="http://127.0.0.1:5000"
export MODEL_RUN_ID="6dd459b11b4e48dc862f4e1019d166f6"

mlflow artifacts download \
    --run-id ${MODEL_RUN_ID} \
    --artifact-path model \
    --dst-path .
```
