from django.http import HttpResponse
from django.urls import resolve, Resolver404
from config.constants import HEALTH_CHECK_URL_NAME

class HealthCheckMiddleware:
    """ This middleware exists to create a health check for load balancers or
        uptime monitoring that won't get blocked (such as by ALLOWED_HOSTS) or
        redirected (such as by SECURE_SSL_REDIRECT) """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            if resolve(request.path_info).view_name == HEALTH_CHECK_URL_NAME:
                return HttpResponse("ok")
        except Resolver404:
            pass
        return self.get_response(request)
