from celery import Celery
from flask import g
def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL']
        #we don't need to store results so no need for backend
    )
    class ContextTask(celery.Task):
        def __call__(self,*args,**kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery