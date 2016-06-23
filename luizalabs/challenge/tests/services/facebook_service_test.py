import httpretty
import json

from luizalabs.challenge.tests import base
from luizalabs.challenge.services import facebook_service, exceptions


class FacebookServiceTest(base.BaseTest):
    def setUp(self):
        super(FacebookServiceTest, self).setUp()

    @httpretty.activate
    def test_it_raises_exception_when_user_not_found(self):
        httpretty.register_uri(
            httpretty.GET,
            "{}/{}".format(facebook_service.FB_API_URI, "123"),
            status=404
        )

        with self.app.test_request_context():
            with self.assertRaises(exceptions.FBUserNotFoundError):
                facebook_service.get_user("123")

    @httpretty.activate
    def test_it_raises_exception_when_unauthorized(self):
        httpretty.register_uri(
            httpretty.GET,
            "{}/{}".format(facebook_service.FB_API_URI, "123"),
            status=401,
            body=json.dumps({"error": {"message": "unauthorized"}}),
            content_type="application/json",
        )

        with self.app.test_request_context():
            with self.assertRaises(exceptions.FBUnauthorizedError) as e:
                facebook_service.get_user("123")
                self.assertEquals(e.message, "unauthorized")

    @httpretty.activate
    def test_it_raises_exception_when_bad_request(self):
        httpretty.register_uri(
            httpretty.GET,
            "{}/{}".format(facebook_service.FB_API_URI, "123"),
            status=400,
            body=json.dumps({"error": {"message": "custom"}}),
            content_type="application/json",
        )

        with self.app.test_request_context():
            with self.assertRaises(Exception) as e:
                facebook_service.get_user("123")
                self.assertEquals(e.message, "custom")

    @httpretty.activate
    def test_it_raises_exception_when_status_code_not_200(self):
        httpretty.register_uri(
            httpretty.GET,
            "{}/{}".format(facebook_service.FB_API_URI, "123"),
            status=500,
        )

        with self.app.test_request_context():
            with self.assertRaises(Exception) as e:
                facebook_service.get_user("123")
                self.assertEquals(e.message, "Unknown error")

    @httpretty.activate
    def test_it_returns_fb_user_data_correctly(self):
        httpretty.register_uri(
            httpretty.GET,
            "{}/{}".format(facebook_service.FB_API_URI, "123"),
            status=200,
            body=json.dumps({"name": "John Doe"}),
            content_type="application/json",
        )

        with self.app.test_request_context():
            user = facebook_service.get_user("123")
            self.assertEquals(user["name"], "John Doe")
