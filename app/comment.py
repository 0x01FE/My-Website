import flask
import flask_session
import flask_wtf
import wtforms




class CommentForm(flask_wtf.FlaskForm):
    textbox = wtforms.TextAreaField()




