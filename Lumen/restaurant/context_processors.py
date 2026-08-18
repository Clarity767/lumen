from django.db.models import Q
from .models import Message, User


def unread_messages_count(request):
    if not request.user.is_authenticated:
        return {}

    if request.user.is_staff:
        count = Message.objects.filter(
            receiver=request.user, is_read=False
        ).count()
    else:
        count = Message.objects.filter(
            receiver=request.user, is_read=False, sender__is_staff=True
        ).count()

    return {'unread_messages_count': count}