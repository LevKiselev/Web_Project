from os import path, remove
from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
from PIL import Image
from data import db_session
from data.users import User
from data.pictures import Picture
from data.comments import Comment
from forms.user import RegisterForm, LoginForm, UserEditForm, ChangePasswordForm, UserSortForm
from forms.picture import PictureAddForm, PictureEditForm, PictureDelForm
from forms.comment import CommentAddForm, CommentDelForm

app = Flask(__name__)
app.debug = False
app.config['SECRET_KEY'] = 'klentest_secret_key'
app.config['MAX_FSIZE'] = 3  # Максимальный объем картинки в Мб
app.config['MAX_CONTENT_LENGTH'] = app.config['MAX_FSIZE'] * 1024 * 1024
login_manager = LoginManager()
login_manager.init_app(app)

errors = {
    413: "Вы пытаетесь загрузить слишком большой файл.",
    404: "К сожалению, такая страница не найдена...",
    401: "Для входа на эту страницу требуется авторизация."
}


def user_last_time_update():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user:
            user.last_date = datetime.now().replace(microsecond=0)
            db_sess.commit()
        db_sess.close()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/')
@app.route('/index/<int:user_id>')
def index(user_id=0):
    user_last_time_update()
    db_sess = db_session.create_session()
    if user_id:
        user = db_sess.query(User).filter(user_id == User.id).first()
        if user:
            pics = db_sess.query(Picture).filter(user_id == Picture.user_id).order_by(Picture.id.desc()).all()
        else:
            abort(404)
    else:
        user = None
        pics = db_sess.query(Picture).order_by(Picture.id.desc()).limit(24).all()
    # db_sess.close()
    return render_template('index.html', user=user, items=pics)


@app.route('/picview/<int:pic_id>', methods=['GET', 'POST'])
def picview(pic_id=0):
    user_last_time_update()
    db_sess = db_session.create_session()
    pic = db_sess.query(Picture).filter(pic_id == Picture.id).first()
    if pic:
        form_com_add = CommentAddForm()
        form_pic_edit = PictureEditForm()
        form_pic_del = PictureDelForm()
        form_com_del = CommentDelForm()
        if request.method == "GET":
            form_pic_edit.title.data = pic.title
            form_pic_edit.descr.data = pic.descr
        if form_pic_edit.validate_on_submit() and form_pic_edit.title.data:
            pic.title = form_pic_edit.title.data
            pic.descr = form_pic_edit.descr.data
            db_sess.commit()
        if form_com_add.validate_on_submit() and form_com_add.content.data:
            com = Comment(
                content=form_com_add.content.data,
                user_id=current_user.id,
                picture_id=pic.id
            )
            db_sess.add(com)
            db_sess.commit()
        if form_pic_del.validate_on_submit() and current_user.id == pic.user_id and form_pic_del.pic_id.data:
            db_sess.query(Comment).filter(Comment.picture_id == pic.id).delete(synchronize_session='fetch')
            db_sess.delete(pic)
            db_sess.commit()
            remove(f"static/photos/{pic.filename}")
            remove(f"static/thumb/{pic.filename}")
            return redirect(f"/index/{current_user.id}")
        if form_com_del.validate_on_submit() and form_com_del.com_id.data:
            com = db_sess.query(Comment).filter(Comment.id == form_com_del.com_id.data).first()
            if com and current_user.id in [pic.user_id, com.user_id]:
                db_sess.delete(com)
                db_sess.commit()
        # db_sess.close()
        return render_template('picview.html', pic=pic, form_com_add=form_com_add, form_com_del=form_com_del,
                               form_pic_del=form_pic_del, form_pic_edit=form_pic_edit)
    db_sess.close()
    abort(404)


@app.route('/userlist', methods=['GET', 'POST'])
def userlist():
    user_last_time_update()
    form_sort = UserSortForm()
    sorting = "name"
    if form_sort.validate_on_submit():
        sorting = form_sort.select.data
    db_sess = db_session.create_session()
    if sorting == "pics":
        users = db_sess.query(User).all()
        users.sort(key=User.pic_cnt, reverse=True)
    elif sorting == "comments":
        users = db_sess.query(User).all()
        users.sort(key=User.com_cnt, reverse=True)
    else:
        users = db_sess.query(User).order_by(sorting).all()
        if sorting != "name":
            users.reverse()
    pics_sets = {}
    for user in users:
        pics_sets[user.id] = db_sess.query(Picture.filename).filter(user.id == Picture.user_id).order_by(
            Picture.id.desc()).limit(3).all()
    db_sess.close()
    return render_template('userlist.html', items=users, pics=pics_sets, form_sort=form_sort)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        db_sess.close()
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/rules')
def rules():
    return render_template('rules.html', max_size=app.config['MAX_FSIZE'])


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        db_sess.close()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/user_edit', methods=['GET', 'POST'])
@login_required
def user_edit():
    form = UserEditForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user:
            form.name.data = user.name
            form.about.data = user.about
            db_sess.close()
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user:
            user.name = form.name.data
            user.about = form.about.data
            db_sess.commit()
            db_sess.close()
            return redirect('/')
        else:
            abort(404)
    return render_template('user_edit.html', title='Редактирование профиля', form=form)


@app.route('/passw_edit', methods=['GET', 'POST'])
@login_required
def passw_edit():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user and form.password.data == form.password_again.data:
            user.set_password(form.password.data)
            db_sess.commit()
            db_sess.close()
            return redirect('/')
        else:
            abort(404)
    return render_template('passw_edit.html', title='Смена пароля', form=form)


@app.route('/picture_add', methods=['GET', 'POST'])
@login_required
def picture_add():
    form = PictureAddForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        new_id = 1
        pic = db_sess.query(Picture).order_by(Picture.id.desc()).first()
        if pic:
            new_id = pic.id + 1
        file = form.upload.data
        picture = Picture(
            id=new_id,
            filename=f"f{new_id:08d}{path.splitext(file.filename)[1]}",
            title=form.title.data,
            descr=form.descr.data,
            user_id=current_user.id
        )
        file.save(f"static/photos/{picture.filename}")
        image = Image.open(f"static/photos/{picture.filename}")
        image.thumbnail((300, 300))
        image.save(f"static/thumb/{picture.filename}")
        db_sess.add(picture)
        db_sess.commit()
        db_sess.close()
        return redirect('/')
    return render_template('picture_add.html', form=form, max_size=app.config['MAX_FSIZE'])


@app.route('/comment_del/<int:com_id>', methods=['GET', 'POST'])
@login_required
def comment_del(com_id):
    db_sess = db_session.create_session()
    com = db_sess.query(Comment).filter(Comment.id == com_id, Comment.user_id == current_user.id).first()
    if com:
        db_sess.delete(com)
        db_sess.commit()
        db_sess.close()
    else:
        abort(404)
    return redirect(f"/picview/{com.picture_id}")


@app.errorhandler(413)
@app.errorhandler(404)
@app.errorhandler(401)
def request_error(err):
    err.description = errors[err.code]
    return render_template('error_page.html', error=err)


def main():
    db_session.global_init("db/database.db")
    app.run()


if __name__ == '__main__':
    main()
