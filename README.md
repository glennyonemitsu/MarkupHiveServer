# MarkupHiveServer

This is the source of my ambitious PAAS project.

All keys and credentials have been removed including the git history.





## Interesting bits of code

src/service/flask_utils.py

UUID converter

src/service/pyjade_filters.py

pyjade filters: markdown support

src/service/util.py

api_signature

url_builder_manager


src/config/__init__.py


src/mode/cms.py

metaclasses to dynamically build wtform objects


src/application/blueprint.py

new route decorator for api versioning

blueprints

custom context processors to avoid repetition


src/application/__init__.py

custom WSGI middleware dispatcher

url_builder_manager registered for blueprints with subdomains, remove from url_for params


TODO src/application/*/*
