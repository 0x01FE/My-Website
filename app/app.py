import os
import glob
import configparser
import random
import base64
import datetime

import requests
import flask
import flask_wtf.csrf
import flask_session
import waitress
import markdown

from post import Post
import comment
import user

app = flask.Flask(__name__, static_url_path='', static_folder='static')
app.register_blueprint(comment.comments)
app.register_blueprint(user.user)

# CONFIG
CONFIG_PATH = "./config.ini"
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

WRITING_FOLDER = 'static/writing/'
POSTS_FOLDER = config['POSTS']['POSTS_FOLDER']
STATUS_FILE = config['STATUS']['STATUS_FILE']
PORT = int(config['NETWORK']['PORT'])
DEV = int(config['NETWORK']['DEV'])


# CSRF Protect
app.config['SECRET_KEY'] = base64.b64decode(config["FLASK"]["SECRET"])
csrf = flask_wtf.csrf.CSRFProtect()
csrf.init_app(app)

# Session Setup
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './data/.flask_session/'
flask_session.Session(app)

MUSIC_API_TOKEN = config['AUTH']['MUSIC_API_TOKEN']
MUSIC_API_URL = config['NETWORK']['MUSIC_API_URL']
statuses = {}

def get_posts(category_filter : str | None = None) -> list[Post]:
    post_files = glob.glob(f'{POSTS_FOLDER}/*')
    try:
        post_files.remove(f'{POSTS_FOLDER}/POST_TEMPLATE.md')
    except ValueError as e:
        print(e)
        print(f'Couldn\'t remove the template file probably; {post_files}')
        exit()

    posts: list[Post] = []
    for post_file in post_files:
        post = Post(post_file)

        if not category_filter:
            posts.append(post)
        elif category_filter == post.category:
            posts.append(post)

    # Order Posts by Date
    ordered_posts = []
    for i in range(len(posts)):

        most_recent = posts[0]
        for p in posts:
            if p.date < most_recent.date:
                most_recent = p

        ordered_posts.append(most_recent)
        posts.remove(most_recent)

    return reversed(ordered_posts)

def read_status_file() -> dict:
    with open(STATUS_FILE, 'r', encoding='utf-8') as file:
        data = file.readlines()

    result = {}
    current_key = None
    for line in data:
        if line[0] == '#':

            # Empty Key-Value pairs will cause errors
            if current_key:
                if not result[current_key]:
                    result.pop(current_key)

            current_key = line.replace('#', '').strip()
            result[current_key] = []
        elif not (line == '\n'):
            result[current_key].append(line)

    return result

def get_status() -> str:
    keys = list(statuses.keys())

    selected_key = keys[random.randint(0, len(keys) - 1)]
    section: list = statuses[selected_key]

    selected_status = section[random.randint(0, len(section) - 1)]

    return f'<div title="{selected_key}">{markdown.markdown(selected_status)}</div>'

# Main Page
@app.route('/')
def index():

    # Get posts
    posts = get_posts()

    if 'username' in flask.session:
        user = flask.session['username']
    else:
        user = 'Anon'

    # Get Comments
    posts_and_comments = []
    for post in posts:

        comments = comment.get_comments(post.title)
        posts_and_comments.append(({
            "body" : post.body,
            "title" : post.title,
            "date" : post.get_date()
            },
            comments))

    # Get status
    status = get_status()

    # Setup Comment Form
    form = comment.CommentForm()

    return flask.render_template('index.html', posts=posts_and_comments, status=status, form=form, user=user, title='0x01fe.net')

# Posts
@app.route('/post/<string:post_name>')
def post(post_name: str):

    for post in get_posts():
        if post.title == post_name:
            comments = comment.get_comments(post.title)

            if 'username' in flask.session:
                user = flask.session['username']
            else:
                user = 'Anon'

            # Setup Comment Form
            form = comment.CommentForm()

            return flask.render_template('index.html', posts=[[{'body': post.body, 'title': post.title}, comments]], status=get_status(), form=form, user=user, title='0x01fe.net')

    flask.abort(404)

# Games Page
@app.route('/category/<string:category>/')
def category_filter(category: str):

    # Get posts
    posts = get_posts(category_filter=category)

    if 'username' in flask.session:
        user = flask.session['username']
    else:
        user = 'Anon'

    # Get Comments
    posts_and_comments = []
    for post in posts:

        comments = comment.get_comments(post.title)
        posts_and_comments.append(({
            "body" : post.body,
            "title" : post.title,
            "date" : post.get_date()
            },
            comments))

    # Get status
    status = get_status()

    # Setup Comment Form
    form = comment.CommentForm()

    return flask.render_template('index.html', posts=posts_and_comments, status=status, form=form, user=user, title=category.replace('-', ' '))

# Music Page
@app.route('/music/')
def music():

    # Get posts
    posts = get_posts(category_filter="music")

    post_bodies = []
    for post in posts:
        post_bodies.append(post.body)

    # Get status
    status = get_status()

    # Get top albums
    r = requests.get(
        MUSIC_API_URL +'/top/albums',
        headers={
            'token' : MUSIC_API_TOKEN,
            'user' : '1',
            'limit' : '9'
        })

    top_albums = r.json()['top']
    for album_index in range(0, len(top_albums)):
        album = top_albums[album_index]

        time = int(album['listen_time'])
        hours = round(time/1000/60/60, 1)

        top_albums[album_index]['listen_time'] = hours

    return flask.render_template('music.html', posts=post_bodies, status=status, top_albums=top_albums)

# Programming Page
@app.route('/programming/')
def programming():

    # Get posts
    posts = get_posts(category_filter="programming")

    post_bodies = []
    for post in posts:
        post_bodies.append(post.body)

    # Get status
    status = get_status()

    return flask.render_template('programming.html', posts=post_bodies, status=status)

@app.route('/writing/')
def writing():

    works = []

    # Get all works in writing folder
    files = glob.glob(WRITING_FOLDER + '*')

    for path in files:

        date: str = datetime.datetime.fromtimestamp(os.path.getctime(path)).strftime("%B %d, %Y")
        name: str = path.split('/')[-1]

        works.append({
            'date' : date,
            'name' : name,
            'path' : path
        })

    return flask.render_template('writing.html', works=works)





# About Page
@app.route('/about/')
def about():

    # Get status
    status = get_status()

    return flask.render_template('about.html', status=status)

# MISC

@app.route('/albumsquare/<user_id>/<int:rows>')
def album_square(user_id, rows : int):

    limit = rows ** 2

    res = (1080/(rows))-rows

    # Get top albums
    r = requests.get(
        MUSIC_API_URL +'/top/albums',
        headers={
            'token' : MUSIC_API_TOKEN,
            'user' : user_id,
            'limit' : str(limit)
        })

    top_albums = r.json()['top']
    for album_index in range(0, len(top_albums)):
        album = top_albums[album_index]

        time = int(album['listen_time'])
        hours = round(time/1000/60/60, 1)

        top_albums[album_index]['listen_time'] = hours


    return flask.render_template('album_square.html', top_albums=top_albums, limit=rows, res=res)



if __name__ == "__main__":

    statuses = read_status_file()

    if DEV:
        app.run(port=PORT)
    else:
        waitress.serve(app, host='0.0.0.0', port=PORT)
