from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

import json

class JSONField(models.TextField):
    def from_db_value(self, value, expression, connection, context):
        return value
    def to_python(self, value):
        """Convert our string value to JSON after we load it from the DB"""
        if value == "":
                    return None
        try:
            if isinstance(value, basestring):
                return json.loads(value)
        except ValueError:
            pass
        return value

    def get_db_prep_save(self, value,**kwargs):
        """Convert our JSON object to a string before we save"""

        if value == "":
            return None

        if isinstance(value, dict):
            value = json.dumps(value, cls=DjangoJSONEncoder,sort_keys=True)

        return super(JSONField, self).get_db_prep_save(value,**kwargs)