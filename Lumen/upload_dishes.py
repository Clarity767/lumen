import os
import django
import cloudinary
import cloudinary.uploader

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lumen.settings')
django.setup()

from restaurant.models import Dish

cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
)

dishes_folder = os.path.join(os.path.dirname(__file__), 'dishes')

for dish in Dish.objects.all():
    if not dish.photo:
        print(f'Пропуск: {dish.name} — фото нет')
        continue

    filename = os.path.basename(dish.photo.name)
    local_path = os.path.join(dishes_folder, filename)

    if not os.path.exists(local_path):
        print(f'Файл не найден: {local_path}')
        continue

    public_id = os.path.splitext(filename)[0]

    print(f'Загрузка: {filename}')

    with open(local_path, 'rb') as file:
        result = cloudinary.uploader.upload(
            file,
            folder='dishes',
            public_id=public_id,
            overwrite=True
        )

    print(f'OK: {result["secure_url"]}')

print('Готово!')