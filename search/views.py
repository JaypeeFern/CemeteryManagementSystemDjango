import mimetypes

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import SuspiciousFileOperation
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import DeceasedInformation
from .storage import PrivateGraveImageStorage

# Create your views here.

@login_required(login_url='Home')
def RenderDeceasedSearch(request):
    return render(request, "search/index.html", {
        'data': DeceasedInformation.objects.all()
    })
   
@login_required(login_url='Home')
def tables(request):
    return render(request, "search/tables.html")


def _grave_image_response(name):
    storage = PrivateGraveImageStorage()
    content_type, _ = mimetypes.guess_type(name)
    if content_type not in {
        'image/bmp',
        'image/gif',
        'image/jpeg',
        'image/png',
        'image/tiff',
        'image/webp',
    }:
        raise Http404

    try:
        image_file = storage.open(name, 'rb')
    except (FileNotFoundError, SuspiciousFileOperation, ValueError):
        raise Http404

    response = FileResponse(image_file, content_type=content_type)
    response['Cache-Control'] = 'private, no-store'
    response['X-Content-Type-Options'] = 'nosniff'
    return response


@user_passes_test(
    lambda user: user.is_authenticated and user.is_active,
    login_url='Home',
)
def private_grave_image(request, name):
    return _grave_image_response(name)


@user_passes_test(
    lambda user: user.is_authenticated and user.is_active,
    login_url='Home',
)
def private_grave_image_for_record(request, pk):
    deceased = get_object_or_404(DeceasedInformation, pk=pk)
    if not deceased.graveimage:
        raise Http404
    return _grave_image_response(deceased.graveimage.name)
