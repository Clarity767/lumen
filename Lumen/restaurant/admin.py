from django.contrib import admin
from .models import Profile, Category, Table, Dish, Booking, BookingItem, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'seats', 'is_available')
    list_filter = ('is_available', 'category')

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'is_available')
    list_filter = ('is_available', 'category')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'table', 'booking_date', 'status', 'total_price')
    list_filter = ('status',)

admin.site.register(Profile)
admin.site.register(BookingItem)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('dish', 'user', 'rating', 'created_at')
    list_filter = ('rating',)