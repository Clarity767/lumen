from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from .forms import RegisterForm, BookingForm, ProfileForm, ReviewForm, ContactForm
from .models import Table, Dish, Booking, BookingItem, Message, Category, Profile, Payment, Review, GamePromoCode
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
import uuid
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.db.models import Avg
from django.views.decorators.http import require_POST
import json



def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'restaurant/register.html', {'form': form})

def get_support_user():
    return User.objects.filter(is_staff=True).order_by('id').first()
def home_view(request):
    return render(request, 'restaurant/home.html')


def build_floorplan_data(tables):
    now = timezone.localtime()
    today = now.date()
    now_naive = now.replace(tzinfo=None)

    todays_bookings = Booking.objects.filter(
        booking_date=today,
        status__in=['confirmed', 'paid'],
    ).order_by('booking_time')

    bookings_by_table = {}
    for b in todays_bookings:
        bookings_by_table.setdefault(b.table_id, []).append(b)

    def booking_start(b):
        return datetime.combine(b.booking_date, b.booking_time)

    def booking_end(b):
        return booking_start(b) + timedelta(minutes=b.duration_minutes)

    data = []
    for t in tables:
        status = 'free'
        free_from = None

        if not t.is_available:
            status = 'taken'
        else:
            table_bookings = bookings_by_table.get(t.pk, [])
            active_end = None
            for b in table_bookings:
                start = booking_start(b)
                end = booking_end(b)
                if start <= now_naive < end:
                    active_end = end
                    break

            if active_end is not None:
                status = 'taken'
                changed = True
                while changed:
                    changed = False
                    for b in table_bookings:
                        start = booking_start(b)
                        end = booking_end(b)
                        if start <= active_end and end > active_end:
                            active_end = end
                            changed = True
                free_from = active_end.strftime('%H:%M')

        data.append({
            'id': t.pk,
            'title': t.title,
            'seats': t.seats,
            'price': float(t.price),
            'zone': getattr(t, 'zone', '') or '',
            'x': getattr(t, 'pos_x', None),
            'y': getattr(t, 'pos_y', None),
            'status': status,
            'free_from': free_from,
        })
    return data

def table_list_view(request):
    all_tables = Table.objects.all()
    tables = all_tables.filter(is_available=True)

    table_categories = Category.objects.filter(type='table')
    selected_category = request.GET.get('category')
    if selected_category:
        tables = tables.filter(category__slug=selected_category)

    return render(request, 'restaurant/table_list.html', {
        'tables': tables,
        'floorplan_data': build_floorplan_data(all_tables),
        'categories': table_categories,
        'selected_category': selected_category,
    })


def table_detail_view(request, pk):
    table = Table.objects.get(pk=pk)
    return render(request, 'restaurant/table_detail.html', {
        'table': table,
        'floorplan_data': build_floorplan_data(Table.objects.all()),
    })


def menu_view(request):
    dishes = Dish.objects.filter(is_available=True)

    dish_categories = Category.objects.filter(type='dish')
    selected_category = request.GET.get('category')
    if selected_category:
        dishes = dishes.filter(category__slug=selected_category)

    return render(request, 'restaurant/menu.html', {
        'dishes': dishes,
        'categories': dish_categories,
        'selected_category': selected_category,
    })


@login_required
def profile_view(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'restaurant/profile.html', {'bookings': bookings})

