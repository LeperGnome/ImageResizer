from django.core.files import File
import time
import PIL
import requests
from io import BytesIO


def retrieve_image(url):
    content = requests.get(url).content
    img = PIL.Image.open(BytesIO(content))
    # raises exception if file is not an image
    img.verify()

    return File(img)


def generate_image_name():
    return f'image_{time.time()}'
