from flask import Flask, render_template, make_response, request, redirect, url_for, flash
import hashlib
import secrets
import bcrypt
from utils.db import connect_db
from utils.login import extract_credentials, validate_password
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
        username, password = extract_credentials(request)
        response = (
            "HTTP/1.1 302 Found\r\n"
            "Location: /\r\n"
            "Content-Type: text/html; charset=utf-8\r\n\r\n"
        ).encode('utf-8')

        user = credential_collection.find_one({"username": username})
        if user is None or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            return response

        auth_token = secrets.token_hex(16)
        hash_auth_token = hashlib.sha256(auth_token.encode('utf-8')).digest()
        xsrf_token = secrets.token_hex(16)
        credential_collection.update_one(
            {"username": username},
            {"$set": {"auth_token": hash_auth_token, "xsrf_token": xsrf_token}}
        )

        response_with_cookie = (
            "HTTP/1.1 302 Found\r\n"
            "Location: /\r\n"
            f"Set-Cookie: auth_token={auth_token}; HttpOnly; Max-Age=3600; Path=/\r\n"
            f"Set-Cookie: xsrf_token={xsrf_token}; HttpOnly; Max-Age=3600; Path=/\r\n"
            "Content-Type: text/html; charset=utf-8\r\n\r\n"
        ).encode('utf-8')
        return response_with_cookie
    if request.method == 'GET':
        response = make_response(render_template('login.html'))
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Extract the username and passwords from the request
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate input
        if not username:
            flash("Username cannot be empty", "error")
            return render_template('home_page.html')  # Stay on home page
        if not password:
            flash("Password cannot be empty", "error")
            return render_template('home_page.html')  # Stay on home page
        if not confirm_password:
            flash("Confirm password cannot be empty", "error")
            return render_template('home_page.html')  # Stay on home page

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template('home_page.html')  # Stay on home page

        if not validate_password(password):
            flash("Password invalid", "error")
            return render_template('home_page.html')  # Stay on home page

        # Check if the username is already taken
        if credential_collection.find_one({"username": username}):
            flash("Username already taken", "error")
            return render_template('home_page.html')  # Stay on home page

        # Hash the password with bcrypt and insert into database
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        credential_collection.insert_one({
            "username": username,
            "password_hash": hashed_password
        })
        flash("Registration successful! You can now log in.", "success")

        # Render the home page with a success message
        return render_template('home_page.html')  # Stay on home page

    # GET request
    return render_template('home_page.html')  # Render home page


@app.route('/logout', methods=['GET'])
def logout():
    response = make_response(redirect(url_for('home')))  # Redirect to home page after logout
    response.set_cookie('auth_token', '', expires=0)  # Invalidate the auth token
    flash("You have been logged out.", "success")
    return response

@app.route('/home', methods=['GET'])
def home():
    response = make_response(render_template('home_page.html'))
    response.mimetype = "text/html"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.route('/posts', methods=['GET','POST'])
def posts():
    if request.method == 'GET':
        posts = get_post()
        response = make_response()
        response.set_data(posts)
        response.mimetype = "application/json"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
    
    if request.method == 'POST':
        create_post(request)
        response = make_response()
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
        

@app.route('/posts/<string:post_id>', methods=['DELETE'])
def delete_posts(post_id):
    #implement delete post
    pass

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)

