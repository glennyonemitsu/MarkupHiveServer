'''
Everything to use to improve or customize flask's features
'''
import uuid

from werkzeug.routing import BaseConverter


class UUIDConverter(BaseConverter):

    regex = '(?:[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

    def to_python(self, value):
        return uuid.UUID(value)

    def to_url(self, value):
        return str(value)


