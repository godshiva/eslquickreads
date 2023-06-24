from eslquickreads import app, bcrypt, db
from flask import render_template, url_for, flash, redirect
from flask_login import login_user, logout_user, login_required
from datetime import datetime
from eslquickreads.route.form.users_form import LoginForm, RegisterForm, EmailPasswordForm, PasswordForm
from eslquickreads.route.models.user_models import Users, Developer


@app.route("/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        dev = Developer.query.filter_by(email=form.email.data).first()
        user = Users.query.filter_by(email=form.email.data).first()

        # developer login
        if dev:
            if bcrypt.check_password_hash(dev.password, form.password.data):
                if dev.active:
                    """Developer login"""
                    login_user(dev)
                    return redirect(url_for('home'))
                else:
                    flash('Your account has been deactivated', 'info')
                    return redirect(url_for('login'))
            flash("Invalid Password", 'info')
            return redirect(url_for('login'))
        # user login
        elif user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                if user.active:
                    """Developer login"""
                    login_user(user)
                    return redirect(url_for('home'))
                else:
                    flash('Your account has been deactivated', 'info')
                    return redirect(url_for('login'))
            flash("Invalid Password", 'info')
            return redirect(url_for('login'))
    return render_template('login.html', form=form, title='Home')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(email=form.email.data, password=hashed_password, date_created=datetime.now())
        #user = Developer(email=form.email.data, password=hashed_password, date_created=datetime.now())
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form, title='Register')


@app.route("/send_reset_password", methods=['GET', 'POST'])
def send_reset_password():
    form = EmailPasswordForm()
    return render_template('login.html', form=form, title='Request Reset Password')


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    form = PasswordForm()
    return render_template('login.html', form=form, title='Reset Password')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile.html', title='Profile', Developer=Developer)
