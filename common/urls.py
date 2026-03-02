from django.conf import settings
from django.urls import include, path

from common import views
from common.constants import ATTACHMENT_PK_URL_KWARG

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    # START_FEATURE django_react
    # TODO: delete me; this is just a reference example
    path("django-react/", views.DjangoReactView.as_view(), name='django_react_demo'),
    # END_FEATURE django_react

    # START_FEATURE direct_upload
    path(
        f"attachments/upload-start/",
        views.FileUploadStartView.as_view(),
        name='attachment_upload_start'
    ),
    path(
        f"attachments/<uuid:{ATTACHMENT_PK_URL_KWARG}>/upload-stream/",
        views.FileUploadStreamView.as_view(),
        name='attachment_upload_stream'
    ),
    path(
        f"attachments/<uuid:{ATTACHMENT_PK_URL_KWARG}>/upload-complete/",
        views.FileUploadCompleteView.as_view(),
        name='attachment_upload_complete'
    ),
    path(
        f"attachments/<uuid:{ATTACHMENT_PK_URL_KWARG}>/download/",
        views.FileDownloadView.as_view(),
        name='attachment_download'
    ),
    path(
        f"attachments/<uuid:{ATTACHMENT_PK_URL_KWARG}>/open/",
        views.FileOpenView.as_view(),
        name='attachment_open'
    ),
    # END_FEATURE direct_upload

    path("logout", views.LogoutView.as_view(), name="logout"),
    path("robots.txt", views.RobotsTxtView.as_view(), name="robots_txt"),
]

# START_FEATURE debug_toolbar
if settings.DEBUG_TOOLBAR:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
# END_FEATURE debug_toolbar
