from django.db import models


class RequestThrottleBucket(models.Model):
    bucket_key = models.CharField(max_length=64, primary_key=True)
    count = models.PositiveIntegerField(default=1)
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = 'home_request_throttle_bucket'
