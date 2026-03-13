from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from config import load_settings
from models import db
from prediction_service import load_pipeline
from routes import register_routes


def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    app.config.update(load_settings())

    frontend_origins = app.config["FRONTEND_ORIGINS"]
    if frontend_origins:
        CORS(
            app,
            resources={r"/predict": {"origins": frontend_origins}, r"/health": {"origins": frontend_origins}},
        )
    else:
        CORS(app, resources={r"/predict": {"origins": "*"}, r"/health": {"origins": "*"}})

    if app.config["ENABLE_DB_RECORDING"]:
        if not app.config["SQLALCHEMY_DATABASE_URI"]:
            raise RuntimeError("ENABLE_DB_RECORDING=true exige DATABASE_URL.")
        db.init_app(app)

        @app.cli.command("init-db")
        def init_db_command():
            with app.app_context():
                db.create_all()
            print("Base de donnees initialisee.")

        if app.config["AUTO_CREATE_DB"]:
            with app.app_context():
                db.create_all()

    app.config["PIPELINE"] = load_pipeline(app)
    register_routes(app)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=app.config["FLASK_HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"],
    )
