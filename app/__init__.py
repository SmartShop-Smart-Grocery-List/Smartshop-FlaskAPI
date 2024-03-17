from flask import Flask
from config import Config
from model.preprocessing import preprocess


def create_app():
    app = Flask(__name__)
    config = Config()
    app.config.from_object(config)
    from app.db.models import db
    db.init_app(app)

    with app.app_context():
        db.create_all()
        preprocess.data = preprocess.DataManager()
        preprocess.data.setup_recipe_colab_filter()

    from app.routes.api import api
    api.init_app(app)

    return app
