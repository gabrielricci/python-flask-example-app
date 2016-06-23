import flask
import json


def json_response(status_code, data, additional_headers=None):
    headers = {
        "Content-Type": "application/json",
    }

    return flask.make_response(json.dumps(data),
                               status_code,
                               headers)
