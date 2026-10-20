from django.core.exceptions import ValidationError


MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024
UPLOAD_SIZE_ERROR_MESSAGE = 'Uploaded files must be 5 MB or smaller.'


def validate_upload_size(upload):
    if upload.size > MAX_UPLOAD_SIZE_BYTES:
        raise ValidationError(UPLOAD_SIZE_ERROR_MESSAGE)
