from . import user


class Repository(object):
    def __init__(self, session):
        self.session = session

        self.users = user.UserRepository(session)