@login_required
def booking_create_view(request, table_pk):
    table = get_object_or_404(Table, pk=table_pk)
    dishes = Dish.objects.filter(is_available=True)

    if request.method == 'POST':
        form = BookingForm(request.POST, user=request.user)
        if form.is_valid():
            new_date = form.cleaned_data['booking_date']
            new_time = form.cleaned_data['booking_time']
            new_duration = form.cleaned_data.get('duration_minutes', 120)
            promo = form.cleaned_data.get('promo_code')  

            existing = Booking.objects.filter(
                table=table, booking_date=new_date,
                status__in=['pending', 'confirmed', 'paid']
            )
            for b in existing:
                if b.overlaps_with(new_date, new_time, new_duration):
                    messages.error(request, 'Цей столик вже заброньовано на обраний час. Оберіть інший час.')
                    return render(request, 'restaurant/booking_create.html', {
                        'form': form, 'table': table, 'dishes': dishes,
                    })

            with transaction.atomic():
                booking = form.save(commit=False)
                booking.user = request.user
                booking.table = table
                booking.status = 'pending'

                total = table.price
                selected_items = []
                for dish in dishes:
                    qty = request.POST.get(f'dish_{dish.id}')
                    if qty and int(qty) > 0:
                        qty = int(qty)
                        selected_items.append((dish, qty))
                        total += dish.price * qty


                discount_applied = 0
                if promo:
                    discount_applied = min(promo.discount_amount, total)
                    total -= discount_applied

                    booking.promo_code = promo
                    booking.promo_discount_applied = discount_applied

                booking.total_price = total
                booking.save()

                for dish, qty in selected_items:
                    BookingItem.objects.create(
                        booking=booking, dish=dish,
                        quantity=qty, price_at_order=dish.price
                    )

                if promo:
                    promo.is_used = True
                    promo.save(update_fields=['is_used'])

            if promo:
                messages.success(
                    request,
                    f'Бронювання створено! Промокод застосовано: -{discount_applied} грн '
                    f'({promo.reward_description}). До сплати: {total} грн.'
                )
            else:
                messages.success(request, 'Бронювання успішно створено!')
            return redirect('profile')
    else:
        form = BookingForm(user=request.user)

    return render(request, 'restaurant/booking_create.html', {
        'form': form, 'table': table, 'dishes': dishes,
    })

@login_required
def payment_view(request, booking_pk):
    if request.method == 'POST':
        with transaction.atomic():
            booking = get_object_or_404(
                Booking.objects.select_for_update(),
                pk=booking_pk,
                user=request.user
            )

            if booking.status == 'paid':
                messages.info(request, 'Це бронювання вже оплачено.')
                return redirect('profile')

            payment, created = Payment.objects.get_or_create(
                booking=booking,
                defaults={'amount': booking.total_price}
            )

            payment.status = 'success'
            payment.transaction_id = f'SIM-{uuid.uuid4().hex[:12].upper()}'
            payment.paid_at = timezone.now()
            payment.save()

            booking.status = 'paid'
            booking.save()

        messages.success(request, 'Оплата пройшла успішно!')
        return redirect('payment_success', booking_pk=booking_pk)


    booking = get_object_or_404(Booking, pk=booking_pk, user=request.user)
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={'amount': booking.total_price}
    )
    return render(request, 'restaurant/payment.html', {
        'booking': booking,
        'payment': payment,
    })



@login_required
def client_chat_view(request):
    support = get_support_user()
    if not support:
        messages.error(request, 'Чат тимчасово недоступний.')
        return redirect('profile')

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Message.objects.create(sender=request.user, receiver=support, text=text)
        return redirect('client_chat')

    chat_messages = Message.objects.filter(
        Q(sender=request.user, receiver=support) | Q(sender=support, receiver=request.user)
    ).order_by('created_at')


    chat_messages.filter(sender=support, receiver=request.user, is_read=False).update(is_read=True)

    return render(request, 'restaurant/client_chat.html', {
        'chat_messages': chat_messages,
        'support': support,
    })


@login_required
def client_chat_poll_view(request):

    support = get_support_user()
    chat_messages = Message.objects.filter(
        Q(sender=request.user, receiver=support) | Q(sender=support, receiver=request.user)
    ).order_by('created_at').values('sender__username', 'text', 'created_at')
    return JsonResponse({'messages': list(chat_messages)}, safe=False)


@login_required
def admin_chat_list_view(request):
    if not request.user.is_staff:
        return redirect('home')


    client_ids = Message.objects.filter(receiver=request.user).values_list('sender_id', flat=True)
    clients = User.objects.filter(id__in=client_ids).distinct()

    unread_counts = {
        c.id: Message.objects.filter(sender=c, receiver=request.user, is_read=False).count()
        for c in clients
    }

    return render(request, 'restaurant/admin_chat_list.html', {
        'clients': clients,
        'unread_counts': unread_counts,
    })


