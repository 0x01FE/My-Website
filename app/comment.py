import json

import flask
import flask_session
import flask_wtf.csrf
import wtforms

comments = flask.Blueprint('comment', __name__, template_folder='./templates')

class CommentForm(flask_wtf.FlaskForm):
    textbox = wtforms.TextAreaField('Input')

@comments.route('/comment/', methods=['POST'])
def comment():
    form = CommentForm(csrf_enabled=True)

    return flask.redirect('/')


def get_comments(post_id : int) -> list[dict]:


