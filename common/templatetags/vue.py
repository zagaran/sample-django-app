# START_FEATURE vue
import json
import re

from django.core.serializers.json import DjangoJSONEncoder
from django.template.defaultfilters import register


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
    return json.dumps(value, cls=DjangoJSONEncoder).translate({
        ord(">"): "\\u003E",
        ord("<"): "\\u003C",
        ord("&"): "\\u0026",
    })
# END_FEATURE vue
