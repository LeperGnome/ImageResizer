from core.models import Image
from core.forms import UploadForm
from core.tasks import save_image_by_url
from django.http import Http404
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response


upload_template = 'image_upload.html'
list_template = 'image_list.html'
image_view_template = 'image_view.html'


@api_view(['GET'])
def list_images(request):
    images = Image.objects.all()
    return render(request, list_template, {'entries_list': images})


@api_view(['GET'])
def get_image(request, pk):
    image = Image.objects.get_or_none(pk=pk)
    if not image:
        raise Http404
    return render(request, image_view_template, {'image': image})


class Upload(APIView):
    def get(self, request):
        form = UploadForm()
        return render(request, upload_template, {'form': form})

    def post(self, request):
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            img_url = form.cleaned_data.get('url', None)
            img_file = form.cleaned_data.get('img_file', None)

            if img_url:  # if image is uploaded by url
                # adding image saving to celery queue
                save_image_by_url.delay(img_url)
                return Response(data={'detail': 'Image is uploading'})

            elif img_file:  # if image is uploaded by file
                img_object = Image(img_file=img_file)
                img_object.save()
                return Response(data={'detail': 'Image uploaded'})

        else:
            return render(
                request, upload_template,
                {'form': form}, status=400
            )
