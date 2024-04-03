import flask
import flask_wtf.csrf
import wtforms

user = flask.Blueprint('user', __name__, template_folder='./templates/user')

class RegisterUserForm(flask_wtf.FlaskForm):
    username = wtforms.StringField("Username", [
        wtforms.validators.Length(min=4, max=32),
        wtforms.validators.DataRequired()
    ])
    password = wtforms.PasswordField("Password", [
        wtforms.validators.Length(min=8, max=64),
        wtforms.validators.DataRequired()
    ])

@user.route('/user/add/', methods=["POST"])
def add_user():
    pass

@user.route('/user/register/')
def register_user():
    form = RegisterUserForm()

    return flask.render_template('register.html', form=form)
