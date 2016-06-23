import flask
import json


def json_response(status_code, data, additional_headers=None):
    headers = {
        "Content-Type": "application/json",
    }

    if isinstance(additional_headers, list):
        headers.update(additional_headers)

    return flask.make_response(json.dumps(data),
                               status_code,
                               headers)
