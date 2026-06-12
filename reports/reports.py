from django.contrib.auth.models import Permission

from common.models import User
from reports.helpers import ReportColumn, ReportSerializerBase


class UsersReport(ReportSerializerBase):
    report_filename = 'users_report'
    model = User
    columns = [
        ReportColumn("email"),
        ReportColumn("full_name", callable=lambda user: user.get_full_name()),
    ]
    filter_kwargs = {"is_active": True}


class PermissionsReport(ReportSerializerBase):
    report_filename = 'permissions_report'
    model = Permission
    columns = [
        ReportColumn("name"),
        ReportColumn("object_type", model_field="content_type__model"),
        ReportColumn("groups_with_permission")
    ]
    prefetch_related = ["group_set"]

    def _get_row_values(self, permission):
        row_values = super()._get_row_values(permission)
        if permission.group_set.exists():
            val = ",".join(group.name for group in permission.group_set.all())
        else:
            val = None
        row_values["groups_with_permission"] = val
        return row_values
