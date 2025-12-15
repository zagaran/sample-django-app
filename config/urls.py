"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path

from config.constants import HEALTH_CHECK_URL_NAME

urlpatterns = [
    path('admin/', admin.site.urls),
    path("oauth/", include("social_django.urls", namespace="social")),
    path('', include("common.urls")),
    # Health check is actually handled by the HealthCheckMiddleware
    path("health-check/", lambda request: HttpResponse("ok"), name=HEALTH_CHECK_URL_NAME),
]

handler404 = "common.views.error_404"
handler500 = "common.views.error_500"
