def queryset_to_pages(queryset, page_size=2000, index_field="pk"):
    """
    Paginate queryset, ordered by `index_field`. `index_field` must be unique.
    """
    page = queryset.order_by(index_field)[:page_size]
    while page:
        yield page
        next_index = [getattr(obj, index_field) for obj in page][-1]
        page = queryset.filter(**{f"{index_field}__gt": next_index}).order_by(index_field)[:page_size]
