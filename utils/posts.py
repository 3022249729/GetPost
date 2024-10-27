import json
import hashlib
import html
from bson import ObjectId
from datetime import datetime

def create_post(db, request):
    auth_token = request.cookies.get("auth_token")
    if not auth_token:
        return 403
    body = request.body.decode()
    content = json.loads(body)

    user_collection = db["credential"]
    user = user_collection.find_one({"auth_token_hash":hashlib.sha256(auth_token.encode()).hexdigest()})
    if not user: #add xsrf later
        return 403
    
    post_collection = db["posts"]
    escaped = html.escape(content["message"])
    post_collection.insert_one({"username": user["username"], "timestamp": datetime.now(), "message": escaped, "attachments": [], "likes": 0, "dislikes": 0, "comments": {}})
    return 200
    

def delete_post(db, request, post_id):
    auth_token = request.cookies.get("auth_token")
    if not auth_token:
        return 403
    
    body = request.data.decode()
    # content = json.loads(body)

    user_collection = db["credential"]
    user = user_collection.find_one({"auth_token_hash": hashlib.sha256(auth_token.encode()).hexdigest()})
    if not user: #add xsrf later
        return 403
    
    post_collection = db["posts"]
    result = post_collection.delete_one({"username": user["username"], "_id": ObjectId(post_id)})
    if result.deleted_count > 0:
        return 204
    else:
        return 403

def get_post(db):
    post_collection = db["posts"]

    posts_list = []
    posts = post_collection.find()
    for post in posts:
        posts_list.append({
            "id": str(post["_id"]),
            "title": "Post by " + post["username"],  # Use username as title if needed
            "content": post["message"],
            "author": post["username"],
            "likes": [None] * post["likes"],  # Fake array with 'likes' count to match frontend's logic
            "comments": [{"username": k, "text": v} for k, v in post["comments"].items()],
            "timestamp": post["timestamp"].isoformat()
        })

    return json.dumps(posts_list)

def add_comment(db, request, post_id):
    auth_token = request.cookies.get("auth_token")
    if not auth_token:
        return 403

    body = request.body.decode()
    content = json.loads(body)
    comment_text = html.escape(content["comment"])

    user_collection = db["credential"]
    user = user_collection.find_one({"auth_token_hash": hashlib.sha256(auth_token.encode()).hexdigest()})
    if not user:
        return 403

    post_collection = db["posts"]
    post_collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$set": {f"comments.{user['username']}": comment_text}}
    )

    return 200

