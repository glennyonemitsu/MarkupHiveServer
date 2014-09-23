# MarkupHiveServer

This is the source of my ambitious PAAS project. It uses many popular Python 
technologies such as flask, pyjade, WSGI, and SQLAlchemy. Hopefully this will 
serve as a good illustration and resource for people looking to use these
technologies and frameworks.

The code is pretty big, so the README contains some parts of the code that might
be of interest. They are the "unusual" features provided such as flask 
blueprints. If anyone is curious about the more basic usage and common practices
in this repo, please reach out to me at yonemitsu@gmail.com and I will add them
to the README.

Pull requests welcome: especially with README improvements and additional 
comments in the source.

Note: All keys and credentials have been removed, so the git history went with it.


## Interesting bits of code

`src/service/flask_utils.py`

- UUID converter


`src/service/pyjade_filters.py`

- pyjade filters: markdown support


`src/service/util.py`

- api_signature
- url_builder_manager


`src/config/__init__.py`

- a common way to store multiple configurations and load during different deployment levels



`src/mode/cms.py`

- metaclasses to dynamically build wtform objects based on the content type setup the user has in the CMS


`src/application/blueprint.py`

- new route decorator for api versioning
- blueprints
- custom context processors to avoid repetition


`src/application/__init__.py`

- custom WSGI middleware dispatcher
- url_builder_manager registered for blueprints with subdomains, remove from url_for params


`src/application/api/view/__init__.py`

- api_reply
- check_signature, used in view/cms.py and view/general.py
