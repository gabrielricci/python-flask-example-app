import mock

from luizalabs.challenge import models
from luizalabs.challenge.tests import base
from luizalabs.challenge.services import exceptions


class UsersApiCreateTest(base.SqlTest, base.BaseTest):
    def setUp(self):
        super(UsersApiCreateTest, self).setUp()

    @mock.patch("luizalabs.challenge.services.facebook_service.get_user")
    def test_it_creates_and_returns_user_correctly(self, mock_patch):
        mock_patch.return_value = {
            "id": "123",
            "name": "John Doe",
            "gender": "male",
        }

        with self.app.test_client() as app:
            response = app.post(
                self.url_for("users.create"),
                data={"facebook_id": "123"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        mock_patch.assert_called_once_with("123")
        self.assertEquals(201, response.status_code)

        response_data = self.to_json_or_fail(response.data)

        self.assertEquals(response_data["name"], "John Doe")
        self.assertEquals(response_data["gender"], "male")
        self.assertEquals(response_data["facebook_id"], "123")

        self.db.session.expunge_all()
        user, = self.db.users.all()

        self.assertTrue(user is not None)
        self.assertEquals(user.name, "John Doe")
        self.assertEquals(user.gender, "male")
        self.assertEquals(user.facebook_id, "123")

    def test_it_returns_409_when_user_already_exists(self):
        self.db.users.insert(
            models.User(
                name="John Doe",
                facebook_id="123",
            )
        )

        with self.app.test_client() as app:
            response = app.post(
                self.url_for("users.create"),
                data={"facebook_id": "123"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        self.assertEquals(409, response.status_code)

        response_data = self.to_json_or_fail(response.data)

        self.assertEquals(response_data["error"], "user already exists")

    def test_it_returns_bad_request_when_no_fb_id_informed(self):
        with self.app.test_client() as app:
            response = app.post(
                self.url_for("users.create"),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        self.assertEquals(400, response.status_code)

        response_data = self.to_json_or_fail(response.data)

        self.assertEquals("fb id not specified", response_data["error"])

    @mock.patch("luizalabs.challenge.services.facebook_service.get_user")
    def test_it_returns_404_when_fb_user_not_found(self, mock_patch):
        mock_patch.side_effect = exceptions.FBUserNotFoundError()

        with self.app.test_client() as app:
            response = app.post(
                self.url_for("users.create"),
                data={"facebook_id": "123"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        mock_patch.assert_called_once_with("123")
        self.assertEquals(404, response.status_code)

        response_data = self.to_json_or_fail(response.data)

        self.assertEquals("fb user not found", response_data["error"])

    @mock.patch("luizalabs.challenge.api.users.logger.warning")
    @mock.patch("luizalabs.challenge.services.facebook_service.get_user")
    def test_it_returns_502_when_unauthorized(self, service_mock, logger_mock):
        service_mock.side_effect = exceptions.FBUnauthorizedError()

        with self.app.test_client() as app:
            response = app.post(
                self.url_for("users.create"),
                data={"facebook_id": "123"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        service_mock.assert_called_once_with("123")
        logger_mock.assert_called_once()

        self.assertEquals(502, response.status_code)

        response_data = self.to_json_or_fail(response.data)

        self.assertEquals("fb access token is invalid", response_data["error"])

    @mock.patch("luizalabs.challenge.api.users.logger.warning")
    @mock.patch("luizalabs.challenge.services.facebook_service.get_user")
    def test_it_returns_502_when_exception(self, service_mock, logger_mock):
        service_mock.side_effect = Exception("custom message")

        with self.app.test_client() as app:
            response = app.post(
                self.url_for("users.create"),
                data={"facebook_id": "123"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        service_mock.assert_called_once_with("123")
        logger_mock.assert_called_once()

        self.assertEquals(502, response.status_code)

        response_data = self.to_json_or_fail(response.data)

        self.assertEquals("custom message", response_data["error"])


class UsersApiDeleteTest(base.SqlTest, base.BaseTest):
    def setUp(self):
        super(UsersApiDeleteTest, self).setUp()

    def test_it_delete_user_correctly(self):
        self.db.users.insert(
            models.User(
                name="John Doe",
                gender="male",
                facebook_id="123",
            )
        )
        with self.app.test_client() as app:
            response = app.delete(
                self.url_for("users.delete", facebook_id="123"),
            )

        self.assertEquals(204, response.status_code)

        self.db.session.expunge_all()
        self.assertEquals([], self.db.users.all())

    def test_it_returns_204_when_user_doesnt_exist_in_local_database(self):
        with self.app.test_client() as app:
            response = app.delete(
                self.url_for("users.delete", facebook_id="123"),
            )

        self.assertEquals(204, response.status_code)


class UsersApiGetByIdTest(base.SqlTest, base.BaseTest):
    def setUp(self):
        super(UsersApiGetByIdTest, self).setUp()

    def test_it_returns_user_correctly(self):
        self.db.users.insert(
            models.User(
                name="John Doe",
                gender="male",
                facebook_id="123",
            )
        )
        with self.app.test_client() as app:
            response = app.get(
                self.url_for("users.get_by_id", facebook_id="123"),
            )

        self.assertEquals(200, response.status_code)

        response_data = self.to_json_or_fail(response.data)

        self.assertEquals(response_data["name"], "John Doe")
        self.assertEquals(response_data["facebook_id"], "123")
        self.assertEquals(response_data["gender"], "male")

    def test_it_returns_404_when_user_doesnt_exist_in_local_database(self):
        with self.app.test_client() as app:
            response = app.get(
                self.url_for("users.get_by_id", facebook_id="123"),
            )

        self.assertEquals(404, response.status_code)


class UsersApiListTest(base.SqlTest, base.BaseTest):
    def setUp(self):
        super(UsersApiListTest, self).setUp()

    def test_it_returns_empty_list_when_no_user(self):
        with self.app.test_client() as app:
            response = app.get(
                self.url_for("users.list")
            )

        self.assertEquals(200, response.status_code)

        response_data = self.to_json_or_fail(response.data)

        self.assertEquals([], response_data["users"])

    def test_it_returns_all_users(self, limit=None):
        users_to_add = 10

        users_added = {
            str(x):  self.db.users.insert(
                models.User(
                    name="User {}".format(x),
                    gender="male",
                    facebook_id=str(x),
                )
            ) for x in xrange(users_to_add)
        }

        with self.app.test_client() as app:
            response = app.get(
                self.url_for("users.list", limit=limit),
            )

        self.assertEquals(200, response.status_code)

        response_data = self.to_json_or_fail(response.data)

        if limit and limit < users_to_add:
            self.assertEquals(limit, len(response_data["users"]))
        else:
            self.assertEquals(users_to_add, len(response_data["users"]))

        for user in response_data["users"]:
            db_user = users_added.get(user["facebook_id"])
            self.assertTrue(db_user is not None)
            self.assertEquals(user["name"], db_user.name)
            self.assertEquals(user["gender"], db_user.gender)
            self.assertEquals(user["facebook_id"], db_user.facebook_id)

    def test_it_returns_limited_number_of_users(self):
        return self.test_it_returns_all_users(limit=5)
