from django.core.files.base import ContentFile
from core.models import Image, ResizedImage, generate_image_name
import PIL
import requests
from io import BytesIO


def pil_to_django(image) -> ContentFile:
    img_io = BytesIO()
    image.save(img_io, format='JPEG')
    img_file = ContentFile(img_io.getvalue())
    return img_file


def retrieve_image(url: str) -> ContentFile:
    content = BytesIO(requests.get(url).content)
    img = PIL.Image.open(content)
    return pil_to_django(img)


def get_resized_image(image, width, height, size):
    def int_or_default(param, param_string):
        default = getattr(image.img_file, param_string)
        try:
            param = int(param)
            if param <= 0:
                param = default
        except:
            param = default
        return param

    width = int_or_default(width, 'width')
    height = int_or_default(height, 'height')
    size = int_or_default(size, 'size')

    # check if base image suits conditions
    if width == image.img_file.width \
            and height == image.img_file.height \
            and size >= image.img_file.size:
        return image

    # looking for cached image
    cached_image = ResizedImage.objects.filter(
        base=image, width=width, height=height, size__lte=size)
    if cached_image:
        return cached_image[0]

    # performing resize
    pil_image = PIL.Image.open(image.img_file.path)
    resized_image = pil_image.resize(size=(width, height))

    # saving new image
    django_image = pil_to_django(resized_image)
    new_resized_image = ResizedImage(
        base=image,
        width=width,
        height=height,
        size=django_image.size
    )
    new_resized_image.img_file.save(
        content=django_image, name=generate_image_name())

    return new_resized_image
