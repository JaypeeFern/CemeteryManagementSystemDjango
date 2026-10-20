from django.core.files.uploadhandler import FileUploadHandler, StopUpload

from .upload_validation import MAX_UPLOAD_SIZE_BYTES


class UploadSizeLimitHandler(FileUploadHandler):
    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        self.uploaded_bytes = 0

    def receive_data_chunk(self, raw_data, start):
        self.uploaded_bytes += len(raw_data)
        if self.uploaded_bytes > MAX_UPLOAD_SIZE_BYTES:
            self.request.upload_too_large = True
            raise StopUpload(connection_reset=True)
        return raw_data

    def file_complete(self, file_size):
        return None
