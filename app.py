<<<<<<< HEAD
from flask import Flask, render_template, make_response, request, redirect, url_for, flash, send_from_directory
=======
import eventlet

eventlet.monkey_patch()

from flask import Flask, render_template, make_response, request, redirect, url_for, flash, send_from_directory
from flask_socketio import SocketIO, send, emit
>>>>>>> d8dadfd (websocket-liked-comments)
from utils.db import connect_db
from utils.login import validate_password
from utils.posts import get_post, create_post, delete_post
from utils.upload import get_file_extension
import hashlib
import secrets
import bcrypt
import os
from bson import ObjectId
<<<<<<< HEAD

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
=======
import html
import json
from datetime import datetime

ws = True

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
socketio = SocketIO(app)
>>>>>>> d8dadfd (websocket-liked-comments)

db = connect_db()
if db is not None:
    print('Database connected successfully')
else:
    print('Database not connected')
credential_collection = db["credential"]


@app.route('/css/<path:filename>', methods=['GET'])
def serve_css(filename):
    response = make_response(send_from_directory('static/css', filename))
    response.mimetype = "text/css"
    return response

<<<<<<< HEAD
=======

>>>>>>> d8dadfd (websocket-liked-comments)
@app.route('/js/<path:filename>', methods=['GET'])
def serve_js(filename):
    response = make_response(send_from_directory('static', filename))
    response.mimetype = "text/javascript"
    return response

<<<<<<< HEAD
=======

>>>>>>> d8dadfd (websocket-liked-comments)
@app.route('/images/<path:filename>', methods=['GET'])
def serve_image(filename):
    response = make_response(send_from_directory('static/images', filename))
    return response
<<<<<<< HEAD
#functions to serve static files
=======


# functions to serve static files
>>>>>>> d8dadfd (websocket-liked-comments)


@app.after_request
def add_nosniff_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response
<<<<<<< HEAD
#function to add nosniff to every response

@app.route('/login', methods=['GET','POST'])
=======


# function to add nosniff to every response

@app.route('/login', methods=['GET', 'POST'])
>>>>>>> d8dadfd (websocket-liked-comments)
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = credential_collection.find_one({"username": username})
        if user is None or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            flash("Invalid username/password", "error")
            response = make_response(redirect(url_for('login')))
            response.mimetype = "text/html"
            return response

        response = make_response(redirect('/'))
        auth_token = secrets.token_hex(16)
        hash_auth_token = hashlib.sha256(auth_token.encode('utf-8')).hexdigest()
        credential_collection.update_one(
            {"username": username},
            {"$set": {"auth_token_hash": hash_auth_token}}
        )
        response.set_cookie('auth_token', auth_token, httponly=True, max_age=3600)
        response.mimetype = "text/html"
        return response
<<<<<<< HEAD
    
=======

>>>>>>> d8dadfd (websocket-liked-comments)
    if request.method == 'GET':
        auth_token = request.cookies.get('auth_token')
        if auth_token:
            user = credential_collection.find_one({"auth_token_hash": hashlib.sha256(auth_token.encode()).hexdigest()})
            if user:
                response = make_response(redirect('/'))
                response.mimetype = "text/html"
                return response
<<<<<<< HEAD
            
=======

>>>>>>> d8dadfd (websocket-liked-comments)
        response = make_response(render_template('login.html'))
        response.set_cookie('auth_token', '', expires=0)
        response.mimetype = "text/html"
        return response


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match", "error")
            response = make_response(render_template('register.html'))
            response.mimetype = "text/html"
            return response

        # Check if password meets strength requirements
        if not validate_password(password):
<<<<<<< HEAD
            flash("Password does not meet the requirements:<br>- 8+ characters<br>- 1 lowercase letter<br>- 1 uppercase letter<br>- 1 special character: !,@,#,$,%,^,&,(,),-,_,=", "error")
=======
            flash(
                "Password does not meet the requirements:<br>- 8+ characters<br>- 1 lowercase letter<br>- 1 uppercase letter<br>- 1 special character: !,@,#,$,%,^,&,(,),-,_,=",
                "error")
>>>>>>> d8dadfd (websocket-liked-comments)
            response = make_response(render_template('register.html'))
            response.mimetype = "text/html"
            return response

        # Check if the username is already taken
        if credential_collection.find_one({"username": username}):
            flash("Username already taken", "error")
            response = make_response(render_template('register.html'))
            response.mimetype = "text/html"
            return response

        # Hash the password with bcrypt and insert into database
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        credential_collection.insert_one({
            "username": username,
            "password_hash": hashed_password,
            "pfp": "default.png"
        })
        response = make_response(redirect(url_for('login')))
        response.mimetype = "text/html"
        return response

    # GET request
    response = make_response(render_template('register.html'))
    response.mimetype = "text/html"
    return response


