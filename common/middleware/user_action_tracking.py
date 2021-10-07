# START_FEATURE user_action_tracking
from django.conf import settings
from common.models import UserAction


class UserActionTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        self.create_user_action(request, response)
        return response
    
    def create_user_action(self, request, response):
        try:
            user = request.user
        except AttributeError:
            return
        
        if not user.is_authenticated:
            return
        
        url_name = None
        if request.resolver_match:
            url_name = request.resolver_match.url_name
        
        if url_name in settings.USER_TRACKING_EXEMPT_ROUTES:
            return
        
        UserAction.objects.create(
            user=user,
            url=request.build_absolute_uri(),
            method=request.method,
            url_name=url_name,
            status_code=response.status_code,
            user_agent=request.META.get("HTTP_USER_AGENT")
        )
# END_FEATURE user_action_tracking
