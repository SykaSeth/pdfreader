from .models import User
from .views import logout

from django.utils import timezone

def session_processor(request):
    user = request.session.get('user', None)
    if user:
        user = User.objects.get(id=user['id'])
        if user.last_login :
            now = timezone.now()
            difference = now - user.last_login
            if difference.total_seconds() > 24*3600:
                logout(request)
                return
        request.session['user'] = user.to_json()
    return {'session': request.session}
