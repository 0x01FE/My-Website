import os
import glob
import configparser
import random
import datetime

import requests
import flask
import waitress
import markdown

from post import Post

app = flask.Flask(__name__, static_url_path='', static_folder='static')

CONFIG_PATH = "./config.ini"
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

WRITING_FOLDER = 'static/writing/'
POSTS_FOLDER = config['POSTS']['POSTS_FOLDER']
STATUS_FILE = config['STATUS']['STATUS_FILE']
PORT = int(config['NETWORK']['PORT'])
DEV = int(config['NETWORK']['DEV'])

MUSIC_API_TOKEN = config['AUTH']['MUSIC_API_TOKEN']
MUSIC_API_URL = config['NETWORK']['MUSIC_API_URL']
statuses = None

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

def read_status_file() -> list[str]:
    with open(STATUS_FILE, 'r', encoding='utf-8') as file:
        data = file.readlines()

    result = []
    for line in data:
        if not (line == '\n' or line[0] == '#'):
            result.append(line)

    return result

def get_status() -> str:
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
    print(statuses)

    if DEV:
        app.run(port=PORT)
    else:
        waitress.serve(app, host='0.0.0.0', port=PORT)
