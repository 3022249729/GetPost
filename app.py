from flask import Flask, render_template, make_response
from utils.db import connect_db

app = Flask(__name__)

@app.route('/login', methods=['GET'])
def login():
    response = make_response(render_template('login.html'))
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