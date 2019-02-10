from celery import Celery
from utils.fileChecker import fileChecker
import os
app = Celery('', broker= 'redis://localhost:6379/0')
@app.task
def run_check():
    try:
        os.chdir('./utils')
    except:
        pass
    fileChecker()