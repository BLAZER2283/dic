import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
app = Celery('dic')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.task_routes = {
    'ucrp.tasks.run_optimization': {'queue': 'ucrp_queue'},
    'dic_api.tasks.process_dic_task': {'queue': 'dic_queue'},
}

app.conf.task_default_queue = 'default'
app.conf.worker_prefetch_multiplier = 1