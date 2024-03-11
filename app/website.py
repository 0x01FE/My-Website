import glob
import configparser

import flask

from post import Post

app = flask.Flask(__name__, static_url_path='', static_folder='static')

config = configparser.ConfigParser()
config.read("config.ini")

POSTS_FOLDER = config['POSTS']['POSTS_FOLDER']

def get_posts() -> list[Post]:
    post_files= glob.glob(f'{POSTS_FOLDER}/*')
    post_files.remove(f'{POSTS_FOLDER}\\POST_TEMPLATE.md')

    posts: list[Post] = []
    for post_file in post_files:
        post = Post(post_file)

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

@app.route('/')
def index():

    # Get posts
    posts = get_posts()

    post_bodies = []
    for post in posts:
        post_bodies.append(post.body)

    return flask.render_template('index.html', posts=post_bodies)


if __name__ == "__main__":
    app.run()
