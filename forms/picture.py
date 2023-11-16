from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired


class PictureAddForm(FlaskForm):
    upload = FileField('image',
                       validators=[FileRequired(), FileAllowed(['jpg', 'png', 'gif'], 'Допустимы только JPG, PNG, GIF')])
    title = StringField("Название", validators=[DataRequired()])
    descr = TextAreaField("Описание")
    submit = SubmitField('Отправить')


class PictureEditForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired()])
    descr = TextAreaField("Описание")
    submit = SubmitField('Сохранить')


class PictureDelForm(FlaskForm):
    pic_id = HiddenField()
    submit = SubmitField('Удалить')
