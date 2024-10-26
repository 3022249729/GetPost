from flask import Flask, render_template, make_response,request,redirect,url_for
from utils.db import connect_db

app = Flask(__name__)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        response = make_response(redirect(url_for('home')))
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
    if request.method == 'GET':
        response = make_response(render_template('login.html'))
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        response = make_response(redirect(url_for('home')))
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
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