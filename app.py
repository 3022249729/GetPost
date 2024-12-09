import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, make_response, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_socketio import SocketIO, disconnect, emit
from utils.db import connect_db
from utils.login import validate_password
from utils.posts import get_post, create_post, delete_post
from utils.upload import get_file_extension
import hashlib
import secrets
import bcrypt
import os
from bson import ObjectId
import html
import json
from collections import defaultdict
from datetime import datetime, timedelta

ws = True

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
socketio = SocketIO(app)

db = connect_db()
if db is not None:
    print('Database connected successfully')
else:
    print('Database not connected')
credential_collection = db["credential"]

MAX_REQUESTS = 50
TIME_WINDOW = timedelta(seconds=10)
BLOCK_TIME = timedelta(seconds=30)

requests_by_ip = defaultdict(list)  # Store timestamps of requests by IP
blocked_ips = {}  # Store blocked IPs and their block time

@app.before_request
def limit_requests():
    ip = request.remote_addr  # client's IP address
    current_time = datetime.now()


    if ip in blocked_ips:
        block_time = blocked_ips[ip]
        if current_time < block_time + BLOCK_TIME: # the time it block +30sec
            return make_response(
                jsonify({"message": "Too many requests. Please try again later."}), 429
            )
        else:
            # block time has passed, unblock the IP
            del blocked_ips[ip]

    #request timestamp for this IP
    requests_by_ip[ip].append(current_time)

    # Remove requests older than the 10-second time window
    requests_by_ip[ip] = [
        timestamp for timestamp in requests_by_ip[ip] if current_time - timestamp < TIME_WINDOW
    ]

    #less than 10sec more than 50 reuestes
    if len(requests_by_ip[ip]) > MAX_REQUESTS:
  # the blcoked list = current time
        blocked_ips[ip] = current_time
        return make_response(
            jsonify({"message": "Too many requests. Please try again later."}), 429
        )


@app.route('/css/<path:filename>', methods=['GET'])
def serve_css(filename):
    if ".." in filename or "/" in filename:
        response = make_response("404 NOT FOUND", 404)
        response.mimetype = "text/html"
        return response
    
    file_path = os.path.join("static/css", filename)
    if not os.path.isfile(file_path):
        response = make_response("404 NOT FOUND", 404)
        response.mimetype = "text/html"
        return response
    
    response = make_response(send_from_directory('static/css', filename))
    response.mimetype = "text/css"
    return response


@app.route('/js/<path:filename>', methods=['GET'])
def serve_js(filename):
    if ".." in filename or "/" in filename:
        response = make_response("404 NOT FOUND", 404)
        response.mimetype = "text/html"
        return response
    
    file_path = os.path.join("static", filename)
    if not os.path.isfile(file_path):
        response = make_response("404 NOT FOUND", 404)
        response.mimetype = "text/html"
        return response
    
    response = make_response(send_from_directory('static', filename))
    response.mimetype = "text/javascript"
    return response


@app.route('/images/<path:filename>', methods=['GET'])
def serve_image(filename):
    if ".." in filename or "/" in filename:
        response = make_response("404 NOT FOUND", 404)
        response.mimetype = "text/html"
        return response
    
    file_path = os.path.join("static/images", filename)
    if not os.path.isfile(file_path):
        response = make_response("404 NOT FOUND", 404)
        response.mimetype = "text/html"
        return response
    
    response = make_response(send_from_directory('static/images', filename))
    return response


# functions to serve static files


@app.after_request
def add_nosniff_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


# function to add nosniff to every response

