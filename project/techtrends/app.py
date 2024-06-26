import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import os

# Track number of connection
num_connection = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection(inc = True):
    global num_connection
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    if inc:
        app.logger.info('get_db_connection')
        num_connection = num_connection + 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.info('A non-existing article is accessed')
        return render_template('404.html'), 404
    else:
        app.logger.info(f'An existing article is accessed => {post[2]}')
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('"About Us" page is retrieved')
    return render_template('about.html')

# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            app.logger.info(f'A new article is created => {title}')
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

# Define healthcheck endpoint
@app.route('/healthz')
def healthz():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Healthcheck request successfully')
    return response

# Define metrics endpoint
@app.route('/metrics')
def metrics():
    connection = get_db_connection(False)
    num_posts = len(connection.execute('SELECT * FROM posts').fetchall())
    connection.close()
    response = app.response_class(
            # response=json.dumps({"db_connection_count":f"{num_connection}","post_count":f"{num_posts}"}),
            response=json.dumps({"db_connection_count":num_connection,"post_count":num_posts}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Metrics request successfully')
    return response

# start the application on port 3111
if __name__ == "__main__":
    logfile = 'app.log'
    if os.path.exists(logfile):
        os.remove(logfile)
    # Stream logs to a file, and set the default log level to DEBUG
    # logging.basicConfig(filename=logfile, level=logging.DEBUG)

    # See https://docs.python.org/3/library/logging.handlers.html
    # See https://docs.python.org/3/library/logging.html#logging.basicConfig
    # logging.basicConfig(level=logging.DEBUG, handlers=[logging.FileHandler(logfile), logging.StreamHandler()])
    logging.basicConfig(level=logging.DEBUG, handlers=[logging.FileHandler(logfile), logging.StreamHandler()], format= '%(levelname)s:%(name)s:%(asctime)s, %(message)s')

    app.run(host='0.0.0.0', port='3111')
