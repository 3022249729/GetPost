from flask import Flask, render_template, make_response, request, redirect, url_for, flash, send_from_directory
from utils.db import connect_db
from utils.login import validate_password
from utils.posts import get_post, create_post, delete_post
import hashlib
import secrets
import bcrypt
from bson import ObjectId

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

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

@app.route('/js/<path:filename>', methods=['GET'])
def serve_js(filename):
    response = make_response(send_from_directory('static', filename))
    response.mimetype = "text/javascript"
    return response

@app.route('/images/<path:filename>', methods=['GET'])
def serve_image(filename):
    response = make_response(send_from_directory('static/images', filename))
    return response
#functions to serve static files


@app.after_request
def add_nosniff_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response
#function to add nosniff to every response

@app.route('/login', methods=['GET','POST'])
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
    
    if request.method == 'GET':
        auth_token = request.cookies.get('auth_token')
        if auth_token:
            user = credential_collection.find_one({"auth_token_hash": hashlib.sha256(auth_token.encode()).hexdigest()})
            if user:
                response = make_response(redirect('/'))
                response.mimetype = "text/html"
                return response
            
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
            flash("Password does not meet the requirements:<br>- 8+ characters<br>- 1 lowercase letter<br>- 1 uppercase letter<br>- 1 special character: !,@,#,$,%,^,&,(,),-,_,=", "error")
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
            "password_hash": hashed_password
        })
        response = make_response(redirect(url_for('login')))
        response.mimetype = "text/html"
        return response

    # GET request
    response = make_response(render_template('register.html'))
    response.mimetype = "text/html"
    return response


@app.route('/logout', methods=['POST'])
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
    #if not logged in redirect back to login
    
    auth_token = request.cookies.get("auth_token")
    user = credential_collection.find_one({"auth_token_hash":hashlib.sha256(auth_token.encode()).hexdigest()})
    if not user:
        response = make_response(redirect(url_for("login"), 302))
        response.set_cookie('auth_token', '', expires=0)
        response.mimetype = "text/html"
        return response
    #if using invalid auth_token, redirect back to login

    username = user['username']
    response = make_response(render_template('home_page.html', username=username))
    response.mimetype = "text/html"
    return response


@app.route('/posts', methods=['GET','POST'])
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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)

