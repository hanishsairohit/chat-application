from app.endpoints.check import status_blueprint
from app.endpoints.login import login_blueprint
from app.endpoints.messages import messages_blueprint
from app.endpoints.users import user_blueprint

def init_app(app, **kwargs):
    app.register_blueprint(status_blueprint)
    app.register_blueprint(login_blueprint)
    app.register_blueprint(messages_blueprint)
    app.register_blueprint(user_blueprint)
