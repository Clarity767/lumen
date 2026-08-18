from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime, timedelta
import random
import string
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Профіль'
        verbose_name_plural = 'Профілі'

class Category(models.Model):
    TYPE_CHOICES = [
        ('table', 'Столик'),
        ('dish', 'Страва'),
    ]
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'

    def __str__(self):
        return self.name


class Table(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='tables/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    seats = models.PositiveIntegerField(default=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Столик'
        verbose_name_plural = 'Столики'


class Dish(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.ImageField(upload_to='dishes/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Страва'
        verbose_name_plural = 'Страви'

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
    ('pending', 'Очікує'),
    ('confirmed', 'Підтверджено'),
    ('paid', 'Оплачено'),
    ('cancelled', 'Скасовано'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(
        default=120,
        help_text='Тривалість бронювання в хвилинах (за замовчуванням 2 години)'
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    promo_code = models.OneToOneField(
        'GamePromoCode', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='used_in_booking',
    )
    promo_discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    def overlaps_with(self, other_date, other_time, other_duration):
        if self.booking_date != other_date:
            return False
        start1 = datetime.combine(self.booking_date, self.booking_time)
        end1 = start1 + timedelta(minutes=self.duration_minutes)
        start2 = datetime.combine(other_date, other_time)
        end2 = start2 + timedelta(minutes=other_duration)
        return start1 < end2 and start2 < end1
    def __str__(self):
        return f"{self.user} — {self.table} ({self.booking_date})"
    
    class Meta:
        verbose_name = 'Бронювання'
        verbose_name_plural = 'Бронювання'


class BookingItem(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.dish} x{self.quantity}"
    
    class Meta:
        verbose_name = 'Позиція бронювання'
        verbose_name_plural = 'Позиції бронювання'


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікує оплати'),
        ('success', 'Оплачено'),
        ('failed', 'Помилка оплати'),
    ]
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Оплата #{self.id} — {self.booking}"

    class Meta:
        verbose_name = 'Оплата'
        verbose_name_plural = 'Оплати'

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender} → {self.receiver}: {self.text[:30]}'

    class Meta:
        verbose_name = 'Повідомлення'
        verbose_name_plural = 'Повідомлення'
        ordering = ['created_at']


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Відгук'
        verbose_name_plural = 'Відгуки'
        unique_together = ('dish', 'user')  
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.dish.name} ({self.rating}★)'
    



class GamePromoCode(models.Model):
    REWARD_CHOICES = [
        ('drink', 'Безкоштовний напій'),
        ('dish', 'Безкоштовна страва'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='promo_codes')
    code = models.CharField(max_length=20, unique=True)
    score = models.PositiveIntegerField()
    reward_type = models.CharField(max_length=10, choices=REWARD_CHOICES)
    reward_description = models.CharField(max_length=200)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # NEW
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.code} ({self.user})'

    @staticmethod
    def generate_code():
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not GamePromoCode.objects.filter(code=code).exists():
                return code