@app.route('/login', methods=['GET', 'POST'])
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
        expiry_time = datetime.now() + timedelta(hours=1)
        credential_collection.update_one(
            {"username": username},
            {"$set": {"auth_token_hash": hash_auth_token, "tokens_expiry": expiry_time}}
        )

        xsrf_token = hashlib.sha256(os.urandom(48)).hexdigest()
        credential_collection.update_one({"_id": user["_id"]}, {"$set": {"xsrf_token": xsrf_token}})
        response.set_cookie('auth_token', auth_token, httponly=True, secure=True, max_age=3600)
        response.set_cookie('xsrf_token', xsrf_token, secure=True, max_age=3600)
        response.mimetype = "text/html"
        return response

    if request.method == 'GET':
        auth_token = request.cookies.get('auth_token')
        xsrf_token = request.cookies.get('xsrf_token')
        
        if auth_token and xsrf_token:
            user = credential_collection.find_one({"auth_token_hash": hashlib.sha256(auth_token.encode()).hexdigest()})
            if user:
                response = make_response(redirect('/'))
                response.mimetype = "text/html"
                return response

        response = make_response(render_template('login.html'))
        response.set_cookie('auth_token', '', expires=0)
        response.set_cookie('xsrf_token', '', expires=0)
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
            flash(
                "Password does not meet the requirements:<br>- 8+ characters<br>- 1 lowercase letter<br>- 1 uppercase letter<br>- 1 special character: !,@,#,$,%,^,&,(,),-,_,=",
                "error")
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
            "xsrf_token": None,
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
            credential_collection.update_one({"_id": user["_id"]}, {"$set": {"auth_token_hash": None, "xsrf_token":None}})

    response = make_response(redirect(url_for('login')))
    response.set_cookie('auth_token', '', expires=0)
    response.set_cookie('xsrf_token', '', expires=0)
    return response


@app.route('/', methods=['GET'])
def home():
    auth_token = request.cookies.get("auth_token")
    if not auth_token:
        response = make_response(redirect(url_for("login"), 302))
        response.set_cookie('auth_token', '', expires=0)
        response.set_cookie('xsrf_token', '', expires=0)
        response.mimetype = "text/html"
        return response

    user = credential_collection.find_one({"auth_token_hash": hashlib.sha256(auth_token.encode()).hexdigest()})
    if not user or datetime.now() > user['tokens_expiry']:
        response = make_response(redirect(url_for("login"), 302))
        response.set_cookie('auth_token', '', expires=0)
        response.set_cookie('xsrf_token', '', expires=0)
        response.mimetype = "text/html"
        return response
        # verify user

    username = user['username']
    pfp = "default.png"
    if "pfp" in user:
        pfp = user["pfp"]

    response = make_response(render_template('home_page.html', username=username, pfp=pfp))
    response.mimetype = "text/html"
    return response


@app.route('/posts', methods=['GET', 'POST'])
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
            return response

        elif code == 200:
            response = make_response('', 200)
            response.mimetype = "text/plain"
            return response


@app.route('/posts/<string:post_id>', methods=['DELETE'])
def delete_posts(post_id):
    code = delete_post(db, request, post_id)

    if code == 403:
        response = make_response("Permission Denied", 403)
        response.mimetype = "text/plain"
        return response

    elif code == 204:
        response = make_response("No Content", 204)
        response.mimetype = "text/plain"
        return response


@app.route('/like/<string:post_id>', methods=['POST'])
def like_post(post_id):
    auth_token = request.cookies.get("auth_token")
    if not auth_token:
        response = make_response("Permission Denied", 403)
        response.mimetype = "text/plain"
        return response

    user = credential_collection.find_one({"auth_token_hash": hashlib.sha256(auth_token.encode()).hexdigest()})
    if not user:
        response = make_response("Permission Denied", 403)
        response.mimetype = "text/plain"
        return response

    post_collection = db["posts"]
    post_collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$addToSet": {"likes": user["username"]}}
    )

    response = make_response("OK", 200)
    response.mimetype = "text/plain"
    return response


@app.route('/setpfp/<string:image_name>', methods=['POST'])
def setpfp(image_name):
    auth_token = request.cookies.get("auth_token")
    xsrf_token = request.headers.get('XSRF-TOKEN')
    if not auth_token or not xsrf_token:
        return {'success': False, 'message': 'Session expired/invalid token, please login again.'}, 403

    user = credential_collection.find_one({"auth_token_hash": hashlib.sha256(auth_token.encode()).hexdigest()})
    if not user or xsrf_token != user["xsrf_token"] or datetime.now() > user['tokens_expiry']:
        return {'success': False, 'message': 'Session expired/invalid token, please login again.'}, 403
        # verify user

    if ".." in image_name or "/" in image_name:
        return {'success': False, 'message': 'Invalid profile picture name.'}, 400
    
    file_path = os.path.join("static/images", image_name)
    if not os.path.isfile(file_path):
        return {'success': False, 'message': 'Invalid profile picture name.'}, 400
    
    credential_collection.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$set": {"pfp": image_name}}
    )

    return {'success': True}, 200


