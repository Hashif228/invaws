from flask import Flask
from .models import db
from flask_mail import Mail
import os
from flask_migrate import Migrate


mail = Mail()
db = db

def create_app():
    templ = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'templates')
    sta = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static')

    app = Flask(__name__, template_folder=templ, static_folder=sta)
    app.config.from_object("config.Config")
    migrate = Migrate(app, db)

    mail.init_app(app)
    db.init_app(app)

    from .routes import main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app
