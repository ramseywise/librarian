---
imported_hash: 3e3f34c82ba25e11
title: Overview
summary: ''
order: 23
kind: reading
section: Deployment / Web service
source: learn-ai-engineering/data-engineering/DataTalks MLOps/04-deployment/web-service/README.md
---

## Deploying a model as a web-service

* Creating a virtual environment with Pipenv
* Creating a script for predictiong
* Putting the script into a Flask app
* Packaging the app to Docker


```bash
docker build -t ride-duration-prediction-service:v1 .
```

```bash
docker run -it --rm -p 9696:9696  ride-duration-prediction-service:v1
```
