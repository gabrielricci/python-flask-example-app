import logging

import flask
import requests

from . import exceptions

FB_API_URI = "https://graph.facebook.com/v2.6"

logger = logging.getLogger(__name__)


def get_user(facebook_id):
    logging.debug("Calling FB Graph API to retrieve user {}".format(facebook_id))

    response = requests.get(
        "{}/{}".format(FB_API_URI, facebook_id),
        headers={"Authorization": "OAuth {}".format(flask.current_app.config["FB_ACCESS_TOKEN"])},
        params={"fields": "name,gender"}
    )

    if response.status_code != 200:
        # TODO: Implement log
        if response.status_code == 404:
            raise exceptions.FBUserNotFoundError()
        elif response.status_code == 401:
            raise exceptions.FBUnauthorizedError()
        elif response.status_code == 400:
            raise Exception(response.json().get("error", {}).get("message"))
        else:
            raise Exception("Unknown error")

    return response.json()
