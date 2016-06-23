import flask

from luizalabs.challenge import models
from luizalabs.challenge.api import viewmodels
from luizalabs.challenge.helpers import www_helper
from luizalabs.challenge.services import facebook_service, exceptions


blueprint = flask.Blueprint("users", __name__)


@blueprint.route("/<string:facebook_id>", methods=["POST"])
def create(facebook_id):
    try:
        fb_user = facebook_service.get_user(facebook_id)
    except exceptions.FBUserNotFound:
        return www_helper.json_response(404, {"error": "not_found"})
    except Exception as e:
        return www_helper.json_response(500, {"error": e.message})

    user = models.User(
        facebook_id=fb_user["id"],
        name=fb_user["name"],
        gender=fb_user.get("gender")
    )

    user = flask.g.db.users.insert(user)

    return www_helper.json_response(200, viewmodels.user(user))


@blueprint.route("/<string:facebook_id>", methods=["DELETE"])
def delete(facebook_id):
    user = flask.g.db.users.get_by_facebook_id(facebook_id)
    if not user:
        return www_helper.json_response(404, {"error": "not_found"})

    flask.g.db.users.delete(user)

    return flask.make_response("", 204)   # 204 responses should not have any body


@blueprint.route("/<string:facebook_id>", methods=["GET"])
def get_by_id(facebook_id):
    user = flask.g.db.users.get_by_facebook_id(facebook_id)
    if not user:
        return www_helper.json_response(404, {"error": "not_found"})

    return www_helper.json_response(200, viewmodels.user(user))


@blueprint.route("/", methods=["GET"])
def list():
    limit = flask.request.args.get("limit")
    print limit
    users = flask.g.db.users.all(limit=limit)

    return www_helper.json_response(200, viewmodels.user_list(users))
