def serialize_orm(obj):
    """Convert a SQLAlchemy ORM object to dict without extra state."""
    if isinstance(obj, list):
        return [serialize_orm(o) for o in obj]
    d = dict(obj.__dict__)
    d.pop("_sa_instance_state", None)
    return d
