import os
from django.core.management.base import BaseCommand
from django.core.files import File
from restaurant.models import Dish, Table, Profile


class Command(BaseCommand):
    help = 'Uploads local media files to Cloudinary based on existing DB paths'

    def add_arguments(self, parser):
        parser.add_argument(
            '--media-root',
            type=str,
            required=True,
            help='Path to the local media folder that still has the files',
        )

    def handle(self, *args, **options):
        media_root = options['media_root']

        self.process_model(Dish, 'photo', media_root)
        self.process_model(Table, 'image', media_root)
        self.process_model(Profile, 'avatar', media_root)

    def process_model(self, model, field_name, media_root):
        self.stdout.write(f'--- Processing {model.__name__}.{field_name} ---')
        for obj in model.objects.all():
            field = getattr(obj, field_name)
            if not field:
                continue

            relative_path = str(field)
            local_path = os.path.join(media_root, relative_path)

            if not os.path.exists(local_path):
                self.stdout.write(self.style.WARNING(
                    f'  [SKIP] {model.__name__} id={obj.pk}: file not found at {local_path}'
                ))
                continue

            filename = os.path.basename(local_path)
            with open(local_path, 'rb') as f:
                getattr(obj, field_name).save(filename, File(f), save=True)

            self.stdout.write(self.style.SUCCESS(
                f'  [OK] {model.__name__} id={obj.pk}: uploaded {filename}'
            ))