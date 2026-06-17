def queryset_to_pages(queryset, page_size=2000):
    page = queryset.order_by("pk")[:page_size]
    while page:
        yield page
        pk = max(obj.pk for obj in page)
        page = queryset.filter(pk__gt=pk).order_by("pk")[:page_size]
