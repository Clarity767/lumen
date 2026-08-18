from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Booking, Dish, Profile, Review, GamePromoCode
from django.utils import timezone
from datetime import datetime, time as dt_time



class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']



class BookingForm(forms.ModelForm):
    promo_code = forms.CharField(
        required=False,
        label='Промокод з гри',
        widget=forms.TextInput(attrs={'placeholder': 'Наприклад: A1B2C3D4', 'class': 'form-control'}),
    )

    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'duration_minutes']
        widgets = {
            'booking_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'min': timezone.localdate().isoformat(),
                },
            ),
            'booking_time': forms.TimeInput(
                format='%H:%M',
                attrs={
                    'type': 'time',
                    'class': 'form-control',
                    'step': 900,
                },
            ),
            'duration_minutes': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 30, 'step': 15}
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_booking_date(self):
        date = self.cleaned_data['booking_date']
        if date < timezone.localdate():
            raise forms.ValidationError('Не можна забронювати столик на минулу дату.')
        return date

    def clean(self):
        cleaned = super().clean()
        date = cleaned.get('booking_date')
        time_ = cleaned.get('booking_time')
        if date and time_ and date == timezone.localdate():
            if time_ < timezone.localtime().time():
                raise forms.ValidationError('Обраний час вже минув на сьогодні.')
        return cleaned

    def clean_promo_code(self):
        code = self.cleaned_data.get('promo_code', '').strip().upper()
        if not code:
            return None

        try:
            promo = GamePromoCode.objects.get(code=code, user=self.user)
        except GamePromoCode.DoesNotExist:
            raise forms.ValidationError('Такого промокоду не існує або він належить іншому користувачу.')

        if promo.is_used:
            raise forms.ValidationError('Цей промокод вже використано.')

        return promo



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'phone', 'bio']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+380...'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }




class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ваш відгук про страву...'}),
        }



class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ваше ім'я"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Повідомлення'}))