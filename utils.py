from datetime import datetime
from bson import ObjectId

def serialize_for_cache(data: dict) -> dict:
    result = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, dict):
            result[key] = serialize_for_cache(value)
        else:
            result[key] = value
    return result