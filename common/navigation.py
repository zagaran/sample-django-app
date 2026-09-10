from copy import copy

from django.conf import settings
from django.urls import resolve, NoReverseMatch


def get_view_class_for_breadcrumb(url, request):
    try:
        resolver = resolve(url)
    except NoReverseMatch:
        if settings.DEBUG:
            raise
        return None
    view_class = resolver.func.view_class(**resolver.func.view_initkwargs)
    parent_request = copy(request)
    parent_request.path = url
    parent_request.resolver_match = resolver
    view_class.setup(parent_request, *resolver.args, **resolver.kwargs)
    if hasattr(view_class, "get_object"):
        view_class.get_object()  # Assumes get_object sets self.object
        if hasattr(view_class, "object") and view_class.object is None:
            raise Exception(f"Invalid url kwargs for view {view_class}: object does not exist")
    return view_class