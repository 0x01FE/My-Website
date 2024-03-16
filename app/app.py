import glob
import configparser
import random

import flask
import waitress
import markdown

from post import Post

app = flask.Flask(__name__, static_url_path='', static_folder='static')

CONFIG_PATH = "./config.ini"
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

POSTS_FOLDER = config['POSTS']['POSTS_FOLDER']
STATUS_FILE = config['STATUS']['STATUS_FILE']
PORT = int(config['NETWORK']['PORT'])
DEV = int(config['NETWORK']['DEV'])

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

def get_status() -> str:
    with open(STATUS_FILE, 'r', encoding='utf-8') as file:
        statuses = file.readlines()

    status = random.randint(0, len(statuses) - 1)

    return markdown.markdown(statuses[status])

# Main Page
@app.route('/')
def index():

    # Get posts
    posts = get_posts()

    post_bodies = []
    for post in posts:
        post_bodies.append(post.body)

    # Get status
    status = get_status()

    return flask.render_template('index.html', posts=post_bodies, status=status)

# Games Page
@app.route('/games/')
def games():

    # Get posts
    posts = get_posts(category_filter="games")

    post_bodies = []
    for post in posts:
        post_bodies.append(post.body)

    # Get status
    status = get_status()

    return flask.render_template('games.html', posts=post_bodies, status=status)

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

    return flask.render_template('music.html', posts=post_bodies, status=status)

# Motion Pictures Page
@app.route('/motion-pictures/')
def motion_pictures():

    # Get posts
    posts = get_posts(category_filter="motion-pictures")

    post_bodies = []
    for post in posts:
        post_bodies.append(post.body)

    # Get status
    status = get_status()

    return flask.render_template('motion-pictures.html', posts=post_bodies, status=status)

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

# About Page
@app.route('/about/')
def about():

    # Get status
    status = get_status()

    return flask.render_template('about.html', status=status)

if __name__ == "__main__":
    if DEV:
        app.run(port=PORT)
    else:
        waitress.serve(app, host='0.0.0.0', port=PORT)
