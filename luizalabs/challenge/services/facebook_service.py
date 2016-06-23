import os
import requests

from . import exceptions


FB_ACCESS_TOKEN = os.environ["FB_ACCESS_TOKEN"]


def get_user(facebook_id):
    response = requests.get("https://graph.facebook.com/v2.6/{}".format(facebook_id),
                            headers={"Authorization": "OAuth {}".format(FB_ACCESS_TOKEN)},
                            params={"fields": "name,gender"})

    if response.status_code != 200:
        # TODO: Implement log
        if response.status_code == 404:
            raise exceptions.FBUserNotFound()
        elif response.status_code == 400:
            raise Exception(response.json().get("error", {}).get("message"))
        else:
            raise Exception("Unknown error")

    return response.json()
