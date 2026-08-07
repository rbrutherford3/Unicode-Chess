from app import app as flask_app
from werkzeug.middleware.proxy_fix import ProxyFix

flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app, x_for=1, x_proto=1, x_host=1)
application = flask_app
