from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        base_qs = Notification.objects.filter(user=request.user)
        return {
            'notif_list': base_qs.order_by('-created_at')[:10],
            'notif_count': base_qs.filter(read=False).count(),
        }
    return {'notif_list': [], 'notif_count': 0}