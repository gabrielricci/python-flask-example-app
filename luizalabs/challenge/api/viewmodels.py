import flask


def user_list(users):
    return {
        "_links": {},
        "users": [user(u) for u in users]
    }


def user(user):
    return {
        "_links": {
            "self": {
                "href": flask.url_for("users.get_by_id", facebook_id=user.facebook_id)
            }
        },
        "name": user.name,
        "facebook_id": user.facebook_id,
        "gender": user.gender,
    }
