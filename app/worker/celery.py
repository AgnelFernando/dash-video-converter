import os
from celery import Celery

from debugger import initialize_celery_worker_debugger_if_needed

initialize_celery_worker_debugger_if_needed()

app = Celery(__name__, include=['worker.tasks'])
app.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
app.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

if __name__ == '__main__':
    app.start()