from core.models import Image
from core.utils import retrieve_image, generate_image_name
from ImageResizer.celery import app


@app.task
def save_image_by_url(url):
    res_file = retrieve_image(url)
    img_object = Image()
    img_object.img_file.save(content=res_file, name=generate_image_name())
