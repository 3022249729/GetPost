from flask import Flask, request, render_template, make_response
from utils.db import connect_db
from utils.posts import get_post, create_post

app = Flask(__name__)

db = connect_db()
if db is not None:
    print('databse connected successfully')
    # app.logger.info('databse connected successfully')
else:
    print('databse not connected')
    # app.logger.info('databse not connected')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        response = make_response(render_template('login.html'))
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
        #respond with the html
    if request.method == 'POST':
        #do post implementation
        pass


@app.route('/', methods=['GET'])
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