@app.route('/logout', methods=['GET'])
def logout():
    auth_token = request.cookies.get('auth_token')
    if auth_token:
        user = credential_collection.find_one({"auth_token_hash": hashlib.sha256(auth_token.encode()).hexdigest()})
        if user:
            credential_collection.update_one({"_id": user["_id"]}, {"$set": {"auth_token_hash": None}})

    response = make_response(redirect(url_for('login')))
    response.set_cookie('auth_token', '', expires=0)
    return response


@app.route('/', methods=['GET'])
def home():
    if "auth_token" not in request.cookies:
        response = make_response(redirect(url_for("login"), 302))
        response.mimetype = "text/html"
        return response
<<<<<<< HEAD
    #if not logged in redirect back to login
    
    auth_token = request.cookies.get("auth_token")
    user = credential_collection.find_one({"auth_token_hash":hashlib.sha256(auth_token.encode()).hexdigest()})
=======
    # if not logged in redirect back to login

    auth_token = request.cookies.get("auth_token")
    user = credential_collection.find_one({"auth_token_hash": hashlib.sha256(auth_token.encode()).hexdigest()})
>>>>>>> d8dadfd (websocket-liked-comments)
    if not user:
        response = make_response(redirect(url_for("login"), 302))
        response.set_cookie('auth_token', '', expires=0)
        response.mimetype = "text/html"
        return response
<<<<<<< HEAD
    #if using invalid auth_token, redirect back to login
=======
    # if using invalid auth_token, redirect back to login
>>>>>>> d8dadfd (websocket-liked-comments)

    username = user['username']
    pfp = "default.png"
    if "pfp" in user:
        pfp = user["pfp"]

    response = make_response(render_template('home_page.html', username=username, pfp=pfp))
    response.mimetype = "text/html"
    return response


<<<<<<< HEAD
@app.route('/posts', methods=['GET','POST'])
=======
@app.route('/posts', methods=['GET', 'POST'])
>>>>>>> d8dadfd (websocket-liked-comments)
def posts():
    if request.method == 'GET':
        posts = get_post(db, request)
        response = make_response()
        response.set_data(posts)
        response.mimetype = "application/json"
        return response
    if request.method == 'POST':
        code = create_post(db, request)
        if code == 403:
            response = make_response("Permission Denied", 403)
            response.mimetype = "text/plain"
<<<<<<< HEAD
            return response  

        elif code == 200:
            response = make_response('', 200) 
            response.mimetype = "text/plain"
            return response  
        
=======
            return response

        elif code == 200:
            response = make_response('', 200)
            response.mimetype = "text/plain"
            return response

>>>>>>> d8dadfd (websocket-liked-comments)

@app.route('/posts/<string:post_id>', methods=['DELETE'])
def delete_posts(post_id):
    code = delete_post(db, request, post_id)

    if code == 403:
        response = make_response("Permission Denied", 403)
        response.mimetype = "text/plain"
<<<<<<< HEAD
        return response  
=======
        return response
>>>>>>> d8dadfd (websocket-liked-comments)

    elif code == 204:
        response = make_response("No Content", 204)
        response.mimetype = "text/plain"
<<<<<<< HEAD
        return response  
    
=======
        return response


>>>>>>> d8dadfd (websocket-liked-comments)
@app.route('/like/<string:post_id>', methods=['POST'])
def like_post(post_id):
    auth_token = request.cookies.get("auth_token")
    if not auth_token:
        response = make_response("Permission Denied", 403)
        response.mimetype = "text/plain"
<<<<<<< HEAD
        return response  
    
=======
        return response

>>>>>>> d8dadfd (websocket-liked-comments)
    user = credential_collection.find_one({"auth_token_hash": hashlib.sha256(auth_token.encode()).hexdigest()})
    if not user:
        response = make_response("Permission Denied", 403)
        response.mimetype = "text/plain"
<<<<<<< HEAD
        return response  
    
=======
        return response

>>>>>>> d8dadfd (websocket-liked-comments)
    post_collection = db["posts"]
    post_collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$addToSet": {"likes": user["username"]}}
    )

    response = make_response("OK", 200)
    response.mimetype = "text/plain"
    return response

