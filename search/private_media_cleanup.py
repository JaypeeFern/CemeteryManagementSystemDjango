import json
import os
import hashlib
from pathlib import Path
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.core.files.storage import FileSystemStorage


PENDING_PUBLIC_GRAVE_IMAGE_DELETIONS = '.pending-public-grave-images'


def _manifest_path():
    return Path(settings.PRIVATE_MEDIA_ROOT) / PENDING_PUBLIC_GRAVE_IMAGE_DELETIONS


def record_public_grave_image_for_deletion(name):
    public_storage = FileSystemStorage(location=settings.MEDIA_ROOT)
    public_storage.path(name)

    pending_directory = _manifest_path()
    pending_directory.mkdir(parents=True, exist_ok=True)
    marker_name = f'{hashlib.sha256(name.encode("utf-8")).hexdigest()}.json'
    marker_path = pending_directory / marker_name

    with NamedTemporaryFile('w', encoding='utf-8', dir=pending_directory, delete=False) as temporary_file:
        temporary_path = Path(temporary_file.name)
        json.dump(name, temporary_file)

    os.replace(temporary_path, marker_path)


def cleanup_pending_public_grave_images():
    pending_directory = _manifest_path()
    if not pending_directory.exists():
        return 0

    public_storage = FileSystemStorage(location=settings.MEDIA_ROOT)
    deleted_count = 0
    for marker_path in pending_directory.glob('*.json'):
        name = json.loads(marker_path.read_text(encoding='utf-8'))
        if not isinstance(name, str):
            raise ValueError('Pending grave-image cleanup marker is invalid.')
        public_storage.path(name)
        public_storage.delete(name)
        try:
            marker_path.unlink()
        except FileNotFoundError:
            pass
        deleted_count += 1

    try:
        pending_directory.rmdir()
    except OSError:
        pass

    return deleted_count
