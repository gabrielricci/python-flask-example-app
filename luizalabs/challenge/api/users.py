import logging

import flask

from luizalabs.challenge import models
from luizalabs.challenge.api import viewmodels
from luizalabs.challenge.helpers import www_helper
from luizalabs.challenge.services import facebook_service, exceptions


logger = logging.getLogger(__name__)
blueprint = flask.Blueprint("users", __name__)


@blueprint.route("/", methods=["POST"], strict_slashes=False)
def create():
    facebook_id = flask.request.form.get("facebook_id")
    if not facebook_id:
        return www_helper.json_response(400, {"error": "fb id not specified"})

    existing_user = flask.g.db.users.get_by_facebook_id(facebook_id)
    if existing_user:
        # There's a lot of discussion on what status code to be returned on this case. Some argue
        # that a 400 Bad Request is sufficient in this case, some other argue that 409 Conflict
        # is the best option and there are some people who thinks that the WebDav 422 Unprocessable
        # Entity might suit as well. That's a discussion I'd love to have with you guys at LuizaLabs
        #
        # For now I went with 409.
        return www_helper.json_response(409, {"error": "user already exists"})

    try:
        fb_user = facebook_service.get_user(facebook_id)
    except exceptions.FBUserNotFoundError:
        return www_helper.json_response(404, {"error": "fb user not found"})
    except exceptions.FBUnauthorizedError as e:
        logger.warning(e, exc_info=True)
        return www_helper.json_response(502, {"error": "fb access token is invalid"})
    except Exception as e:
        logger.warning(e, exc_info=True)
        return www_helper.json_response(502, {"error": e.message})

    user = models.User(
        facebook_id=fb_user["id"],
        name=fb_user["name"],
        gender=fb_user.get("gender")
    )

    user = flask.g.db.users.insert(user)

    logger.info("User created (FB id {})".format(facebook_id))

    return www_helper.json_response(201, viewmodels.user(user))


@blueprint.route("/<string:facebook_id>", methods=["DELETE"])
def delete(facebook_id):
    user = flask.g.db.users.get_by_facebook_id(facebook_id)
    if not user:
        return flask.make_response("", 204)   # delete should be idempotent

    flask.g.db.users.delete(user)

    logger.info("User deleted (FB id {})".format(facebook_id))

    return flask.make_response("", 204)   # 204 responses should not have any body


@blueprint.route("/<string:facebook_id>", methods=["GET"])
def get_by_id(facebook_id):
    user = flask.g.db.users.get_by_facebook_id(facebook_id)
    if not user:
        return www_helper.json_response(404, {"error": "not_found"})

    return www_helper.json_response(200, viewmodels.user(user))


@blueprint.route("/", methods=["GET"], strict_slashes=False)
def list():
    limit = flask.request.args.get("limit")
    users = flask.g.db.users.all(limit=limit)

    return www_helper.json_response(200, viewmodels.user_list(users))
