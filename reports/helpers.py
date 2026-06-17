import csv
import gc
import io
import logging
from datetime import datetime, date

from django.core.files.base import ContentFile
from django.core.files.storage import storages
from django.db import models

from common.utils import queryset_to_pages


def get_object_attr(obj, attr):
    """
    Gets attribute from object, with support for foreign key traversal via __
    """
    parts = attr.split("__")
    val = obj
    for part in parts:
        val = getattr(val, part, None)
        if val is None:
            # no related object, stop traversing
            break
    return val


class ReportWriter:
    def __init__(self, report_filename, columns_list, autoformat=True):
        """
        Takes in report_folder and columns_list.

        If autoformat is True (default), automatic formatting will be applied to
        non-string data types
        """
        self.report_filename = report_filename
        self.csv_string_io = io.StringIO()
        self.current_date = datetime.now().date()
        self.autoformat = autoformat
        self.columns_list = columns_list

        self.dict_writer = csv.DictWriter(self.csv_string_io,
                                          fieldnames=self.columns_list)
        self.dict_writer.writeheader()

        self.storage = storages["reports"]

    def writerow(self, row_dict):
        self.dict_writer.writerow(self.format_row(row_dict))

    def format_row(self, row_dict):
        return {key: self.format_value(value) for (key, value) in
                row_dict.items()}

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
        formatted_date = self.current_date.isoformat()
        return f"{self.report_filename}/{formatted_date}.csv"

    def save(self):
        self.csv_string_io.seek(0)
        report_file = ContentFile(self.csv_string_io.read().encode('utf-8'))
        self.storage.save(self.get_filename(), report_file)
        return report_file


class ReportColumn:
    """
    When instantiated with only name, the report will have a column with that
    field.

    Passing model_field in addition to name will add a column called name,
    where the row value comes from model_field.

    Passing callable in addition to name will add a column called callable,
    where the row value comes from the result of evaluating callable on an
    instance of the model. callable takes priority over model_field.
    """

    def __init__(self, name, model_field=None, callable=None):
        self.name = name
        self.callable = callable
        self.model_field = None if callable else (model_field or name)


class ReportSerializerBase:
    """ Generic model serializer intended for report writing.

    Takes a Django model and list of columns and generates a
    CSV report of specified fields on database objects.
    """

    report_folder = ""
    """Folder where the report file will be saved"""

    model: type[models.Model]
    """Django model that will be serialized into a report"""

    columns: list[ReportColumn]
    """
    List of columns that will be the headers of the CSV report. 
    See ReportColumn for details on column configuration options.
    """

    related_model_args = []
    """List of arguments to select_related"""

    prefetch_related = []
    """List of arguments to prefetch_related (strings or Prefetch objects)"""

    filter_kwargs = {}
    """Dictionary of keyword arguments that will be passed to filter"""

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
        logging.info(
            f"Beginning export of {self.model.objects.count()} {self.model.__name__} objects")

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
        writer = ReportWriter(self.report_folder,
                              columns_list=[column.name for column in
                                            self.columns])
        for page in queryset_to_pages(self.get_iterable()):
            for obj in page:
                writer.writerow(self.get_row(obj))
            gc.collect()
        writer.save()
        logging.info("Done!")
