from django.http import HttpResponse

from .upload_validation import UPLOAD_SIZE_ERROR_MESSAGE


class UploadSizeLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if getattr(request, 'upload_too_large', False):
            return HttpResponse(UPLOAD_SIZE_ERROR_MESSAGE, status=413)
        return response
