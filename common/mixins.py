from django.conf import settings
from django.urls import reverse
from django.views.generic.base import ContextMixin

from common.navigation import get_view_class_for_breadcrumb


class CommonContextMixin(ContextMixin):
    """
    Base view mixin for handling navigation and shared page elements.
    """
    no_page_header = False  # Set to true if the page intentionally has no header, to silence DEBUG warnings
    page_header = None  # Main page <h1> element
    page_title = None  # Text for <title> element. Defaults to page header if not provided.

    breadcrumb_text = None  # Text for breadcrumb element. Defaults to page title if not provided.
    parent_url_name = None  # View name of the navigational parent of this view (for breadcrumbs).
    pass_through_url_kwargs = True  # Set to False if parent URL kwargs are not a superset of this view's kwargs
    is_root_view = False  # Set to True to not display breadcrumbs on this view

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        header = self.get_page_header()
        context["page_header"] = header
        context["page_title"] = self.get_page_title()
        context["warn_missing_page_header"] = settings.DEBUG and header is None and not self.no_page_header
        context["breadcrumbs"] = self.get_breadcrumb_list()
        context["is_root_view"] = self.is_root_view
        return context

    def get_page_header(self):
        return self.page_header

    def get_page_title(self):
        return self.page_title if self.page_title is not None else self.get_page_header()

    def get_breadcrumb_text(self):
        return self.breadcrumb_text if self.breadcrumb_text is not None else self.get_page_title()

    def get_breadcrumb_list(self):
        breadcrumbs = []
        if parent_url := self.get_parent_url():
            parent_class = get_view_class_for_breadcrumb(parent_url, self.request)
            if parent_class is not None:
                breadcrumbs.extend(parent_class.get_breadcrumb_list())
        breadcrumbs.append({
            "url": self.request.path,
            "text": self.get_breadcrumb_text(),
            "is_root_view": self.is_root_view,
        })
        return breadcrumbs

    def get_parent_url(self):
        parent_url_name = self.get_parent_url_name()
        if parent_url_name is None:
            return None
        return reverse(self.parent_url_name, kwargs=self.get_parent_url_kwargs())

    def get_parent_url_name(self):
        return self.parent_url_name

    def get_parent_url_kwargs(self):
        if self.pass_through_url_kwargs:
            return self.kwargs
        return {}

    def get_object(self):
        super_class = super()
        if getattr(self, "object", None):
            return self.object
        if hasattr(super_class, "get_object"):
            self.object = super_class.get_object()
            return self.object