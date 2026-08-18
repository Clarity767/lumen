from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', LoginView.as_view(template_name='restaurant/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('tables/', views.table_list_view, name='table_list'),
    path('tables/<int:pk>/', views.table_detail_view, name='table_detail'),
    path('menu/', views.menu_view, name='menu'),
    path('profile/', views.profile_view, name='profile'),
    path('tables/<int:table_pk>/book/', views.booking_create_view, name='booking_create'),
    path('chat/', views.client_chat_view, name='client_chat'),
    path('chat/poll/', views.client_chat_poll_view, name='client_chat_poll'),
    path('admin-chat/', views.admin_chat_list_view, name='admin_chat_list'),
    path('admin-chat/<int:user_id>/', views.admin_chat_thread_view, name='admin_chat_thread'),
    path('booking/<int:booking_pk>/pay/', views.payment_view, name='payment'),
    path('booking/<int:booking_pk>/pay/success/', views.payment_success_view, name='payment_success'),
    path('chat/', views.client_chat_view, name='client_chat'),
    path('chat/poll/', views.client_chat_poll_view, name='client_chat_poll'),
    path('admin-chat/', views.admin_chat_list_view, name='admin_chat_list'),
    path('admin-chat/<int:user_id>/', views.admin_chat_thread_view, name='admin_chat_thread'),
    path('admin-chat/<int:user_id>/poll/', views.admin_chat_poll_view, name='admin_chat_poll'),
    path('bookings/<int:booking_pk>/cancel/', views.booking_cancel_view, name='booking_cancel'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('menu/<int:pk>/', views.dish_detail_view, name='dish_detail'),
    path('search/', views.search_view, name='search'),
    path('about/', views.about_view, name='about'),
    path('game/', views.game_view, name='game'),
path('game/finish/', views.game_finish_view, name='game_finish'),
]