from celery import Celery
from fileChecker import fileChecker
app = Celery('', broker= 'redis://localhost:6379/0')
@app.task
def run_check():
    fileChecker()
    