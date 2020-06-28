from core.models import Image
from ImageResizer.celery import app


@app.task
def save_image_by_url(url):
    pass
