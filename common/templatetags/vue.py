# START_FEATURE vue
import json
import re

from django.core.serializers.json import DjangoJSONEncoder
from django.template.defaultfilters import register
from django.utils.html import escapejs
from django.utils.safestring import mark_safe


@register.filter
def to_v_init_arg(model_name):
    """
    Converts a v-model field key to the value expected for a v-init arg
    """
    v_init_arg = ":".join(model_name.split("."))
    # https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    camel_case_re = re.compile(r'(?<!^)(?=[A-Z])')
    v_init_arg = camel_case_re.sub('-', v_init_arg).lower()
    return v_init_arg


@register.filter
def jsonify(value):
    json_str = json.dumps(value, cls=DjangoJSONEncoder)
    return mark_safe(f"JSON.parse('{escapejs(json_str)}')")
# END_FEATURE vue
