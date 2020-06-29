from django.core.files.base import ContentFile
import time
import PIL
import requests
from io import BytesIO


def retrieve_image(url):
    content = BytesIO(requests.get(url).content)

    img = PIL.Image.open(content)
    img_io = BytesIO()
    img.save(img_io, format='JPEG')

    img_file = ContentFile(img_io.getvalue())
    return img_file


def generate_image_name():
    return f'image_{time.time()}'
