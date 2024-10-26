from flask import Flask, render_template, make_response,request,redirect,url_for,flash
from utils.db import connect_db
from utils.login import extract_credentials, validate_password
import hashlib, secrets, bcrypt

app = Flask(__name__)
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

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username, password, confirm_password= extract_credentials(request)
        if not username :
            print("user")
        if not password :
            print("pass")
        if not confirm_password:
            print("confirm_pass")
        response = (
            "HTTP/1.1 302 Found\r\n"
            "Location: /home\r\n"
            "Content-Type: text/html; charset=utf-8\r\n\r\n"
        ).encode('utf-8')
        if not validate_password(password):
            flash("Password invalid", "error")
            return response
        if credential_collection.find_one({"username": username}):
            flash("Username used", "error")
            return response
        if password != confirm_password:
            flash("Confirm_password enter not the same as password", "error")
            return response
        # Hash the password with bcrypt and insert into database
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        credential_collection.insert_one({
            "username": username,
            "password_hash": hashed_password
        })
        # Redirect response after successful registration ( should load to new page)
        success_response = (
            "HTTP/1.1 302 Found\r\n"
            "Location: /login\r\n"
            "Content-Type: text/html; charset=utf-8\r\n\r\n"
        ).encode('utf-8')
        flash("Registration successful! You can now log in.", "success")
        return success_response

    if request.method == 'GET':
        response = make_response(render_template('register.html'))
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response


@app.route('/home', methods=['GET'])
def home():
    db = connect_db()
    if db is not None:
        app.logger.info('databse connected successfully')
    else:
        app.logger.info('databse not connected')
    response = make_response(render_template('home_page.html'))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)