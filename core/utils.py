from django.core.files.base import ContentFile
from core.models import Image, ResizedImage, generate_image_name
import PIL
import requests
from io import BytesIO


class file_counter(object):
    def __init__(self):
        self.position = self.size = 0

    def seek(self, offset, whence=0):
        if whence == 1:
            offset += self.position
        elif whence == 2:
            offset += self.size
        self.position = min(offset, self.size)

    def tell(self):
        return self.position

    def write(self, string):
        self.position += len(string)
        self.size = max(self.size, self.position)


def optimal_quality(im, size, guess=70, subsampling=1, low=1, high=100):
    while low < high:
        counter = file_counter()
        im.save(counter, format='JPEG', subsampling=subsampling, quality=guess)
        if counter.size < size:
            low = guess
        else:
            high = guess - 1
        guess = (low + high + 1) // 2
    return low


def pil_to_django(image, quality=100, subsampling=1) -> ContentFile:
    img_io = BytesIO()
    image.save(img_io, format='JPEG', quality=quality, subsampling=subsampling)
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
    cached_images = ResizedImage.objects.filter(
        base=image, width=width, height=height, size=size)
    if cached_images:
        return cached_images.order_by('-size')[0]

    # performing resize
    pil_image = PIL.Image.open(image.img_file.path)
    resized_image = pil_image.resize(size=(width, height))
    django_image = pil_to_django(resized_image)

    # quality reduction to fit size
    if django_image.size >= size:
        quality = optimal_quality(resized_image, size)
        django_image = pil_to_django(resized_image, quality=quality)

    # saving new image
    new_resized_image = ResizedImage(
        base=image,
        width=width,
        height=height,
        size=django_image.size
    )
    new_resized_image.img_file.save(
        content=django_image, name=generate_image_name())

    return new_resized_image
