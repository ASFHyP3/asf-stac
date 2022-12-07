import json
from datetime import datetime, timezone


def jsonify_stac_item(stac_item: dict) -> str:
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime) and obj.tzinfo == timezone.utc:
                return obj.isoformat().removesuffix('+00:00') + 'Z'
            return json.JSONEncoder.default(self, obj)

    return json.dumps(stac_item, cls=DateTimeEncoder)
