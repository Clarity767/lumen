import os
import cloudinary
import cloudinary.uploader

from django.core.files import File
from django import setup

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lumen.settings')
setup()

from restaurant.models import Dish


cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
)


dishes_folder = os.path.join(os.path.dirname(__file__), 'dishes')


for dish in Dish.objects.all():
    if not dish.photo:
        print(f'Пропуск: {dish.name} — фотографии нет')
        continue

    filename = os.path.basename(dish.photo.name)
    local_path = os.path.join(dishes_folder, filename)

    if not os.path.exists(local_path):
        print(f'Файл не найден: {local_path}')
        continue

    print(f'Загрузка: {dish.name} → {filename}')

    with open(local_path, 'rb') as file:
        result = cloudinary.uploader.upload(
            file,
            folder='dishes',
            public_id=os.path.splitext(filename)[0],
            overwrite=True,
        )

    print(f'Готово: {result["secure_url"]}')

print('Все фотографии обработаны!')