import base64
import json

import flask
import flask_wtf.csrf
import wtforms

user = flask.Blueprint('user', __name__, template_folder='./templates/user')
USERS_PATH = "./data/users.json"
class RegisterUserForm(flask_wtf.FlaskForm):
    username = wtforms.StringField("Username", [
        wtforms.validators.Length(min=4, max=32),
        wtforms.validators.DataRequired()
    ])
    password = wtforms.PasswordField("Password", [
        wtforms.validators.Length(min=8, max=64),
        wtforms.validators.DataRequired()
    ])

class LoginUserForm(flask_wtf.FlaskForm):
    username = wtforms.StringField("Username", [
        wtforms.validators.DataRequired()
    ])
    password = wtforms.PasswordField("Password", [
        wtforms.validators.DataRequired()
    ])

@user.route('/user/add/', methods=["POST"])
def add_user():

    # Get form data
    form = RegisterUserForm(csrf_enabled=True)

    username = form.username.data
    password = form.password.data

    # Read existing user data
    with open(USERS_PATH, 'r') as file:
        user_data = json.loads(file.read())

    # check if user exists
    if username in user_data:
        flask.abort(400)

    # Store password / server side cookie
    user_data[username] = base64.b64encode(password.encode()).decode()
    flask.session['username'] = username

    # Write user data
    with open(USERS_PATH, 'w') as file:
        file.write(json.dumps(user_data))

    flask.redirect('/')

@user.route('/user/register/')
def register_page():
    form = RegisterUserForm()

    return flask.render_template('register.html', form=form)

@user.route('/user/login/', methods=["POST"])
def login_user():
    form = LoginUserForm(csrf_enabled=True)

    username = form.username.data
    password = base64.b64encode(form.password.data.encode()).decode()

    # Read existing user data
    with open(USERS_PATH, 'r') as file:
        user_data = json.loads(file.read())

    # check if user exists
    if username not in user_data:
        flask.abort(400)

    # Does password match?
    if user_data[username] != password:
        flask.abort(400)

    flask.session['username'] = username

    return flask.redirect('/')

@user.route('/login/')
def login_page():
    form = LoginUserForm()

    return flask.render_template('login.html', form=form)

@user.route('/logout/')
def logout_user():

    if 'username' in flask.session:
        flask.session.pop('username')

    return flask.redirect('/')
