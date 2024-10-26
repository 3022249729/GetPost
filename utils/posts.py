import json
import hashlib
import html
from datetime import datetime


def create_post(db, request):
    auth_token = request.cookies.get("auth_token")
    if not auth_token:
        return 403

    user_collection = db["users"]
    user = user_collection.find_one({"auth_token_hash": hashlib.sha256(auth_token.encode()).hexdigest()})
    if not user or content["xsrf_token"] != user["xsrf_token"]:
        return 403

    post_collection = db["posts"]
    escaped = html.escape(content["message"])
    post_collection.insert_one(
        {"username": user["username"], "timestamp": datetime.datetime.now(), "message": escaped, })

    body = request.body.decode()
    content = json.loads(body)


def delete_post(db, request):
    pass


def get_post(db):
    post_collection = db["posts"]

    posts_list = []
    posts = post_collection.find()
    for post in posts:
        posts_list.append(post)

    content = json.dumps(posts_list)
    return content