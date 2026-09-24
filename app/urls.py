from django.urls import path

from app import views
from app.constants import SAMPLE_OBJECT_PK_URL_KWARG

urlpatterns = [
    path(
        f"dashboard/",
        views.DashboardView.as_view(),
        name='dashboard'
    ),
    path(
        f"sample-objects/create/",
        views.SampleObjectCreateView.as_view(),
        name='sample-object-create'
    ),
    path(
        f"sample-objects/<uuid:{SAMPLE_OBJECT_PK_URL_KWARG}>/",
        views.SampleObjectDetailView.as_view(),
        name='sample-object'
    ),
    path(
        f"sample-objects/<uuid:{SAMPLE_OBJECT_PK_URL_KWARG}>/edit/",
        views.SampleObjectEditView.as_view(),
        name='sample-object-edit'
    ),
]
