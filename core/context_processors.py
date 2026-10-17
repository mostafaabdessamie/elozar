def notifications(request):
    if request.user.is_authenticated:
        
        return {
            'notif_count': 3,
            'notifications': [
                {'icon':'cash-coin', 'title':'Paiement reçu', 'desc':'Ahmed 300 DH', 'time':'5 min'},
            ]
        }
    return {}