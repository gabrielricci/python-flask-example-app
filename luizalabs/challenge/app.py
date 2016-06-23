import os

import flask
import sqlalchemy
from sqlalchemy import orm


def register_blueprints(app):
    from luizalabs.challenge.api import users

    app.register_blueprint(users.blueprint, url_prefix="/users")


def setup_database(app):
    engine = sqlalchemy.create_engine(os.environ["DATABASE_URI"])
    Session = orm.sessionmaker(bind=engine)

    from luizalabs.challenge.models import repository

    app.app_ctx_globals_class.db_session = Session()
    app.app_ctx_globals_class.db = repository.Repository(app.app_ctx_globals_class.db_session)

    @app.after_request
    def finalize_db_session(response):
        if not flask.g.db_session.is_active:  # already rolled back
            flask.g.db_session.close()
        if 200 <= response.status_code < 400:
            flask.g.db_session.commit()
        else:
            flask.g.db_session.rollback()

        return response


app = flask.Flask(__name__)

register_blueprints(app)
setup_database(app)
