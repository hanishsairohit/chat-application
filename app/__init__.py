from flask import Flask

def create_app():
    """
    Flask app factory method.
    """
    app = Flask(__name__)

    from app import endpoints

    endpoints.init_app(app)

    return app
