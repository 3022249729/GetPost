from flask import Flask, render_template, make_response, request, redirect, url_for, flash
from utils.db import connect_db
from utils.login import extract_credentials, validate_password
from utils.posts import get_post, create_post, delete_post
import hashlib
import secrets
import bcrypt
from utils.posts import get_post, create_post

app = Flask(__name__)

secret_key = secrets.token_hex(32)
app.secret_key = 'HOIiot895@#128&900adf(afsd0)_12hrgafsd'

db = connect_db()
if db is not None:
    print('database connect successfully')
else:
    print('database not connected')
credential_collection = db["credential"]

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        response = make_response(redirect('/'))
        user = credential_collection.find_one({"username": username})
        if user is None or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            return response

        auth_token = secrets.token_hex(16)
        hash_auth_token = hashlib.sha256(auth_token.encode('utf-8')).hexdigest()
        credential_collection.update_one(
            {"username": username},
            {"$set": {"auth_token_hash": hash_auth_token}}
        )
        response.set_cookie('auth_token', auth_token, httponly=True, max_age=3600)
        return response
    if request.method == 'GET':
        response = make_response(render_template('login.html'))
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if not username:
            flash("Username cannot be empty", "error")
        if not password:
            flash("Password cannot be empty", "error")
        if not confirm_password:
            flash("Confirm password cannot be empty", "error")

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template('register.html')  # Stay on home page


        if not validate_password(password):
            flash("Password invalid", "error")
            return render_template('register.html')  # Stay on home page

        # Check if the username is already taken
        if credential_collection.find_one({"username": username}):
            flash("Username already taken", "error")
            return render_template('register.html')  # Stay on home page

        # Hash the password with bcrypt and insert into database
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        credential_collection.insert_one({
            "username": username,
            "password_hash": hashed_password
        })
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login'), 302)


    # GET request
    return render_template('register.html')  # Render home page


@app.route('/logout', methods=['GET'])
def logout():
    response = make_response(redirect(url_for('home')))  # Redirect to home page after logout
    response.set_cookie('auth_token', '', expires=0)  # Invalidate the auth token
    flash("You have been logged out.", "success")
    return response


@app.route('/', methods=['GET'])
def home():
    if "auth_token" not in request.cookies:
        return redirect(url_for("login"), 302)
    #if not logged in redirect back to login

    auth_token = request.cookies.get("auth_token")
    user = credential_collection.find_one({"auth_token_hash":hashlib.sha256(auth_token.encode()).hexdigest()})
    if not user:
        return redirect(url_for("login"), 302)
    #if using invalid auth_token, redirect back to login
    response = make_response(render_template('home_page.html'))
    response.mimetype = "text/html"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.route('/posts', methods=['GET','POST'])
def posts():
    if request.method == 'GET':
        posts = get_post(db)
        response = make_response()
        response.set_data(posts)
        response.mimetype = "application/json"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
    if request.method == 'POST':
        code = create_post(request)
        if code == 403:
            response = make_response("Permission Denied", 403)
            response.mimetype = "text/plain"
            response.headers['X-Content-Type-Options'] = 'nosniff'
            return response  

        elif code == 200:
            response = make_response('', 200) 
            response.headers['X-Content-Type-Options'] = 'nosniff'
            return response  
        

@app.route('/posts/<string:post_id>', methods=['DELETE'])
def delete_posts(post_id):
    code = delete_post(db, request, post_id)

    if code == 403:
        response = make_response("Permission Denied", 403)
        response.mimetype = "text/plain"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response  

    elif code == 204:
        response = make_response('', 204) 
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response  

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)

