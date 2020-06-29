from django.core.files.base import ContentFile
from core.models import Image, ResizedImage
import PIL
import requests
from io import BytesIO


def retrieve_image(url: str) -> ContentFile:
    content = BytesIO(requests.get(url).content)

    img = PIL.Image.open(content)
    img_io = BytesIO()
    img.save(img_io, format='JPEG')

    img_file = ContentFile(img_io.getvalue())
    return img_file


def get_resized_image(image, width, height, size):
    #
    # TODO: look for cached images with given parameters
    #       -> create new one and save if none found
    #
    return image
