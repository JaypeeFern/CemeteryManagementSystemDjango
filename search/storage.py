from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import SuspiciousFileOperation
from django.urls import reverse
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivateGraveImageStorage(FileSystemStorage):
    """Store grave images outside the directory used for public media."""

    @property
    def location(self):
        return str(settings.PRIVATE_MEDIA_ROOT)

    def url(self, name):
        # The route enforces account approval and opens the file through this
        # storage, so this URL never exposes a MEDIA_URL path.
        self.path(name)
        return reverse('PrivateGraveImage', kwargs={'name': name})
