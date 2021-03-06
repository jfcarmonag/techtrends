import logging
import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`

connection_count=0

def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global connection_count
    connection_count += 1
    return connection

def count_posts():
    connection = get_db_connection()
    p_count = connection.execute('SELECT Count(*) FROM posts').fetchone()[0]
    connection.close()
    return p_count

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
      app.logger.info('Non existing article, 404 returned')
      return render_template('404.html'), 404
    else:
       app.logger.info(post['title'])
       return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('AboutUs page retreived')
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
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('"{}" created'.format(title))
            return redirect(url_for('index'))

    return render_template('create.html')
#Healthcheck endpoint
@app.route('/healthz')
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    ## log line
    app.logger.info('Status request successful')
    return response
#Metrics endpoint
@app.route('/metrics')
def metrics():
    p_count = count_posts()
    response = app.response_class(
            response=json.dumps({"db_connection_count": connection_count, "post_count": p_count}),
            status=200,
            mimetype='application/json'
    )

    ## log line
    app.logger.info('Metrics request successful')
    return response

# start the application on port 3111
if __name__ == "__main__":
   #stream logs to a file
   import sys

   file_handler = logging.FileHandler(filename='app.log')
   stdout_handler = logging.StreamHandler(sys.stdout)
   stderr_handler = logging.StreamHandler(sys.stderr)
   handlers = [file_handler, stdout_handler,stderr_handler]

   logging.basicConfig(
      level=logging.DEBUG, 
      format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
      handlers=handlers)
   
   app.run(host='0.0.0.0', port='3111')
