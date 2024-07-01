import json
import os

import flask
import flask_wtf.csrf
import wtforms

COMMENTS_PATH = "./data/comments.json"
comments = flask.Blueprint('comment', __name__, template_folder='./templates')

class CommentForm(flask_wtf.FlaskForm):
    textbox = wtforms.TextAreaField('Input')

@comments.route('/comment/<string:post_title>', methods=['POST'])
def comment(post_title: str):
    form = CommentForm(csrf_enabled=True)

    save_comment(form.textbox.data, post_title)

    return flask.redirect('/')

def save_comment(content: str, post_title: str):
    with open(COMMENTS_PATH, 'r') as file:
        comment_data = json.loads(file.read())

    # See if user is logged in, otherwise setup as anon
    if 'username' in flask.session:
        username = flask.session['username']
    else:
        username = 'Anon'

    comment = {
        "username" : username,
        "content" : content
    }

    # Add comment to JSON data
    if post_title in comment_data:
        comment_data[post_title].append(comment)
    else:
        comment_data[post_title] = [comment]

    # Save JSON data
    with open(COMMENTS_PATH, 'w') as file:
        file.write(json.dumps(comment_data))

def get_comments(post_title : int) -> list[dict]:

    with open(COMMENTS_PATH, 'r') as file:
        comment_data = json.loads(file.read())

    if post_title in comment_data:
        return comment_data[post_title]
    else:
        return []

# Check Comments file exists
if not os.path.exists(COMMENTS_PATH):
    with open(COMMENTS_PATH, 'w+') as file:
        file.write('{}')

