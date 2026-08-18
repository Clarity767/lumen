from django.core.management.base import BaseCommand
from restaurant.models import Category, Table, Dish


class Command(BaseCommand):
    help = 'Наповнює базу тестовими даними: категорії, столики, страви'

    def handle(self, *args, **kwargs):
        # Категорії для столиків
        cat_window, _ = Category.objects.get_or_create(name='У вікна', slug='window', type='table')
        cat_vip, _ = Category.objects.get_or_create(name='VIP', slug='vip', type='table')
        cat_terrace, _ = Category.objects.get_or_create(name='Тераса', slug='terrace', type='table')

        # Категорії для страв
        cat_soup, _ = Category.objects.get_or_create(name='Супи', slug='soups', type='dish')
        cat_main, _ = Category.objects.get_or_create(name='Основні страви', slug='main', type='dish')
        cat_dessert, _ = Category.objects.get_or_create(name='Десерти', slug='desserts', type='dish')
        cat_drinks, _ = Category.objects.get_or_create(name='Напої', slug='drinks', type='dish')

        tables = [
            {'title': 'Столик №1', 'description': 'Затишний столик біля вікна з видом на вулицю.', 'price': 150, 'category': cat_window, 'seats': 2},
            {'title': 'Столик №2', 'description': 'Просторий столик для компанії до 4 осіб.', 'price': 200, 'category': cat_window, 'seats': 4},
            {'title': 'VIP-кабінет №1', 'description': 'Приватний кабінет з окремим входом та обслуговуванням.', 'price': 500, 'category': cat_vip, 'seats': 6},
            {'title': 'VIP-кабінет №2', 'description': 'Розкішний кабінет для особливих подій.', 'price': 600, 'category': cat_vip, 'seats': 8},
            {'title': 'Тераса №1', 'description': 'Столик на відкритій терасі з видом на сад.', 'price': 180, 'category': cat_terrace, 'seats': 2},
            {'title': 'Тераса №2', 'description': 'Великий стіл на терасі для компанії друзів.', 'price': 250, 'category': cat_terrace, 'seats': 6},
        ]

        for t in tables:
            Table.objects.get_or_create(
                title=t['title'],
                defaults={
                    'description': t['description'],
                    'price': t['price'],
                    'category': t['category'],
                    'seats': t['seats'],
                    'is_available': True,
                }
            )

        dishes = [
            {'name': 'Борщ український', 'description': 'Класичний борщ з м\'ясом та сметаною.', 'price': 95, 'category': cat_soup},
            {'name': 'Крем-суп з грибів', 'description': 'Ніжний суп-пюре з лісових грибів.', 'price': 85, 'category': cat_soup},
            {'name': 'Стейк з лосося', 'description': 'Стейк на грилі з овочами.', 'price': 320, 'category': cat_main},
            {'name': 'Паста Карбонара', 'description': 'Класична італійська паста з беконом.', 'price': 210, 'category': cat_main},
            {'name': 'Куряче філе гриль', 'description': 'Соковите куряче філе з гарніром.', 'price': 180, 'category': cat_main},
            {'name': 'Тірамісу', 'description': 'Класичний італійський десерт.', 'price': 110, 'category': cat_dessert},
            {'name': 'Чізкейк Нью-Йорк', 'description': 'Ніжний чізкейк з ягідним соусом.', 'price': 120, 'category': cat_dessert},
            {'name': 'Лимонад домашній', 'description': 'Освіжаючий лимонад з м\'ятою.', 'price': 60, 'category': cat_drinks},
            {'name': 'Кава American', 'description': 'Класична чорна кава.', 'price': 45, 'category': cat_drinks},
            {'name': 'Свіжовичавлений сік', 'description': 'Апельсиновий або яблучний сік.', 'price': 70, 'category': cat_drinks},
        ]

        for d in dishes:
            Dish.objects.get_or_create(
                name=d['name'],
                defaults={
                    'description': d['description'],
                    'price': d['price'],
                    'category': d['category'],
                    'is_available': True,
                }
            )

        self.stdout.write(self.style.SUCCESS('Тестові дані успішно додано!'))