<<<<<<< HEAD
=======

>>>>>>> d8dadfd (websocket-liked-comments)
@app.route('/setpfp/<string:image_name>', methods=['POST'])
def setpfp(image_name):
    auth_token = request.cookies.get("auth_token")
    if not auth_token:
        response = make_response("Permission Denied", 403)
        response.mimetype = "text/plain"
<<<<<<< HEAD
        return response  
    
=======
        return response

>>>>>>> d8dadfd (websocket-liked-comments)
    user = credential_collection.find_one({"auth_token_hash": hashlib.sha256(auth_token.encode()).hexdigest()})
    if not user:
        response = make_response("Permission Denied", 403)
        response.mimetype = "text/plain"
<<<<<<< HEAD
        return response 
    #verify user
    
=======
        return response
        # verify user

>>>>>>> d8dadfd (websocket-liked-comments)
    credential_collection.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$set": {"pfp": image_name}}
    )

    response = make_response("OK", 200)
    response.mimetype = "text/html"
    return response

<<<<<<< HEAD
=======

>>>>>>> d8dadfd (websocket-liked-comments)
@app.route('/uploadpfp', methods=['POST'])
def uploadpfp():
    auth_token = request.cookies.get("auth_token")
    if not auth_token:
        response = make_response("Permission Denied", 403)
        response.mimetype = "text/plain"
<<<<<<< HEAD
        return response  
    
=======
        return response

>>>>>>> d8dadfd (websocket-liked-comments)
    user = credential_collection.find_one({"auth_token_hash": hashlib.sha256(auth_token.encode()).hexdigest()})
    if not user:
        response = make_response("Permission Denied", 403)
        response.mimetype = "text/plain"
<<<<<<< HEAD
        return response 
    #verify user
=======
        return response
        # verify user
>>>>>>> d8dadfd (websocket-liked-comments)

    file = request.files['pfp']
    file_bytes = file.read()

    extension = get_file_extension(file_bytes)
    if extension == None or extension == "mp4":
        return {'success': False, 'message': 'Unsupported file type.'}, 400
<<<<<<< HEAD
    
=======

>>>>>>> d8dadfd (websocket-liked-comments)
    filename = os.urandom(16).hex()
    file_path = os.path.join("./static/images", f"{filename}.{extension}")
    with open(file_path, 'wb') as f:
        f.write(file_bytes)

    credential_collection.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$set": {"pfp": f"{filename}.{extension}"}}
    )

    return {'success': True}, 200


<<<<<<< HEAD
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)

=======
@socketio.on('message')
def handle_websocket_message(str_data):
    json_data = json.loads(str_data)
    action = json_data.get('action')

    auth_token = request.cookies.get("auth_token")
    if auth_token:
        user = credential_collection.find_one({"auth_token_hash": hashlib.sha256(auth_token.encode()).hexdigest()})
        if user:
            data = json_data['data']

            if action == 'create_post':
                escaped = html.escape(data["message"])
                post_collection = db["posts"]

                time = datetime.now()
                result = post_collection.insert_one(
                    {"username": user["username"], "timestamp": time, "message": escaped, "attachments": [],
                     "likes": [], "dislikes": [], "comments": {}})

                inserted_id = result.inserted_id
                author = credential_collection.find_one({"username": user["username"]})
                author_pfp = "default.png"
                if "pfp" in author:
                    author_pfp = author["pfp"]

                post = {
                    "user": user["username"],
                    "id": str(inserted_id),
                    "content": escaped,
                    "author": user["username"],
                    "author_pfp": author_pfp,
                    "likes": [],
                    "comments": [],
                    "timestamp": time.isoformat()
                }
                socketio.emit('create_post', {'data': post})

            if action == 'like_post':
                post_id = data["post_id"]
                post_collection = db["posts"]
                post_collection.update_one(
                    {"_id": ObjectId(post_id)},
                    {"$addToSet": {"likes": user["username"]}}
                )
                post = post_collection.find_one({"_id": ObjectId(post_id)})
                like_count = len(post["likes"])
                socketio.emit('like_post', {'post_id': post_id, 'like_count': like_count, 'like_list': post["likes"]})


if __name__ == "__main__":
    if ws:
        socketio.run(app, host='0.0.0.0', port=8080)
    else:
        app.run(host='0.0.0.0', port=8080, debug=True)
>>>>>>> d8dadfd (websocket-liked-comments)
