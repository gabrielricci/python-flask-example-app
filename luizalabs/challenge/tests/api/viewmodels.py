from luizalabs.challenge import models
from luizalabs.challenge.api import viewmodels
from luizalabs.challenge.tests import base


class ViewmodelsTest(base.BaseTest):
    def setUp(self):
        super(ViewmodelsTest, self).setUp()

    def test_it_add_hypermedia_links_to_user(self):
        user = self.db.users.insert(
            models.User(
                name="John Doe",
                gender="male",
                facebook_id="123",
            )
        )

        user_viewmodel = viewmodels.user(user)
        self.assertEquals(user_viewmodel["_links"]["self"]["href"],
                          self.url_for("users.get_by_id", facebook_id="123"))
