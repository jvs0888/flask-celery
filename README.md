## Description
API template with Flask, Celery tasks queue and FlowerUI (monitoring and managing Celery clusters)

---

## How to Run the Service
To start the service, run separately two scripts:

- API (default port :9999) - ```/app/api.py```
- Celery (FlowerUI default port :5555)- ```/celery_run.sh``` This file runs Celery workers and FlowerUI dashboard, if you need to use more workers you need to add them into this file.

Also you can change default ports in setting files ```/settings/*.json```
