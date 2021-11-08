from django.conf import settings
from django.conf.urls import url
from django.urls import include, path

from common import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("health_check/", views.HealthCheckView.as_view(), name="health_check"),
    # START_FEATURE django_react
    # TODO: delete me; this is just a reference example
    path("django_react/", views.DjangoReactView.as_view(), name='django_react_demo'),
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
