from pathlib import Path
import celery.exceptions
from celery.contrib.abortable import AbortableAsyncResult
from flask import Flask, Response, jsonify, abort
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth

try:
    from loggers.logger import logger
    from settings.config import config
    from app.celery_task import celery, worker, services
except ImportError as ie:
    exit(f'{ie} :: {Path(__file__).resolve()}')


app: Flask = Flask(__name__)
api: Api = Api(app, prefix="/")

auth: HTTPBasicAuth = HTTPBasicAuth()

@auth.verify_password
def authenticate(username, password) -> bool:
    if all((username, password)):
        if username == config.API_USER and password == config.API_PASS:
            return True
    else:
        return False

@app.url_value_preprocessor
def service_validate(endpoint: str | None, values: dict | None) -> None:
    if values and 'service' in values:
        service: str = values['service']
        if service not in services:
            abort(code=404, description='unknown service')

def get_celery_tasks(service: str) -> str | None:
    active_tasks: dict = celery.control.inspect().active()

    if not active_tasks:
        return

    for task_values in active_tasks.values():
        for task_value in task_values:
            if service in task_value.get('kwargs', {}).values():
                return task_value.get('id', None)


class Start(Resource):
    @auth.login_required
    def get(self, service: str) -> Response:
        if get_celery_tasks(service=service):
            abort(code=409, description='service already running')

        result: AbortableAsyncResult = worker.apply_async(kwargs={'service': service})
        if result.state == 'FAILURE':
            abort(code=500, description='failed to start service')

        return jsonify({'message': 'service running'})


class Stop(Resource):
    @auth.login_required
    def get(self, service: str) -> Response:
        task_id: str | None = get_celery_tasks(service=service)

        if task_id:
            result: AbortableAsyncResult = worker.AsyncResult(task_id)

            try:
                result.abort()
                if not result.is_aborted():
                    raise celery.exceptions.TaskRevokedError
            except Exception:
                logger.error(f'failed to abort task :: {task_id}')
                abort(code=500, description='failed to stop service')

        return jsonify({'message': 'service stopped'})


api.add_resource(Start, '/start/<string:service>')
api.add_resource(Stop, '/stop/<string:service>')


if __name__ == '__main__':
    app.run(**config.api)

