import application.admin.view
import application.api.view
import application.api.view.cms
import application.api.view.general
import application.app.view
import application.manager.view
import application.manager.view.cms
from application import blueprint, flask_app, wsgi_app


flask_app.register_blueprint(blueprint.admin)
flask_app.register_blueprint(blueprint.app)
flask_app.register_blueprint(blueprint.api)
flask_app.register_blueprint(blueprint.manager)
flask_app.register_blueprint(blueprint.cms)


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    from werkzeug.debug import DebuggedApplication

    run_simple('0.0.0.0', 8000, wsgi_app, use_evalex=True, use_reloader=True, use_debugger=True)
