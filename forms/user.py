from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField, SelectField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('E-mail', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Отправить')


class UserEditForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Сохранить')


class ChangePasswordForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class LoginForm(FlaskForm):
    email = EmailField('E-mail', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class UserSortForm(FlaskForm):
    select = SelectField('Сортировка', choices=[("name", "Имя"), ("created_date", "Дата регистрации"),
                                                ("last_date", "Последний вход"),
                                                ("pics", "Количество фотографий"),
                                                ("comments", "Количество комментариев")])
    submit = SubmitField('Сортировать')
