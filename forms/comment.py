from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired


class CommentAddForm(FlaskForm):
    content = TextAreaField("Комментарий", validators=[DataRequired()])
    submit = SubmitField('Сохранить')

class CommentDelForm(FlaskForm):
    com_id = HiddenField()
    submit = SubmitField('Удалить')
