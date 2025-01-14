#!/bin/bash

source settings/.env

celery -A base.celery_task.celery worker -c 1 -l info -Q scraper_queue -n scraper_worker_1 &
WORKER_PID_1=$!
celery -A base.celery_task.celery worker -c 1 -l info -Q scraper_queue -n scraper_worker_2 &
WORKER_PID_2=$!

celery -A base.celery_task.celery flower --port=5555 --basic_auth=$FLOWER_USER:$FLOWER_PASS &
FLOWER_PID=$!

trap "kill $WORKER_PID_1 $WORKER_PID_2 $FLOWER_PID" SIGINT

wait $WORKER_PID_1
wait $WORKER_PID_2
wait $FLOWER_PID
