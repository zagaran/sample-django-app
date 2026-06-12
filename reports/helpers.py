import csv
import gc
import io
import logging
from datetime import datetime, date

from django.core.files.base import ContentFile
from django.core.files.storage import storages
from django.db import models


def queryset_to_pages(queryset, page_size=2000):
    page = queryset.order_by("pk")[:page_size]
    while page:
        yield page
        pk = max(obj.pk for obj in page)
        page = queryset.filter(pk__gt=pk).order_by("pk")[:page_size]

def get_object_attr(obj, attr):
    """
    Gets attribute from object, with support for foreign key traversal via `__`
    """
    parts = attr.split("__")
    val = obj
    for part in parts:
        val = getattr(val, part, None)
        if val is None:
            # no related object, stop traversing
            break
    return val


class ReportWriter(object):
    def __init__(self, report_filename, columns_list, autoformat=False):
        """
        Takes in report_filename and columns_list.

        If `autoformat` is True, automatic formatting will be applied to
        non-string data types
        """
        self.report_filename = report_filename
        self.csv_string_io = io.StringIO()
        self.current_date = datetime.now().date()
        self.autoformat = autoformat
        self.columns_list = columns_list

        self.dict_writer = csv.DictWriter(self.csv_string_io, fieldnames=self.columns_list)
        self.dict_writer.writeheader()

        self.storage = storages["reports"]

    def writerow(self, row_dict):
        self.dict_writer.writerow(self.format_row(row_dict))

    def format_row(self, row_dict):
        return {key: self.format_value(value) for (key, value) in row_dict.items()}

    def format_value(self, value):
        if not self.autoformat:
            return value
        if isinstance(value, date) or isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, bool):
            return str(value)
        if value is None:
            return ""
        return value

    def get_filename(self):
        filename = f"{self.report_filename}.csv"
        formatted_date = self.current_date.isoformat()
        return f"{formatted_date}/{filename}"

    def save(self):
        self.csv_string_io.seek(0)
        report_file = ContentFile(self.csv_string_io.read().encode('utf-8'))
        self.storage.save(self.get_filename(), report_file)
        return report_file


class ReportColumn(object):
    def __init__(self, name, model_field=None, callable=None):
        self.name = name
        self.callable = callable
        self.model_field = None if callable else (model_field or name)


class ReportSerializerBase(object):
    report_filename = None
    model: type[models.Model]
    columns: list[ReportColumn]
    related_model_args = []
    prefetch_related = []
    filter_kwargs = {}

    def __init__(self):
        # Save the select_related arguments for any model_fields that need foreign key traversal
        related_model_args = [*self.related_model_args]
        for column in self.columns:
            model_field = column.model_field
            if model_field is None:
                continue
            if "__" in model_field:
                parts = model_field.split("__")
                related_model_args.append("__".join(parts[:-1]))
        self.related_model_args = related_model_args
        logging.info(f"Beginning export of {self.model.objects.count()} {self.model.__name__} objects")

    def get_iterable(self):
        queryset = self.model.objects.filter(
            **self.filter_kwargs
        ).select_related(
            *self.related_model_args
        ).prefetch_related(
            *self.prefetch_related
        )
        return queryset

    def _get_row_values(self, obj):
        """If any column needs more complex handling, fill them out here"""
        return {}

    def get_row(self, obj):
        row = self._get_row_values(obj)
        for column in self.columns:
            if column.name in row:
                continue
            if column.callable is not None:
                val = column.callable(obj)
            else:
                val = get_object_attr(obj, column.model_field)
            row[column.name] = val
        return row

    def write_report(self):
        writer = ReportWriter(self.report_filename, columns_list=[column.name for column in self.columns], autoformat=True)
        for page in queryset_to_pages(self.get_iterable()):
            for obj in page:
                writer.writerow(self.get_row(obj))
            gc.collect()
        writer.save()
        logging.info("Done!")
