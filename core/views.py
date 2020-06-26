from core.models import Image
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def list_images(request):
    images = Image.objects.all()
    return render(request, 'image_list.html', {'entries_list': images})


@api_view()
def get_image(request):
    pass


class Upload(APIView):
    def get(self, request):
        pass

    def post(self, request):
        pass
