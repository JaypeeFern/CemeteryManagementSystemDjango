from django.core.management.base import BaseCommand

from search.private_media_cleanup import cleanup_pending_public_grave_images


class Command(BaseCommand):
    help = 'Retry removing public grave-image copies left by an interrupted migration.'

    def handle(self, *args, **options):
        deleted_count = cleanup_pending_public_grave_images()
        self.stdout.write(f'Removed {deleted_count} pending public grave-image copies.')
