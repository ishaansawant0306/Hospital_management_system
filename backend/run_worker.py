import eventlet
eventlet.monkey_patch()

from celery_worker import celery

if __name__ == '__main__':
    celery.worker_main(['worker', '--loglevel=info', '--pool=eventlet'])
