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


def optimal_quality(im, size, guess=100, subsampling=1, low=1, high=100) -> int:
    '''
    Binary search algorithm for finding optimal quality compression rate 
    in order to suit maximum size. If desired size is not achived 
    that returns closest possible 

    Args:
        im: (PIL.Image) image object
        size: (int) desired size in bytes
        guess: (int) number of guesses
        subsampling: (int) subsampling rate
        low: (int) lowest acceptable quality
        high: (int) highest acceptable quality

    Returns:
        int - most suitable quality (or lowest if desired size is not achieved)
    '''
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
    '''
    Converts PIL image to django ContentFile

    Args:
        image: (PIL.Image)
        quality: (int) compression rate (100 returns original)
        subsampling: (int) subsampling rate

    Returns:
        Image as ContentFile
    '''
    img_io = BytesIO()
    image.save(img_io, format='JPEG', quality=quality, subsampling=subsampling)
    img_file = ContentFile(img_io.getvalue())
    return img_file


def retrieve_image(url: str) -> ContentFile:
    '''
    Downloads image and returns django ContentFile

    Args:
        url: image url

    Returns:
        Image as ContentFile

    Raises:
        different connection errors
    '''
    content = BytesIO(requests.get(url).content)
    img = PIL.Image.open(content)
    return pil_to_django(img)


def get_resized_image(image, width, height, size):
    '''
    Resizes incoming image to resolution (width, height) and compresses to (size).
    Functions uses cached images (ResizedImage) to not generate identical images.
    If desired size in unachievable - size sets to be lowest possible
    If size is not set, ResizedImage will contain size of original image, 
    even if ResizedImage actuall size is different

    Args:
        image: (core.models.Image) Image model object
        width: (int) width to set
        heigth: (int) heigth to set
        size:(int) size in bytes to compress to

    Returns:
        Image or ResizedImage - objects of django models. 
        Image is returned when all parameters suit original image
        ResizedImage is returned otherwise
    '''
    def int_or_default(param, param_string):
        default = getattr(image.img_file, param_string)
        try:
            param = int(param)
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
        size=size
    )
    new_resized_image.img_file.save(
        content=django_image, name=generate_image_name())

    return new_resized_image
