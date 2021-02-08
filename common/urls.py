from django.conf.urls import url
from django.urls import path, include
from common import views
from config import settings

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    # START_FEATURE django_react
    path("djangre", views.DjangreView.as_view(), name='djangre-demo'),
    # END_FEATURE django_react
    path("logout", views.LogoutView.as_view(), name="logout")
]

# START_FEATURE debug_toolbar
if settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
# END_FEATURE debug_toolbar