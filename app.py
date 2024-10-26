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


@app.route('/register', methods=['GET','POST'])
def register():
   if request.method == 'POST':
       username, password, confirm_password= extract_credentials(request)
       if not username:
           flash("Username cannot be empty", "error")
           return redirect(url_for('register'))
       if not password:
           flash("Password cannot be empty", "error")
           return redirect(url_for('register'))
       if not confirm_password:
           flash("Confirm password cannot be empty", "error")
           return redirect(url_for('register'))

       if not validate_password(password):
           flash("Password invalid", "error")
           return redirect(url_for('register'))
       if credential_collection.find_one({"username": username}):
           flash("Username already taken", "error")
           return redirect(url_for('register'))
       if password != confirm_password:
           flash("Confirm_password enter not the same as password", "error")
           return redirect(url_for('register'))


       # Hash the password with bcrypt and insert into database
       hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
       credential_collection.insert_one({
           "username": username,
           "password_hash": hashed_password
       })
       # Redirect response after successful registration ( should load to new page)
       flash("Registration successful! You can now log in.", "success")
       return redirect(url_for('login'))  # Redirect to login page


   if request.method == 'GET':
       response = make_response(render_template('register.html'))
       response.headers['X-Content-Type-Options'] = 'nosniff'
       return response



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
    user_collection = db["credential"]
    user = user_collection.find_one({"auth_token_hash":hashlib.sha256(auth_token.encode()).hexdigest()})
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