@app.route('/uploadpfp', methods=['POST'])
def uploadpfp():
    auth_token = request.cookies.get("auth_token")
    xsrf_token = request.headers.get('XSRF-TOKEN')
    if not auth_token or not xsrf_token:
        return {'success': False, 'message': 'Session expired/invalid token, please login again.'}, 403

    user = credential_collection.find_one({"auth_token_hash": hashlib.sha256(auth_token.encode()).hexdigest()})
    if not user or xsrf_token != user["xsrf_token"] or datetime.now() > user['tokens_expiry']:
        return {'success': False, 'message': 'Session expired/invalid token, please login again.'}, 403
        # verify user

    file = request.files['pfp']
    file_bytes = file.read()

    extension = get_file_extension(file_bytes)
    if extension == None or extension == "mp4":
        return {'success': False, 'message': 'Unsupported file type.'}, 400

    filename = os.urandom(16).hex()
    file_path = os.path.join("./static/images", f"{filename}.{extension}")
    with open(file_path, 'wb') as f:
        f.write(file_bytes)

    credential_collection.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$set": {"pfp": f"{filename}.{extension}"}}
    )

    return {'success': True}, 200


@socketio.on('connect')
def handle_connect():
    xsrf_token = request.args.get('xsrf_token')
    auth_token = request.cookies.get("auth_token")

    app.logger.info("connecting")
    if not xsrf_token or not auth_token:
        socketio.emit('unauthorized', {'message': 'Session expired/invalid token, please login again.'}, to=request.sid)
        return 
    
    user = credential_collection.find_one({"auth_token_hash": hashlib.sha256(auth_token.encode()).hexdigest()})
    if not user or xsrf_token != user["xsrf_token"]:
        socketio.emit('unauthorized', {'message': 'Session expired/invalid token, please login again.'}, to=request.sid)
        return
        

@socketio.on('message')
def handle_websocket_message(str_data):
    json_data = json.loads(str_data)
    action = json_data.get('action')

    auth_token = request.cookies.get("auth_token")
    user = credential_collection.find_one({"auth_token_hash": hashlib.sha256(auth_token.encode()).hexdigest()})

    data = json_data['data']

    current_time = datetime.now()
    if current_time > user['tokens_expiry']:
        socketio.emit('unauthorized', {'message': 'Session expired/invalid token, please login again.'}, to=request.sid)
        disconnect()
        return

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
        return

    if action == 'like_post':
        post_id = data["post_id"]
        post_collection = db["posts"]

        post = post_collection.find_one({"_id": ObjectId(post_id)})
        if user["username"] in post["likes"]:
            post_collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$pull": {"likes": user["username"]}}
            )
            post = post_collection.find_one({"_id": ObjectId(post_id)})
            like_count = len(post["likes"])
            socketio.emit('unlike_post', {'post_id': post_id, 'like_count': like_count, 'like_list': post["likes"]})
        else:
            post_collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$addToSet": {"likes": user["username"]}}
            )
            post = post_collection.find_one({"_id": ObjectId(post_id)})
            like_count = len(post["likes"])
            socketio.emit('like_post', {'post_id': post_id, 'like_count': like_count, 'like_list': post["likes"]})
        return
    
    if action == 'delete_post':
        post_id = data["post_id"]
        post_collection = db["posts"]

        post = post_collection.find_one({"_id": ObjectId(post_id)})
        if not post:
            return
        
        if user["username"] == post["username"]:
            post = post_collection.delete_one({"_id": ObjectId(post_id)})
            socketio.emit('delete_post', {'post_id': post_id})
        return
            
        
                


if __name__ == "__main__":
    if ws:
        socketio.run(app, host='0.0.0.0', port=8080, debug=True)
    else:
        app.run(host='0.0.0.0', port=8080, debug=True)

