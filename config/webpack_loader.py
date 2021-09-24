# START_FEATURE django_react

from django.conf import settings

from webpack_loader.loader import WebpackLoader


class DynamicWebpackLoader(WebpackLoader):
    """
    Custom django-webpack-loader loader to allow for hotloading in development.
    """

    def get_chunk_url(self, chunk):
        path = super().get_chunk_url(chunk)
        if settings.WEBPACK_LOADER_HOTLOAD:
            path = f"http://localhost:3000{path}"
        return path

# END_FEATURE django_react
