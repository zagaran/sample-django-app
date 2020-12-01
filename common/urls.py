from django.urls import path
from common import views


urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("logout", views.LogoutView.as_view(), name="logout")
]
