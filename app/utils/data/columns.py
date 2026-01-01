from sqlalchemy.inspection import inspect


def models_to_dict(items: list):
    if not items:
        return {}

    mapper = inspect(items[0].__class__)
    column_keys = [col.key for col in mapper.columns]

    result = {key: [] for key in column_keys}

    for obj in items:
        for key in column_keys:
            result[key].append(getattr(obj, key))

    return result
