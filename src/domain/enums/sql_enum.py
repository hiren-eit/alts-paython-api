from sqlalchemy import types

class SqlEnum(types.TypeDecorator):
    impl = types.String
    cache_ok = True

    def __init__(self, enumtype, *args, **kwargs):
        kwargs.pop('name', None)
        super().__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if hasattr(value, 'value'):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self._enumtype(value)
