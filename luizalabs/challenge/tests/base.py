import flask
import json
import unittest

from sqlalchemy import orm

import luizalabs.challenge.app
from luizalabs.challenge.models import repository, sqlbase


class BaseTest(unittest.TestCase):

    def setUp(self):
        super(BaseTest, self).setUp()

        self.app = luizalabs.challenge.app.create_app(settings={
            "DATABASE_URI": "sqlite://",
            "FB_ACCESS_TOKEN": "SomeTOken",
            "TESTING": True,
        })

    def to_json_or_fail(self, json_data):
        try:
            return json.loads(json_data)
        except:
            self.fail("Bad JSON: {}".foramt(json_data))

    def url_for(self, *args, **kwargs):
        with self.app.test_request_context():
            return flask.url_for(*args, **kwargs)


class SqlTest(object):
    def setUp(self):
        super(SqlTest, self).setUp()

        self.addCleanup(self.app.engine.dispose)

        metadata = sqlbase.Base.metadata
        metadata.create_all(self.app.engine, checkfirst=True)

        for table in reversed(metadata.sorted_tables):
            self.app.engine.execute("DELETE FROM {}".format(table))

        self.sessionmaker = orm.sessionmaker(bind=self.app.engine)
        self.db = repository.Repository(self.sessionmaker(autocommit=True, expire_on_commit=True))

        self.addCleanup(self.db.session.close)