@login_required
def admin_chat_thread_view(request, user_id):
    if not request.user.is_staff:
        return redirect('home')

    client = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Message.objects.create(sender=request.user, receiver=client, text=text)
        return redirect('admin_chat_thread', user_id=user_id)

    chat_messages = Message.objects.filter(
        Q(sender=client, receiver=request.user) | Q(sender=request.user, receiver=client)
    ).order_by('created_at')

    chat_messages.filter(sender=client, receiver=request.user, is_read=False).update(is_read=True)

    return render(request, 'restaurant/admin_chat_thread.html', {
        'chat_messages': chat_messages,
        'client': client,
    })

@login_required
def admin_chat_poll_view(request, user_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'forbidden'}, status=403)

    client = get_object_or_404(User, pk=user_id)

    chat_messages = Message.objects.filter(
        Q(sender=client, receiver=request.user) | Q(sender=request.user, receiver=client)
    ).order_by('created_at').values('sender__username', 'text', 'created_at')

    Message.objects.filter(sender=client, receiver=request.user, is_read=False).update(is_read=True)

    return JsonResponse({'messages': list(chat_messages)}, safe=False)

@login_required
def payment_success_view(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, user=request.user)
    return render(request, 'restaurant/payment_success.html', {'booking': booking})


@login_required
def booking_cancel_view(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, user=request.user)

    if request.method == 'POST':
        if booking.status in ['pending', 'confirmed']:
            booking.status = 'cancelled'
            booking.save()
            messages.success(request, 'Бронювання скасовано.')
        else:
            messages.error(request, 'Це бронювання не можна скасувати.')
        return redirect('profile')

    return redirect('profile')


@login_required
def profile_edit_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профіль оновлено!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'restaurant/profile_edit.html', {'form': form})


def dish_detail_view(request, pk):
    dish = get_object_or_404(Dish, pk=pk)
    reviews = dish.reviews.select_related('user')
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']

    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Увійдіть, щоб залишити відгук.')
            return redirect('login')

        form = ReviewForm(request.POST, instance=user_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.dish = dish
            review.user = request.user
            review.save()
            messages.success(request, 'Дякуємо за відгук!')
            return redirect('dish_detail', pk=dish.pk)
    else:
        form = ReviewForm(instance=user_review)

    return render(request, 'restaurant/dish_detail.html', {
        'dish': dish,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'form': form,
        'user_review': user_review,
    })


def search_view(request):
    query = request.GET.get('q', '').strip()

    dishes = []
    tables = []

    if query:
        dishes = Dish.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_available=True
        )
        tables = Table.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            is_available=True
        )

    return render(request, 'restaurant/search_results.html', {
        'query': query,
        'dishes': dishes,
        'tables': tables,
    })


def about_view(request):
    return render(request, 'restaurant/about.html')


def about_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Дякуємо! Ваше повідомлення надіслано.')
            return redirect('about')
    else:
        form = ContactForm()

    return render(request, 'restaurant/about.html', {'form': form})

REWARD_THRESHOLDS = [
    (500, 'dish',  'Безкоштовна страва (знижка 200 грн)', 200),
    (300, 'dish',  'Знижка 120 грн на страву',             120),
    (150, 'drink', 'Безкоштовний напій (знижка 80 грн)',   80),
    (50,  'drink', 'Знижка 30 грн на напій',                30),
]


@login_required
def game_view(request):
    thresholds = sorted(REWARD_THRESHOLDS, key=lambda x: x[0])
    return render(request, 'restaurant/game.html', {'thresholds': thresholds})


@login_required
@require_POST
def game_finish_view(request):
    try:
        data = json.loads(request.body)
        score = int(data.get('score', 0))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid data'}, status=400)

    if score < 0 or score > 100000:
        return JsonResponse({'error': 'invalid score'}, status=400)

    reward = None
    for threshold, reward_type, description, discount in sorted(REWARD_THRESHOLDS, key=lambda x: -x[0]):
        if score >= threshold:
            reward = (threshold, reward_type, description, discount)
            break

    if not reward:
        return JsonResponse({'success': True, 'score': score, 'promo': None})

    _, reward_type, description, discount = reward
    promo = GamePromoCode.objects.create(
        user=request.user,
        code=GamePromoCode.generate_code(),
        score=score,
        reward_type=reward_type,
        reward_description=description,
        discount_amount=discount,
    )

    return JsonResponse({
        'success': True,
        'score': score,
        'promo': {
            'code': promo.code,
            'description': promo.reward_description,
            'discount': str(promo.discount_amount),
        },
    })