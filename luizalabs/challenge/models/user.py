import sqlalchemy

from . import sqlbase


class User(sqlbase.Base):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    facebook_id = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    gender = sqlalchemy.Column(sqlalchemy.String, nullable=True)


class UserRepository(object):
    def __init__(self, session):
        self.session = session

    def all(self, limit=None):
        query = self.session.query(User)

        if limit:
            query = query.limit(int(limit))

        return query.all()

    def delete(self, user):
        assert(isinstance(user, User))
        self.session.delete(user)
        self.session.flush()

    def get_by_facebook_id(self, facebook_id):
        return self.session.query(User).filter_by(facebook_id=facebook_id).first()

    def insert(self, user):
        assert(isinstance(user, User))
        self.session.add(user)
        self.session.flush()

        return user
