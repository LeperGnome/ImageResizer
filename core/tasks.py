from core.models import Image
from core.utils import retrieve_image
from ImageResizer.celery import app


@app.task
def save_image_by_url(url):
    res_file = retrieve_image(url)
    img_object = Image(img_file=res_file)
    img_object.save()
