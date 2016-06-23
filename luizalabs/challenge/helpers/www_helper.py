import flask
import json


def json_response(status_code, data):
    return flask.make_response(json.dumps(data),
                               status_code,
                               {"Content-Type": "application/json"})
